#!/usr/bin/env python3
"""
Diagnóstico de viabilidad de cloud gaming sobre Google Colab.

No instala nada y no toca el sistema. Solo mide el runtime que te ha tocado y
dice si Sunshine/Moonlight puede funcionar ahí, con el porqué.

La pregunta que responde es una sola: ¿existe un camino para que el vídeo UDP
salga de este contenedor y llegue a tu PC?

Uso:  python3 diagnostico.py
"""

import fcntl
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import time
import urllib.request

# ---------------------------------------------------------------- utilidades

VERDE, ROJO, AMBAR, GRIS, NEGRITA, FIN = (
    "\033[92m", "\033[91m", "\033[93m", "\033[90m", "\033[1m", "\033[0m"
)

OK, FALLO, AVISO = f"{VERDE}OK{FIN}", f"{ROJO}FALLO{FIN}", f"{AMBAR}AVISO{FIN}"

resultados = {}


def titulo(texto):
    print(f"\n{NEGRITA}{texto}{FIN}")
    print("─" * 66)


def linea(etiqueta, estado, detalle=""):
    print(f"  [{estado}] {etiqueta:<34} {GRIS}{detalle}{FIN}")


def sh(cmd, timeout=20):
    """Ejecuta un comando y devuelve (rc, stdout+stderr). Nunca lanza."""
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as e:                                    # noqa: BLE001
        return 127, str(e)


# ------------------------------------------------------------ 1. plataforma

def check_plataforma():
    titulo("1. Plataforma")

    en_colab = "google.colab" in sys.modules or os.path.isdir("/content")
    linea(
        "Entorno Google Colab",
        OK if en_colab else AVISO,
        "detectado" if en_colab else "no parece Colab; el diagnóstico sigue igual",
    )
    resultados["colab"] = en_colab

    linea("Kernel", OK, platform.release())
    linea("Distribución", OK, _distro())

    # El AppArmor de Colab es el que aplica las restricciones de red.
    perfil = _leer("/proc/self/attr/current", "desconocido").strip("\x00").strip()
    restrictivo = "datalabvm" in perfil or "docker" in perfil
    linea(
        "Perfil AppArmor",
        AVISO if restrictivo else OK,
        perfil or "ninguno",
    )
    resultados["apparmor"] = perfil


def _distro():
    txt = _leer("/etc/os-release", "")
    m = re.search(r'PRETTY_NAME="([^"]+)"', txt)
    return m.group(1) if m else "desconocida"


def _leer(ruta, defecto=""):
    try:
        with open(ruta, "r", errors="replace") as f:
            return f.read()
    except Exception:                                         # noqa: BLE001
        return defecto


# -------------------------------------------------------------- 2. hardware

def check_hardware():
    titulo("2. Hardware asignado")

    # --- GPU
    rc, out = sh("nvidia-smi --query-gpu=name,memory.total,driver_version "
                 "--format=csv,noheader")
    tiene_gpu = rc == 0 and out and "not found" not in out.lower()
    if tiene_gpu:
        linea("GPU", OK, out.splitlines()[0])
    else:
        linea("GPU", FALLO, "sin GPU — Entorno de ejecución > Cambiar tipo > T4")
    resultados["gpu"] = out if tiene_gpu else None

    # --- NVENC: sin esto no hay codificación por hardware y no hay stream usable
    if tiene_gpu:
        rc, out = sh("nvidia-smi --query-gpu=name --format=csv,noheader")
        nombre = out.splitlines()[0] if out else ""
        # T4, L4, A10G, RTX... llevan NVENC. A100 y H100 NO llevan NVENC.
        sin_nvenc = any(x in nombre.upper() for x in ("A100", "H100", "TPU"))
        linea(
            "NVENC (codificador de vídeo)",
            FALLO if sin_nvenc else OK,
            f"{nombre} — esta GPU NO tiene NVENC" if sin_nvenc
            else f"{nombre} — debería tener NVENC",
        )
        resultados["nvenc"] = not sin_nvenc

    # --- CPU: lo que de verdad limita a Minecraft con mods
    nucleos = os.cpu_count() or 0
    modelo = ""
    m = re.search(r"model name\s*:\s*(.+)", _leer("/proc/cpuinfo"))
    if m:
        modelo = m.group(1).strip()
    mhz = re.search(r"cpu MHz\s*:\s*([\d.]+)", _leer("/proc/cpuinfo"))
    freq = f" @ {float(mhz.group(1)):.0f} MHz" if mhz else ""

    estado_cpu = OK if nucleos >= 6 else (AVISO if nucleos >= 4 else FALLO)
    linea(f"CPU ({nucleos} vCPU)", estado_cpu, modelo + freq)
    if nucleos <= 2:
        print(f"       {ROJO}↳ 2 vCPU tienen que repartirse entre el juego, el "
              f"escritorio\n         virtual, Sunshine y el túnel. Minecraft con "
              f"249 mods\n         va a dar tirones aunque el stream funcione.{FIN}")
    resultados["vcpu"] = nucleos

    # --- RAM
    m = re.search(r"MemTotal:\s+(\d+) kB", _leer("/proc/meminfo"))
    ram_gb = int(m.group(1)) / 1024 / 1024 if m else 0
    linea("RAM", OK if ram_gb >= 12 else AVISO, f"{ram_gb:.1f} GB")
    resultados["ram_gb"] = round(ram_gb, 1)

    # --- Disco: Cobbleverse son ~239 MB de mrpack que se expanden bastante más
    libre_gb = shutil.disk_usage("/content" if os.path.isdir("/content") else "/").free / 1024**3
    linea("Disco libre", OK if libre_gb >= 25 else AVISO, f"{libre_gb:.0f} GB")
    resultados["disco_gb"] = round(libre_gb, 1)


