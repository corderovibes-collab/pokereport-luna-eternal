# Rendimiento y optimización

Máquina: **16 GB RAM · 300% CPU (3 núcleos) · 180 GB disco**. El cuello de botella real de este
servidor son los **3 núcleos**, no la RAM ni el disco. Todo lo de abajo está pensado con eso.

## 1. Memoria: el fallo que traía el servidor de fábrica

El egg del panel arranca siempre así, y **no se puede editar desde la API de cliente**:

```
java -Xms128M -Xmx16384M -jar server.jar
```

Eso pone el heap de Java en **16384 MB dentro de un contenedor de 16384 MB**. No deja nada para
el *metaspace* (103 mods son ~600 MB), el *code cache*, las pilas de hilos, los buffers de red ni
las estructuras del recolector de basura. Mientras el heap va medio vacío no pasa nada; el día
que se llene de verdad, el contenedor se pasa del límite y **Docker mata el servidor**. Es la
causa número uno de "se cae solo y no hay error en el log".

### Solución aplicada

`server.jar` ya no es el lanzador de Fabric: es un **puente de 2,7 KB**
([código fuente](../server-pack/launcher/Launcher.java)) que lee
[`jvm-args.txt`](../server-pack/config/jvm-args.txt) y arranca el Fabric real
(`fabric-server-launch.jar`) como proceso hijo con la memoria acotada.

- Hereda `stdin`/`stdout`/`stderr`, así que **la consola del panel funciona igual** y el botón
  de parar sigue enviando `stop` correctamente.
- Propaga `SIGTERM` al hijo, así que al parar desde el panel **el mundo se guarda bien**.
- Devuelve el mismo código de salida, así que el panel detecta caídas.

Probado en local antes de subirlo: flags aplicadas, `stdin` pasa al hijo, código de salida
propagado.

### El reparto de los 16 GB

| Concepto | Memoria |
|---|---|
| Heap de Java (`-Xms`/`-Xmx`, fijos e iguales) | 12 288 MB |
| Metaspace, code cache, hilos, red, GC | ~3 900 MB de margen |

Medido con el servidor arrancado y pregenerando: **13,2 GB de 16 GB**. Margen real de ~2,8 GB.

Además van las **flags de Aikar** (perfil ≤12 GB), que es el estándar para servidores modded:
reparten el heap para que el GC haga pausas cortas y frecuentes en vez de parones largos, que
es lo que se nota como tirón. Y `-XX:ActiveProcessorCount=3`, porque si no la JVM ve los
núcleos del **host** y sobredimensiona todos los pools de hilos (GC, C2ME, ThreadTweak).

> Si algún día TaroHosting te deja editar el comando de arranque, lo limpio es pedirles
> `java @jvm-args.txt -jar fabric-server-launch.jar nogui` y borrar el puente.

## 2. Mods de optimización

### Los que ya traía Cobbleverse (verificados y activos)

| Mod | Qué hace |
|---|---|
| **Lithium** | Optimiza la lógica del servidor: IA de mobs, física, colisiones |
| **C2ME** | Carga y generación de chunks en paralelo. 13 módulos activos |
| **ScalableLux** | Motor de luz multihilo (el sucesor de Starlight) |
| **Krypton** | Optimiza la pila de red |
| **FerriteCore** | Reduce mucho la memoria que ocupan los blockstates |
| **ModernFix** | Arranque más rápido y menos memoria |
| **zFastNoise** | Generación de ruido acelerada |
| **Debugify / PacketFixer** | Corrigen bugs de vanilla y paquetes que desconectan clientes |
| **Neruina / NotEnoughCrashes** | Aíslan un error en una entidad o bloque en vez de tumbar el servidor |

Cobbleverse ya viene bien montado en esto. Lo que **no** traía es lo de abajo.

### Los 7 que he añadido

| Mod | Por qué |
|---|---|
| **Chunky** 1.4.23 | Pregeneración de chunks. Es *el* mod que pediste: sin él, cada jugador que explora genera terreno en vivo y eso es el tirón más gordo que existe |
| **VMP** 0.2.0-beta.7.172 | Optimiza el envío de chunks y el seguimiento de jugadores. Es justo lo de *"que entren y les cargue todo rápido"*. Del mismo autor que C2ME, diseñados para ir juntos |
| **spark** 1.10.109 | Profiler. Sin esto, diagnosticar un lag es adivinar |
| **ThreadTweak** 0.1.5 | Ajusta prioridades y tamaño de los pools de hilos. Con 3 núcleos importa mucho quién tiene prioridad |
| **Alternate Current** 1.9.0 | Motor de redstone bastante más eficiente |
| **Clumps** 19.0.0.1 | Agrupa los orbes de experiencia. En Cobbleverse llueve XP de combates, y cada orbe es una entidad |
| **Get It Together, Drops!** 1.3.1 | Agrupa los items del suelo. Menos entidades = más TPS |

### Los que descarté a propósito

No todo lo que pone "optimización" conviene. Estos los dejé fuera con motivo:

