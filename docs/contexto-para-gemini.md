# Contexto del evento — para pasar a otro modelo

Copia todo lo que hay debajo de la línea y pégalo. Está escrito para que quien lo lea
tenga el cuadro completo: la historia, lo que ya existe, y sobre todo **lo que el motor
del juego permite y lo que no**, que es donde casi todos los diseños se rompen.

---

# ENCARGO

Quiero que diseñes un **evento de rol narrativo** para un servidor privado de Minecraft
con el mod Cobblemon (Pokémon). Es para unos 15-40 amigos, dura unas 3 horas, y lo
protagoniza un streamer llamado **AlejandroReport**.

Lo que ya tengo funciona pero es **plano**: diálogos cortos, poca tensión, poca
personalidad en los villanos, y la estructura es demasiado lineal. Quiero que lo
reescribas para que sea **una aventura de verdad**: épica, con giros, con personajes que
den miedo o den pena, y con momentos que la gente recuerde y comente después.

## Qué quiero de ti

1. **Historia reescrita**, con estructura de acto real: enganche, escalada, punto de no
   retorno, clímax y cierre emocional.
2. **Diálogos completos y escritos**, no resúmenes. Cada personaje con voz propia.
3. **Interfaces gráficas propias y espectaculares.** Esto es prioritario. No quiero que la
   información llegue como mensajitos de chat: quiero **arte**. HUD propio, marcos
   ornamentados, hologramas, terminales que se hackean, pantallas de misión. Lee el
   apartado de interfaces más abajo: hay más margen del que la gente cree, y quiero que
   lo exprimas. Descríbeme **cómo se ve cada cosa**, no solo qué dice.
4. **Momentos de espectáculo**: qué ve y qué oye la gente en los cinco o seis instantes
   que tienen que ponerles la piel de gallina.
5. **Ritmo**: qué pasa cada quince minutos para que nadie se aburra.

---

# EL MUNDO

**Servidor**: «PokeReport: Luna Eternal». Minecraft 1.21.1 con Fabric y el modpack
Cobbleverse (118 mods). Privado, entre amigos. Español **latino** — nunca de España,
nada de «vosotros», «tenéis» ni «coged».

**Jugadores**: 15-40 personas, nivel de juego variado. Algunos son veteranos de Pokémon y
otros entran por primera vez. El evento no puede depender de saber jugar bien.

**AlejandroReport**: el streamer. El evento es un regalo para él. Tiene que acabar con
él como protagonista, pero sin que los demás se sientan público.

---

# LUNA — el corazón de todo

Luna es un **Pokémon inventado para este servidor**, creado a partir de la perra real de
AlejandroReport. Ya está implementada en el juego con su modelo, sus estadísticas y su
entrada de Pokédex.

**Su lore, y esto es lo que hay que honrar:**

> Luna, la Diosa del Amor Incondicional.
>
> Es la fuerza que une a todos los seres vivos. Su poder sana el corazón, inspira
> esperanza y crea vínculos imposibles de romper.
>
> Mientras Arceus dio origen al universo, **Luna le dio el motivo para seguir
> existiendo: el amor**.
>
> De todas las formas que pudo tomar en este mundo, eligió ser la compañera de un solo
> entrenador.

**Datos**: tipo Psíquico/Hada. Ejemplar único, no se reproduce, no aparece salvaje.
Estadísticas base 540 (una legendaria menor).

**La tensión dramática que quiero explotar**: durante casi todo el evento el grupo cree
que rescata a una legendaria nueva. Solo al final descubren **qué salvaron de verdad**.
Ese giro tiene que estar bien plantado desde el principio con pistas que solo se
entienden al releerlas.

---

# LO QUE YA EXISTE (y funciona)

No hace falta rehacerlo, pero puedes reorganizarlo.

## Personajes

