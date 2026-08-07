#!/usr/bin/env python3
"""Genera el manifest.json que consume el launcher, a partir del .mrpack oficial.

El manifiesto describe la instancia de cliente completa (mods, config, resource
packs, shaders, datapacks) con SHA1 y tamano de cada fichero. El launcher compara
ese SHA1 con lo que hay en disco, asi que anadir o cambiar un mod en el futuro es
solo regenerar este fichero y volver a publicarlo: los jugadores reciben el delta.

Uso:
  python tools/build_manifest.py --mrpack "COBBLEVERSE 1.7.42.mrpack" --out manifest.json
  python tools/build_manifest.py ... --assets-base https://github.com/<user>/<repo>/releases/download/pack-1.7.42
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zipfile

UA = {"User-Agent": "cobbleverse-manifest/1.0"}

# Carpetas del .mrpack que van tal cual a la instancia del cliente.
OVERRIDE_DIRS = ("config/", "datapacks/", "resourcepacks/", "shaderpacks/", "mods/")

# Ficheros que se escriben una vez y luego son del jugador: el launcher no los pisa.
# Se comparan por ruta exacta, no por terminacion: `config/fancymenu/options.txt`
# tambien acaba en "options.txt" y ese si tiene que actualizarse con el pack.
# `iris.properties` lo ponemos nosotros (shaders apagados de salida) pero a partir
# de ahi es del jugador: si lo reescribieramos, quien los encienda se los veria
# apagados otra vez en cada actualizacion.
ONCE = frozenset({"options.txt", "servers.dat", "config/iris.properties"})


def es_del_jugador(rel: str, gestionados: set[str]) -> bool:
    """Decide si un fichero deja de tocarse tras la primera instalacion.

    Todo lo de `config/` es configuracion que el jugador puede querer cambiar
    (controles, Sodium, volumen del chat de voz...). Si el launcher lo reescribiera
    en cada actualizacion, cada vez que alguien vuelve a jugar perderia sus ajustes.
    Se exceptua lo que ponemos nosotros a proposito (el menu y la marca), que si
    tiene que actualizarse.
    """
    if rel in ONCE:
        return True
    return rel.startswith("config/") and rel not in gestionados


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def modrinth_client_files(mrpack: zipfile.ZipFile) -> tuple[list[dict], dict]:
    """Ficheros del indice que valen para el cliente, con su URL del CDN de Modrinth."""
    index = json.loads(mrpack.read("modrinth.index.json"))
    out = []
    for entry in index["files"]:
        env = entry.get("env", {})
        if env.get("client") == "unsupported":
            continue
        out.append({
            "path": entry["path"].replace("\\", "/"),
            "sha1": entry["hashes"]["sha1"],
            "size": entry.get("fileSize"),
            "url": entry["downloads"][0],
        })
    return out, index


# Carpetas con miles de ficheros diminutos: se sirven como un unico zip en vez de
# como entradas sueltas. 1234 peticiones para un shaderpack no tienen sentido.
BUNDLE_DIRS = ("shaderpacks/",)


def override_files(mrpack: zipfile.ZipFile) -> tuple[list[tuple[str, bytes]], list[tuple[str, bytes]]]:
    """Divide overrides/ en (ficheros sueltos, carpetas empaquetadas como zip)."""
    loose: list[tuple[str, bytes]] = []
    bundles: dict[str, list[tuple[str, bytes]]] = {}

    for info in mrpack.infolist():
        if info.is_dir() or not info.filename.startswith("overrides/"):
            continue
        rel = info.filename[len("overrides/"):]
        if not rel or rel.endswith(".pdf"):
            continue
        if not rel.startswith(OVERRIDE_DIRS):
            continue

        if rel.startswith(BUNDLE_DIRS) and rel.count("/") >= 2:
            # shaderpacks/<nombre>/... -> se agrupa por la carpeta de segundo nivel
            root = "/".join(rel.split("/")[:2])
            bundles.setdefault(root, []).append((rel[len(root) + 1:], mrpack.read(info)))
        else:
            loose.append((rel, mrpack.read(info)))

    packed = []
    for root, entries in sorted(bundles.items()):
        buf = io.BytesIO()
        # Sin timestamps variables: el mismo contenido produce el mismo SHA1, y asi
        # regenerar el manifiesto no obliga a los jugadores a bajarlo otra vez.
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for name, data in sorted(entries):
                zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, data)
        packed.append((root, buf.getvalue()))
        print(f"  empaquetado {root}: {len(entries)} ficheros -> {len(buf.getvalue()) / 1048576:.1f} MB")

    return loose, packed


def extra_mods(paths: list[str]) -> list[tuple[str, bytes]]:
    out = []
    for p in paths:
        for name in sorted(os.listdir(p)):
            full = os.path.join(p, name)
            if os.path.isfile(full) and name.endswith(".jar"):
                with open(full, "rb") as fh:
                    out.append((f"mods/{name}", fh.read()))
    return out


def fetch_json(url: str):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())


def modrinth_extra(slugs: list[str], mc: str, loader: str, optional: bool = True) -> list[dict]:
    """Resuelve mods sueltos por slug contra Modrinth (extras de optimizacion, skins, voz)."""
    out = []
    for slug in slugs:
        q = urllib.parse.urlencode({"game_versions": f'["{mc}"]', "loaders": f'["{loader}"]'})
        versions = fetch_json(f"https://api.modrinth.com/v2/project/{slug}/version?{q}")
        if not versions:
            print(f"  AVISO: {slug} no tiene build para {mc}/{loader}, se omite", file=sys.stderr)
            continue
        v = versions[0]
        f = next((x for x in v["files"] if x["primary"]), v["files"][0])
        entry = {
            "path": f"mods/{f['filename']}",
            "sha1": f["hashes"]["sha1"],
            "size": f["size"],
            "url": f["url"],
        }
        if optional:
            entry.update({"optional": True, "group": "extra"})
        out.append(entry)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mrpack", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--payload-dir", default=None,
                    help="donde escribir los ficheros de overrides que hay que subir a GitHub")
    ap.add_argument("--assets-base", default="",
                    help="URL base desde la que se serviran esos ficheros")
    ap.add_argument("--local-mods", nargs="*", default=[],
                    help="carpetas con jars que no estan en ningun CDN (se sirven desde GitHub)")
    ap.add_argument("--server-host", default="s17.mia.us.tarohosting.lat")
    ap.add_argument("--server-port", type=int, default=33445)
    # Obligatorios, no opcionales:
    #  - voice chat: quien no lo tenga no oye a nadie.
    #
    # Las skins ya no piden nada en el cliente: las sirve SkinRestorer desde el
    # servidor (/skin set ely.by | web) por el sistema oficial de Mojang, asi que
    # las ve todo el mundo, tenga mods de skins o no. Fabric Tailor sale de aqui
    # porque su ventana solo funciona si el mismo mod esta en el servidor, y alli
    # lo sustituye SkinRestorer (los dos registran /skin y no pueden convivir).
    ap.add_argument("--required-extra", nargs="*",
                    default=["simple-voice-chat"])
    ap.add_argument("--overlay", nargs="*", default=[],
                    help="carpetas cuyo contenido se copia tal cual sobre la instancia (menu, etc.)")
    # SkinShuffle queda fuera a proposito: mete un muñeco del jugador y un boton
    # de "Presets de Skin" en la pantalla de inicio, encima del menu. El launcher
    # ya tiene su propio visor de personaje, asi que no aporta y estorba.
    ap.add_argument("--extra", nargs="*", default=[
        "sodium-extra", "dynamic-fps", "threadtweak", "language-reload",
        "fast-ip-ping", "3dskinlayers",
    ])
    args = ap.parse_args()

    mrpack = zipfile.ZipFile(args.mrpack)
    files, index = modrinth_client_files(mrpack)
    mc = index["dependencies"]["minecraft"]
    loader = index["dependencies"]["fabric-loader"]
    print(f"pack {index['versionId']} | minecraft {mc} | fabric {loader}")
    print(f"  ficheros de cliente en el indice: {len(files)}")

    loose, packed = override_files(mrpack)
    if args.local_mods:
        loose += extra_mods(args.local_mods)
    print(f"  ficheros de overrides: {len(loose)} sueltos + {len(packed)} empaquetados")

    base = args.assets_base.rstrip("/")
    if args.payload_dir:
        os.makedirs(args.payload_dir, exist_ok=True)

    vistos: dict[str, str] = {}

    # Lo que viene de nuestros overlays se gestiona siempre; lo del pack, no.
    gestionados: set[str] = set()
    for overlay in args.overlay:
        for root, _, names in os.walk(overlay):
            for name in names:
                gestionados.add(os.path.relpath(os.path.join(root, name), overlay).replace("\\", "/"))

    def publish(rel: str, data: bytes, entry: dict) -> None:
        # GitHub Releases aplana los nombres, asi que se codifica la ruta en el nombre.
        #
        # Y ademas los **renombra**: cualquier caracter que no sea alfanumerico, punto,
        # guion o guion bajo lo sustituye. Si el manifiesto apunta al nombre original,
        # la descarga da 404 (paso con los shaderpacks, que llevan parentesis). Por eso
        # se sanea aqui: lo que se sube y lo que se pide son el mismo nombre.
        flat = re.sub(r"[^A-Za-z0-9._-]", "_", rel.replace("/", "__"))
        if flat in vistos and vistos[flat] != rel:
            sys.exit(f"Colision de nombres al aplanar: '{rel}' y '{vistos[flat]}' -> '{flat}'")
        vistos[flat] = rel
        entry.update({
            "path": rel,
            "sha1": sha1_bytes(data),
            "size": len(data),
            "url": f"{base}/{urllib.parse.quote(flat)}" if base else f"PENDIENTE/{flat}",
        })
        files.append(entry)
        if args.payload_dir:
            with open(os.path.join(args.payload_dir, flat), "wb") as fh:
                fh.write(data)

    for rel, data in loose:
        publish(rel, data, {"once": es_del_jugador(rel, gestionados)})
    for rel, data in packed:
        publish(f"{rel}.zip", data, {})
        # El destino de extraccion es la carpeta original, sin el .zip del nombre.
        files[-1]["path"] = rel
        files[-1]["archive"] = True

    # Ficheros propios (el menu de FancyMenu y su arte) que no salen del .mrpack.
    for overlay in args.overlay:
        for root, _, names in os.walk(overlay):
            for name in sorted(names):
                full = os.path.join(root, name)
                rel = os.path.relpath(full, overlay).replace("\\", "/")
                with open(full, "rb") as fh:
                    # `once` tambien aqui: options.txt y servers.dat salen del overlay
                    # y son ajustes que el jugador puede cambiar despues.
                    publish(rel, fh.read(), {"once": rel in ONCE})
        print(f"  overlay {overlay}: aplicado")

    print("  resolviendo extras en Modrinth...")
    files += modrinth_extra(args.required_extra, mc, "fabric", optional=False)
    files += modrinth_extra(args.extra, mc, "fabric")

    # Un overlay puede pisar un fichero del pack (el layout de FancyMenu, sin ir mas
    # lejos). Si quedan las dos entradas, el launcher se baja las dos en paralelo y
    # cual acaba en disco es una carrera: hay que dejar solo la ultima.
    unique: dict[str, dict] = {}
    for entry in files:
        unique[entry["path"]] = entry
    if len(unique) != len(files):
        print(f"  deduplicadas {len(files) - len(unique)} rutas repetidas (gana el overlay)")
    files = list(unique.values())

    manifest = {
        "schema": 1,
        "name": "COBBLEVERSE",
        "packVersion": index["versionId"],
        "minecraft": mc,
        "fabricLoader": loader,
        "java": 21,
        "server": {"host": args.server_host, "port": args.server_port, "name": "PokeReport: Luna Eternal"},
        "files": files,
    }

    with io.open(args.out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)

    total = sum(f.get("size") or 0 for f in files)
    print(f"\nescrito {args.out}: {len(files)} ficheros, {total / 1048576:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
