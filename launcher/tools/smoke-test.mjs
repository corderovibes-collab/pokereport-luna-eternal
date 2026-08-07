/**
 * Prueba de humo del núcleo del launcher, sin Electron y sin interfaz.
 *
 * Cubre lo que de verdad puede romperse en silencio: el lector de ZIP escrito a
 * mano, el filtrado de librerías por reglas de sistema operativo, el UUID offline
 * (si no coincide con el del servidor, los jugadores pierden el progreso) y que
 * los metadatos reales de Mojang y Fabric se resuelvan.
 *
 * Uso:  node tools/smoke-test.mjs
 */
import assert from 'node:assert/strict';
import { mkdtemp, rm, readdir, stat } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

process.env.COBBLEVERSE_ROOT ??= path.join(os.tmpdir(), 'cobbleverse-smoke');

const { extractZip } = await import('../src/main/core/zip.js');
const { resolveLibraries, allowed, fetchVersionJson } = await import('../src/main/core/minecraft.js');
const { fetchFabricProfile } = await import('../src/main/core/fabric.js');
const { offlineUuid, createOfflineAccount } = await import('../src/main/core/auth.js');
const { download } = await import('../src/main/core/net.js');

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    console.log(`  OK    ${name}`);
    passed++;
  } catch (err) {
    console.log(`  FALLO ${name}\n        ${err.message}`);
    failed++;
  }
}

console.log('\n== UUID offline ==');
await test('coincide con la fórmula del servidor de Minecraft', () => {
  // UUID v3 sobre "OfflinePlayer:<nombre>". Contrastado con una implementación
  // independiente (uuid.UUID(bytes=md5(...), version=3) de Python).
  assert.equal(offlineUuid('Notch'), 'b50ad385-829d-3141-a216-7e7d7539ba7f');
  assert.equal(offlineUuid('jeb_'), 'a762f560-4fce-3236-812a-b80efff0b62b');
  assert.equal(offlineUuid('Ash'), '4491e473-c7c9-3195-a8de-330c79a24db4');
});

await test('es estable y sensible al nombre', () => {
  assert.equal(offlineUuid('Ash'), offlineUuid('Ash'));
  assert.notEqual(offlineUuid('Ash'), offlineUuid('ash'));
});

await test('rechaza nombres inválidos', () => {
  assert.throws(() => createOfflineAccount('a'));
  assert.throws(() => createOfflineAccount('nombre con espacios'));
  assert.throws(() => createOfflineAccount('demasiado_largo_para_minecraft'));
  assert.equal(createOfflineAccount('Entrenador_1').name, 'Entrenador_1');
});

console.log('\n== Requisitos del equipo ==');
const { preflight } = await import('../src/main/core/preflight.js');
const REAL_GPU = 'ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00003EA0) Direct3D11 vs_5_0, D3D11-31.0)';

await test('comprueba las seis cosas que pueden faltar', async () => {
  const report = await preflight({ gpuRenderer: REAL_GPU });
  assert.equal(report.checks.length, 6);
  const ids = report.checks.map((c) => c.id);
  assert.deepEqual(ids, ['so', 'arch', 'vcredist', 'ram', 'disco', 'gpu']);
  assert.ok(report.checks.every((c) => c.title && c.detail));
});

await test('el renderizado por software avisa pero no impide jugar', async () => {
  // Avisa, no bloquea: lo que se lee es el renderizador de Chromium, y cae a software
  // en equipos donde Minecraft si funciona. Bloquear dejaba fuera a gente que podia jugar.
  for (const renderer of ['Google SwiftShader', 'Microsoft Basic Render Driver', 'llvmpipe (LLVM 15)']) {
    const report = await preflight({ gpuRenderer: renderer });
    assert.ok(report.warnings.some((c) => c.id === 'gpu'), `deberia avisar con ${renderer}`);
    assert.ok(!report.blocking.some((c) => c.id === 'gpu'), `no deberia bloquear con ${renderer}`);
  }
});

await test('una gráfica real no bloquea y se muestra con nombre legible', async () => {
  const report = await preflight({ gpuRenderer: REAL_GPU });
  const gpu = report.checks.find((c) => c.id === 'gpu');
  assert.equal(gpu.level, 'ok');
  assert.match(gpu.detail, /Intel\(R\) UHD Graphics 620/);
  assert.ok(!gpu.detail.includes('ANGLE'), 'no deberia enseñar la envoltura de ANGLE');
});

