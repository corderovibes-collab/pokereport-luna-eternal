# Cobblemon: Vocalized — versión en español

Fork del mod [cobblemon-vocalized](https://gitlab.com/cable-mc/cobblemon-vocalized) adaptado al
servidor. Permite dar órdenes por voz en español: usar movimientos, sacar al Pokémon, guardarlo y
cambiar de Pokémon.

Licencia original **MPL-2.0**, que obliga a mantener bajo la misma licencia los ficheros
modificados. Todos los cambios están en ficheros que ya eran MPL, así que el fork hereda la
licencia sin más trámite.

## Por qué había que tocar el mod

El mod publicado en Modrinth **no puede funcionar en español tal cual**, por tres motivos
independientes:

1. **El modelo de reconocimiento es inglés y está fijado en el código.**
   `Vocalized.MODEL` era la constante `"en_us"`. El motor (Vosk) sólo entiende el idioma del
   modelo que se le carga.
2. **No existía "sacar al Pokémon".** El único controlador fuera de combate era
   `RecallVoiceController`, y su condición de activación era
   `pokemon.state is SentOutState` — es decir, sólo se encendía cuando el Pokémon **ya estaba
   fuera**. Servía para guardarlo, nunca para sacarlo.
3. **No existía "cambiar de Pokémon"**, ni dentro ni fuera del combate.

Además el jar publicado está compilado contra Cobblemon 1.6.0, mientras que el servidor usa
**Cobblemon 1.7.3+1.21.1**. Compilar desde el código fuente también corrige ese desfase.

## Qué se cambió

| Fichero | Cambio |
|---|---|
| `Vocalized.kt` | Modelo por defecto `es_es`; normalización que respeta tildes y ñ |
| `VocalizedVoice.kt` | El modelo se resuelve en ejecución: ajuste manual → idioma del juego → por defecto |
| `ClientConfig.kt` | Nueva opción `voiceModel` para forzar un modelo concreto |
| `VocalizedPhrases.kt` *(nuevo)* | Frases de activación traducibles, separadas por `\|` |
| `PartyVoiceController.kt` *(nuevo)* | Sacar, guardar y cambiar de Pokémon fuera del combate |
| `BattleVoiceController.kt` | Cambio de Pokémon en combate, incluido el relevo forzado |
| `NumberWordConverter.kt` | Añadido el formato numérico español |
| `lang/es_es.json` *(nuevo)* | Traducción e inventario de frases |
| `build.gradle.kts` (×3) | Se empaqueta sólo el modelo `es_es` |
| `controller/recall/` | Eliminado, absorbido por `PartyVoiceController` |

### Sobre las tildes

La normalización original era `[^a-zA-Z0-9 ]`, que borra cualquier carácter no ASCII. Conviene
entender bien qué hacía, porque es fácil sacar la conclusión equivocada: como se aplicaba **igual
al texto reconocido y a la frase candidata**, "Puño Fuego" quedaba en `pu o fuego` en los dos
lados y aún casaba. No rompía el reconocimiento, lo degradaba: partía palabras en trozos y
ensuciaba el umbral de coincidencia por mayoría. Ahora el patrón es Unicode y "puño" sigue siendo
una sola palabra.

### Por qué un solo controlador fuera del combate

`VoiceController` abre **una captura de micrófono por cada controlador activo**. Los dos originales
nunca coincidían (uno exige combate, el otro exige no-combate). Separar "sacar", "guardar" y
"cambiar" en tres controladores habría abierto tres capturas simultáneas del mismo micrófono, así
que los tres comandos viven en `PartyVoiceController`.

## Órdenes disponibles

Se definen en `lang/es_es.json` y se pueden editar sin recompilar (varias alternativas por orden,
separadas por `|`).

**Fuera del combate**
- Sacar: *adelante*, *yo te elijo*, *a luchar*, *sal ya*, *te elijo a ti*
- Guardar: *vuelve*, *regresa*, *ven aquí*, *retírate*, *descansa*
- Cambiar: decir el nombre del Pokémon, o *cambia a \<nombre\>*

**En combate**
- Movimientos: el nombre del movimiento tal y como lo muestra Cobblemon en español
- Cambiar: *cambia a \<nombre\>* o sólo el nombre
- Rendirse: *me rindo*, *abandono*, *me retiro*

Los nombres de los movimientos no hay que traducirlos a mano: el mod se los pide a Cobblemon ya
traducidos (`translated.displayName.string`). Si el cliente está en español, las frases salen en
español solas.

## Requisito para los jugadores

**El cliente tiene que estar en español.** El jar sólo incluye el modelo `es_es` (cada modelo pesa
unos 60 MB e incluir los tres triplicaría la descarga). Si el juego está en otro idioma, Cobblemon
dará los nombres de movimiento en ese idioma y el reconocedor español nunca podrá casarlos; queda
avisado en el log.

## Los ficheros del modelo van en minúscula

Dentro del jar el modelo se llama `gr.fst`, `hclr.fst` y `readme`, **en minúscula**, aunque Vosk
los distribuye como `Gr.fst`, `HCLr.fst` y `README`. No es un capricho: las rutas de recursos de
Minecraft sólo admiten `[a-z0-9/._-]`, así que un fichero con mayúsculas **no aparece siquiera en
el listado de recursos**. Por eso `VocalizedVoice` los renombra al extraerlos:

```kotlin
"hclr.fst", "hcl_r.fst", "hcl-r.fst" -> "HCLr.fst"
"gr.fst" -> "Gr.fst"
```

Si algún día se cambia de modelo hay que renombrarlos a minúscula al meterlos. El fallo es
traicionero porque no da error: el mod simplemente se queda sin voz.

## Gramática restringida (opcional)

Vosk admite `Recognizer(model, sampleRate, grammar)` para limitar el reconocimiento a una lista
cerrada de frases en lugar de transcribir español abierto. Está implementado: la tubería ya conoce
las frases posibles en cada instante (los movimientos del Pokémon activo, el equipo y las órdenes)
y se las pasa al reconocedor, más `[unk]` para que pueda decir "no era ninguna".

**Viene apagado** (`restrictVocabulary = false`). Vosk sólo acepta en la gramática palabras que ya
estén en el léxico del modelo, y los nombres propios de Pokémon ("Granbull", "Ribombee") casi
seguro no lo están: activarlo podría dejar mudo justo el cambio de Pokémon por nombre. Se enciende
en la configuración del cliente, sin cambiar de jar, y si el modelo rechaza la gramática se vuelve
solo al reconocimiento libre.

Merece la pena medirlo: con vocabulario cerrado el acierto sube bastante, y el modelo pequeño
declara un WER del 16 % en habla limpia.

## Pendiente

- Probar el reconocimiento con voces reales y decidir si compensa `restrictVocabulary`.
- Comprobar qué nombres compuestos ("Hidrobomba", "Lanzallamas") reconoce el modelo pequeño.
