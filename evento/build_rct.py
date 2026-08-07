# -*- coding: utf-8 -*-
"""Genera los guardianes del Eclipse como entrenadores de RCT.

Por que RCT y no los NPCs de Cobblemon ni Easy NPC:

  - Cobblemon define equipos con especie y nivel, nada mas, y su NPC no sabe
    cuando ha perdido.
  - Easy NPC tiene skin propia pero no pelea.
  - RCT hace las dos cosas: equipo completo (naturaleza, habilidad, movimientos,
    IVs, EVs, objetos de combate) **y** textura propia por entrenador, en
    `assets/rctmod/textures/trainers/single/<id>.png`.

Ademas `forceBattleOnSight` esta activo en la config del servidor, asi que retan
al acercarse — que es exactamente lo que queremos de un guardian bloqueando el
camino.

Se colocan en el juego con:
    /rctmod trainer summon_persistent <id>

Uso:  python evento/build_rct.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-RCT-DP.zip")
PACK_FORMAT = 48

ficheros: dict[str, dict] = {}


def entrenador(ident, nombre, equipo, pociones=2):
    ficheros[f"data/rctmod/trainers/{ident}.json"] = {
        "name": nombre,
        # El AI de RCT juega bastante bien; el margen bajo lo hace mas certero
        # al elegir movimiento. 0.15 es lo que usan sus entrenadores de elite.
        "ai": {"type": "rct", "data": {"maxSelectMargin": 0.15}},
        "battleRules": {"maxItemUses": pociones},
        "bag": [{"item": "cobblemon:superb_remedy", "quantity": pociones}],
        "team": equipo,
    }


def poke(especie, nivel, naturaleza, habilidad, movimientos, genero="MALE"):
    return {
        "species": especie,
        "gender": genero,
        "level": nivel,
        "nature": naturaleza,
        "ability": habilidad,
        "moveset": movimientos,
        "ivs": {},
        "evs": {},
    }


# ===========================================================================
#  Señal 1 — el bosque
# ===========================================================================
#
# Primer combate del evento: tiene que enseñar como se pelea sin castigar.
# Dos siniestros de nivel 27-30 contra un grupo que llega con equipo de 30-40.
# Intimidacion baja el ataque nada mas salir, asi que se nota que es un rival
# preparado, pero sin movimientos que puedan barrer a nadie de un golpe.
entrenador("grum_eclipse", "Grum del Eclipse", [
    poke("poochyena", 27, "adamant", "runaway",
         ["bite", "howl", "suckerpunch", "swagger"]),
    poke("mightyena", 30, "adamant", "intimidate",
         ["crunch", "suckerpunch", "firefang", "playrough"]),
])


# ===========================================================================
#  Señal 2 — la montaña
# ===========================================================================
entrenador("sable_eclipse", "Sable del Eclipse", [
    # Ojo con los nombres: Cobblemon usa los identificadores de Showdown, asi
    # que es "iceshard" (no "icyshard") y "feintattack" (Faint Attack se
    # renombro a Feint Attack). Con el nombre mal, el equipo se carga a medias.
    poke("sneasel", 32, "jolly", "innerfocus",
         ["iceshard", "feintattack", "screech", "quickattack"]),
    poke("weavile", 35, "jolly", "pressure",
         ["iceshard", "nightslash", "swordsdance", "iciclecrash"]),
], pociones=3)


# ===========================================================================
#  Señal 3 — la costa
# ===========================================================================
entrenador("nix_eclipse", "Nix del Eclipse", [
    poke("carvanha", 37, "adamant", "roughskin",
         ["bite", "aquajet", "screech", "swagger"]),
    poke("sharpedo", 40, "adamant", "roughskin",
         ["crunch", "aquajet", "icefang", "screech"]),
], pociones=3)


# ===========================================================================
#  Laboratorio
# ===========================================================================
entrenador("guardia_eclipse", "Guardia del Eclipse", [
    poke("golbat", 40, "jolly", "innerfocus",
         ["airslash", "bite", "confuseray", "quickattack"]),
    poke("muk", 41, "adamant", "stench",
         ["gunkshot", "poisonjab", "minimize", "screech"]),
    poke("houndoom", 43, "modest", "flashfire",
         ["flamethrower", "darkpulse", "nastyplot", "willowisp"]),
], pociones=4)


entrenador("vex_eclipse", "Doctora Vex", [
    poke("crobat", 47, "jolly", "innerfocus",
         ["crosspoison", "airslash", "confuseray", "leechlife"], "FEMALE"),
    poke("magnezone", 48, "modest", "sturdy",
         ["thunderbolt", "flashcannon", "thunderwave", "lightscreen"]),
    poke("drapion", 50, "adamant", "sniper",
         ["crosspoison", "nightslash", "swordsdance", "aquatail"]),
    poke("weavile", 51, "jolly", "pressure",
         ["iciclecrash", "nightslash", "swordsdance", "iceshard"], "FEMALE"),
    poke("gengar", 53, "timid", "cursedbody",
         ["shadowball", "sludgebomb", "nastyplot", "hex"]),
    poke("hydreigon", 55, "modest", "levitate",
         ["darkpulse", "dragonpulse", "flamethrower", "nastyplot"]),
], pociones=4)


def main() -> int:
    meta = {"pack": {"pack_format": PACK_FORMAT,
                     "description": "PokeReport · El Rastro de Luna — entrenadores del Eclipse"}}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, indent=2, ensure_ascii=False))
        for ruta, datos in ficheros.items():
            z.writestr(ruta, json.dumps(datos, indent=2, ensure_ascii=False))

    print(f"   {SALIDA}")
    for ruta, d in ficheros.items():
        ident = ruta.split("/")[-1][:-5]
        niveles = "-".join(str(p["level"]) for p in d["team"])
        print(f"     {ident:<18} {d['name']:<22} {len(d['team'])} Pokemon (niv. {niveles})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
