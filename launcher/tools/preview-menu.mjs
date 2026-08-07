/**
 * Vista previa del menu de inicio, renderizada con Playwright.
 *
 * FancyMenu solo se puede ver abriendo Minecraft, y eso son varios minutos por
 * cada ajuste. Aqui se reconstruye la misma composicion en HTML leyendo las
 * coordenadas reales del layout, asi que colocar el titulo, los botones y a Luna
 * se comprueba en segundos y con las imagenes de verdad.
 *
 * Uso:  cd launcher && node tools/preview-menu.mjs
 */
import { chromium } from 'playwright';
import { readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const menu = path.join(raiz, 'client-pack', 'menu');
const assets = path.join(menu, 'config', 'fancymenu', 'assets');

const layout = await readFile(
  path.join(menu, 'config', 'fancymenu', 'customization', 'pokereport_main.txt'), 'utf8');

/** Saca `clave = valor` de un bloque del layout. */
const val = (bloque, clave) => bloque.match(new RegExp(`^\\s*${clave} = (.*)$`, 'm'))?.[1]?.trim();

/** Trocea el fichero en bloques de primer nivel. */
function bloques(texto, tipo) {
  const out = [];
  const re = new RegExp(`^${tipo} \\{$`, 'gm');
  for (const m of texto.matchAll(re)) {
    const fin = texto.indexOf('\n}', m.index);
    out.push(texto.slice(m.index, fin));
  }
  return out;
}

// El layout trabaja en la resolucion base declarada en su cabecera.
const BASE_W = 640;
const BASE_H = 360;

const elementos = [];
for (const b of bloques(layout, 'element')) {
  const src = val(b, 'source') ?? '';
  const m = src.match(/assets\/(.+)$/);
  if (!m || val(b, 'element_type') !== 'image') continue;
  elementos.push({
    archivo: m[1],
    anchor: val(b, 'anchor_point'),
    x: Number(val(b, 'x')), y: Number(val(b, 'y')),
    w: Number(val(b, 'width')), h: Number(val(b, 'height')),
  });
}

// Los botones propios (custom_button) son elementos, no `vanilla_button`.
const propios = bloques(layout, 'element')
  .filter((b) => val(b, 'element_type') === 'custom_button')
  .map((b) => ({
    id: 'custom', anchor: val(b, 'anchor_point'),
    x: Number(val(b, 'x')), y: Number(val(b, 'y')),
    w: Number(val(b, 'width')), h: Number(val(b, 'height')),
    etiqueta: val(b, 'label'),
  }));

const botones = bloques(layout, 'vanilla_button')
  .map((b) => ({
    id: val(b, 'instance_identifier'),
    anchor: val(b, 'anchor_point'),
    x: Number(val(b, 'x')), y: Number(val(b, 'y')),
    w: Number(val(b, 'width')), h: Number(val(b, 'height')),
    etiqueta: val(b, 'label'),
  }))
  .filter((b) => Number.isFinite(b.x) && b.w > 0 && b.x > -1000 && /titlescreen/.test(b.id ?? ''))
  .concat(propios);

/** Traduce el anclaje de FancyMenu a coordenadas absolutas de la base. */
function situar({ anchor, x, y, w, h }) {
  const centros = {
    'top-left': [0, 0], 'top-centered': [BASE_W / 2, 0], 'top-right': [BASE_W, 0],
    'mid-left': [0, BASE_H / 2], 'mid-centered': [BASE_W / 2, BASE_H / 2], 'mid-right': [BASE_W, BASE_H / 2],
    'bottom-left': [0, BASE_H], 'bottom-centered': [BASE_W / 2, BASE_H], 'bottom-right': [BASE_W, BASE_H],
  };
  const [cx, cy] = centros[anchor] ?? [BASE_W / 2, BASE_H / 2];
  return { left: cx + x, top: cy + y, w, h };
}

const uri = (f) => pathToFileURL(path.join(assets, f)).href;

const piezas = [
  `<img class="fondo" src="${uri('pokereport_background.png')}">`,
  ...elementos.map((e) => {
    const p = situar(e);
    return `<img class="pieza" src="${uri(e.archivo)}" style="left:${p.left}px;top:${p.top}px;width:${p.w}px;height:${p.h}px">`;
  }),
  ...botones.map((b) => {
    const p = situar(b);
    return `<div class="boton" style="left:${p.left}px;top:${p.top}px;width:${p.w}px;height:${p.h}px">`
      + `<span>${b.etiqueta ?? ''}</span></div>`;
  }),
].join('\n');

const html = `<!doctype html><meta charset="utf-8">
<style>
  body { margin:0; background:#000; }
  .lienzo { position:relative; width:${BASE_W}px; height:${BASE_H}px; overflow:hidden;
            transform-origin:0 0; transform:scale(2); image-rendering:pixelated; }
  .fondo { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
  .pieza { position:absolute; image-rendering:pixelated; }
  .boton { position:absolute; display:grid; place-items:center;
           background-image:url("${uri('boton.png')}"); background-size:100% 100%;
           image-rendering:pixelated; }
  .boton span { color:#eaeef7; font:600 8px/1 system-ui; text-shadow:0 1px 0 #000; letter-spacing:.04em; }
</style>
<div class="lienzo">${piezas}</div>`;

// El HTML se escribe junto a las imagenes y se navega con file://: desde
// `about:blank` (que es lo que usa setContent) Chromium bloquea las rutas locales.
const htmlPath = path.join(menu, '.vista.html');
await writeFile(htmlPath, html);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: BASE_W * 2, height: BASE_H * 2 } });
await page.goto(pathToFileURL(htmlPath).href);
await page.waitForTimeout(700);
await writeFile(path.join(raiz, 'client-pack', 'menu', 'vista-menu.png'), await page.screenshot());
await browser.close();
await rm(htmlPath, { force: true });

console.log(`  imagenes colocadas: ${elementos.map((e) => e.archivo).join(', ')}`);
console.log(`  botones dibujados : ${botones.length}`);
console.log('  vista: client-pack/menu/vista-menu.png');
