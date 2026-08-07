#!/usr/bin/env python3
"""Pregeneracion de chunks con Chunky, encadenando dimensiones de una en una.

Ejecutarlas en paralelo repartiria los mismos 3 nucleos entre las tres dimensiones
sin ganar tiempo total, y multiplica la presion sobre el heap.

Sobrevive a reinicios del servidor: guarda el progreso en docs/pregen-state.json y,
cuando el servidor vuelve, reanuda la MISMA dimension con "chunky continue" en vez
de saltar a la siguiente.

Uso:  PTERO_KEY=... python scripts/pregen.py            # arrancar / reanudar
      PTERO_KEY=... python scripts/pregen.py --status   # solo consultar
"""
import json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptero

# El nether va primero porque es el que quedo a medias tras el reinicio del servidor.
TASKS = [
    ("minecraft:the_nether", 2000),
    ("minecraft:overworld", 5000),
    ("minecraft:the_end", 1500),
]
DISK_LIMIT_MB = 150_000     # margen de seguridad sobre los 180 GB del plan
POLL = 60
WAIT_FOR_SERVER = 30 * 60   # cuanto esperar como maximo a que el servidor vuelva

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "docs", "pregen-progress.log")
STATE = os.path.join(ROOT, "docs", "pregen-state.json")


def say(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1)


def tail(n=4000):
    try:
        return ptero.read("/logs/latest.log").splitlines()[-n:]
    except RuntimeError:
        return []


def chunky_lines(world, lines=None):
    lines = tail() if lines is None else lines
    return [l for l in lines if "[Chunky]" in l and world in l]


def finished_count(world, lines=None):
    return sum(1 for l in chunky_lines(world, lines) if "Task finished" in l)


def send(*cmds):
    for c in cmds:
        ptero.command(c)
        time.sleep(1.5)


def wait_for_server(world):
    """Espera a que el servidor vuelva y reanuda la tarea. False si no vuelve."""
    say(f"{world}: servidor no disponible, esperando...")
    deadline = time.time() + WAIT_FOR_SERVER
    while time.time() < deadline:
        time.sleep(POLL)
        try:
            if ptero.resources()["current_state"] == "running":
                time.sleep(30)          # dejar que termine de cargar el mundo
                send(f"chunky world {world}", "chunky continue")
                say(f"{world}: servidor de vuelta, tarea reanudada")
                return True
        except RuntimeError:
            pass
    say(f"{world}: el servidor no volvio en {WAIT_FOR_SERVER // 60} min, abandono")
    return False


def run(world, radius):
    st = load_state()
    if st.get(world) == "done":
        say(f"{world}: ya completado, saltando")
        return True

    if st.get(world) == "in_progress":
        say(f"{world}: reanudando tarea en curso")
        send(f"chunky world {world}", "chunky continue")
    else:
        say(f"{world}: lanzando pregeneracion radio {radius}")
        send(f"chunky world {world}", "chunky center 0 0", "chunky shape square",
             f"chunky radius {radius}", "chunky start")
        st[world] = "in_progress"
        save_state(st)

    # Solo cuentan los "Task finished" que aparezcan a partir de ahora.
    base = finished_count(world)

    while True:
        time.sleep(POLL)
        try:
            r = ptero.resources()
        except RuntimeError:
            if not wait_for_server(world):
                return False
            continue

        if r["current_state"] != "running":
            if not wait_for_server(world):
                return False
            continue

        disk = r["resources"]["disk_bytes"] / 1048576
        if disk > DISK_LIMIT_MB:
            send("chunky pause")
            say(f"PARADA DE SEGURIDAD: disco en {disk:.0f} MB")
            return False

        lines = tail()
        if finished_count(world, lines) > base:
            st = load_state()
            st[world] = "done"
            save_state(st)
            say(f"{world}: TERMINADO")
            return True

        recent = chunky_lines(world, lines)
        m = re.search(r"Processed: ([\d.]+) chunks \(([\d.]+)%\).*?ETA: (\S+), Rate: ([\d.]+) cps",
                      recent[-1] if recent else "")
        if m:
            say(f"{world}: {m.group(2)}% ({m.group(1)} chunks) ETA {m.group(3)} a {m.group(4)} cps "
                f"| disco {disk:.0f} MB | RAM {r['resources']['memory_bytes']/1048576:.0f} MB")


def main():
    if "--status" in sys.argv:
        st = load_state()
        for w, _ in TASKS:
            recent = chunky_lines(w)
            say(f"{w}: [{st.get(w, 'pendiente')}] {recent[-1][-110:] if recent else 'sin datos'}")
        return 0

    send("chunky quiet 60", "chunky worldborder off")
    for world, radius in TASKS:
        if not run(world, radius):
            say("secuencia interrumpida; relanza este script para continuar")
            return 1
    say("PREGENERACION COMPLETA en las 3 dimensiones")
    return 0


if __name__ == "__main__":
    sys.exit(main())
