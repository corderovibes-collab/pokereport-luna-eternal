# Dónde lo dejamos

## 7 de agosto — el evento entero encadenado, del bosque al laboratorio

**57 voces** publicadas: 32 de Oak y las de los cuatro antagonistas.

```
Acto I    Oak                                    laboratorio de Oak, 1084 66 530
Acto II   Grum → Sable → Nix                     tres incursiones encadenadas
Acto III  el cifrado                             cinco pruebas, sin construir nada
Acto IV   Vex · Hydreigon 70 · tier 7            el clímax
Acto V    el reencuentro                         pendiente
```

### Los cuatro antagonistas

Cada uno sostiene lo mismo de una forma distinta, y en ese orden:

| | | |
|---|---|---|
| **Grum** | culpa | cree que fue piedad, pero no duerme |
| **Sable** | certeza | Luna no puede alcanzarlo, y por eso lo eligieron |
| **Nix** | miedo | de lo que hay detrás de la puerta |
| **Vex** | fracaso | lleva dos años fallando y lo sabe con precisión decimal |

La cadena narrativa se pasa el testigo sola. Nix deja caer que **Luna pudo irse
el primer día y nunca lo intentó**; Vex lo confirma —*«la puerta lleva abierta
desde el segundo día»*— y deja la pregunta que paga el Acto V: *«ninguno de
ustedes ha perdido lo suficiente para entender la respuesta»*.

### Coordenadas

```
Oak       1084 66 530
Grum      1888 64 257    cristal 1890 64 259    marcador 1887 64 255
Sable     1630 69 164    cristal 1632 69 161    marcador 1631 69 222 (boca de cueva)
Nix       1621 63 550    cristal 1625 63 548    marcador 1613 63 557
Vex       1800 80 569    cristal 1796 80 568
```

### Los jefes

| | Pokémon | nivel | vida | tier | fases |
|---|---|---|---|---|---|
| Grum | Mightyena | 45 | ×8 | 5 | 4 |
| Sable | Weavile | 52 | ×10 | 5 | 5 |
| Nix | Sharpedo | 58 | ×12 | 5 | 5 |
| **Vex** | **Hydreigon** | **70** | **×16** | **7** | **6** |

Tier siete es el único que el mod deja vacío a propósito para jefes propios.

### Todo cerrado con cerrojo

Los NPCs y los cristales viven en el mundo permanentemente, pero **nadie puede
tocarlos hasta que empiece el evento**:

- **Cristales**: `is_active=false`. Cada uno se enciende solo cuando el motor
  marca su señal; el de Vex, al arrancar el Acto IV.
- **NPCs**: si el evento está parado y un no-admin se acerca a menos de 5
  bloques, se le cierra el diálogo y le sale *«No hay nada que hablar todavía»*.

**`can_reset=false` no es opcional.** Con él a `true` los cristales se reciclan
cada dos horas y **cambian de jefe solos** — el de Sable apareció un día con un
Great Tusk en vez de su Weavile.

### El launcher, ahora también en macOS

Un único enlace para repartir:

```
https://github.com/corderovibes-collab/pokereport-luna-eternal/releases/latest
```

Tres instaladores: `.exe`, `-x64.dmg` (Intel) y `-arm64.dmg` (Apple Silicon).
Se compilan solos con `git tag launcher-v…`. Detalle en
[launcher-mac.md](launcher-mac.md).

### El proyecto ya está en git

249 ficheros, 9,9 MB. Fuera `voz/` (3,1 GB), el `.mrpack` y `node_modules`.
**Dentro las 50 voces en OGG**, que sin el modelo de clonado no se pueden
rehacer.

---

## 6 de agosto (tarde) — señal 2 montada y el Acto II encadenado

### Sable, el guardián de la montaña

Voz grabada (6 líneas, `sa_01`–`sa_06`), preset con diálogo listo, y su Weavile
como jefe de incursión. Publicado el resourcepack: **44 voces** (32 Oak, 6 Grum,
6 Sable).

```
marcador   1631, 69, 222    boca de la cueva — aquí salta el aviso de llegada
Sable      1630, 69, 164    58 bloques dentro
cristal    1632, 69, 161    justo detrás de él
```

El aviso de llegada apunta a la **entrada**, no a donde está Sable: la escena
tiene que empezar al entrar en la cueva, no cuando ya lo tienen delante.

