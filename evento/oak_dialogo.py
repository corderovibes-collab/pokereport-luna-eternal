# -*- coding: utf-8 -*-
"""Inserta el arbol de dialogos de Oak en su preset de Easy NPC.

El preset se exporta desde el juego en NBT comprimido. Aqui se lee conservando
los tipos (un byte y un int no son lo mismo y el mod los distingue), se le anade
`DialogData`, y se vuelve a escribir. Todo lo demas —skin, nombre, variante,
atributos— se copia tal cual: la idea es no pisar nada de lo configurado a mano.

El esquema de dialogo sale del preset `professor_quiz` que trae el propio mod.

Uso:  python evento/oak_dialogo.py entrada.npc.nbt salida.npc.nbt
"""
import gzip
import struct
import sys

# --- lectura y escritura de NBT conservando tipos -------------------------
END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE = 0, 1, 2, 3, 4, 5, 6
BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = 7, 8, 9, 10, 11, 12


class Tag:
    __slots__ = ("t", "v")

    def __init__(self, t, v):
        self.t, self.v = t, v


class Lector:
    def __init__(self, d):
        self.d, self.i = d, 0

    def _u(self, f, n):
        v = struct.unpack_from(f, self.d, self.i)[0]
        self.i += n
        return v

    def cadena(self):
        n = self._u(">H", 2)
        v = self.d[self.i:self.i + n]          # bytes crudos, sin decodificar
        self.i += n
        return v

    def valor(self, t):
        if t == BYTE:   return self._u(">b", 1)
        if t == SHORT:  return self._u(">h", 2)
        if t == INT:    return self._u(">i", 4)
        if t == LONG:   return self._u(">q", 8)
        if t == FLOAT:  return self._u(">f", 4)
        if t == DOUBLE: return self._u(">d", 8)
        if t == STRING: return self.cadena()
        if t == BYTE_ARRAY:
            n = self._u(">i", 4); v = self.d[self.i:self.i + n]; self.i += n; return v
        if t == INT_ARRAY:
            n = self._u(">i", 4); return [self._u(">i", 4) for _ in range(n)]
        if t == LONG_ARRAY:
            n = self._u(">i", 4); return [self._u(">q", 8) for _ in range(n)]
        if t == LIST:
            it = self._u(">b", 1); n = self._u(">i", 4)
            return (it, [self.valor(it) for _ in range(n)])
        if t == COMPOUND:
            o = {}
            while True:
                tt = self._u(">b", 1)
                if tt == END:
                    return o
                # El nombre va antes que el valor en el fichero. Ojo con
                # escribirlo en una sola linea: Python evalua la derecha
                # primero y leeria el valor antes que el nombre.
                nombre = self.cadena()
                o[nombre] = Tag(tt, self.valor(tt))
        raise ValueError(f"tipo NBT desconocido: {t}")


class Escritor:
    def __init__(self):
        self.b = bytearray()

    def cadena(self, s):
        e = s if isinstance(s, bytes) else s.encode("utf-8")
        self.b += struct.pack(">H", len(e)) + e

    def valor(self, t, v):
        if t == BYTE:   self.b += struct.pack(">b", v)
        elif t == SHORT: self.b += struct.pack(">h", v)
        elif t == INT:   self.b += struct.pack(">i", v)
        elif t == LONG:  self.b += struct.pack(">q", v)
        elif t == FLOAT: self.b += struct.pack(">f", v)
        elif t == DOUBLE: self.b += struct.pack(">d", v)
        elif t == STRING: self.cadena(v)
        elif t == BYTE_ARRAY: self.b += struct.pack(">i", len(v)) + bytes(v)
        elif t == INT_ARRAY:
            self.b += struct.pack(">i", len(v))
            for x in v: self.b += struct.pack(">i", x)
        elif t == LONG_ARRAY:
            self.b += struct.pack(">i", len(v))
            for x in v: self.b += struct.pack(">q", x)
        elif t == LIST:
            it, items = v
            self.b += struct.pack(">b", it) + struct.pack(">i", len(items))
            for x in items: self.valor(it, x)
        elif t == COMPOUND:
            for k, tag in v.items():
                self.b += struct.pack(">b", tag.t)
                self.cadena(k)
                self.valor(tag.t, tag.v)
            self.b += struct.pack(">b", END)
        else:
            raise ValueError(t)


# --- ayudas para construir el dialogo --------------------------------------
def S(s):   return Tag(STRING, s.encode("utf-8"))
def C(**kw): return {k.encode("utf-8"): v for k, v in kw.items()}


