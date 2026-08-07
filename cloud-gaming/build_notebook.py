#!/usr/bin/env python3
"""
Genera PokeReport-Colab.ipynb.

El notebook se construye desde aquí en vez de editarse a mano para que
`diagnostico.py` viva en un fichero normal, revisable y con resaltado de
sintaxis, y no duplicado dentro del JSON del notebook.

Uso:  python build_notebook.py
"""

import json
import pathlib

AQUI = pathlib.Path(__file__).parent
DIAGNOSTICO = (AQUI / "diagnostico.py").read_text(encoding="utf-8")


def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": texto.strip().split("\n")}


def code(texto, titulo=None):
    meta = {}
    if titulo:
        meta["cellView"] = "form"
    return {
        "cell_type": "code",
        "metadata": meta,
        "execution_count": None,
        "outputs": [],
        "source": texto.strip("\n").split("\n"),
    }


# --------------------------------------------------------------------------
CELDAS = []

CELDAS.append(md(r"""
# Cobbleverse en la nube — versión transparente

Reconstrucción de [kmille36/Colab-Cloud-Gaming](https://github.com/kmille36/Colab-Cloud-Gaming)
(archivado el 18/06/2026) adaptada a Minecraft en vez de Steam.

**Por qué está reescrito y no se usa el original:** los dos ficheros ejecutables del repo
(`ColabSteam` y `colab-moonweb`) son binarios ELF generados con **shc**, que cifra un script
bash con RC4 dentro de un ELF. No se puede leer qué hacen. El notebook original te pide
montar tu Google Drive *antes* de ejecutarlos como root. Aquí todo el código está a la vista.

---

### Antes de empezar, dos cosas

1. **Esto va contra el ToS de Colab.** El FAQ oficial prohíbe *"using a remote desktop or SSH"*
   y avisa de que esas sesiones *"may be terminated at any time without warning"*.
   **Usa una cuenta de Google desechable**, no la tuya. No montes tu Drive personal.
2. **Ejecuta primero la celda 2 (Diagnóstico).** Tarda 30 segundos y te dice si tu runtime
   concreto puede hacer esto, antes de que inviertas una hora. Si dice `NO VIABLE`,
   las celdas siguientes no van a funcionar y el porqué está explicado en la salida.
"""))

CELDAS.append(md("## 1 · Mantener viva la sesión"))

# Ojo: `%%html` tiene que ser la primera línea real de la celda. Colab elimina
# `#@title` antes de ejecutar, pero NO los comentarios normales: si se cuela uno
# entre medias, el magic deja de detectarse y la celda peta.
CELDAS.append(code(r"""
#@title Reproduce este audio para que Colab no te desconecte { display-mode: "form" }
%%html
<b>Dale al play y deja la pestaña visible.</b><br/>
<audio autoplay loop controls
       src="https://github.com/anars/blank-audio/raw/master/10-minutes-of-silence.mp3"></audio>
"""))

CELDAS.append(md("""
## 2 · Diagnóstico — ejecuta esto primero

No instala nada ni modifica el sistema. Mide el runtime que te ha tocado y responde a una
sola pregunta: **¿puede salir el vídeo UDP de este contenedor hasta tu PC?**
"""))

CELDAS.append(code("%%writefile diagnostico.py\n" + DIAGNOSTICO))
CELDAS.append(code("!python3 diagnostico.py"))

CELDAS.append(md(r"""
### Cómo leer el resultado

| Veredicto | Qué significa | Qué hacer |
|---|---|---|
| `CAMINO ABIERTO` | Se pudo crear una interfaz TUN. Colab ha cambiado respecto a lo documentado. | Sigue en la celda 3 |
| `NO VIABLE` | Sin `CAP_NET_ADMIN` no hay TUN → no hay VPN → no hay ruta UDP. | Ver `docs/cloud-gaming.md` |
| `sin GPU` | No te han asignado T4. | *Entorno de ejecución → Cambiar tipo → T4*, y repite |

**Por qué `NO VIABLE` no tiene arreglo desde aquí:** Moonlight manda el vídeo por UDP.
Colab no expone puertos entrantes, así que la única forma de recibir UDP sería una VPN,
y toda VPN necesita un dispositivo TUN que el sandbox de Colab no deja crear. Lo único que
queda es un túnel HTTP/TCP saliente, y meter vídeo en tiempo real por TCP causa
*head-of-line blocking*: cada paquete perdido congela la imagen hasta que se retransmite.

Eso es literalmente el issue **#11 del repo original** (*"High latency with Cloudflare tunnel"*),
y la razón de que se archivara.
"""))

CELDAS.append(md("""
---
## 3 · Entorno gráfico con aceleración por GPU

Solo si el diagnóstico dijo `CAMINO ABIERTO`.

El montaje es: **Xvfb** da el display, **VirtualGL con backend EGL** hace que OpenGL se
renderice en la T4 (sin necesidad de un servidor X con driver NVIDIA, que en un contenedor
no se puede levantar), y **Sunshine** captura ese display y lo codifica con **NVENC**.

Sin VirtualGL, Minecraft renderizaría por software (llvmpipe) sobre 2 vCPU: la T4 solo
estaría codificando vídeo y el juego iría a pocos FPS.
"""))

