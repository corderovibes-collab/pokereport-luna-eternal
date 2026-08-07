#!/usr/bin/env python3
"""Anade a Luna las orejas caidas de cocker y las pinta en la textura.

Se aprovechan los huesos que ya trae el rig heredado de Eevee (`ear_left` ->
`ear2_left` y sus simetricos) en vez de crear huesos nuevos: asi las animaciones que
ya existen las siguen moviendo, y al ser dos tramos la oreja se dobla por la mitad
como una oreja de verdad en vez de ser una tabla rigida.

Medidas: la cabeza es un cubo de 7x7x7 entre y=9,5 y y=16,5. La oreja arranca arriba,
pegada al lateral, y baja 10 unidades hasta y=6, o sea 3,5 por debajo de la mandibula,
igual que en la referencia. El tramo de abajo es mas ancho para que se abra al caer.

Las UV se colocan en zona libre del atlas (comprobado que no pisan nada) y se pintan
con el mismo pelo rizado negro de la referencia.

Uso:  python addon-luna/tools/orejas.py
"""
import json
import os
import random
import shutil

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(RAIZ, "blockbench", "luna.geo.json")
TEXTURA = os.path.join(RAIZ, "blockbench", "luna.png")

NEGRO = (38, 38, 42, 255)
RIZO_OSC = (20, 20, 24, 255)
RIZO_CLARO = (84, 84, 94, 255)

# hueso -> (origen, tamano, uv, pivote nuevo)
OREJAS = {
    "ear_left":   ([3.5, 11.0, -5.0], [2, 5, 5], [40, 14], [3.5, 16.0, -2.5]),
    "ear2_left":  ([3.5, 6.0, -5.5],  [3, 5, 6], [56, 14], [3.5, 11.0, -2.5]),
    "ear_right":  ([-5.5, 11.0, -5.0], [2, 5, 5], [76, 14], [-3.5, 16.0, -2.5]),
    "ear2_right": ([-6.5, 6.0, -5.5],  [3, 5, 6], [92, 14], [-3.5, 11.0, -2.5]),
}


def caras(uv, size):
    u, v = uv
    w, h, d = [int(round(s)) for s in size]
    return {
        "abajo": (u + d, v, w, d), "arriba": (u + d + w, v, w, d),
        "izquierda": (u, v + d, d, h), "frente": (u + d, v + d, w, h),
        "derecha": (u + d + w, v + d, d, h), "espalda": (u + d + w + d, v + d, w, h),
    }


def ocupacion(geo, W, H):
    """Que pixeles del atlas usa ya el modelo, para no pisarlos."""
    usado = set()
    for b in geo["minecraft:geometry"][0]["bones"]:
        for c in b.get("cubes", []):
            uv = c.get("uv")
            if not isinstance(uv, list):
                continue
            for (x, y, w, h) in caras(uv, c["size"]).values():
                for py in range(int(y), int(y + h)):
                    for px in range(int(x), int(x + w)):
                        usado.add((px, py))
    return usado


def pelo(img, rect, rng):
    x, y, w, h = rect
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=NEGRO)
    for _ in range(int(w * h * 0.30)):
        px, py = rng.randrange(x, x + w), rng.randrange(y, y + h)
        color = RIZO_OSC if rng.random() < 0.6 else RIZO_CLARO
        for i in range(rng.choice((1, 2, 2, 3))):
            qx = px + (i if rng.random() < 0.5 else 0)
            qy = py + (i if rng.random() >= 0.5 else 0)
            if x <= qx < x + w and y <= qy < y + h:
                img.putpixel((qx, qy), color)


def main():
    shutil.copy(MODELO, MODELO + ".bak")
    shutil.copy(TEXTURA, TEXTURA + ".bak")

    geo = json.load(open(MODELO, encoding="utf-8"))
    desc = geo["minecraft:geometry"][0]["description"]
    W, H = desc["texture_width"], desc["texture_height"]
    ya_usado = ocupacion(geo, W, H)

    # comprobar que las UV nuevas caben y no pisan nada
    nuevos = set()
    for nombre, (_, tam, uv, _) in OREJAS.items():
        for cara, (x, y, w, h) in caras(uv, tam).items():
            if x + w > W or y + h > H:
                raise SystemExit(f"{nombre}/{cara} se sale del atlas {W}x{H}")
            for py in range(y, y + h):
                for px in range(x, x + w):
                    if (px, py) in ya_usado:
                        raise SystemExit(f"{nombre}/{cara} pisa UV ya usada en {(px, py)}")
                    nuevos.add((px, py))

    bones = {b["name"]: b for b in geo["minecraft:geometry"][0]["bones"]}
    for nombre, (origen, tam, uv, pivote) in OREJAS.items():
        hueso = bones[nombre]
        hueso["pivot"] = pivote
        hueso["cubes"] = [{"origin": origen, "size": tam, "uv": uv}]
        print(f"   {nombre:12s} cubo {tam} en {origen}, uv {uv}")

    json.dump(geo, open(MODELO, "w", encoding="utf-8", newline="\n"), indent=2)

    img = Image.open(TEXTURA).convert("RGBA")
    rng = random.Random(20260730)
    for nombre, (_, tam, uv, _) in OREJAS.items():
        for rect in caras(uv, tam).values():
            pelo(img, rect, rng)
    img.save(TEXTURA)

    print()
    print(f"   {len(nuevos)} px nuevos pintados en el atlas, sin pisar nada")
    print(f"   copias de seguridad: luna.geo.json.bak y luna.png.bak")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
