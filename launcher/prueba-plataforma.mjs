// Comprobacion rapida de plataforma.js: se simula cada sistema reescribiendo
// process.platform/arch antes de importar el modulo.
//   node launcher/prueba-plataforma.mjs
const NATIVES = [
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-windows',
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-windows-arm64',
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-windows-x86',
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-macos',
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-macos-arm64',
  'org.lwjgl:lwjgl-freetype:3.3.3:natives-macos-patch',
  'org.lwjgl:lwjgl-glfw:3.3.3:natives-linux',
];
const ESPERADO = {
  'win32/x64':   ['natives-windows'],
  'darwin/x64':  ['natives-macos', 'natives-macos-patch'],
  'darwin/arm64':['natives-macos-arm64', 'natives-macos-patch'],
  'linux/x64':   ['natives-linux'],
};
let fallos = 0;
for (const clave of Object.keys(ESPERADO)) {
  const [plat, arch] = clave.split('/');
  Object.defineProperty(process, 'platform', { value: plat, configurable: true });
  Object.defineProperty(process, 'arch', { value: arch, configurable: true });
  const m = await import(`./src/main/core/plataforma.js?${plat}${arch}`);
  const ok = NATIVES.filter((n) => m.nativoDeEstaMaquina(n)).map((n) => n.split(':')[3]);
  const bien = JSON.stringify(ok) === JSON.stringify(ESPERADO[clave]);
  if (!bien) fallos++;
  console.log(`${clave.padEnd(13)} os=${m.OS_MOJANG.padEnd(8)} `
    + `java=${m.javaSinConsola('H').split(/[\/]/).pop().padEnd(9)} `
    + `adoptium=${(m.adoptium().os + '/' + m.adoptium().comprimido).padEnd(13)} ${bien ? 'OK' : 'MAL'}`);
  console.log(`${' '.repeat(13)} natives -> ${ok.join(', ') || '(ninguno)'}`);
  console.log(`${' '.repeat(13)} datos   -> ${m.raizDatos()}`);
}
console.log(fallos ? `\n${fallos} casos MAL` : '\nlos 4 casos correctos');
process.exit(fallos ? 1 : 0);
