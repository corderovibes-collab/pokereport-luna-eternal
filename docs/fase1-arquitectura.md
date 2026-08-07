# FASE 1 — Arquitectura, mods y dependencias

Auditoría de los 118 mods del pack contra lo que pide el diseño, y árbol de directorios.

---

## Resumen

**No hace falta instalar casi nada.** El pack ya trae las cinco piezas que sostienen todo
lo que se pide, y tres de ellas son justo las que un diseño desde cero habría propuesto.

| Ya instalado | Para qué sirve aquí |
|---|---|
| **FancyMenu 3.9.8** + Konkrete + Melody | **Pantallas propias, capas de imagen, animaciones, superposiciones.** Es la herramienta de interfaces épicas, y ya se usa para los menús del launcher |
| **Polymer 0.9.19** (bundled) | Contenido del lado del servidor que el cliente ve sin instalar nada: objetos con textura propia, menús, entidades virtuales |
| **Cobblemon 1.7.3** | NPCs, diálogos ramificados con retratos, combates con equipo fijo |
| **GeckoLib 4.9.2** | Modelos animados |
| **Sound Physics Remastered** | Audio con reverberación y oclusión reales. El laboratorio va a sonar a laboratorio |
| **owo-lib 0.12.15** | Framework de interfaces (owo-ui) por si hace falta una pantalla a medida |
| **Styled Chat 2.6.1** | Chat con formato, colores y componentes pinchables |
| **GlobalPacks 21.0.6** | Fuerza resourcepacks sin que nadie toque ajustes |
| **RespackOpts 4.14.0** | Opciones dentro del resourcepack |

---

## Lo que hay que añadir

**Nada obligatorio.** Después de buscar en Modrinth y GitHub, la conclusión honesta es que
el pack cubre el diseño. Añadir mods aquí sería ruido: cada uno son megas para 40 personas,
más superficie de fallo, y **ya vamos por 120 jars**.

Lo único que evaluaría, y solo si el diseño lo pide de verdad:

| Candidato | Cuándo tendría sentido | Estado |
|---|---|---|
| Un mod de cámara cinematográfica | Si queremos travellings suaves | **No hace falta**: se hace en vainilla con espectador + entidad móvil |
| `sgui` | Menús de cofre programables | **No hace falta**: es una librería Maven, ya viaja dentro de Polymer y Styled Chat |

---

## Cómo se resuelve cada sistema pedido

### 1 · Sistema de Resonancia (El Nexo)

**Sin mods.** Datapack puro:

- Objeto: un `minecraft:compass` con componentes propios y `custom_model_data` para que el
  resourcepack le ponga textura de amuleto.
- Detección de mano izquierda: `execute as @a if items entity @s weapon.offhand minecraft:compass[...]`
- Latido con tono variable: se mide la distancia al objetivo y se traduce a un `pitch`
  entre 0,5 y 2,0 en el `playsound`.
- Partículas: `particle` cada tick alrededor del jugador.

### 2 · Interfaces gráficas y HUD

**Dos capas que se complementan:**

**FancyMenu** para pantallas completas y superposiciones: puede añadir capas de imagen,
texto, botones y animaciones sobre cualquier pantalla del juego, incluida la partida. Se
configura con ficheros de layout que viajan en el pack del launcher.

**Fuentes de mapa de bits con espacios negativos** para el HUD dentro de la partida: barras
de progreso dibujadas, marcos alrededor de los diálogos, sellos del Eclipse. Van en el
resourcepack, no necesitan mod, y funcionan en títulos, barra de acción, chat y nombres de
inventario.

### 3 · Hackeo de terminales

**Menú de cofre con Polymer.** Cada hueco es un botón con icono propio vía
`custom_model_data`. Polymer permite servir esas texturas desde el servidor.

Alternativa más vistosa: **pantalla completa de FancyMenu** con arte de terminal y botones
reales. Más épico, pero hay que hacer el arte.

### 4 · Director de Escena

**Ya está construido y probado.** Panel de botones pinchables en el chat, con estado en
vivo y ayuda al pasar el ratón. Ver `docs/runbook-evento.md`.

Se abre con `/function evento:admin/soy_admin`. No usa `/trigger` porque el admin es
operador y puede lanzar funciones directamente — `/trigger` solo hace falta para jugadores
sin permisos.

