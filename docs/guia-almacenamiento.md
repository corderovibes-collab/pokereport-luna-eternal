# Guía de almacenamiento — PokeReport: Luna Eternal

Cómo tener todos los cofres ordenados y que las cosas se coloquen solas.

El servidor ya trae **tres mods** para esto. No hay que instalar nada: están puestos
desde siempre y casi nadie los usa.

---

## Lo rápido

| Quiero… | Uso |
|---|---|
| Un botón que me ordene el cofre | **Client Sort** |
| Una pantalla que busque en todos mis cofres a la vez | **Tom's Simple Storage** |
| Que un cofre se llene o se vacíe solo | **Sophisticated Storage** |

Todas las recetas se miran **en el juego con REI**: abre el inventario y busca el objeto
en el panel de la derecha. No hace falta memorizar nada.

---

## 1 · Ordenar de un clic

**Client Sort**, recién añadido. Abre cualquier cofre y verás un **botón de ordenar**
arriba a la derecha. También funciona en tu propio inventario.

Atajos que ahorran mucho tiempo:

| Tecla | Qué hace |
|---|---|
| Clic en el botón | Ordena el cofre |
| `Ctrl` + clic izquierdo | Mete todo lo que encaje |
| Doble clic en un hueco | Junta todos los montones de ese objeto |

Es **solo del cliente**: el servidor ni se entera, así que no cuesta rendimiento.

---

## 2 · Una pantalla para todos los cofres

**Tom's Simple Storage** es lo que de verdad resuelve el desorden. En vez de tener veinte
cofres y no acordarte de qué hay en cuál, montas **una pantalla** que los ve todos.

### Montaje mínimo

Hacen falta tres cosas:

```
        [ Terminal de almacenamiento ]     ← la pantalla con buscador
                    │
        [ Conector de inventario ]         ← el corazón de la red
           ┌────────┼────────┐
        [cofre]  [cofre]  [cofre]          ← pegados al conector
```

1. Pon el **Conector de inventario** (*Inventory Connector*) en el suelo.
2. Pega los cofres a su alrededor, tocándolo.
3. Pon el **Terminal de almacenamiento** (*Storage Terminal*) sobre el conector.

Ya está. Abre el terminal y verás el contenido de todos los cofres a la vez, con
buscador.

### Lo que hace que valga la pena

- **Buscas escribiendo.** Pones «pokeball» y te salta a lo que hay.
- **Al meter cosas se reparten solas** al cofre donde ya tienes de eso. Esto es
  literalmente «que se acomode en cada cofre».
- **`Shift` + clic** para depositar de golpe todo el inventario.

### Cuando se te queda pequeño

| Bloque | Para qué |
|---|---|
| **Cable de inventario** | Alarga la red: los cofres ya no tienen que tocar el conector |
| **Conector de cable** | Conecta un cofre lejano al cable |
| **Terminal de fabricación** | El mismo terminal pero con mesa de crafteo incorporada |
| **Terminal inalámbrico** | Abre tu red desde cualquier sitio |
| **Terminal inalámbrico avanzado** | Igual pero con más alcance |

El terminal de fabricación es el que más se agradece: crafteas tirando directamente de
todos los cofres, sin ir sacando materiales.

---

## 3 · Cofres que se gestionan solos

**Sophisticated Storage** son cofres, barriles y cofres de shulker con **ranuras de
mejora**. Un cofre normal guarda; uno de estos trabaja.

Las mejoras que más se usan:

| Mejora | Qué hace |
|---|---|
| **Filtro (Hopper)** | Mete y saca objetos solo, según el filtro que le pongas |
| **Imán (Magnet)** | Recoge lo que caiga cerca, sin que tú lo toques |
| **Anulador (Void)** | Tira lo que no quieres — perfecto para tierra y grava |
| **Apilado (Stack)** | Multiplica cuánto cabe en cada hueco |
| **Compactador** | Convierte los lingotes en bloques automáticamente |
| **Fundidor** | Funde lo que entra |
| **Bomba de experiencia** | Guarda la experiencia y te la devuelve |

Además, estos cofres **ya traen sus propios botones de ordenar** dentro: por nombre, por
cantidad o por mod.

Y hay **mochilas** (*Sophisticated Backpacks*) con el mismo sistema de mejoras. Una
mochila con imán mientras minas te ahorra media vida.

---

## Cómo combinarlo

Lo que mejor funciona en la práctica:

1. **Sophisticated Storage** para los cofres que trabajan — el que recoge lo que produce
   una granja, el que tira la basura.
2. **Tom's Storage** encima de todo, para tener una sola pantalla con todo.
3. **Client Sort** para el día a día.

Los tres conviven sin problema: los cofres de Sophisticated se conectan a la red de Tom's
igual que un cofre normal.

---

## Notas

- El terminal de Tom's **no tiene protección propia**: si tu base está en un chunk
  reclamado, ya estás cubierto. Si no, reclámalo con `/openpac-claims claim`.
- La red de Tom's tiene un límite de bloques conectados. Si dejas de ver cofres, has
  llegado al tope: monta una segunda red.
- **Tom's Storage está en la versión 2.4.1** desde el 3 de agosto de 2026.
