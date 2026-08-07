# Servidor Cobbleverse — Paquete Ender Dragon

Servidor de Minecraft con el modpack **COBBLEVERSE 1.7.42** sobre **Minecraft 1.21.1 + Fabric**,
alojado en TaroHosting (panel Pterodactyl).

## Datos de conexión

| | |
|---|---|
| **IP para jugadores** | `s17.mia.us.tarohosting.lat:33445` |
| Modo | **Offline** (`online-mode=false`) con EasyAuth |
| **Chat de voz** | `s17.mia.us.tarohosting.lat:33595` (Simple Voice Chat, proximidad 64 bloques) |
| Pack (público) | https://github.com/corderovibes-collab/pokereport-luna-eternal |
| Panel | https://control.tarohosting.com |
| ID del servidor | `2a0a48ff` |
| Nodo | `s17.mia.us.tarohosting.lat` |
| SFTP | `s17.mia.us.tarohosting.lat:2022` |

Recursos del plan: **16 GB RAM · 300% CPU (3 núcleos) · 180 GB disco**.

## Qué versión hay que instalar en el cliente

Los jugadores necesitan **COBBLEVERSE 1.7.42** exactamente (Minecraft 1.21.1, Fabric loader 0.18.4),
desde el [Modrinth oficial del pack](https://modrinth.com/modpack/cobbleverse).
Si un jugador tiene otra versión del pack, no podrá entrar.

## Estado actual

- Servidor **arrancado y funcionando**: arranque completo en 16 s, 249 mods cargados, cero errores reales.
- 103 mods server-side + los 5 datapacks de Cobbleverse activos y verificados.
- 7 mods de optimización añadidos sobre lo que ya traía el pack.
- Pregeneración en curso: radio 5000 overworld, 2000 nether, 1500 end.

Medido con spark **mientras pregenera** a 35 chunks/s:

```
TPS (5s, 10s, 1m, 5m, 15m):  20.0, 20.0, 20.0, 20.0, 20.0
Duración de tick (min/med/95%/max): 0.1 / 0.2 / 0.4 / 3.7 ms   (el presupuesto son 50 ms)
RAM: 13,2 GB de 16 GB    CPU: 71% de 300%
```

## Estructura del repo

```
docs/          informes: auditoría, decisiones, operación, rendimiento y guía del cliente
audit/         datos crudos de la auditoría (JSON) para poder rehacerla
scripts/       cliente de la API del panel + despliegue + pregeneración
server-pack/   lo que está desplegado en el servidor (manifiesto, configs, launcher)
client-pack/   lo que instalan los jugadores: el .mrpack exacto + extras de optimización
launcher/      PokeReport Launcher (Electron) + herramientas de publicación
cloud-gaming/  notebook de Colab para jugar desde la nube + diagnóstico de viabilidad
```

## Documentación

- [docs/azure.md](docs/azure.md) — **activar el login con Minecraft original** (registro de Azure, 5 min, gratis).
- [docs/menu-arte.md](docs/menu-arte.md) — **menú de inicio Luna Eternal**: medidas del arte y prompts para generarlo.
- [docs/launcher.md](docs/launcher.md) — **el launcher propio**: qué hace, cómo publicar actualizaciones y cómo compilarlo.
- [docs/cliente.md](docs/cliente.md) — instalación manual del modpack (alternativa al launcher), RAM y ajustes.
- [docs/cloud-gaming.md](docs/cloud-gaming.md) — **jugar desde la nube**: viabilidad real de Colab-Cloud-Gaming y alternativas. La parte ejecutable está en [cloud-gaming/](cloud-gaming/).
- [docs/auditoria.md](docs/auditoria.md) — qué trae el modpack, qué se instaló y qué se descartó, con el porqué.
- [docs/rendimiento.md](docs/rendimiento.md) — optimización, capacidad para 12 jugadores y cómo seguir ajustando.
- [docs/operacion.md](docs/operacion.md) — cómo arrancar, parar, actualizar, diagnosticar y hacer copias.

## Reparto cliente / servidor

Sodium y todo lo de render va en el **cliente** (ya viene dentro del modpack); lo que optimiza
lógica y chunks va en el **servidor**. Detalle completo en [docs/cliente.md](docs/cliente.md).

| | Mods |
|---|---|
| Cliente | 123 mods + 30 resourcepacks + Complementary Unbound |
| Servidor | 103 mods (sin nada de render) |

## Uso de los scripts

```bash
export PTERO_KEY=ptlc_...          # la API key del panel (ver scripts/.env.example)

python scripts/ptero.py resources          # estado y consumo
python scripts/ptero.py ls /mods           # listar ficheros
python scripts/pregen.py --status          # avance de la pregeneración
python scripts/deploy_mods.py --verify-only   # comprobar que están los 103 mods
```

> La API key **no** está guardada en el repo. Ver [scripts/.env.example](scripts/.env.example).
