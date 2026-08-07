#!/usr/bin/env python3
"""Cliente minimo de la API de Pterodactyl (panel TaroHosting) para el servidor Cobbleverse.

La API key se lee de la variable de entorno PTERO_KEY (ver scripts/.env.example).
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

PANEL = os.environ.get("PTERO_PANEL", "https://control.tarohosting.com")
KEY = os.environ.get("PTERO_KEY", "")
SERVER = os.environ.get("PTERO_SERVER", "2a0a48ff")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

if not KEY:
    sys.exit("Falta PTERO_KEY en el entorno")


def call(method, path, body=None, raw=False, base=None):
    url = f"{PANEL}{base or f'/api/client/servers/{SERVER}'}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        # Cloudflare (error 1010) rechaza el UA por defecto de urllib.
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = r.read()
    except urllib.error.HTTPError as e:
        payload = e.read()
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {payload[:600].decode('utf-8','replace')}")
    if raw:
        return payload
    return json.loads(payload) if payload else {}


# ---- helpers de ficheros -------------------------------------------------
def ls(directory="/"):
    return call("GET", f"/files/list?directory={urllib.parse.quote(directory)}")


def read(path):
    return call("GET", f"/files/contents?file={urllib.parse.quote(path)}", raw=True).decode("utf-8", "replace")


def write(path, content):
    url = f"{PANEL}/api/client/servers/{SERVER}/files/write?file={urllib.parse.quote(path)}"
    req = urllib.request.Request(url, data=content.encode("utf-8"), method="POST", headers={
        "Authorization": f"Bearer {KEY}", "Accept": "application/json",
        "Content-Type": "application/octet-stream", "User-Agent": UA,
    })
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.status


def pull(url, directory="/", filename=None, foreground=False):
    body = {"url": url, "directory": directory, "use_header": False, "foreground": foreground}
    if filename:
        body["filename"] = filename
    return call("POST", "/files/pull", body)


def mkdir(root, name):
    return call("POST", "/files/create-folder", {"root": root, "name": name})


def decompress(root, file):
    return call("POST", "/files/decompress", {"root": root, "file": file})


def delete(root, files):
    return call("POST", "/files/delete", {"root": root, "files": files})


def rename(root, frm, to):
    return call("PUT", "/files/rename", {"root": root, "files": [{"from": frm, "to": to}]})


def upload_url():
    return call("GET", "/files/upload")["attributes"]["url"]


# ---- power / estado ------------------------------------------------------
def power(signal):
    return call("POST", "/power", {"signal": signal})


def resources():
    return call("GET", "/resources")["attributes"]


def command(cmd):
    return call("POST", "/command", {"command": cmd})


def startup():
    return call("GET", "/startup")


def set_var(key, value):
    return call("PUT", "/startup/variable", {"key": key, "value": value})


def set_image(image):
    return call("PUT", "/settings/docker-image", {"docker_image": image})


def reinstall():
    return call("POST", "/settings/reinstall")


if __name__ == "__main__":
    fn = sys.argv[1]
    args = sys.argv[2:]
    try:
        out = globals()[fn](*args)
    except RuntimeError as e:
        sys.exit(str(e)[:400])
    print(json.dumps(out, indent=1) if not isinstance(out, (str, int)) else out)
