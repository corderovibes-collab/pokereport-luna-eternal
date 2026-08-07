#!/usr/bin/env python3
"""Empaqueta el addon de Luna en dos zips.

Van separados a proposito: el servidor solo necesita los datos de especie y el
cliente solo el modelo y la textura, y asi cada lado carga lo justo. Los dos se
sirven con GlobalPacks, igual que los datapacks de COBBLEVERSE.

Uso:  python addon-luna/tools/package.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# carpeta -> (nombre del zip, pack_format, descripcion)
#   48 = datapack de 1.21.1   ·   34 = resourcepack de 1.21.1
PAQUETES = {
    "data": ("Luna-DP.zip", 48, "Luna, la perrita de AlejandroReport - datos de especie"),
    "assets": ("Luna-RP.zip", 34, "Luna, la perrita de AlejandroReport - modelo y textura"),
}


def main():
    destino = os.path.join(RAIZ, "build")
    os.makedirs(destino, exist_ok=True)

    for carpeta, (nombre, fmt, desc) in PAQUETES.items():
        ruta = os.path.join(destino, nombre)
        origen = os.path.join(RAIZ, carpeta)
        with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("pack.mcmeta", json.dumps(
                {"pack": {"pack_format": fmt, "description": desc}}, indent=2))
            n = 0
            for base, _, ficheros in os.walk(origen):
                for f in ficheros:
                    completo = os.path.join(base, f)
                    interno = os.path.relpath(completo, RAIZ).replace(os.sep, "/")
                    z.write(completo, interno)
                    n += 1
        print("   %-14s %7d bytes  %d ficheros" % (nombre, os.path.getsize(ruta), n))

    for carpeta, (nombre, _, _) in PAQUETES.items():
        with zipfile.ZipFile(os.path.join(destino, nombre)) as z:
            print("\n  ", nombre)
            for x in z.namelist():
                print("     ", x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