CELDAS.append(code(r"""
%%bash
set -euo pipefail

echo "▶ Paquetes base…"
apt-get update -qq
# Sin `|| true`: si esto falla hay que verlo, no seguir a ciegas.
# libnvidia-encode no se instala aquí a propósito: lo aporta el driver que Colab
# ya trae, y pinear una versión que no case con el driver rompe NVENC.
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    xvfb x11-utils xauth openbox \
    libegl1 libgl1 libglx-mesa0 mesa-utils \
    pulseaudio pulseaudio-utils

echo "▶ VirtualGL (render en GPU vía EGL)…"
VGL=3.1.1
curl -fsSL -o /tmp/vgl.deb \
  "https://github.com/VirtualGL/virtualgl/releases/download/${VGL}/virtualgl_${VGL}_amd64.deb"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/vgl.deb

echo "▶ Sunshine…"
SUN=$(curl -fsSL https://api.github.com/repos/LizardByte/Sunshine/releases/latest \
      | grep -o 'https://[^"]*ubuntu-22.04-amd64.deb' | head -1)
curl -fsSL -o /tmp/sunshine.deb "$SUN"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb

echo "▶ Arrancando display virtual…"
export DISPLAY=:0
Xvfb :0 -screen 0 1920x1080x24 +extension GLX +extension RANDR &
sleep 3
openbox --sm-disable &
pulseaudio --start --exit-idle-time=-1 2>/dev/null || true

echo
echo "▶ Comprobación: ¿quién está renderizando OpenGL?"
DISPLAY=:0 vglrun -d egl glxinfo 2>/dev/null | grep -E "OpenGL renderer" \
  || echo "  ⚠ VirtualGL no pudo usar EGL — el render caería en llvmpipe (CPU)"
"""))

CELDAS.append(md("""
Si la última línea dice **`OpenGL renderer: ... Tesla T4 ...`**, el render va por GPU.
Si dice **`llvmpipe`**, está renderizando por CPU y Cobbleverse será injugable
independientemente del stream.
"""))

CELDAS.append(md(r"""
---
## 4 · Minecraft + Cobbleverse 1.7.42

Tu launcher (`PokeReport Launcher`) **no sirve aquí**: `launcher/electron-builder.yml` solo
compila target `nsis` para Windows x64 y esto es Linux. Se usa **Prism Launcher**, que es la
*Opción B* de tu propio `docs/cliente.md` y acepta el mismo `.mrpack`.

**Importante:** tiene que ser el `.mrpack` **exacto 1.7.42**, o el servidor te rechaza.
Sube `client-pack/COBBLEVERSE 1.7.42.mrpack` a la raíz de tu Drive (el de la cuenta
desechable) y ejecuta la celda.
"""))

CELDAS.append(code(r"""
from google.colab import drive
drive.mount('/content/drive')
"""))

CELDAS.append(code(r"""
%%bash
set -euo pipefail
export DISPLAY=:0

MRPACK="/content/drive/MyDrive/COBBLEVERSE 1.7.42.mrpack"
if [ ! -f "$MRPACK" ]; then
  echo "✖ No encuentro el modpack en la raíz de tu Drive."
  echo "  Sube: client-pack/COBBLEVERSE 1.7.42.mrpack"
  exit 1
fi

echo "▶ Java 21…"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq openjdk-21-jre

echo "▶ Prism Launcher…"
curl -fsSL -o /tmp/prism.AppImage \
  "$(curl -fsSL https://api.github.com/repos/PrismLauncher/PrismLauncher/releases/latest \
     | grep -o 'https://[^\"]*x86_64.AppImage' | head -1)"
chmod +x /tmp/prism.AppImage
/tmp/prism.AppImage --appimage-extract >/dev/null 2>&1
mv squashfs-root /opt/prism

echo "▶ Importando el modpack (tarda: son 249 mods)…"
/opt/prism/AppRun --import "$MRPACK" || true

echo
echo "✔ Listo. Ajustes según tu docs/cliente.md:"
echo "    · 6 GB de RAM al juego (no más)"
echo "    · distancia de renderizado 8"
echo "    · SIN shaders — Complementary duplica el coste de encoder también"
"""))

CELDAS.append(md(r"""
---
## 5 · Túnel

Esta celda **falla a propósito** si el diagnóstico dijo `NO VIABLE`, en vez de dejarte montar
un túnel TCP que da 300 ms y parece que funciona hasta que intentas jugar.
"""))

