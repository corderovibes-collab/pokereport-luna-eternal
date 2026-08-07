#!/usr/bin/env python3
"""Genera el menu de inicio 'PokeReport: Luna Eternal' para FancyMenu.

En vez de escribir un layout desde cero (FancyMenu 3.9.8 tiene ~70 claves por
elemento y una sola mal puesta deja el menu en blanco), se parte del layout que
ya trae COBBLEVERSE y se le cambia lo justo: fondo, logo, textos y los elementos
nuevos dedicados a Luna. Todas las claves salen de un fichero que ya funciona.

Uso:
  python scripts/build_menu.py --mrpack "client-pack/COBBLEVERSE 1.7.42.mrpack" \
      --out client-pack/menu
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import uuid
import zipfile

SRC_LAYOUT = "overrides/config/fancymenu/customization/cobbleverse_main.txt"
ASSET_DIR = "config/fancymenu/assets"

# Nuestros ficheros de arte. Si alguno falta, FancyMenu usa el `fallback_path`
# y el menu sigue abriendo, solo que con la imagen original del pack.
BACKGROUND = "pokereport_background.png"
LOGO = "pokereport_logo.png"
LUNA = "luna.png"
BOTON = "boton.png"
BOTON_HOVER = "boton_hover.png"


def new_id() -> str:
    """Identificador con el mismo formato que genera FancyMenu: uuid-timestamp."""
    return f"{uuid.uuid4()}-1790000000000"


def element(kind: str, *, anchor: str, x: int, y: int, w: int, h: int, extra: str) -> str:
    """Elemento con el juego completo de claves que espera FancyMenu 3.9.8."""
    req = new_id()
    return f"""
element {{
{extra.rstrip()}
  element_type = {kind}
  instance_identifier = {new_id()}
  appearance_delay = no_delay
  disappearance_delay = no_delay
  fade_in_v2 = no_fading
  fade_out = no_fading
  auto_sizing = false
  auto_sizing_base_screen_width = 2563
  auto_sizing_base_screen_height = 1443
  sticky_anchor = false
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stay_on_screen = true
  element_loading_requirement_container_identifier = {req}
  [loading_requirement_container_meta:{req}] = [groups:][instances:]
  enable_parallax = false
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  layer_hidden_in_editor = false
  advanced_rotation_mode = false
  advanced_vertical_tilt_mode = false
  advanced_horizontal_tilt_mode = false
  should_be_affected_by_decoration_overlays = false
  in_editor_color = #FFC800FF
  advanced_posx = -2147483648
  advanced_posy = -2147483648
  advanced_width = -2147483648
  advanced_height = -2147483648
  stretch_x = false
  stretch_y = false
  appearance_delay_seconds = 1.0
  disappearance_delay_seconds = 1.0
  fade_in_speed = 1.0
  fade_out_speed = 1.0
  base_opacity = 1.0
  parallax_intensity_x = 0.5
  parallax_intensity_y = 0.5
  rotation_degrees = 0.0
  advanced_rotation_degrees = 0.0
  vertical_tilt_degrees = 0.0
  advanced_vertical_tilt_degrees = 0.0
  horizontal_tilt_degrees = 0.0
  advanced_horizontal_tilt_degrees = 0.0
{IMAGE_TAIL if kind == "image" else TEXT_TAIL}
}}
"""


IMAGE_TAIL = """  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  restart_animated_on_menu_load = false
  image_tint = #FFFFFF
  rounding_radius_top_left = 0.0
  rounding_radius_top_right = 0.0
  rounding_radius_bottom_right = 0.0
  rounding_radius_bottom_left = 0.0"""

TEXT_TAIL = """  base_color = #FFFFFFFF
  scale = 1.0
  text_border = 2
  line_spacing = 2
  quote_indent = 8.0
  bullet_list_indent = 8.0
  bullet_list_spacing = 3.0
  table_line_thickness = 1.0
  table_cell_padding = 8.0
  table_margin = 4.0"""


def image_element(path: str, *, anchor: str, x: int, y: int, w: int, h: int) -> str:
    return element("image", anchor=anchor, x=x, y=y, w=w, h=h,
                   extra=f"  source = [source:local]/{ASSET_DIR}/{path}")


def text_element(markdown: str, *, anchor: str, x: int, y: int, w: int, h: int,
                 escala: float = 1.15) -> str:
    extra = f"""  interactable = false
  source = {markdown}
  source_mode = direct
  shadow = true
  enable_scrolling = false
  auto_line_wrapping = false
  remove_html_breaks = true
  code_block_single_color = #737373FF
  code_block_multi_color = #565656FF
  headline_line_color = #A9A9A9FF
  separation_line_color = #A9A9A9FF
  hyperlink_color = #0771FCFF
  click_event_color = #FFEA00
  hover_event_color = #0771FCFF
  quote_color = #818181FF
  quote_italic = false
  bullet_list_dot_color = #A9A9A9FF
  parse_markdown = true
  table_show_header = true
  table_alternate_row_colors = true
  table_line_color = #787878FF
  table_header_background_color = #323232FF
  table_row_background_color = #282828FF
  table_alternate_row_color = #3C3C3CFF"""
    bloque = element("text_v2", anchor=anchor, x=x, y=y, w=w, h=h, extra=extra)
    # Un pelin mas grande y con mas borde: sobre un fondo con estrellas y hierba,
    # el texto a tamano 1.0 y borde 2 se pierde.
    bloque = bloque.replace("  scale = 1.0", f"  scale = {escala}")
    bloque = bloque.replace("  text_border = 2", "  text_border = 3")
    return bloque


