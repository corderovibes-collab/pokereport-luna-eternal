#!/usr/bin/env python3
"""Render isometrico del modelo, para poder juzgarlo sin abrir Blockbench.

Existe por una razon concreta: modelar a ciegas no funciona. Con esto se compara
el resultado contra la referencia en el mismo angulo y se itera sobre lo que se ve,
no sobre lo que uno cree que ha hecho.

Proyeccion isometrica clasica de Minecraft: giro de 45 grados en Y y ~30 en X. Cada
cara es un paralelogramo, asi que el mapeo desde la textura es afin y se puede
resolver exacto (nada de interpolar a ojo): se invierte la base del paralelogramo y
se muestrea la textura pixel a pixel. Las caras se pintan de atras hacia delante.

Uso:  python addon-luna/tools/render.py [salida.png] [escala]
"""
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_model import HUESOS, caras

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTURA = os.path.join(RAIZ, "assets", "cobblemon", "textures", "pokemon", "9001_luna", "luna.png")

# Sombreado por orientacion, como hace el juego: arriba a plena luz, un costado
# mas apagado que el otro para que se lea el volumen.
LUZ = {"arriba": 1.0, "frente": 0.78, "derecha": 0.62, "izquierda": 0.62,
       "espalda": 0.78, "abajo": 0.45}

# Esquinas de cada cara en coordenadas locales del cubo (origen, u, v) donde u y v
# recorren la cara. El orden importa: (esquina, vector_u, vector_v).
CARAS_3D = {
    "arriba":    ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
    "abajo":     ((0, 0, 1), (1, 0, 0), (0, 0, -1)),
    "frente":    ((0, 1, 0), (1, 0, 0), (0, -1, 0)),   # -Z, mira al frente
    "espalda":   ((1, 1, 1), (-1, 0, 0), (0, -1, 0)),
    "izquierda": ((1, 1, 0), (0, 0, 1), (0, -1, 0)),   # +X
    "derecha":   ((0, 1, 1), (0, 0, -1), (0, -1, 0)),  # -X
}


def proyectar(p, ang_y=math.radians(145), ang_x=math.radians(30)):
    """Modelo 3D -> pantalla 2D, con profundidad para ordenar las caras."""
    x, y, z = p
    xr = x * math.cos(ang_y) - z * math.sin(ang_y)
    zr = x * math.sin(ang_y) + z * math.cos(ang_y)
    yr = y * math.cos(ang_x) - zr * math.sin(ang_x)
    prof = y * math.sin(ang_x) + zr * math.cos(ang_x)
    return xr, -yr, prof


# Normal de cada cara en coordenadas del modelo.
NORMALES = {
    "arriba": (0, 1, 0), "abajo": (0, -1, 0),
    "frente": (0, 0, -1), "espalda": (0, 0, 1),
    "izquierda": (1, 0, 0), "derecha": (-1, 0, 0),
}


def cara_visible(nombre, ang_y=math.radians(145), ang_x=math.radians(30)):
    """Visible si su normal apunta hacia la camara.

    Se calcula, no se decide a mano: elegir las caras "a ojo" segun el angulo es
    justo lo que hacia que el render mintiera y el modelo pareciera plano.
    """
    nx, ny, nz = NORMALES[nombre]
    zr = nx * math.sin(ang_y) + nz * math.cos(ang_y)
    return ny * math.sin(ang_x) + zr * math.cos(ang_x) > 0


def main(salida="render_luna.png", escala=14, grados=145):
    """`grados` gira la camara: a 145 la profundidad y la anchura se proyectan casi
    igual y el bicho se ve como un bloque; hacia 120 el cuerpo se lee largo."""
    ang_y = math.radians(grados)
    tex = Image.open(TEXTURA).convert("RGBA")
    quads = []

    for nombre, (_, _, origen, tam, uv) in HUESOS.items():
        if not origen:
            continue
        ox, oy, oz = origen
        sx, sy, sz = tam
        rects = caras(uv, tam)
        for cara, (esq, vu, vv) in CARAS_3D.items():
            if not cara_visible(cara, ang_y):
                continue
            # esquina y vectores en unidades de modelo
            p0 = (ox + esq[0] * sx, oy + esq[1] * sy, oz + esq[2] * sz)
            du = (vu[0] * sx, vu[1] * sy, vu[2] * sz)
            dv = (vv[0] * sx, vv[1] * sy, vv[2] * sz)
            a = proyectar(p0, ang_y)
            b = proyectar((p0[0] + du[0], p0[1] + du[1], p0[2] + du[2]), ang_y)
            c = proyectar((p0[0] + dv[0], p0[1] + dv[1], p0[2] + dv[2]), ang_y)
            quads.append((min(a[2], b[2], c[2]), cara, rects[cara], a, b, c))

    quads.sort(key=lambda q: q[0])  # de atras hacia delante

    xs = [p[0] for q in quads for p in q[3:6]]
    ys = [p[1] for q in quads for p in q[3:6]]
    ancho = int((max(xs) - min(xs) + 2) * escala)
    alto = int((max(ys) - min(ys) + 2) * escala)
    img = Image.new("RGBA", (ancho, alto), (122, 158, 96, 255))
    px = img.load()
    tpx = tex.load()

    for _, cara, rect, a, b, c in quads:
        # base del paralelogramo en pantalla
        ax = (a[0] - min(xs) + 1) * escala
        ay = (a[1] - min(ys) + 1) * escala
        ux = (b[0] - a[0]) * escala
        uy = (b[1] - a[1]) * escala
        vx = (c[0] - a[0]) * escala
        vy = (c[1] - a[1]) * escala
        det = ux * vy - uy * vx
        if abs(det) < 1e-9:
            continue
        rx, ry, rw, rh = rect
        luz = LUZ[cara]

        x0 = int(min(ax, ax + ux, ax + vx, ax + ux + vx))
        x1 = int(max(ax, ax + ux, ax + vx, ax + ux + vx)) + 1
        y0 = int(min(ay, ay + uy, ay + vy, ay + uy + vy))
        y1 = int(max(ay, ay + uy, ay + vy, ay + uy + vy)) + 1
        for sy_ in range(max(0, y0), min(alto, y1)):
            for sx_ in range(max(0, x0), min(ancho, x1)):
                dx, dy = sx_ + 0.5 - ax, sy_ + 0.5 - ay
                s = (dx * vy - dy * vx) / det
                t = (ux * dy - uy * dx) / det
                if not (0 <= s < 1 and 0 <= t < 1):
                    continue
                tx = rx + min(rw - 1, int(s * rw))
                ty = ry + min(rh - 1, int(t * rh))
                r, g, b_, al = tpx[tx, ty]
                if al == 0:
                    continue
                px[sx_, sy_] = (int(r * luz), int(g * luz), int(b_ * luz), 255)

    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), salida)
    img.save(ruta)
    print(f"   {salida}: {ancho}x{alto} px, {len(quads)} caras")
    return ruta


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "render_luna.png",
         int(sys.argv[2]) if len(sys.argv) > 2 else 14,
         int(sys.argv[3]) if len(sys.argv) > 3 else 145)
