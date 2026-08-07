# Acto I — «La llamada». Prueba y pulido

Un solo acto. Lo dejamos perfecto y luego pasamos al siguiente.

**Tiempo de prueba: 15 minutos.**

---

## Qué tiene que sentir el jugador

Están todos reunidos. La pantalla se funde a negro. La cámara despega del suelo,
sube sobre el grupo y barre el paisaje mientras una voz de anciano empieza a contar algo
que no debería existir. La cámara vuelve, la pantalla corta a blanco, y ahí está el
Profesor Oak, delante, esperando.

Si al terminar no se te ha puesto la piel de gallina, no está bien todavía.

---

## Preparación · 3 min

### 1 · Abre el launcher

Deja que termine de descargar. Baja tres mods nuevos (KantoNPCs, Blabber, Cutscene API)
y el pack de voces.

**Si el launcher da error → PARA y dímelo.** Sin eso no hay nada que probar.

### 2 · Entra y hazte admin

```
/function evento:admin/soy_admin
```

Se abre el panel de botones. A partir de aquí no tecleas más.

### 3 · Monta la zona

Ponte en un sitio **llano y despejado**, con **50 bloques libres alrededor** y cielo
abierto — la cámara sube hasta 42 bloques y se aleja 34.

Pulsa **[ MONTAR ZONA ]**.

---

## Prueba 1 — La cinemática · lo más importante

Pulsa **[ APERTURA ]**.

Deberían pasar **20 segundos** así:

| Segundo | Cámara | Voz |
|---|---|---|
| 0 | Funde desde negro | — |
| 0-4 | Se despega del suelo, muy despacio | «Entrenadores. Escúchenme bien...» |
| 4-9 | Sube y se abre al cielo | «...no está en ninguna Pokédex.» |
| 9-15 | **Gran barrido lateral sobre el paisaje** | «Hace tres semanas detecté una lectura...» |
| 15-20 | Cae y frena delante del grupo | «...pensé que era un fallo del equipo.» |
| 20 | Corta a blanco | — |

### Qué mirar, en orden de importancia

**1. ¿Se oye la voz de Oak?**
Es lo primero. Si solo hay imagen, el resourcepack no se activó.

**2. ¿La cámara se mueve suave o da tirones?**

**3. ¿Atraviesa terreno?** Si pasa por dentro de una montaña o del suelo, hay que subir el
recorrido.

**4. ¿El barrido enseña algo bonito?** Es el plano que vende el evento.

**5. ¿Termina mirando al grupo** o se queda mirando al cielo / al suelo?

**6. ¿Los 20 segundos se hacen largos o cortos?**

---

## Prueba 2 — El diálogo de Oak

Pulsa **[ OAK ]** en el panel. Se abre a todos a la vez.

**Qué mirar:**

- ¿Sale una pantalla de diálogo **grande, tipo JRPG**, o una cajita sosa?
- ¿Hay un **retrato** a la izquierda? ¿Se ve bien o sale un monigote raro?
- ¿El retrato **te sigue con la mirada**?
- ¿Las opciones se leen bien?

Prueba la rama: elige **«¿Le miró a usted? ¿Cómo?»**. Debe contarte lo de la mirada y
volver al hilo.

---

## Prueba 3 — El rastreador

Pulsa **[ RASTREADORES ]**. Comprueba que la brújula se llama «Rastreador de energía»,
tiene descripción en gris y **brilla** como encantada.

---

## Prueba 4 — El acto entero

Pulsa **[ REINICIAR ]** y luego **[ INICIAR ]**.

Eso es lo que verá la gente el día del evento: rótulo de acto, cinemática con voz, y a
partir de ahí ya están dentro de la historia.

**¿Fluye o se nota que son piezas pegadas?**

---

## Qué contarme

Con esto ajusto. Cada síntoma tiene arreglo concreto:

| Lo que ves | Lo que hago |
|---|---|
| No se oye nada | Reviso la activación del resourcepack |
| La cámara atraviesa el suelo o una montaña | Subo los puntos de control del Bézier |
| Gira demasiado rápido / marea | Cambio la curva de suavizado |
| Se queda mirando mal al final | Ajusto la rotación de llegada |
| Demasiado lenta o rápida | Cambio la duración, y si hace falta se regraba |
| El barrido no enseña nada | Reescribo el tramo 3 |
| El retrato sale feo | Pruebo otra entidad, o texturas propias |
| La pantalla de diálogo es sosa | Le meto arte: marco, sello del Eclipse, fondo |
| El texto no convence | Lo reescribimos |

**Dime lo que sea, aunque sea «no sé, no me gusta».** Con eso trabajo.

---

## Lo que NO probamos hoy

Nada de señales, misiones, laboratorio ni final. Ese es el error que veníamos cometiendo.

**Acto I hasta que esté bien. Luego el II.**