# Medidas del titulo dentro del menu, en las unidades del layout (base 1920x1080).
# Se fija el ancho y el alto sale de la proporcion real de la imagen, para que no
# se aplaste: el hueco original era 268x39 (6.9:1) y el titulo nuevo es 3.8:1.
TITULO_ANCHO = 300


def colocar_titulo(layout: str, proporcion: float) -> str:
    """Recoloca el elemento del titulo: arriba, centrado y con su proporcion real."""
    alto = round(TITULO_ANCHO / proporcion)
    i = layout.find(LOGO)
    if i < 0:
        return layout
    ini = layout.rfind("element {", 0, i)
    fin = layout.find("\n}", i)
    bloque = layout[ini:fin]

    # Desplazado a la derecha del centro: asi despeja la cabeza de Luna, que en el
    # fondo esta en el tercio izquierdo, y queda alineado con la columna de botones.
    for clave, valor in (("anchor_point", "top-centered"),
                         ("x", -TITULO_ANCHO // 2 + 46),
                         ("y", 14),
                         ("width", TITULO_ANCHO),
                         ("height", alto)):
        bloque = re.sub(rf"^(\s*{clave} = ).*$", rf"\g<1>{valor}", bloque, count=1, flags=re.M)

    print(f"  titulo: {TITULO_ANCHO}x{alto} arriba y centrado (proporcion {proporcion:.2f}:1)")
    return layout[:ini] + bloque + layout[fin:]


def _bloques(texto: str, tipo: str) -> list[tuple[int, int, str]]:
    """Localiza los bloques de primer nivel de un tipo: (inicio, fin, contenido)."""
    out = []
    for m in re.finditer(rf"^{tipo} \{{$", texto, re.M):
        fin = texto.index("\n}", m.start())
        out.append((m.start(), fin + 2, texto[m.start():fin]))
    return out


# Adornos que trae el layout de COBBLEVERSE y que no pintan nada en el nuestro:
# el marco del Pokedex, el pase de diapositivas, el icono de Discord y un boton
# de publicidad de hosting.
BASURA = ("pokedex_menu", "slideshow_frame", "discord_icon", "cobbleverse")

# Tipos de elemento del pack que sobran enteros (el "by LUMYVERSE" del splash).
TIPOS_BASURA = ("slideshow", "custom_button", "splash_text")


def limpiar_pack(layout: str) -> str:
    """Borra los elementos decorativos del pack original."""
    fuera = []
    for ini, fin, blk in _bloques(layout, "element"):
        tipo = re.search(r"element_type = (\S+)", blk)
        src = re.search(r"source = (\S+)", blk)
        es_basura = (
            (tipo and tipo.group(1) in TIPOS_BASURA)
            or (src and any(k in src.group(1) for k in BASURA))
        )
        if es_basura:
            fuera.append((ini, fin))
    for ini, fin in reversed(fuera):
        layout = layout[:ini] + layout[fin:]
    print(f"  adornos del pack eliminados: {len(fuera)}")
    return layout


SERVIDOR = "s17.mia.us.tarohosting.lat:33445"

# Columna de botones, en unidades del layout (base 640x360). Van a la derecha,
# sobre el cielo, dejando libre la ladera de la izquierda para Luna.
#
# Solo quedan Opciones y Salir: el de conectarse se crea aparte porque es un boton
# propio con la accion `joinserver`, no uno de los de Minecraft.
COLUMNA = [
    ("mc_titlescreen_options_button", -2),
    ("mc_titlescreen_quit_button", 24),
]
BOTON_ANCHO, BOTON_ALTO = 176, 20
BOTON_X = -(BOTON_ANCHO + 40)   # respecto al borde derecho
CONECTAR_Y = -34                # justo encima de Opciones

# Botones de Minecraft que sobran en un launcher dedicado a un solo servidor, mas
# los widgets que FancyMenu declara como "vanilla_button" sin serlo (el logo, el
# splash amarillo y el aviso de Realms).
FUERA_DE_PANTALLA = (
    "mc_titlescreen_multiplayer_button",
    "mc_titlescreen_singleplayer_button",
    "mc_titlescreen_realms_button",
    "modmenu_titlescreen_mods_button",
    "minecraft_logo_widget",
    "minecraft_splash_widget",
    "minecraft_realms_notification_icons_widget",
)


def boton_conectar() -> str:
    """Boton propio que entra directo al servidor.

    Usa la accion `joinserver` de FancyMenu (clase JoinServerAction), asi que hace
    lo mismo que elegir el servidor en la lista de multijugador, pero de un clic.
    """
    accion = new_id()
    bloque = new_id()
    extra = f"""  button_element_executable_block_identifier = {bloque}
  [executable_action_instance:{accion}][action_type:joinserver] = {SERVIDOR}
  [executable_block:{bloque}][type:generic] = [executables:{accion}]
  underline_label_on_hover = false
  transparent_background = false
  restartbackgroundanimations = true
  nine_slice_custom_background = true
  nine_slice_border_x = 6
  nine_slice_border_y = 6
  backgroundnormal = [source:local]/{ASSET_DIR}/{BOTON}
  backgroundhovered = [source:local]/{ASSET_DIR}/{BOTON_HOVER}
  description = Entrar al servidor PokeReport: Luna Eternal
  label = Conectarse a PokeReport
  navigatable = true
  widget_active_state_requirement_container_identifier = {new_id()}
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  label_scale = 1.0
  label_shadow = true
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5"""
    return element("custom_button", anchor="mid-right", x=BOTON_X, y=CONECTAR_Y,
                   w=BOTON_ANCHO, h=BOTON_ALTO, extra=extra)

# Widgets que se dejan como estan: son informativos y van discretos abajo.
INTOCABLES = ("title_screen_copyright_button", "minecraft_branding_widget")


def colocar_botones(layout: str) -> str:
    """Coloca la columna a la derecha y saca de en medio lo que no es un boton."""
    destinos = dict(COLUMNA)
    movidos = 0
    for ini, fin, blk in reversed(_bloques(layout, "vanilla_button")):
        ident = re.search(r"instance_identifier = (\S+)", blk)
        if not ident:
            continue
        nombre = ident.group(1)

        if nombre in INTOCABLES:
            continue
        if nombre in FUERA_DE_PANTALLA:
            # `stay_on_screen` es la clave: con ella activada FancyMenu ignora la
            # posicion y devuelve el boton al borde visible. Por eso "Multijugador"
            # reaparecia a la izquierda por mucho que se mandara a -9999.
            nuevo = {"anchor_point": "mid-left", "x": -9999, "y": 0,
                     "stay_on_screen": "false"}
        elif nombre in destinos:
            nuevo = {"anchor_point": "mid-right", "x": BOTON_X, "y": destinos[nombre],
                     "width": BOTON_ANCHO, "height": BOTON_ALTO}
        else:
            # Botones sueltos que anaden los mods: tampoco pintan nada aqui.
            nuevo = {"anchor_point": "mid-left", "x": -9999, "y": 0,
                     "stay_on_screen": "false"}
            movidos += 1

        for clave, valor in nuevo.items():
            blk = re.sub(rf"^(\s*{clave} = ).*$", rf"\g<1>{valor}", blk, count=1, flags=re.M)
        layout = layout[:ini] + blk + layout[fin - 2:]

    print(f"  columna a la derecha ({len(COLUMNA)} botones), "
          f"{len(FUERA_DE_PANTALLA)} widgets y {movidos} iconos de mods fuera de pantalla")
    return layout


def texturizar_botones(layout: str) -> str:
    """Pone textura propia a los botones del menu.

    Las claves (`backgroundnormal`, `backgroundhovered`) salen de mirar el jar de
    FancyMenu 3.9.8, no de adivinar. Se activa el nine-slice con borde de 6 px para
    que la placa se estire sin deformar las esquinas.
    """
    nuevas = "\n".join([
        "  nine_slice_custom_background = true",
        "  nine_slice_border_x = 6",
        "  nine_slice_border_y = 6",
        f"  backgroundnormal = [source:local]/{ASSET_DIR}/{BOTON}",
        f"  backgroundhovered = [source:local]/{ASSET_DIR}/{BOTON_HOVER}",
    ]) + "\n"

    # Solo los cinco botones de verdad. Texturizar los widgets informativos es lo
    # que llenaba la pantalla de recuadros vacios.
    reales = {nombre for nombre, _ in COLUMNA}

    partes = layout.split("vanilla_button {")
    salida = [partes[0]]
    tocados = 0
    for bloque in partes[1:]:
        ident = re.search(r"instance_identifier = (\S+)", bloque)
        if (ident and ident.group(1) in reales
                and "backgroundnormal" not in bloque
                and "nine_slice_custom_background = false\n" in bloque):
            bloque = bloque.replace("  nine_slice_custom_background = false\n", nuevas, 1)
            tocados += 1
        salida.append(bloque)
    print(f"  botones texturizados: {tocados}")
    return "vanilla_button {".join(salida)


def customize(layout: str, proporcion: float | None = None) -> str:
    # 1) Fondo: el nuestro, con el del pack como red de seguridad.
    layout = re.sub(
        r"(image_path = \[source:local\]/config/fancymenu/assets/)latias_latios_background\.png",
        rf"\1{BACKGROUND}", layout)
    layout = re.sub(
        r"(fallback_path = \[source:local\]/config/fancymenu/assets/)bg_test\.png",
        r"\1latias_latios_background.png", layout)

    # 2) Logo en lugar del titulo de COBBLEVERSE.
    layout = layout.replace(
        f"source = [source:local]/{ASSET_DIR}/cobbleverse_title.png",
        f"source = [source:local]/{ASSET_DIR}/{LOGO}")

    # 3) La marca de la esquina inferior izquierda se elimina entera: repetia el
    #    titulo que ya esta arriba y encima quedaba tapada por los iconos de mods.
    for ini, fin, blk in reversed(_bloques(layout, "element")):
        if "COBBLE%#%VERSE" in blk:
            layout = layout[:ini] + layout[fin:]

    # 4) Elementos nuevos, justo antes del cierre del fichero.
    # Luna ya no va como elemento suelto: viene dentro del propio fondo, sentada
    # en la colina mirando a la luna. Ponerla otra vez la duplicaria.
    # La dedicatoria va debajo de los botones, sobre el cielo limpio: abajo del
    # todo caia sobre la hierba y las flores y no habia quien la leyera. La caja
    # de 12 px tambien la cortaba por la mitad.
    nuevos = (
        boton_conectar()
        + text_element(
            "%#E8DCFF%*Para Luna*%#%%#8A7BB8% · %#%%#C6A7FF%*siempre con nosotros*%#%",
            anchor="mid-right", x=BOTON_X, y=58, w=BOTON_ANCHO + 30, h=22, escala=1.0)
    )
    layout = limpiar_pack(layout)
    layout = colocar_botones(layout)
    layout = texturizar_botones(layout.rstrip()) + "\n" + nuevos
    if proporcion:
        layout = colocar_titulo(layout, proporcion)
    return layout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mrpack", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--titulo", default=None,
                    help="PNG del titulo (se copia a assets y se ajusta el layout a su proporcion)")
    args = ap.parse_args()

    with zipfile.ZipFile(args.mrpack) as z:
        try:
            base = z.read(SRC_LAYOUT).decode("utf-8")
        except KeyError:
            sys.exit(f"El .mrpack no contiene {SRC_LAYOUT}")

    proporcion = None
    if args.titulo:
        from PIL import Image
        img = Image.open(args.titulo).convert("RGBA")
        caja = img.getbbox() or (0, 0, *img.size)
        img = img.crop(caja)
        proporcion = img.width / img.height
        # 2048 px de ancho: nitido en pantallas grandes sin engordar el pack.
        destino_img = os.path.join(args.out, "config", "fancymenu", "assets", LOGO)
        os.makedirs(os.path.dirname(destino_img), exist_ok=True)
        img.resize((2048, round(2048 / proporcion)), Image.NEAREST).save(destino_img)
        print(f"  titulo importado: {img.width}x{img.height} -> 2048x{round(2048/proporcion)}")

    layout = customize(base, proporcion)

    out_layout = os.path.join(args.out, "config", "fancymenu", "customization")
    os.makedirs(out_layout, exist_ok=True)
    dest = os.path.join(out_layout, "pokereport_main.txt")
    with io.open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(layout)

    # FancyMenu aplica TODOS los layouts activos de la misma pantalla, asi que el
    # del pack se reescribe desactivado: si no, los dos se pintan encima y el
    # resultado depende del orden de carga.
    off = re.sub(r"^(\s*is_enabled\s*=\s*)true\s*$", r"\1false", base, count=1, flags=re.M)
    if off == base:
        print("  AVISO: no se encontro 'is_enabled' en el layout del pack; desactivalo a mano")
    with io.open(os.path.join(out_layout, "cobbleverse_main.txt"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write(off)

    print(f"escrito {dest}")
    print("  y cobbleverse_main.txt con is_enabled = false (para que no se solapen)")
    print(f"  elementos: {len(re.findall(r'^element \{', layout, re.M))} "
          f"| botones vanilla: {len(re.findall(r'^vanilla_button \{', layout, re.M))}")
    print(f"  arte esperado en {ASSET_DIR}/: {BACKGROUND}, {LOGO}, {LUNA}")
    print("  (si falta alguno, FancyMenu tira del fallback y el menu abre igual)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
