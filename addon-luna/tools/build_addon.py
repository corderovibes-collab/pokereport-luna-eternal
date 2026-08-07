#!/usr/bin/env python3
"""Genera los datos de Luna: especie, animaciones, poser, resolver y lang.

El modelo y la textura los produce build_model.py y build_texture.py; esto es todo
lo demas. Se escribe con el esquema exacto de Cobblemon 1.7.3, y las habilidades y
movimientos estan verificados uno a uno contra el lang del propio mod (310
habilidades y 932 movimientos), asi que nada de esto puede fallar por un nombre mal
escrito.

Decisiones de diseno, por si hay que justificarlas dentro de seis meses:
  - `maleRatio: 0` porque Luna es una perrita.
  - `eggGroups: ["undiscovered"]` para que no se pueda criar: sigue siendo unica.
  - No hay fichero de spawn: no aparece en el mundo, solo se da con /pokegive.
  - `willDefendOwner` porque es exactamente lo que hace un perro.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def escribir(rel, data):
    ruta = os.path.join(RAIZ, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print("   %-72s %6d bytes" % (rel, os.path.getsize(ruta)))


def kf(pares):
    """Fotogramas clave de Bedrock: {"tiempo": valor}."""
    return {str(t): v for t, v in pares}


ESPECIE = {
    "implemented": True,
    "nationalPokedexNumber": 9001,
    "name": "Luna",
    "primaryType": "psychic",
    "secondaryType": "fairy",
    "maleRatio": 0.0,
    "height": 6,
    "weight": 145,
    "pokedex": ["cobblemon.species.luna.desc"],
    "labels": ["custom", "pokereport"],
    "aspects": [],
    "abilities": ["telepathy", "cutecharm", "h:magicguard"],
    "eggGroups": ["undiscovered"],
    "baseStats": {"hp": 88, "attack": 65, "defence": 80,
                  "special_attack": 112, "special_defence": 100, "speed": 95},
    "evYield": {"hp": 0, "attack": 0, "defence": 0,
                "special_attack": 2, "special_defence": 1, "speed": 0},
    "baseExperienceYield": 180,
    "experienceGroup": "slow",
    "catchRate": 3,
    "eggCycles": 120,
    "baseFriendship": 140,
    "baseScale": 0.9,
    "hitbox": {"width": 0.9, "height": 0.9, "fixed": False},
    "behaviour": {
        "resting": {"willSleepOnBed": True, "times": ["night"],
                    "drowsyChance": 0.004, "rouseChance": 0.003},
        "moving": {"swim": {"avoidsWater": False, "canSwimInWater": True}},
        "combat": {"willDefendSelf": True, "willDefendOwner": True, "willFlee": False},
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

ANIMACIONES = {
    "format_version": "1.8.0",
    "animations": {
        "animation.luna.ground_idle": {
            "loop": True, "animation_length": 4.0,
            "bones": {
                "cuerpo": {"position": kf([(0, [0, 0, 0]), (2, [0, 0.3, 0]), (4, [0, 0, 0])])},
                "cabeza": {"rotation": kf([(0, [0, 0, 0]), (1.5, [-3, 6, 0]),
                                           (2.5, [-2, -5, 0]), (4, [0, 0, 0])])},
                "oreja_izq": {"rotation": kf([(0, [0, 0, 4]), (2, [0, 0, -6]), (4, [0, 0, 4])])},
                "oreja_der": {"rotation": kf([(0, [0, 0, -4]), (2, [0, 0, 6]), (4, [0, 0, -4])])},
            },
        },
        "animation.luna.ground_walk": {
            "loop": True, "animation_length": 0.8,
            "bones": {
                "pata_del_izq": {"rotation": kf([(0, [32, 0, 0]), (0.4, [-32, 0, 0]), (0.8, [32, 0, 0])])},
                "pata_del_der": {"rotation": kf([(0, [-32, 0, 0]), (0.4, [32, 0, 0]), (0.8, [-32, 0, 0])])},
                "pata_tra_izq": {"rotation": kf([(0, [-30, 0, 0]), (0.4, [30, 0, 0]), (0.8, [-30, 0, 0])])},
                "pata_tra_der": {"rotation": kf([(0, [30, 0, 0]), (0.4, [-30, 0, 0]), (0.8, [30, 0, 0])])},
                "cuerpo": {"position": kf([(0, [0, 0, 0]), (0.2, [0, 0.5, 0]), (0.4, [0, 0, 0]),
                                           (0.6, [0, 0.5, 0]), (0.8, [0, 0, 0])])},
                "oreja_izq": {"rotation": kf([(0, [0, 0, 10]), (0.4, [0, 0, -10]), (0.8, [0, 0, 10])])},
                "oreja_der": {"rotation": kf([(0, [0, 0, -10]), (0.4, [0, 0, 10]), (0.8, [0, 0, -10])])},
            },
        },
        "animation.luna.sleep": {
            "loop": True, "animation_length": 5.0,
            "bones": {
                "luna": {"position": kf([(0, [0, -6, 0])]), "rotation": kf([(0, [0, 0, 90])])},
                "cuerpo": {"position": kf([(0, [0, 0, 0]), (2.5, [0, 0.2, 0]), (5, [0, 0, 0])])},
            },
        },
        "animation.luna.cry": {
            "loop": False, "animation_length": 1.0,
            "bones": {
                "cabeza": {"rotation": kf([(0, [0, 0, 0]), (0.3, [-22, 0, 0]),
                                           (0.7, [-18, 0, 0]), (1, [0, 0, 0])])},
                "hocico": {"rotation": kf([(0, [0, 0, 0]), (0.3, [-8, 0, 0]), (1, [0, 0, 0])])},
            },
        },
        "animation.luna.faint": {
            "loop": False, "animation_length": 1.2,
            "bones": {
                "luna": {
                    "rotation": kf([(0, [0, 0, 0]), (1.2, [0, 0, 88])]),
                    "position": kf([(0, [0, 0, 0]), (1.2, [0, -5, 0])]),
                },
            },
        },
    },
}

POSER = {
    "portraitScale": 1.9,
    "portraitTranslation": [-0.1, -0.9, 0],
    "profileScale": 0.85,
    "profileTranslation": [0, 0.35, 0],
    "rootBone": "luna",
    "animations": {
        "cry": "q.bedrock_stateful('luna', 'cry')",
        "faint": "q.bedrock_primary('luna', 'faint', q.curve('one'))",
    },
    "poses": {
        "standing": {
            "poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"],
            "isBattle": False,
            "animations": ["q.look('cabeza')", "q.bedrock('luna', 'ground_idle')"],
        },
        "battle-standing": {
            "poseTypes": ["STAND"],
            "isBattle": True,
            "animations": ["q.look('cabeza')", "q.bedrock('luna', 'ground_idle')"],
        },
        "walking": {
            "poseTypes": ["WALK"],
            "animations": ["q.look('cabeza')", "q.bedrock('luna', 'ground_walk')"],
        },
        "sleep": {
            "poseTypes": ["SLEEP"],
            "animations": ["q.bedrock('luna', 'sleep')"],
        },
    },
}

RESOLVER = {
    "species": "cobblemon:luna",
    "order": 0,
    "variations": [
        {
            "aspects": [],
            "poser": "cobblemon:luna",
            "model": "cobblemon:luna.geo",
            "texture": "cobblemon:textures/pokemon/9001_luna/luna.png",
            "layers": [],
        },
        {
            "aspects": ["shiny"],
            "texture": "cobblemon:textures/pokemon/9001_luna/luna_shiny.png",
        },
    ],
}

DESC = ("La compañera inseparable de AlejandroReport. Cuentan que su pelaje absorbe la luz "
        "de la luna y que percibe lo que siente su entrenador antes de que él mismo lo sepa. "
        "Solo existe una.")


def main():
    escribir("data/cobblemon/species/pokereport/luna.json", ESPECIE)
    escribir("assets/cobblemon/bedrock/pokemon/animations/9001_luna/luna.animation.json", ANIMACIONES)
    escribir("assets/cobblemon/bedrock/pokemon/posers/9001_luna/luna.json", POSER)
    escribir("assets/cobblemon/bedrock/pokemon/resolvers/9001_luna/0_luna_base.json", RESOLVER)
    for cod in ("es_es", "en_us"):
        escribir(f"assets/cobblemon/lang/{cod}.json",
                 {"cobblemon.species.luna.name": "Luna", "cobblemon.species.luna.desc": DESC})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
