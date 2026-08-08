# -*- coding: utf-8 -*-
"""Genera el capitulo de FTB Quests que da acceso al evento.

    python evento/build_quests.py

Y se sube a  config/ftbquests/quests/chapters/el_rastro_de_luna.snbt
seguido de   /ftbquests reload quests


QUE HACE ESTE CAPITULO
======================
Es el filtro de entrada al evento. Nadie participa sin pasarlo, y al terminarlo
el jugador recibe la etiqueta `ev_apto`, que es lo que el motor del evento mira
para dejarle entrar.

    ┌──────────────────────────────────────────────────────────────┐
    │  EL RASTRO DE LUNA                                           │
    │                                                              │
    │   ⚙  El informe            leer  ──────────────┐             │
    │                                                │             │
    │   ⬡  TANQUE    Granbull    capturar niv. 60  ──┤ en cadena:  │
    │   ⬡  DANO      Machamp     capturar niv. 60  ──┤ cada una    │
    │   ⬡  SOPORTE   Ribombee    capturar niv. 60  ──┤ abre la     │
    │                                                │ siguiente   │
    │   ⚙  Acreditacion          reclamar  ──────────┘             │
    │        └─> tag @s add ev_apto                                │
    └──────────────────────────────────────────────────────────────┘

El flujo completo, del libro al evento:

    admin: [ REPARTIR LIBROS ]
              │  give @a ftbquests:book
              v
    jugador: abre el libro, lee el informe, lo marca
              │
              v
    admin: [ POBLAR ZONAS ]
              │  48 Pokemon de nivel 60 en tres sitios conocidos
              v
    jugador: captura Granbull -> Machamp -> Ribombee
              │  cada captura desbloquea la siguiente mision
              v
    jugador: reclama la ACREDITACION
              │  recompensa de tipo `command`:  tag @s add ev_apto
              v
    admin: [ ACREDITADOS ]   <- lista quien lo tiene y quien no
    admin: [ INVITAR ] [ INICIAR ]


POR QUE ESTAS TRES ESPECIES
===========================
No son tres tipos al azar: son tres ROLES elegidos contra los jefes reales del
evento. Los cuatro guardianes son siniestros, y tres de los cuatro pegan en
fisico — solo el Hydreigon de Vex es especial.

    Granbull   TANQUE    Intimidacion baja el ataque de Mightyena, Weavile y
                         Sharpedo nada mas salir. Hada resiste siniestro y es
                         INMUNE a dragon, que es el arma contra Hydreigon.
    Machamp    DANO      130 de ataque, y lucha pega x2 a los cuatro. Lucha
                         puro: volador, psiquico y hada no los usa ningun jefe.
    Ribombee   SOPORTE   Bicho/hada resiste siniestro x0,25 y lucha x0,5. Danza
                         Aleteo sube al equipo y Bola Polen cura al aliado.

Nivel 60 porque los jefes van de 45 a 70. Con un nivel 40 el Hydreigon de Vex
los borra de un golpe.


CUATRO COSAS DEL FORMATO QUE COSTARON DIAS
==========================================
Las cuatro fallan **en silencio**: el capitulo carga, el log dice "N quests", y
nada funciona.

1.  RUTA.  Se sube a `config/ftbquests/quests/`, NO a `world/ftbquests/quests/`.
    La segunda existe, tiene la misma estructura, y el mod no la mira. El
    capitulo estuvo ahi una semana con el libro vacio. La ruta buena la dice el
    propio mod al recargar:

        Loading quests from /home/container/config/ftbquests/quests

2.  IDs POSITIVOS.  FTB los lee como enteros con signo. Si el primer digito hex
    es 8 o mas el numero sale negativo y lo rechaza con `Invalid Object ID`. Los
    IDs de aqui estan fijados a mano y todos empiezan por 0-7.

3.  ESPECIE CON NAMESPACE.  `pokemon: "cobblemon:granbull"`, no `"granbull"`.

4.  TODOS LOS CAMPOS DE LA TAREA, aunque vayan vacios. `abilities: ""`,
    `aspects: ""`, `biome: ""`... Si falta alguno la tarea no engancha y las
    capturas no cuentan nunca. De ahi `tarea_captura()`, que los escribe todos.

Los IDs y el esqueleto salen de un capitulo hecho a mano dentro del juego, que
ya funcionaba. Se conservan tal cual para no perder el progreso de quien lleve
misiones hechas.
"""
import os

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "el_rastro_de_luna.snbt")

NIVEL = 60
T = "\t"

# IDs fijos, heredados del capitulo que ya funcionaba. No se generan: cambiarlos
# borraria el progreso de todo el mundo.
ID_CAPITULO = "1D2697E2E77257FE"


