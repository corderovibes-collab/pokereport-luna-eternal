# Arquitectura v2 — con interfaces y cinemáticas de verdad

Reestructuración tras bajar el aforo a 12 personas y meter tres proyectos externos.
Todo lo de aquí está **instalado y verificado en el servidor**, no propuesto.

---

## Lo que cambia y por qué

Con 40 personas el peso de descarga y el riesgo de que a alguien no le arranque el juego
pesaban más que la ambición. **Con 12 no.** Doce personas se actualizan solas por el
launcher y si algo falla se arregla en cinco minutos.

Eso desbloquea mods de cliente, y con ellos tres cosas que antes eran imposibles.

---

## Los tres proyectos añadidos

Buscados en Modrinth, descargados, verificados por SHA1 y arrancados en el servidor.
**2,3 MB en total** y cero conflictos.

### KantoNPCs 1.0.5 — 1,73 MB

NPCs hechos **para Cobblemon**, no adaptados. Del proyecto CobbleKanto.

| Trae | Para qué en el evento |
|---|---|
| **86 skins de entrenador**, y una es `prof oak.png` | Oak parece Oak, no un Steve con nombre |
| Carpeta de skins externa | Metemos skins propias para Vex y el Equipo Eclipse |
| NPCs de diálogo, de combate y de rival | Los guardianes, los guardias, la jefa |
| Combates de entrenador Cobblemon | Nativo, sin adaptar nada |
| Tienda y trueque | Un mercado negro del Eclipse, si interesa |
| Modelo fino y ancho | Vex puede tener silueta propia |

Comandos: `/kantonpcs rivalstarters`, `money`, `resetnpcs`, entre otros.

### Blabber 1.8.1 — 0,33 MB

API de diálogo de **Ladysnake** (los de Requiem y Cardinal Components). Dos estilos de
pantalla incluidos, uno de ellos tipo JRPG con retrato grande.

**Lo que de verdad cambia:**

```
/blabber dialogue start <dialogo> [<jugadores>]
```

Ese comando se puede lanzar **desde el datapack**, que corre con permisos de servidor.

Antes teníamos un techo: los diálogos de Cobblemon no podían ejecutar nada, porque
`run_command` corre con permisos del jugador. Ahora es al revés — **el motor decide cuándo
se abre un diálogo**, a quién y con qué contenido. Se acabó depender de que alguien haga
clic derecho en el momento justo.

Los diálogos son ficheros JSON, así que encajan con el sistema de generación que ya
tenemos.

### Cutscene API 1.6.6 — 0,27 MB

Cinemáticas de verdad, definidas en datapacks. Licencia MIT.

**Trayectorias de cámara** por segmentos, y cada segmento puede ser:

- línea recta
- **curva de Bézier**
- **spline Catmull-Rom**
- punto fijo
- punto definido por funciones matemáticas

La rotación usa el mismo sistema. Más transiciones de entrada y salida, efectos, duración
en ticks y control de lo que el jugador puede hacer mientras mira.

```
/cutscene start <jugador> <tipo> [at_preview|<posicion>]
/cutscene preview (set|hide)
/cutscene stop [<jugador>]
```

El modo `preview` deja **colocar la cámara dentro del juego** y ver el encuadre antes de
escribir nada. Se diseña volando, no a ciegas con coordenadas.

---

## Lo que ya estaba y sigue mandando

| Mod | Papel |
|---|---|
| **FancyMenu 3.9.8** | Pantallas propias, capas de imagen, animaciones sobre la partida |
| **Polymer 0.9.19** | Objetos y menús servidos desde el servidor |
| **Cobblemon 1.7.3** | Especies, combates, Luna |
| **GeckoLib 4.9.2** | Modelos animados |
| **Sound Physics Remastered** | Reverberación y oclusión reales |
| **owo-lib** | Framework de interfaz, por si hace falta pantalla a medida |

---

## Cómo queda repartido cada sistema

| Sistema | Con qué se hace |
|---|---|
| **Diálogos** | **Blabber**, lanzados por el motor |
| **NPCs y su aspecto** | **KantoNPCs** con skins reales |
| **Cinemáticas** | **Cutscene API** con splines |
| **HUD en partida** | Fuentes de mapa de bits + espacios negativos (resourcepack) |
| **Pantallas completas** | **FancyMenu** |
| **Terminales de hackeo** | Menú de cofre con **Polymer** o pantalla de FancyMenu |
| **Hologramas en el mundo** | `text_display` / `item_display`, vainilla |
| **Motor, relojes, misiones** | Datapack propio, ya hecho |
| **Panel de admin** | Botones pinchables en chat, ya hecho |
| **Voz** | 32 líneas ya grabadas y empaquetadas |

---

## Qué se conserva del trabajo anterior

**El motor entero.** 70 funciones probadas: actos, relojes, límites de tiempo, misiones
con detección automática, escenas con voz sincronizada, panel de admin, zona de ensayo.

Nada de eso depende de la historia. Si la narrativa cambia, se cambian los textos.

**Lo que se sustituye:**

| Antes | Ahora | Motivo |
|---|---|---|
| NPCs de Cobblemon | **KantoNPCs** | Skins de verdad, y Oak parece Oak |
| Diálogos de Cobblemon | **Blabber** | Los lanza el motor, y la pantalla es mejor |
| Escenas con títulos | **Cutscene API** + voz | Cámara con splines en vez de texto en pantalla |

Los diálogos viejos no se tiran: el **texto** se aprovecha, cambia el envoltorio.

---

## Estado del servidor

```
123 jars en /mods            (eran 120)
454 ficheros en el pack      (eran 451)
Arranque: Done (4.426s)      sin conflictos
```

`config/kantonpcs/skins/` — 86 skins listas, incluida `prof oak.png`.

---

## Lo siguiente

1. **Skins propias** para Vex y el Equipo Eclipse, al directorio de KantoNPCs
2. **Rehacer los 6 NPCs** con KantoNPCs en vez de Cobblemon
3. **Portar los diálogos** a formato Blabber, aprovechando el texto
4. **Diseñar las cinemáticas** con `/cutscene preview` volando por el mapa
5. **Arte del HUD**: marcos, barras, sellos del Eclipse