**Weavile nivel 52**, vida ×10 (Grum va a ×8), siniestro/hielo, cinco fases de
escudo en vez de cuatro.

Sable no repite a Grum: donde Grum dudaba, a Sable **Luna no puede alcanzarlo**,
y por eso lo eligieron para apagarla. Su línea `sa_05` es la que mueve la trama —
el Eclipse no está *guardando* a Luna, la está **midiendo**, para aprender a
hacer lo que ella hace sin que ella exista. De ahí sale el laboratorio de Vex.

### El Acto II ya se encadena solo

Antes, al ganar una señal el marcador **no se repuntaba a la siguiente**: el
grupo se quedaba con la brújula clavada en el sitio ya hecho hasta que saltaba
el límite de 25 minutos. Ahora:

```
victoria → SEÑAL LOCALIZADA → Oak espera a que salgan todos
        → línea de victoria (a2_02, 10 s) → 12 s
        → SEÑAL DETECTADA + a2_03 hacia la montaña
        → se arma sola la vigilancia del cristal siguiente
```

Y si **no hay más señales construidas**, salta al Acto III en vez de esperar. El
evento se adapta a lo que haya montado en el mundo: añadir la costa a `SENALES`
lo encadena todo sin tocar nada más.

### Guardianes generalizados

El remate de la escena estaba escrito solo para Grum. Ahora es `guardianes/` con
`ev_reto` (segundos) y `ev_reto_id` (quién). Cada uno tiene su Pokémon, su sonido
y su aviso de dónde está el cristal.

### Ocho `playsound` que no oía nadie

Sin `at @s` suenan en el origen del mundo, y con volumen 1 el alcance son 16
bloques. **Había ocho**, entre ellos el de «SEÑAL DETECTADA» y el del arranque
del Acto II. Corregidos todos de una pasada con una expresión regular, en vez de
ir cazándolos de uno en uno.

### Construir con schematics: Litematica no sirve

**Litematica es un mod de cliente.** Instalarlo en el servidor no hace nada: el
coste de dibujar un schematic es del cliente, así que no arregla ni la lentitud
ni los cierres inesperados.

Lo que sí resolvería el problema es **WorldEdit en el servidor**: `//schem load`
+ `//paste` coloca la construcción entera del lado del servidor, sin que el
cliente dibuje un solo bloque fantasma. Sin instalar todavía.

---

## 6 de agosto — la escena de Grum, cerrada y probada de punta a punta

Funciona entera, sin que el director toque nada:

```
Grum habla — 6 líneas con voz, 5 páginas
   → «Apártate» → espera 8 s → cierra el diálogo él solo
   → título MIGHTYENA + doble gruñido → al cristal
   → incursión de hasta 12, un Pokémon cada uno
   → SEÑAL LOCALIZADA automático al ganar
   → Oak espera a que TODOS salgan de la arena, y entonces habla
```

### El truco del retardo

El último botón no remata la escena: la línea `g1_06` dura casi 7 segundos y el
gruñido le pisaba la voz. Easy NPC bloquea `function` y `schedule`, **pero
`scoreboard` no**. Así que el botón solo deja `ev_grum = 8` y se va; el reloj del
datapack lo baja de uno en uno y remata al llegar a cero.

De paso apareció `easy_npc dialog close <jugador>`, así que el diálogo se cierra
solo y nadie tiene que darle a Escape.

### Cómo sabe el motor que han ganado

El bloque del cristal lleva un contador `raid_cleared`. Al marcar la señal se
apunta cuánto vale y se compara cada segundo. Se compara **contra una marca, no
contra cero**, porque el cristal se reutiliza y el contador no vuelve atrás.

Oak no habla hasta que la dimensión de la incursión se queda sin nadie del grupo:

```
execute in cobblemonraiddens:raid_dimension positioned 0 0 0
        if entity @a[tag=ev_participa,distance=..]
```

Funciona porque `distance` **solo casa con entidades de la dimensión del
contexto**. Comprobado en el servidor.

### La calibración de la incursión

Medida de verdad, no estimada:

| vida | en solitario | 12 personas |
|---|---|---|
| ×25 · 1,15 | 10% | ~52% → **derrota** |
| ×8 · 1,08 | 30% | 150-190% → victoria |

> **Regla: % en solitario × 5,2 = margen del grupo.**
> Por debajo del 20% en solitario, doce personas pierden.