def lista(*txt) -> str:
    return "[" + ", ".join('"' + t.replace('"', r'\"') + '"' for t in txt) + "]"


# ===========================================================================
#  Lenguaje visual
# ===========================================================================
#
# Un color por funcion, igual en las cinco paginas. Sin esto cada mision parece
# de un juego distinto.
#
#   &e&l  encabezados      &f  lo que hay que hacer
#   &7    explicacion      &8&o  voz de Oak       &c  avisos
SEP = "&8&m                                        "


CAPTURAS = [
    dict(
        id="7EF2784A51D4FAA0", tarea="34A6D03D7B3A149D",
        especie="granbull", nombre="Granbull", rol="TANQUE", color="&d",
        icono="cobblemon:fairy_gem", y=-5.0, deps=["530A8DC94688BAEB"],
        lema="El que aguanta",
        porque=[
            "&7Nada mas salir al campo &fbaja el ataque del rival&7.",
            "&7Los tres primeros guardianes pegan en fisico, asi que",
            "&7cada golpe que reciban sera mas flojo.",
            "",
            "&7Y siendo &dhada&7, el dragon de la Doctora Vex",
            "&f&lno puede ni tocarlo&7.",
        ],
        zona=(1238, 64, 508), sitio="la pradera del este",
    ),
    dict(
        id="6F4CFB2D10CD8007", tarea="00000F9806690C3B",
        especie="machamp", nombre="Machamp", rol="DANO", color="&c",
        icono="cobblemon:fighting_gem", y=-3.5,
        deps=["7EF2784A51D4FAA0", "530A8DC94688BAEB"],
        lema="El que rompe",
        porque=[
            "&7El tipo lucha pega &fel doble&7 a todo lo siniestro,",
            "&7y los cuatro guardianes lo son.",
            "",
            "&7Es lucha puro: sus debilidades son volador, psiquico",
            "&7y hada. &f&lNinguno de los cuatro las usa&7.",
        ],
        zona=(1230, 69, 460), sitio="las colinas del norte",
    ),
    dict(
        id="76949A978B9C29ED", tarea="60B7D2575D9920BE",
        especie="ribombee", nombre="Ribombee", rol="SOPORTE", color="&a",
        icono="cobblemon:bug_gem", y=-2.0,
        deps=["7EF2784A51D4FAA0", "6F4CFB2D10CD8007", "530A8DC94688BAEB"],
        lema="El que sostiene",
        porque=[
            "&7Bicho y hada a la vez: resiste lo siniestro a &fla cuarta",
            "&fparte&7 y lo de lucha a la mitad. Aguanta lo que le echen.",
            "",
            "&7Danza Aleteo sube al equipo entero, y &f&lBola Polen",
            "&f&lcura al companero de al lado&7 en mitad del combate.",
        ],
        zona=(1162, 68, 412), sitio="el claro del oeste",
    ),
]


def tarea_captura(c) -> str:
    """La tarea de Cobblemon, con TODOS los campos.

    Los vacios no son relleno: si falta alguno la tarea no engancha y la captura
    no cuenta nunca, sin dar el menor aviso. Y la especie va con namespace.
    """
    return f"""{T}{T}{T}{{
{T}{T}{T}{T}id: "{c['tarea']}"
{T}{T}{T}{T}type: "cobblemon_tasks:cobblemon_task"
{T}{T}{T}{T}action: "catch"
{T}{T}{T}{T}pokemon: "cobblemon:{c['especie']}"
{T}{T}{T}{T}amount: 1L
{T}{T}{T}{T}min_level: {NIVEL}
{T}{T}{T}{T}max_level: {NIVEL}
{T}{T}{T}{T}abilities: ""
{T}{T}{T}{T}aspects: ""
{T}{T}{T}{T}biome: ""
{T}{T}{T}{T}dex_progress: "seen"
{T}{T}{T}{T}dimension: ""
{T}{T}{T}{T}form: ""
{T}{T}{T}{T}gender: ""
{T}{T}{T}{T}held_items: ""
{T}{T}{T}{T}max_turns: 0
{T}{T}{T}{T}moves: ""
{T}{T}{T}{T}natures: ""
{T}{T}{T}{T}poke_ball_used: ""
{T}{T}{T}{T}pokemon_type: ""
{T}{T}{T}{T}raid_tiers: ""
{T}{T}{T}{T}region: ""
{T}{T}{T}{T}shiny: false
{T}{T}{T}{T}targetPlayer: ""
{T}{T}{T}{T}time_max: 24000L
{T}{T}{T}{T}time_min: 0L
{T}{T}{T}{T}trainers: ""
{T}{T}{T}}}"""


