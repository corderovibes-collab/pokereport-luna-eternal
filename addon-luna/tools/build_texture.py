#!/usr/bin/env python3
"""Pinta la textura de Luna sobre el mapa UV que define build_model.py.

Se pinta por caras, no a ojo: `caras()` da el rectangulo exacto de cada cara de cada
cubo, asi que cada marca cae donde toca — los ojos en el frente de la cabeza, la
mancha blanca en el pecho, el hocico marron con la barbilla blanca debajo.

El pelo rizado de la referencia se imita con ruido determinista y trazos cortos:
misma semilla, misma textura, asi que regenerarla no produce diferencias entre
ejecuciones ni obliga a los jugadores a descargarla otra vez sin motivo.
"""
import os
import random
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_model import HUESOS, TEX_H, TEX_W, caras

NEGRO      = (38, 38, 42, 255)
RIZO_OSC   = (20, 20, 24, 255)
RIZO_CLARO = (84, 84, 94, 255)
BLANCO     = (236, 236, 236, 255)
MARRON     = (74, 48, 36, 255)
MARRON_CLR = (99, 66, 48, 255)
NARIZ      = (18, 18, 20, 255)
IRIS       = (86, 58, 38, 255)
COLLAR     = (150, 150, 156, 255)
COLLAR_LUZ = (210, 210, 216, 255)
HEBILLA    = (232, 232, 238, 255)


def pelo(img, rect, rng):
    """Base oscura con trazos rizados cortos, como el patron de la referencia."""
    x, y, w, h = rect
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=NEGRO)
    for _ in range(int(w * h * 0.30)):
        px, py = rng.randrange(x, x + w), rng.randrange(y, y + h)
        color = RIZO_OSC if rng.random() < 0.6 else RIZO_CLARO
        for i in range(rng.choice((1, 2, 2, 3))):     # trazo corto, no punto suelto
            qx = px + (i if rng.random() < 0.5 else 0)
            qy = py + (i if rng.random() >= 0.5 else 0)
            if x <= qx < x + w and y <= qy < y + h:
                img.putpixel((qx, qy), color)


def main():
    rng = random.Random(20260730)
    img = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = {}

    for nombre, (_, _, _, tam, uv) in HUESOS.items():
        if not uv:
            continue
        r[nombre] = caras(uv, tam)
        for cara in r[nombre].values():
            pelo(img, cara, rng)

    # --- ojos: en el tercio superior del frente de la cabeza ---------------
    x, y, w, h = r["cabeza"]["frente"]
    for dx in (1, 6):
        d.rectangle([x + dx, y + 2, x + dx + 1, y + 3], fill=BLANCO)
        img.putpixel((x + dx + (1 if dx == 1 else 0), y + 3), IRIS)
        img.putpixel((x + dx + (0 if dx == 1 else 1), y + 2), IRIS)

    # --- hocico: trufa negra arriba, marron los lados, barbilla blanca -----
    for cara in ("izquierda", "derecha", "arriba"):
        x, y, w, h = r["hocico"][cara]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=MARRON)
        for _ in range(int(w * h * 0.2)):
            img.putpixel((rng.randrange(x, x + w), rng.randrange(y, y + h)), MARRON_CLR)
    x, y, w, h = r["hocico"]["frente"]
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=MARRON)
    d.rectangle([x + 1, y, x + w - 2, y + 1], fill=NARIZ)
    d.rectangle([x, y + h - 1, x + w - 1, y + h - 1], fill=BLANCO)
    x, y, w, h = r["hocico"]["abajo"]
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=BLANCO)

    # --- pecho: la mancha blanca en zigzag --------------------------------
    x, y, w, h = r["cuerpo"]["frente"]
    centro = x + w // 2
    for i, fila in enumerate(range(y + 1, y + h)):
        ancho = 1 if i % 2 else 0
        d.rectangle([centro - ancho, fila, centro + ancho, fila], fill=BLANCO)

    # --- collar: gris con hebilla, en su propia pieza ---------------------
    for rect in r["collar"].values():
        x, y, w, h = rect
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=COLLAR)
        for px in range(x, x + w, 2):
            img.putpixel((px, y), COLLAR_LUZ)
    x, y, w, h = r["collar"]["frente"]
    d.rectangle([x + w // 2 - 1, y, x + w // 2, y + h - 1], fill=HEBILLA)

    # --- patas: almohadillas oscuras --------------------------------------
    for pata in [k for k in r if k.startswith("pata")]:
        x, y, w, h = r[pata]["abajo"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=RIZO_OSC)

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "assets", "cobblemon", "textures", "pokemon", "9001_luna")
    os.makedirs(destino, exist_ok=True)
    img.save(os.path.join(destino, "luna.png"))

    # shiny: mismo pelo tirando a azul lunar, respetando marcas y collar
    sh = img.copy()
    px = sh.load()
    for j in range(TEX_H):
        for i in range(TEX_W):
            cr, cg, cb, ca = px[i, j]
            if ca and abs(cr - cg) < 10 and abs(cg - cb) < 10 and cr < 90:
                px[i, j] = (min(255, cr + 16), min(255, cg + 24), min(255, cb + 72), ca)
    sh.save(os.path.join(destino, "luna_shiny.png"))
    print("   luna.png y luna_shiny.png regeneradas")


if __name__ == "__main__":
    main()
