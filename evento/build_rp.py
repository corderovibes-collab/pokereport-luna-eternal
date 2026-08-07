# -*- coding: utf-8 -*-
"""Monta el resourcepack de audio del evento a partir de los OGG ya convertidos.

Se regenera entero cada vez: sounds.json se deriva de los ficheros que hay en
disco, asi que anadir o quitar una linea no obliga a tocar nada a mano.

Uso:  python evento/build_rp.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(RAIZ, "audio")
SALIDA = os.path.join(RAIZ, "build", "Evento-RP.zip")

# 34 = formato de resourcepack de 1.21.1
META = {
    "pack": {
        "pack_format": 34,
        "description": "PokeReport · El Rastro de Luna — voces del evento",
    }
}


def main():
    sonidos = {}
    ficheros = []
    for carpeta, _, nombres in os.walk(AUDIO):
        for n in sorted(nombres):
            if not n.endswith(".ogg"):
                continue
            ruta = os.path.join(carpeta, n)
            rel = os.path.relpath(ruta, AUDIO).replace(os.sep, "/")
            ficheros.append((ruta, rel))
            # voz/oak/a1_01.ogg  ->  clave voz.oak.a1_01
            clave = rel[:-4].replace("/", ".")
            sonidos[clave] = {
                "category": "voice",
                # stream=true evita cargar en memoria las lineas largas
                "sounds": [{"name": f"evento:{rel[:-4]}", "stream": True}],
            }

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(META, indent=2, ensure_ascii=False))
        z.writestr("assets/evento/sounds.json", json.dumps(sonidos, indent=2, ensure_ascii=False))
        for ruta, rel in ficheros:
            # Los OGG ya van comprimidos: recomprimir solo gasta tiempo.
            z.write(ruta, f"assets/evento/sounds/{rel}", compress_type=zipfile.ZIP_STORED)

    print(f"   {SALIDA}")
    print(f"   {len(ficheros)} sonidos, {os.path.getsize(SALIDA)/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