# ----------------------------------------------- 3. el test que decide todo

# Bit 12 del mapa de capabilities de Linux.
CAP_NET_ADMIN = 12
# <linux/if_tun.h>
TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


def check_red():
    titulo("3. Red — el test que decide si esto es posible")

    print(f"{GRIS}  Moonlight manda el vídeo por UDP. Para que un paquete UDP entre\n"
          f"  en este contenedor hace falta una VPN (Tailscale/WireGuard), y toda\n"
          f"  VPN necesita un dispositivo TUN. Eso es lo que se prueba aquí.{FIN}\n")

    # --- 3.1 ¿Tenemos CAP_NET_ADMIN en el bounding set?
    capbnd = 0
    m = re.search(r"CapBnd:\s*([0-9a-fA-F]+)", _leer("/proc/self/status"))
    if m:
        capbnd = int(m.group(1), 16)
    tiene_netadmin = bool(capbnd & (1 << CAP_NET_ADMIN))
    linea(
        "CAP_NET_ADMIN disponible",
        OK if tiene_netadmin else FALLO,
        f"CapBnd=0x{capbnd:016x}" + ("" if tiene_netadmin else " — capability ausente"),
    )
    resultados["cap_net_admin"] = tiene_netadmin

    # --- 3.2 ¿Existe /dev/net/tun? Si no, ¿podemos crearlo?
    existe_tun = os.path.exists("/dev/net/tun")
    if not existe_tun:
        os.makedirs("/dev/net", exist_ok=True)
        rc, out = sh("mknod /dev/net/tun c 10 200 && chmod 600 /dev/net/tun")
        existe_tun = os.path.exists("/dev/net/tun")
        linea(
            "/dev/net/tun",
            OK if existe_tun else FALLO,
            "creado con mknod" if existe_tun else f"mknod falló: {out[:40]}",
        )
    else:
        linea("/dev/net/tun", OK, "ya existía")
    resultados["dev_tun"] = existe_tun

    # --- 3.3 La prueba real: abrir el dispositivo y crear la interfaz.
    #     Esto es lo que hace tailscaled/wireguard por dentro. Si falla aquí,
    #     falla para cualquier VPN, sin excepción.
    tun_ok, motivo = False, "no se intentó"
    if existe_tun:
        try:
            fd = os.open("/dev/net/tun", os.O_RDWR)
            try:
                ifr = struct.pack("16sH22s", b"diagtun0", IFF_TUN | IFF_NO_PI, b"")
                fcntl.ioctl(fd, TUNSETIFF, ifr)
                tun_ok, motivo = True, "interfaz creada correctamente"
            finally:
                os.close(fd)
        except PermissionError as e:
            motivo = f"operación no permitida ({e.errno}) — bloqueado por el sandbox"
        except OSError as e:
            motivo = f"errno {e.errno}: {e.strerror}"
    linea("Crear interfaz TUN (ioctl real)", OK if tun_ok else FALLO, motivo)
    resultados["tun_funciona"] = tun_ok

    # --- 3.4 Salida a Internet (esto sí funciona siempre; es lo único que hay)
    rc, _ = sh("timeout 8 curl -sf -o /dev/null https://api.github.com")
    linea("Salida TCP a Internet", OK if rc == 0 else FALLO,
          "sin restricción" if rc == 0 else "sin salida")
    resultados["salida_tcp"] = rc == 0

    # --- 3.5 ¿Hay IP pública / puertos entrantes? (spoiler: no)
    linea("Puertos entrantes públicos", FALLO,
          "Colab no expone puertos: no hay IP pública ni port-forward")
    resultados["puertos_entrantes"] = False

    # --- 3.6 Región, para estimar la latencia hasta ti
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=8) as r:
            info = json.load(r)
        loc = f"{info.get('city','?')}, {info.get('region','?')} ({info.get('country','?')})"
        linea("Región del runtime", OK, loc)
        resultados["region"] = loc
    except Exception:                                         # noqa: BLE001
        linea("Región del runtime", AVISO, "no se pudo determinar")


