#!/usr/bin/env python3
"""Sube ficheros al servidor Pterodactyl por lotes (multipart directo a wings).

El endpoint /files/pull del panel esta muy limitado (429), asi que subimos
directo al nodo con la URL firmada de /files/upload, que no pasa por Cloudflare.

Uso:  PTERO_KEY=... python scripts/upload_files.py <dir_local> <dir_remoto>
"""
import os, sys, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptero

BATCH_BYTES = 8 << 20   # ~8 MB por peticion (lotes mayores cortan la conexion)
TOKEN_TTL = 600         # refrescar la URL firmada cada 10 min
RETRIES = 4


class Uploader:
    def __init__(self):
        self._url = None
        self._ts = 0

    def url(self):
        if not self._url or time.time() - self._ts > TOKEN_TTL:
            self._url = ptero.upload_url()
            self._ts = time.time()
        return self._url

    def send(self, paths, remote_dir):
        boundary = "----ptero" + uuid.uuid4().hex
        parts = []
        for p in paths:
            name = os.path.basename(p)
            parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="files"; '
                f'filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
            )
            with open(p, "rb") as f:
                parts.append(f.read())
            parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        req = urllib.request.Request(
            f"{self.url()}&directory={urllib.parse.quote(remote_dir)}",
            data=body, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                     "User-Agent": ptero.UA},
        )
        with urllib.request.urlopen(req, timeout=900) as r:
            return r.status

    def send_retry(self, paths, remote_dir):
        """Reintenta el lote; si sigue fallando, sube fichero a fichero."""
        for attempt in range(RETRIES):
            try:
                return self.send(paths, remote_dir)
            except Exception as exc:
                self._url = None  # forzar token nuevo
                if attempt == RETRIES - 1:
                    if len(paths) == 1:
                        raise
                    print(f"    lote falla ({str(exc)[:60]}), subiendo 1 a 1")
                    for p in paths:
                        self.send_retry([p], remote_dir)
                    return 200
                time.sleep(2 * (attempt + 1))


import urllib.parse  # noqa: E402  (usado en send)


def upload_dir(local_dir, remote_dir, skip_existing=True):
    up = Uploader()
    try:
        have = {e["attributes"]["name"]: e["attributes"]["size"]
                for e in ptero.ls(remote_dir)["data"]}
    except RuntimeError:
        have = {}

    files = []
    for name in sorted(os.listdir(local_dir)):
        p = os.path.join(local_dir, name)
        if not os.path.isfile(p):
            continue
        if skip_existing and have.get(name, -1) == os.path.getsize(p):
            continue
        files.append(p)

    total = sum(os.path.getsize(p) for p in files)
    print(f"subiendo {len(files)} ficheros ({total/1048576:.1f} MB) -> {remote_dir}")

    batch, size, n = [], 0, 0
    t0 = time.time()
    for p in files:
        s = os.path.getsize(p)
        if batch and size + s > BATCH_BYTES:
            up.send_retry(batch, remote_dir)
            n += len(batch)
            print(f"  {n}/{len(files)}  ({time.time()-t0:.0f}s)")
            batch, size = [], 0
        batch.append(p)
        size += s
    if batch:
        up.send_retry(batch, remote_dir)
        n += len(batch)
        print(f"  {n}/{len(files)}  ({time.time()-t0:.0f}s)")

    have = {e["attributes"]["name"]: e["attributes"]["size"]
            for e in ptero.ls(remote_dir)["data"]}
    missing = [os.path.basename(p) for p in files
               if have.get(os.path.basename(p), -1) != os.path.getsize(p)]
    print(f"en {remote_dir}: {len(have)} ficheros")
    if missing:
        print("INCOMPLETOS:", missing)
        return 1
    print("OK: subida verificada por tamano")
    return 0


if __name__ == "__main__":
    sys.exit(upload_dir(sys.argv[1], sys.argv[2]))
