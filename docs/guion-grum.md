# Guion de voz — Grum del Eclipse

Seis líneas. Mismo procedimiento que con Oak: se generan en Voicebox y se dejan
en `evento/audio/voz/grum/` con el nombre exacto del identificador.

```
evento/audio/voz/grum/g1_01.ogg
evento/audio/voz/grum/g1_02.ogg
...
```

El nombre de la carpeta importa: `build_rp.py` deriva la clave del sonido de la
ruta, así que `voz/grum/g1_01.ogg` se convierte en `voz.grum.g1_01`, que es lo
que llaman los botones del diálogo. Si la carpeta se llama distinto, no suena.

## Cómo debería sonar

Grum no es un matón de dibujos animados. Es alguien que lleva demasiado tiempo
haciendo guardia y que **cree de verdad** lo que dice. Voz grave, cansada, sin
prisa. Solo se le rompe un poco en `g1_04`, que es donde admite que lo que vio
le sigue quitando el sueño.

Sube el tono únicamente en la última.

---

## Las líneas

### g1_01 — al acercarse

```
Alto ahí. Este bosque está cerrado. Den la vuelta por donde vinieron.
```

### g1_02 — «¿Y tú quién eres?»

```
Grum. Del Equipo Eclipse. Y ustedes son los del profesor, ¿verdad? Ese viejo nunca aprende.
```

### g1_03 — «Venimos por Luna.»

```
No vienen por ella. Vienen porque él les dijo que vinieran. No es lo mismo, aunque ahora no lo vean.
```

### g1_04 — «¿Qué le hicieron?»

```
¿Saben lo que hace esa criatura? Se te mete dentro. Te hace querer cosas que no elegiste. Yo la custodié tres días. Tres. Y todavía sueño con ella.
```

### g1_05 — «Eso no es cierto.»

```
Nosotros no la robamos. La apagamos. Hay una diferencia, y algún día me lo van a agradecer.
```

### g1_06 — «Apártate.»

```
Pero ustedes no lo van a entender. Nunca entienden. Mightyena, enséñales lo que hay al otro lado del bosque.
```

---

## Por qué dice lo que dice

`g1_04` y `g1_05` son las que hacen el trabajo. Grum plantea que un amor
incondicional que te alcanza **sin haberlo elegido** es una forma de control, y
que apagar a Luna fue un acto de piedad, no un robo.

Es un argumento lo bastante razonable como para dejar dudas. Eso es
deliberado: prepara el giro del Acto V en vez de gastarlo, y de paso resuelve
lo que quedó apuntado en `contexto-para-gemini.md` — que los villanos del evento
eran planos.

Nadie tiene que darle la razón. Basta con que el grupo salga de ahí sin estar
del todo seguro.

## Una vez grabadas

```
python evento/build_rp.py
```

Y se sube el resourcepack al pack del launcher, igual que con las de Oak.
