#!/usr/bin/env python3
"""Genera la capa de personalizacion del cliente: marca propia y ajustes de rendimiento.

Todo lo que sale de aqui se copia encima de la instancia del modpack, asi que del
COBBLEVERSE original no queda nada a la vista: titulo de ventana, iconos, pantalla
de carga, menus y lista de servidores. Ademas deja el juego configurado para un PC
justo (sin shaders, distancias cortas), que es lo que mas se nota.

Uso:
  python scripts/build_client.py --mrpack "client-pack/COBBLEVERSE 1.7.42.mrpack" \
      --out client-pack/menu
"""
from __future__ import annotations

import argparse
import io
import os
import re
import struct
import sys
import zipfile

SERVIDOR_NOMBRE = "PokeReport: Luna Eternal"
SERVIDOR_IP = "s17.mia.us.tarohosting.lat:33445"
TITULO_VENTANA = "PokeReport: Luna Eternal"

ASSETS = "config/fancymenu/assets"


# --------------------------------------------------------------------- NBT

def _str(valor: str) -> bytes:
    b = valor.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def servers_dat(entradas: list[tuple[str, str]]) -> bytes:
    """servers.dat es NBT **sin comprimir**; son cuatro etiquetas, no hace falta libreria."""
    cuerpo = b""
    for nombre, ip in entradas:
        cuerpo += b"\x08" + _str("name") + _str(nombre)
        cuerpo += b"\x08" + _str("ip") + _str(ip)
        cuerpo += b"\x00"  # fin del compound de este servidor
    lista = b"\x09" + _str("servers") + b"\x0a" + struct.pack(">i", len(entradas)) + cuerpo
    return b"\x0a" + _str("") + lista + b"\x00"


# ------------------------------------------------------------ ajustes del juego

def options_txt() -> str:
    """Ajustes de video pensados para un PC limitado.

    Se marca `once` en el manifiesto, asi que esto es solo el punto de partida: en
    cuanto el jugador toque algo en las opciones, manda lo suyo y no se le pisa.
    """
    ajustes = {
        # Lo que mas cuesta, por orden.
        "renderDistance": 6,          # el servidor manda 8; pedir mas no aporta nada
        "simulationDistance": 5,
        "graphicsMode": 0,            # rapido
        "particles": 2,               # minimo: los combates Pokemon escupen muchisimas
        "entityShadows": "false",
        "entityDistanceScaling": 0.5,
        "biomeBlendRadius": 0,
        "mipmapLevels": 0,
        "ao": "false",
        "cloudStatus": 0,
        "screenEffectScale": 0.0,
        "fovEffectScale": 0.0,
        "darknessEffectScale": 0.0,
        "bobView": "false",
        "enableVsync": "false",
        "maxFps": 120,
        "guiScale": 2,
        "fov": 70.0,
        "renderClouds": "false",
        "chatOpacity": 1.0,
        "pauseOnLostFocus": "false",   # el juego sigue cargando si te vas a otra ventana
        "narrator": 0,
        "tutorialStep": "none",
        "skipMultiplayerWarning": "true",
        "onboardAccessibility": "false",
        "joinedFirstServer": "true",   # sin esto sale el aviso al entrar por primera vez
    }
    return "".join(f"{k}:{v}\n" for k, v in ajustes.items())


def iris_properties(original: str) -> str:
    """Shaders fuera. Es, con diferencia, lo que mas FPS devuelve en un equipo justo."""
    texto = re.sub(r"^enableShaders=.*$", "enableShaders=false", original, flags=re.M)
    texto = re.sub(r"^shaderPack=.*$", "shaderPack=", texto, flags=re.M)
    return texto


def fancymenu_options(original: str) -> str:
    """Titulo e iconos de la ventana: es lo primero que se ve y decia COBBLEVERSE."""
    texto = re.sub(r"^(\s*S:custom_window_title = ').*?(';)$",
                   rf"\1{TITULO_VENTANA}\2", original, flags=re.M)
    texto = re.sub(r"^(\s*S:custom_window_icon_16 = ').*?(';)$",
                   rf"\1/{ASSETS}/pokereport_icon_16.png\2", texto, flags=re.M)
    texto = re.sub(r"^(\s*S:custom_window_icon_32 = ').*?(';)$",
                   rf"\1/{ASSETS}/pokereport_icon_32.png\2", texto, flags=re.M)
    # El .icns es solo de macOS; se deja apuntando al original para no romper la clave.
    return texto


def quitar_marca(layout: str) -> str:
    """Cambia el titulo de COBBLEVERSE por el nuestro en cualquier layout de FancyMenu."""
    return layout.replace(f"[source:local]/{ASSETS}/cobbleverse_title.png",
                          f"[source:local]/{ASSETS}/pokereport_logo.png")


# ---------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mrpack", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    z = zipfile.ZipFile(args.mrpack)

    def leer(rel: str) -> str:
        return z.read(f"overrides/{rel}").decode("utf-8")

    def escribir(rel: str, datos) -> None:
        destino = os.path.join(args.out, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        modo = "wb" if isinstance(datos, bytes) else "w"
        with io.open(destino, modo, **({} if isinstance(datos, bytes) else {"encoding": "utf-8", "newline": "\n"})) as fh:
            fh.write(datos)
        print(f"  {rel}")

    print("Marca propia:")
    escribir("config/fancymenu/options.txt", fancymenu_options(leer("config/fancymenu/options.txt")))
    for layout in ("cobbleverse_pause_menu.txt", "cobbleverse_resourcepack_selection.txt",
                   "cobbleverse_multiplayer_screen.txt"):
        try:
            escribir(f"config/fancymenu/customization/{layout}",
                     quitar_marca(leer(f"config/fancymenu/customization/{layout}")))
        except KeyError:
            print(f"  (no existe {layout}, se omite)")

    print("Servidor:")
    escribir("servers.dat", servers_dat([(SERVIDOR_NOMBRE, SERVIDOR_IP)]))

    print("Rendimiento:")
    escribir("options.txt", options_txt())
    escribir("config/iris.properties", iris_properties(leer("config/iris.properties")))

    print("\nListo. Falta el arte: ver docs/menu-arte.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
