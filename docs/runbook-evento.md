# Guion del día — «El Rastro de Luna»

Lo que hace el admin, en orden, el día del evento. Pensado para leerse con prisa.

**Todo se hace desde un panel de botones.** Escribe esto una vez y no vuelvas a teclear:

```
/function evento:admin/soy_admin
```

Te marca como admin, empiezas a recibir los avisos internos y te abre el panel. Para
volver a abrirlo: `/function evento:admin/panel`.

---

## Probar sin tener los escenarios

Mientras se construye el mapa se puede recorrer el evento entero en veinte bloques.
Ponte donde quieras y pulsa **[ MONTAR ZONA ]**:

```
                    Vex          Guardia
                         \      /
        baliza            \    /            baliza
                           Oak
       Nix  ────────────  (tú)  ──────────  Grum
                          Sable
        baliza          baliza      baliza
```

Planta los **seis NPCs y las cinco balizas** a tu alrededor. Desde ahí puedes hablar con
todos, pelear con los guardianes, probar las escenas con voz y recorrer los cinco actos
sin moverte.

Para recogerlo: **[ DESMONTAR ]**. Solo borra lo del ensayo — los NPCs de Cobblemon que
haya por el mundo se quedan donde están, porque los del evento van marcados con un tag
propio.

Comprobado en el servidor: montó los 6 NPCs y las 5 balizas, y al desmontar quedaron cero.

---

## Una hora antes

| | Qué | Cómo |
|---|---|---|
| 1 | Comprobación previa | Botón **[ COMPROBAR ]** |
| 2 | Colocar los NPCs | `/spawnnpc cobblemon:ev_oak` etc. — ver tabla abajo |
| 3 | Esconder las balizas | Botón **[ PONER BALIZA ]** en cinco sitios |
| 4 | Subir el resourcepack de voces | **A mano**, ver más abajo |
| 5 | Abrir el servidor | `/whitelist off` |

### Dónde va cada NPC

| Comando | Quién | Dónde |
|---|---|---|
| `/spawnnpc cobblemon:ev_oak` | Profesor Oak | La aldea, junto a la estatua |
| `/spawnnpc cobblemon:ev_grum` | Grum | Señal 1 — bosque |
| `/spawnnpc cobblemon:ev_sable` | Sable | Señal 2 — montaña |
| `/spawnnpc cobblemon:ev_nix` | Nix | Señal 3 — costa |
| `/spawnnpc cobblemon:ev_guardia` | Guardia | Sala 1 del laboratorio (pon dos) |
| `/spawnnpc cobblemon:ev_vex` | Doctora Vex | Sala 3 del laboratorio |

Te colocas donde quieras que esté y lanzas el comando. No desaparecen.

### El resourcepack de voces

`evento/build/Evento-RP.zip` **no está subido a propósito**: cualquiera podría abrir el
ZIP y escuchar el final del evento, incluida la revelación de Luna.

Súbelo **el mismo día**, antes de abrir. Sin él, las escenas se ven con subtítulos pero
sin voz.

---

## Durante el evento

### Acto I — La llamada · 20 min

Con la gente reunida junto a Oak:

1. Botón **[ INICIAR ]**
2. Arranca sola la escena de Oak: **64 segundos**, seis líneas con voz y subtítulo.
   No toques nada mientras corre.
3. Al acabar, botón **[ RASTREADORES ]**
4. Que hablen con Oak si quieren oír más.

### Acto II — Las señales · 60 min

El grupo va **unido** de señal en señal.

- Cuando el guardián cae en combate → botón **[ GUARDIAN CAIDO ]**
- Eso suma una señal y, a la tercera, el motor pasa solo al Acto III.

> **Por qué hay que pulsarlo tú:** Cobblemon no avisa de que un NPC ha perdido. Lo
> comprobé en su código: `battleConfiguration` no tiene gancho de derrota y MoLang no
> expone nada parecido. Es el único punto del evento que no se automatiza.

Si una señal se eterniza, a los **25 minutos** Oak «recalibra» solo y el grupo avanza.

### Acto III — El cifrado · 40 min

Aquí el grupo **se separa**. Es el respiro del evento.

No tienes que hacer nada: las seis misiones se detectan solas. Con **cuatro** completadas
el motor pasa al Acto IV, y si a los 40 minutos no llegan, Oak descifra el resto con su
línea con voz.

### Acto IV — El laboratorio · 50 min

Sin límite de tiempo. Es el clímax.

- Sala 1: dos guardias
- Sala 2: cuatro palancas en el orden del código
- Sala 3: Vex

Cuando Vex cae → botón **[ VEX CAIDA ]**

### Acto V — El reencuentro · 15 min

1. Con todos delante de la cápsula, botón **[ REVELACION ]**
2. Corren seis líneas con voz: las lecturas raras, «ella se dejó encontrar», Arceus,
   la Diosa del Amor Incondicional, y «Alejandro, acércate tú».
3. Suelta a Luna a **nivel 70**. Solo AlejandroReport la captura.
4. Al capturarla → botón **[ LUNA CAPTURADA ]** — fuegos artificiales y cierre.

**La revelación no se lanza sola** a propósito: quieres dispararla cuando el grupo esté
delante de la cápsula, no cuando lo decida un reloj.

---

## Cuando algo se rompe

| Problema | Qué hacer |
|---|---|
| Un combate se cuelga | **[ SALTAR ACTO ]** da el acto por completado |
| Vamos con retraso | **[ MODO CORTO ]** — se salta la costa, quedan 2h 20min |
| La escena se lía | **[ CORTAR ]** y sigues a mano |
| Alguien entra tarde | No hagas nada: se le pone el acto en curso solo |
| Se cae el servidor | Los marcadores se guardan. Al volver sigue donde estaba |
| Hay que empezar de cero | **[ REINICIAR ]** |
| Alguien se atasca en las misiones | Solo hacen falta 4 de 6, y a los 40 min se completa |

**Un `/reload` no rompe nada.** Los marcadores solo se inicializan si no existen, y las
escenas van con el reloj propio en vez de con `schedule` justo por esto.

**Pero un cambio en los NPCs sí necesita reiniciar el servidor**: Cobblemon no relee sus
NPCs con `/reload`. Si tocas algo de `Evento-Datos-DP.zip`, reinicia.

---

## Comandos, por si falla el panel

```
/function evento:admin/iniciar          empezar
/function evento:admin/estado           cómo va todo
/function evento:admin/comprobar        repaso previo
/function evento:admin/saltar           forzar acto siguiente
/function evento:admin/reiniciar        todo a cero
/function evento:admin/modo_corto       saltar la costa
/function evento:admin/modo_completo    las tres señales
/function evento:admin/dar_rastreadores
/function evento:admin/poner_baliza
/function evento:admin/quitar_balizas
/function evento:admin/cortar_escena

/function evento:senales/completar      guardián derrotado
/function evento:lab/vex_derrotada      cae Vex
/function evento:actos/terminar         Luna capturada
/function evento:escenas/lanzar_acto1
/function evento:escenas/lanzar_revelacion
```

---

## Después

1. `/whitelist on` si quieres cerrar
2. **[ REINICIAR ]** para dejar los marcadores limpios
3. `/function evento:admin/quitar_balizas`
4. Los NPCs se quedan puestos; bórralos con `/kill @e[type=cobblemon:npc]` si molestan
   — ojo, eso también mata los NPCs de Cobblemon que no sean del evento.
