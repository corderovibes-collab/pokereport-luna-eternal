# -*- coding: utf-8 -*-
"""Inserta el arbol de dialogos de Grum en su preset de Easy NPC.

Misma mecanica que Oak — la maquinaria de NBT se reutiliza tal cual en vez de
copiarla, que ya costo bastante afinarla la primera vez.

DONDE ENCAJA
------------
Grum es lo ultimo que pasa antes de la incursion. La escena va asi:

    el grupo llega al campamento
        -> habla con Grum (una persona conduce, el resto escucha)
        -> Grum suelta a su Mightyena
        -> todos tocan el cristal y pelean la incursion

Por eso el ultimo boton no da ningun objeto: solo manda al cristal.

SOBRE EL PERSONAJE
------------------
Grum no es un maton de dos frases. Cree de verdad que el Eclipse hizo lo
correcto, y su argumento —que un amor incondicional que te alcanza sin haberlo
elegido es una forma de control— es lo bastante razonable como para dejar dudas.
Eso prepara el giro del Acto V en vez de gastarlo.

Uso:
    python evento/grum_dialogo.py audit/grum.npc.nbt audit/grum_con_dialogo.npc.nbt
"""
import gzip
import struct
import sys

from oak_dialogo import (COMPOUND, INT, LIST, Escritor, Lector, Tag,
                         accion_comando, accion_dialogo, boton, pagina)


def voz(clip):
    return accion_comando(
        f"/playsound evento:voz.grum.{clip} voice @a[tag=ev_participa] ~ ~ ~ 1000000 1")


def callar():
    return accion_comando("/stopsound @a[tag=ev_participa] voice")


def coro(texto):
    """Lo que ve todo el grupo, no solo quien esta hablando con el NPC."""
    # Barra + n como DOS caracteres: es un escape dentro del JSON del tellraw,
    # no un salto de linea real. Con un salto de verdad el comando no compila.
    NL = chr(92) + "n"
    seguro = texto.replace('"', "'")
    return accion_comando(
        '/tellraw @a[tag=ev_participa] ["",{"text":"' + NL + '  GRUM DEL ECLIPSE  ","color":"dark_red","bold":true},'
        '{"text":"' + seguro + NL + '","color":"gray"}]')


# El remate de la escena NO se dispara aqui.
#
# `g1_06` dura casi siete segundos. Si el gruñido, el titulo y el aviso salen al
# pulsar el boton, le pisan la voz y la escena se atropella.
#
# Easy NPC no puede llamar a `function` ni a `schedule` (los bloquea
# `unsafeNpcCommands`), pero `scoreboard` si le pasa. Asi que el boton solo deja
# un numero y se va: el reloj del datapack lo baja de uno en uno y remata al
# llegar a cero, ya con la voz terminada. Ver `grum/cuenta` y `grum/reto` en
# build_dp.py.
GUARDIAN = 1   # ver GUARDIANES en build_dp.py
ESPERA = 8     # segundos; g1_06 dura 6,96

REMATE_ID = accion_comando(f"/scoreboard players set #ev ev_reto_id {GUARDIAN}")
REMATE = accion_comando(f"/scoreboard players set #ev ev_reto {ESPERA}")


DIALOGOS = [
    pagina("default", "El guardián", [
        "Alto ahí.\nEste bosque está cerrado. Den la vuelta por donde vinieron.",
    ], [
        boton("b_quien", "¿Y tú quién eres?",
              callar(), voz("g1_02"),
              coro("Grum. Del Equipo Eclipse. Y ustedes son los del profesor, "
                   "verdad? Ese viejo nunca aprende."),
              accion_dialogo("quien")),
    ]),

    pagina("quien", "Grum", [
        "Grum. Del Equipo Eclipse.\nY ustedes son los del profesor, ¿verdad?"
        " Ese viejo nunca aprende.",
    ], [
        boton("b_venimos", "Venimos por Luna.",
              callar(), voz("g1_03"),
              coro("No vienen por ella. Vienen porque el les dijo que vinieran. "
                   "No es lo mismo, aunque ahora no lo vean."),
              accion_dialogo("motivo")),
    ]),

    pagina("motivo", "El motivo", [
        "No vienen por ella.\nVienen porque él les dijo que vinieran. No es lo"
        " mismo, aunque ahora no lo vean.",
    ], [
        boton("b_hicieron", "¿Qué le hicieron?",
              callar(), voz("g1_04"),
              coro("Saben lo que hace esa criatura? Se te mete dentro. Te hace "
                   "querer cosas que no elegiste. Yo la custodie tres dias. "
                   "Tres. Y todavia sueno con ella."),
              accion_dialogo("advertencia")),
    ]),

    # La pagina que hace el trabajo de verdad: aqui es donde el villano deja de
    # ser un obstaculo y se convierte en alguien que puede tener razon.
    pagina("advertencia", "La advertencia", [
        "¿Saben lo que hace esa criatura?\nSe te mete dentro. Te hace querer"
        " cosas que no elegiste.\nYo la custodié tres días. Tres. Y todavía"
        " sueño con ella.",
    ], [
        boton("b_mentira", "Eso no es cierto.",
              callar(), voz("g1_05"),
              coro("Nosotros no la robamos. La apagamos. Hay una diferencia, y "
                   "algun dia me lo van a agradecer."),
              accion_dialogo("eclipse")),
    ]),

    pagina("eclipse", "El Eclipse", [
        "Nosotros no la robamos. La apagamos.\nHay una diferencia, y algún día"
        " me lo van a agradecer.",
    ], [
        boton("b_apartate", "Apártate.",
              callar(), voz("g1_06"),
              coro("Pero ustedes no lo van a entender. Nunca entienden. "
                   "Mightyena — enseñales lo que hay al otro lado del bosque."),
              REMATE_ID, REMATE),
    ]),
]


