# -*- coding: utf-8 -*-
"""Genera el capitulo de FTB Quests que da acceso al evento.

EL PROBLEMA QUE RESUELVE
------------------------
Hay que comprobar que cada participante llega preparado: Pokemon de un tipo
concreto, dentro de un rango de nivel, y capturados **para la ocasion** (no vale
sacarlos de la caja).

Los avances de Minecraft no sirven: el disparador `catch_pokemon` de Cobblemon
filtra por **especie** y nada mas. Ni tipo ni nivel.

Cobblemon Quests Reloaded si:

    action: "catch"        el jugador tiene que capturarlo, no solo tenerlo
    pokemon_type: "..."    filtro por tipo
    min_level / max_level  rango de nivel
    amount                 cuantos

POR QUE TRES ESPECIES CONCRETAS Y NO TRES TIPOS
-----------------------------------------------
La primera version pedia "un tipo lucha cualquiera". Eso dejaba presentarse con
algo inservible y llamarlo preparacion.

Ahora se pide el Pokemon exacto, y cada uno cubre un rol contra los jefes
reales del evento — que son todos siniestros, y tres de los cuatro pegan en
fisico. Ver el bloque CAPTURAS mas abajo.

Ademas los tres estan soltados en zonas conocidas, al mismo nivel, para que el
grupo entero los capture junto. La mision lleva las coordenadas dentro.

EL PUENTE CON EL MOTOR DEL EVENTO
---------------------------------
La ultima mision entrega una recompensa de tipo `command` que ejecuta:

    tag @s add ev_apto

A partir de ahi el motor distingue tres estados por jugador:

    sin tag                       ni se ha apuntado
    ev_participa                  apuntado pero SIN acreditar
    ev_participa + ev_apto        listo

`admin/revisar` los lista, y el arranque avisa de quien va sin acreditar.

Uso:  python evento/build_quests.py
"""
import hashlib
import os

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "preparativos.snbt")

def ident(semilla: str) -> str:
    """ID de 16 hex en mayusculas, que es lo que usa FTB Quests.

    Derivado del nombre y no aleatorio: asi regenerar el fichero no rompe el
    progreso de quien ya lleve misiones hechas.
    """
    return hashlib.sha1(f"pokereport:{semilla}".encode()).hexdigest()[:16].upper()


def lineas(*txt) -> str:
    return "[" + ", ".join('"' + t.replace('"', r'\"') + '"' for t in txt) + "]"


# ---------------------------------------------------------------------------
#  Las tres capturas
# ---------------------------------------------------------------------------
#
# No son tres tipos sueltos: son tres ROLES, y cada uno esta elegido contra los
# jefes concretos del evento.
#
# Todos los guardianes son siniestros y tres de los cuatro pegan en fisico
# —solo el Hydreigon de Vex es especial—. De ahi:
#
#   Granbull   TANQUE    Intimidacion baja el ataque de Mightyena, Weavile y
#                        Sharpedo nada mas salir. Hada resiste siniestro y es
#                        INMUNE a dragon, que es el arma contra Hydreigon.
#   Machamp    DANO      130 de ataque, y lucha pega x2 a los cuatro. Lucha
#                        puro: volador, psiquico y hada no los usa ningun jefe.
#   Ribombee   SOPORTE   Bicho/hada resiste siniestro x0,25 y lucha x0,5. Danza
#                        Aleteo sube al equipo y Bola Polen cura al aliado.
#
# La tarea filtra por ESPECIE, no por tipo. Antes pedia "un tipo lucha
# cualquiera", y eso permitia presentarse con algo inservible. Ahora se pide el
# Pokemon exacto, que ademas es el que hay soltado en su zona.
#
# El nivel tambien cambia: 60 en vez de 30-45. Los jefes van de 45 a 70; con un
# nivel 40 el Hydreigon de Vex los borra de un golpe.
NIVEL_CAPTURA = 60

CAPTURAS = [
    ("granbull", "Granbull",  "TANQUE",  "&d", "minecraft:pink_petals", -2.0,
     (1238, 64, 508),
     "Intimidacion les baja el ataque a Grum, Sable y Nix nada mas salir.",
     "Y siendo hada, el dragon de Vex no puede ni tocarlo."),
    ("machamp",  "Machamp",   "DANO",    "&c", "minecraft:iron_axe", 0.0,
     (1230, 69, 460),
     "Ciento treinta de ataque, y lucha pega el doble a los cuatro.",
     "Lo que le hace dano a el, ninguno de ellos lo usa."),
    ("ribombee", "Ribombee",  "SOPORTE", "&a", "minecraft:honeycomb", 2.0,
     (1162, 68, 412),
     "Aguanta lo que le echen: resiste siniestro a la cuarta parte.",
     "Y su Bola Polen cura al companero de al lado."),
]


def tarea_captura(especie: str) -> str:
    return f"""			{{
				id: "{ident('t_' + especie)}"
				type: "cobblemon_tasks:cobblemon_task"
				action: "catch"
				pokemon: "{especie}"
				min_level: {NIVEL_CAPTURA}
				max_level: {NIVEL_CAPTURA}
				amount: 1L
			}}"""