Sirve para calibrar a Sable y a Nix sin volver a hacer las cuentas. Hay un jefe
`grum_prueba` (Poochyena nivel 5, media vida) para probar la cadena entera sin
tener que ganar una pelea de verdad.

### Cuatro fallos encontrados

1. **La voz de Oak sonaba en TODO el servidor.** En `escenas/e*` el `playsound`
   iba a `@a` mientras el `stopsound` y los `title` de al lado sí filtraban por
   grupo — y con volumen 1000000, o sea audible a cualquier distancia.
2. **Dos `playsound` que no oía nadie**, en `senales/completar` y
   `senales/rendir`: sin `at @s` suenan en el origen del mundo, y con volumen 1
   el alcance son 16 bloques.
3. **La vigilancia de la incursión se apagaba antes de empezar.** Se colgaba de
   `ev_senal_act`, que se pone a cero **al llegar** al campamento — justo un
   segundo antes de hacer falta. Ahora `ev_raid_v` guarda el número de señal.
4. **El namespace de `/crd dens` no es opcional.** Sin `cobblemonraiddens:` el
   mod lanza una excepción y solo se ve *"An unexpected error occurred"*.

### Trabajar con gente conectada

`sendCommandFeedback` está en `false`, así que los jugadores no ven la respuesta
de los comandos. Lo único que se filtraba eran los marcadores `say` de la
consola — ya no se usan; ahora el log se lee por diferencia de tamaño.

Todo lo que emite el motor va a `@a[tag=ev_participa]`, salvo la invitación, que
debe llegar a todos a propósito.

### Recuperar objetos borrados

Dos procedimientos que funcionaron y conviene no olvidar.

**Mochilas de Sophisticated Backpacks.** El contenido vive en
`world/data/sophisticatedbackpacks.dat` indexado por UUID; el objeto es solo la
llave. Borrarlo en creativo no borra nada:

```
give <jugador> sophisticatedbackpacks:diamond_backpack[sophisticatedcore:storage_uuid=[I;a,b,c,d]] 1
```

Las claves de componente van **sin comillas** — el formato con comillas es el de
`/data get`, y en `/give` no vale.

**Tumbas.** `self_destruction_time: -1` y `non_owner_protection_time: -1`, o sea
que **no caducan y solo las abre su dueño**. Los datos están en
`world/data/universal-graves.dat`, con posición y contenido completo.

---

## 5 de agosto (noche) — Grum pasa a incursión y llega el filtro de acceso

### Grum ya no es un combate 1v1

Era el problema de fondo: un combate de entrenador es de uno contra uno, así que
con doce personas hay once mirando. Ahora es una **incursión de grupo**
(`cobblemonraiddens`, que ya estaba instalado sin usarse).

| | |
|---|---|
| Jefe | Mightyena nivel 45, ×1.8 de tamaño, ×25 de vida |
| Aforo | **12** (el mod trae 4 por defecto; se pisa desde el propio jefe) |
| Aporte | **1 Pokémon por jugador** |
| Fases | escudo al 60%, borra mejoras al 45%, cae el escudo al 30%, último arreón al 15% |
| Repeticiones | sin límite (por defecto el cristal moría a las 3) |

Generado por `evento/build_raid.py`. El aforo, la vida y las fases se retocan ahí
y se vuelve a generar — no hay nada escrito a mano.

Hay dos versiones: `grum_eclipse` (la segura) y `grum_eclipse_max` (con Dinamax,
que depende de Mega Showdown). Van separadas a propósito para que un fallo de la
segunda no se lleve por delante a la primera.

**Ya está colocado** en el campamento de la señal 1, en **1890, 64, 259**:

```
/crd dens 1890 64 259 boss cobblemonraiddens:grum_eclipse
```

**El namespace no es opcional.** Sin `cobblemonraiddens:` el mod no dice que no
encuentre al jefe — lanza una excepción, y lo único que se ve es *"An unexpected
error occurred"*. Despista porque los ficheros del datapack no llevan namespace
en el nombre. Costó un rato.

Para quitarlo: `setblock <pos> minecraft:air replace` — con `replace`, que
`destroy` suelta el cristal como objeto.

`weight: 0.0` lo mantiene fuera de la generación natural: solo existe donde lo
pongamos nosotros.

### Filtro de acceso al evento — «PROTOCOLO LUNA»

