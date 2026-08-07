# Guion de voz — Nix del Eclipse

Guardián de la señal 3, la costa. El último antes del laboratorio. Seis líneas,
mismo procedimiento que Grum y Sable.

```
evento/audio/voz/nix/ni_01.ogg
...
evento/audio/voz/nix/ni_06.ogg
```

La carpeta importa: `build_rp.py` deriva la clave del sonido de la ruta, así que
`voz/nix/ni_01.ogg` se convierte en `voz.nix.ni_01`.

---

## Quién es

Los tres guardianes son tres formas distintas de sostener lo mismo:

| | |
|---|---|
| **Grum** | culpa — cree que fue piedad, pero no duerme |
| **Sable** | certeza — Luna no puede alcanzarlo, y por eso lo eligieron |
| **Nix** | **miedo** — y no de los jugadores |

Nix está aterrado por lo que hay detrás de esa puerta, no por lo que tiene
delante. Pelea porque le toca, pero **quiere que ganen**. Su última línea es casi
un deseo de suerte.

Y su `ni_05` es la que planta el giro del Acto V sin gastarlo:

> **Luna pudo haberse ido el primer día. Nunca lo intentó.**

Eso no se explica aquí. Solo se deja caer, y el grupo llega al laboratorio con esa
pregunta encima.

---

## Las líneas

### ni_01 — al acercarse

```
Alto. El agua de aquí no es segura, y yo tampoco. Váyanse mientras puedan.
```

### ni_02 — «¿Y tú quién eres?»

```
Nix. El último antes del laboratorio. Grum les dio un sermón y Sable les dio una lección. Yo solo quiero que se den la vuelta.
```

### ni_03 — «No nos vamos a ir.»

```
Ya lo sé. Por eso llevo tres noches sin dormir. Y no es por ustedes: es por lo que hay al otro lado de esa puerta.
```

### ni_04 — «¿Qué hay al otro lado?»

```
La doctora Vex terminó de medirla. Dice que ya sabe cómo se hace, que ya no la necesita. Y lo peor de todo es que le creo.
```

### ni_05 — «¿Y por qué te da tanto miedo?»

```
No es eso. Es que hay algo que no le cuadra a nadie. Esa Pokémon pudo haberse ido el primer día. Pudo. Nunca lo intentó. Ni una sola vez. Se quedó.
```

### ni_06 — «Apártate.»

```
Ojalá alguno de ustedes averigüe por qué. Sharpedo, al agua. Que no lleguen a esa puerta.
```

---

## Cómo debería sonar

El tercero tiene que sonar distinto de los otros dos o la escena se repite.

| | Grum | Sable | **Nix** |
|---|---|---|---|
| Voz | Barítono grave, gastado | Tenor limpio, sin aspereza | **Más joven, algo agudo** |
| Ritmo | Lento, pausas largas | Rápido, cortado | **Atropellado, se corrige** |
| Volumen | Constante | Constante | **Sube y baja** |
| Actitud | Culpa | Certeza | **Miedo** |

Nix **habla de más**, que es lo que hace la gente asustada. No es un guardián
seguro de sí mismo: es alguien a quien le tocó la peor guardia y lo sabe.

Las dos que importan:

- **`ni_05`** es la única donde baja el ritmo. Lo dice despacio porque lleva
  semanas dándole vueltas. Deja silencio antes de *«Se quedó»*.
- **`ni_06`** empieza casi en un susurro (*«Ojalá alguno de ustedes averigüe por
  qué»*) y solo levanta la voz al llamar a Sharpedo. Está peleando contra su
  propia gana de dejarlos pasar.

### Para el campo «Personality» de Voicebox

```
A man in his mid-twenties, the last Eclipse Team guard before the laboratory.
Higher, lighter voice than the others, a little unsteady. He talks too much and
too fast, the way frightened people do — starting sentences over, adding one
more detail he shouldn't. His volume rises and falls without him controlling it.
He is not afraid of the people in front of him; he is afraid of what is behind
him. He almost wants them to win, and he is fighting that.
```

Lo que hace el trabajo es **«he is afraid of what is behind him»**.

---

## Su equipo

Ya definido en `evento/build_rct.py`:

| | |
|---|---|
| Carvanha | nivel 37 |
| **Sharpedo** | nivel 40 — su as, el que suelta en `ni_06` |

Sharpedo es **agua/siniestro**. Lucha, bicho y hada le siguen entrando por el
siniestro, y el agua añade planta y eléctrico. El PROTOCOLO LUNA vuelve a servir.

## Cuando estén grabadas

```
python evento/build_rp.py
```

Y se publica el resourcepack, como con Grum y Sable.

## Coordenadas

```
señal 3 (marcador)   1613, 63, 557
cristal de raid      pendiente — hace falta decidirlo
```