def mision_captura(c) -> str:
    x, y, z = c["zona"]
    deps = "\n".join(f'{T}{T}{T}"{d}"' for d in c["deps"])
    desc = lista(
        f"{c['color']}&l{c['lema'].upper()}",
        SEP,
        "",
        *c["porque"],
        "",
        SEP,
        "&e&lQUE HAY QUE HACER",
        f"&fCapturar 1 {c['nombre']} de nivel &e&l{NIVEL}&f.",
        "",
        "&e&lDONDE",
        f"&f  {x}   {y}   {z}",
        f"&8{c['sitio']}",
        "&7Hay dieciseis sueltos y todos del mismo nivel,",
        "&7asi que da igual cual te toque.",
        "",
        SEP,
        "&8&oPuedes usar tus Pokemon de siempre para capturarlo.",
        "&8&oEn la expedicion, estos tres son los que cuentan.",
    )
    return f"""{T}{T}{{
{T}{T}{T}id: "{c['id']}"
{T}{T}{T}x: -1.5d
{T}{T}{T}y: {c['y']}d
{T}{T}{T}shape: "hexagon"
{T}{T}{T}size: 1.3d
{T}{T}{T}title: "{c['color']}&l{c['rol']}&r &f{c['nombre']}"
{T}{T}{T}subtitle: "Captura 1 de nivel {NIVEL}   ·   {x} {y} {z}"
{T}{T}{T}icon: {{ id: "{c['icono']}" }}
{T}{T}{T}description: {desc}
{T}{T}{T}dependencies: [
{deps}
{T}{T}{T}]
{T}{T}{T}min_required_dependencies: {len(c['deps'])}
{T}{T}{T}tasks: [
{tarea_captura(c)}
{T}{T}{T}]
{T}{T}{T}rewards: [
{T}{T}{T}{T}{{
{T}{T}{T}{T}{T}id: "{c['id'][:15]}1"
{T}{T}{T}{T}{T}type: "xp"
{T}{T}{T}{T}{T}xp: 250
{T}{T}{T}{T}}}
{T}{T}{T}]
{T}{T}}}"""


INFORME = f"""{T}{T}{{
{T}{T}{T}id: "530A8DC94688BAEB"
{T}{T}{T}x: -1.5d
{T}{T}{T}y: -6.5d
{T}{T}{T}shape: "gear"
{T}{T}{T}size: 2.0d
{T}{T}{T}title: "&5&lEL RASTRO DE LUNA"
{T}{T}{T}subtitle: "Del escritorio del Profesor Oak"
{T}{T}{T}icon: {{ id: "minecraft:written_book" }}
{T}{T}{T}description: {lista(
    "&8&oHace tres semanas detecte una lectura de energia que no",
    "&8&ocorrespondia a ninguna especie conocida. Fui a verla yo",
    "&8&omismo, convencido de que era un fallo del equipo.",
    "",
    "&8&oNo lo era.",
    "",
    "&8&oEl Equipo Eclipse se la llevo al dia siguiente. Llevo desde",
    "&8&oentonces siguiendo su rastro, y ya se donde termina.",
    "",
    SEP,
    "",
    "&fNo voy a mandar a nadie ahi fuera sin comprobar que puede",
    "&fvolver. Lo que hay al otro lado no son entrenadores: son",
    "&fcuatro guardianes, y los cuatro pelean con Pokemon",
    "&8&lsiniestros&f.",
    "",
    "&7Lo siniestro solo teme tres cosas: la fuerza bruta, los",
    "&7insectos, y lo que no se deja corromper.",
    "",
    "&fTres condiciones. No son negociables.",
    "",
    SEP,
    "&e&lLO QUE PIDE OAK",
    "&f  1.   &dUn tanque&f que aguante el primer golpe",
    "&f  2.   &cUn dano&f que pegue el doble a los cuatro",
    "&f  3.   &aUn soporte&f que mantenga al grupo en pie",
    "",
    "&8&oMarca esta pagina cuando la hayas leido.",
)}
{T}{T}{T}tasks: [
{T}{T}{T}{T}{{
{T}{T}{T}{T}{T}id: "007ABA01C9EC4E00"
{T}{T}{T}{T}{T}type: "checkmark"
{T}{T}{T}{T}{T}title: "He leido el informe"
{T}{T}{T}{T}}}
{T}{T}{T}]
{T}{T}}}"""