Capítulo de FTB Quests que hay que completar **antes** de poder entrar.

Los avances de Minecraft no servían: el disparador `catch_pokemon` de Cobblemon
filtra por especie y nada más. **Cobblemon Quests Reloaded** sí sabe filtrar por
`pokemon_type`, `min_level` y `max_level`, que es exactamente lo que hacía falta.

Tres capturas obligatorias, nivel **30–45**, y tienen que ser **capturas nuevas**
(acción `catch`, no vale sacarlos de la caja):

| Misión | Tipo | Por qué |
|---|---|---|
| Un aliado de tipo lucha | `fighting` | |
| Un aliado de tipo bicho | `bug` | |
| Un aliado de tipo hada | `fairy` | |

No son al azar. **Todos los guardianes del evento son siniestros** — Mightyena,
Weavile, Sharpedo, Hydreigon, Gengar — y el tipo siniestro tiene exactamente
tres debilidades: lucha, bicho y hada. Las misiones no son un peaje: son el
equipo que hace falta para ganar. Y como son tres capturas, el mínimo de tres
Pokémon sale solo.

### El puente entre las misiones y el motor

La última misión entrega una recompensa de tipo `command`:

```
tag @s add ev_apto
```

A partir de ahí el motor distingue tres estados:

```
sin tag                   ni se ha apuntado
ev_participa              apuntado pero SIN acreditar
ev_participa + ev_apto    listo
```

`[ INICIAR ]` ya no arranca a ciegas: si alguien del grupo va sin acreditar, lo
lista por nombre y ofrece `[ EMPEZAR IGUAL ]`. Es un aviso, no un bloqueo — el
día del evento manda el director, no el datapack. Botón nuevo
`[ ACREDITADOS ]` en el panel para ver la tabla cuando quieras.

Generado por `evento/build_quests.py`.

### Tres fallos que salieron por el camino

1. **Sable llevaba dos movimientos inexistentes** (`icyshard`, `faintattack`). Los
   nombres correctos son los de Showdown: `iceshard` y `feintattack`. Su equipo
   se cargaba a medias y nadie lo había notado.
2. **`admin/grupo` mandaba la lista al grupo, no al admin.** En
   `execute as @a[...] run tellraw @s`, el `@s` del destino pasa a ser cada
   participante. Resuelto con un tag temporal `ev_lector`.
3. **Chunky se reanuda solo al reiniciar** (`continueOnRestart`). Vuelto a pausar.

---

## 5 de agosto — Acto I completo y probado

**Funciona de punta a punta**, sin que el admin toque nada entre medias:

```
[ ME APUNTO ] → [ INICIAR ] → hablar con Oak (5 páginas con voz)
   → «Cuente conmigo» entrega el rastreador
   → ACTO II automático, brújula apuntando al bosque
   → llegar a 25 bloques → SEÑAL LOCALIZADA
```

Sin cinemática: se quitó del Acto I por decisión de diseño. La escena la lleva Oak en
persona — uno habla y el resto escucha por chat y voz.

### El campamento de la señal 1

Construido en **1887, 64, 255** (bosque oscuro, 850 bloques al este-noreste de la aldea).
Lleva la jaula vacía con el collar (`lumymon:ice_necklace` sobre un `item_display`).

### Tres fallos que costaron encontrar

1. **`execute if entity @s[distance=..25] positioned X Y Z`** medía la distancia del
   jugador a sí mismo (siempre 0), así que la llegada saltaba al instante. El
   `positioned` va **antes** de la comprobación.
2. **Atajos de teclado**: FTB Quests y FTB Teams se quedaron con `T` y `R`, dejando sin
   chat y sin poder sacar Pokémon. Resuelto dejándolos sin asignar en `options.txt` del
   pack (solo afecta a instalaciones nuevas; quien ya juega lo ajusta a mano una vez).
3. **Cinemáticas que dejaban al jugador encerrado**: `disable_actions` se quedaba pegado
   al jugador *en el servidor*, así que reinstalar el cliente no servía. Hay red de
   seguridad (`cine/vigilar`) y botón de pánico `admin/soltar_a_todos`.

### Sistema de misiones instalado

FTB Library + FTB Teams + FTB Quests + Cobblemon Quests Reloaded + el puente
**EasyNPC × FTB Quests**, que permite que un NPC reparta misiones desde su diálogo.
Sin configurar todavía.

