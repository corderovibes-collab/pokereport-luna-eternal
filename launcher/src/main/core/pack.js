import { rm, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { download, getJson, isIntact, pool } from './net.js';
import { paths } from './paths.js';
import { loadInstalled, saveInstalled } from './store.js';
import { extractZip } from './zip.js';

const CONCURRENCY = 10;

/** Carpetas que administra el launcher: solo dentro de ellas puede borrar. */
const MANAGED = ['mods', 'config', 'resourcepacks', 'shaderpacks', 'datapacks'];

const isManaged = (rel) => MANAGED.some((dir) => rel === dir || rel.startsWith(`${dir}/`));

/** Bloquea rutas que se escapen de la instancia (`../`, absolutas, unidades). */
function safeJoin(rel) {
  const target = path.join(paths.instance, rel);
  const check = path.relative(paths.instance, target);
  if (check.startsWith('..') || path.isAbsolute(check)) {
    throw new Error(`Ruta no permitida en el manifiesto: ${rel}`);
  }
  return target;
}

export async function fetchManifest(url) {
  const manifest = await getJson(url, { headers: { 'Cache-Control': 'no-cache' } });
  if (!Array.isArray(manifest.files)) throw new Error('El manifiesto no trae lista de ficheros');
  return manifest;
}

/**
 * Deja la instancia igual que el manifiesto.
 *
 * Solo se descarga lo que cambia de verdad (se compara por SHA1), así que la
 * primera instalación baja todo y las siguientes actualizaciones apenas mueven
 * los mods tocados. Los ficheros marcados `once` (options.txt, servers.dat) se
 * escriben si faltan pero nunca se pisan: son ajustes del jugador.
 */
export async function syncPack(manifest, { includeOptional = true } = {}) {
  const installed = await loadInstalled();
  const wanted = manifest.files.filter((f) => includeOptional || !f.optional);

  const toDownload = [];
  const nextState = {};

  for (const file of wanted) {
    const dest = safeJoin(file.path);
    nextState[file.path] = file.sha1;

    if (file.once) {
      // Solo si no existe. Nada de comparar tamaño ni hash: en cuanto el jugador
      // toca un ajuste el fichero deja de coincidir con el del manifiesto, y darlo
      // por corrupto significaba restaurarlo y borrarle la configuración en cada
      // arranque. `isIntact` sin criterio se limita a comprobar que hay algo.
      if (!(await isIntact(dest))) toDownload.push({ file, dest });
      continue;
    }
    if (file.archive) {
      // De una carpeta no se puede comprobar el SHA1: basta con que el manifiesto
      // siga anunciando el mismo zip que se extrajo la última vez.
      if (installed.files?.[file.path] !== file.sha1) toDownload.push({ file, dest });
      continue;
    }
    if (installed.files?.[file.path] === file.sha1 && (await isIntact(dest, { sha1: file.sha1 }))) {
      continue;
    }
    toDownload.push({ file, dest });
  }

  // Lo que estaba instalado y ya no está en el manifiesto (mod retirado o renombrado).
  const stale = Object.keys(installed.files ?? {})
    .filter((rel) => !nextState[rel] && isManaged(rel));

  return {
    manifest,
    toDownload,
    stale,
    bytes: toDownload.reduce((n, d) => n + (d.file.size ?? 0), 0),
  };
}

export async function applySync(plan, onProgress) {
  const { toDownload, stale, manifest } = plan;

  // `recursive` porque una entrada retirada puede ser un fichero o una carpeta extraída.
  for (const rel of stale) {
    await rm(safeJoin(rel), { force: true, recursive: true }).catch(() => {});
  }

  const total = plan.bytes || 1;
  let doneBytes = 0;
  let doneFiles = 0;

  await mkdir(paths.instance, { recursive: true });
  await pool(toDownload, CONCURRENCY, async ({ file, dest }) => {
    const track = (n) => {
      doneBytes += n;
      onProgress?.({
        phase: 'pack',
        message: 'Descargando el modpack…',
        progress: Math.min(doneBytes / total, 1),
      });
    };

    if (file.archive) {
      // Carpetas con muchísimos ficheros pequeños (el shaderpack son 1234) viajan
      // como un zip: una petición en vez de mil, y se extrae encima de lo que haya
      // para no borrar la config que generan los mods al ejecutarse.
      const cached = path.join(paths.cache, `${file.sha1}.zip`);
      await download(file.url, cached, { sha1: file.sha1, size: file.size, onChunk: track });
      await mkdir(dest, { recursive: true });
      await extractZip(cached, dest, { strip: file.strip ?? 0 });
      await rm(cached, { force: true });
    } else {
      await download(file.url, dest, {
        sha1: file.once ? undefined : file.sha1,
        size: file.size,
        onChunk: track,
      });
    }
    doneFiles++;
    onProgress?.({
      phase: 'pack',
      message: `Descargando el modpack… (${doneFiles}/${toDownload.length})`,
      progress: Math.min(doneBytes / total, 1),
    });
  });

  const files = {};
  for (const f of manifest.files) files[f.path] = f.sha1;
  await saveInstalled({ version: manifest.packVersion, updatedAt: Date.now(), files });

  return { downloaded: doneFiles, removed: stale.length };
}