ACREDITACION = f"""{T}{T}{{
{T}{T}{T}id: "74D6989CD75EF25F"
{T}{T}{T}x: -1.5d
{T}{T}{T}y: -0.5d
{T}{T}{T}shape: "gear"
{T}{T}{T}size: 2.0d
{T}{T}{T}title: "&6&lACREDITACION DE CAMPO"
{T}{T}{T}subtitle: "El pase a la expedicion"
{T}{T}{T}icon: {{ id: "minecraft:compass" }}
{T}{T}{T}description: {lista(
    "&6&lTRES POKEMON. TRES ROLES. TODOS TUYOS.",
    SEP,
    "",
    "&8&oNo se los di yo. Salieron a buscarlos y volvieron con ellos.",
    "&8&oEso ya me dice bastante.",
    "",
    "&7El &dtanque&7 para los tres primeros guardianes.",
    "&7El &cdano&7 para todos.",
    "&7El &asoporte&7 para el laboratorio, que es donde de verdad",
    "&7van a hacer falta las curaciones.",
    "",
    SEP,
    "&e&lQUE TE DA ESTO",
    "&fEl pase para entrar a la expedicion.",
    "&7Sin el, el rastreador no te llegara aunque te apuntes.",
    "",
    SEP,
    "&8&oNos vemos en el bosque.",
    "&8&o                              - Prof. Oak",
)}
{T}{T}{T}dependencies: [
{T}{T}{T}{T}"7EF2784A51D4FAA0"
{T}{T}{T}{T}"6F4CFB2D10CD8007"
{T}{T}{T}{T}"76949A978B9C29ED"
{T}{T}{T}{T}"530A8DC94688BAEB"
{T}{T}{T}]
{T}{T}{T}min_required_dependencies: 4
{T}{T}{T}tasks: [
{T}{T}{T}{T}{{
{T}{T}{T}{T}{T}id: "5787E98DCAFD88F5"
{T}{T}{T}{T}{T}type: "checkmark"
{T}{T}{T}{T}{T}title: "Solicitar la acreditacion"
{T}{T}{T}{T}}}
{T}{T}{T}]
{T}{T}{T}rewards: [
{T}{T}{T}{T}{{
{T}{T}{T}{T}{T}id: "5787E98DCAFD88F6"
{T}{T}{T}{T}{T}type: "command"
{T}{T}{T}{T}{T}title: "Acreditacion de campo"
{T}{T}{T}{T}{T}icon: {{ id: "minecraft:compass" }}
{T}{T}{T}{T}{T}command: "tag @s add ev_apto"
{T}{T}{T}{T}{T}elevate_perms: true
{T}{T}{T}{T}{T}silent: true
{T}{T}{T}{T}{T}auto: "no_toast"
{T}{T}{T}{T}}}
{T}{T}{T}{T}{{
{T}{T}{T}{T}{T}id: "5787E98DCAFD88F7"
{T}{T}{T}{T}{T}type: "xp"
{T}{T}{T}{T}{T}xp: 1000
{T}{T}{T}{T}}}
{T}{T}{T}]
{T}{T}}}"""


def capitulo() -> str:
    quests = "\n".join([INFORME] + [mision_captura(c) for c in CAPTURAS] + [ACREDITACION])
    return f"""{{
{T}id: "{ID_CAPITULO}"
{T}group: ""
{T}order_index: 0
{T}filename: "el_rastro_de_luna"
{T}title: "&5&lEL RASTRO DE LUNA"
{T}subtitle: {lista("&7Requisitos de campo para la expedicion")}
{T}icon: {{ id: "minecraft:heart_of_the_sea" }}
{T}default_quest_shape: ""
{T}default_hide_dependency_lines: false
{T}images: [ ]
{T}quest_links: [ ]
{T}quests: [
{quests}
{T}]
}}
"""


def main() -> int:
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    texto = capitulo()

    if texto.count("{") != texto.count("}"):
        raise SystemExit(f"SNBT descuadrado: {texto.count('{')} abre, {texto.count('}')} cierra")
    if texto.count("[") != texto.count("]"):
        raise SystemExit("corchetes descuadrados")
    # Todos los IDs tienen que caber en un long con signo.
    import re
    for i in set(re.findall(r'"([0-9A-F]{16})"', texto)):
        if int(i, 16) > 0x7FFFFFFFFFFFFFFF:
            raise SystemExit(f"ID negativo, FTB lo rechazaria: {i}")

    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)

    print(f"  {SALIDA}  ({len(texto)} bytes)")
    print(f"    capitulo   EL RASTRO DE LUNA")
    print(f"    misiones   informe + {len(CAPTURAS)} capturas + acreditacion")
    for c in CAPTURAS:
        x, y, z = c["zona"]
        print(f"      {c['rol']:<8} {c['nombre']:<10} nivel {NIVEL}   {x} {y} {z}")
    print(f"    entrega    tag @s add ev_apto")
    print()
    print("  Subir a  config/ftbquests/quests/chapters/  y  /ftbquests reload quests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