Retirado: Tom's Simple Storage.

### Lo siguiente

**Grum**, el guardián del bosque. Hay una decisión pendiente:

| | Aspecto | Combate Pokémon |
|---|---|---|
| Easy NPC | skin propia ✔ | no pelea ✘ |
| NPC de Cobblemon | genérico ✘ | equipo fijo ✔ (ya hecho y probado) |

Falta mirar si Cobblemon tiene un comando para lanzar un combate de entrenador; si lo
tiene, Grum puede ser un Easy NPC guapo cuyo diálogo dispare la pelea.

---

## 4 de agosto (tarde) — Oak funcionando

**Desbloqueado.** El problema era KantoNPCs, no el cliente: **Easy NPC dibuja bien** donde
el otro fallaba. Instalado Easy NPC 7.4.1 (bundle + core + config UI), 128 jars.

### Lo que quedó hecho

| | |
|---|---|
| **Profesor Oak** | Colocado, con skin propia por URL y variante `PROFESSOR_01` |
| **Diálogo con voz** | 5 páginas, cada paso con su línea de Oak (`a1_01` … `a1_06`) |
| **Entrega el rastreador** | Botón final con `/give` directo |
| **Difusión al grupo** | Voz y texto van a todos, no solo a quien habla |
| **Inscripción al evento** | `[ ME APUNTO ] [ PASO ]` por `/trigger`; quien no se apunta no recibe nada |

### Cómo se edita el diálogo de Oak

No se toca a mano. El generador está en `evento/oak_dialogo.py`:

```
python evento/oak_dialogo.py audit/oak.npc.nbt audit/oak_con_dialogo.npc.nbt
```

Lee el preset exportado del juego (NBT comprimido), le inyecta `DialogData` conservando
skin, nombre y atributos, y lo vuelve a escribir. Luego se sube a
`world/easy_npc/preset/humanoid/` y se importa desde el juego con **Import → World**.

### Tres límites de Easy NPC, comprobados

1. **`function` y `execute` están bloqueados** para NPCs (`unsafeNpcCommands` en
   `config/easy_npc/security.cfg`). Por eso el rastreador se entrega con `give` directo.
   `playsound`, `give` y `tellraw` sí pasan.
2. **La interfaz de diálogo no se puede duplicar** a otros jugadores. Se rodea al revés:
   quien habla conduce y los comandos difunden a `@a[tag=ev_participa]`.
3. **No hay sincronía labial**: el modelo de jugador no tiene boca articulada. Sí se
   puede gesticular con `/easy_npc rotate <npc> <modelPart>`.

### Lo siguiente: el Acto II

Nada de esto está construido todavía.

1. **El marcador** — rayo de luz + distancia en vivo + desaparece al llegar. Xaero's no
   sirve: su `ServerWaypointManager` es una API para otros mods, no un canal de servidor.
2. **Los guardianes** — Grum, Sable y Nix siguen siendo NPCs de Cobblemon. Hay que
   rehacerlos con Easy NPC como Oak.
3. **Construir la señal 1** — guía completa en [senales-construccion.md](senales-construccion.md).
   Falta que decidáis las coordenadas.

### Voces pendientes de grabar

Si se quieren recuperar las ramas del diálogo que se quitaron por no tener audio, los
textos están al final de `guion-oak.md`: `quien`, `mirada` y `eclipse`. La de `mirada` es
la que plantaba el giro del Acto V.

---

## 4 de agosto (mañana) — bloqueados con los NPCs

**Paso 1 del evento (colocar a Oak) sigue sin salir.** La pantalla de configuración de
KantoNPCs se abre pero **no se dibuja**: sale un recuadro blanco.

Lo descartado, en orden:

| Sospechoso | Resultado |
|---|---|
| Driver de Intel desactualizado | **Descartado.** Tras actualizar, los miles de `GL_INVALID_OPERATION` desaparecieron del log — pero la pantalla sigue en blanco |
| Versión distinta cliente/servidor | Descartado: 1.0.5 en ambos |
| Errores en el servidor | Ninguno |
| Fuente propia de FancyMenu | Probado (`use_minecraft_font = 'true'`) — **tampoco** |

Queda por aislar: **FancyMenu entero** o **Sodium**. Y solo hay una persona para probar,
lo que lo hace lento.