### 5 · Cinemáticas

**Vainilla, sin mods.** El patrón que funciona:

1. Se invoca un `item_display` o `armor_stand` invisible como cámara
2. Se mueve por interpolación o por teletransportes suaves cada tick
3. Los jugadores pasan a espectador y se les hace `spectate` de esa entidad
4. Al acabar, vuelven a supervivencia en su sitio

Da control total del encuadre sin pedirle a nadie que instale nada.

---

## Corrección técnica importante

> «Todos los comandos (`/give`, `/summon`, `/item`, `/execute`), así como las entidades de
> display, deben utilizar obligatoriamente el formato de Componentes de Objetos.»

**Eso es correcto para objetos y falso para entidades.** En 1.21.1:

- **Objetos** → componentes: `give @s minecraft:compass[custom_name='...',lore=[...]]` ✅
- **Entidades** → siguen usando NBT: `summon text_display ~ ~ ~ {text:'...',billboard:"center"}` ✅

Los componentes sustituyeron al NBT **de los objetos**, no al de las entidades. Un
`text_display` o un `armor_stand` se sigue invocando con `{...}`.

Si aplicamos la regla tal como está escrita, generaríamos comandos de `summon` inválidos.
El código que ya está desplegado respeta la distinción correcta.

---

## Árbol de directorios

```
evento/
├── build_dp.py                    genera el motor
├── build_npcs.py                  genera NPCs y diálogos
├── build_rp.py                    genera el resourcepack de audio
├── build_ui.py                    ← NUEVO: fuentes y texturas de interfaz
│
├── datos/
│   ├── tipos_cobblemon.json       1.025 especies por tipo
│   ├── duraciones.json            duración exacta de cada línea de voz
│   └── layouts/                   ← NUEVO: layouts de FancyMenu
│
├── audio/voz/oak/                 32 líneas .ogg
├── arte/                          ← NUEVO
│   ├── hud/                       barras, marcos, sellos
│   ├── terminal/                  pantallas de hackeo
│   └── fuente/                    PNG de la fuente de mapa de bits
│
└── build/
    ├── Evento-DP.zip              motor: 70 funciones, 5 avances
    ├── Evento-Datos-DP.zip        6 NPCs, 6 diálogos
    ├── Evento-RP.zip              32 voces
    └── Evento-UI-RP.zip           ← NUEVO: interfaces
```

### Dentro del resourcepack de interfaz

```
Evento-UI-RP.zip
├── pack.mcmeta
└── assets/evento/
    ├── font/
    │   ├── hud.json               fuente con las imágenes del HUD
    │   └── espacios.json          caracteres de anchura negativa
    ├── textures/
    │   ├── font/                  los PNG que usa la fuente
    │   ├── item/                  texturas de custom_model_data
    │   └── gui/                   fondos de terminal
    └── items/                     definiciones de modelo de objeto
```

### Dónde vive cada cosa en el servidor

```
/mods/                             120 jars (sin cambios)
/world/datapacks/
    Evento-DP.zip                  ya desplegado
    Evento-Datos-DP.zip            ya desplegado
/config/xaero/                     radar sin Pokémon
```

Y en el pack del launcher:

```
config/cobbleverse/
    Luna-RP.zip
    Evento-RP.zip                  ya publicado
    Evento-UI-RP.zip               ← pendiente
config/fancymenu/                  layouts de las pantallas propias
```

---

## Lo que ya está hecho y probado

Antes de rehacer nada, conviene saber qué funciona ya. Todo esto está **desplegado y
verificado en el servidor**, no en teoría:

| Sistema | Estado |
|---|---|
| Motor de actos, relojes y límites | 70 funciones, probado de punta a punta |
| 6 NPCs con diálogo ramificado y combate | Probado: aparecen, hablan y pelean |
| 6 misiones con detección automática | 5 avances, incluido uno con 69 especies |
| Escenas con voz sincronizada | Cronometrado: 64 s el Acto I |
| Panel de admin pinchable | Probado |
| Zona de ensayo montable | Probada: monta y desmonta limpio |
| 32 líneas de voz de Oak | Generadas y empaquetadas |

**Si la nueva narrativa cambia la historia, el motor se aprovecha entero.** Lo único que
habría que rehacer son los textos de los diálogos y, si cambian mucho las frases de Oak,
regrabar voces.
