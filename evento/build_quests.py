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

POR QUE ESTOS TRES TIPOS
------------------------
No son al azar. Todos los guardianes del evento son **siniestros**:

    Grum    Mightyena           siniestro
    Sable   Weavile             siniestro / hielo
    Nix     Sharpedo            agua / siniestro
    Vex     Hydreigon, Gengar   siniestro / fantasma

El tipo siniestro tiene exactamente tres debilidades: **lucha, bicho y hada**.
Asi que las tres misiones no son un peaje — son el equipo que hace falta para
ganar. Quien las hace llega armado sin que nadie se lo explique.

Y como son tres capturas obligatorias, el minimo de tres Pokemon sale solo.

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

# Rango de nivel exigido. Los guardianes van de 27 a 55 y el jefe de incursion
# es nivel 45; por debajo de 30 la expedicion es un paseo por el bosque con
# Pokemon que se desmayan de un golpe.
NIVEL_MIN = 30
NIVEL_MAX = 45


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
TIPOS = [
    ("lucha", "fighting", "&cLUCHA", "minecraft:iron_axe", -2.0,
     "Los siniestros no aguantan un golpe directo.",
     "Trae algo que sepa pegar de cerca."),
    ("bicho", "bug", "&aBICHO", "minecraft:honeycomb", 0.0,
     "Pequeno, rapido, y con ventaja sobre la oscuridad.",
     "Subestimado por todos menos por quien lo ha sufrido."),
    ("hada", "fairy", "&dHADA", "minecraft:allium", 2.0,
     "El unico tipo del que la oscuridad no puede alimentarse.",
     "Luna aprobaria la eleccion."),
]


def tarea_captura(tipo_id: str, tipo_cobblemon: str) -> str:
    return f"""			{{
				id: "{ident('t_' + tipo_id)}"
				type: "cobblemon_tasks:cobblemon_task"
				action: "catch"
				pokemon_type: "{tipo_cobblemon}"
				min_level: {NIVEL_MIN}
				max_level: {NIVEL_MAX}
				amount: 1L
			}}"""


def mision_captura(tipo_id, tipo_cobblemon, etiqueta, icono, y, desc1, desc2) -> str:
    return f"""		{{
			id: "{ident('q_' + tipo_id)}"
			x: 0.0d
			y: {y}d
			shape: "circle"
			size: 1.0d
			title: "{etiqueta} &r&fUn aliado de tipo {tipo_id}"
			icon: "{icono}"
			description: {lineas(
                desc1,
                desc2,
                "",
                f"&7Captura &f1 Pokemon de tipo {tipo_id}&7 de nivel &f{NIVEL_MIN}-{NIVEL_MAX}&7.",
                "",
                "&8No vale sacarlo de la caja: tiene que ser una captura nueva.")}
			dependencies: ["{ident('q_informe')}"]
			tasks: [
{tarea_captura(tipo_id, tipo_cobblemon)}
			]
			rewards: [
				{{
					id: "{ident('r_' + tipo_id)}"
					type: "xp"
					xp: 150
				}}
			]
		}}"""


# ---------------------------------------------------------------------------
#  El capitulo entero
# ---------------------------------------------------------------------------
def capitulo() -> str:
    capturas = ",\n".join(mision_captura(*t) for t in TIPOS)
    dep_capturas = ", ".join(f'"{ident("q_" + t[0])}"' for t in TIPOS)

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
    print(f"    misiones   informe + {len(TIPOS)} capturas + acreditacion")
    print(f"    nivel      {NIVEL_MIN}-{NIVEL_MAX}")
    print(f"    tipos      {', '.join(t[1] for t in TIPOS)}")
    print(f"    entrega    tag @s add ev_apto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