| Quién | Papel |
|---|---|
| **Profesor Oak** | El que convoca. Mayor, cálido, culpable de no haber llegado a tiempo |
| **Doctora Vex** | La villana. Científica. Llama a Luna «una anomalía, un error del universo que voy a corregir» |
| **Grum, Sable, Nix** | Tres guardianes del Equipo Eclipse, uno por zona |
| **Guardias del Eclipse** | Tropa del laboratorio |

## Estructura actual (la que quiero que mejores)

- **Acto I** — Oak convoca al grupo y entrega un rastreador
- **Acto II** — Tres señales; en cada una un guardián y un combate
- **Acto III** — Misiones en solitario para descifrar un código
- **Acto IV** — Laboratorio de tres salas, jefe final
- **Acto V** — Se libera a Luna; Alejandro la captura

## Audio ya grabado

**32 líneas del Profesor Oak con voz clonada**, en español latino, ya funcionando en el
juego. Si tu guion cambia mucho el texto de Oak, dímelo claramente para regrabar.

También hay 1.074 gritos de Pokémon con licencia y un grito propio para Luna.

---

# LÍMITES TÉCNICOS — LÉELOS ANTES DE DISEÑAR

Esto lo he comprobado leyendo el código del mod y probando en el servidor. **No son
opiniones.** Un diseño que los ignore no se puede construir.

## Lo que SÍ se puede

- **NPCs con diálogo ramificado**: páginas, opciones múltiples, retratos, saltos entre
  páginas según lo que elija el jugador. La interfaz es la nativa de Cobblemon y se ve
  integrada.
- **Combates contra NPC** con equipo y niveles fijos.
- **Voz sincronizada** con subtítulos, encadenando líneas con sus tiempos exactos.
- **Títulos en pantalla**, subtítulos, barra de acción, mensajes de chat con formato,
  colores y **botones pinchables**.
- **Sonidos** propios en cualquier momento.
- **Detectar**: capturas por especie, combates ganados, subidas de nivel, pescas,
  cercanía a un punto, bloques pisados o usados.
- **Contadores por jugador y globales**, que sobreviven a reinicios.
- **Límites de tiempo** con consecuencias.
- Dar objetos con **nombre e historia propios** (ej. un rastreador que es una brújula).
- Fuegos artificiales, partículas, efectos de estado, teletransportes, cambios de clima
  y de hora.

## Lo que NO se puede

1. **Un NPC no sabe si ha perdido un combate.** El mod no lo expone. Cualquier avance
   que dependa de «cuando derroten a X» tiene que dispararlo un admin con un botón.
   → Diseña asumiendo que **hay un director de escena humano** pulsando cosas.

2. **No se puede filtrar por tipo ni por nivel** al detectar capturas. Solo por especie
   concreta. «Captura un siniestro» hay que escribirlo enumerando las 69 especies
   siniestras.

3. **Los diálogos no pueden ejecutar comandos** con permisos de servidor. Un diálogo
   puede contar cosas y ramificar, pero no puede dar objetos ni cambiar el estado del
   evento por sí solo.

4. **No hay comandos personalizados** tipo `/evento iniciar` sin escribir un mod. Todo va
   por funciones o por botones en el chat.

5. **Los jugadores no pueden separarse mucho**: el mundo tiene chunks cargados limitados y
   la gente se pierde. Las fases en solitario deben ser cortas y con vuelta clara.

## INTERFACES GRÁFICAS — sí se pueden, y quiero que las uses

Esto es importante: **controlo el launcher del servidor**, así que puedo repartir a todos
los jugadores el resourcepack y los mods que hagan falta. Las interfaces no están
limitadas a lo que trae Minecraft de serie. Quiero **interfaces propias y espectaculares**,
y estas son las técnicas reales disponibles:

### Fuentes de mapa de bits con espacios negativos

La técnica que usan los servidores grandes para tener HUD propio sin obligar a nadie a
instalar nada. Se mete una imagen en el resourcepack como si fuera un carácter de fuente,
y con caracteres de anchura negativa se coloca donde sea.

