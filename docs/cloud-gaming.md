# Cloud gaming: ¿se puede jugar Cobbleverse en una VM en la nube?

Análisis de viabilidad de [kmille36/Colab-Cloud-Gaming](https://github.com/kmille36/Colab-Cloud-Gaming)
y de las alternativas reales, medido contra la máquina desde la que se juega hoy.

## Veredicto en una línea

**El proyecto de Colab está muerto y además no resolvería tu problema.** Está archivado desde el
18/06/2026, viola el ToS de Colab explícitamente, y —lo más importante— Colab da **2 vCPU**, que es
justo el recurso del que Cobbleverse va escaso. Ganarías GPU y perderías CPU.

Lo que sí funciona está en [Opciones reales](#opciones-reales-ordenadas-por-relación-coste-resultado).

## 1. Qué es exactamente ese proyecto

No es una "VM gamer". Es un notebook de Colab que, sobre el runtime de Linux con T4:

| Pieza | Función |
|---|---|
| Contenedor + escritorio virtual | Un display X sin monitor físico (la T4 no tiene salida de vídeo) |
| **Sunshine** (host) | Captura el escritorio y lo codifica con NVENC de la T4 |
| **Moonlight** (cliente) | Lo que abres en tu PC para ver y jugar |
| **Tailscale / Cloudflare Tunnel** | El túnel para llegar al puerto 47990, porque Colab no expone puertos |
| **Steam** | Lo que instala; el proyecto está construido alrededor de Steam, no de Java |
| `silence.m4a` | Audio en bucle para engañar al detector de inactividad de Colab |

Ese último punto —un fichero de audio silencioso cuya única razón de existir es evitar que Google
te desconecte— resume bien la naturaleza del proyecto: es un *workaround*, no una plataforma.

### Los dos ejecutables son binarios ofuscados

Esto no se ve desde la página del repo y conviene saberlo. `ColabSteam` (15 KB) y `colab-moonweb`
(24 KB) **no son scripts**: son ejecutables **ELF x86-64**. Al extraerles las cadenas aparecen 61
símbolos, todos de libc, y una firma inconfundible:

```
E: neither argv[0] nor $_ works.
```

Ese mensaje es de **shc** (*Shell Script Compiler*), que coge un script bash, lo **cifra con RC4**
y lo empotra dentro de un ELF que lo descifra en memoria y lo pasa al shell. Cero cadenas de
aplicación: no hay forma de leer qué hace sin desofuscarlo.

Y la celda 3 del notebook te ofrece **montar tu Google Drive justo antes de ejecutarlo como root**:

```python
Mount_Google_Drive = False #@param {type:"boolean"}
...
!wget -q .../ColabSteam && chmod +x ColabSteam && ./ColabSteam
```

No estoy afirmando que el binario haga nada malicioso — no lo sé, y ese es exactamente el problema.
Es código que no se puede auditar, ejecutándose como root, con acceso opcional a tu Drive.
Por eso la reconstrucción de [`cloud-gaming/`](../cloud-gaming/) está escrita en claro.

## 2. Por qué hoy no funciona

Cinco hechos, todos verificables:

1. **Repositorio archivado el 18 de junio de 2026**, en solo lectura. El autor lo abandonó.
2. **Los issues cerrados dicen exactamente qué pasó**: `#6 It doesnt work anymore`,
   `#14 Runtime always get disconnected`, `#11 High latency with Cloudflare tunnel`,
   `#18 Cloudflare Tunnel Error`, `#9 No me funciona`. Es el patrón clásico de Google cerrando
   la puerta y el proyecto persiguiéndola hasta rendirse.
3. **Colab prohíbe esto por escrito.** El FAQ oficial lista entre las acciones prohibidas
   *"using a remote desktop or SSH"* y *"connecting to remote proxies"*, y añade que esas sesiones
   *"may be terminated at any time without warning"*. No es una zona gris.
4. **El riesgo no es perder la partida, es perder la cuenta.** La cuenta de Colab es tu cuenta de
   Google: Gmail, Drive, YouTube, el Azure/Microsoft que tengas enlazado. Google ya ha baneado
   proyectos enteros en Colab por uso no interactivo. No merece la pena.
5. **El límite práctico es 4 h/día** (el propio README lo dice) y el disco se borra entero al
   terminar. Cobbleverse son 239 MB de `.mrpack` + 249 mods + compilar shaders **en cada sesión**,
   o restaurar un `backup.tar.gz` de decenas de GB desde Drive antes de poder jugar.

## 3. La causa raíz: no hay ruta para el vídeo

Por encima de todo lo anterior hay un bloqueo estructural que no depende de la versión del script
ni de que alguien mantenga el repo. Es una cadena de hechos, cada uno consecuencia del anterior:

1. El contenedor de Colab **no tiene `CAP_NET_ADMIN`** en su *bounding set*. Lo imponen su perfil
   de AppArmor (`datalabvm enforce`) y su filtro seccomp.
2. Sin esa capability **no se puede crear una interfaz TUN**, aunque consigas crear el fichero
   `/dev/net/tun` con `mknod`. El error es `CreateTUN: operation not permitted`.
3. Sin TUN **no hay Tailscale, ni WireGuard, ni ninguna VPN**. Es el
   [issue #634 de Tailscale](https://github.com/tailscale/tailscale/issues/634), abierto en 2020
   y todavía sin resolver.
4. Colab **tampoco expone puertos entrantes**: no hay IP pública ni port-forward.
5. Luego el único transporte posible es un **túnel HTTP/TCP saliente** (Cloudflare Tunnel, ngrok).
6. Y el vídeo de Moonlight va por **UDP**. Meter vídeo en tiempo real por TCP provoca
   *head-of-line blocking*: cada paquete perdido **congela la imagen** hasta que se retransmite,
   en vez de producir un microglitch y seguir.

El punto 6 es el issue **#11** del repo, literal: *"High latency with Cloudflare tunnel"*. No era
un bug que alguien pudiera arreglar; era la arquitectura tocando fondo.

> Esto es verificable en tu propio runtime en 30 segundos con
> [`cloud-gaming/diagnostico.py`](../cloud-gaming/diagnostico.py). No hace falta creerme.

## 4. El problema técnico que nadie menciona

Aquí está el fondo del asunto, y es específico de Minecraft:

> **Minecraft Java con mods es un juego limitado por CPU de un solo hilo, no por GPU.**

El *tick* del servidor y del cliente, la lógica de los 249 mods, la generación de chunks y el
*meshing* de Sodium corren mayoritariamente en un hilo. Y Colab te da:

| | Colab free (T4) | Tu portátil |
|---|---|---|
| CPU | **2 vCPU** Xeon ~2,2 GHz, sin turbo, compartidos | i7-8565U, 4c/8t, turbo hasta 4,6 GHz |
| Rendimiento monohilo | Bajo (núcleo de datacenter compartido) | **Claramente superior** |
| RAM | 12–13 GB | 16 GB en doble canal |
| GPU | T4 (muy superior) | UHD 620 (el cuello de botella real) |
| Persistencia | Ninguna | Disco D: con 140 GB libres |

Con 2 vCPU tienes que repartir entre: el juego, el escritorio virtual, Sunshine y el túnel. En
Cobbleverse eso significa *stutter* constante al cargar chunks y en los combates Pokémon — que es
precisamente cuando más partículas y entidades hay. **Cambiarías FPS bajos estables por FPS altos
con tirones**, que subjetivamente es peor.

Añadido: **tu launcher no correría ahí.** `launcher/electron-builder.yml` solo construye target
`nsis` para Windows x64. Colab es Linux. Tendrías que usar la Modrinth App de Linux con el
`.mrpack` a mano, cada sesión.

## 5. Latencia medida desde tu conexión

Medido con `Test-Connection`, 4 paquetes, hoy:

| Destino | RTT medio |
|---|---|
| Tu servidor MC (Miami) | **61 ms** |
| AWS us-east-1 (Virginia) | **83 ms** |
| Cloudflare / Google (nodo local) | 18–26 ms |

Interpretación para streaming: al RTT de red hay que sumarle captura + codificación + decodificación
+ presentación, unos **15–25 ms** más. Un cloud gaming en Virginia te daría **~100 ms de input lag**
total; en Miami, **~80 ms**.

Eso es jugable en Minecraft (no es un shooter competitivo), pero se nota: el lag no afecta solo a
las acciones, afecta al **movimiento de cámara con el ratón**, que es mucho más perceptible. Y no
es acumulativo con los 61 ms al servidor — si la VM está en Miami, la VM juega a ~0 ms del servidor
y tú ves el resultado con ~80 ms de retraso.

## 6. Lo que realmente te está pasando

Tu problema no es que necesites un PC gamer en la nube. Es esto, y está en tu propio
[docs/cliente.md](cliente.md):

> *"Shaders (Complementary) — Solo con GPU dedicada. Puede costar la mitad de los FPS."*

**Complementary Unbound sobre una UHD 620 es injugable**, sin discusión: la iGPU no tiene ni ancho
de banda de memoria ni potencia de sombreado para un shader de ese nivel. Con shaders vas a estar
en un dígito de FPS hagas lo que hagas.

Sin shaders, con Sodium y distancia 8, una UHD 620 en doble canal (que ya tienes: 2×8 GB) mueve
Cobbleverse **razonablemente**. La estimación realista es 35–55 FPS a 1080p con los ajustes de tu
propia guía, y por encima de 60 si bajas a 1600×900.

**Antes de gastar un euro, hay que medir eso.** Si sin shaders vas a 45 FPS, no necesitas nube:
necesitas aceptar jugar sin shaders.

## Opciones reales, ordenadas por relación coste-resultado

| # | Opción | Coste | Latencia | Windows / tu launcher | Veredicto |
|---|---|---|---|---|---|
| 0 | **Optimizar tu portátil** | 0 € | 61 ms al server | Nativo | **Empieza aquí, siempre** |
| 1 | **AirGPU** | 0,65 $/h (T4) + 3,50 $/mes 50 GB | ~80–100 ms | ✅ Sí, con disco persistente | Mejor opción si de verdad hace falta nube |
| 2 | **Shadow PC** | 34–55 $/mes fijo | ~80–100 ms | ✅ Sí | Sin datacenter en Latinoamérica; cuota mensual |
| 3 | **VM propia GCP/AWS + Sunshine** | ~0,20–0,55 $/h | ~83 ms | ✅ Sí, control total | Legal y potente, pero es un proyecto de infra |
| 4 | Colab Pro + notebook | 9,99 $/mes | ~80–100 ms | ❌ Linux, 2 vCPU | Ver nota abajo |
| 5 | vast.ai | 0,16 $/h | Variable | ❌ Docker/Linux, sin persistencia | No sirve para jugar |
| 6 | GeForce NOW | 10–20 $/mes | Baja | ❌ | **No soporta Minecraft Java.** Descartado |
| 7 | **PC/GPU de segunda mano** | 350–500 € una vez | 61 ms | Nativo | Se amortiza en ~12 meses vs. opción 2 |

Números de la opción 1, que es la que recomendaría si hay presupuesto:

| Horas/mes | Coste total |
|---|---|
| 20 h | ~16,50 $/mes |
| 40 h | ~29,50 $/mes |
| 80 h | ~55,50 $/mes |

### Dos notas de precisión

**Sobre GCP gratis:** el trial de 300 $ **no permite GPUs**. La documentación de Google es explícita:
con una cuenta de trial no facturable *no puedes añadir GPUs ni pedir aumento de cuota*. Hay que
pasar a cuenta de pago primero (conservas el crédito sin usar, 91 días). Mucha gente vende esto como
"cloud gaming gratis" y es falso.

**Sobre Colab Pro:** el texto del FAQ prohíbe el escritorio remoto *"from managed Colab runtimes
running free of charge, **without a positive Colab compute unit balance**"*. Literalmente, con
saldo de unidades esa frase concreta deja de aplicar, y ~10 $ dan unas 55 h de T4 (≈0,18 $/h), que
es el precio más bajo de la tabla. **Pero sigue siendo Linux, sigue siendo 2 vCPU, sigue sin haber
persistencia y sigue habiendo otras cláusulas de uso interactivo.** Lo menciono por rigor, no como
recomendación.

## Ruta recomendada

1. **Medir**: arrancar Cobbleverse **sin shaders**, distancia 8, con los 5 mods de
   [`client-pack/extra-optimizacion/`](../client-pack/) instalados, y mirar el F3.
2. Si sale **> 40 FPS**: no hay nada que resolver en la nube. Ajustar y jugar.
3. Si sale **< 30 FPS**: revisar primero plan de energía en *Máximo rendimiento*, 6 GB a Java 21,
   Discord y Chrome cerrados, resolución 1600×900, sin Fresh Animations.
4. Solo si tras eso sigue mal, y hay presupuesto: **AirGPU** por horas. Instalas ahí tu launcher
   `.exe` tal cual, disco persistente, sin trucos ni riesgo de baneo.
5. Si el uso va a superar ~40 h/mes de forma sostenida, sale más barato **comprar hardware**.

---

*Última revisión: 5 de agosto de 2026.*
