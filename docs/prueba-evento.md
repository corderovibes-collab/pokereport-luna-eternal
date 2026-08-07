# Cómo probarlo todo, paso a paso

Guion de prueba para recorrer el evento entero sin tener los escenarios construidos.
Unos 30-40 minutos. Ve marcando lo que falle.

---

## Antes de entrar

### 1 · Abre el launcher

Se te van a descargar cosas nuevas. Déjalo terminar.

| Qué baja | Cuánto |
|---|---|
| Voces del Profesor Oak | 2,2 MB |
| Tom's Simple Storage 2.4.1 | 1,9 MB |
| Client Sort | 0,3 MB |
| Radar sin Pokémon | pequeño |

**Si el launcher da error**, avísame: significa que algo del manifiesto está mal.

### 2 · Entra al servidor

Solo tú estás en la lista blanca. Si quieres meter a alguien más para probar:

```
/whitelist add <nombre>
```

---

## Comprobaciones rápidas (2 minutos)

Antes del evento, verifica los cambios sueltos:

| # | Qué mirar | Debería pasar |
|---|---|---|
| 1 | El **minimapa** | **No** salen Pokémon, ni sus iconos ni sus nombres |
| 2 | El **mapa grande** | Lo mismo |
| 3 | Abre un **cofre** | Hay un botón de ordenar arriba a la derecha |
| 4 | Busca en REI «Storage Terminal» | Aparece la receta de Tom's |

Si en el minimapa **siguen saliendo** Pokémon, dímelo: quedaría la tercera vía, que es
forzar la configuración desde el cliente.

---

## El evento

### 3 · Hazte admin

```
/function evento:admin/soy_admin
```

Te sale el panel con botones. **Todo lo demás es hacer clic.** Para reabrirlo:
`/function evento:admin/panel`

### 4 · Comprueba el estado

Pulsa **[ COMPROBAR ]**. Debería decirte que no hay NPCs ni balizas todavía, y que el
evento está parado. Eso es lo correcto antes de empezar.

### 5 · Monta la zona de ensayo

Ponte en un sitio **llano y despejado** — hacen falta unos 20 bloques a la redonda.
Pulsa **[ MONTAR ZONA ]**.

Aparecen seis NPCs a tu alrededor:

```
                Vex          Guardia
                    \        /
    baliza           \      /          baliza
                       Oak
   Nix  ───────────── (tú) ───────────── Grum
                      Sable
    baliza         baliza        baliza
```

**Verifica:** que están los seis, con sus nombres encima.

---

## Prueba 1 — La escena con voz

Pulsa **[ INICIAR ]**.

Debería pasar esto, sin tocar nada, durante **64 segundos**:

| Segundo | Qué |
|---|---|
| 0 | Título «ACTO I · LA LLAMADA» |
| 0-8 | Oak: «Entrenadores. Escúchenme bien.» **con voz** |
| 8-20 | «Hace tres semanas detecté una lectura de energía...» |
| 20-33 | «Era una Pokémon. Y me miró como si me conociera.» |
| 33-41 | «El Equipo Eclipse se la llevó.» |
| 41-51 | «Necesito que me ayuden a traerla de vuelta.» |
| 51-64 | «Tomen el rastreador. Apunta hacia ella.» |

**Lo que hay que verificar:**

- ¿**Se oye** la voz? Si solo ves subtítulos, el resourcepack no se activó.
- ¿El subtítulo **cambia a la vez** que la voz, o va desfasado?
- ¿Los subtítulos se leen bien, o pasan muy rápido?

Si algo va desfasado, dime cuál y ajusto los tiempos.

---

## Prueba 2 — El rastreador

Pulsa **[ RASTREADORES ]**. Te da una brújula llamada «Rastreador de energía», con
descripción y brillo de encantamiento.

---

## Prueba 3 — Hablar con Oak

Clic derecho sobre el Profesor Oak.

