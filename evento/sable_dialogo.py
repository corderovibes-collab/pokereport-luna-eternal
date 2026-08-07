# -*- coding: utf-8 -*-
"""Inserta el arbol de dialogos de Sable en su preset de Easy NPC.

Misma mecanica que Grum. La maquinaria de NBT se reutiliza de `oak_dialogo`.

QUIEN ES SABLE
--------------
Grum dudaba; Sable no, y no por ser mas malvado sino por algo peor: **Luna no
puede alcanzarlo**. Donde Grum la custodio tres dias y todavia suena con ella,
Sable la miro a los ojos y no sintio nada. Por eso lo eligieron a el para
apagarla — buscaron entre cientos hasta dar con alguien inmune.

Su linea `sa_05` es la que mueve la trama: el Eclipse no esta **guardando** a
Luna, la esta **midiendo**. Quieren aprender a hacer lo que ella hace sin
necesidad de que ella exista. De ahi sale el laboratorio de Vex.

DONDE ENCAJA
------------
    el grupo sube a la montana (senal 2, marcador en 1630 69 164)
        -> habla con Sable, plantado antes de la boca de la cueva
        -> Sable suelta a su Weavile
        -> entran a la cueva y tocan el cristal (1632 69 161)

El cristal esta DENTRO de la cueva, asi que su haz no se ve desde fuera: por eso
el aviso final dice explicitamente que esta al fondo.

Uso:
    python evento/sable_dialogo.py audit/sable.npc.nbt audit/sable_con_dialogo.npc.nbt
"""
import gzip
import struct
import sys

from oak_dialogo import (COMPOUND, INT, LIST, Escritor, Lector, Tag,
                         accion_comando, accion_dialogo, boton, pagina)

# Numero de guardian, para que el motor sepa a quien rematar. Ver GUARDIANES en
# build_dp.py.
GUARDIAN = 2

# `sa_06` dura 4,24 s. Cinco segundos deja que termine sin dejar un silencio
# raro. Grum usa ocho porque su ultima linea es mas larga.
ESPERA = 5


def voz(clip):
    return accion_comando(
        f"/playsound evento:voz.sable.{clip} voice @a[tag=ev_participa] ~ ~ ~ 1000000 1")


def callar():
    return accion_comando("/stopsound @a[tag=ev_participa] voice")


def coro(texto):
    """Lo que ve todo el grupo, no solo quien esta hablando con el NPC."""
    # Barra + n como DOS caracteres: es un escape del JSON del tellraw, no un
    # salto de linea real. Con un salto de verdad el comando no compila.
    NL = chr(92) + "n"
    seguro = texto.replace('"', "'")
    return accion_comando(
        '/tellraw @a[tag=ev_participa] ["",{"text":"' + NL + '  SABLE DEL ECLIPSE  ","color":"aqua","bold":true},'
        '{"text":"' + seguro + NL + '","color":"gray"}]')


# El remate no se dispara aqui: el boton solo deja dos numeros y el reloj del
# datapack hace el resto cuando la voz ya ha terminado.
REMATE_ID = accion_comando(f"/scoreboard players set #ev ev_reto_id {GUARDIAN}")
REMATE = accion_comando(f"/scoreboard players set #ev ev_reto {ESPERA}")


DIALOGOS = [
    pagina("default", "El especialista", [
        "No debieron subir tanto.\nAquí arriba el aire engaña, y la caída es larga.",
    ], [
        boton("b_otro", "¿Otro del Eclipse?",
              callar(), voz("sa_02"),
              coro("Sable. Y se exactamente quienes son: los que Grum dejo "
                   "pasar. Yo no cometo ese error."),
              accion_dialogo("quien")),
    ]),

    pagina("quien", "Sable", [
        "Sable.\nY sé exactamente quiénes son: los que Grum dejó pasar.\nYo no"
        " cometo ese error.",
    ], [
        boton("b_bajarla", "Vamos a bajarla de ahí.",
              callar(), voz("sa_03"),
              coro("Grum les conto lo que sintio, verdad? Los tres dias. Que "
                   "todavia suena con ella. Yo la mire a los ojos y no senti "
                   "absolutamente nada."),
              accion_dialogo("nada")),
    ]),

    # El nucleo del personaje: se define por contraste con Grum, y el contraste
    # es lo que da miedo.
    pagina("nada", "Nada", [
        "Grum les contó lo que sintió, ¿verdad? Los tres días. Que todavía"
        " sueña con ella.\nYo la miré a los ojos y no sentí absolutamente nada.",
    ], [
        boton("b_bien", "¿Y eso te parece bien?",
              callar(), voz("sa_04"),
              coro("Me parece util. Por eso me eligieron a mi para apagarla. "
                   "Buscaron entre cientos hasta encontrar a alguien a quien no "
                   "pudiera alcanzar. Me encontraron."),
              accion_dialogo("elegido")),
    ]),

    pagina("elegido", "El elegido", [
        "Me parece útil.\nPor eso me eligieron a mí para apagarla. Buscaron"
        " entre cientos hasta encontrar a alguien a quien no pudiera alcanzar."
        "\nMe encontraron.",
    ], [
        boton("b_haciendo", "¿Qué le están haciendo?",
              callar(), voz("sa_05"),
              coro("No la estamos guardando. La estamos midiendo. Y cuando "
                   "terminemos, sabremos hacer lo que ella hace sin necesidad "
                   "de que ella exista."),
              accion_dialogo("midiendo")),
    ]),

    # La revelacion que apunta al laboratorio.
    pagina("midiendo", "La medida", [
        "No la estamos guardando. La estamos midiendo.\nY cuando terminemos,"
        " sabremos hacer lo que ella hace sin necesidad de que ella exista.",
    ], [
        boton("b_apartate", "Apártate.",
              callar(), voz("sa_06"),
              coro("Ya hable mas de lo que debia. Weavile. Que no lleguen a la "
                   "cumbre."),
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
                "/playsound evento:voz.sable.sa_01 voice @a[tag=ev_participa] ~ ~ ~ 1000000 1"))
            limpio.insert(1, coro(
                "No debieron subir tanto. Aqui arriba el aire engana, y la "
                "caida es larga."))
            oi.v = (it, limpio)

    w = Escritor()
    w.b += struct.pack(">b", tipo_raiz)
    w.cadena(nombre_raiz)
    w.valor(tipo_raiz, raiz)
    open(salida, "wb").write(gzip.compress(bytes(w.b)))

    print(f"   {salida}")
    print(f"   {len(DIALOGOS)} paginas, 6 lineas de voz (sa_01 - sa_06)")
    for p in DIALOGOS:
        nb = len(p[b"Buttons"].v[1]) if b"Buttons" in p else 0
        print(f"     {p[b'Label'].v.decode():<12} {p[b'Name'].v.decode():<20} {nb} opcion(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