def mision_captura(especie, nombre, rol, color, icono, y, pos, desc1, desc2) -> str:
    x, yy, z = pos
    return f"""		{{
			id: "{ident('q_' + especie)}"
			x: 0.0d
			y: {y}d
			shape: "circle"
			size: 1.0d
			title: "{color}&l{rol} &r&f{nombre}"
			icon: "{icono}"
			description: {lineas(
                desc1,
                desc2,
                "",
                f"&7Captura &f1 {nombre}&7 de nivel &f{NIVEL_CAPTURA}&7.",
                "",
                "&e&lDONDE:",
                f"&f  {x}  {yy}  {z}",
                "&7Hay dieciseis sueltos. Van todos al mismo nivel,",
                "&7asi que da igual cual te toque.",
                "",
                "&8Puedes usar tus Pokemon de siempre para capturarlo.")}
			dependencies: ["{ident('q_informe')}"]
			tasks: [
{tarea_captura(especie)}
			]
			rewards: [
				{{
					id: "{ident('r_' + especie)}"
					type: "xp"
					xp: 150
				}}
			]
		}}"""


# ---------------------------------------------------------------------------
#  El capitulo entero
# ---------------------------------------------------------------------------
def capitulo() -> str:
    capturas = ",\n".join(mision_captura(*c) for c in CAPTURAS)
    dep_capturas = ", ".join(f'"{ident("q_" + c[0])}"' for c in CAPTURAS)

    return f"""{{
	id: "{ident('cap_preparativos')}"
	group: ""
	order_index: 0
	filename: "preparativos"
	title: "&5&lPROTOCOLO LUNA"
	icon: "minecraft:compass"
	default_quest_shape: "circle"
	default_hide_dependency_lines: false
	subtitle: {lineas("Requisitos de campo para la expedicion")}
	quests: [
		{{
			id: "{ident('q_informe')}"
			x: -3.0d
			y: 0.0d
			shape: "hexagon"
			size: 1.5d
			title: "&5&lEl Rastro de Luna"
			icon: "minecraft:written_book"
			description: {lineas(
                "&7Del escritorio del &fProfesor Oak&7:",
                "",
                "&fHace semanas que el bosque no suena igual. Alguien esta",
                "&fapagando algo que llevaba encendido mucho tiempo.",
                "",
                "&fNo voy a mandar a nadie ahi fuera sin comprobar que puede",
                "&fvolver. Tres condiciones. No son negociables.",
                "",
                "&8Marca esta pagina cuando la hayas leido.")}
			tasks: [
				{{
					id: "{ident('t_informe')}"
					type: "checkmark"
					title: "He leido el informe"
				}}
			]
		}},
{capturas},
		{{
			id: "{ident('q_acreditacion')}"
			x: 3.0d
			y: 0.0d
			shape: "gear"
			size: 2.0d
			title: "&6&lACREDITACION DE CAMPO"
			icon: "minecraft:compass"
			description: {lineas(
                "&7Tres Pokemon. Tres tipos. Todos capturados por ti.",
                "",
                "&fLos guardianes que vais a encontrar son siniestros, y el",
                "&ftipo siniestro solo teme tres cosas: la fuerza bruta, los",
                "&finsectos y lo que no se deja corromper.",
                "",
                "&fYa las llevas encima. Ahora si.",
                "",
                "&a&lReclama la acreditacion para poder entrar al evento.")}
			dependencies: [{dep_capturas}]
			tasks: [
				{{
					id: "{ident('t_acreditacion')}"
					type: "checkmark"
					title: "Solicitar la acreditacion"
				}}
			]
			rewards: [
				{{
					id: "{ident('r_acreditacion')}"
					type: "command"
					title: "Acreditacion de campo"
					icon: "minecraft:compass"
					command: "tag @s add ev_apto"
					elevate_perms: true
					silent: true
					auto: "no_toast"
				}},
				{{
					id: "{ident('r_acreditacion_xp')}"
					type: "xp"
					xp: 500
				}}
			]
		}}
	]
}}
"""


def main() -> int:
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    texto = capitulo()
    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)

    # Comprobacion barata pero que atrapa lo que de verdad suele romperse:
    # llaves descuadradas por una f-string mal cerrada.
    if texto.count("{") != texto.count("}"):
        raise SystemExit(f"SNBT descuadrado: {texto.count('{')} abre, {texto.count('}')} cierra")

    print(f"  {SALIDA}  ({len(texto)} bytes)")
    print(f"    capitulo   PROTOCOLO LUNA")
    print(f"    misiones   informe + {len(CAPTURAS)} capturas + acreditacion")
    print(f"    nivel      {NIVEL_CAPTURA}")
    print(f"    especies   {', '.join(c[1] for c in CAPTURAS)}")
    print(f"    entrega    tag @s add ev_apto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
