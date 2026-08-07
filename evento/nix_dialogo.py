# -*- coding: utf-8 -*-
"""Inserta el arbol de dialogos de Nix en su preset de Easy NPC.

Misma mecanica que Grum y Sable. La maquinaria de NBT se reutiliza de
`oak_dialogo`.

QUIEN ES NIX
------------
Los tres guardianes son tres formas distintas de sostener lo mismo:

    Grum    culpa      cree que fue piedad, pero no duerme
    Sable   certeza    Luna no puede alcanzarlo, y por eso lo eligieron
    Nix     miedo      y no de los jugadores

Nix esta aterrado por lo que hay **detras** de el, no por lo que tiene delante.
Pelea porque le toca, pero quiere que ganen: su ultima linea es casi desearles
suerte.

Su `ni_05` planta el giro del Acto V sin gastarlo — **Luna pudo haberse ido el
primer dia y nunca lo intento**. No se explica nada; se deja caer, y el grupo
llega al laboratorio con esa pregunta encima.

DONDE ENCAJA
------------
    el grupo llega a la costa (senal 3, marcador en 1613 63 557)
        -> habla con Nix, plantado en 1621 63 550
        -> Nix suelta a su Sharpedo
        -> tocan el cristal (1625 63 548) y pelean la incursion
        -> ganada la tercera senal, arranca el Acto III

Uso:
    python evento/nix_dialogo.py audit/nix.npc.nbt audit/nix_con_dialogo.npc.nbt
"""
import gzip
import struct
import sys

from oak_dialogo import (COMPOUND, INT, LIST, Escritor, Lector, Tag,
                         accion_comando, accion_dialogo, boton, pagina)

# Numero de guardian, para que el motor sepa a quien rematar. Ver GUARDIANES en
# build_dp.py.
GUARDIAN = 3

# `ni_06` dura 4,88 s. Seis segundos dejan que termine sin silencio raro.
ESPERA = 6

# El salto de linea de los textos de pagina se escribe como los DOS caracteres
# barra + n. Easy NPC los interpreta al mostrar el dialogo; un salto real
# rompe el NBT.
NL = chr(92) + "n"


def voz(clip):
    return accion_comando(
        f"/playsound evento:voz.nix.{clip} voice @a[tag=ev_participa] ~ ~ ~ 1000000 1")


def callar():
    return accion_comando("/stopsound @a[tag=ev_participa] voice")


def coro(texto):
    """Lo que ve todo el grupo, no solo quien esta hablando con el NPC."""
    seguro = texto.replace('"', "'")
    return accion_comando(
        '/tellraw @a[tag=ev_participa] ["",{"text":"' + NL + '  NIX DEL ECLIPSE  ","color":"dark_aqua","bold":true},'
        '{"text":"' + seguro + NL + '","color":"gray"}]')


# El remate no se dispara aqui: el boton deja dos numeros y el reloj del
# datapack remata cuando la voz ya ha terminado.
REMATE_ID = accion_comando(f"/scoreboard players set #ev ev_reto_id {GUARDIAN}")
REMATE = accion_comando(f"/scoreboard players set #ev ev_reto {ESPERA}")


