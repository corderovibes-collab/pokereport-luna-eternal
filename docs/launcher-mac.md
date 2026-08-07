# El launcher en macOS

No hay un launcher aparte. **Es el mismo**, compilado para Mac.

---

## Para quien va a jugar

Descarga el `.dmg` que corresponda a tu Mac:

| Tu Mac | Fichero |
|---|---|
| Apple Silicon (M1, M2, M3, M4) | `PokeReportLauncher-x.y.z-arm64.dmg` |
| Intel | `PokeReportLauncher-x.y.z-x64.dmg` |

Si no sabes cuál tienes: menú Apple → **Acerca de este Mac**.

### La primera vez macOS lo va a bloquear

Sale un aviso diciendo que no se puede abrir porque no se ha podido comprobar
al desarrollador. Es normal: **el launcher no está firmado con un certificado de
Apple**, que cuesta 99 dólares al año y esto es privado.

Para abrirlo:

1. **Clic derecho** sobre la aplicación → **Abrir**
2. En el aviso, **Abrir** otra vez

Solo hay que hacerlo la primera vez. Después se abre normal.

Si aun así se niega, desde la Terminal:

```
xattr -dr com.apple.quarantine "/Applications/PokeReport Launcher.app"
```

### Dónde se instala todo

```
~/Library/Application Support/cobbleverse/
```

Ahí van los mods, el mundo, las capturas y el Java que descarga el launcher.
**Desinstalar es borrar esa carpeta** y arrastrar la aplicación a la papelera.

---

## Para quien lo mantiene

### Lo que hubo que cambiar

El launcher estaba escrito dando por hecho que corría en Windows. Todo lo que
depende del sistema vive ahora en un único fichero,
[`src/main/core/plataforma.js`](../launcher/src/main/core/plataforma.js). El
resto del núcleo no pregunta por `process.platform` — si alguna vez hace falta,
es que falta algo en ese módulo.

| Qué | Antes | Ahora |
|---|---|---|
| Carpeta de datos | `%APPDATA%` a secas | Convención de cada sistema |
| Ejecutable de Java | `javaw.exe` | `javaw.exe` / `java` |
| Reglas de Mojang | clavadas a `'windows'` | `windows` / `osx` / `linux` |
| JRE de Adoptium | `os=windows`, `.zip` | `mac`/`linux`, `.tar.gz` |
| `JAVA_HOME` | la carpeta | `Contents/Home` en Mac |
| Natives | **todos** los `natives-*` | solo el de esta arquitectura |

### El fallo que importa de verdad

Mojang le pone **la misma regla** a todas las variantes de arquitectura:

```
org.lwjgl:lwjgl-glfw:3.3.3:natives-macos        -> allow os=osx
org.lwjgl:lwjgl-glfw:3.3.3:natives-macos-arm64  -> allow os=osx
```

Evaluar `rules` no basta: en un Mac **las dos pasan el filtro**, se extraen en
la misma carpeta con los mismos nombres de `.dylib`, y gana la última. En Intel
puede colar de casualidad; en Apple Silicon carga los binarios equivocados y el
juego no abre, sin decir por qué.

Por eso hay que filtrar por el **sufijo del nombre Maven**, no solo por reglas.
Eso es lo que hace `nativoDeEstaMaquina()`.

El mismo fallo estaba en Windows: se extraían `natives-windows`,
`natives-windows-arm64` y `natives-windows-x86` los tres encima. Funcionaba de
milagro.

### `-XstartOnFirstThread`

macOS lo necesita o el juego se cierra al abrir la ventana. **No hay que
añadirlo a mano**: viene en el JSON de versión de Mojang bajo una regla
`os=osx`, así que aparece solo en cuanto las reglas se evalúan bien. Ponerlo
también en `jvmFlags()` lo duplicaría.

### Comprobación

```
node launcher/prueba-plataforma.mjs
```

Simula los cuatro sistemas y verifica que cada uno elige sus natives. Corre
también en CI antes de compilar, porque es el tipo de fallo que no da error:
simplemente no arranca.

### Compilar

Un `.dmg` **solo se puede construir desde un Mac** — electron-builder necesita
`hdiutil` y `codesign`, que no existen en Windows. Sin un Mac a mano, se usa un
runner de GitHub:

```
git tag launcher-v1.2.3
git push --tags
```

[`.github/workflows/launcher.yml`](../.github/workflows/launcher.yml) compila
Windows y Mac en paralelo y publica los tres instaladores en la release. También
se puede lanzar a mano desde la pestaña **Actions**.

### Lo que falta por probar

Todo esto está escrito y validado, pero **nadie lo ha ejecutado en un Mac de
verdad**. Lo que hay que mirar la primera vez:

1. Que el JRE de Adoptium se descomprima bien (`tar` del sistema, no el
   extractor propio)
2. Que encuentre `Contents/Home/bin/java`
3. Que el juego abra ventana — si no, es `-XstartOnFirstThread`
4. En Apple Silicon, que cargue los `.dylib` de arm64
5. Que Gatekeeper deje pasar con clic derecho → Abrir
