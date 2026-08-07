#!/usr/bin/env python3
"""Parte del modelo de Eevee de Cobblemon y lo renombra a Luna.

Eevee es un cuadrupedo con rig completo (92 huesos: parpados, formas de boca, orejas
articuladas, patas con codo y rodilla, cola en segmentos) y con animaciones ya hechas.
Modelar encima de eso da un resultado infinitamente mejor que esculpir cubos a mano,
y ademas hereda animaciones que funcionan.

Que hace exactamente:
  - copia la geometria cambiando el identificador a geometry.luna
  - copia las animaciones renombrando animation.eevee.* a animation.luna.*
  - adapta el poser para que apunte a esas animaciones
  - deja la textura de Eevee como punto de partida para repintarla
  - copia la LICENCIA junto al modelo, que es lo que exige la CC de Cobblemon

Lo que queda para ti en Blockbench: quitar la cola (Luna no tiene), ensanchar las
orejas para que cuelguen como las de una cocker, y repintar la textura.

Uso:  python addon-luna/tools/base_eevee.py
"""
import json
import os
import re
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR = os.path.join(os.environ["APPDATA"], ".cobbleverse", "instance", "mods",
                   "Cobblemon-fabric-1.7.3+1.21.1.jar")
BASE = "assets/cobblemon/bedrock/pokemon"


def escribir(rel, contenido, binario=False):
    ruta = os.path.join(RAIZ, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    modo, kw = ("wb", {}) if binario else ("w", {"encoding": "utf-8", "newline": "\n"})
    with open(ruta, modo, **kw) as fh:
        fh.write(contenido)
    print("   %-74s %7d bytes" % (rel, os.path.getsize(ruta)))


def main():
    z = zipfile.ZipFile(JAR)

    # --- geometria -------------------------------------------------------
    geo = json.loads(z.read(f"{BASE}/models/0133_eevee/eevee_male.geo.json"))
    desc = geo["minecraft:geometry"][0]["description"]
    desc["identifier"] = "geometry.luna"
    huesos = [b["name"] for b in geo["minecraft:geometry"][0]["bones"]]
    escribir("assets/cobblemon/bedrock/pokemon/models/9001_luna/luna.geo.json",
             json.dumps(geo, indent=2))

    # --- animaciones: animation.eevee.X -> animation.luna.X ---------------
    anim = z.read(f"{BASE}/animations/0133_eevee/eevee.animation.json").decode("utf-8")
    anim = anim.replace("animation.eevee.", "animation.luna.")
    escribir("assets/cobblemon/bedrock/pokemon/animations/9001_luna/luna.animation.json", anim)
    nombres = sorted(json.loads(anim)["animations"])

    # --- poser: mismas poses, apuntando a las animaciones de Luna ---------
    poser = z.read(f"{BASE}/posers/0133_eevee/eevee.json").decode("utf-8")
    poser = re.sub(r"'eevee'", "'luna'", poser)
    p = json.loads(poser)
    if p.get("rootBone") == "eevee":
        p["rootBone"] = "eevee"          # el hueso raiz del rig sigue llamandose asi
    escribir("assets/cobblemon/bedrock/pokemon/posers/9001_luna/luna.json",
             json.dumps(p, indent=2))

    # --- resolver --------------------------------------------------------
    resolver = {
        "species": "cobblemon:luna", "order": 0,
        "variations": [
            {"aspects": [], "poser": "cobblemon:luna", "model": "cobblemon:luna.geo",
             "texture": "cobblemon:textures/pokemon/9001_luna/luna.png", "layers": []},
            {"aspects": ["shiny"],
             "texture": "cobblemon:textures/pokemon/9001_luna/luna_shiny.png"},
        ],
    }
    escribir("assets/cobblemon/bedrock/pokemon/resolvers/9001_luna/0_luna_base.json",
             json.dumps(resolver, indent=2))

    # --- texturas de partida y licencia ----------------------------------
    for origen, destino in [
        ("textures/pokemon/0133_eevee/eevee.png", "luna.png"),
        ("textures/pokemon/0133_eevee/eevee_shiny.png", "luna_shiny.png"),
    ]:
        escribir(f"assets/cobblemon/textures/pokemon/9001_luna/{destino}",
                 z.read(f"assets/cobblemon/{origen}"), binario=True)
    escribir("assets/cobblemon/bedrock/pokemon/models/9001_luna/license",
             z.read(f"{BASE}/models/0133_eevee/license").decode("utf-8", "replace"))
    escribir("CREDITOS.txt",
             "El modelo, el rig y las animaciones de Luna derivan del modelo de Eevee\n"
             "del mod Cobblemon, usado bajo su licencia Creative Commons no comercial.\n"
             "La licencia completa esta junto al modelo, en\n"
             "assets/cobblemon/bedrock/pokemon/models/9001_luna/license\n")

    print()
    print(f"   rig heredado: {len(huesos)} huesos")
    print(f"   animaciones : {', '.join(n.split('.')[-1] for n in nombres)}")
    print(f"   poses       : {', '.join(p.get('poses', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
