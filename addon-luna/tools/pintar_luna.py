#!/usr/bin/env python3
"""Convierte la textura de Eevee en la de Luna, sin romper nada.

El enfoque importa: NO se repinta de cero. Se parte de la textura original de Eevee y
se recolorea su paleta de marrones a una escala de negros, conservando el sombreado
que hizo su artista. Asi el resultado tiene volumen de verdad en vez de manchas
planas, y sobre todo se respetan los pixeles funcionales.

Eso ultimo no es un detalle: el modelo tiene formas de boca, lengua, parpados y
brillos de ojo como cubos propios y animados. Repintar por encima los convertia en
parches sueltos — que es justo lo que se veia mal. Aqui la lengua y los ojos
conservan sus colores originales, y los parpados se oscurecen igual que el pelo para
que al parpadear no desentonen.

Encima del recoloreado se anaden las marcas de Luna: barbilla blanca, raya blanca en
el pecho y collar gris claro rodeando el cuello, cada una en la cara exacta que le
corresponde segun el .geo.json.

Uso:  python addon-luna/tools/pintar_luna.py
"""
import json
import os
import random
import shutil

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(RAIZ, "blockbench", "luna.geo.json")
TEXTURA = os.path.join(RAIZ, "blockbench", "luna.png")
EEVEE = os.path.join(RAIZ, "tools", "eevee_original.png")

# Paleta de Eevee -> paleta de Luna, ordenada de mas clara a mas oscura. Se mantiene
# la misma estructura de luces y sombras, solo cambia el tono.
MAPA = {
    (242, 215, 169): (74, 74, 82),    # brillo del pelo
    (230, 197, 148): (62, 62, 69),
    (216, 176, 130): (52, 52, 58),
    (204, 156, 112): (44, 44, 49),
    (195, 147, 87):  (38, 38, 42),    # tono medio
    (184, 129, 73):  (32, 32, 36),
    (169, 108, 58):  (27, 27, 30),
    (157, 90, 45):   (22, 22, 25),
    (144, 72, 33):   (17, 17, 20),    # sombra profunda
}
# Los ojos y la boca NO se protegen por color sino por ZONA. Protegerlos por color
# fallaba: el brillo del ojo de Eevee es #ffffff puro, el mismo blanco que aparece en
# otras partes, y el recoloreo lo convertia en gris oscuro. De ahi que los ojos
# salieran negros. Estos huesos se copian pixel a pixel del original.
INTOCABLES_HUESO = ("eyeshine", "emote", "mouth", "tongue")

BLANCO = (240, 240, 238, 255)
BLANCO_SOM = (203, 203, 201, 255)
COLLAR = (156, 156, 162, 255)
COLLAR_LUZ = (201, 201, 207, 255)
RIZO_OSC = (14, 14, 16, 255)
RIZO_CLARO = (58, 58, 65, 255)

# Piezas grandes de pelo donde se dibuja el rizo. Fuera quedan la cara y los
# cubos de expresion, para no ensuciar ojos ni boca.
RIZO_EN = {"torso", "torso2", "torso3", "neckfur", "head_angle",
           "ear_left", "ear2_left", "ear_right", "ear2_right",
           "front_leg_left", "elbow_left", "front_leg_right", "elbow_right",
           "back_leg_left", "knee_left", "ankle_left",
           "back_leg_right", "knee_right", "ankle_right"}


def rect_plano(uv, size):
    """Rectangulo UV de un cubo. Si el grosor es 0 la cruz degenera en frente+espalda,
    que es justo el caso de los ojos y las bocas: son planos pegados a la cara."""
    u, v = uv
    w, h, d = [int(round(s)) for s in size]
    return (u, v, 2 * w + 2 * d if d else 2 * w, h + d)


def caras(uv, size):
    u, v = uv
    w, h, d = [max(1, int(round(s))) for s in size]
    return {
        "abajo": (u + d, v, w, d), "arriba": (u + d + w, v, w, d),
        "izquierda": (u, v + d, d, h), "frente": (u + d, v + d, w, h),
        "derecha": (u + d + w, v + d, d, h), "espalda": (u + d + w + d, v + d, w, h),
    }


def mas_cercano(color):
    """El tono de Luna equivalente, por distancia en la paleta de Eevee."""
    return min(MAPA.items(), key=lambda kv: sum((a - b) ** 2 for a, b in zip(kv[0], color)))[1]


def rizo(img, rect, rng, densidad=0.16):
    """Trazos cortos en L sobre lo ya pintado, para el aspecto rizado."""
    x, y, w, h = rect
    for _ in range(max(1, int(w * h * densidad))):
        px, py = rng.randrange(x, x + w), rng.randrange(y, y + h)
        color = RIZO_OSC if rng.random() < 0.6 else RIZO_CLARO
        largo = rng.choice((1, 2, 2))
        horiz = rng.random() < 0.5
        for i in range(largo):
            qx, qy = (px + i, py) if horiz else (px, py + i)
            if x <= qx < x + w and y <= qy < y + h:
                img.putpixel((qx, qy), color)
        qx, qy = (px + largo - 1, py + 1) if horiz else (px + 1, py + largo - 1)
        if x <= qx < x + w and y <= qy < y + h:
            img.putpixel((qx, qy), color)


