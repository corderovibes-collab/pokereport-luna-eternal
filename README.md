# PokeReport: Luna Eternal

Servidor privado de Minecraft con **COBBLEVERSE 1.7.42** sobre **Minecraft 1.21.1 + Fabric**,
su propio launcher, y un evento narrativo con voces, incursiones y misiones.

```
s17.mia.us.tarohosting.lat:33445
```

---

## Qué hay aquí

| Carpeta | Qué es |
|---|---|
| [`evento/`](evento/) | Los generadores del evento. Nada se escribe a mano: todo se regenera |
| [`launcher/`](launcher/) | El launcher, en Electron. Windows y macOS |
| [`scripts/`](scripts/) | Herramientas del servidor: API de Pterodactyl, pregeneración, despliegue |
| [`addon-luna/`](addon-luna/) | Luna, la Pokémon del evento: modelo, texturas y datos de Cobblemon |
| [`server-pack/`](server-pack/) | Configuración del servidor |
| [`client-pack/`](client-pack/) | El manifiesto que consume el launcher |
| [`docs/`](docs/) | El porqué de cada decisión. **Empieza aquí** |

En la raíz viven además `manifest.json`, `assets/` y `skins/`: son los ficheros
que el launcher descarga en caliente. **No moverlos** — hay clientes apuntando a
esas URL.

---

## El evento — *El Rastro de Luna*

Para hasta doce personas, unas tres horas.

```
Acto I     La llamada        el Profesor Oak pide ayuda
Acto II    Las señales       tres guardianes, tres incursiones de grupo
Acto III   El cifrado        cinco pruebas que descifran el código
Acto IV    El laboratorio    la Doctora Vex
Acto V     El reencuentro    Luna
```

Con **50 líneas de voz** grabadas, incursiones cooperativas de doce jugadores y
un filtro de acceso por misiones de FTB Quests.

Todo se regenera desde los scripts:

```
python evento/build_dp.py       el motor: 128 funciones
python evento/build_raid.py     los jefes de incursión
python evento/build_quests.py   el capítulo de FTB Quests
python evento/build_rp.py       el resourcepack de voces
```

Estado y decisiones pendientes: [`docs/estado-actual.md`](docs/estado-actual.md).

---

## El launcher

Descarga Java, el modpack y los assets, y lanza el juego. No hace falta que
nadie instale nada por su cuenta.

- **Windows** — instalador `.exe`
- **macOS** — `.dmg` para Intel y para Apple Silicon. Ver [`docs/launcher-mac.md`](docs/launcher-mac.md)

Se compila solo con GitHub Actions:

```
git tag launcher-v1.2.3 && git push --tags
```

---

## Secretos

Ninguna clave entra al repositorio. `scripts/.env.example` es la plantilla:
se copia a `scripts/.env` y se rellena en local.
