# Guía de operación

## Arrancar, parar y consola

Desde el panel https://control.tarohosting.com (servidor `2a0a48ff`), o por API:

```bash
export PTERO_KEY=ptlc_...

python scripts/ptero.py power start      # start | stop | restart | kill
python scripts/ptero.py resources        # estado, RAM, CPU, disco
python scripts/ptero.py command "say hola"
```

Para leer el log:

```bash
python -c "import sys;sys.path.insert(0,'scripts');import ptero;print(ptero.read('/logs/latest.log'))"
```

> El log rota cada día a las 00:00 UTC; los anteriores quedan en `/logs/` comprimidos.

## Copias de seguridad

**El plan tiene el límite de backups en 0**, así que el panel no deja crear ninguna. En un
servidor de Cobblemon, perder el mundo es perder todos los Pokémon y el progreso de todos.
Merece la pena resolverlo. Opciones, de mejor a peor:

1. **Pedir backups a TaroHosting** (ampliar el plan o que suban el límite). Es lo correcto.
2. **Descargar el mundo por SFTP** periódicamente a `s17.mia.us.tarohosting.lat:2022`
   con las credenciales del panel. La carpeta a salvar es `/world`.
3. Descargar `/world` por API cuando toque.

Hazlo **con el servidor parado** o justo después de un `save-all flush`, o te llevarás
región a medio escribir.

## Pregeneración de chunks

```bash
python scripts/pregen.py --status     # avance actual
python scripts/pregen.py              # arrancar / reanudar la secuencia completa
```

En la consola del servidor:

```
chunky pause          # pausar (por ejemplo si hay mucha gente conectada)
chunky continue       # reanudar donde iba
chunky cancel         # cancelar la tarea de la dimensión actual
```

Si el servidor se reinicia a mitad, Chunky **guarda el punto** y se reanuda con
`chunky continue`. No se pierde lo hecho.

## Actualizar el modpack

Cuando salga una versión nueva de Cobbleverse, **los jugadores y el servidor tienen que ir a la
misma**. El proceso, sin improvisar:

1. Parar el servidor y **guardar copia de `/world`** (ver arriba).
2. Regenerar el manifiesto para la versión nueva y comparar con el actual
   (`server-pack/mods-manifest.json`) para ver qué cambia.
3. Borrar `/mods` y subir el conjunto nuevo con `scripts/upload_files.py`.
4. Subir el `config/` y los `datapacks/` nuevos del pack.
5. Arrancar y revisar el log antes de dejar entrar a nadie.

**Ojo con dos cosas** que se pierden si reinstalas el egg desde el panel:

- `server.jar` (el puente de memoria) lo sobrescribe el instalador de Fabric.
  Hay que volver a subir [`server-pack/launcher/`](../server-pack/launcher/) y renombrar.
- `jvm-args.txt` y `server.properties` conviene comprobarlos.

## Diagnóstico

| Síntoma | Qué mirar |
|---|---|
| Va a tirones | `spark tps`, luego `spark profiler --timeout 60` |
| Se cae solo sin error | Memoria. `spark heapsummary`. Bajar `-Xmx` en `jvm-args.txt` |
| Un jugador no entra | Que tenga **Cobbleverse 1.7.42** exacto, ni más nueva ni más vieja |
| "Flying is not enabled" | `allow-flight=true` en `server.properties` (ya está puesto) |
| Lag al explorar | Zona sin pregenerar. Ampliar radio con Chunky |

## Comandos útiles en el juego

```
/spark tps
/datapack list
/chunky status
/forceload query
```

## Cosas que conviene decidir más adelante

- **Whitelist**: ahora está desactivada, cualquiera con la IP puede entrar.
  Se activa con `whitelist on` + `whitelist add <jugador>`.
- **Ser OP**: `python scripts/ptero.py command "op TuNombre"`.
- **`max-players`**: puesto en 40 como estimación razonable para 16 GB y 3 núcleos.
  Con gente real dentro, mira `spark tps` y ajusta.
- **Datapacks opcionales** (Hoenn, Johto, Sinnoh, Terralith) subidos en `/datapacks/extra/`
  sin activar. Terralith cambia la generación del mundo: **activarlo con el mundo ya
  pregenerado deja una costura visible** entre lo viejo y lo nuevo. Si lo quieres, hay que
  decidirlo antes de generar más mundo.
