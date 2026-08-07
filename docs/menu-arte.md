# Menú de inicio — PokeReport: Luna Eternal

Prompts listos para pegar en Gemini y medidas exactas. Ya hay versiones provisionales
funcionando en [`client-pack/menu/`](../client-pack/menu/), así que el menú **abre
desde ya**; cuando tengas las buenas, se sustituyen los ficheros.

## Antes de empezar: tres reglas

1. **Pide siempre "sin texto, sin letras, sin marcas de agua".** Los generadores
   escriben fatal y te arruinan la imagen.
2. **Pide la proporción** (16:9 para el fondo, cuadrado para Luna). Si no, te la da
   cuadrada por defecto y al recortar pierdes composición.
3. **Para las que necesitan fondo transparente**, pídelas sobre **fondo verde liso**
   y luego se recorta. Los generadores casi nunca dan PNG transparente de verdad.

## Ficheros y medidas

Van en `config/fancymenu/assets/` dentro de la instancia del cliente.

| Fichero | Medidas | Transparencia | Para qué |
|---|---|---|---|
| `pokereport_background.png` | **2560 × 1440** | No | Fondo del menú |
| `pokereport_logo.png` | **2041 × 297** | Sí | El título |
| `luna.png` | **512 × 512** | Sí | Luna, junto a los botones |
| `boton_normal.png` | **200 × 40** | Sí | Botón en reposo (opcional) |
| `boton_hover.png` | **200 × 40** | Sí | Botón con el ratón encima (opcional) |

---

## 1 · Fondo del menú

Proporción **16:9**. Es la imagen más importante.

```
Ilustración digital de un paisaje nocturno de fantasía estilo Pokémon, en
proporción 16:9 panorámica. En primer plano, una colina suave en silueta oscura
con hierba alta y flores pequeñas. Al fondo a la derecha, la silueta de un pueblo
acogedor con tejados inclinados y ventanas iluminadas de amarillo cálido. Cielo
nocturno azul-violeta profundo lleno de estrellas, con una luna llena grande y
brillante en el tercio superior derecho, rodeada de un halo de luz suave.
Luciérnagas doradas flotando por el aire. Estilo pintura digital limpia de
videojuego, colores fríos con acentos cálidos dorados, ambiente sereno y
esperanzador, luminoso, nada triste ni sombrío. La mitad izquierda de la imagen
debe quedar despejada y sin detalles importantes. Sin texto, sin letras, sin
logotipos, sin personajes humanos, sin marcas de agua.
```

**Por qué la mitad izquierda despejada:** ahí van el título y los botones. Si hay
mucho detalle debajo, no se lee nada.

---

## 2 · Luna

Cuadrada. **Sustituye lo que va entre corchetes** por cómo es ella de verdad — cuanto
más concreto, más se le parecerá.

```
Ilustración de un perro [RAZA] de pelaje [COLOR Y DESCRIPCIÓN: por ejemplo, marrón
claro con el pecho blanco], sentado de perfil mirando hacia arriba al cielo, cuerpo
entero, en proporción cuadrada 1:1. Lleva un collar [COLOR DEL COLLAR] con una
placa dorada. Orejas [caídas / de punta]. Expresión tranquila, serena y feliz.
Estilo pintura digital limpia de videojuego, contornos suaves, sin realismo
fotográfico. Iluminado por detrás con luz de luna azulada que le dibuja el contorno
del pelaje. Fondo verde liso uniforme, sin sombra en el suelo, sin escenario. Sin
texto, sin letras, sin marcas de agua.
```

Cuando la tengas: **mándamela y le quito el fondo verde**, o lo haces tú con
remove.bg o Photopea.

---

## 3 · El título

**No lo generes con IA.** Escriben mal las letras casi siempre: se inventan
caracteres y salen deformadas. El `pokereport_logo.png` que hay ahora está compuesto
con tipografía de verdad y se lee perfecto.

Si lo quieres más vistoso, pide **solo el adorno, sin letras**, y yo le monto el
texto encima:

