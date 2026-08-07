# -*- coding: utf-8 -*-
"""Genera los NPCs y dialogos del evento «El Rastro de Luna».

El esquema no esta inventado: sale de leer los ejemplos reales del jar de
Cobblemon 1.7.3 (`data/cobblemon/npcs/sacchi.json`, `npc_presets/battler_test.json`
y `dialogues/sacchi_interaction.json`).

Dos limites del mod, comprobados en su codigo, que condicionan el diseño:

  1. `battleConfiguration` solo admite canChallenge, healAfterwards y
     simultaneousBattles. No hay gancho de "derrotado".
  2. MoLang no expone ninguna funcion tipo `was_defeated_by`.

Es decir: **el NPC no puede saber que ha perdido**. Por eso el avance del evento
lo dispara el admin con `/function evento:senales/completar` al ver caer al
guardian, en vez de fiarlo a algo que el mod no ofrece.

Uso:  python evento/build_npcs.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-Datos-DP.zip")
PACK_FORMAT = 48

ficheros: dict[str, dict] = {}


def npc(ident_corto: str, nombre: str, dialogo: str, equipo=None, skill=5, reto=False) -> None:
    ident = "ev_" + ident_corto
    d = {
        "hitbox": "player",
        "names": [nombre],
        "canDespawn": False,
        "interaction": {"type": "dialogue", "dialogue": f"cobblemon:ev_{dialogo}"},
    }
    if reto:
        # healAfterwards: el jugador sale del combate curado. En un evento de tres
        # horas, obligar a volver al centro Pokemon entre guardianes es tiempo muerto.
        d["battleConfiguration"] = {"canChallenge": True, "healAfterwards": True,
                                    "simultaneousBattles": False}
        d["skill"] = skill
    if equipo:
        # SimplePartyProvider en vez de PoolPartyProvider: el pool sortea y en las
        # pruebas dejaba al NPC sin equipo ("has no Pokemon on Party"). Aqui el
        # equipo es fijo y los niveles exactos, que es lo que quiere un evento
        # guionizado: nadie deberia encontrarse un jefe distinto al del ensayo.
        d["party"] = {
            "type": "simple",
            "isStatic": True,
            "pokemon": [f"{especie} level={nivel}" for especie, nivel in equipo],
        }
    ficheros[f"data/cobblemon/npcs/evento/{ident}.json"] = d


HABLANTES = {
    "npc": {"name": {"type": "expression", "expression": "q.npc.name"}, "face": "q.npc.face();"},
    "player": {"name": {"type": "expression", "expression": "q.player.username"},
               "face": "q.player.face();"},
}


def dialogo(ident_corto: str, paginas: list) -> None:
    ident = "ev_" + ident_corto
    ficheros[f"data/cobblemon/dialogues/evento/{ident}.json"] = {
        "speakers": HABLANTES,
        "pages": paginas,
    }


def pag(pid: str, lineas, entrada, hablante="npc") -> dict:
    return {"id": pid, "speaker": hablante,
            "lines": lineas if isinstance(lineas, list) else [lineas],
            "input": entrada}


def opciones(*pares) -> dict:
    """pares = (texto, accion[, isSelectable])"""
    ops = []
    for p in pares:
        o = {"text": p[0], "value": p[0].lower().replace(" ", "_"), "action": p[1]}
        if len(p) > 2:
            o["isSelectable"] = p[2]
        ops.append(o)
    return {"type": "option", "vertical": True, "options": ops}


COMBATE = ["q.dialogue.close();", "q.npc.start_battle(q.player, 'single');"]
CERRAR = "q.dialogue.close();"


# ===========================================================================
#  Profesor Oak
# ===========================================================================
npc("oak", "Profesor Oak", "oak")
dialogo("oak", [
    pag("saludo", [
        "Entrenadores. Escuchenme bien.",
        "Lo que les voy a contar no esta en ninguna Pokedex.",
    ], "q.dialogue.set_page('historia');"),
    pag("historia", [
        "Hace tres semanas detecte una lectura de energia que no correspondia a ninguna especie conocida.",
        "Fui a verla yo mismo. Era una Pokemon... y me miro como si me conociera de toda la vida.",
        "La llame Luna.",
    ], "q.dialogue.set_page('perdida');"),
    pag("perdida", [
        "Iba a estudiarla al dia siguiente. No llegue a tiempo.",
        "El Equipo Eclipse se la llevo.",
    ], opciones(
        ("Cuente conmigo", "q.dialogue.set_page('rastreador');"),
        ("Que es el Equipo Eclipse?", "q.dialogue.set_page('eclipse');"),
    )),
    pag("eclipse", [
        "Gente que ve a los Pokemon como piezas de laboratorio, no como companeros.",
        "Los dirige una tal doctora Vex. Y creanme: sabe lo que hace.",
    ], "q.dialogue.set_page('rastreador');"),
    pag("rastreador", [
        "Yo ya estoy viejo para esto, muchachos. Ustedes no.",
        "Tomen el rastreador de energia. No es gran cosa, pero apunta hacia ella.",
        "Vayan todos juntos. Y no se separen.",
    ], CERRAR),
])


# ===========================================================================
#  Guardianes del Eclipse
# ===========================================================================
GUARDIANES = [
    ("grum", "Grum", "Bosque", 6,
     [("poochyena", 27), ("mightyena", 30)],
     ["Alto ahi.", "Este bosque es nuestro, y lo que buscan tambien."],
     "Creen que esa cosa es un Pokemon? Es una anomalia. La doctora nos lo explico bien claro."),
    ("sable", "Sable", "Montana", 7,
     [("sneasel", 32), ("weavile", 35)],
     ["Vaya. Grum cayo y aun asi siguen subiendo.", "Tercos. Eso les reconozco."],
     "La doctora Vex lleva anos esperando algo asi. No va a soltarlo porque unos ninos se lo pidan."),
    ("nix", "Nix", "Costa", 8,
     [("carvanha", 37), ("sharpedo", 40)],
     ["Hasta aqui llegaron.", "Detras de mi esta la entrada, y no la van a ver nunca."],
     "Saben que le va a hacer? Va a abrirla para ver que tiene dentro. Y yo pienso ayudarla."),
]

for ident, nombre, zona, skill, equipo, saludo, desafio in GUARDIANES:
    npc(ident, f"{nombre} del Eclipse", ident, equipo=equipo, skill=skill, reto=True)
    dialogo(ident, [
        pag("saludo", saludo, opciones(
            ("Apartate", "q.dialogue.set_page('reto');"),
            ("Por que hacen esto?", "q.dialogue.set_page('motivo');"),
        )),
        pag("motivo", [desafio], "q.dialogue.set_page('reto');"),
        pag("reto", [
            "Si tanto la quieren, quitenmela.",
            "Un combate. Uno de ustedes contra mi.",
        ], opciones(
            ("Acepto el combate", COMBATE, "c.npc.can_battle;"),
            ("Todavia no", CERRAR),
        )),
    ])


# ===========================================================================
#  Guardias del laboratorio
# ===========================================================================
npc("guardia", "Guardia del Eclipse", "guardia", skill=7, reto=True,
    equipo=[("golbat", 40), ("muk", 41), ("houndoom", 43)])
dialogo("guardia", [
    pag("saludo", [
        "Zona restringida. Den media vuelta.",
    ], opciones(
        ("Combatir", COMBATE, "c.npc.can_battle;"),
        ("Retirarse", CERRAR),
    )),
])


# ===========================================================================
#  Doctora Vex
# ===========================================================================
npc("vex", "Doctora Vex", "vex", skill=9, reto=True, equipo=[
    ("crobat", 47), ("magnezone", 48), ("drapion", 50),
    ("hydreigon", 55), ("weavile", 51), ("gengar", 53),
])
dialogo("vex", [
    pag("saludo", [
        "Asi que son ustedes.",
        "Los que llevan toda la tarde rompiendo mis cosas.",
    ], "q.dialogue.set_page('anomalia');"),
    pag("anomalia", [
        "Saben lo que tengo aqui? No es un Pokemon.",
        "Es una anomalia. Un error del universo que yo voy a corregir.",
    ], opciones(
        ("No es un error. Es de alguien.", "q.dialogue.set_page('desprecio');"),
        ("Vamos al combate", "q.dialogue.set_page('combate');"),
    )),
    pag("desprecio", [
        "De alguien. Que enternecedor.",
        "Y no, no me interesa su opinion al respecto.",
    ], "q.dialogue.set_page('combate');"),
    pag("combate", [
        "Seis Pokemon. Los mejores que he criado.",
        "Vengan de tres en tres si quieren. Me da igual el orden en que caigan.",
    ], opciones(
        ("Combatir", COMBATE, "c.npc.can_battle;"),
        ("Esperar", CERRAR),
    )),
])


# ===========================================================================
#  Empaquetado
# ===========================================================================
def main() -> int:
    meta = {"pack": {"pack_format": PACK_FORMAT,
                     "description": "PokeReport · El Rastro de Luna — NPCs y diálogos"}}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, indent=2, ensure_ascii=False))
        for ruta, datos in ficheros.items():
            z.writestr(ruta, json.dumps(datos, indent=2, ensure_ascii=False))

    npcs = sum(1 for k in ficheros if "/npcs/" in k)
    dial = sum(1 for k in ficheros if "/dialogues/" in k)
    print(f"   {SALIDA}")
    print(f"   {npcs} NPCs, {dial} diálogos, {os.path.getsize(SALIDA)/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