**Decisión tomada: buscar otro mod de NPCs.** Es lo primero de la próxima sesión.

Lo que se necesita del mod: NPC con **skin propia** (Oak con cara de Oak), diálogo, y a
poder ser configurable **desde ficheros**, no solo por interfaz — así el problema de
dibujado deja de bloquear.

Candidatos ya vistos pero sin evaluar a fondo: **Easy NPC** (1M descargas, tiene interfaz
de configuración) y volver a los **NPCs nativos de Cobblemon**, que sí se definen por
JSON y ya estaban funcionando.

---

# Estado anterior — 3 de agosto de 2026

Punto de guardado. Lo que está hecho, lo que está a medias y por dónde seguir.

---

## Servidor

```
Estado:        encendido
Lista blanca:  ACTIVA, solo TheJuanCE
Evento:        parado (ev_estado = 0), sin restos de pruebas
Mundo:         guardado
Mods:          123 jars
```

Para reabrirlo al público: `/whitelist off`
Para readmitir a alguien: `/whitelist add A1ejandroreport`

---

## El evento: 7 de 8 fases

| Fase | Estado |
|---|---|
| 0 · Investigación y audio | hecha |
| 1 · Datapack motor | hecha y probada |
| 2 · NPCs | hecha y probada — **a rehacer con KantoNPCs** |
| 3 · Diálogos y escenas | hecha y probada — **a portar a Blabber** |
| 4 · Seis misiones | hecha y probada |
| 5 · 32 voces de Oak | hecha |
| **6 · Construir escenarios** | **vuestra, pendiente** |
| 7 · Panel de admin y guion del día | hecha y probada |
| 8 · Ensayo con gente | pendiente |

---

## Lo desplegado y funcionando

```
/world/datapacks/
    Evento-DP.zip            70 funciones, 5 avances
    Evento-Datos-DP.zip      6 NPCs, 6 diálogos

pack del launcher (454 ficheros)
    config/cobbleverse/Evento-RP.zip     32 voces de Oak
    mods/kantonpcs-1.0.5.jar
    mods/blabber-1.8.1-standalone.jar
    mods/cutscene-api-...-1.6.6.jar
    mods/toms_storage_...-2.4.1.jar
    mods/clientsort-...jar
```

---

## Cambios sueltos de hoy, ya en producción

- **Pokémon fuera del minimapa y del mapa** — desplegado por dos vías (perfil impuesto del
  servidor + fichero del pack sin `once`). **Falta que lo confirmes con los ojos.**
- **Tom's Simple Storage** actualizado a 2.4.1
- **Client Sort** añadido — botón de ordenar en cofres
- **Lore de Luna** reescrito como Diosa del Amor Incondicional, en Pokédex ES e EN

---

## Lo primero de mañana

1. **Entrar al juego y probar** siguiendo [prueba-evento.md](prueba-evento.md). Lo que más
   me sirve saber: **¿se oye la voz de Oak?** y **¿siguen saliendo Pokémon en el minimapa?**
   Son las dos cosas que yo no puedo verificar.

2. **Decidir el rumbo**: la arquitectura v2 está instalada pero sin usar. Toca elegir entre
   - rehacer los 6 NPCs con **KantoNPCs** (salto visual inmediato: Oak con cara de Oak), o
   - montar la primera **cinemática** con `/cutscene preview` para ver de qué es capaz.

3. **La historia**: hay un contexto preparado en [contexto-para-gemini.md](contexto-para-gemini.md)
   por si quieres una narrativa reescrita antes de seguir construyendo.

---

## Pendientes que arrastramos

- **Rotar las dos claves de API** — la de Pterodactyl y la de MineSkin. Llevan todo el día
  circulando por el chat.
- **`git init`** y un `.gitignore` en condiciones. El repositorio tiene 1,1 GB sin control
  de versiones.
- **Pregeneración del mundo** parada en 30,4%: `python scripts/pregen.py`
- El **resourcepack de voces ya está publicado**, así que quien abra el launcher se baja
  las 32 líneas. Si te preocupa el destripe, se saca del manifiesto y se vuelve a meter el
  día del evento.

---

## Los generadores

Nada está escrito a mano: todo se regenera.

```
python evento/build_dp.py      motor + avances de misión
python evento/build_npcs.py    NPCs y diálogos
python evento/build_rp.py      resourcepack de voces
```
