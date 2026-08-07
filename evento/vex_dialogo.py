# -*- coding: utf-8 -*-
"""Inserta el arbol de dialogos de la Doctora Vex en su preset de Easy NPC.

Siete paginas en vez de las cinco de los guardianes: aqui es donde se paga lo
que el grupo viene arrastrando desde el bosque.

QUIEN ES VEX
------------
No es una cientifica malvada. Es alguien que **lleva dos anos fracasando** y lo
sabe con precision decimal. Midio lo que hace Luna —doscientas once sesiones—
y tiene la formula exacta. No funciona, porque lo que Luna hace no se emite: se
da. Y algo que se da solo se puede recibir, nunca fabricar.

LAS DOS LINEAS QUE SOSTIENEN EL EVENTO
--------------------------------------
`vx_02` contesta lo que Nix dejo en el aire:

    "No esta encerrada. La puerta lleva abierta desde el segundo dia."

`vx_06` no contesta nada, y por eso funciona:

    "Ninguno de ustedes ha perdido lo suficiente para entender la respuesta."

Ahi esta el Acto V. Vex no quiere copiar a Luna por poder: quiere alcanzar a
alguien. Y la razon de que Luna se quedara es que, de todo el laboratorio, Vex
era quien mas la necesitaba. Eso NO se dice aqui.

DONDE ENCAJA
------------
    Acto IV -> el laboratorio (1084 66 530)
        -> Vex espera en 1800 80 569
        -> suelta a su Hydreigon
        -> el cristal (1796 80 568) se encendio al arrancar el acto
        -> ganada la incursion, cae Vex y empieza el Acto V

Uso:
    python evento/vex_dialogo.py audit/vex.npc.nbt audit/vex_con_dialogo.npc.nbt
"""
import gzip
import struct
import sys

from oak_dialogo import (COMPOUND, INT, LIST, Escritor, Lector, Tag,
                         accion_comando, accion_dialogo, boton, pagina)

# Cuarto "guardian" a efectos del remate. Ver GUARDIANES en build_dp.py.
GUARDIAN = 4

# `vx_07` dura 7,04 s.
ESPERA = 8

# Barra + n como DOS caracteres: es un escape del JSON, no un salto real.
NL = chr(92) + "n"


def voz(clip):
    return accion_comando(
        f"/playsound evento:voz.vex.{clip} voice @a[tag=ev_participa] ~ ~ ~ 1000000 1")


def callar():
    return accion_comando("/stopsound @a[tag=ev_participa] voice")


def coro(texto):
    """Lo que ve todo el grupo, no solo quien esta hablando con ella."""
    seguro = texto.replace('"', "'")
    return accion_comando(
        '/tellraw @a[tag=ev_participa] ["",{"text":"' + NL + '  DOCTORA VEX  ","color":"light_purple","bold":true},'
        '{"text":"' + seguro + NL + '","color":"gray"}]')


REMATE_ID = accion_comando(f"/scoreboard players set #ev ev_reto_id {GUARDIAN}")
REMATE = accion_comando(f"/scoreboard players set #ev ev_reto {ESPERA}")


