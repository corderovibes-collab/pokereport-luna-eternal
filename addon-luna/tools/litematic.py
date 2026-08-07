#!/usr/bin/env python3
"""Convierte el modelo de Luna en una estatua .litematic para construir en el juego.

Como funciona, de fuera hacia dentro:

  1. Se recorre la jerarquia de huesos del .geo.json acumulando transformaciones.
     Importa hacerlo bien: las orejas llevan rotacion propia, y si se ignora salen
     rectas en vez de caidas.
  2. Para cada voxel del volumen se transforma su centro al espacio local de cada
     cubo y se comprueba si cae dentro. Es al reves de lo intuitivo (voxel -> cubo,
     no cubo -> voxels) pero es lo unico que respeta rotaciones sin deformar.
  3. Del voxel se mira a que cara del cubo esta mas pegado, se calcula su UV en esa
     cara y se lee el color real de la textura.
  4. Ese color se traduce al bloque de Minecraft mas parecido, por distancia RGB.
  5. Se escribe el NBT con el empaquetado de bits de Litematica y se comprime.

El formato lo verifique en el jar de Litematica instalado: version 7, subversion 1.

Uso:  python addon-luna/tools/litematic.py [escala] [salida.litematic]
      escala 1 = 22 bloques de alto, 2 = 44, 3 = 66
"""
import gzip
import json
import math
import os
import struct
import sys
import time

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(RAIZ, "blockbench", "luna.geo.json")
TEXTURA = os.path.join(RAIZ, "blockbench", "luna.png")
DATA_VERSION = 3955          # Minecraft 1.21.1

# Rampa de grises para el pelo, de mas oscuro a mas claro. El pelo de Luna ocupa un
# rango de luminancia estrechisimo (15 a 84 sobre 255), asi que mapear "al bloque mas
# parecido" mete todo en dos negros identicos y la estatua queda como un bulto sin
# forma. Se estira ese rango sobre toda la rampa: asi el sombreado que pinto el
# artista de Eevee se convierte en relieve visible a escala de bloques.
RAMPA = [
    "minecraft:black_concrete",
    "minecraft:blackstone",
    "minecraft:polished_blackstone",
    "minecraft:deepslate",
    "minecraft:gray_concrete",
    "minecraft:cobbled_deepslate",
    "minecraft:light_gray_concrete",
]

# Paleta: bloques solidos de color plano, con su RGB medio real.
BLOQUES = [
    ("minecraft:black_concrete",        (8, 10, 15)),
    ("minecraft:black_wool",            (20, 21, 25)),
    ("minecraft:gray_concrete",         (54, 57, 61)),
    ("minecraft:gray_wool",             (62, 68, 71)),
    ("minecraft:light_gray_concrete",   (125, 125, 115)),
    ("minecraft:light_gray_wool",       (142, 142, 134)),
    ("minecraft:white_concrete",        (207, 213, 214)),
    ("minecraft:white_wool",            (233, 236, 236)),
    ("minecraft:brown_concrete",        (96, 60, 32)),
    ("minecraft:brown_terracotta",      (77, 51, 36)),
    ("minecraft:red_terracotta",        (143, 61, 47)),
    ("minecraft:pink_wool",             (237, 141, 172)),
]


# ---------------------------------------------------------------- NBT
def _b(v): return struct.pack(">b", v)
def _s(v): return struct.pack(">h", v)
def _i(v): return struct.pack(">i", v)
def _l(v): return struct.pack(">q", v)
def _str(t):
    d = t.encode("utf-8"); return struct.pack(">H", len(d)) + d


def nbt(tag):
    """Serializa un valor python al cuerpo de su etiqueta NBT."""
    tipo, valor = tag
    if tipo == "int": return _i(valor)
    if tipo == "long": return _l(valor)
    if tipo == "str": return _str(valor)
    if tipo == "longarray":
        return _i(len(valor)) + b"".join(_l(v) for v in valor)
    if tipo == "compound":
        out = b""
        for k, v in valor.items():
            out += _b(TIPOS[v[0]]) + _str(k) + nbt(v)
        return out + _b(0)
    if tipo == "list":
        sub, items = valor
        out = _b(TIPOS[sub]) + _i(len(items))
        return out + b"".join(nbt((sub, x)) for x in items)
    raise ValueError(tipo)


TIPOS = {"int": 3, "long": 4, "str": 8, "list": 9, "compound": 10, "longarray": 12}