def main():
    if os.path.exists(TEXTURA):
        shutil.copy(TEXTURA, TEXTURA + ".prev")

    base = Image.open(EEVEE).convert("RGBA")
    W, H = base.size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bp, ip = base.load(), img.load()

    geo = json.load(open(MODELO, encoding="utf-8"))

    # --- 0) que pixeles son ojos o boca, para copiarlos tal cual ----------
    protegidos = set()
    for bone in geo["minecraft:geometry"][0]["bones"]:
        if not any(k in bone["name"] for k in INTOCABLES_HUESO):
            continue
        for c in bone.get("cubes", []):
            if not isinstance(c.get("uv"), list):
                continue
            x, y, w, h = rect_plano(c["uv"], c["size"])
            for py in range(y, y + h):
                for px in range(x, x + w):
                    protegidos.add((px, py))

    # --- 1) recolorear el pelo, dejando intactos ojos y boca --------------
    tocados = intactos = 0
    for y in range(H):
        for x in range(W):
            r, g, b, a = bp[x, y]
            if not a:
                continue
            if (x, y) in protegidos:
                ip[x, y] = (r, g, b, a); intactos += 1
            else:
                ip[x, y] = (*mas_cercano((r, g, b)), a); tocados += 1

    rect = {}
    for bone in geo["minecraft:geometry"][0]["bones"]:
        for c in bone.get("cubes", []):
            if isinstance(c.get("uv"), list):
                rect.setdefault(bone["name"], caras(c["uv"], c["size"]))

    d = ImageDraw.Draw(img)
    rng = random.Random(731)

    # --- 2) las orejas son cubos nuevos: no existen en la textura de Eevee -
    for oreja in ("ear_left", "ear2_left", "ear_right", "ear2_right"):
        for r in rect[oreja].values():
            d.rectangle([r[0], r[1], r[0] + r[2] - 1, r[1] + r[3] - 1], fill=(30, 30, 34, 255))
            rizo(img, r, rng, 0.34)

    # --- 3) rizo sobre las piezas grandes ---------------------------------
    for nombre in RIZO_EN:
        if nombre in rect and not nombre.startswith("ear"):
            for r in rect[nombre].values():
                rizo(img, r, rng)

    # --- 4) barbilla blanca: cara de abajo del morro ----------------------
    x, y, w, h = rect["muzzle"]["abajo"]
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=BLANCO)
    for _ in range(5):
        ip[rng.randrange(x, x + w), rng.randrange(y, y + h)] = BLANCO_SOM
    x, y, w, h = rect["muzzle"]["frente"]
    d.rectangle([x + 1, y + h - 1, x + w - 2, y + h - 1], fill=BLANCO)

    # --- 5) collar: fila de arriba del cuello, justo bajo la cabeza -------
    for cara in ("frente", "izquierda", "derecha", "espalda"):
        x, y, w, h = rect["neckfur"][cara]
        d.rectangle([x, y, x + w - 1, y], fill=COLLAR)
        for px in range(x, x + w, 3):
            ip[px, y] = COLLAR_LUZ

    # --- 6) raya del pecho: sigue bajo el collar y baja al torso ----------
    x, y, w, h = rect["neckfur"]["frente"]
    centro = x + w // 2
    for i, fila in enumerate(range(y + 1, y + h)):
        ancho = 1 if i % 2 else 0
        d.rectangle([centro - ancho, fila, centro + ancho, fila], fill=BLANCO)
    x, y, w, h = rect["torso3"]["frente"]
    centro = x + w // 2
    for i, fila in enumerate(range(y, y + h - 1)):
        ancho = 1 if i % 2 else 0
        d.rectangle([centro - ancho, fila, centro + ancho, fila], fill=BLANCO)
        if i % 2:
            ip[centro - 1, fila] = BLANCO_SOM

    img.save(TEXTURA)
    img.save(os.path.join(RAIZ, "assets", "cobblemon", "textures", "pokemon", "9001_luna", "luna.png"))

    sh = img.copy()
    sp = sh.load()
    for y in range(H):
        for x in range(W):
            cr, cg, cb, ca = sp[x, y]
            if ca and abs(cr - cg) < 8 and abs(cg - cb) < 8 and cr < 80:
                sp[x, y] = (min(255, cr + 14), min(255, cg + 22), min(255, cb + 78), ca)
    for destino in (os.path.join(RAIZ, "blockbench", "luna_shiny.png"),
                    os.path.join(RAIZ, "assets", "cobblemon", "textures", "pokemon",
                                 "9001_luna", "luna_shiny.png")):
        sh.save(destino)

    print(f"   {tocados} px recoloreados, {intactos} px intactos (ojos, trufa y lengua)")
    print(f"   rizo en {len(RIZO_EN)} piezas, orejas pintadas de cero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
