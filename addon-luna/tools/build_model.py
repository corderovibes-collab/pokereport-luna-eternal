#!/usr/bin/env python3
"""Genera el modelo Bedrock de Luna y define el mapa UV que usa la textura.

Las proporciones salen de medir la referencia, no de inventarlas: cabeza cubica y
grande (es una cocker), orejas anchas que cuelgan por fuera y pasan de la mandibula,
hocico que sobresale, cuatro patas gruesas con hueco entre ellas, collar como pieza
propia rodeando el cuello, y sin cola.

Las UV usan el modo "box uv" de Bedrock, que reparte las seis caras de cada cubo en
una cruz con un orden fijo. `caras()` replica ese orden exacto, y por eso la textura
se puede pintar sin abrir Blockbench: sabemos que rectangulo es cada cara. Si aqui
cambia un tamano, la textura se regenera sola y sigue cuadrando.

El modelo mide 22 unidades de alto (1,4 bloques): perro mediano, no cachorro.
"""
import json
import os

TEX_W, TEX_H = 128, 128

# nombre -> (padre, pivote, origen del cubo, tamano, esquina uv)
HUESOS = {
    "luna":     (None,     [0, 0, 0],        None,                None,       None),
    "cuerpo":   ("luna",   [0, 12, 0],       [-4.5, 9, -4],       [9, 8, 13], [0, 0]),
    "collar":   ("cuerpo", [0, 14, -5],      [-5, 13, -6],        [10, 2, 3], [86, 0]),
    "cabeza":   ("cuerpo", [0, 15, -5],      [-4, 14, -12],       [8, 8, 7],  [44, 0]),
    "hocico":   ("cabeza", [0, 16, -12],     [-2.5, 14.5, -16],   [5, 4, 4],  [0, 24]),
    "oreja_izq":("cabeza", [4, 20, -9],      [4, 12, -11],        [2, 8, 5],  [20, 24]),
    "oreja_der":("cabeza", [-4, 20, -9],     [-6, 12, -11],       [2, 8, 5],  [36, 24]),
    "pata_del_izq": ("cuerpo", [2.5, 8, -2],  [0.5, 0, -3],       [4, 9, 4],  [52, 24]),
    "pata_del_der": ("cuerpo", [-2.5, 8, -2], [-4.5, 0, -3],      [4, 9, 4],  [70, 24]),
    "pata_tra_izq": ("cuerpo", [2.5, 8, 5],   [0.5, 0, 4],        [4, 9, 4],  [88, 24]),
    "pata_tra_der": ("cuerpo", [-2.5, 8, 5],  [-4.5, 0, 4],       [4, 9, 4],  [0, 46]),
}


def caras(uv, size):
    """Rectangulos (x, y, w, h) de cada cara segun el box-uv de Bedrock."""
    u, v = uv
    w, h, d = [int(round(s)) for s in size]
    return {
        "abajo":     (u + d,         v,     w, d),
        "arriba":    (u + d + w,     v,     w, d),
        "izquierda": (u,             v + d, d, h),
        "frente":    (u + d,         v + d, w, h),
        "derecha":   (u + d + w,     v + d, d, h),
        "espalda":   (u + d + w + d, v + d, w, h),
    }


def geometria():
    bones = []
    for nombre, (padre, pivote, origen, tam, uv) in HUESOS.items():
        b = {"name": nombre, "pivot": pivote}
        if padre:
            b["parent"] = padre
        if origen:
            b["cubes"] = [{"origin": origen, "size": tam, "uv": uv}]
        bones.append(b)
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.luna",
                "texture_width": TEX_W,
                "texture_height": TEX_H,
                "visible_bounds_width": 3,
                "visible_bounds_height": 2.5,
                "visible_bounds_offset": [0, 1, 0],
            },
            "bones": bones,
        }],
    }


def comprobar_uv():
    """Ningun cubo puede salirse del atlas ni pisar a otro."""
    ocupado = {}
    for nombre, (_, _, _, tam, uv) in HUESOS.items():
        if not uv:
            continue
        for cara, (x, y, w, h) in caras(uv, tam).items():
            if x + w > TEX_W or y + h > TEX_H:
                raise SystemExit(f"{nombre}/{cara} se sale del atlas: {(x, y, w, h)}")
            for px in range(x, x + w):
                for py in range(y, y + h):
                    otro = ocupado.get((px, py))
                    if otro and otro != nombre:
                        raise SystemExit(f"solapan {nombre} y {otro} en {(px, py)}")
                    ocupado[(px, py)] = nombre
    return len(ocupado)


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    usados = comprobar_uv()
    destino = os.path.join(raiz, "assets", "cobblemon", "bedrock", "pokemon", "models", "9001_luna")
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, "luna.geo.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(geometria(), fh, indent=2)
    piezas = [n for n, v in HUESOS.items() if v[2]]
    alto = max(v[2][1] + v[3][1] for v in HUESOS.values() if v[2])
    print(f"   luna.geo.json: {len(piezas)} cubos, {alto} unidades de alto")
    print(f"   atlas {TEX_W}x{TEX_H}: {usados} px usados, sin solapes ni desbordes")
