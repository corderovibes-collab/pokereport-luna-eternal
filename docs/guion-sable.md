# Guion de voz — Sable del Eclipse

Guardián de la señal 2, la montaña. Seis líneas, mismo procedimiento que Grum.

```
evento/audio/voz/sable/sa_01.ogg
evento/audio/voz/sable/sa_02.ogg
...
```

El nombre de la carpeta importa: `build_rp.py` deriva la clave del sonido de la
ruta, así que `voz/sable/sa_01.ogg` se convierte en `voz.sable.sa_01`, que es lo
que llaman los botones del diálogo.

---

## Quién es

Grum dudaba. Sable no.

Y no por ser más malvado, sino por algo peor: **Luna no puede alcanzarlo**.
Donde Grum la custodió tres días y todavía sueña con ella, Sable la miró a los
ojos y no sintió nada. Por eso lo eligieron a él para apagarla — buscaron entre
cientos hasta dar con alguien inmune.

Su línea `sa_05` es la que mueve la historia: **el Eclipse no está guardando a
Luna, la está midiendo**. Quieren aprender a hacer lo que ella hace sin
necesitar que exista. Eso es lo que apunta al laboratorio de Vex.

---

## Las líneas

### sa_01 — al acercarse

```
No debieron subir tanto. Aquí arriba el aire engaña, y la caída es larga.
```

### sa_02 — «¿Otro del Eclipse?»

```
Sable. Y sé exactamente quiénes son: los que Grum dejó pasar. Yo no cometo ese error.
```

### sa_03 — «Vamos a bajarla de ahí.»

```
Grum les contó lo que sintió, ¿verdad? Los tres días. Que todavía sueña con ella. Yo la miré a los ojos y no sentí absolutamente nada.
```

### sa_04 — «¿Y eso te parece bien?»

```
Me parece útil. Por eso me eligieron a mí para apagarla. Buscaron entre cientos hasta encontrar a alguien a quien no pudiera alcanzar. Me encontraron.
```

### sa_05 — «¿Qué le están haciendo?»

```
No la estamos guardando. La estamos midiendo. Y cuando terminemos, sabremos hacer lo que ella hace sin necesidad de que ella exista.
```

### sa_06 — «Apártate.»

```
Ya hablé más de lo que debía. Weavile. Que no lleguen a la cumbre.
```

---

## Cómo debería sonar

Lo contrario de Grum en todo, y ahí está la gracia de que los dos sean hombres:
el contraste no lo da el género, lo da el carácter.

Grum es un barítono grave y gastado que habla despacio, con pausas largas.
**Sable es un tenor limpio, sin aspereza ninguna, y va rápido.** Nada de matón.
Treinta y pocos, dicción cuidada, frases cortadas y eficientes. No amenaza:
informa. No sube la voz en ninguna línea, ni siquiera en la última.

Si los pones seguidos tienen que sonar a dos especies distintas de persona.

La clave está en `sa_03` y `sa_04`: tiene que decir *«no sentí absolutamente
nada»* con la misma naturalidad con la que diría la hora. Si suena orgulloso o
cruel, se pierde — lo que inquieta es que para él sea un dato y no una postura.

### Para el campo «Personality» de Voicebox

```
A man in his early thirties, an Eclipse Team specialist. Light, clear, precise
voice with no roughness or gravel to it — nothing like a thug. Educated
diction, clipped and efficient, slightly quick. He never raises his volume and
never threatens; he informs. Polite the way a surgeon is polite. He states
appalling things as plain facts, without pride or cruelty, because to him they
are simply true. No warmth, but no malice either.
```

Lo que hace el trabajo es **«he states appalling things as plain facts»** y
**«nothing like a thug»** — eso último es lo que lo separa de Grum.

---

## Su equipo

Ya está definido en `evento/build_rct.py`:

| | |
|---|---|
| Sneasel | nivel 32 |
| **Weavile** | nivel 35 — su as, el que suelta en `sa_06` |

Weavile es **siniestro/hielo**, así que las misiones del PROTOCOLO LUNA (lucha,
bicho, hada) siguen sirviendo, y el hielo añade una debilidad más: acero, fuego,
roca y lucha.

## Cuando estén grabadas

```
python evento/build_rp.py
```

Y se publica el resourcepack. Falta también decidir las coordenadas del
campamento de la montaña, para el cristal de incursión y el marcador.
