# -*- coding: utf-8 -*-
"""Genera los dialogos del evento en formato Blabber.

Esquema tomado del oficial de Ladysnake
(https://ladysnake.org/schemas/blabber/dialogue.schema.json) y de los ejemplos
reales del repositorio, no inventado.

Por que Blabber y no los dialogos de Cobblemon:

  - Los lanza el motor con `/blabber dialogue start <id> <jugadores>`, que corre
    con permisos de servidor. Los de Cobblemon solo se abren al hacer clic en un
    NPC, y desde dentro no pueden ejecutar nada (run_command va con permisos del
    jugador). Aqui se invierte: el evento decide cuando se habla y con quien.
  - Diseno `blabber:rpg`, con retrato grande.
  - Ilustraciones que son entidades de verdad y siguen al jugador con la mirada.

Uso:  python evento/build_blabber.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-Blabber-DP.zip")
PACK_FORMAT = 48

ficheros: dict[str, dict] = {}

FIN = {"text": "", "choices": [], "type": "end_dialogue"}


def retrato(entidad: str) -> dict:
    """Retrato animado: una entidad de verdad, mirando hacia el texto."""
    return {
        "type": "blabber:fake_entity",
        "id": entidad,
        "anchor": "before_main_text",
        "x1": -55, "y1": -135, "x2": 55, "y2": 5,
        "size": 65,
        "stare_at_x": 50, "stare_at_y": 10,
    }


def dialogo(ident: str, estados: dict, entidad: str, inicio: str = "inicio") -> None:
    estados = dict(estados)
    estados["end"] = FIN
    # Todo estado que no diga lo contrario lleva el retrato.
    for k, v in estados.items():
        if k != "end" and "illustrations" not in v:
            v["illustrations"] = ["retrato"]
    ficheros[f"data/evento/blabber/dialogues/{ident}.json"] = {
        "layout": {"type": "blabber:rpg"},
        "start_at": inicio,
        "states": estados,
        "illustrations": {"retrato": retrato(entidad)},
    }


def op(texto: str, siguiente: str) -> dict:
    return {"text": texto, "next": siguiente}


NPC = "cobblemon:npc"


# ===========================================================================
#  Profesor Oak — la llamada
# ===========================================================================
dialogo("oak_llamada", {
    "inicio": {
        "text": "Entrenadores. Escúchenme bien. Lo que les voy a contar no está en ninguna Pokédex.",
        "choices": [op("Le escuchamos, profesor.", "descubrimiento")],
    },
    "descubrimiento": {
        "text": "Hace tres semanas detecté una lectura de energía que no correspondía a ninguna especie "
                "conocida. Ni una sola. Fui a verla yo mismo, convencido de que era un fallo del equipo.",
        "choices": [op("¿Y qué era?", "encuentro")],
    },
    "encuentro": {
        "text": "No lo era. Era una Pokémon. Pequeña, tranquila… y me miró como si me conociera de toda "
                "la vida. La llamé Luna.",
        "choices": [
            op("¿Dónde está ahora?", "perdida"),
            op("¿Le miró a usted? ¿Cómo?", "mirada"),
        ],
    },
    "mirada": {
        "text": "Como quien reconoce a alguien. No como un Pokémon salvaje mira a un desconocido. "
                "Llevo cincuenta años en esto y jamás vi nada parecido. Lo apunté como una anomalía "
                "del registro… y ojalá le hubiera dado más importancia.",
        "choices": [op("¿Dónde está ahora?", "perdida")],
    },
    "perdida": {
        "text": "Iba a estudiarla al día siguiente. No llegué a tiempo. El Equipo Eclipse se la llevó.",
        "choices": [
            op("¿Quiénes son el Equipo Eclipse?", "eclipse"),
            op("Vamos a traerla de vuelta.", "rastreador"),
        ],
    },
    "eclipse": {
        "text": "Gente que ve a los Pokémon como piezas de laboratorio, no como compañeros. "
                "Los dirige una tal doctora Vex. Y créanme: sabe exactamente lo que hace.",
        "choices": [op("Entonces no hay tiempo que perder.", "rastreador")],
    },
    "rastreador": {
        "text": "Yo ya estoy viejo para esto, muchachos. Ustedes no. Tomen el rastreador de energía: "
                "lo armé anoche con lo que tenía. No es gran cosa, pero apunta hacia ella. "
                "Vayan todos juntos. Y no se separen.",
        "choices": [op("Cuente con nosotros.", "end")],
    },
}, NPC)


# ===========================================================================
#  Guardianes del Eclipse
# ===========================================================================
GUARDIANES = {
    "grum": (
        "Alto ahí. Este bosque es nuestro, y lo que buscan también.",
        "¿Creen que esa cosa es un Pokémon? Es una anomalía. La doctora nos lo explicó bien claro, "
        "y desde entonces duermo mejor.",
    ),
    "sable": (
        "Vaya. Grum cayó y aun así siguen subiendo. Tercos. Eso se lo reconozco.",
        "La doctora Vex lleva años esperando algo así. No va a soltarlo porque unos niños se lo pidan.",
    ),
    "nix": (
        "Hasta aquí llegaron. Detrás de mí está la entrada, y no la van a ver nunca.",
        "¿Saben qué le va a hacer? Va a abrirla para ver qué tiene dentro. Y yo pienso ayudarla.",
    ),
}

for ident, (saludo, motivo) in GUARDIANES.items():
    dialogo(f"{ident}_reto", {
        "inicio": {
            "text": saludo,
            "choices": [op("Apártate.", "reto"), op("¿Por qué hacen esto?", "motivo")],
        },
        "motivo": {"text": motivo, "choices": [op("No pienso discutir contigo.", "reto")]},
        "reto": {
            "text": "Si tanto la quieren, quítenmela. Un combate. Uno de ustedes contra mí.",
            "choices": [op("Acepto.", "end"), op("Todavía no.", "end")],
        },
    }, NPC)


# ===========================================================================
#  Guardia del laboratorio
# ===========================================================================
dialogo("guardia_alto", {
    "inicio": {
        "text": "Zona restringida. Den media vuelta y nadie tendrá que redactar un informe.",
        "choices": [op("Apártate.", "end"), op("Nos vamos.", "end")],
    },
}, NPC)


# ===========================================================================
#  Doctora Vex
# ===========================================================================
dialogo("vex_encuentro", {
    "inicio": {
        "text": "Así que son ustedes. Los que llevan toda la tarde rompiendo mis cosas.",
        "choices": [op("Suelta a Luna.", "anomalia")],
    },
    "anomalia": {
        "text": "¿Saben lo que tengo aquí? No es un Pokémon. Es una anomalía. Un error del universo "
                "que yo voy a corregir.",
        "choices": [
            op("No es un error. Es de alguien.", "desprecio"),
            op("Basta de charla.", "combate"),
        ],
    },
    "desprecio": {
        "text": "De alguien. Qué enternecedor. ¿Y qué pasará con ese alguien el día que ella no esté? "
                "Yo he visto lo que hace la pérdida. Lo estoy arreglando.",
        "choices": [op("Eso no te da derecho.", "combate")],
    },
    "combate": {
        "text": "Seis Pokémon. Los mejores que he criado. Vengan de tres en tres si quieren: "
                "me da exactamente igual el orden en que caigan.",
        "choices": [op("Vamos allá.", "end")],
    },
}, NPC)


# ===========================================================================
#  Empaquetado
# ===========================================================================
def main() -> int:
    meta = {"pack": {"pack_format": PACK_FORMAT,
                     "description": "PokeReport · El Rastro de Luna — diálogos Blabber"}}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, indent=2, ensure_ascii=False))
        for ruta, datos in ficheros.items():
            z.writestr(ruta, json.dumps(datos, indent=2, ensure_ascii=False))

    print(f"   {SALIDA}")
    print(f"   {len(ficheros)} diálogos, {os.path.getsize(SALIDA)/1024:.1f} KB")
    for r in ficheros:
        print("     evento:" + r.split("/")[-1][:-5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
