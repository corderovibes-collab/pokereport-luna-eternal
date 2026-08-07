#!/usr/bin/env python3
"""Despliega los mods server-side en el servidor Pterodactyl.

Usa /files/pull para que el nodo descargue directo del CDN de Modrinth (rapido,
no sube nada desde casa). Reintenta los que falten y verifica al final.

Uso:  PTERO_KEY=... python scripts/deploy_mods.py [--verify-only]
"""
import json, os, sys, time
import concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptero

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "server-pack", "mods-manifest.json")


def present():
    """Nombres de ficheros ya presentes en /mods (con su tamano)."""
    try:
        data = ptero.ls("/mods")["data"]
    except RuntimeError:
        return {}
    return {e["attributes"]["name"]: e["attributes"]["size"] for e in data}


def main():
    entries = json.load(open(MANIFEST, encoding="utf-8"))
    remote = [e for e in entries if e["url"]]

    try:
        ptero.mkdir("/", "mods")
    except RuntimeError:
        pass

    if "--verify-only" not in sys.argv:
        for attempt in range(1, 5):
            have = present()
            todo = [e for e in remote if have.get(e["file"], 0) == 0]
            if not todo:
                break
            print(f"[intento {attempt}] faltan {len(todo)} mods, descargando...")

            def grab(e):
                try:
                    ptero.pull(e["url"], directory="/mods", filename=e["file"])
                    return None
                except RuntimeError as exc:
                    return f"{e['file']}: {str(exc)[:120]}"

            with cf.ThreadPoolExecutor(max_workers=4) as ex:
                errs = [r for r in ex.map(grab, todo) if r]
            for x in errs[:10]:
                print("   ERR", x)
            # las descargas son asincronas en wings: dar tiempo a que terminen
            time.sleep(20 + len(todo) * 0.6)

    have = present()
    missing = [e["file"] for e in remote if have.get(e["file"], 0) == 0]
    print(f"\npresentes en /mods: {len(have)}   esperados (remotos): {len(remote)}")
    if missing:
        print("FALTAN:")
        for m in missing:
            print("  ", m)
        return 1
    print("OK: todos los mods remotos estan en el servidor")
    extra = set(have) - {e["file"] for e in entries}
    if extra:
        print("Ficheros extra en /mods (revisar):", sorted(extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
