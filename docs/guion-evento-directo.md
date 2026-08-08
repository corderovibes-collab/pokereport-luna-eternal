# El Rastro de Luna — guion de directo

Paso a paso para conducir el evento. Los comandos van tal cual, con las llaves donde las haya.

Panel de mando, por si se pierde de vista:

```
/function evento:admin/panel
```

---

## 0. Antes de abrir

Con el servidor aún cerrado.

| Comprobación | Cómo |
|---|---|
| Los 5 NPCs colocados | Oak `1084 66 530` · Grum `1888 64 257` · Sable `1630 69 164` · Nix `1621 63 550` · Vex `1800 80 569` |
| Jefes en modo real | `/function evento:admin/modo_real` |
| Estado limpio | `[ REINICIAR ]` si se ha ensayado antes |

`[ REINICIAR ]` borra los 35 marcadores y las brújulas. Úsalo sin miedo **antes** de empezar; nunca a mitad.

---

## 1. Abrir el servidor

```
/whitelist off
```

Entran y andan por la aldea a su aire. El evento no ha empezado: no hay nada activo y los cristales están apagados.

---

## 2. Boom — la sala de espera

```
/function evento:sala/abrir_min {min:2}
```

En ese instante, a todos menos a los admin:

- Pantalla completa con Luna y la cuenta atrás
- Teletransporte a **1084 66 553**, junto al laboratorio de Oak
- Bloqueados: si se mueven, se les repone la posición
- Sin daño ni hambre

Tú sigues viendo el mundo y moviéndote con normalidad.

Alternativas: `/function evento:sala/panel` saca una botonera con duraciones, **[ EMPEZAR YA ]** y **[ CANCELAR ]**.

---

## 3. Repartir, mientras están quietos

Es el mejor momento: están juntos y no se dispersan.

1. **[ REPARTIR LIBROS ]** — el libro de misiones a todo el mundo
2. **[ POBLAR ZONAS ]** — suelta los 48 Pokémon de las tres zonas
3. **[ INVITAR ]** — les sale el botón para apuntarse

> El orden importa. Primero los libros y luego los Pokémon: al revés, se encuentran bichos de nivel 60 por el mapa sin ninguna explicación.

Las tres zonas y lo que hay en cada una:

| Zona | Pokémon | Coordenadas | Papel |
|---|---|---|---|
| 1 | Granbull | `1238 64 508` | Tanque |
| 2 | Machamp | `1230 69 460` | Daño |
| 3 | Ribombee | `1162 68 412` | Soporte |

Todos de nivel 60. Hasta que no capturen los tres no quedan acreditados.

---

## 4. Esperar a que capturen

Sin prisa. Puedes ir viendo quién lleva ya la acreditación con **[ ESTADO ]**.

---

## 5. Arrancar la historia

```
[ INICIAR ]
```

Tiene tres seguros y se niega a empezar si:

- Ya hay un evento en curso
- No hay nadie apuntado
- **Alguien apuntado no está acreditado** — y te dice quién falta

---

## 6. A partir de aquí va solo

No hay que tocar nada. La cadena se encadena sola:

```
Oak entrega la brújula
   ↓
Señal 1 → Grum → cristal se enciende → raid
   ↓
Señal 2 → Sable → cristal → raid
   ↓
Señal 3 → Nix → cristal → raid
   ↓
Laboratorio → Vex (raid de grupo)
   ↓
Revelación → aparece Luna, nivel 75, quieta
   ↓
Solo A1ejandroreport recibe la Ball → la captura → fin
```

Los cristales se encienden cuando el grupo llega a cada señal. Antes están apagados a propósito, para que nadie entre a una raid antes de tiempo.

---

## Red de seguridad

Solo si algo se atasca en directo.

| Situación | Qué hacer |
|---|---|
| Un acto no avanza | **[ SALTAR ACTO ]** |
| Alguien se queda bloqueado en la sala | `/function evento:sala/cerrar` |
| Hay que rehacerlo todo | **[ REINICIAR ]** y volver al paso 2 |
| Ver en qué punto va | **[ ESTADO ]** |

---

## Voces

Las 19 líneas se reproducen con `execute as @a[tag=ev_participa] at @s`, así que **cada participante la oye en su propia posición**. Quien no esté apuntado no oye nada.

Si alguien no oye ninguna voz, es que no tiene el resource pack: que abra el launcher y le dé a jugar.