def accion_dialogo(destino):
    return C(Cmd=S(destino), Type=S("OPEN_NAMED_DIALOG"))


def accion_comando(cmd):
    return C(Cmd=S(cmd), Type=S("COMMAND"))


def boton(etiqueta, texto, *acciones):
    return C(Label=S(etiqueta), Name=S(texto),
             Actions=Tag(LIST, (COMPOUND, list(acciones))))


def pagina(etiqueta, titulo, textos, botones=()):
    d = C(Label=S(etiqueta), Name=S(titulo),
          Texts=Tag(LIST, (COMPOUND, [C(Text=S(t)) for t in textos])))
    if botones:
        d[b"Buttons"] = Tag(LIST, (COMPOUND, list(botones)))
    return d


# --- el arbol de Oak --------------------------------------------------------
#
# Ramifica de verdad: la pregunta «¿Le miro a usted? ¿Como?» existe solo para
# plantar el giro del Acto V sin destriparlo. Quien la haga entendera el final;
# quien no, se llevara la sorpresa entera.
#
# Cada boton lleva su `playsound`: al pulsarlo suena la linea de Oak con su voz
# clonada mientras se lee el texto. Las voces ya viajan en Evento-RP.zip.
#
# Ojo con los comandos: Easy NPC bloquea `function` y `execute` por seguridad
# (ver `unsafeNpcCommands` en security.cfg). Por eso el rastreador se entrega
# con un `give` directo en vez de llamar a la funcion del datapack.

def voz(clip):
    return accion_comando(f"/playsound evento:voz.oak.{clip} voice @a[tag=ev_participa] ~ ~ ~ 1000000 1")


def callar():
    return accion_comando("/stopsound @a[tag=ev_participa] voice")


def coro(texto):
    """Lo que ve TODO el grupo, no solo quien habla con Oak.

    La interfaz de dialogo es del cliente que interactua y no se puede duplicar,
    asi que se le da la vuelta: el que habla conduce la escena y los demas la
    reciben por chat y por voz. En un evento en grupo eso funciona mejor que una
    pantalla compartida, porque nadie se queda mirando la espalda de otro.
    """
    # El salto se escribe como los DOS caracteres barra + n: es un escape dentro
    # del JSON del tellraw, no un salto de linea de verdad. Escribirlo como salto
    # real rompe el comando.
    NL = chr(92) + "n"
    seguro = texto.replace('"', "'")
    return accion_comando(
        '/tellraw @a[tag=ev_participa] ["",{"text":"' + NL + '  PROFESOR OAK  ","color":"gold","bold":true},'
        '{"text":"' + seguro + NL + '","color":"white"}]')


def titular():
    return accion_comando(
        '/title @a times 4 60 12')


# El rastreador nace ya apuntando a la senal 1.
#
# Antes salia sin destino, y una brujula sin `lodestone_tracker` apunta al
# spawn del mundo. Le ponia el rumbo el Acto II al arrancar, asi que durante un
# segundo apuntaba mal — y si alguien hablaba con Oak fuera de secuencia (un
# admin, al que el cerrojo no frena) se quedaba con una brujula rota para
# siempre, sin ninguna pista de por que.
#
# Naciendo apuntada, el objeto es correcto en cualquier orden. `s1_marcar` lo
# vuelve a entregar igual al arrancar el acto; entregarlo dos veces no molesta.
#
# `tracked:false` evita que Minecraft exija una piedra iman de verdad ahi.
RASTREADOR = (
    "/give @p minecraft:compass["
    "custom_name='{\"text\":\"Rastreador de energia\",\"color\":\"aqua\",\"italic\":false}',"
    "lore=['{\"text\":\"Lo armo el Profesor Oak anoche.\",\"color\":\"gray\",\"italic\":true}',"
    "'{\"text\":\"Apunta hacia Luna.\",\"color\":\"dark_gray\",\"italic\":true}'],"
    "enchantment_glint_override=true,"
    "minecraft:lodestone_tracker={target:{pos:[I;1887,64,255],"
    "dimension:\"minecraft:overworld\"},tracked:false}]"
)