| Mod | Por qué no |
|---|---|
| **Noisium** | Toca la generación de mundo igual que C2ME. Se pisan y da problemas. C2ME ya cubre esto |
| **ServerCore** | Sus funciones asíncronas se solapan con VMP. Dos mods peleándose por lo mismo es peor que ninguno |
| **Let Me Despawn** | Cambia el despawn de mobs. En un servidor de Pokémon eso puede hacer desaparecer Pokémon salvajes de forma rara. No compensa |
| **FasterRandom** | Ganancia mínima y toca el RNG, con Terralith y Repurposed Structures de por medio no vale el riesgo |
| **Sodium, Iris, EntityCulling, ImmediatelyFast, More Culling, BadOptimizations** | Son de **cliente**. Cada jugador ya los tiene con el modpack; en el servidor no pintan nada |

> Nota sobre *plugins*: esto es **Fabric**, no Paper/Spigot, así que **no admite plugins de
> Bukkit**. Todo lo equivalente se hace con mods. No es una limitación real: para Fabric 1.21.1
> existe todo lo que necesitas.

## 3. `server.properties`

Lo relevante y por qué:

| Ajuste | Valor | Motivo |
|---|---|---|
| `view-distance` | 8 | Lo que se ve. Con 3 núcleos, subir de 8 se paga caro por jugador |
| `simulation-distance` | 6 | Lo que *tickea*. Es lo que de verdad cuesta CPU |
| `sync-chunk-writes` | **false** | Deja de bloquear el hilo principal en cada escritura a disco. Mejora gorda y gratis |
| `max-tick-time` | **-1** | Desactiva el watchdog. En modded, un chunk lento hacía que el watchdog matara el servidor sin motivo real. Neruina y NotEnoughCrashes ya cubren los errores de verdad |
| `allow-flight` | **true** | **Imprescindible en Cobblemon**: los Pokémon voladores montables hacen que el anticheat de vanilla expulse a los jugadores si esto está en `false` |
| `enforce-secure-profile` | false | Evita expulsiones por firma de chat con mods |
| `spawn-protection` | 0 | Si no, nadie puede construir cerca del spawn |
| `entity-broadcast-range-percentage` | 100 | Bajarlo ahorra red, pero hace que los Pokémon aparezcan y desaparezcan a media distancia. En este pack no compensa |
| `max-players` | 40 | Estimación para 16 GB / 3 núcleos. Ajustable |

> **Margen disponible**: con solo 12 jugadores previstos y el tick en 0,2 ms de 50, sobra CPU
> para subir `view-distance` de 8 a **10** y que se vea bastante más lejos. Son ~50% más de
> chunks por jugador (289 → 441), perfectamente asumible para 12 personas.
> Conviene hacerlo **cuando termine la pregeneración**, porque hay que reiniciar: editar
> `server.properties`, reiniciar, y reanudar con `chunky continue`.

## 4. Pregeneración de chunks

Medido en este servidor concreto, no estimado a ojo: **~30 chunks/s** y **~5 KB por chunk**.

En marcha (radio 5000 overworld, 2000 nether, 1500 end, centrado en 0,0, forma cuadrada):

```bash
python scripts/pregen.py --status      # ver avance
```

El avance también queda en [`docs/pregen-progress.log`](pregen-progress.log).

Se ejecuta **una dimensión detrás de otra** a propósito: lanzarlas a la vez repartiría los
mismos 3 núcleos entre las tres sin ganar tiempo total, y multiplicaría la presión sobre el heap.

Decidiste **mundo infinito, sin world border**. Consecuencia a tener presente: el que se aleje
más de 5000 bloques del centro saldrá de la zona precargada y ahí sí generará terreno en vivo.
Si algún día ves quejas de tirones por exploración, se amplía en caliente sin parar el servidor:

```
chunky world minecraft:overworld
chunky radius 8000
chunky start
```

Chunky no repite lo ya generado, así que ampliar solo cuesta el anillo nuevo.

## 5. Por qué el panel marca ~13 GiB de 16 (y por qué está bien)

El panel **no miente**: la API devuelve exactamente lo mismo y esos 12,9 GiB son memoria que el
contenedor tiene reservada de verdad. Lo que pasa es que **panel y spark miden cosas distintas**:

| Lo que ves | Qué mide | Valor |
|---|---|---|
| Panel / API | Toda la memoria que el contenedor le ha pedido al sistema | **12,9 GiB / 16 GiB** |
| `spark healthreport` | Cuánto del heap contiene datos vivos ahora mismo | **5,2 GB / 12 GB** |

Los dos son ciertos a la vez. En `jvm-args.txt` está puesto `-Xms12288M` igual que `-Xmx`, más
`-XX:+AlwaysPreTouch`: la JVM **reclama los 12 GB enteros al arrancar** y no se los devuelve
nunca al sistema. De esos 12 GB, ahora mismo 5,2 tienen datos y el resto es espacio libre
*dentro* del heap que Java reutiliza sin volver a pedir nada. Los ~0,9 GiB que faltan hasta
12,9 son la memoria nativa de la JVM (metaspace, code cache, hilos, buffers de red).

