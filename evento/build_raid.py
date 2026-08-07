# -*- coding: utf-8 -*-
"""Genera los jefes de incursion (raid) del evento.

Por que raid y no un entrenador de RCT:

  Un combate de entrenador es 1 contra 1. Con doce personas eso significa once
  mirando. Una incursion es lo contrario: **todos entran a la vez**, cada uno
  aporta un Pokemon, y el jefe escala de vida segun cuantos sean.

Lo que aporta el mod (`cobblemonraiddens`):

  - Arena instanciada en su propia dimension: el mundo no se toca.
  - Animos compartidos (Ataque / Defensa / Curacion) — juego cooperativo real.
  - Escudos por umbral de vida, que obligan a coordinarse.
  - Reparto de recompensa **por dano hecho** (asi esta la config del servidor).

Todo campo que aqui se define **pisa** al de `config/cobblemonraiddens/tier_*.json5`,
asi que el aforo de 12 sale del propio jefe y no hay que tocar la configuracion
global ni reiniciar el servidor.

`weight: 0.0` es deliberado: mantiene al jefe fuera de la tabla de aparicion
natural. Solo existe donde nosotros lo coloquemos.

COMO SE COLOCA
--------------
    /crd dens 1890 64 259 boss cobblemonraiddens:grum_eclipse

**El namespace no es opcional.** Sin `cobblemonraiddens:` el mod no avisa de que
no encuentra al jefe: lanza una excepcion y solo se ve "An unexpected error
occurred", que no dice nada. Despista porque los ficheros de este datapack no
llevan namespace en el nombre.

Para quitarlo, `setblock <pos> minecraft:air replace` (con `replace` y no
`destroy`, que si no suelta el cristal como objeto).

Colocado en el campamento de la senal 1, en **1890, 64, 259**.

Uso:  python evento/build_raid.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-Raid-DP.zip")
PACK_FORMAT = 48

# Aforo del evento. El mod trae 4 por defecto en todos los tiers.
AFORO = 12

ficheros: dict[str, dict] = {}


def jefe(ident, *, especie, nivel, movimientos, habilidad, tipo, tier,
         barra, escala=1.0, vida=8.0, vida_por_jugador=1.08,
         guion=None, dinero=8000, rasgos=None, aforo=AFORO):
    """Define un jefe de incursion.

    `vida` multiplica la vida base del Pokemon; `vida_por_jugador` la vuelve a
    multiplicar por cada participante extra.

    Calibrado con una prueba real: en solitario y con un solo Pokemon, un x25
    solo perdia el 10% de vida. Como la vida crece con cada participante, doce
    personas no pegan doce veces mas rapido en terminos relativos — con aquellos
    numeros el grupo habria perdido.

        x25 y 1,15 por jugador  ->  10% en solitario  ->  12 personas al 26%. Derrota.
        x8  y 1,08 por jugador  ->  30% en solitario  ->  12 personas al 150-190%. Victoria.

    Las dos cifras en solitario estan medidas en el servidor, no estimadas. La
    regla para reajustar, si alguna vez hay que repetir esto:

        margen del grupo  =  % en solitario  x  12  /  (1,08^11)
                          =  % en solitario  x  5,2

    O sea que **un 20% en solitario es el minimo** para que doce personas ganen.
    Por debajo de eso, aflojar.

    Ante la duda se afloja: perder al primer guardian del evento arruina la
    escena, y siempre se puede volver a apretar si resulta facil.
    """
    d = {
        "pokemon": {
            "species": especie,
            "level": nivel,
            "ability": habilidad,
            "moves": movimientos,
        },
        "raid_tier": tier,
        "raid_type": tipo,
        # Fuera de la tabla de aparicion natural: este jefe solo sale si lo
        # colocamos a mano.
        "weight": 0.0,

        "boss_bar_text": barra,
        "scale": escala,

        "max_players": aforo,
        "raid_party_size": 1,
        # Sin limite de victorias: si el grupo pierde o hay que repetir la
        # escena, el cristal sigue sirviendo. El valor por defecto (3) dejaria
        # el campamento muerto a mitad del evento.
        "max_clears": -1,
        "max_cheers": 3,

        "health_multi": vida,
        "multiplayer_health_multi": vida_por_jugador,
        "currency": dinero,
    }
    if rasgos:
        d["pokemon"]["aspects"] = rasgos
    if guion:
        d["script"] = guion
    ficheros[f"data/cobblemonraiddens/raid/boss/{ident}.json"] = d


# ===========================================================================
#  Senal 1 — el bosque.  El Mightyena de Grum
# ===========================================================================
#
# Primer encuentro del evento, asi que ensena las reglas sin castigar:
#
#   60%  escudo + lluvia   -> hay que romper el escudo entre todos
#   45%  limpia las mejoras del grupo y sube su ataque
#   30%  cae el escudo     -> ventana para pegar fuerte
#   15%  ultimo arreon
#
# Nivel 45 contra equipos de 30-40, pero son doce contra uno.
GUION_GRUM = {
    "hp:0.60": ["SHIELD_UP", "SET_RAIN"],
    "hp:0.45": ["RESET_PLAYER", "BOSS:ATK:1"],
    "hp:0.30": ["SHIELD_DOWN"],
    "hp:0.15": ["BOSS:ATK:1", "BOSS:SPE:2"],
}

jefe(
    "grum_eclipse",
    especie="mightyena",
    nivel=45,
    habilidad="intimidate",
    # Colmillo igneo y carantona cubren acero y lucha, que es lo que le
    # sacarian los equipos tipicos a un siniestro.
    movimientos=["crunch", "playrough", "firefang", "snarl"],
    tipo="DARK",
    tier="TIER_FIVE",
    barra="Mightyena de Grum",
    escala=1.8,
    guion=GUION_GRUM,
)


# La misma pelea con Dinamax. Va aparte a proposito: depende de Mega Showdown,
# y si esa via fallara no queremos que se lleve por delante al jefe bueno.
jefe(
    "grum_eclipse_max",
    especie="mightyena",
    nivel=45,
    habilidad="intimidate",
    movimientos=["crunch", "playrough", "firefang", "snarl"],
    tipo="DARK",
    tier="TIER_FIVE",
    barra={"text": "Mightyena de Grum", "color": "dark_purple", "bold": True},
    escala=1.0,          # Dinamax ya lo agranda; no hay que sumar escala
    guion=GUION_GRUM,
)
ficheros["data/cobblemonraiddens/raid/boss/grum_eclipse_max.json"]["raid_feature"] = "dynamax"


# ===========================================================================
#  Senal 2 — la montana.  El Weavile de Sable
# ===========================================================================
#
# Segundo encuentro, asi que aprieta un poco mas que Grum: nivel 52 en vez de
# 45, un escudo mas y una granizada que le sube la defensa especial.
#
# Weavile es siniestro/hielo, o sea que suma las debilidades de los dos tipos:
# lucha, bicho, hada, acero, fuego y roca. El PROTOCOLO LUNA les hizo capturar
# los tres primeros, asi que llegan servidos — pero el hielo pega mas fuerte,
# y a nivel 52 con Danza Espada duele de verdad.
#
# La vida sube solo de 8 a 10: la regla dice que el 30% en solitario da victoria
# con margen, y este tiene que costar mas sin llegar a ser injusto.
jefe(
    "sable_eclipse",
    especie="weavile",
    nivel=52,
    habilidad="pressure",
    movimientos=["iciclecrash", "nightslash", "swordsdance", "iceshard"],
    tipo="ICE",
    tier="TIER_FIVE",
    barra="Weavile de Sable",
    escala=1.8,
    vida=10.0,
    dinero=12000,
    guion={
        "hp:0.70": ["SHIELD_UP", "SET_SNOW"],
        "hp:0.55": ["RESET_PLAYER", "BOSS:ATK:1"],
        "hp:0.40": ["SHIELD_DOWN"],
        "hp:0.25": ["SHIELD_UP", "BOSS:SPE:1"],
        "hp:0.10": ["SHIELD_DOWN", "BOSS:ATK:2"],
    },
)


# ===========================================================================
#  Senal 3 — la costa.  El Sharpedo de Nix
# ===========================================================================
#
# Tercero y ultimo antes del laboratorio, asi que es el mas duro de los tres:
# nivel 58 y vida x12. Sigue estando por debajo del umbral que haria perder al
# grupo — la regla dice que basta con pasar del 20% en solitario.
#
# Sharpedo es agua/siniestro y lleva Piel Tosca: cada golpe cuerpo a cuerpo le
# devuelve dano a quien pega. Eso obliga a variar y no darle sin pensar, que es
# justo lo que hace el grupo cuando ya lleva dos incursiones ganadas.
jefe(
    "nix_eclipse",
    especie="sharpedo",
    nivel=58,
    habilidad="roughskin",
    movimientos=["crunch", "aquajet", "icefang", "screech"],
    tipo="WATER",
    tier="TIER_FIVE",
    barra="Sharpedo de Nix",
    escala=1.7,
    vida=12.0,
    dinero=16000,
    guion={
        "hp:0.75": ["SHIELD_UP", "SET_RAIN"],
        "hp:0.60": ["RESET_PLAYER", "BOSS:ATK:1"],
        "hp:0.45": ["SHIELD_DOWN"],
        "hp:0.30": ["SHIELD_UP", "BOSS:SPE:2"],
        "hp:0.15": ["SHIELD_DOWN", "BOSS:ATK:1"],
    },
)


# ===========================================================================
#  Acto IV — el laboratorio.  El Hydreigon de la Doctora Vex
# ===========================================================================
#
# El climax. Va a TIER_SEVEN, que es el unico tier que el mod deja vacio a
# proposito para jefes propios: haz de luz mas intenso, mejores recompensas y
# su propio logro.
#
# Nivel 70 y vida x16, bastante por encima de Nix. Aun asi la regla dice que
# doce personas ganan: lo que hace duro este combate no es la vida, son las
# siete fases: dos escudos seguidos y una limpieza de mejoras justo antes del
# ultimo tramo.
#
# Hydreigon es siniestro/dragon. El siniestro sigue cayendo ante lucha, bicho
# y hada —lo que el PROTOCOLO LUNA les hizo capturar—, pero el dragon suma
# hielo y dragon. Quien llegue aqui con el equipo del principio lo va a notar.
jefe(
    "vex_eclipse",
    especie="hydreigon",
    nivel=70,
    habilidad="levitate",
    movimientos=["darkpulse", "dragonpulse", "flamethrower", "nastyplot"],
    tipo="DRAGON",
    tier="TIER_SEVEN",
    barra={"text": "Hydreigon de la Doctora Vex", "color": "dark_purple", "bold": True},
    escala=1.6,
    vida=16.0,
    dinero=50000,
    guion={
        "hp:0.85": ["SHIELD_UP", "BOSS:SPA:1"],
        "hp:0.70": ["SHIELD_DOWN"],
        "hp:0.55": ["RESET_PLAYER", "SET_SUN"],
        "hp:0.40": ["SHIELD_UP", "BOSS:SPE:1"],
        "hp:0.25": ["SHIELD_DOWN", "BOSS:SPA:1"],
        "hp:0.10": ["RESET_PLAYER", "BOSS:ATK:2"],
    },
)


# ===========================================================================
#  Jefe de pruebas
# ===========================================================================
#
# Existe solo para comprobar la cadena completa sin tener que ganar una pelea
# de verdad: victoria -> sube el contador del cristal -> el motor se entera ->
# rotulo y frase de Oak.
#
# Nivel 5 y media vida: se cae de un golpe. NO USAR EN EL EVENTO.
jefe(
    "grum_prueba",
    especie="poochyena",
    nivel=5,
    habilidad="runaway",
    movimientos=["tackle", "howl", "sandattack", "bite"],
    tipo="DARK",
    tier="TIER_FIVE",
    barra="PRUEBA - no usar en el evento",
    escala=1.0,
    vida=0.5,
    vida_por_jugador=1.0,
    dinero=0,
)


def main() -> int:
    meta = {"pack": {"pack_format": PACK_FORMAT,
                     "description": "PokeReport - El Rastro de Luna: incursiones del Eclipse"}}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, indent=2, ensure_ascii=False))
        for ruta, datos in ficheros.items():
            # Validar aqui evita descubrir una coma de mas con doce personas
            # esperando delante del cristal.
            texto = json.dumps(datos, indent=2, ensure_ascii=False)
            json.loads(texto)
            z.writestr(ruta, texto)

    print(f"  {SALIDA}")
    for ruta, d in ficheros.items():
        ident = ruta.split("/")[-1][:-5]
        p = d["pokemon"]
        extra = f"  [{d['raid_feature']}]" if "raid_feature" in d else ""
        print(f"    {ident:<20} {p['species']} niv.{p['level']}  {d['raid_tier']}"
              f"  aforo {d['max_players']}  vida x{d['health_multi']}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