```
Emblema decorativo horizontal para logotipo de videojuego, muy alargado en
proporción 7:1. Marco ornamental de filigrana dorada, simétrico, con una media luna
creciente en el extremo izquierdo y una huella de perro en el extremo derecho.
El centro completamente vacío y despejado. Estilo limpio de interfaz de videojuego
de fantasía, dorado con reflejos suaves. Fondo verde liso uniforme. Sin texto, sin
letras, sin números, sin marcas de agua.
```

---

## 4 · Botones (opcional)

Solo si quieres botones con textura en vez de los de Minecraft.

**En reposo:**

```
Textura de botón rectangular horizontal para interfaz de videojuego, proporción 5:1.
Estilo Pokédex: placa de plástico azul oscuro con borde biselado, esquinas
redondeadas y un fino filo dorado alrededor. Superficie lisa con un brillo suave
arriba. Centro completamente vacío y liso. Vista frontal plana, sin perspectiva.
Fondo verde liso uniforme. Sin texto, sin letras, sin iconos, sin marcas de agua.
```

**Con el ratón encima** (mismo prompt cambiando el color, para que se noten
iguales pero encendido):

```
Textura de botón rectangular horizontal para interfaz de videojuego, proporción 5:1.
Estilo Pokédex: placa de plástico azul claro luminoso con borde biselado, esquinas
redondeadas y un filo dorado brillante alrededor, con un resplandor cálido suave
como si estuviera encendido. Centro completamente vacío y liso. Vista frontal plana,
sin perspectiva. Fondo verde liso uniforme. Sin texto, sin letras, sin iconos, sin
marcas de agua.
```

Genera los dos **en la misma conversación y seguidos**, para que salgan del mismo
estilo. Si los pides por separado no cuadran entre sí.

---

## 5 · Detalle extra (opcional)

Queda muy bien arriba a la derecha, cerca de la luna del fondo:

```
Constelación de estrellas con forma de huella de perro, líneas finas blancas
conectando puntos de luz brillantes, estilo mapa estelar minimalista y delicado.
Fondo verde liso uniforme. Sin texto, sin letras, sin marcas de agua.
```

---

## Qué hacer con las imágenes

1. Recorta o escala a las **medidas exactas** de la tabla de arriba.
2. Quita el fondo verde de las que lleven transparencia.
3. Déjalas en `client-pack/menu/config/fancymenu/assets/` con **esos nombres exactos**.
4. Republica el pack (ver [launcher.md](launcher.md)) y los jugadores lo reciben solos.

Si alguna imagen falta o tiene otro nombre, FancyMenu tira del `fallback_path` y el
menú abre igual con la imagen original del pack. No se rompe nada.

## Regenerar el layout

```bash
python scripts/build_menu.py --mrpack "client-pack/COBBLEVERSE 1.7.42.mrpack" --out client-pack/menu
```

### Por qué se toca también `cobbleverse_main.txt`

FancyMenu aplica **todos** los layouts activos de una misma pantalla. Si dejas el del
pack encendido, los dos se pintan encima y el resultado depende del orden de carga.
Por eso el script genera una copia del suyo con `is_enabled = false`.

## Mover cosas sin editar ficheros

Dentro del juego: **Opciones → FancyMenu → Editar layout de la pantalla de título**.
Se arrastran los elementos con el ratón. Es más cómodo que el `.txt`, y lo que
guardes ahí manda.

## Qué hay puesto ahora

- Fondo de noche estrellada con luna llena (provisional, generado).
- Título **POKEREPORT / LUNA ETERNAL** compuesto con tipografía.
- Silueta de Luna con collar dorado junto a los botones (provisional).
- Marca en la esquina: `POKEREPORT [Luna Eternal]`.
- Debajo de los botones: *«Para Luna. Siempre con nosotros.»*

Ese texto se cambia en `scripts/build_menu.py` (busca `Para Luna`) o en el editor de
FancyMenu dentro del juego.