DIALOGOS = [
    pagina("default", "La doctora", [
        "Llegaron antes de lo que calculé." + NL + "Eso también es un dato.",
    ], [
        boton("b_donde", "¿Dónde está Luna?",
              callar(), voz("vx_02"),
              coro("Aqui. Siempre estuvo aqui. Y antes de que lo pregunten: no "
                   "esta encerrada. La puerta lleva abierta desde el segundo dia."),
              accion_dialogo("puerta")),
    ]),

    # La respuesta a lo que Nix dejo caer: Luna pudo irse y no lo hizo.
    pagina("puerta", "La puerta abierta", [
        "Aquí. Siempre estuvo aquí." + NL +
        "Y antes de que lo pregunten: no está encerrada." + NL +
        "La puerta lleva abierta desde el segundo día.",
    ], [
        boton("b_hiciste", "¿Qué le hiciste?",
              callar(), voz("vx_03"),
              coro("Medirla. Doscientas once sesiones. Se cuanto pesa lo que "
                   "hace, a que velocidad viaja y cuanto tarda en alcanzar a "
                   "alguien que no quiere ser alcanzado."),
              accion_dialogo("medir")),
    ]),

    pagina("medir", "Doscientas once sesiones", [
        "Medirla. Doscientas once sesiones." + NL +
        "Sé cuánto pesa lo que hace, a qué velocidad viaja y cuánto tarda en"
        " alcanzar a alguien que no quiere ser alcanzado.",
    ], [
        boton("b_nosepuede", "Eso no se puede medir.",
              callar(), voz("vx_04"),
              coro("Se puede. Medirlo no era lo dificil. Lo dificil es que al "
                   "reproducirlo no funciona. Tengo la formula exacta y lo que "
                   "sale de ella no sirve para nada."),
              accion_dialogo("formula")),
    ]),

    pagina("formula", "La fórmula", [
        "Se puede. Medirlo no era lo difícil." + NL +
        "Lo difícil es que al reproducirlo no funciona." + NL +
        "Tengo la fórmula exacta y lo que sale de ella no sirve para nada.",
    ], [
        boton("b_porque", "¿Por qué no funciona?",
              callar(), voz("vx_05"),
              coro("Porque ella lo da. No lo emite: lo da. Y algo que se da no "
                   "se fabrica, solo se recibe. Llevo dos anos negandome a "
                   "aceptar esa frase."),
              accion_dialogo("se_da")),
    ]),

    # El nucleo del personaje: lo entendio hace mucho y no lo acepta.
    pagina("se_da", "Se da", [
        "Porque ella lo da. No lo emite: lo da." + NL +
        "Y algo que se da no se fabrica, solo se recibe." + NL +
        "Llevo dos años negándome a aceptar esa frase.",
    ], [
        boton("b_paraque", "¿Y para qué querías copiarlo?",
              callar(), voz("vx_06"),
              coro("Esa pregunta no se la voy a responder. Ninguno de ustedes "
                   "ha perdido lo suficiente para entender la respuesta."),
              accion_dialogo("perdido")),
    ]),

    # La que NO contesta. Aqui esta plantado el Acto V.
    pagina("perdido", "Lo que no dice", [
        "Esa pregunta no se la voy a responder." + NL +
        "Ninguno de ustedes ha perdido lo suficiente para entender la respuesta.",
    ], [
        boton("b_llevarnosla", "Vamos a llevárnosla.",
              callar(), voz("vx_07"),
              coro("Entonces demuestren que la merecen mas que yo. Y les "
                   "advierto una cosa: yo la necesito bastante."),
              REMATE_ID, REMATE),
    ]),
]


def validar_comandos():
    """Comprueba el JSON de cada tellraw antes de escribir nada."""
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
    datos[b"ActionData"].v[b"ActionPermissionLevel"] = Tag(INT, 4)

    ev = datos[b"ActionData"].v.get(b"ActionEventSet")
    if ev:
        oi = ev.v.get(b"ON_INTERACTION")
        if oi:
            it, items = oi.v
            limpio = [x for x in items
                      if x.get(b"Type") and x[b"Type"].v != b"OPEN_TRADING_SCREEN"]
            limpio.insert(0, accion_comando(
                "/playsound evento:voz.vex.vx_01 voice @a[tag=ev_participa] ~ ~ ~ 1000000 1"))
            limpio.insert(1, coro(
                "Llegaron antes de lo que calcule. Eso tambien es un dato."))
            oi.v = (it, limpio)

    w = Escritor()
    w.b += struct.pack(">b", tipo_raiz)
    w.cadena(nombre_raiz)
    w.valor(tipo_raiz, raiz)
    open(salida, "wb").write(gzip.compress(bytes(w.b)))

    print(f"   {salida}")
    print(f"   {len(DIALOGOS)} paginas, 7 lineas de voz (vx_01 - vx_07)")
    for p in DIALOGOS:
        nb = len(p[b"Buttons"].v[1]) if b"Buttons" in p else 0
        print(f"     {p[b'Label'].v.decode():<14} {p[b'Name'].v.decode():<24} {nb} opcion(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