def validar_comandos():
    """Comprueba el JSON de cada tellraw antes de escribir nada.

    Un tellraw mal formado no da error al importar el preset: el boton
    simplemente no hace nada, y eso se descubre con el grupo delante. Mas vale
    que reviente aqui.
    """
    import json
    revisados = 0
    def recorrer(nodo):
        nonlocal revisados
        if isinstance(nodo, dict):
            cmd = nodo.get(b"Cmd")
            if cmd is not None and nodo.get(b"Type", Tag(0, b"")).v == b"COMMAND":
                texto = cmd.v.decode("utf-8")
                if texto.startswith("/tellraw"):
                    # El JSON es todo lo que va tras el selector.
                    json.loads(texto.split("] ", 1)[1])
                    revisados += 1
                elif texto.startswith("/title") and " title " in texto or " subtitle " in texto:
                    trozo = texto.split(" title ", 1)[-1].split(" subtitle ", 1)[-1]
                    if trozo.startswith("{"):
                        json.loads(trozo); revisados += 1
            for v in nodo.values():
                recorrer(v)
        elif isinstance(nodo, Tag):
            recorrer(nodo.v)
        elif isinstance(nodo, tuple) and len(nodo) == 2:
            recorrer(nodo[1])
        elif isinstance(nodo, list):
            for v in nodo:
                recorrer(v)
    for p in DIALOGOS:
        recorrer(p)
    recorrer(REMATE)
    return revisados


def main(entrada, salida):
    n = validar_comandos()
    print(f"   {n} comandos con JSON validados, 0 malos")
    d = gzip.decompress(open(entrada, "rb").read())
    r = Lector(d)
    tipo_raiz = r._u(">b", 1)
    nombre_raiz = r.cadena()
    raiz = r.valor(tipo_raiz)

    datos = raiz[b"data"].v
    datos[b"DialogData"] = Tag(COMPOUND, {
        b"DialogDataSet": Tag(LIST, (COMPOUND, DIALOGOS))})

    # Sin esto los botones con comando no tienen permiso para ejecutarlos.
    datos[b"ActionData"].v[b"ActionPermissionLevel"] = Tag(INT, 4)

    # Al acercarse suena su primera linea y se quita la pantalla de comercio:
    # un guardian del Eclipse no le vende nada a nadie.
    ev = datos[b"ActionData"].v.get(b"ActionEventSet")
    if ev:
        oi = ev.v.get(b"ON_INTERACTION")
        if oi:
            it, items = oi.v
            limpio = [x for x in items
                      if x.get(b"Type") and x[b"Type"].v != b"OPEN_TRADING_SCREEN"]
            limpio.insert(0, accion_comando(
                "/playsound evento:voz.grum.g1_01 voice @a[tag=ev_participa] ~ ~ ~ 1000000 1"))
            limpio.insert(1, coro(
                "Alto ahi. Este bosque esta cerrado. Den la vuelta por donde vinieron."))
            oi.v = (it, limpio)

    w = Escritor()
    w.b += struct.pack(">b", tipo_raiz)
    w.cadena(nombre_raiz)
    w.valor(tipo_raiz, raiz)
    open(salida, "wb").write(gzip.compress(bytes(w.b)))

    print(f"   {salida}")
    print(f"   {len(DIALOGOS)} paginas de dialogo, 6 lineas de voz (g1_01 - g1_06)")
    for p in DIALOGOS:
        nb = len(p[b"Buttons"].v[1]) if b"Buttons" in p else 0
        print(f"     {p[b'Label'].v.decode():<14} {p[b'Name'].v.decode():<18} {nb} opcion(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