await test('el arreglo de Visual C++ se ofrece solo cuando falta', async () => {
  const vc = (await preflight({ gpuRenderer: REAL_GPU })).checks.find((c) => c.id === 'vcredist');
  // En esta máquina está instalado, así que no debe ofrecer acción.
  if (vc.level === 'ok') assert.equal(vc.action, undefined);
  else assert.equal(vc.action, 'install-vcredist');
});

console.log('\n== Reglas de sistema operativo ==');
await test('sin reglas se permite', () => assert.equal(allowed(undefined), true));
await test('deniega lo que no es Windows', () => {
  assert.equal(allowed([{ action: 'allow', os: { name: 'osx' } }]), false);
  assert.equal(allowed([{ action: 'allow', os: { name: 'windows' } }]), true);
});
await test('gana la última regla que encaja', () => {
  assert.equal(allowed([{ action: 'allow' }, { action: 'disallow', os: { name: 'windows' } }]), false);
});
await test('las features se respetan', () => {
  const rules = [{ action: 'allow', features: { is_demo_user: true } }];
  assert.equal(allowed(rules, { is_demo_user: false }), false);
  assert.equal(allowed(rules, { is_demo_user: true }), true);
});

console.log('\n== Metadatos reales de Mojang / Fabric ==');
let versionJson;
await test('descarga el JSON de Minecraft 1.21.1', async () => {
  versionJson = await fetchVersionJson('1.21.1');
  assert.equal(versionJson.id, '1.21.1');
  assert.equal(versionJson.javaVersion.majorVersion, 21, 'el pack exige Java 21');
  assert.ok(versionJson.downloads.client.url);
});

await test('resuelve librerías y natives para Windows', () => {
  const { classpath, natives } = resolveLibraries(versionJson.libraries);
  assert.ok(classpath.length > 20, `classpath demasiado corto: ${classpath.length}`);
  assert.ok(natives.length > 0, 'no se encontró ningún native de LWJGL');
  assert.ok(classpath.every((c) => c.url && c.dest));
  // Ninguna librería de otro sistema debe colarse.
  assert.ok(!classpath.some((c) => /natives-(linux|macos)/.test(c.dest)));
});

await test('el perfil de Fabric 0.18.4 trae la clase principal', async () => {
  const profile = await fetchFabricProfile('1.21.1', '0.18.4');
  assert.match(profile.mainClass, /KnotClient/);
  const { classpath } = resolveLibraries(profile.libraries);
  assert.ok(classpath.length >= 3);
  assert.ok(classpath.every((c) => c.url.startsWith('http')));
});

console.log('\n== Descarga + verificación SHA1 ==');
const tmp = await mkdtemp(path.join(os.tmpdir(), 'cv-test-'));
let jar;
await test('descarga un jar y valida su SHA1', async () => {
  const lib = resolveLibraries(versionJson.libraries).classpath.find((c) => c.sha1 && c.size < 3e6);
  jar = path.join(tmp, 'lib.jar');
  await download(lib.url, jar, { sha1: lib.sha1, size: lib.size });
  assert.equal((await stat(jar)).size, lib.size);
});

await test('un SHA1 incorrecto hace fallar la descarga', async () => {
  const lib = resolveLibraries(versionJson.libraries).classpath.find((c) => c.sha1 && c.size < 3e6);
  await assert.rejects(
    download(lib.url, path.join(tmp, 'malo.jar'), { sha1: '0'.repeat(40) }),
    /SHA1 no coincide/,
  );
});

console.log('\n== Lector de ZIP propio ==');
await test('extrae un jar real y descomprime bien', async () => {
  const out = path.join(tmp, 'extraido');
  const count = await extractZip(jar, out, { filter: (n) => !n.startsWith('META-INF/') });
  assert.ok(count > 0, 'no extrajo nada');
  const entries = await readdir(out);
  assert.ok(entries.length > 0);
});

await test('el filtro y `strip` funcionan', async () => {
  const out = path.join(tmp, 'filtrado');
  const count = await extractZip(jar, out, { filter: (n) => n.endsWith('.class'), strip: 1 });
  assert.ok(count >= 0);
});

await rm(tmp, { recursive: true, force: true });
await rm(process.env.COBBLEVERSE_ROOT, { recursive: true, force: true });

console.log(`\n${failed === 0 ? 'TODO CORRECTO' : 'HAY FALLOS'} — ${passed} pasadas, ${failed} fallidas\n`);
process.exit(failed === 0 ? 0 : 1);
