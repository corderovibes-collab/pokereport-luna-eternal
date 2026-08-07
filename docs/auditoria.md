# Auditoría e instalación — Cobbleverse en Paquete Ender Dragon

Fecha: 28 de julio de 2026.

## 1. Qué había antes

El servidor `2a0a48ff` ("Paquete Ender Dragon") estaba **completamente vacío** y apagado:
cero ficheros, sin mundo y sin modpack. No se ha borrado nada de nadie.

El otro servidor de la cuenta, "Paquete Esqueleto" (4 GB, Fabric 1.20.1), **no se ha tocado**.

## 2. Versión correcta del modpack

Tu intuición de la 1.21.1 era correcta, y lo he confirmado en origen en vez de darlo por bueno:

| Dato | Valor | De dónde sale |
|---|---|---|
| Modpack | COBBLEVERSE 1.7.42 | última *release* en Modrinth, publicada el 21-jul-2026 |
| Minecraft | **1.21.1** | campo `dependencies` del `modrinth.index.json` del pack |
| Loader | **Fabric 0.18.4** | mismo campo |
| Instalador Fabric | 1.1.1 (estable) | meta oficial de FabricMC |

Cobbleverse **solo existe para Fabric**. No hay versión oficial de NeoForge (hay un *port*
no oficial de terceros, descartado: no lo mantiene el autor del pack).

Todo eso está instalado y verificado en el servidor: el arranque dice
`Loading Minecraft 1.21.1 with Fabric Loader 0.18.4`.

## 3. Java: cambiado de 25 a 21

El servidor venía con la imagen **Java 25**. Minecraft 1.21.1 y toda su cadena de Mixin están
pensados para **Java 21**; Java 25 es una fuente conocida de fallos raros de Mixin en packs
grandes. Lo he cambiado a `java_21_zulu`, que es la versión soportada.

## 4. El reparto cliente / servidor (lo importante de la auditoría)

Un `.mrpack` trae 168 ficheros y **los 168 vienen marcados como `server: required`**, cosa que
es falsa: ahí dentro están Sodium, Iris, los shaders y 60 mods más que son puramente de cliente.
Copiar la carpeta `mods` entera al servidor es el error clásico que hace que un servidor de
Cobbleverse ni arranque.

Así que he clasificado los 168 ficheros por dos vías independientes:

1. El campo `server_side` de cada proyecto en la API de Modrinth.
2. El campo `environment` del `fabric.mod.json` **dentro de cada jar**, leído directamente
   de los 136 jars (con *HTTP Range*, sin bajarme 670 MB para mirar un fichero de texto).

**Las dos vías coincidieron al 100%**: ningún mod que Modrinth diera por válido en servidor
resultó ser `environment: client` en su jar. Resultado:

| Categoría | Nº | Va al servidor |
|---|---|---|
| Solo servidor | 13 | Sí |
| Cliente y servidor | 94 | Sí |
| **Solo cliente** | **61** | **No** |

Los 61 descartados están listados con su motivo en
[`audit/mods-excluidos-cliente.json`](../audit/mods-excluidos-cliente.json). Entre ellos:
Sodium, Iris, ImmediatelyFast, EntityCulling, More Culling, BadOptimizations, Mod Menu,
Xaero's… y los 19 resourcepacks y el shaderpack (Complementary Unbound), que son del cliente.

### Las dos excepciones que había que cazar

Aquí es donde un despliegue automático se rompe. `CobbleFurnies` y `Rechiseled` **dependen**
de `athena` y `fusion`, dos librerías de texturas conectadas que Modrinth marca como
"solo cliente". Si haces caso a Modrinth y las excluyes, **Fabric se niega a arrancar**
por dependencia insatisfecha.

Sus jars declaran `environment: "*"`, o sea que sí cargan en servidor. Las he incluido
a mano. Por eso el servidor arranca a la primera.

Además verifiqué el **cierre completo de dependencias** de los 103 mods: los 11 casos que
parecían faltar (`c2me-base`, `cardinal-components-*`, `libjf-*`, `xaerolib`,
`team_reborn_energy`, `jackfredlib-lying`) están todos empaquetados como *jar-in-jar* dentro
de sus mods padre. Comprobado uno a uno.

## 5. Qué se ha desplegado

**103 mods** en `/mods` (346,6 MB), verificados por **SHA1** uno a uno contra Modrinth:

- 96 del modpack (94 del índice + athena + fusion), incluido
  `cobblemon-battle-positions-1.1.3.jar`, que no está en Modrinth y venía dentro del `.mrpack`.
- 7 añadidos de optimización (ver [rendimiento.md](rendimiento.md)).

**Configuración del pack**: los 111 ficheros/carpetas de `config/` tal cual vienen en el pack,
sin tocar, para no romper el balanceo que ya trae hecho Cobbleverse.

**Datapacks**: los 5 obligatorios, confirmados como activos en el mundo con `/datapack list`:

```
COBBLEVERSE-DP-v31.zip        (Global)   <- el grueso del contenido
COBBLEVERSE-Loot-DP-v11.zip   (Global)
COBBLEVERSE-RCT-DP-v20.zip    (Global)   <- 1714 entrenadores registrados
COBBLEVERSE - No Ender Dragon.zip (Global)
COBBLEVERSE - No Hunger.zip   (Global)
```

Los opcionales (Hoenn, Johto, Sinnoh, Terralith) están subidos en `/datapacks/extra/` y se
pueden activar cuando quieras.

## 6. Resultado del arranque

```
Loading Minecraft 1.21.1 with Fabric Loader 0.18.4
Loading 249 mods                     (103 + sus librerías anidadas)
Done (15.941s)! For help, type "help"
54 data pack(s) enabled
Registered 1714 trainers
```

**Cero errores reales.** Los `ERROR` que salen en el log son ruido cosmético normal en modded:

- `No data fixer registered for ...` — los mods no registran migraciones de versiones antiguas.
  Sale en todos los servidores modded, no afecta a nada.
- `Registry '...' was empty after loading` — registros de VanillaBackport sin contenido.
- `Invalid path in mod resource-pack cobblemon: README.md` — un README dentro de un pack.

El único aviso a tener en cuenta es `recommends modmenu, which is missing`: Mod Menu es un mod
de cliente y **no debe** estar en el servidor. Es correcto que falte.

## 7. Lo que hay que saber

**No hay copias de seguridad disponibles.** El plan tiene el límite de backups en **0**, así que
el panel no deja crear ninguna. Con un mundo de Pokémon donde la gente pierde progreso esto es
un riesgo serio. Está explicado en [operacion.md](operacion.md#copias-de-seguridad).