# ------------------------------------------------------- transformaciones
def matriz_hueso(bones, nombre, cache):
    """Transformacion acumulada del hueso: (rotacion 3x3, traslacion)."""
    if nombre in cache:
        return cache[nombre]
    b = bones[nombre]
    rot = b.get("rotation", [0, 0, 0])
    piv = b.get("pivot", [0, 0, 0])
    m = rot_xyz([math.radians(r) for r in rot])
    # rotar alrededor del pivote: T(piv) . R . T(-piv)
    t = [piv[i] - sum(m[i][j] * piv[j] for j in range(3)) for i in range(3)]
    padre = b.get("parent")
    if padre and padre in bones:
        pm, pt = matriz_hueso(bones, padre, cache)
        m2 = [[sum(pm[i][k] * m[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
        t2 = [sum(pm[i][k] * t[k] for k in range(3)) + pt[i] for i in range(3)]
        m, t = m2, t2
    cache[nombre] = (m, t)
    return m, t


def rot_xyz(r):
    cx, sx = math.cos(r[0]), math.sin(r[0])
    cy, sy = math.cos(r[1]), math.sin(r[1])
    cz, sz = math.cos(r[2]), math.sin(r[2])
    return [
        [cy * cz, -cy * sz, sy],
        [cx * sz + sx * sy * cz, cx * cz - sx * sy * sz, -sx * cy],
        [sx * sz - cx * sy * cz, sx * cz + cx * sy * sz, cx * cy],
    ]


def caras(uv, size):
    u, v = uv
    w, h, d = [max(1, int(round(s))) for s in size]
    return {
        "abajo": (u + d, v, w, d), "arriba": (u + d + w, v, w, d),
        "izquierda": (u, v + d, d, h), "frente": (u + d, v + d, w, h),
        "derecha": (u + d + w, v + d, d, h), "espalda": (u + d + w + d, v + d, w, h),
    }


# Bloques por orientacion de la superficie. Una estatua se lee por su volumen, no
# por el ruido de la textura: las caras que miran arriba reciben luz, los costados
# quedan a medias y lo de abajo en sombra. Ese degradado es lo que da forma.
SUPERFICIE = {
    "arriba":    "minecraft:polished_blackstone",   # recibe luz: el tono mas claro
    "izquierda": "minecraft:blackstone",
    "derecha":   "minecraft:blackstone",
    "frente":    "minecraft:black_concrete",
    "espalda":   "minecraft:black_concrete",
    "abajo":     "minecraft:black_concrete",         # en sombra
}
INTERIOR = "minecraft:black_concrete"

# Material por pieza del cuerpo. Es la decision clave de toda la estatua: usar el
# color "real" de Luna significa negro en todo, y en Minecraft eso no tiene silueta
# — se ve un bulto. Los que construyen estatuas dan a cada parte un material
# distinto dentro de la misma gama, y asi la forma se lee de lejos. Sigue siendo
# negra, pero con cabeza, orejas, patas y cuerpo distinguibles.
MATERIAL = {
    "head_angle": "minecraft:blackstone",
    "muzzle":     "minecraft:polished_blackstone",
    "ear":        "minecraft:deepslate",
    "torso":      "minecraft:black_concrete",
    "neck":       "minecraft:polished_blackstone",
    "leg":        "minecraft:polished_deepslate",
    "elbow":      "minecraft:polished_deepslate",
    "knee":       "minecraft:polished_deepslate",
    "ankle":      "minecraft:polished_deepslate",
    "paw":        "minecraft:black_concrete",
}


def material_de(hueso):
    for clave, bloque in MATERIAL.items():
        if clave in hueso:
            return bloque
    return INTERIOR

# Marcas deliberadas: se detectan por color y se ponen en su bloque puro, sin
# escalones intermedios. Son lo que hace reconocible a Luna de lejos.
MARCAS = [
    ((236, 236, 236), "minecraft:white_concrete"),   # pecho y barbilla
    ((156, 156, 162), "minecraft:light_gray_concrete"),  # collar
    ((74, 48, 36),    "minecraft:brown_concrete"),   # hocico
    ((100, 38, 47),   "minecraft:red_terracotta"),   # boca
    ((202, 122, 122), "minecraft:pink_wool"),        # lengua
    ((255, 255, 255), "minecraft:white_concrete"),   # brillo del ojo
    ((17, 10, 10),    "minecraft:black_concrete"),   # iris
]


def marca(rgb):
    """Devuelve el bloque si el color es una marca clara, o None si es pelo."""
    # Umbral estrecho a proposito. Con uno ancho, el gris oscuro del pelo caia dentro
    # del marron del hocico (distancia 1432) y mil bloques del cuerpo salian marrones.
    mejor, dist = None, 500
    for col, bloque in MARCAS:
        d = sum((a - b) ** 2 for a, b in zip(col, rgb))
        if d < dist:
            mejor, dist = bloque, d
    return mejor


def es_pelo(rgb):
    """Gris o casi: el pelo. Lo blanco, lo marron y lo rosa van por color."""
    r, g, b = rgb
    return max(r, g, b) - min(r, g, b) < 22 and max(r, g, b) < 130


def bloque_mas_cercano(rgb, lo=15, hi=90):
    """Indice en BLOQUES, o negativo para indicar posicion en la RAMPA."""
    if es_pelo(rgb):
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        t = min(1.0, max(0.0, (lum - lo) / max(1, hi - lo)))
        return -(1 + int(t * (len(RAMPA) - 1)))
    return min(range(len(BLOQUES)),
               key=lambda i: sum((a - b) ** 2 for a, b in zip(BLOQUES[i][1], rgb)))


def voxelizar(escala=2):
    """Devuelve (dimensiones, {voxel: indice de bloque}). Separado de main para
    poder previsualizar la estatua sin escribir el fichero."""
    geo = json.load(open(MODELO, encoding="utf-8"))
    bones = {b["name"]: b for b in geo["minecraft:geometry"][0]["bones"]}
    tex = Image.open(TEXTURA).convert("RGBA")
    tpx = tex.load()
    cache = {}

    # cubos en espacio mundo: (matriz, traslacion, origen, tam, rects de textura)
    piezas = []
    for nombre, b in bones.items():
        for c in b.get("cubes", []):
            if not isinstance(c.get("uv"), list):
                continue
            m, t = matriz_hueso(bones, nombre, cache)
            piezas.append((m, t, c["origin"], c["size"], caras(c["uv"], c["size"]), nombre))

    # volumen que ocupa todo, ya rotado
    pts = []
    for m, t, o, s, _, _ in piezas:
        for dx in (0, s[0]):
            for dy in (0, s[1]):
                for dz in (0, s[2]):
                    p = [o[0] + dx, o[1] + dy, o[2] + dz]
                    pts.append([sum(m[i][j] * p[j] for j in range(3)) + t[i] for i in range(3)])
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    dim = [int(math.ceil((hi[i] - lo[i]) * escala)) + 1 for i in range(3)]
    print(f"   volumen: {dim[0]} x {dim[1]} x {dim[2]} bloques")

    # Los detalles pequenos se comprueban primero para que ganen a las piezas
    # grandes: si no, la cabeza se come los ojos, que estan pegados a su superficie.
    piezas.sort(key=lambda p: p[3][0] * p[3][1] * p[3][2])

    # inversa de cada transformacion (es rigida: la traspuesta vale)
    inv = [([[m[j][i] for j in range(3)] for i in range(3)], t) for m, t, _, _, _, _ in piezas]

    crudos = {}
    for vy in range(dim[1]):
        for vz in range(dim[2]):
            for vx in range(dim[0]):
                # centro del voxel en unidades de modelo
                p = [lo[0] + (vx + 0.5) / escala, lo[1] + (vy + 0.5) / escala,
                     lo[2] + (vz + 0.5) / escala]
                for k, (mi, t) in enumerate(inv):
                    q = [p[i] - t[i] for i in range(3)]
                    lx = sum(mi[0][j] * q[j] for j in range(3))
                    ly = sum(mi[1][j] * q[j] for j in range(3))
                    lz = sum(mi[2][j] * q[j] for j in range(3))
                    _, _, o, s, rects, hueso = piezas[k]
                    # Los ojos y las bocas son planos de grosor 0: sin un minimo,
                    # ningun centro de voxel cae justo en el plano y desaparecen.
                    s = [max(v, 0.8) for v in s]
                    fx, fy, fz = lx - o[0], ly - o[1], lz - o[2]
                    if not (0 <= fx <= s[0] and 0 <= fy <= s[1] and 0 <= fz <= s[2]):
                        continue
                    # cara mas cercana -> color real de la textura
                    dist = {"izquierda": fx, "derecha": s[0] - fx, "abajo": fy,
                            "arriba": s[1] - fy, "frente": fz, "espalda": s[2] - fz}
                    cara = min(dist, key=dist.get)
                    rx, ry, rw, rh = rects[cara]
                    if cara in ("arriba", "abajo"):
                        u, v = fx / s[0], fz / s[2]
                    elif cara in ("frente", "espalda"):
                        u, v = fx / s[0], 1 - fy / s[1]
                    else:
                        u, v = fz / s[2], 1 - fy / s[1]
                    px = rx + min(rw - 1, int(u * rw))
                    py = ry + min(rh - 1, int(v * rh))
                    col = tpx[px, py]
                    if col[3] == 0:
                        continue
                    crudos[(vx, vy, vz)] = (col[:3], cara, dist[cara], hueso)
                    break

    # Segunda pasada, con criterio de estatua y no de textura.
    #
    # Muestrear el rizo pixel a pixel producia ruido: a escala de bloques, las motas
    # claras del pelo no se leen como pelo sino como desperfectos. Una estatua se lee
    # por su volumen, asi que el pelo se pinta segun la ORIENTACION de la superficie
    # — arriba mas claro, costados medio, interior negro — y solo las marcas
    # deliberadas (pecho, barbilla, collar, hocico, ojos) conservan su color.
    voxels = {}
    for pos, (rgb, cara, profundidad, hueso) in crudos.items():
        bloque = marca(rgb)
        if bloque is None:
            bloque = material_de(hueso)
        voxels[pos] = bloque

    print(f"   bloques colocados: {len(voxels)}")
    return dim, voxels


def main(escala=2, salida=None):
    dim, voxels = voxelizar(escala)
    usados = sorted(set(voxels.values()))
    paleta = [("compound", {"Name": ("str", "minecraft:air")})]
    remap = {}
    for nuevo, nombre in enumerate(usados, start=1):
        paleta.append(("compound", {"Name": ("str", nombre)}))
        remap[nombre] = nuevo
    print(f"   paleta: {len(paleta)} bloques distintos")

    bits = max(2, (len(paleta) - 1).bit_length())
    total = dim[0] * dim[1] * dim[2]
    longs = [0] * ((total * bits + 63) // 64)
    mascara = (1 << bits) - 1
    for (vx, vy, vz), b in voxels.items():
        idx = (vy * dim[2] + vz) * dim[0] + vx
        val = remap[b]
        off = idx * bits
        a, bit = off >> 6, off & 63
        # hay que recortar a 64 bits en cada escritura: si el valor cae a caballo
        # entre dos longs, el desplazamiento se sale y python no trunca solo.
        longs[a] = (longs[a] | ((val & mascara) << bit)) & 0xFFFFFFFFFFFFFFFF
        if bit + bits > 64:
            longs[a + 1] = (longs[a + 1] | ((val & mascara) >> (64 - bit))) & 0xFFFFFFFFFFFFFFFF
    longs = [v - (1 << 64) if v >= (1 << 63) else v for v in longs]

    ahora = int(time.time() * 1000)
    raiz = ("compound", {
        "MinecraftDataVersion": ("int", DATA_VERSION),
        "Version": ("int", 7),
        "SubVersion": ("int", 1),
        "Metadata": ("compound", {
            "Name": ("str", "Luna"),
            "Author": ("str", "PokeReport"),
            "Description": ("str", "Estatua de Luna, la perrita de AlejandroReport"),
            "RegionCount": ("int", 1),
            "TotalVolume": ("int", total),
            "TotalBlocks": ("int", len(voxels)),
            "TimeCreated": ("long", ahora),
            "TimeModified": ("long", ahora),
            "EnclosingSize": ("compound", {"x": ("int", dim[0]), "y": ("int", dim[1]),
                                           "z": ("int", dim[2])}),
        }),
        "Regions": ("compound", {"Luna": ("compound", {
            "Position": ("compound", {"x": ("int", 0), "y": ("int", 0), "z": ("int", 0)}),
            "Size": ("compound", {"x": ("int", dim[0]), "y": ("int", dim[1]), "z": ("int", dim[2])}),
            "BlockStatePalette": ("list", ("compound", [p[1] for p in paleta])),
            "BlockStates": ("longarray", longs),
            "Entities": ("list", ("compound", [])),
            # Las dos claves a proposito: en 1.21 Minecraft renombro TileEntity a
            # BlockEntity y Litematica menciona ambas. Vacias no estorban, y asi da
            # igual cual de las dos busque su lector.
            "TileEntities": ("list", ("compound", [])),
            "BlockEntities": ("list", ("compound", [])),
            "PendingBlockTicks": ("list", ("compound", [])),
            "PendingFluidTicks": ("list", ("compound", [])),
        })}),
    })

    cuerpo = _b(10) + _str("") + nbt(raiz)
    salida = salida or os.path.join(RAIZ, "build", f"luna_x{escala}.litematic")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with gzip.open(salida, "wb") as fh:
        fh.write(cuerpo)
    print(f"   {salida}  ({os.path.getsize(salida)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2,
                          sys.argv[2] if len(sys.argv) > 2 else None))