**La consecuencia práctica**: ese número se queda plano en ~12,9-13,2 GiB tanto con 0 jugadores
como con 12. No va a subir hasta 16 ni te vas a quedar sin memoria. Lo que se mueve por dentro
es el 5,2 / 12 GB.

Es a propósito. Si quitara el pre-reservado, la gráfica empezaría baja e iría subiendo — más
bonita de ver, pero **peor**: cada vez que el heap crece hay una pausa, y al ir trepando hacia
los 16 GB sí acabaría en un OOM-kill. Un número plano y predecible es justo lo que se busca.

> Si aun así prefieres que la gráfica refleje el uso real, se cambia `-Xms12288M` por `-Xms4096M`
> y se quita `-XX:+AlwaysPreTouch` en [`jvm-args.txt`](../server-pack/config/jvm-args.txt).
> Funciona igual, solo que con algún micro-tirón cuando el heap crece.

El **242% de CPU** también es real, y es la **pregeneración**, no el juego: está usando los
núcleos libres a propósito. En cuanto termine, baja mucho.

Ojo con un detalle de `spark`: la línea `Disk usage: 531 GB / 925 GB` es el disco **físico del
nodo** de TaroHosting, no el tuyo. Lo tuyo es lo que marca el panel: ~1 GB de tus 180 GB.

## 6. Avisos conocidos del log (revisados, ninguno es problema)

| Aviso | Veredicto |
|---|---|
| `Empty or non-existent pool: bca:paths`, `bca:store_workers`, `bca:feature/decor`, `bca:feature/berries` | **Bug del propio Cobblemon Additions**, no de la instalación. Las estructuras piden `bca:paths` pero el mod define `bca:default/paths`, `bca:dark/paths`, `bca:stores/store_workers`… Solo afecta a algunas piezas decorativas dentro de los pueblos. **Comprobado con `/locate`: los pueblos se generan bien** (`bca:village/default_mid` a 1910 bloques, `fighting_large`, `witch_hut`). No se toca: adivinar a qué pool debería apuntar cada uno metería edificios equivocados en el mundo de forma permanente |
| `Tried to load a block entity for ... part=top / half=upper` | Benigno. Es la mitad **superior** de bloques de dos alturas (el PC de Cobblemon, las estatuas). El block entity solo vive en la mitad de abajo |
| `Can't keep up! Running Xms behind` | Sale al ejecutar un `/locate` de una estructura lejana, que bloquea el hilo mientras busca. Con jugadores normales no aparece |

## 7. ¿Aguanta 12 jugadores?

Sí, y con margen de sobra. No es una estimación: son medidas tomadas en este servidor
**mientras pregeneraba a 32 chunks/s**, que es la carga más dura que se le puede meter.

| Métrica | Medido ahora | Límite | Margen |
|---|---|---|---|
| TPS | **20.0** en las 5 ventanas | 20 es el máximo | perfecto |
| Duración de tick | **0,2 ms** de mediana (máx. 7,3) | 50 ms | usando el **0,4%** del presupuesto |
| Heap | **6,5 GB** | 12 GB | 45% libre |
| CPU | 66-70% | 300% | más del doble sin usar |
| Disco | 875 MB | 180 GB | 0,5% |

Lo importante de esos números: los **6,5 GB de heap y el 70% de CPU son casi todos de la
pregeneración**, no del juego. Cuando termine, el consumo en reposo caerá mucho, y esos recursos
quedan libres para los jugadores.

Para dimensionar 12 jugadores:

- **Memoria**: con `view-distance=8`, cada jugador mantiene ~289 chunks. Aunque los 12 se
  repartan por el mapa sin solaparse, son ~3.500 chunks, del orden de **0,5 GB**. Contra 12 GB
  de heap, no hay debate.
- **CPU**: aquí está el matiz que importa. Minecraft ejecuta la lógica del juego en **un solo
  hilo**, así que de los 3 núcleos, uno lleva el tick y los otros dos hacen chunks, red y E/S.
  Con el tick en 0,2 ms de 50 disponibles, hay muchísimo colchón. 12 jugadores tirarían de
  quizá 5-15 ms.
- **Disco**: 180 GB para un mundo que va por 875 MB. Irrelevante.

**Lo único que puede tumbarlo** no es el número de jugadores, sino la cantidad de **entidades**:
granjas gigantes de mobs, cientos de items en el suelo, o mucha gente con equipos completos de
Pokémon fuera de la Poké Ball a la vez. Por eso están puestos Clumps y Get It Together Drops.

Referencia práctica: este servidor iría bien hasta ~30-40 jugadores. Los 12 no son problema.
Si algún día el TPS baja de 18, `spark profiler --timeout 60` dice exactamente qué lo causa.

## 8. Cómo comprobar que va fino

Con **spark**, desde la consola del panel o en el juego siendo OP:

```
spark tps                  # TPS y uso de CPU. 20.0 es perfecto, por debajo de 18 hay que mirar
spark profiler --timeout 60    # dice qué mod concreto se está comiendo el tick
spark heapsummary          # qué está ocupando la memoria
```

Si el TPS baja, mirar en este orden: número de entidades cargadas → `spark profiler` → bajar
`simulation-distance` a 5 antes que tocar `view-distance`.
