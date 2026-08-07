#!/usr/bin/env python3
"""Monta una tarjeta de presentacion de Luna a partir de la captura de Blockbench.

La captura de Blockbench sale recortada y con fondo transparente, que esta muy bien
para trabajar pero se ve pobre al enviarla por Discord. Esto la coloca sobre un fondo
nocturno con luna, le pone el nombre, los tipos y las estadisticas leidas del propio
fichero de especie — nada escrito a mano que pueda quedar desincronizado.

Uso:  python addon-luna/tools/tarjeta.py captura.png [salida.png]
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESPECIE = os.path.join(RAIZ, "data", "cobblemon", "species", "pokereport", "luna.json")

W, H = 1200, 675                      # 16:9, va bien en Discord y en pantalla
CIELO_ALTO = (18, 16, 38)
CIELO_BAJO = (52, 30, 62)
LILA = (198, 170, 255)
ORO = (255, 226, 168)
TIPOS = {"psychic": ((246, 92, 138), "PSÍQUICO"), "fairy": ((239, 154, 216), "HADA")}


def fuente(tam, negrita=False):
    for nombre in (("seguibl.ttf", "segoeuib.ttf") if negrita else ("segoeui.ttf",)):
        ruta = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", nombre)
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default(tam)


def fondo():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):                       # degradado vertical
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(
            int(a + (b - a) * t) for a, b in zip(CIELO_ALTO, CIELO_BAJO)))
    rng = random.Random(9001)
    for _ in range(220):                     # estrellas
        x, y = rng.randrange(W), rng.randrange(int(H * 0.75))
        brillo = rng.randint(90, 255)
        r = 1 if rng.random() < 0.85 else 2
        d.ellipse([x, y, x + r, y + r], fill=(brillo, brillo, min(255, brillo + 20)))

    luna = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(luna)
    cx, cy, r = W - 210, 150, 95
    dl.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 248, 226, 255))
    luna = luna.filter(ImageFilter.GaussianBlur(2))
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2],
                                 fill=(180, 170, 255, 60))
    img.paste(Image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(40)), luna),
              (0, 0), Image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(40)), luna))
    return img.convert("RGBA")


def main(captura, salida=None):
    esp = json.load(open(ESPECIE, encoding="utf-8"))
    img = fondo()
    d = ImageDraw.Draw(img)

    # --- el modelo, escalado para que ocupe el alto util ------------------
    luna = Image.open(captura).convert("RGBA")
    caja = luna.getbbox() or (0, 0, *luna.size)
    luna = luna.crop(caja)
    escala = min(430 / luna.height, 620 / luna.width)
    luna = luna.resize((int(luna.width * escala), int(luna.height * escala)), Image.LANCZOS)
    px, py = 90, H - luna.height - 120

    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse(
        [px + luna.width * 0.1, py + luna.height - 26,
         px + luna.width * 0.9, py + luna.height + 24], fill=(0, 0, 0, 120))
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(luna, (px, py))

    # --- textos ------------------------------------------------------------
    d.text((px + luna.width + 60, 150), esp["name"].upper(), font=fuente(96, True), fill=(255, 255, 255))
    d.text((px + luna.width + 64, 258), "la perrita de AlejandroReport",
           font=fuente(28), fill=LILA)

    x = px + luna.width + 64
    for tipo in (esp["primaryType"], esp.get("secondaryType")):
        if not tipo:
            continue
        color, etiqueta = TIPOS.get(tipo, ((150, 150, 150), tipo.upper()))
        f = fuente(24, True)
        ancho = int(d.textlength(etiqueta, font=f)) + 44
        d.rounded_rectangle([x, 310, x + ancho, 356], 23, fill=color)
        d.text((x + 22, 320), etiqueta, font=f, fill=(30, 20, 40))
        x += ancho + 14

    f, fb = fuente(22), fuente(22, True)
    filas = [("PS", "hp"), ("Ataque", "attack"), ("Defensa", "defence"),
             ("At. Esp.", "special_attack"), ("Def. Esp.", "special_defence"), ("Velocidad", "speed")]
    y = 400
    for etiqueta, clave in filas:
        v = esp["baseStats"][clave]
        d.text((px + luna.width + 64, y), etiqueta, font=f, fill=(214, 206, 236))
        barra = int(200 * min(v, 150) / 150)
        d.rounded_rectangle([px + luna.width + 190, y + 4, px + luna.width + 390, y + 20], 8,
                            fill=(255, 255, 255, 28))
        d.rounded_rectangle([px + luna.width + 190, y + 4, px + luna.width + 190 + barra, y + 20], 8,
                            fill=LILA)
        d.text((px + luna.width + 402, y), str(v), font=fb, fill=ORO)
        y += 34

    d.text((60, H - 58), f"Psíquico · Hada    {esp['height']/10} m    {esp['weight']/10} kg"
                         f"    Ejemplar único", font=fuente(22), fill=(176, 168, 200))

    salida = salida or os.path.join(os.path.dirname(captura), "luna_tarjeta.png")
    img.convert("RGB").save(salida, quality=95)
    print(f"   tarjeta guardada en {salida}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raise SystemExit(main(*sys.argv[1:3]))