**Verifica:**
- Se abre la interfaz de diálogo de Cobblemon, con su cara
- El texto avanza por páginas
- En la tercera página salen **dos opciones**: «Cuente conmigo» y «Qué es el Equipo Eclipse?»
- Elige la segunda: debe contarte lo del Eclipse y volver al hilo

---

## Prueba 4 — Un combate

Clic derecho sobre **Grum del Eclipse**.

**Verifica:**
- Saluda y ofrece dos opciones
- «Acepto el combate» arranca el combate
- Su equipo es **Poochyena nivel 27 y Mightyena nivel 30** — exactamente esos
- Al terminar, tu equipo sale **curado**

Repite con Vex si quieres ver el jefe: seis Pokémon, del 47 al 55, con Hydreigon.

---

## Prueba 5 — El motor de actos

Con el evento en el Acto I:

| Paso | Botón | Debe pasar |
|---|---|---|
| 1 | **[ SALTAR ACTO ]** | Título «ACTO II · LAS SEÑALES» |
| 2 | **[ GUARDIAN CAIDO ]** | «SEÑAL LOCALIZADA», contador 1 de 3 |
| 3 | **[ GUARDIAN CAIDO ]** | 2 de 3 |
| 4 | **[ GUARDIAN CAIDO ]** | 3 de 3 y **salta solo** al Acto III |

Ese último salto automático es la prueba de que el motor funciona.

---

## Prueba 6 — Las balizas

Ya estás en el Acto III, que es cuando cuentan las misiones.

Camina hasta una de las cinco balizas (están a unos 20 bloques). Al acercarte a **cinco
bloques**:

- Suena una campana
- Sale «Baliza encontrada 1 de 5» en la barra de acción

Recórrelas las cinco. A la quinta se completa la misión y suma un dígito.

**Ojo:** las balizas son invisibles. Están en las cinco direcciones del dibujo de arriba.

---

## Prueba 7 — Las misiones de Cobblemon

Sigues en el Acto III. Prueba las que puedas:

| Misión | Cómo dispararla |
|---|---|
| Cazador nocturno | Captura 3 Pokémon **siniestros** |
| Corazón de hielo | Captura 1 de **hielo** |
| Veterano | Gana 5 combates |
| Coleccionista | Sube 3 Pokémon a nivel 40 |
| Pescador | Pesca 10 Pokémon |

Con **cuatro misiones** completadas pasa solo al Acto IV. Si te da pereza, usa
**[ SALTAR ACTO ]**.

---

## Prueba 8 — El final

| Paso | Botón | Debe pasar |
|---|---|---|
| 1 | **[ VEX CAIDA ]** | Pasa al Acto V |
| 2 | **[ REVELACION ]** | Seis líneas con voz: las lecturas raras, «ella se dejó encontrar», Arceus, la Diosa del Amor Incondicional, «Alejandro, acércate tú» |
| 3 | **[ LUNA CAPTURADA ]** | Fuegos artificiales y cierre |

La revelación son unos **70 segundos**. Es el momento más importante del evento: escúchalo
entero y dime si funciona emocionalmente o si hay que retocar el texto.

---

## Al terminar

```
[ DESMONTAR ]     recoge los NPCs y balizas del ensayo
[ REINICIAR ]     marcadores a cero
```

---

## Qué contarme

Apunta lo que chirríe. Lo que más me sirve:

1. **¿Se oye la voz?** Es lo primero. Sin eso, lo demás da igual.
2. **¿Los tiempos cuadran?** ¿Subtítulos desfasados, muy rápidos, muy lentos?
3. **¿Los equipos de los guardianes están bien de nivel?** ¿Demasiado fáciles, demasiado duros?
4. **¿Los textos suenan bien en latino?** Se me pueden haber colado giros de España.
5. **¿El panel se entiende** o hay botones confusos?
6. **¿Siguen saliendo Pokémon en el minimapa?**

Con eso afino la fase 8 y queda listo para el día.
