#!/usr/bin/env python3
"""Publica el pack en GitHub: sube los ficheros y deja el manifest.json servido.

Reparto por defecto:
  - Los mods vienen del CDN de Modrinth (mas rapido y no gasta tu cuota de GitHub).
  - Lo propio del pack (config, resourcepacks, datapacks, shaders) va a una Release.
  - El manifest.json se commitea a la rama principal, que es la URL fija que lee
    el launcher; asi actualizar el pack es volver a ejecutar esto.

Requiere la CLI `gh` autenticada (gh auth login).

Uso:
  python tools/publish_github.py --repo usuario/cobbleverse-pack \
      --manifest ../client-pack/manifest.json --payload <carpeta> --version 1.7.42
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, text=True, capture_output=True, **kw)


def need_gh() -> None:
    if shutil.which("gh") is None:
        sys.exit("Falta la CLI de GitHub. Instalala desde https://cli.github.com y haz `gh auth login`.")
    if run(["gh", "auth", "status"]).returncode != 0:
        sys.exit("`gh` no esta autenticado. Ejecuta: gh auth login")


def ensure_repo(repo: str, private: bool) -> None:
    if run(["gh", "repo", "view", repo]).returncode == 0:
        print(f"  repo {repo}: ya existe")
        return
    print(f"  repo {repo}: creando...")
    vis = "--private" if private else "--public"
    res = run(["gh", "repo", "create", repo, vis, "--description",
               "Pack del launcher privado de Cobbleverse"])
    if res.returncode != 0:
        sys.exit(f"No se pudo crear el repo:\n{res.stderr}")


def seed_repo(repo: str) -> None:
    """Un repo recien creado esta vacio y GitHub rechaza crear releases ahi.

    Se sube un README con la API de contenidos, que ademas crea la rama por defecto.
    """
    if run(["gh", "api", f"repos/{repo}/contents/README.md"]).returncode == 0:
        return

    readme = (
        "# PokeReport: Luna Eternal\n\n"
        "Ficheros del modpack para el launcher privado del servidor.\n\n"
        "- `manifest.json` es lo que lee el launcher.\n"
        "- Los ficheros del pack van en las *releases*, etiquetadas `pack-<version>`.\n\n"
        "Generado con `tools/publish_github.py`.\n"
    )
    content = base64.b64encode(readme.encode()).decode()
    res = run(["gh", "api", f"repos/{repo}/contents/README.md", "-X", "PUT",
               "-f", "message=Commit inicial", "-f", f"content={content}"])
    if res.returncode != 0:
        sys.exit(f"No se pudo inicializar el repo:\n{res.stderr}")
    print("  repo inicializado con un README")


def ensure_release(repo: str, tag: str) -> None:
    if run(["gh", "release", "view", tag, "--repo", repo]).returncode == 0:
        print(f"  release {tag}: ya existe, se reutiliza")
        return
    print(f"  release {tag}: creando...")
    res = run(["gh", "release", "create", tag, "--repo", repo,
               "--title", f"Pack {tag}", "--notes", "Ficheros del modpack para el launcher."])
    if res.returncode != 0:
        sys.exit(f"No se pudo crear la release:\n{res.stderr}")


def upload_assets(repo: str, tag: str, payload: str) -> None:
    names = sorted(os.listdir(payload))
    print(f"  subiendo {len(names)} ficheros a la release...")
    # `gh release upload` acepta varios de golpe; en lotes para que un fallo no
    # obligue a repetir los 250 y para poder ver el avance.
    BATCH = 25
    for i in range(0, len(names), BATCH):
        chunk = [os.path.join(payload, n) for n in names[i:i + BATCH]]
        res = run(["gh", "release", "upload", tag, "--repo", repo, "--clobber", *chunk])
        if res.returncode != 0:
            sys.exit(f"Fallo subiendo el lote {i // BATCH + 1}:\n{res.stderr}")
        print(f"    {min(i + BATCH, len(names))}/{len(names)}")


def rewrite_manifest(manifest_path: str, repo: str, tag: str) -> dict:
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)

    base = f"https://github.com/{repo}/releases/download/{urllib.parse.quote(tag)}"
    changed = 0
    for entry in manifest["files"]:
        if entry["url"].startswith("PENDIENTE/"):
            entry["url"] = f"{base}/{entry['url'][len('PENDIENTE/'):]}"
            changed += 1
    print(f"  manifiesto: {changed} URLs apuntando ya a la release")

    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    return manifest


def commit_manifest(repo: str, manifest_path: str) -> str:
    """Deja manifest.json en la rama principal: esa es la URL que lee el launcher."""
    with tempfile.TemporaryDirectory() as tmp:
        clone = os.path.join(tmp, "repo")
        res = run(["gh", "repo", "clone", repo, clone, "--", "--depth", "1"])
        if res.returncode != 0:
            sys.exit(f"No se pudo clonar el repo:\n{res.stderr}")

        shutil.copy(manifest_path, os.path.join(clone, "manifest.json"))
        run(["git", "-C", clone, "add", "manifest.json"])
        if run(["git", "-C", clone, "diff", "--cached", "--quiet"]).returncode == 0:
            print("  manifiesto: sin cambios que commitear")
        else:
            run(["git", "-C", clone, "commit", "-m", "Actualizar manifiesto del pack"])
            push = run(["git", "-C", clone, "push"])
            if push.returncode != 0:
                sys.exit(f"No se pudo hacer push del manifiesto:\n{push.stderr}")
            print("  manifiesto: publicado")

        branch = run(["git", "-C", clone, "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() or "main"
    return f"https://raw.githubusercontent.com/{repo}/{branch}/manifest.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="usuario/repositorio")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--payload", required=True, help="carpeta generada por build_manifest.py")
    ap.add_argument("--version", required=True)
    ap.add_argument("--public", action="store_true", help="crear el repo publico (por defecto privado)")
    args = ap.parse_args()

    need_gh()
    tag = f"pack-{args.version}"

    print("Publicando en GitHub")
    ensure_repo(args.repo, private=not args.public)
    seed_repo(args.repo)
    ensure_release(args.repo, tag)
    upload_assets(args.repo, tag, args.payload)
    manifest = rewrite_manifest(args.manifest, args.repo, tag)
    url = commit_manifest(args.repo, args.manifest)

    total = sum(f.get("size") or 0 for f in manifest["files"])
    print(f"\nListo. {len(manifest['files'])} ficheros, {total / 1048576:.1f} MB")
    print(f"URL del manifiesto para el launcher:\n  {url}")
    print("\nPegala en Ajustes del launcher, o ponla como COBBLEVERSE_MANIFEST en src/main/main.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