CELDAS.append(code(r"""
import json, subprocess, sys

try:
    r = json.load(open("/content/diagnostico-resultado.json"))
except FileNotFoundError:
    sys.exit("✖ Ejecuta primero la celda 2 (Diagnóstico).")

if not r.get("tun_funciona"):
    print("✖ El diagnóstico dijo NO VIABLE: no se puede crear un TUN en este runtime.")
    print()
    print("  Montar aquí un túnel Cloudflare/ngrok te daría un stream por TCP, que es")
    print("  exactamente lo que hacía el repo original y por lo que se archivó.")
    print("  No merece la pena. Alternativas reales en docs/cloud-gaming.md")
    sys.exit(1)

print("✔ TUN disponible — instalando Tailscale…")
subprocess.run("curl -fsSL https://tailscale.com/install.sh | sh", shell=True, check=True)
subprocess.run("tailscaled --state=/var/lib/tailscale/tailscaled.state &",
               shell=True, check=True)
print()
print("Ahora ejecuta en una celda nueva:  !tailscale up")
print("Te dará una URL para autenticar. Después:  !tailscale ip -4")
"""))

CELDAS.append(md(r"""
---
## 6 · Emparejar Moonlight

1. `!tailscale ip -4` → te da la IP del runtime (ej. `100.x.y.z`).
2. Instala Tailscale y **Moonlight** en tu PC, con la misma cuenta.
3. En Moonlight, *Add PC* → esa IP. Te enseña un **PIN de 4 dígitos**.
4. Ejecuta la celda de abajo con ese PIN.

Es el mismo flujo que `moon-pair.sh` del repo original, que hacía dos llamadas a la API de
Sunshine: una para fijar las credenciales y otra para aceptar el PIN. Aquí la contraseña no
se queda en `admin:admin`.
"""))

CELDAS.append(code(r"""
PIN = ""  #@param {type:"string"}
CLAVE_SUNSHINE = ""  #@param {type:"string"}

import subprocess, sys
if not PIN or not CLAVE_SUNSHINE:
    sys.exit("Rellena el PIN de Moonlight y una contraseña para Sunshine.")

subprocess.run([
    "curl", "-u", "admin:admin", "-X", "POST", "-k",
    "https://localhost:47990/api/password",
    "-H", "Content-Type: application/json",
    "-d", ('{"currentUsername":"admin","currentPassword":"admin",'
           f'"newUsername":"admin","newPassword":"{CLAVE_SUNSHINE}",'
           f'"confirmNewPassword":"{CLAVE_SUNSHINE}"}}'),
], check=False)

subprocess.run([
    "curl", "-u", f"admin:{CLAVE_SUNSHINE}", "-X", "POST", "-k",
    "https://localhost:47990/api/pin",
    "-H", "Content-Type: application/json",
    "-d", f'{{"pin":"{PIN}","name":"moonlight"}}',
], check=False)
print("\n✔ Emparejado. Lanza el juego desde Moonlight.")
""", titulo=True))

CELDAS.append(md(r"""
---
## 7 · Persistencia

Colab **borra el disco entero** al cerrar la sesión. Sin copia, cada vez repites la descarga
de los 249 mods y la compilación de shaders.

Esta celda comprime la instancia de Prism a tu Drive. Restaurar tarda bastante menos que
reinstalar, pero sigue siendo varios minutos por sesión: es una limitación de la plataforma,
no algo que se pueda optimizar.
"""))

CELDAS.append(code(r"""
#@title Copia / restauración { display-mode: "form" }
ACCION = "backup"  #@param ["backup", "restaurar"]

import subprocess, os
DESTINO = "/content/drive/MyDrive/cobbleverse-instancia.tar.zst"
ORIGEN  = os.path.expanduser("~/.local/share/PrismLauncher")

if ACCION == "backup":
    subprocess.run(f'tar --zstd -cf "{DESTINO}" -C "{os.path.dirname(ORIGEN)}" '
                   f'"{os.path.basename(ORIGEN)}"', shell=True, check=True)
    print(f"✔ Guardado en {DESTINO}")
else:
    if not os.path.exists(DESTINO):
        print("✖ No hay copia previa en el Drive.")
    else:
        os.makedirs(os.path.dirname(ORIGEN), exist_ok=True)
        subprocess.run(f'tar --zstd -xf "{DESTINO}" -C "{os.path.dirname(ORIGEN)}"',
                       shell=True, check=True)
        print("✔ Restaurado.")
"""))

CELDAS.append(md(r"""
---
## Límites que no desaparecen aunque todo lo anterior funcione

| Límite | Valor |
|---|---|
| Tiempo de juego | ~4 h, y luego espera de 24 h |
| CPU | 2 vCPU compartidos — es el cuello de botella de Minecraft con mods |
| Persistencia | Ninguna; solo copias manuales a Drive |
| Riesgo | Suspensión de la cuenta de Google usada |

Comparativa completa con las opciones de pago en [`docs/cloud-gaming.md`](../docs/cloud-gaming.md).
"""))

# --------------------------------------------------------------------------

NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
    },
    "cells": CELDAS,
}

destino = AQUI / "PokeReport-Colab.ipynb"
destino.write_text(json.dumps(NOTEBOOK, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Escrito {destino}  ({len(CELDAS)} celdas)")
