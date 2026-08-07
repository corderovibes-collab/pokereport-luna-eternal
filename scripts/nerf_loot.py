#!/usr/bin/env python3
"""Rebaja el loot de Pokemon en los cofres de estructuras tempranas.

COBBLEVERSE-Loot-DP inyecta sus tablas en 53 cofres vanilla. Tal cual viene, un
dungeon corriente puede soltar hasta 9 items de Cobblemon, ultra balls y objetos
equipables competitivos incluidos, asi que la progresion se salta sola.

Que hace este script:
  - Las 16 estructuras tardias (ciudad antigua, bastiones, end city, fortalezas,
    mansion, recompensas ominosas) se quedan EXACTAMENTE igual: son el premio por
    haber avanzado.
  - En las demas, los pools que reparten objetos potentes tiran la mitad de veces.
  - Dentro de esos pools, cada entrada potente ademas tiene que pasar un dado:
    30% las premium (balls especiales, vitaminas, rare candy, objetos equipables)
    y 60% las intermedias (piedras evolutivas, TMs, gemas, mentas, fosiles).
  - Los pools que solo dan balls normales, bayas, curacion o comida NO se tocan:
    son el bucle basico del juego y sin eso no hay con que capturar.

Uso:  python scripts/nerf_loot.py <zip original> <zip de salida>

El zip de salida se sube a /datapacks con el MISMO nombre que el original (lo carga
GlobalPacks) y se aplica con /reload. El original vive en
server-pack/datapacks/COBBLEVERSE-Loot-DP-v11.ORIGINAL.zip para poder revertir.
"""
import json
import math
import sys
import zipfile

TARDIAS = {
    "ancient_city", "ancient_city_ice_box", "bastion_bridge", "bastion_hoglin_stable",
    "bastion_other", "bastion_treasure", "end_city_treasure", "nether_bridge",
    "stronghold_corridor", "stronghold_crossing", "stronghold_library", "woodland_mansion",
    "shipwreck_treasure", "reward_ominous_common", "reward_ominous_rare", "reward_ominous_unique",
}
PREMIUM = {"special_pokeball", "special_items", "rare_items", "vitamin",
           "ancient_pokeball", "ancient_special_pokeball"}
MEDIO = {"evolutionary", "boost_items", "gems", "tms", "mints", "fossil"}


def ref(entry):
    """Nombre corto de la tabla a la que apunta una entrada, o '' si es un item suelto."""
    if not entry["type"].endswith("loot_table"):
        return ""
    return str(entry.get("value") or entry.get("name", "")).split("/")[-1]


def ajustar(tabla):
    """Devuelve True si toco algo."""
    tocado = False
    for pool in tabla.get("pools", []):
        refs = [r for r in (ref(e) for e in pool.get("entries", [])) if r]
        if not any(r in PREMIUM or r in MEDIO for r in refs):
            continue
        rolls = pool.get("rolls")
        if isinstance(rolls, dict) and "max" in rolls:
            rolls["min"] = 0.0
            rolls["max"] = float(max(1, math.ceil(rolls["max"] / 2)))
        elif isinstance(rolls, (int, float)):
            pool["rolls"] = float(max(1, math.floor(rolls / 2)))
        for e in pool.get("entries", []):
            chance = {True: 0.30}.get(ref(e) in PREMIUM) or (0.60 if ref(e) in MEDIO else None)
            ya = any(c.get("condition", "").endswith("random_chance") for c in e.get("conditions", []))
            if chance and not ya:
                e.setdefault("conditions", []).append(
                    {"condition": "minecraft:random_chance", "chance": chance})
        tocado = True
    return tocado


def main(origen, destino):
    src = zipfile.ZipFile(origen)
    n = 0
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            nombre = item.filename.split("/")[-1].removesuffix(".json")
            es_cofre = ("minecraft/loot_table/chests" in item.filename
                        and item.filename.endswith(".json"))
            if es_cofre and nombre not in TARDIAS:
                tabla = json.loads(data)
                if ajustar(tabla):
                    data = json.dumps(tabla, indent=2).encode()
                    n += 1
            out.writestr(item, data)
    print(f"{n} tablas de cofre ajustadas -> {destino}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