DIALOGOS = [
    pagina("default", "La llamada", [
        "Entrenadores. Escúchenme bien.\nLo que les voy a contar no está en ninguna Pokédex.",
    ], [
        boton("b_escucho", "Le escuchamos, profesor.",
              callar(), voz("a1_02"),
              coro("Hace tres semanas detecte una lectura de energia que no correspondia a ninguna especie conocida. Ni una sola. Fui a verla yo mismo."),
              accion_dialogo("historia")),
    ]),

    pagina("historia", "La lectura", [
        "Hace tres semanas detecté una lectura de energía que no correspondía"
        " a ninguna especie conocida. Ni una sola.\nFui a verla yo mismo,"
        " convencido de que era un fallo del equipo.",
    ], [
        boton("b_yque", "¿Y qué era?",
              callar(), voz("a1_03"),
              coro("Era una Pokemon. Pequena, tranquila... y me miro como si me conociera de toda la vida. La llame Luna."),
              accion_dialogo("encuentro")),
    ]),

    pagina("encuentro", "El encuentro", [
        "No lo era.\nEra una Pokémon. Pequeña, tranquila… y me miró como si"
        " me conociera de toda la vida.\nLa llamé Luna.",
    ], [
        boton("b_donde", "¿Dónde está ahora?",
              callar(), voz("a1_04"),
              coro("Iba a estudiarla al dia siguiente. No llegue a tiempo. El Equipo Eclipse se la llevo."),
              accion_dialogo("perdida")),
    ]),

    pagina("perdida", "La pérdida", [
        "Iba a estudiarla al día siguiente. No llegué a tiempo.\nEl Equipo"
        " Eclipse se la llevó.",
    ], [
        boton("b_vamos", "Vamos a traerla de vuelta.",
              callar(), voz("a1_05"),
              coro("Yo ya estoy viejo para esto, muchachos. Ustedes no. Necesito que me ayuden a traerla de vuelta."),
              accion_dialogo("rastreador")),
    ]),

    pagina("rastreador", "El rastreador", [
        "Yo ya estoy viejo para esto, muchachos. Ustedes no.\nTomen el"
        " rastreador de energía: lo armé anoche con lo que tenía. No es gran"
        " cosa, pero apunta hacia ella.\nVayan todos juntos. Y no se separen.",
    ], [
        boton("b_acepto", "Cuente conmigo.",
              callar(), voz("a1_06"),
              coro("Tomen. Es un rastreador de energia, lo arme anoche con lo que tenia. No es gran cosa, pero apunta hacia ella. Siganlo."),
              accion_comando(RASTREADOR),
              # Cierra el Acto I. Antes el motor lo deducia viendo una brujula
              # en el inventario, y eso saltaba con cualquier brujula.
              accion_comando("/scoreboard players set #ev ev_oak_listo 1")),
    ]),
]


def main(entrada, salida):
    d = gzip.decompress(open(entrada, "rb").read())
    r = Lector(d)
    tipo_raiz = r._u(">b", 1)
    nombre_raiz = r.cadena()
    raiz = r.valor(tipo_raiz)

    datos = raiz[b"data"].v
    datos[b"DialogData"] = Tag(COMPOUND, {
        b"DialogDataSet": Tag(LIST, (COMPOUND, DIALOGOS))})

    # Sin esto los botones con comando no tienen permiso para ejecutarlos.
    acc = datos[b"ActionData"].v
    acc[b"ActionPermissionLevel"] = Tag(INT, 4)

    # Al hablarle suena su primera linea con voz, y de paso se quita la
    # pantalla de comercio: Oak no vende nada.
    ev = acc.get(b"ActionEventSet")
    if ev:
        oi = ev.v.get(b"ON_INTERACTION")
        if oi:
            it, items = oi.v
            limpio = [x for x in items
                      if x.get(b"Type") and x[b"Type"].v != b"OPEN_TRADING_SCREEN"]
            limpio.insert(0, accion_comando(
                "/playsound evento:voz.oak.a1_01 voice @a[tag=ev_participa] ~ ~ ~ 1000000 1"))
            limpio.insert(1, coro(
                "Entrenadores. Escuchenme bien. Lo que les voy a contar no esta "
                "en ninguna Pokedex."))
            oi.v = (it, limpio)

    w = Escritor()
    w.b += struct.pack(">b", tipo_raiz)
    w.cadena(nombre_raiz)
    w.valor(tipo_raiz, raiz)
    open(salida, "wb").write(gzip.compress(bytes(w.b)))

    print(f"   {salida}")
    print(f"   {len(DIALOGOS)} páginas de diálogo")
    for p in DIALOGOS:
        nb = len(p[b"Buttons"].v[1]) if b"Buttons" in p else 0
        print(f"     {p[b'Label'].v.decode():<12} {p[b'Name'].v.decode():<18} {nb} opcion(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