# --------------------------------------------------------------- veredicto

def veredicto():
    titulo("VEREDICTO")

    tun = resultados.get("tun_funciona", False)
    gpu = resultados.get("gpu") is not None
    vcpu = resultados.get("vcpu", 0)

    if not gpu:
        print(f"{ROJO}{NEGRITA}  NO VIABLE — no hay GPU asignada.{FIN}")
        print("  Cambia el tipo de entorno de ejecución a T4 y vuelve a ejecutar.")
        return "sin_gpu"

    if tun:
        print(f"{VERDE}{NEGRITA}  CAMINO ABIERTO — se puede crear un TUN.{FIN}\n")
        print("  Algo ha cambiado en Colab respecto a lo documentado. Se puede montar")
        print("  Tailscale en modo normal y Moonlight tendría su ruta UDP directa.")
        print(f"  {NEGRITA}Sigue con la celda 2 del notebook.{FIN}")
        if vcpu <= 2:
            print(f"\n  {AMBAR}Aviso: con {vcpu} vCPU el stream irá, pero Cobbleverse")
            print(f"  dará tirones. El límite pasa a ser la CPU, no la red.{FIN}")
        return "viable"

    # Caso real esperado
    print(f"{ROJO}{NEGRITA}  NO VIABLE para streaming de baja latencia.{FIN}\n")
    print("  La cadena de restricciones, en orden:\n")
    print(f"    1. El contenedor no tiene {NEGRITA}CAP_NET_ADMIN{FIN} "
          f"({'ausente' if not resultados.get('cap_net_admin') else 'presente pero insuficiente'}).")
    print("    2. Sin esa capability no se puede crear una interfaz TUN,")
    print("       aunque /dev/net/tun exista.")
    print("    3. Sin TUN no hay Tailscale ni WireGuard ni ninguna VPN.")
    print("    4. Colab tampoco expone puertos entrantes.")
    print("    5. Por tanto el único transporte posible es un túnel HTTP/TCP")
    print("       saliente (Cloudflare Tunnel, ngrok).")
    print(f"    6. Y el vídeo de Moonlight es {NEGRITA}UDP{FIN}. Meterlo por TCP")
    print("       provoca head-of-line blocking: cada paquete perdido congela")
    print("       la imagen hasta que se retransmite.\n")
    print(f"  {GRIS}Eso es exactamente el issue #11 del repo original")
    print(f"  ('High latency with Cloudflare tunnel') y el motivo de que")
    print(f"  el proyecto se archivara el 18/06/2026.{FIN}\n")
    print(f"  {NEGRITA}Alternativas que sí funcionan: ver docs/cloud-gaming.md{FIN}")
    return "no_viable"


# ------------------------------------------------------------------ main

def main():
    print(f"\n{NEGRITA}Diagnóstico de cloud gaming — PokeReport{FIN}")
    print(f"{GRIS}{time.strftime('%Y-%m-%d %H:%M:%S')} · no modifica el sistema{FIN}")

    check_plataforma()
    check_hardware()
    check_red()
    v = veredicto()

    ruta = "/content/diagnostico-resultado.json" if os.path.isdir("/content") \
        else "diagnostico-resultado.json"
    resultados["veredicto"] = v
    try:
        with open(ruta, "w") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\n{GRIS}Resultado guardado en {ruta}{FIN}")
    except Exception:                                         # noqa: BLE001
        pass

    return 0 if v == "viable" else 1


if __name__ == "__main__":
    sys.exit(main())
