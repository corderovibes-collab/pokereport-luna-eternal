#!/usr/bin/env python3
"""Deja el addon de Luna listo para desplegar: escala, datos, dex y empaquetado.

La escala se calibra contra Pokemon reales del juego, no a ojo. El modelo viene de
Eevee, que usa baseScale 0.5 para 0,3 m. Growlithe, que es "perro normal", usa 0.75
para 0,7 m. Luna se queda en 0.8: un cocker adulto, claramente mas grande que Eevee
y en la misma liga que un Growlithe.

Ademas copia el modelo y las texturas desde la carpeta de trabajo de Blockbench a la
del addon, escribe la entrada de Pokedex y regenera los dos zips.

Uso:  python addon-luna/tools/finalizar.py
"""
import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRABAJO = os.path.join(RAIZ, "blockbench")
ASSETS = os.path.join(RAIZ, "assets", "cobblemon")

ESPECIE = {
    "implemented": True,
    "nationalPokedexNumber": 9001,
    "name": "Luna",
    "primaryType": "psychic",
    "secondaryType": "fairy",
    "maleRatio": 0.0,                 # siempre hembra
    "height": 6,                      # 0,6 m: un cocker adulto
    "weight": 130,                    # 13 kg, el peso real de la raza
    "pokedex": ["cobblemon.species.luna.desc"],
    "labels": ["custom", "pokereport"],
    "aspects": [],
    "abilities": ["telepathy", "cutecharm", "h:magicguard"],
    "eggGroups": ["undiscovered"],    # no se puede criar: sigue siendo unica
    "baseStats": {"hp": 88, "attack": 65, "defence": 80,
                  "special_attack": 112, "special_defence": 100, "speed": 95},
    "evYield": {"hp": 0, "attack": 0, "defence": 0,
                "special_attack": 2, "special_defence": 1, "speed": 0},
    "baseExperienceYield": 180,
    "experienceGroup": "slow",
    "catchRate": 3,
    "eggCycles": 120,
    "baseFriendship": 140,
    "baseScale": 0.8,
    "hitbox": {"width": 1.0, "height": 1.15, "fixed": False},
    "behaviour": {
        "resting": {"willSleepOnBed": True, "times": ["night"],
                    "drowsyChance": 0.004, "rouseChance": 0.003},
        "moving": {"swim": {"avoidsWater": False, "canSwimInWater": True},
                   "walk": {"canWalk": True, "avoidsLand": False}},
        "combat": {"willDefendSelf": True, "willDefendOwner": True, "willFlee": False},
        "herd": {"maxSize": "1"},     # unica: nunca en grupo
    },
    "drops": {"amount": 0, "entries": []},
    "moves": [
        "1:tackle", "1:babydolleyes", "5:confusion", "9:charm", "13:disarmingvoice",
        "17:psybeam", "21:howl", "25:drainingkiss", "29:extrasensory", "33:lightscreen",
        "37:reflect", "41:playrough", "45:calmmind", "49:moonlight", "53:psyshock",
        "57:dazzlinggleam", "61:mistyterrain", "65:futuresight", "70:psychic", "75:moonblast",
        "tm:protect", "tm:helpinghand", "tm:wish", "tm:yawn", "tm:bite", "tm:crunch",
    ],
    "evolutions": [],
}

DEX = {
    "identifier": "cobblemon:luna",
    "displayName": "cobblemon.species.luna.name",
    "description": "cobblemon.species.luna.desc",
    "species": "cobblemon:luna",
    "forms": [],
}


def escribir(rel, data):
    ruta = os.path.join(RAIZ, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print("   %-70s %6d bytes" % (rel, os.path.getsize(ruta)))


def main():
    # 1) el modelo y las texturas definitivos, desde la carpeta de Blockbench
    copias = [
        ("luna.geo.json", os.path.join(ASSETS, "bedrock", "pokemon", "models", "9001_luna")),
        ("luna.animation.json", os.path.join(ASSETS, "bedrock", "pokemon", "animations", "9001_luna")),
        ("luna.png", os.path.join(ASSETS, "textures", "pokemon", "9001_luna")),
        ("luna_shiny.png", os.path.join(ASSETS, "textures", "pokemon", "9001_luna")),
    ]
    for nombre, destino in copias:
        origen = os.path.join(TRABAJO, nombre)
        if os.path.exists(origen):
            os.makedirs(destino, exist_ok=True)
            shutil.copy(origen, os.path.join(destino, nombre))
            print("   %-70s %6d bytes" % (nombre + " -> assets", os.path.getsize(origen)))

    # 2) datos
    escribir("data/cobblemon/species/pokereport/luna.json", ESPECIE)
    escribir("data/cobblemon/dex_entries/pokemon/pokereport/luna.json", DEX)

    # 3) empaquetar
    print()
    subprocess.run([sys.executable, os.path.join(RAIZ, "tools", "package.py")], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
