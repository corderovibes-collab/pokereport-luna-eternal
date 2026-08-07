# -*- coding: utf-8 -*-
"""Genera las cinemáticas del evento para Cutscene API.

Esquema tomado de los ejemplos reales del repositorio del mod
(thewinnt/Cutscene-API, carpeta «Example Cutscenes»), no inventado.

Notas del formato, comprobadas en esos ejemplos:

  - `length` va en ticks (20 por segundo).
  - Las coordenadas del camino son **relativas al punto de arranque** que se pasa
    al comando, así que la misma cinemática sirve en cualquier lugar del mapa.
  - Segmentos: `bezier` (con dos puntos de control, ambos anulables),
    `catmull_rom` (lista de puntos) y `line`.
  - La rotación usa los mismos segmentos, con `is_rotation: true`, y admite una
    curva de suavizado distinta por eje.
  - `[x, y, z]` en rotación es [cabeceo, guiñada, alabeo].

La duración de cada plano sale de la duración real de las líneas de voz
(`datos/duraciones.json`), no de números a ojo: si se regraba una línea y cambia
de largo, la cámara se ajusta sola al regenerar.

Uso:  python evento/build_cine.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-Cine-DP.zip")
PACK_FORMAT = 48

DUR = json.load(open(os.path.join(RAIZ, "datos", "duraciones.json"), encoding="utf-8"))
TICK = 20

ficheros: dict[str, dict] = {}


def fundido(entrada: bool, ticks_a=25, ticks_b=25, color=(0, 0, 0)) -> dict:
    return {
        "type": "cutscenes:fade",
        "length_a": ticks_a,
        "length_b": ticks_b,
        "color": list(color),
        "ease_in": "in_quad",
        "ease_out": "out_quad",
        "is_start": entrada,
    }


def bezier(inicio, fin, ca=None, cb=None) -> dict:
    return {"type": "cutscenes:bezier", "start": list(inicio),
            "control_a": list(ca) if ca else None,
            "control_b": list(cb) if cb else None,
            "end": list(fin)}


def giro(inicio, fin, ex="in_out_cubic", ey="in_out_cubic", ez="linear") -> dict:
    return {"type": "cutscenes:line", "start": list(inicio), "end": list(fin),
            "easing_x": ex, "easing_y": ey, "easing_z": ez, "is_rotation": True}


def fijo(punto) -> dict:
    return {"type": "cutscenes:constant", "point": list(punto)}


def cine(ident: str, segundos: float, camino: list, rotacion: list,
         color_entrada=(0, 0, 0), color_salida=(0, 0, 0)) -> None:
    ficheros[f"data/evento/cutscenes/{ident}.json"] = {
        "version": 0,
        "length": int(segundos * TICK),
        "start_transition": fundido(True, color=color_entrada),
        "end_transition": fundido(False, color=color_salida),
        "path": {"segments": camino},
        "rotation": {"segments": rotacion},
        # El jugador mira, no toca. Pero se le deja cambiar de perspectiva por si
        # alguien quiere verse a si mismo en el plano.
        "disable_actions": {
            "default": True,
            "change_perspective": False,
            "hide_self": True,
            "consider_spectator": False,
        },
    }


# ===========================================================================
#  APERTURA — Acto I
# ===========================================================================
#
# Dura lo que las dos primeras lineas de Oak. La camara arranca a ras de suelo,
# se eleva describiendo un arco sobre el grupo, barre el paisaje mientras Oak
# cuenta lo de la lectura de energia, y vuelve a bajar hasta quedarse frente a
# ellos justo cuando calla.
SEG_APERTURA = DUR["a1_01"] + DUR["a1_02"]        # 8 + 12 = 20 s

cine("apertura", SEG_APERTURA,
     camino=[
         # 1. Se despega del suelo, despacio, casi sin que se note
         bezier([0, 1, 0], [0, 14, -6], ca=[0, 6, -1], cb=[0, 11, -4]),
         # 2. Sube y se abre hacia el cielo, ganando altura y distancia
         bezier([0, 14, -6], [-34, 42, -30], ca=[-8, 26, -14], cb=[-24, 38, -24]),
         # 3. Gran barrido lateral: aqui es donde se ve el mundo
         bezier([-34, 42, -30], [34, 40, -28], ca=[-14, 55, -52], cb=[16, 54, -50]),
         # 4. Cae en picado controlado y frena delante del grupo
         bezier([34, 40, -28], [0, 2, -7], ca=[26, 22, -18], cb=[10, 6, -10]),
     ],
     rotacion=[
         # Empieza mirando al cielo y termina a la altura de los ojos
         giro([-38, 0, 0], [8, -190, 0]),
     ],
     # Entra desde negro y sale a blanco: el corte al blanco enlaza con el titulo
     color_entrada=(0, 0, 0), color_salida=(255, 255, 255))


# ===========================================================================
#  REVELACIÓN — Acto V
# ===========================================================================
#
# Orbita cerrada alrededor de la capsula mientras Oak entiende lo que tiene
# delante. Lenta, sin sobresaltos: aqui el espectaculo es lo que se dice.
SEG_REVELACION = DUR["a5_01d"] + DUR["a5_01e"]    # 14 + 11 = 25 s

cine("revelacion", SEG_REVELACION,
     camino=[
         # Media orbita, subiendo
         bezier([6, 2, 0], [0, 5, 7], ca=[6, 3, 4], cb=[4, 4, 7]),
         bezier([0, 5, 7], [-6, 7, 0], ca=[-4, 6, 7], cb=[-6, 7, 4]),
         # Se cierra sobre la capsula y se queda quieta
         bezier([-6, 7, 0], [0, 3, -3], ca=[-6, 6, -5], cb=[-3, 4, -5]),
     ],
     rotacion=[
         giro([12, -90, 0], [-6, 30, 0], ex="in_out_quad", ey="in_out_quad"),
     ],
     color_entrada=(0, 0, 0), color_salida=(0, 0, 0))


# ===========================================================================
#  LABORATORIO — Acto IV
# ===========================================================================
#
# Plano de establecimiento cuando se abre la entrada. Corto y seco, como una
# amenaza: baja al agujero y se para.
cine("laboratorio", 7,
     camino=[bezier([0, 12, 12], [0, 1, 2], ca=[0, 10, 6], cb=[0, 3, 3])],
     rotacion=[giro([50, 0, 0], [4, 0, 0], ex="in_out_cubic")],
     color_entrada=(0, 0, 0), color_salida=(0, 0, 0))


# ===========================================================================
#  Empaquetado
# ===========================================================================
def main() -> int:
    meta = {"pack": {"pack_format": PACK_FORMAT,
                     "description": "PokeReport · El Rastro de Luna — cinemáticas"}}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, indent=2, ensure_ascii=False))
        for ruta, datos in ficheros.items():
            z.writestr(ruta, json.dumps(datos, indent=2, ensure_ascii=False))

    print(f"   {SALIDA}")
    for r, d in ficheros.items():
        nombre = r.split("/")[-1][:-5]
        segs = len(d["path"]["segments"])
        print(f"     evento:{nombre:<14} {d['length']:>4} ticks ({d['length']/TICK:.0f} s)  "
              f"{segs} segmento(s) de cámara")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