DIALOGOS = [
    pagina("default", "El ultimo", [
        "Alto." + NL + "El agua de aquí no es segura, y yo tampoco." + NL +
        "Váyanse mientras puedan.",
    ], [
        boton("b_quien", "¿Y tú quién eres?",
              callar(), voz("ni_02"),
              coro("Nix. El ultimo antes del laboratorio. Grum les dio un sermon "
                   "y Sable les dio una leccion. Yo solo quiero que se den la vuelta."),
              accion_dialogo("quien")),
    ]),

    pagina("quien", "Nix", [
        "Nix. El último antes del laboratorio." + NL +
        "Grum les dio un sermón y Sable les dio una lección." + NL +
        "Yo solo quiero que se den la vuelta.",
    ], [
        boton("b_nonos", "No nos vamos a ir.",
              callar(), voz("ni_03"),
              coro("Ya lo se. Por eso llevo tres noches sin dormir. Y no es por "
                   "ustedes: es por lo que hay al otro lado de esa puerta."),
              accion_dialogo("puerta")),
    ]),

    pagina("puerta", "La puerta", [
        "Ya lo sé. Por eso llevo tres noches sin dormir." + NL +
        "Y no es por ustedes: es por lo que hay al otro lado de esa puerta.",
    ], [
        boton("b_queay", "¿Qué hay al otro lado?",
              callar(), voz("ni_04"),
              coro("La doctora Vex termino de medirla. Dice que ya sabe como se "
                   "hace, que ya no la necesita. Y lo peor de todo es que le creo."),
              accion_dialogo("vex")),
    ]),

    pagina("vex", "La doctora Vex", [
        "La doctora Vex terminó de medirla." + NL +
        "Dice que ya sabe cómo se hace, que ya no la necesita." + NL +
        "Y lo peor de todo es que le creo.",
    ], [
        boton("b_miedo", "¿Y por qué te da tanto miedo?",
              callar(), voz("ni_05"),
              coro("No es eso. Es que hay algo que no le cuadra a nadie. Esa "
                   "Pokemon pudo haberse ido el primer dia. Pudo. Nunca lo "
                   "intento. Ni una sola vez. Se quedo."),
              accion_dialogo("sequedo")),
    ]),

    # La pagina que planta el giro del Acto V. No se explica nada: se deja caer
    # y el grupo entra al laboratorio con la pregunta encima.
    pagina("sequedo", "Se quedo", [
        "No es eso. Es que hay algo que no le cuadra a nadie." + NL +
        "Esa Pokémon pudo haberse ido el primer día. Pudo." + NL +
        "Nunca lo intentó. Ni una sola vez." + NL + "Se quedó.",
    ], [
        boton("b_apartate", "Apártate.",
              callar(), voz("ni_06"),
              coro("Ojala alguno de ustedes averigue por que. Sharpedo, al agua. "
                   "Que no lleguen a esa puerta."),
              REMATE_ID, REMATE),
    ]),
]


def validar_comandos():
    """Comprueba el JSON de cada tellraw antes de escribir nada.

    Un tellraw mal formado no da error al importar: el boton simplemente no hace
    nada, y eso se descubre con el grupo delante.
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
                    json.loads(texto.split("] ", 1)[1])
                    revisados += 1
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
    return revisados


def main(entrada, salida):
    print(f"   {validar_comandos()} comandos con JSON validados, 0 malos")
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

    ev = datos[b"ActionData"].v.get(b"ActionEventSet")
    if ev:
        oi = ev.v.get(b"ON_INTERACTION")
        if oi:
            it, items = oi.v
            limpio = [x for x in items
                      if x.get(b"Type") and x[b"Type"].v != b"OPEN_TRADING_SCREEN"]
            limpio.insert(0, accion_comando(
                "/playsound evento:voz.nix.ni_01 voice @a[tag=ev_participa] ~ ~ ~ 1000000 1"))
            limpio.insert(1, coro(
                "Alto. El agua de aqui no es segura, y yo tampoco. Vayanse "
                "mientras puedan."))
            oi.v = (it, limpio)

    w = Escritor()
    w.b += struct.pack(">b", tipo_raiz)
    w.cadena(nombre_raiz)
    w.valor(tipo_raiz, raiz)
    open(salida, "wb").write(gzip.compress(bytes(w.b)))

    print(f"   {salida}")
    print(f"   {len(DIALOGOS)} paginas, 6 lineas de voz (ni_01 - ni_06)")
    for p in DIALOGOS:
        nb = len(p[b"Buttons"].v[1]) if b"Buttons" in p else 0
        print(f"     {p[b'Label'].v.decode():<12} {p[b'Name'].v.decode():<20} {nb} opcion(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
