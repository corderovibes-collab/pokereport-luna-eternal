# Guía del cliente (lo que instalan los jugadores)

**IP del servidor: `s17.mia.us.tarohosting.lat:33445`**

## Lo primero: Sodium y compañía van en el CLIENTE, no en el servidor

Es la duda que suele liar a todo el mundo, así que queda claro:

- **Sodium, Iris, los shaders, EntityCulling, ImmediatelyFast…** son mods de **render**.
  Solo tienen sentido en el PC de cada jugador. En un servidor no pintan nada y de hecho
  muchos ni arrancan ahí.
- Lo que sí va en el servidor es lo que optimiza la **lógica y los chunks**: Lithium, C2ME,
  Krypton, VMP, Chunky…

Por eso el reparto está así, y es lo correcto:

| | Mods |
|---|---|
| **Cliente** (123 mods) | Sodium, Iris, Reese's Sodium Options, ImmediatelyFast, EntityCulling, More Culling, BadOptimizations, Particle Core, ETF/EMF, Xaero's, REI, Mod Menu… + 30 resourcepacks + Complementary Unbound |
| **Servidor** (103 mods) | Cobblemon y todo el contenido, + Lithium, C2ME, ScalableLux, Krypton, FerriteCore, ModernFix, VMP, Chunky, spark… |

Todo lo de Sodium **ya viene dentro del modpack**, así que los jugadores no tienen que hacer nada
especial: instalando el pack lo tienen.

## Instalación (los 12 jugadores tienen que hacer esto)

Hace falta **COBBLEVERSE 1.7.42** exacto. Si alguien tiene otra versión, no entra.

Para que nadie se instale una versión distinta por error, en
[`client-pack/COBBLEVERSE 1.7.42.mrpack`](../client-pack/) está el fichero exacto que usa el
servidor. Pásaselo y que lo instalen desde ahí.

### Opción A — Modrinth App (la más fácil)

1. Bajar la [Modrinth App](https://modrinth.com/app).
2. `Add instance` → `From file` → elegir el `.mrpack`.
3. Esperar a que descargue y darle a jugar.

### Opción B — Prism Launcher

1. `Add Instance` → `Import` → seleccionar el `.mrpack`.
2. En `Edit → Settings → Java`, poner la memoria (ver abajo).

### Opción C — CurseForge App

`Create Custom Profile` → `Import` → el `.mrpack`.

## Memoria a asignar en el launcher

Esto es lo que más gente hace mal: **asignar demasiada RAM empeora el rendimiento**, no lo mejora
(el recolector de basura de Java tarda más en recorrer un montón grande).

| RAM del PC | Asignar al juego |
|---|---|
| 8 GB | 4 GB |
| 16 GB | **6 GB** ← lo normal |
| 32 GB o más | 8 GB (no más) |

Nunca pasar de 8 GB aunque sobre RAM. Y hay que usar **Java 21**; los launchers de arriba lo
descargan solos.

## Ajustes recomendados dentro del juego

En `Opciones → Vídeo`, y con Sodium ya instalado:

| Ajuste | Valor | Por qué |
|---|---|---|
| Distancia de renderizado | 8–12 | El servidor manda 8 chunks; subir más solo gasta GPU sin ver más |
| Distancia de simulación | 6 | La marca el servidor, no sirve subirla |
| Nubes | Desactivadas | Regalo de FPS |
| VSync | Desactivado | Menos *input lag* |
| Partículas | Reducidas | En combates Pokémon hay muchísimas |
| Fresh Animations | Solo si va sobrado | Es bonito pero cuesta bastante |
| Shaders (Complementary) | Solo con GPU dedicada | Puede costar la mitad de los FPS |

Si alguien va justo de FPS, lo primero es **quitar los shaders**, y después bajar las partículas.

## Extra de optimización (opcional, para PCs justos)

En [`client-pack/extra-optimizacion/`](../client-pack/extra-optimizacion/) hay 5 mods **de
cliente** que el pack no trae y que suman FPS sin cambiar nada del juego. Se copian dentro de la
carpeta `mods` de la instancia:

| Mod | Qué hace |
|---|---|
| **Sodium Extra** 0.9.3 | Añade a Sodium controles de niebla, partículas, clima y distancia de entidades. Es el que más se nota |
| **Dynamic FPS** 3.11.4 | Baja los FPS cuando el juego no está en primer plano. Se nota mucho al hacer alt-tab |
| **ThreadTweak** 0.1.5 | Reparte mejor los hilos: carga más rápida |
| **Language Reload** 1.7.6 | Arranque y recarga de recursos más rápidos |
| **Fast IP Ping** 1.0.11 | La lista de servidores deja de tardar en responder |

Los cinco están **verificados por SHA1** y comprobados contra las versiones que trae el pack
(Sodium 0.8.12, Iris 1.8.14, Fabric API 0.116.14). Son opcionales: sin ellos el juego va bien igual.

### Dos que hay que evitar

Los miré y **no valen** con este pack. Si alguien los instala por su cuenta, **no le arrancará
el juego**:

- **Nvidium** — exige `sodium 0.6.13` exacto y el pack lleva **0.8.12**.
- **Cull Less Leaves** — exige `sodium < 0.6`.

## Si algo falla

| Problema | Solución |
|---|---|
| "Incompatible mods" / no entra | Versión del pack distinta. Tiene que ser **1.7.42** |
| "Flying is not enabled" | Ya está resuelto en el servidor (`allow-flight=true`) |
| Se queda sin memoria | Bajar la RAM asignada a 6 GB, no subirla |
| Va a tirones al explorar | Zona todavía sin pregenerar, o shaders. Probar sin shaders |
| Cuelgue al cargar recursos | Quitar Fresh Animations y los resourcepacks pesados |