Permite dibujar **cualquier imagen** en cualquier sitio donde haya texto: barras de vida
con arte propio, marcos ornamentados alrededor de los diálogos, sellos del Equipo Eclipse,
mapas holográficos, contadores con números dibujados a mano, retratos de personaje.

**Sitios donde funciona**: títulos en pantalla, subtítulos, barra de acción, chat,
nombres de inventario, libros, nombres de objetos.

### Entidades de visualización (`text_display`, `item_display`, `block_display`)

Hologramas flotantes en el mundo, con escala, rotación, transparencia y color de fondo
propios. Se pueden animar por interpolación.

Sirven para: rótulos gigantes sobre el laboratorio, la cápsula de Luna con texto
holográfico girando, pantallas de ordenador flotando en las salas, marcadores de misión
en el aire, cuentas atrás en tamaño enorme.

### Menús de cofre con objetos de textura propia

Un inventario de cofre puede usarse como menú: cada hueco es un botón con su icono
dibujado por nosotros. Sirve para un «terminal del Eclipse» que se hackea, para elegir
ruta, o para el diario de misiones.

### Libros escritos con páginas pinchables

Un libro puede tener texto con formato y enlaces que ejecutan acciones. Perfecto para
documentos robados, informes de laboratorio o el cuaderno de campo de Oak.

### Mods de cliente, si hacen falta

Puedo añadir cualquier mod al launcher. Si tu diseño pide algo que necesite un mod
concreto, **dilo y lo evalúo** — no lo descartes por miedo a que no se pueda.

**Quiero que el diseño aproveche esto de verdad.** No me sirve «sale un mensaje en el
chat»: quiero saber **cómo se ve**, con qué arte, qué se anima y en qué momento.

---

# LO QUE NO FUNCIONA DEL DISEÑO ACTUAL

Sé sincero con esto al reescribir:

- **Los villanos son planos.** Vex suelta dos frases de científica malvada y ya. Grum,
  Sable y Nix son intercambiables: no tienen historia propia ni motivo distinto.
- **El Acto III mata el ritmo.** Mandar a la gente a hacer recados sueltos durante 40
  minutos, en medio de una historia, rompe la tensión que se acababa de construir.
- **No hay ningún giro.** Todo va en línea recta: te dicen que la secuestraron, la
  persigues, la rescatas. No hay traición, ni engaño, ni una revelación a mitad.
- **El grupo no toma decisiones.** Nunca eligen nada que cambie lo que pasa después.
- **Alejandro no hace nada especial** hasta el último minuto.
- **No hay coste.** Nadie pierde nada, nadie sacrifica nada.

---

# CÓMO QUIERO LA RESPUESTA

1. **Sinopsis** en un párrafo: la historia en cuanto tiene de buena.
2. **Los personajes**, con lo que quieren y lo que ocultan. Especialmente Vex: quiero
   entender por qué hace lo que hace y que casi se le pueda dar la razón.
3. **Escaleta acto por acto**, con minutos y con qué siente el grupo en cada tramo.
4. **Diálogos escritos enteros**, listos para meter en el juego. Marca cuáles llevan voz.
5. **Los momentos de espectáculo**: cinco o seis, descritos como si fueran una escena de
   película — qué se ve en pantalla, qué interfaz aparece, qué se oye, qué partículas,
   qué se mueve.
6. **Diseño de las interfaces**: para cada pantalla propia, descríbeme el arte. Qué
   marco, qué colores, qué tipografía, dónde va cada elemento, qué se anima. Como si se
   lo estuvieras encargando a un ilustrador.
7. **Las decisiones** que toma el grupo y qué cambian.
8. **Qué hace especial a Alejandro** durante todo el evento, no solo al final.

Escríbelo en **español latino**. Y no me des un esquema: dame el texto de verdad, escrito,
listo para usar.
