# -*- coding: utf-8 -*-
"""Genera el datapack motor del evento «El Rastro de Luna».

Se emite entero desde aqui en vez de mantener treinta ficheros sueltos: asi las
constantes (duraciones, numero de senales, digitos necesarios) viven en un solo
sitio y no hay forma de que una se quede desincronizada de otra.

Uso:  python evento/build_dp.py
"""
import json
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "build", "Evento-DP.zip")

# 48 = formato de datapack de 1.21.1
PACK_FORMAT = 48

# --- reglas del evento, todas juntas ---------------------------------------
SENALES_COMPLETO = 3          # senales del Acto II en modo normal
SENALES_CORTO = 2             # ... y en modo corto (se salta la costa)
DIGITOS_NECESARIOS = 4        # de las 6 misiones del Acto III
LIMITE_SENAL = 25 * 60        # 25 min: el guardian se rinde y Oak "recalibra"
LIMITE_CIFRADO = 40 * 60      # 40 min: Oak descifra el resto
# El Acto IV no lleva limite a proposito: es el climax, se le da lo que pida.

# En latino, igual que las voces: el guion se paso a "ustedes" y estos subtitulos
# se habian quedado en peninsular.
ACTOS = {
    1: ("LA LLAMADA", "El Profesor Oak los necesita"),
    2: ("LAS SENALES", "Sigan el rastreador"),
    3: ("EL CIFRADO", "Demuestren su oficio"),
    4: ("EL LABORATORIO", "Entren con cuidado"),
    5: ("EL REENCUENTRO", "Luna esta al otro lado"),
}

ficheros: dict[str, str] = {}


# Todos los marcadores del evento, sacados de donde se crean. `admin/reiniciar`
# los limpia a partir de estas listas para que anadir uno nuevo no vuelva a
# dejar restos colgados.
_OBJETIVOS_GLOBALES = ['ev_estado', 'ev_reloj', 'ev_senal', 'ev_senal_act', 'ev_codigo', 'ev_modo', 'ev_sys', 'ev_reto', 'ev_reto_id', 'ev_raid0', 'ev_raid', 'ev_raid_v', 'ev_oak', 'ev_oak_esp', 'ev_sig', 'ev_lab', 'ev_lab0', 'ev_lab_v', 'ev_luna', 'ev_fijar', 'ev_oak_listo', 'ev_esc', 'ev_esc_p', 'ev_esc_t', 'ev_cine_t', 'ev_sala', 'ev_sala_t']
_OBJETIVOS_JUGADOR = ['ev_unirse', 'ev_acto', 'ev_baliza', 'ev_m1', 'ev_m2', 'ev_m3', 'ev_m4', 'ev_m5', 'ev_m6', 'ev_p1', 'ev_p4', 'ev_p6']


def f(ruta: str, cuerpo: str) -> None:
    """Registra una mcfunction quitando la indentacion del literal."""
    lineas = [l[4:] if l.startswith("    ") else l for l in cuerpo.strip("\n").split("\n")]
    ficheros[f"data/evento/function/{ruta}.mcfunction"] = "\n".join(lineas) + "\n"


# ===========================================================================
#  Arranque
# ===========================================================================
f("cargar", f"""
    # La barra de la sala de espera. `add` falla sin consecuencias si ya existe,
    # que es lo normal en cada /reload; lo que importa es dejarla configurada.
    bossbar add evento:sala {{"text":"El Rastro de Luna"}}
    bossbar set evento:sala color purple
    bossbar set evento:sala style notched_10
    bossbar set evento:sala max 900
    bossbar set evento:sala visible false

    # Se ejecuta al cargar el mundo y en cada /reload.

    # --- marcadores globales (viven en el jugador falso #ev) ---
    scoreboard objectives add ev_sala dummy
    scoreboard objectives add ev_sala_t dummy
    scoreboard objectives add ev_estado dummy
    scoreboard objectives add ev_reloj dummy
    scoreboard objectives add ev_senal dummy
    scoreboard objectives add ev_senal_act dummy
    scoreboard objectives add ev_codigo dummy
    scoreboard objectives add ev_modo dummy
    scoreboard objectives add ev_sys dummy
    # Cuenta atras del remate de los guardianes. Easy NPC no puede llamar a
    # `function` ni a `schedule`, pero `scoreboard` si le pasa, asi que su
    # ultimo boton deja aqui los segundos y de que guardian se trata.
    scoreboard objectives add ev_reto dummy
    scoreboard objectives add ev_reto_id dummy
    # Vigilancia de la incursion: ev_raid0 es la marca tomada al armar la senal,
    # ev_raid el valor de ahora, ev_raid_v el interruptor, ev_oak el retardo de
    # la frase del profesor.
    scoreboard objectives add ev_raid0 dummy
    scoreboard objectives add ev_raid dummy
    scoreboard objectives add ev_raid_v dummy
    scoreboard objectives add ev_oak dummy
    scoreboard objectives add ev_oak_esp dummy
    # Retardo entre la frase de victoria de Oak y el anuncio de la senal siguiente.
    scoreboard objectives add ev_sig dummy
    # Vigilancia del cristal del laboratorio, aparte de la de las senales.
    scoreboard objectives add ev_lab dummy
    scoreboard objectives add ev_lab0 dummy
    scoreboard objectives add ev_lab_v dummy
    # Marcador del laboratorio activo (para el aviso de llegada).
    scoreboard objectives add ev_lab_m dummy
    # Cuenta atras entre la revelacion y la aparicion de Luna.
    scoreboard objectives add ev_luna dummy
    scoreboard objectives add ev_fijar dummy
    # Oak lo pone a 1 desde su ultimo boton para cerrar el Acto I.
    scoreboard objectives add ev_oak_listo dummy
    # trigger, no dummy: es lo unico que un jugador sin permisos puede usar
    scoreboard objectives add ev_unirse trigger
    scoreboard objectives add ev_esc dummy
    scoreboard objectives add ev_esc_p dummy
    scoreboard objectives add ev_esc_t dummy
    scoreboard objectives add ev_cine_t dummy

    # --- por jugador ---
    scoreboard objectives add ev_acto dummy
    scoreboard objectives add ev_baliza dummy
    scoreboard objectives add ev_m1 dummy
    scoreboard objectives add ev_m2 dummy
    scoreboard objectives add ev_m3 dummy
    scoreboard objectives add ev_m4 dummy
    scoreboard objectives add ev_m5 dummy
    scoreboard objectives add ev_m6 dummy

    # Contadores de los avances que hay que repetir varias veces.
    scoreboard objectives add ev_p1 dummy
    scoreboard objectives add ev_p4 dummy
    scoreboard objectives add ev_p6 dummy

    # Solo se inicializa lo que no exista: un /reload a mitad de evento no
    # puede tirar el progreso por la borda.
    execute unless score #ev ev_estado = #ev ev_estado run scoreboard players set #ev ev_estado 0
    execute unless score #ev ev_reloj = #ev ev_reloj run scoreboard players set #ev ev_reloj 0
    execute unless score #ev ev_senal = #ev ev_senal run scoreboard players set #ev ev_senal 0
    execute unless score #ev ev_senal_act = #ev ev_senal_act run scoreboard players set #ev ev_senal_act 0
    execute unless score #ev ev_codigo = #ev ev_codigo run scoreboard players set #ev ev_codigo 0
    execute unless score #ev ev_modo = #ev ev_modo run scoreboard players set #ev ev_modo 0
    scoreboard players set #ev ev_sys 0

    scoreboard players set #ev ev_cine_t 0
    execute unless score #ev ev_esc = #ev ev_esc run scoreboard players set #ev ev_esc 0
    execute unless score #ev ev_esc_p = #ev ev_esc_p run scoreboard players set #ev ev_esc_p 0
    execute unless score #ev ev_esc_t = #ev ev_esc_t run scoreboard players set #ev ev_esc_t 0

    tellraw @a[tag=ev_admin] {{"text":"[Evento] Motor cargado. /function evento:admin/ayuda","color":"dark_gray"}}
""")


# ===========================================================================
#  Reloj
# ===========================================================================
f("reloj", """
    # tick.json entra aqui 20 veces por segundo. Casi todo el trabajo se hace
    # una vez por segundo: comprobar condiciones 20 veces seguidas no cambia
    # nada y se nota en el rendimiento con gente conectada.
    # La sala va aqui y no en `segundo` a proposito: para retener a la gente hay
    # que reponerles la posicion en cada tick, no una vez por segundo.
    execute if score #ev ev_sala matches 1 run function evento:sala/retener

    scoreboard players add #ev ev_sys 1
    execute if score #ev ev_sys matches 20.. run function evento:segundo
""")

f("segundo", f"""
    scoreboard players set #ev ev_sys 0

    execute if score #ev ev_sala matches 1 run function evento:sala/latido

    # Quien haya pulsado el boton de la invitacion
    execute as @a[scores={{ev_unirse=1}}] run function evento:util/inscribir
    execute as @a[scores={{ev_unirse=2}}] run function evento:util/renunciar

    execute unless score #ev ev_cine_t matches 0 run function evento:cine/vigilar
    execute unless score #ev ev_senal_act matches 0 run function evento:senales/distancia
    execute unless score #ev ev_esc matches 0 run function evento:escenas/reloj

    # Va aqui arriba, ANTES del corte por evento parado, para poder ensayar la
    # escena de Grum sin tener que arrancar el evento entero.
    # `matches 1..` y no `unless matches 0`: si el marcador nunca se ha puesto
    # no tiene valor, y entonces `unless ... matches 0` daria cierto y esto se
    # pondria a restar hacia numeros negativos para siempre.
    execute if score #ev ev_reto matches 1.. run function evento:guardianes/cuenta
    execute if score #ev ev_oak_esp matches 1 run function evento:senales/oak_espera
    execute if score #ev ev_oak matches 1.. run function evento:senales/oak_cuenta
    execute if score #ev ev_sig matches 1.. run function evento:senales/sig_cuenta
    execute if score #ev ev_estado matches 0 run function evento:bloqueo/npcs
    execute if score #ev ev_raid_v matches 1.. run function evento:senales/vigilar_raid
    execute if score #ev ev_lab_v matches 1 run function evento:lab/vigilar_raid
    execute if score #ev ev_lab_m matches 1 run function evento:lab/distancia
    execute if score #ev ev_luna matches 1.. run function evento:lab/luna_cuenta
    execute if score #ev ev_fijar matches 1.. run function evento:lab/fijar_cuenta

    # Evento parado: no se hace nada mas.
    execute if score #ev ev_estado matches 0 run return 0

    scoreboard players add #ev ev_reloj 1

    # Quien entre a mitad del evento se pone al dia solo.
    execute as @a[tag=ev_participa] unless score @s ev_acto = #ev ev_estado run function evento:util/poner_al_dia

    # Mismo motivo que en actos/avanzar: si a2_reloj hace avanzar el acto, la
    # linea siguiente encajaria en el mismo segundo. Un acto por segundo, no dos.
    execute if score #ev ev_estado matches 1 run return run function evento:actos/a1_reloj
    execute if score #ev ev_estado matches 2 run return run function evento:actos/a2_reloj
    execute if score #ev ev_estado matches 3 run return run function evento:actos/a3_reloj
    execute if score #ev ev_estado matches 4 run return run function evento:actos/a4_reloj
    execute if score #ev ev_estado matches 5 run return run function evento:actos/a5_reloj
""")


# ===========================================================================
#  Cerrojo: todo colocado, pero nadie toca nada hasta que empiece
# ===========================================================================
#
# Los NPCs y los cristales viven en el mundo de forma permanente. Eso esta bien
# para la ambientacion pero es un problema el resto del tiempo: cualquiera que
# pase por el bosque puede hablar con Grum, oir la escena entera y destripar el
# evento, o peor, pelear la incursion antes de tiempo.
#
# Dos cerrojos distintos, porque son dos problemas distintos:
#
#   CRISTALES  El propio mod tiene un interruptor, `is_active`. Apagado, el
#              cristal se ve pero al tocarlo responde "The raid den is not
#              active right now". Es la via limpia, y `setblock` conserva el
#              jefe porque el tipo de bloque no cambia.
#
#              `can_reset=false` NO es opcional. Con el a true, el cristal se
#              recicla cada dos horas y **se cambia de jefe solo**: el de Sable
#              aparecio un dia con un Great Tusk en vez de su Weavile. Con esto
#              el jefe se queda fijo para siempre.
#
#   NPCs       Easy NPC no tiene nada parecido, asi que lo hace el reloj: si el
#              evento esta parado y un no-admin esta pegado a un NPC, se le
#              cierra el dialogo y se le avisa por la barra de accion.
#              La comprobacion de cercania evita avisar a quien no lo intenta.
f("bloqueo/npcs", """
    # Solo se mira a quien esta a menos de 5 bloques de un NPC: asi no se avisa
    # a los 40 jugadores del servidor, solo a quien de verdad lo esta intentando.
    execute as @a[tag=!ev_admin] at @s if entity @e[type=easy_npc:humanoid,distance=..5] run easy_npc dialog close @s
    execute as @a[tag=!ev_admin] at @s if entity @e[type=easy_npc:humanoid,distance=..5] run title @s actionbar ["",{"text":"No hay nada que hablar todavia.","color":"gray","italic":true}]
""")


# ===========================================================================
#  Guardianes: el remate de sus escenas
# ===========================================================================
#
# El ultimo boton del dialogo no puede rematar la escena el mismo: la ultima
# linea de voz dura entre cuatro y siete segundos, y si el rugido y el aviso
# salen en el mismo instante le pisan la voz.
#
# Como Easy NPC tiene bloqueados `function` y `schedule`, el boton solo deja dos
# numeros —cuantos segundos esperar y de que guardian se trata— y se va. El reloj
# los baja de uno en uno y remata al llegar a cero: se cierra el dialogo solo,
# suena la bestia y aparece el aviso del cristal.
#
#   ident: (Pokemon que suelta, sonido, tono, donde esta el cristal)
GUARDIANES = {
    1: ("MIGHTYENA", "minecraft:entity.wolf.growl", 0.6,
        "El cristal esta detras de el."),
    2: ("WEAVILE", "minecraft:entity.stray.ambient", 0.7,
        "El cristal esta al fondo de la cueva."),
    3: ("SHARPEDO", "minecraft:entity.guardian.attack", 0.5,
        "El cristal esta junto al agua, detras de el."),
    4: ("HYDREIGON", "minecraft:entity.ender_dragon.growl", 0.7,
        "El cristal esta al fondo del laboratorio."),
}

f("guardianes/cuenta", """
    scoreboard players remove #ev ev_reto 1
    execute if score #ev ev_reto matches 0 run return run function evento:guardianes/reto
""")

f("guardianes/reto", "\n".join(
    [f"execute if score #ev ev_reto_id matches {n} run return run function evento:guardianes/r{n}"
     for n in GUARDIANES]))

for n, (bestia, sonido, tono, donde) in GUARDIANES.items():
    f(f"guardianes/r{n}", f"""
    scoreboard players set #ev ev_reto 0
    scoreboard players set #ev ev_reto_id 0

    # Cerrar el dialogo del que estuviera hablando. El comando pide UN jugador,
    # asi que se recorre el grupo en vez de pasarle un selector de varios.
    execute as @a[tag=ev_participa] run easy_npc dialog close @s

    title @a[tag=ev_participa] times 8 50 15
    title @a[tag=ev_participa] title {{"text":"{bestia}","color":"dark_red","bold":true}}
    title @a[tag=ev_participa] subtitle {{"text":"Toquen el cristal. Todos.","color":"gray"}}

    # `at @s` es obligatorio: una funcion del servidor no tiene posicion propia,
    # y sin ella el sonido se reproduce en 0,0,0 y no lo oye nadie.
    execute as @a[tag=ev_participa] at @s run playsound {sonido} master @s ~ ~ ~ 1 {tono}
    execute as @a[tag=ev_participa] at @s run playsound {sonido} hostile @s ~ ~ ~ 1 {tono + 0.2:.1f}

    tellraw @a[tag=ev_participa] ["",{{"text":"\\n  {donde} ","color":"aqua"}},{{"text":"Cada uno aporta UN Pokemon.\\n","color":"white"}}]
""")


# ===========================================================================
#  Avance de acto
# ===========================================================================
for n, (titulo, sub) in ACTOS.items():
    romano = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}[n]
    f(f"actos/a{n}", f"""
    # --- ACTO {romano}: {titulo} ---
    scoreboard players set #ev ev_estado {n}
    scoreboard players set #ev ev_reloj 0
    scoreboard players set @a[tag=ev_participa] ev_acto {n}

    title @a[tag=ev_participa] times 10 70 20
    title @a[tag=ev_participa] subtitle {{"text":"{sub}","color":"gray"}}
    title @a[tag=ev_participa] title [{{"text":"ACTO {romano}","color":"gold","bold":true}}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.activate voice @s ~ ~ ~ 1 1
    tellraw @a[tag=ev_participa] ["",{{"text":"\\n"}},{{"text":"  ACTO {romano} · {titulo}","color":"gold","bold":true}},{{"text":"\\n  {sub}\\n","color":"gray"}}]
    tellraw @a[tag=ev_admin] {{"text":"[Evento] Acto {n} iniciado","color":"dark_gray"}}
""")

# El Acto IV abre el laboratorio: enciende el cristal de Vex y empieza a
# vigilarlo. Hasta ese momento el cristal esta ahi pero apagado, para que nadie
# pueda pelear el climax del evento por su cuenta.
ficheros["data/evento/function/actos/a4.mcfunction"] += (
    "function evento:cristales/encender_lab" + chr(10)
    + "function evento:lab/armar_raid" + chr(10)
    + "function evento:lab/marcar" + chr(10))

f("actos/avanzar", """
    # Salta al acto siguiente sea cual sea el actual.
    #
    # El "return run" no es adorno: sin el, la primera linea pone el estado a 2,
    # con lo que la segunda tambien encaja y lo pone a 3, y en cascada hasta el
    # final. El evento entero se ejecutaba de golpe. Con "return run" se sale de
    # la funcion en cuanto una encaja.
    execute if score #ev ev_estado matches 1 run return run function evento:actos/a2
    execute if score #ev ev_estado matches 2 run return run function evento:actos/a3
    execute if score #ev ev_estado matches 3 run return run function evento:actos/a4
    execute if score #ev ev_estado matches 4 run return run function evento:actos/a5
    execute if score #ev ev_estado matches 5 run return run function evento:actos/terminar
""")


# ===========================================================================
#  Acto I — la llamada
# ===========================================================================
#
# El acto avanza solo cuando Oak entrega el rastreador. No hace falta que el
# admin pulse nada: se detecta que alguien del grupo lleva la brujula que da
# el boton «Cuente conmigo» del dialogo.
#
# Se comprueba asi porque los NPCs de Easy NPC tienen bloqueado `function`
# (ver unsafeNpcCommands): Oak no puede llamar al motor, pero si puede dar un
# objeto, y el motor si puede mirar los inventarios.
# `actos/a1_reloj` se define mas abajo, junto a SENALES: necesita las
# coordenadas de la senal 1 para reconocer el rastreador.


# ===========================================================================
#  Acto II — las senales
# ===========================================================================
f("actos/a2_reloj", f"""
    # Objetivo cumplido: {SENALES_COMPLETO} senales, o {SENALES_CORTO} en modo corto.
    execute if score #ev ev_modo matches 0 if score #ev ev_senal matches {SENALES_COMPLETO}.. run return run function evento:actos/a3
    execute if score #ev ev_modo matches 1 if score #ev ev_senal matches {SENALES_CORTO}.. run return run function evento:actos/a3

    # Red de seguridad: ningun reloj puede impedir que el evento termine.
    execute if score #ev ev_reloj matches {LIMITE_SENAL}.. run return run function evento:senales/rendir
""")

# ===========================================================================
#  El rastreador y las senales
# ===========================================================================
#
# El marcador NO es un rayo de faro: un faro necesita cielo abierto y la primera
# senal esta en un bosque cerrado. Se usa una brujula de piedra imán, que apunta
# a unas coordenadas fijas desde cualquier distancia y no depende del terreno.
# Es ademas lo que un "rastreador de energia" deberia hacer.
#
# La distancia sale en la barra de accion, actualizada cada segundo.

SENALES = {
    1: (1887, 64, 255, "el bosque"),
    # El marcador apunta a la BOCA de la cueva, no a donde esta Sable. Sable
    # aguarda 58 bloques mas adentro y el cristal justo detras de el: la llegada
    # tiene que dispararse al llegar a la entrada, que es donde empieza la
    # escena, no cuando ya lo tienen delante.
    2: (1631, 69, 222, "la montana"),
    3: (1613, 63, 557, "la costa"),
}
RADIO_LLEGADA = 25          # a cuantos bloques se da por encontrada

# Donde esta el cristal de incursion de cada senal. El motor lo vigila para
# enterarse solo de que el guardian ha caido, sin que el director pulse nada.
CRISTALES = {
    1: (1890, 64, 259),
    # La senal 2 esta DENTRO de una cueva, asi que el haz del cristal no se ve
    # desde fuera. El marcador tiene que llevarlos hasta la boca; el resto lo
    # hace Sable, que esta plantado antes de la entrada.
    2: (1632, 69, 161),
    # Nix aguarda en 1621 63 550; el cristal queda cuatro bloques detras.
    3: (1625, 63, 548),
}


CRISTAL_TIPO = {1: "dark", 2: "ice", 3: "water"}

# El cristal de Vex, en el laboratorio. No es una senal: se enciende al empezar
# el Acto IV y al ganarlo cae ella, no se suma nada.
CRISTAL_LAB = (1796, 80, 568)


def _setbloque(n, activo):
    x, y, z = CRISTALES[n]
    return (f"setblock {x} {y} {z} cobblemonraiddens:raid_crystal_block["
            f"is_active={'true' if activo else 'false'},is_natural=false,"
            f"can_reset=false,raid_tier=tier_five,raid_type={CRISTAL_TIPO[n]}]")


def _setlab(activo):
    """El cristal de Vex. Tier siete: el unico que el mod deja vacio para
    jefes propios, con el haz mas intenso y su propio logro."""
    x, y, z = CRISTAL_LAB
    return (f"setblock {x} {y} {z} cobblemonraiddens:raid_crystal_block["
            f"is_active={'true' if activo else 'false'},is_natural=false,"
            f"can_reset=false,raid_tier=tier_seven,raid_type=dragon]")


# El `forceload` no es un adorno.
#
# `setblock` sobre un chunk descargado falla **en silencio**: el cristal se
# quedaba apagado porque cuando arranca el acto el grupo esta lejos, y luego al
# llegar decia "the raid den is not active right now" sin mas pista.
#
# Y hace falta ademas DESPUES: `senales/vigilar_raid` lee `raid_cleared` cada
# segundo para enterarse de la victoria, y sobre un chunk descargado tampoco
# puede. Asi que la zona se mantiene cargada mientras esa senal este en juego, y
# se suelta al apagar los cristales.
def _cargar(x, z):
    return f"forceload add {x - 1} {z - 1} {x + 1} {z + 1}"


for n, (cx, cy, cz) in CRISTALES.items():
    f(f"cristales/encender{n}", "\n".join([_cargar(cx, cz), _setbloque(n, True)]))

f("cristales/encender_lab", "\n".join(
    [_cargar(CRISTAL_LAB[0], CRISTAL_LAB[2]), _setlab(True)]))

f("cristales/apagar_todos", "\n".join(
    ["# Se llama al reiniciar y al terminar: el mundo queda como estaba.",
     "# Se cargan primero, o el `setblock` de apagado tampoco llegaria."]
    + [_cargar(x, z) for _, (x, _, z) in CRISTALES.items()]
    + [_cargar(CRISTAL_LAB[0], CRISTAL_LAB[2])]
    + [_setbloque(n, False) for n in CRISTALES] + [_setlab(False)]
    + ["forceload remove all"]))


# Vigilancia del cristal del laboratorio.
#
# Va aparte de la de las senales porque el desenlace es otro: al ganarlo no se
# suma una senal, cae Vex y arranca el Acto V. Misma tecnica —comparar el
# contador `raid_cleared` contra una marca tomada al armar—, distinto final.
_LX, _LY, _LZ = CRISTAL_LAB

f("lab/armar_raid", "\n".join([
    "scoreboard players set #ev ev_lab0 0",
    "scoreboard players set #ev ev_lab 0",
    f"execute store result score #ev ev_lab0 run data get block {_LX} {_LY} {_LZ} raid_cleared",
    "scoreboard players set #ev ev_lab_v 1",
]))

# El rastreador vuelve a despertar, ahora hacia el laboratorio.
#
# Sin esto el Acto IV arrancaba y el grupo se quedaba sin saber a donde ir: las
# tres senales tenian su marcador y el laboratorio no. Es el mismo objeto de
# siempre, reapuntado — asi nadie tiene que aprender nada nuevo.
# La ENTRADA del laboratorio, no donde esta Vex. Igual que con la cueva de
# Sable: el marcador lleva a la puerta y la escena la lleva ella dentro.
_VEX = (1787, 65, 569)

f("lab/marcar", f"""
    clear @a[tag=ev_participa] minecraft:compass
    give @a[tag=ev_participa] minecraft:compass[custom_name='{{"text":"Rastreador de energia","color":"light_purple","italic":false}}',lore=['{{"text":"La senal mas fuerte de todas.","color":"gray","italic":true}}','{{"text":"Viene del laboratorio.","color":"dark_gray","italic":true}}'],enchantment_glint_override=true,minecraft:lodestone_tracker={{target:{{pos:[I;{_VEX[0]},{_VEX[1]},{_VEX[2]}],dimension:"minecraft:overworld"}},tracked:false}}]

    title @a[tag=ev_participa] times 5 60 15
    title @a[tag=ev_participa] subtitle {{"text":"El rastreador se ha vuelto loco","color":"gray"}}
    title @a[tag=ev_participa] title [{{"text":"LA FUENTE","color":"light_purple","bold":true}}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.power_select voice @s ~ ~ ~ 1000000 0.6
    tellraw @a[tag=ev_participa] ["",{{"text":"\\n  El rastreador apunta al laboratorio. Sigan la aguja.\\n","color":"gray","italic":true}}]

    scoreboard players set #ev ev_lab_m 1
""")

# La llegada al laboratorio, igual que la de las tres senales.
#
# Faltaba: el marcador llevaba hasta la puerta pero al llegar no pasaba nada y
# la brujula seguia encendida. Las tres senales tienen su aviso y esta no, y se
# notaba justo en el momento mas importante del evento.
f("lab/distancia", f"""
    # `positioned` PRIMERO: si va despues, la distancia se mide del jugador a si
    # mismo (siempre 0) y la llegada salta al instante.
    execute as @a[tag=ev_participa] at @s positioned {_VEX[0]} {_VEX[1]} {_VEX[2]} if entity @s[distance=..{RADIO_LLEGADA}] run return run function evento:lab/llegada
    execute as @a[tag=ev_participa] run title @s actionbar [{{"text":"Senal ","color":"gray"}},{{"text":"el laboratorio","color":"light_purple"}},{{"text":"  ·  sigue la aguja","color":"dark_gray"}}]
""")

f("lab/llegada", """
    # Solo la primera vez: el marcador se apaga para todo el grupo.
    execute unless score #ev ev_lab_m matches 1 run return 0
    scoreboard players set #ev ev_lab_m 0

    clear @a[tag=ev_participa] minecraft:compass
    title @a[tag=ev_participa] times 5 60 15
    title @a[tag=ev_participa] subtitle {"text":"La puerta esta abierta","color":"gray"}
    title @a[tag=ev_participa] title [{"text":"EL LABORATORIO","color":"light_purple","bold":true}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.deactivate voice @s ~ ~ ~ 1 0.6
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  El rastreador se apaga. Ya no hace falta.\\n","color":"gray","italic":true}]
""")

f("lab/vigilar_raid", "\n".join([
    f"execute store result score #ev ev_lab run data get block {_LX} {_LY} {_LZ} raid_cleared",
    "execute unless score #ev ev_lab = #ev ev_lab0 run return run function evento:lab/vex_derrotada",
]))


for n, (x, y, z, zona) in SENALES.items():
    f(f"senales/s{n}_marcar", f"""
    # Reapunta el rastreador de todo el grupo a la senal {n}.
    # `tracked:false` evita que Minecraft exija una piedra iman real ahi.
    clear @a[tag=ev_participa] minecraft:compass
    give @a[tag=ev_participa] minecraft:compass[custom_name='{{"text":"Rastreador de energia","color":"aqua","italic":false}}',lore=['{{"text":"Senal detectada en {zona}.","color":"gray","italic":true}}','{{"text":"Sigue la aguja.","color":"dark_gray","italic":true}}'],enchantment_glint_override=true,minecraft:lodestone_tracker={{target:{{pos:[I;{x},{y},{z}],dimension:"minecraft:overworld"}},tracked:false}}]

    scoreboard players set #ev ev_senal_act {n}
    # Enciende el cristal de esta senal. Hasta ahora estaba apagado
    # para que nadie pudiera pelear la incursion antes de tiempo.
    function evento:cristales/encender{n}

    title @a[tag=ev_participa] times 5 50 15
    title @a[tag=ev_participa] subtitle {{"text":"El rastreador ha despertado","color":"gray"}}
    title @a[tag=ev_participa] title [{{"text":"SENAL DETECTADA","color":"aqua","bold":true}}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.power_select voice @s ~ ~ ~ 1 1.4
""")

# Distancia en vivo y deteccion de llegada, una vez por segundo
_dist = ["# Barra de accion con la distancia, y aviso al llegar."]
for n, (x, y, z, zona) in SENALES.items():
    _dist.append(
        f"execute if score #ev ev_senal_act matches {n} as @a[tag=ev_participa] at @s "
        f"run function evento:senales/s{n}_dist")
f("senales/distancia", "\n".join(_dist))

for n, (x, y, z, zona) in SENALES.items():
    f(f"senales/s{n}_dist", f"""
    # Se ejecuta como cada participante, en su posicion.
    # `positioned` PRIMERO: si va despues, la distancia se mide desde el propio
    # jugador hasta si mismo (siempre 0) y la llegada salta al instante.
    execute positioned {x} {y} {z} if entity @s[distance=..{RADIO_LLEGADA}] run return run function evento:senales/s{n}_llegada
    title @s actionbar [{{"text":"Senal ","color":"gray"}},{{"text":"{zona}","color":"aqua"}},{{"text":"  ·  sigue la aguja","color":"dark_gray"}}]
""")

    f(f"senales/s{n}_llegada", f"""
    # Solo la primera vez: el marcador se apaga para todos.
    execute unless score #ev ev_senal_act matches {n} run return 0
    scoreboard players set #ev ev_senal_act 0

    clear @a[tag=ev_participa] minecraft:compass
    title @a[tag=ev_participa] times 5 60 15
    title @a[tag=ev_participa] subtitle {{"text":"Algo paso aqui","color":"gray"}}
    title @a[tag=ev_participa] title [{{"text":"SENAL LOCALIZADA","color":"aqua","bold":true}}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.deactivate voice @s ~ ~ ~ 1 0.8
    tellraw @a[tag=ev_participa] ["",{{"text":"\\n  El rastreador se apaga. Estan en el sitio.\\n","color":"gray","italic":true}}]
""")


f("senales/completar", """
    # Se llama sola al ganar la incursion (ver senales/vigilar_raid), y tambien
    # a mano desde el panel por si algo fallara.
    scoreboard players add #ev ev_senal 1
    scoreboard players set #ev ev_reloj 0
    scoreboard players set #ev ev_raid_v 0
    scoreboard players set #ev ev_sig 0

    title @a[tag=ev_participa] times 5 50 15
    title @a[tag=ev_participa] subtitle {"text":"Fragmento de datos recuperado","color":"gray"}
    title @a[tag=ev_participa] title [{"text":"SENAL LOCALIZADA","color":"aqua","bold":true}]

    # `at @s` y volumen alto: sin las dos cosas el sonido se reproduce en el
    # origen del mundo con 16 bloques de alcance, o sea que no lo oye nadie.
    execute as @a[tag=ev_participa] at @s run playsound minecraft:entity.player.levelup voice @s ~ ~ ~ 1 1.4
    tellraw @a[tag=ev_participa] ["",{"text":"  Senales: ","color":"gray"},{"score":{"name":"#ev","objective":"ev_senal"},"color":"aqua","bold":true},{"text":" de 3","color":"gray"}]

    # Oak no habla todavia: queda a la espera de que salgan de la arena.
    scoreboard players set #ev ev_oak_esp 1
""")

# Oak reacciona a la caida del guardian, pero NO mientras siguen dentro.
#
# La incursion ocurre en su propia dimension, y al ganar queda la pantalla de
# recompensa y la captura del Pokemon. Si Oak habla en ese momento, la mitad del
# grupo no se entera y la otra mitad lo oye por encima de su propia pantalla.
#
# Asi que primero se espera a que la dimension de la incursion se quede sin
# nadie del grupo, y solo entonces empieza la cuenta atras.
#
# El truco del filtro por dimension: `distance` solo casa con entidades que
# esten en la dimension del contexto de ejecucion, asi que un `execute in ...
# positioned 0 0 0 if entity @a[distance=..]` responde "hay alguien del grupo
# en esta dimension". Comprobado en el servidor.
f("senales/oak_espera", """
    execute in cobblemonraiddens:raid_dimension positioned 0.0 0.0 0.0 if entity @a[tag=ev_participa,distance=..100000000] run return 0
    # Ya han salido todos. Ahora si, tres segundos y habla.
    scoreboard players set #ev ev_oak_esp 0
    scoreboard players set #ev ev_oak 3
""")

f("senales/oak_cuenta", """
    scoreboard players remove #ev ev_oak 1
    execute if score #ev ev_oak matches 0 run return run function evento:senales/oak_victoria
""")

f("senales/oak_victoria", """
    scoreboard players set #ev ev_oak 0
    scoreboard players set #ev ev_oak_esp 0
    stopsound @a[tag=ev_participa] voice
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.a2_02 voice @s ~ ~ ~ 1000000 1
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  PROFESOR OAK  ","color":"gold","bold":true},{"text":"Ese sujeto dejo caer algo. Un fragmento de datos... cifrado, claro. Guardenlo, todavia no puedo leerlo.\\n","color":"white"}]

    # `a2_02` dura 10 s. A los 12 el rastreador vuelve a despertar y apunta a la
    # senal siguiente. Sin esto el grupo se quedaba con la brujula clavada en el
    # sitio que ya habia hecho, esperando a que saltara el limite de tiempo.
    scoreboard players set #ev ev_sig 12
""")

f("senales/sig_cuenta", """
    scoreboard players remove #ev ev_sig 1
    execute if score #ev ev_sig matches 0 run return run function evento:senales/siguiente
""")

# A donde se va despues de una senal.
#
# Si ya se ha cumplido el objetivo no se marca nada: `actos/a2_reloj` se encarga
# de saltar al Acto III en el mismo segundo, y marcar una senal mas seria dar una
# orden que se contradice con la siguiente.
f("senales/siguiente", "\n".join([
    f"execute if score #ev ev_modo matches 0 if score #ev ev_senal matches {SENALES_COMPLETO}.. run return 0",
    f"execute if score #ev ev_modo matches 1 if score #ev ev_senal matches {SENALES_CORTO}.. run return 0",
    *[f"execute if score #ev ev_senal matches {n - 1} run return run function evento:senales/ir{n}"
      for n in SENALES if n > 1],
    "",
    "# Se han hecho todas las senales que hay construidas, pero el objetivo pide",
    "# mas. Sin esta linea el grupo se quedaba 25 minutos parado esperando a que",
    "# saltara el limite de tiempo, con la brujula apuntando a un sitio ya hecho.",
    "# Asi el evento se adapta a lo que haya montado en el mundo.",
    f"execute if score #ev ev_senal matches {max(SENALES)}.. run return run function evento:actos/a3",
]))

# Oak anuncia cada senal con su propia linea: la 2 con a2_03 y la 3 con a2_04.
for n in SENALES:
    if n == 1:
        continue
    clip = f"a2_0{n + 1}"
    frase = {
        2: "El rastreador volvio a despertar. Esta vez hacia la montana. Tengan cuidado: si el Eclipse puso vigilancia ahi arriba, es porque algo esconden.",
        3: "Ultima lectura. Viene de la costa, y es la mas fuerte de las tres. Estan cerca de algo importante. Lo siento en los numeros.",
    }[n]
    f(f"senales/ir{n}", f"""
    # `s{n}_marcar` deja `ev_senal_act` en {n}, y `armar_raid` lo lee para saber
    # que cristal vigilar. El orden importa.
    function evento:senales/s{n}_marcar
    function evento:senales/armar_raid
    scoreboard players set #ev ev_reloj 0

    stopsound @a[tag=ev_participa] voice
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.{clip} voice @s ~ ~ ~ 1000000 1
    tellraw @a[tag=ev_participa] ["",{{"text":"\\n  PROFESOR OAK  ","color":"gold","bold":true}},{{"text":"{frase}\\n","color":"white"}}]
""")

f("senales/rendir", """
    # El guardian se rinde y Oak justifica el salto. Se pierde el combate, no
    # el evento: es preferible a dejar al grupo atascado media hora.
    scoreboard players add #ev ev_senal 1
    scoreboard players set #ev ev_reloj 0

    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.a2_05 voice @s ~ ~ ~ 1000000 1
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  PROFESOR OAK  ","color":"gold","bold":true},{"text":"He recalibrado el rastreador. Sigan adelante.\\n","color":"white"}]
""")


# ===========================================================================
#  Vigilancia de la incursion
# ===========================================================================
#
# COMO SABE EL MOTOR QUE HAN GANADO
#
# El bloque del cristal lleva un contador `raid_cleared`. Al armar la senal se
# apunta cuanto vale, y a partir de ahi se compara cada segundo: en cuanto
# cambia, es que el grupo ha ganado.
#
# Se compara contra una marca en vez de contra cero porque el cristal se puede
# reutilizar (`max_clears: -1`) y el contador no vuelve atras. Asi tambien
# funciona en el segundo ensayo, y en el tercero.
# OJO con de que marcador se cuelga la vigilancia.
#
# La primera version se apoyaba en `ev_senal_act`, y no funcionaba nunca: ese
# marcador se pone a cero **al llegar** al campamento, y la incursion pasa justo
# despues de llegar. La vigilancia se apagaba sola un segundo antes de hacer
# falta. Por eso `ev_raid_v` guarda el numero de senal por su cuenta y no
# depende de nadie.
_arma, _vigila = [], []
for n, (cx, cy, cz) in CRISTALES.items():
    _arma.append(
        f"execute if score #ev ev_senal_act matches {n} store result score #ev ev_raid0 "
        f"run data get block {cx} {cy} {cz} raid_cleared")
    _arma.append(
        f"execute if score #ev ev_senal_act matches {n} run scoreboard players set #ev ev_raid_v {n}")
    _vigila.append(
        f"execute if score #ev ev_raid_v matches {n} store result score #ev ev_raid "
        f"run data get block {cx} {cy} {cz} raid_cleared")

f("senales/armar_raid", "\n".join([
    "# Apunta el contador del cristal tal y como esta ahora y enciende la",
    "# vigilancia con el numero de senal que toca.",
    "scoreboard players set #ev ev_raid0 0",
    "scoreboard players set #ev ev_raid 0",
    *_arma,
]))

f("actos/a1_reloj", f"""
    # El Acto I se cierra cuando el grupo TIENE EL RASTREADOR. Dos vias, y basta
    # con cualquiera:
    #
    #   1. `ev_oak_listo`, que pone el ultimo boton de Oak.
    #   2. El propio rastreador en el inventario.
    #
    # La segunda existe porque el dialogo del NPC vive DENTRO DE LA ENTIDAD, en
    # el chunk — `world/easy_npc/npcs/` es solo un indice y editarlo no cambia
    # nada. Si el NPC plantado es de una version anterior, su boton da la
    # brujula pero no marca nada, y el acto no cerraba nunca. Mirando el objeto
    # da igual de que version sea el NPC.
    #
    # Se reconoce por el BRILLO, no por ser "una brujula cualquiera". Probado en
    # el servidor: `if items` no sabe mirar dentro de `lodestone_tracker`
    # —ni siquiera `~{{}}` para ver si existe—, pero `enchantment_glint_override`
    # si casa. Una brujula normal no lo lleva, y `admin/reiniciar` limpia las
    # brujulas de todos, asi que no queda ninguna de la partida anterior.
    execute if score #ev ev_oak_listo matches 1 run return run function evento:actos/a2
    execute as @a[tag=ev_participa] if items entity @s container.* minecraft:compass[enchantment_glint_override=true] run return run function evento:actos/a2
""")

f("senales/vigilar_raid", "\n".join([
    *_vigila,
    "execute unless score #ev ev_raid = #ev ev_raid0 run return run function evento:senales/completar",
]))


# ===========================================================================
#  Acto III — el cifrado
# ===========================================================================
f("actos/a3_reloj", f"""
    function evento:misiones/balizas
    execute if score #ev ev_codigo matches {DIGITOS_NECESARIOS}.. run return run function evento:actos/a4
    execute if score #ev ev_reloj matches {LIMITE_CIFRADO}.. run return run function evento:misiones/rescate
""")

f("misiones/rescate", """
    # Oak descifra lo que falta. Excusa narrativa para no bloquear a nadie.
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.a3_04 voice @s ~ ~ ~ 1 1
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  PROFESOR OAK  ","color":"gold","bold":true},{"text":"Me canse de esperar al sistema. Ya tengo la ubicacion.\\n","color":"white"}]
    function evento:actos/a4
""")

for n in range(1, 7):
    f(f"misiones/m{n}", f"""
    # Mision {n} superada por @s. La dispara el avance correspondiente, y sirve
    # igual lanzada a mano para pruebas o para desatascar a alguien.
    execute if score @s ev_m{n} matches 1 run return 0
    scoreboard players set @s ev_m{n} 1
    function evento:misiones/sumar
""")

# --- contadores: avances que hay que repetir N veces -------------------------
#
# Un avance de Minecraft solo salta una vez. Para "captura tres siniestros" se
# revoca nada mas concederse, con lo que vuelve a quedar armado, y se lleva la
# cuenta aparte en un marcador.
REPETIBLES = [
    (1, "captura_siniestro", 3, "Siniestro capturado"),
    (4, "subir_nivel_40", 3, "Pokemon a nivel 40"),
    (6, "pescar", 10, "Pokemon pescado"),
]

for mision, avance, veces, etiqueta in REPETIBLES:
    f(f"misiones/paso_{avance}", f"""
    # Solo cuenta mientras el Acto III este en curso.
    execute unless score #ev ev_estado matches 3 run return 0
    execute if score @s ev_m{mision} matches 1 run return 0

    advancement revoke @s only evento:{avance}
    scoreboard players add @s ev_p{mision} 1

    execute unless score @s ev_p{mision} matches {veces}.. run title @s actionbar [{{"text":"{etiqueta}  ","color":"gray"}},{{"score":{{"name":"@s","objective":"ev_p{mision}"}},"color":"yellow"}},{{"text":" de {veces}","color":"gray"}}]
    execute if score @s ev_p{mision} matches {veces}.. run function evento:misiones/m{mision}
""")

# --- avances de un solo disparo ---------------------------------------------
for mision, avance in [(2, "captura_hielo"), (3, "veterano")]:
    f(f"misiones/paso_{avance}", f"""
    execute unless score #ev ev_estado matches 3 run return 0
    function evento:misiones/m{mision}
""")

# --- mision 5: las balizas ---------------------------------------------------
f("misiones/balizas", """
    # Se colocan con: /function evento:admin/poner_baliza  (donde este el admin)
    # Cada armor stand marcado se detecta al acercarse a cinco bloques.
    execute as @a[tag=ev_participa,scores={ev_m5=0}] at @s if entity @e[type=armor_stand,tag=ev_baliza,tag=!ev_usada,distance=..5] run function evento:misiones/tocar_baliza
""")

f("misiones/tocar_baliza", """
    # La baliza se marca por jugador con un tag propio para que cada uno la
    # encuentre por su cuenta: es una mision individual, no una carrera.
    tag @s add ev_buscando
    execute at @s run tag @e[type=armor_stand,tag=ev_baliza,distance=..5,limit=1] add ev_tocada
    tag @s remove ev_buscando
    scoreboard players add @s ev_baliza 1
    playsound minecraft:block.note_block.bell player @s ~ ~ ~ 1 1.6
    execute unless score @s ev_baliza matches 5.. run title @s actionbar [{"text":"Baliza encontrada  ","color":"gray"},{"score":{"name":"@s","objective":"ev_baliza"},"color":"yellow"},{"text":" de 5","color":"gray"}]
    execute if score @s ev_baliza matches 5.. run function evento:misiones/m5
""")

f("admin/poner_baliza", """
    summon armor_stand ~ ~ ~ {Tags:["ev_baliza"],Invisible:1b,Invulnerable:1b,NoGravity:1b,Marker:1b,CustomName:'{"text":"Baliza"}'}
    tellraw @s {"text":"[Evento] Baliza colocada aqui.","color":"yellow"}
""")

f("admin/quitar_balizas", """
    kill @e[type=armor_stand,tag=ev_baliza]
    scoreboard players set @a ev_baliza 0
    tellraw @s {"text":"[Evento] Balizas retiradas.","color":"yellow"}
""")

f("misiones/sumar", f"""
    scoreboard players add #ev ev_codigo 1

    title @s times 5 45 15
    title @s subtitle [{{"text":"Digito ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_codigo"}},"color":"yellow"}},{{"text":" de {DIGITOS_NECESARIOS}","color":"gray"}}]
    title @s title [{{"text":"FRAGMENTO DESCIFRADO","color":"green","bold":true}}]
    playsound minecraft:block.note_block.chime voice @s ~ ~ ~ 1 1.5

    tellraw @a[tag=ev_participa] [{{"selector":"@s","color":"yellow"}},{{"text":" ha descifrado un fragmento (","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_codigo"}},"color":"white"}},{{"text":"/{DIGITOS_NECESARIOS})","color":"gray"}}]
""")


# ===========================================================================
#  Actos IV y V
# ===========================================================================
f("actos/a4_reloj", """
    # Sin limite de tiempo a proposito. El Acto IV avanza cuando cae Vex:
    #   function evento:lab/vex_derrotada
""")

f("lab/vex_derrotada", """
    scoreboard players set #ev ev_lab_v 0
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  La Doctora Vex huye. La capsula queda accesible.\\n","color":"light_purple","italic":true}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:entity.ender_dragon.death voice @s ~ ~ ~ 0.6 1.4
    function evento:actos/a5
""")

f("actos/a5_reloj", """
    # Termina cuando Luna es capturada:
    #   function evento:actos/terminar
""")

f("actos/terminar", """
    scoreboard players set #ev ev_estado 0
    scoreboard players set #ev ev_reloj 0

    title @a[tag=ev_participa] times 10 100 30
    title @a[tag=ev_participa] subtitle {"text":"Luna esta en casa","color":"gray"}
    title @a[tag=ev_participa] title [{"text":"EL RASTRO DE LUNA","color":"light_purple","bold":true}]
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.a5_04 voice @s ~ ~ ~ 1 1
    tellraw @a[tag=ev_participa] ["",{"text":"\\n  ─────────────────────────────\\n","color":"dark_gray"},{"text":"  Gracias por jugar.\\n","color":"white"},{"text":"  ─────────────────────────────\\n","color":"dark_gray"}]
    execute at @a run summon firework_rocket ~ ~2 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{explosions:[{shape:"star",colors:[I;13061821,3887386]}]}}}}
""")


# ===========================================================================
#  Escenas con voz
# ===========================================================================
#
# Una escena reproduce lineas de Oak en orden, con su subtitulo, esperando lo que
# dura cada clip. Se lleva con el reloj de un segundo en vez de con `schedule`
# porque los schedule se pierden en un /reload y una escena a medias en pleno
# evento es justo lo que no puede pasar.
DURACIONES = json.load(open(os.path.join(RAIZ, "datos", "duraciones.json"), encoding="utf-8"))

ESCENAS = {
    1: [  # Acto I — la llamada
        ("a1_01", "Entrenadores. Escuchenme bien."),
        ("a1_02", "Hace tres semanas detecte una lectura de energia..."),
        ("a1_03", "Era una Pokemon. Y me miro como si me conociera."),
        ("a1_04", "El Equipo Eclipse se la llevo."),
        ("a1_05", "Necesito que me ayuden a traerla de vuelta."),
        ("a1_06", "Tomen el rastreador. Apunta hacia ella."),
    ],
    2: [  # Acto V — la revelacion
        ("a5_01", "Ahi esta. Ese collar..."),
        ("a5_01b", "Estos valores no son de un Pokemon legendario."),
        ("a5_01c", "Yo no la descubri. Ella se dejo encontrar."),
        ("a5_01d", "Arceus dio origen al universo. Ella le dio un motivo."),
        ("a5_01e", "Luna es la Diosa del Amor Incondicional."),
        ("a5_02", "Alejandro. Acercate tu."),
    ],
}

f("escenas/reloj", """
    # Corre cada segundo mientras haya una escena en marcha.
    scoreboard players remove #ev ev_esc_t 1
    execute if score #ev ev_esc_t matches ..0 run function evento:escenas/siguiente
""")

lineas_sig = ["scoreboard players add #ev ev_esc_p 1"]
for esc, guion in ESCENAS.items():
    for i, (clip, _) in enumerate(guion, start=1):
        lineas_sig.append(
            f"execute if score #ev ev_esc matches {esc} if score #ev ev_esc_p matches {i} "
            f"run return run function evento:escenas/e{esc}_{i}")
    lineas_sig.append(
        f"execute if score #ev ev_esc matches {esc} if score #ev ev_esc_p matches {len(guion)+1}.. "
        f"run return run function evento:escenas/fin")
f("escenas/siguiente", "\n".join(lineas_sig))

for esc, guion in ESCENAS.items():
    for i, (clip, sub) in enumerate(guion, start=1):
        f(f"escenas/e{esc}_{i}", f"""
    stopsound @a[tag=ev_participa] voice
    # El filtro por grupo va tambien aqui. Sin el, la voz de Oak se oye en TODO
    # el servidor: el volumen es 1000000, o sea audible a cualquier distancia,
    # asi que quien estuviera minando a 5000 bloques se llevaba la escena entera.
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.{clip} voice @s ~ ~ ~ 1000000 1
    title @a[tag=ev_participa] times 8 {DURACIONES[clip] * 20} 12
    title @a[tag=ev_participa] subtitle {{"text":"{sub}","color":"white"}}
    title @a[tag=ev_participa] title [{{"text":"PROFESOR OAK","color":"gold","bold":true}}]
    scoreboard players set #ev ev_esc_t {DURACIONES[clip]}
""")

f("escenas/fin", """
    scoreboard players set #ev ev_esc 0
    scoreboard players set #ev ev_esc_p 0
    scoreboard players set #ev ev_esc_t 0
    title @a[tag=ev_participa] times 5 30 10
    title @a[tag=ev_participa] subtitle {"text":"","color":"white"}
""")

for esc, nombre in [(1, "acto1"), (2, "revelacion")]:
    f(f"escenas/lanzar_{nombre}", f"""
    scoreboard players set #ev ev_esc {esc}
    scoreboard players set #ev ev_esc_p 0
    scoreboard players set #ev ev_esc_t 0
""")


# ===========================================================================
#  El final: Luna
# ===========================================================================
#
# Donde aparece y a quien se le entrega la ball. Se deja arriba y con nombre
# porque son las dos cosas que mas probablemente haya que cambiar el dia del
# evento.
LUNA_POS = (1820, 64, 499)
LUNA_NIVEL = 75
# Luna mide 0,6 bloques. x6 la deja en 3,6 — lo que pidio el usuario.
LUNA_ESCALA = 6.0
LUNA_ELEGIDO = "A1ejandroreport"

# ---------------------------------------------------------------------------
#  Las tres zonas de captura
# ---------------------------------------------------------------------------
#
# Todos los jefes del evento son siniestros, y tres de los cuatro pegan en
# fisico —solo Hydreigon es especial—. De ahi salen los tres roles:
#
#   Granbull   TANQUE     Intimidacion baja el ataque de Mightyena, Weavile y
#                         Sharpedo nada mas salir. Hada resiste siniestro y es
#                         inmune a dragon, que es el arma contra Hydreigon.
#   Machamp    DANO       130 de ataque y lucha pega x2 a los cuatro. Lucha
#                         puro: sus debilidades no las usa ningun jefe.
#   Ribombee   SOPORTE    Bicho/hada resiste siniestro x0,25 y lucha x0,5.
#                         Danza Aleteo y Bola Polen, que cura al aliado.
#
# Nivel 60 contra jefes de 45 a 70: el primero es calentamiento, el ultimo una
# pared. Capturar a 40 como decia la version anterior dejaba al grupo sin nada
# que hacer contra Hydreigon.
NIVEL_CAPTURA = 60

# Cuantos se sueltan por zona. Doce personas necesitan uno cada una, pero se
# fallan capturas: con dieciseis nadie se queda esperando el respawn.
POR_ZONA = 16

ZONAS = {
    1: ("granbull", (1238, 64, 508), "TANQUE"),
    2: ("machamp",  (1230, 69, 460), "DANO"),
    3: ("ribombee", (1162, 68, 412), "SOPORTE"),
}

# La revelacion son seis lineas de Oak (ESCENAS[2]) que suman poco mas de un
# minuto. Luna no aparece hasta que terminan: si sale antes, nadie escucha nada.
_DUR_REVELACION = sum(DURACIONES[c] for c, _ in ESCENAS[2]) + 4

f("lab/revelacion", f"""
    # Se llama sola al caer Vex. Arranca la escena y programa la aparicion.
    function evento:escenas/lanzar_revelacion
    scoreboard players set #ev ev_luna {_DUR_REVELACION}
""")

f("lab/luna_cuenta", """
    scoreboard players remove #ev ev_luna 1
    execute if score #ev ev_luna matches 0 run return run function evento:lab/aparece_luna
""")

f("lab/fijar_cuenta", """
    scoreboard players remove #ev ev_fijar 1
    execute if score #ev ev_fijar matches 0 run return run function evento:lab/fijar_luna
""")

f("lab/fijar_luna", f"""
    scoreboard players set #ev ev_fijar 0

    # Luna se queda clavada donde aparece, y enorme.
    #
    # Si se mueve, la escena final se convierte en perseguirla por el
    # laboratorio con doce personas detras. `NoAI` le apaga el cerebro y
    # `PersistenceRequired` evita que se esfume si el grupo tarda en llegar.
    #
    # El tamano va por el atributo de la ENTIDAD, no por los datos del Pokemon.
    # Esa distincion es justo lo que se buscaba: el atributo vive en la criatura
    # que esta en el mundo, asi que Luna se ve de {LUNA_ESCALA * 0.6:.1f} bloques mientras es
    # salvaje y **vuelve a su tamano normal en cuanto la capturan**, porque a la
    # Pokeball solo se va su ficha. Mide 0,6 de base, de ahi el x{LUNA_ESCALA}.
    #
    # Se busca por cercania al punto de aparicion y con radio corto, para no
    # tocar por error a un Pokemon salvaje que pasara por ahi.
    execute positioned {LUNA_POS[0]} {LUNA_POS[1]} {LUNA_POS[2]} as @e[type=cobblemon:pokemon,distance=..6,limit=1,sort=nearest] run data merge entity @s {{NoAI:1b,PersistenceRequired:1b}}
    execute positioned {LUNA_POS[0]} {LUNA_POS[1]} {LUNA_POS[2]} as @e[type=cobblemon:pokemon,distance=..6,limit=1,sort=nearest] run attribute @s minecraft:generic.scale base set {LUNA_ESCALA}
""")


# ---------------------------------------------------------------------------
#  Poblar las zonas de captura
# ---------------------------------------------------------------------------
#
# Se sueltan a mano en vez de fiarlo a la aparicion natural: con doce personas
# hay que garantizar que haya suficientes y todos del mismo nivel, y las tablas
# de aparicion de Cobblemon no dan ninguna de las dos cosas.
#
# Se reparten en circulo alrededor del centro; amontonados en un bloque se
# empujan entre ellos y quedan feisimos.
import math as _math

for _n, (_especie, (_zx, _zy, _zz), _rol) in ZONAS.items():
    _lineas = [f"# {_rol}: {POR_ZONA} {_especie} de nivel {NIVEL_CAPTURA} en {_zx} {_zy} {_zz}"]
    for _i in range(POR_ZONA):
        _ang = 2 * _math.pi * _i / POR_ZONA
        _r = 6 + (_i % 3) * 3          # tres anillos, para que no formen un aro
        _dx = round(_r * _math.cos(_ang))
        _dz = round(_r * _math.sin(_ang))
        _lineas.append(
            f"pokespawnat {_zx + _dx} {_zy} {_zz + _dz} {_especie} level={NIVEL_CAPTURA}")
    f(f"zonas/poblar{_n}", "\n".join(_lineas))

f("zonas/poblar_todas", "\n".join(
    ["# Suelta las tres zonas de golpe. Es lo que se pulsa antes del evento."] +
    [f"function evento:zonas/poblar{n}" for n in ZONAS]))


# El libro de misiones, a todo el servidor.
#
# Va aparte de `poblar_todas` a proposito, porque el orden importa: primero el
# libro —para que sepan que buscar y donde— y solo despues los Pokemon. Al
# reves, la gente se encuentra bichos de nivel 60 por el mapa sin ninguna
# explicacion.
#
# El atajo de teclado de FTB Quests esta sin asignar en el pack (se habia
# quedado con la T y la R, y dejaba sin chat y sin poder sacar Pokemon), asi que
# el objeto es la unica via comoda de abrirlo.
f("admin/repartir_libros", """
    give @a ftbquests:book 1
    tellraw @a ["",{"text":"\\n  EL RASTRO DE LUNA\\n","color":"light_purple","bold":true},{"text":"  El Profesor Oak ha dejado un informe para todos.\\n","color":"white"},{"text":"  Abre el libro de misiones que acabas de recibir.\\n\\n","color":"gray"}]
    execute as @a at @s run playsound minecraft:item.book.page_turn master @s ~ ~ ~ 1 1
    tellraw @a[tag=ev_admin] {"text":"[Evento] Libros repartidos a todo el servidor.","color":"dark_gray"}
""")

f("zonas/limpiar", "\n".join(
    ["# Recoge lo que quede sin capturar, para no dejar el mapa sembrado."] +
    [f"execute positioned {x} {y} {z} run kill @e[type=cobblemon:pokemon,distance=..25]"
     for _, (x, y, z), _ in ZONAS.values()]))


# ---------------------------------------------------------------------------
#  Modo prueba
# ---------------------------------------------------------------------------
#
# Cambia los cuatro jefes por versiones de nivel 5 con media vida, misma especie
# para que la escena se lea igual. Sirve para recorrer el evento entero en
# solitario sin pasarse una hora peleando.
#
# El `forceload` no es opcional: `crd dens` necesita el chunk cargado, y las
# cuatro zonas estan a cientos de bloques unas de otras.
_TODOS = [("grum", *CRISTALES[1]), ("sable", *CRISTALES[2]),
          ("nix", *CRISTALES[3]), ("vex", *CRISTAL_LAB)]

for _modo, _sufijo in [("prueba", "_prueba"), ("real", "_eclipse")]:
    _l = [f"# Cambia los cuatro cristales a los jefes de {_modo}."]
    for _q, _x, _y, _z in _TODOS:
        _l.append(f"forceload add {_x - 8} {_z - 8} {_x + 8} {_z + 8}")
    for _q, _x, _y, _z in _TODOS:
        _l.append(f"crd dens {_x} {_y} {_z} boss cobblemonraiddens:{_q}{_sufijo}")
    # `crd dens` deja el cristal encendido; el evento decide cuando se abre.
    _l.append("function evento:cristales/apagar_todos")
    _l.append("forceload remove all")
    _l.append(f'tellraw @a[tag=ev_admin] {{"text":"[Evento] Jefes en modo {_modo.upper()}.","color":"yellow"}}')
    f(f"admin/modo_{_modo}", "\n".join(_l))


# Deja el evento listo para recorrerlo una persona sola: dentro del grupo,
# acreditada, y con los jefes en nivel 5.
f("admin/prueba_solo", """
    tag @s add ev_participa
    tag @s add ev_apto
    function evento:admin/modo_prueba
    tellraw @s ["",{"text":"\\n  Listo para probar en solitario.\\n","color":"green","bold":true},{"text":"  Estas en el grupo y acreditado. Jefes a nivel 5.\\n","color":"gray"},{"text":"  Acuerdate de [ MODO REAL ] antes del evento de verdad.\\n","color":"yellow"}]
""")

f("lab/aparece_luna", f"""
    scoreboard players set #ev ev_luna 0

    # `pokespawn` aparece donde este quien ejecuta, y desde la consola eso no es
    # ningun sitio util: `execute positioned` no le sirve porque lee la posicion
    # de la entidad, no la del comando. Cobblemon trae `pokespawnat`, que si
    # acepta coordenadas explicitas.
    pokespawnat {LUNA_POS[0]} {LUNA_POS[1]} {LUNA_POS[2]} luna level={LUNA_NIVEL}

    # Congelarla llega dos segundos despues, no aqui: la entidad no existe
    # todavia en este mismo tick y el `data merge` no encontraria nada.
    scoreboard players set #ev ev_fijar 2

    title @a[tag=ev_participa] times 20 90 30
    title @a[tag=ev_participa] subtitle {{"text":"Ahi esta","color":"gray"}}
    title @a[tag=ev_participa] title [{{"text":"LUNA","color":"light_purple","bold":true}}]
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.power_select voice @s ~ ~ ~ 1000000 0.7

    # La ball va a una sola persona a proposito. Que la capture quien conduce
    # el evento convierte el final en una escena en vez de en una carrera de
    # doce personas lanzando bolas a la vez.
    give {LUNA_ELEGIDO} cobblemon:master_ball[custom_name='{{"text":"Ball de Luna","color":"light_purple","italic":false}}',lore=['{{"text":"La ultima que le quedaba al Profesor Oak.","color":"gray","italic":true}}'],enchantment_glint_override=true] 1
    execute as @a[tag=ev_participa] at @s run playsound evento:voz.oak.a5_03 voice @s ~ ~ ~ 1000000 1
    tellraw @a[tag=ev_participa] ["",{{"text":"\\n  PROFESOR OAK  ","color":"gold","bold":true}},{{"text":"{LUNA_ELEGIDO}, es tuya. Con calma.\\n","color":"white"}}]
""")

# El Acto V lanza su revelacion solo.
#
# Antes la disparaba el admin a mano, con la idea de esperar a que el grupo
# estuviera delante de la capsula. Pero al encadenarse todo lo demas era el
# unico sitio donde el evento se quedaba mudo: caia Vex, salia el rotulo del
# Acto V y ya. Seis lineas grabadas sin usar.
#
# Ahora va detras de la caida de Vex. Sigue habiendo boton en el panel por si
# hay que repetirla.
ficheros["data/evento/function/actos/a5.mcfunction"] += (
    "function evento:lab/revelacion" + chr(10))
# El Acto I NO lanza cinematica: la escena la lleva Oak en persona. Uno habla
# con el y el resto escucha, que es como se decidio montarlo. La cinematica
# de apertura sigue disponible como boton del panel por si algun dia se usa.

# El Acto II arranca el marcador de la primera senal: reparte la brujula de
# piedra iman apuntando al campamento y enciende la deteccion de llegada.
# Cerrar el dialogo de Oak: quien haya hablado con el se queda con la
# pantalla abierta mientras empieza el acto, y eso tapa el rotulo.
ficheros["data/evento/function/actos/a2.mcfunction"] += (
    "execute as @a[tag=ev_participa] run easy_npc dialog close @s" + chr(10))
ficheros["data/evento/function/actos/a2.mcfunction"] += "function evento:senales/s1_marcar" + chr(10)
ficheros["data/evento/function/actos/a2.mcfunction"] += "function evento:senales/armar_raid" + chr(10)

f("admin/cortar_escena", """
    stopsound @a[tag=ev_participa] voice
    function evento:escenas/fin
    tellraw @s {"text":"[Evento] Escena cortada.","color":"yellow"}
""")


# ===========================================================================
#  El rastreador
# ===========================================================================
f("util/rastreador", """
    # Una brujula con nombre e historia. lodestone_tracker sin posicion la deja
    # girando, que es justo el efecto de "algo la esta llamando".
    give @s minecraft:compass[custom_name='{"text":"Rastreador de energia","color":"aqua","italic":false}',lore=['{"text":"Lo armo el Profesor Oak anoche.","color":"gray","italic":true}','{"text":"Apunta hacia Luna.","color":"dark_gray","italic":true}'],enchantment_glint_override=true]
""")

f("admin/dar_rastreadores", """
    execute as @a[tag=ev_participa] run function evento:util/rastreador
    tellraw @s {"text":"[Evento] Rastreador entregado a todos.","color":"yellow"}
""")


# ===========================================================================
#  Utilidades
# ===========================================================================
f("util/poner_al_dia", """
    # Alguien entro tarde o se reconecto: se le pone el acto en curso.
    scoreboard players operation @s ev_acto = #ev ev_estado
    title @s times 5 60 15
    title @s subtitle {"text":"Te has incorporado al evento","color":"gray"}
    title @s title [{"text":"EL RASTRO DE LUNA","color":"light_purple","bold":true}]
""")


# ===========================================================================
#  Administracion
# ===========================================================================
# El arranque pasa por una verja.
#
# El tag `ev_apto` lo pone FTB Quests: la ultima mision del capitulo
# "PROTOCOLO LUNA" tiene una recompensa de tipo `command` que ejecuta
# `tag @s add ev_apto`. Es decir, el datapack no comprueba tipos ni niveles a
# mano — de eso ya se encarga Cobblemon Quests, que si sabe filtrar por tipo y
# por rango de nivel. Aqui solo se lee el resultado.
#
# El aviso NO es un bloqueo duro: trae un boton para empezar igual. El dia del
# evento mandas tu, no el datapack.
f("admin/iniciar", """
    execute unless score #ev ev_estado matches 0 run tellraw @s {"text":"[Evento] Ya hay un evento en curso. Usa reiniciar primero.","color":"red"}
    execute unless score #ev ev_estado matches 0 run return 0

    execute unless entity @a[tag=ev_participa] run tellraw @s {"text":"[Evento] No hay nadie apuntado. Usa INVITAR primero.","color":"red"}
    execute unless entity @a[tag=ev_participa] run return 0

    execute if entity @a[tag=ev_participa,tag=!ev_apto] run return run function evento:admin/falta_acreditar

    function evento:admin/iniciar_ya
""")

f("admin/falta_acreditar", """
    tag @s add ev_lector
    tellraw @a[tag=ev_lector] ["",{"text":"\\n  NO SE PUEDE ARRANCAR TODAVIA\\n","color":"red","bold":true},{"text":"  Estos del grupo no han terminado el Protocolo Luna:\\n","color":"gray"}]
    execute as @a[tag=ev_participa,tag=!ev_apto] run tellraw @a[tag=ev_lector] [{"text":"   x  ","color":"red","bold":true},{"selector":"@s","color":"white"},{"text":"  sin acreditar","color":"dark_gray"}]
    tellraw @a[tag=ev_lector] ["",{"text":"\\n  "},{"text":"[ REVISAR ]","color":"aqua","bold":true,"clickEvent":{"action":"run_command","value":"/function evento:admin/revisar"},"hoverEvent":{"action":"show_text","contents":{"text":"Lista completa del grupo","color":"gray"}}},{"text":"  "},{"text":"[ EMPEZAR IGUAL ]","color":"red","bold":true,"clickEvent":{"action":"run_command","value":"/function evento:admin/iniciar_ya"},"hoverEvent":{"action":"show_text","contents":{"text":"Arranca sin esperar a que se acrediten","color":"gray"}}},{"text":"\\n"}]
    tag @a remove ev_lector
""")

f("admin/revisar", """
    tag @s add ev_lector
    tellraw @a[tag=ev_lector] ["",{"text":"\\n  -- Acreditacion de campo --\\n","color":"gold","bold":true}]
    execute unless entity @a[tag=ev_participa] run tellraw @a[tag=ev_lector] {"text":"   (nadie apuntado todavia)","color":"dark_gray"}
    execute as @a[tag=ev_participa,tag=ev_apto] run tellraw @a[tag=ev_lector] [{"text":"   OK ","color":"green","bold":true},{"selector":"@s","color":"white"},{"text":"  listo","color":"dark_gray"}]
    execute as @a[tag=ev_participa,tag=!ev_apto] run tellraw @a[tag=ev_lector] [{"text":"   x  ","color":"red","bold":true},{"selector":"@s","color":"gray"},{"text":"  le falta el Protocolo Luna","color":"dark_gray"}]
    tellraw @a[tag=ev_lector] {"text":"","color":"gray"}
    tag @a remove ev_lector
""")

f("admin/iniciar_ya", """
    scoreboard players set #ev ev_oak_listo 0
    scoreboard players set #ev ev_senal 0
    scoreboard players set #ev ev_codigo 0
    scoreboard players set @a ev_baliza 0
    scoreboard players set @a ev_m1 0
    scoreboard players set @a ev_m2 0
    scoreboard players set @a ev_m3 0
    scoreboard players set @a ev_m4 0
    scoreboard players set @a ev_m5 0
    scoreboard players set @a ev_m6 0

    function evento:actos/a1
""")

f("admin/saltar", """
    execute if score #ev ev_estado matches 0 run tellraw @s {"text":"[Evento] No hay evento en curso.","color":"red"}
    execute if score #ev ev_estado matches 0 run return 0
    tellraw @s {"text":"[Evento] Saltando al acto siguiente.","color":"yellow"}
    function evento:actos/avanzar
""")

# Reiniciar tiene que dejarlo TODO a cero, no una lista escrita a mano.
#
# La version anterior olvidaba `ev_senal_act`, y eso dejaba el HUD de distancia
# —«Senal el bosque · sigue la aguja»— corriendo para siempre aunque el evento
# estuviera parado. La unica forma de quitarlo era saberse el nombre del
# marcador.
#
# Ahora la lista se deriva de los objetivos que existen de verdad, asi que
# anadir un marcador nuevo no vuelve a dejar restos: se limpia solo.
#
# Se salvan a proposito:
#   ev_modo      completo o corto, es una decision del director
#   ev_sys       el contador interno del reloj
#   ev_unirse    es un `trigger`, lo gestiona el propio juego
_NO_TOCAR = {"ev_modo", "ev_sys", "ev_unirse"}
_GLOBALES = [o for o in _OBJETIVOS_GLOBALES if o not in _NO_TOCAR]
_POR_JUGADOR = [o for o in _OBJETIVOS_JUGADOR if o not in _NO_TOCAR]

f("admin/reiniciar", "\n".join(
    ["function evento:cristales/apagar_todos"]
    + [f"scoreboard players set #ev {o} 0" for o in _GLOBALES]
    + [f"scoreboard players set @a {o} 0" for o in _POR_JUGADOR]
    + ["clear @a minecraft:compass"]
    + ['tellraw @s {"text":"[Evento] Todo a cero. El modo (completo/corto) se mantiene.","color":"yellow"}']
))

f("admin/modo_corto", f"""
    scoreboard players set #ev ev_modo 1
    tellraw @s {{"text":"[Evento] Modo corto: {SENALES_CORTO} senales en vez de {SENALES_COMPLETO}. Unas 2h 20min.","color":"yellow"}}
""")

f("admin/modo_completo", f"""
    scoreboard players set #ev ev_modo 0
    tellraw @s {{"text":"[Evento] Modo completo: {SENALES_COMPLETO} senales. Unas 3h.","color":"yellow"}}
""")

f("admin/estado", f"""
    tellraw @s ["",{{"text":"\\n  ── Estado del evento ──\\n","color":"gold","bold":true}},{{"text":"  Acto:      ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_estado"}},"color":"white"}},{{"text":"  (0 = parado)\\n","color":"dark_gray"}},{{"text":"  Segundos:  ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_reloj"}},"color":"white"}},{{"text":"\\n  Senales:   ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_senal"}},"color":"white"}},{{"text":"\\n  Digitos:   ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_codigo"}},"color":"white"}},{{"text":" de {DIGITOS_NECESARIOS}\\n","color":"dark_gray"}},{{"text":"  Modo:      ","color":"gray"}},{{"score":{{"name":"#ev","objective":"ev_modo"}},"color":"white"}},{{"text":"  (0 = completo)\\n","color":"dark_gray"}}]
""")

def boton(texto, comando, color="white", ayuda=None):
    """Un boton pinchable en el chat. En 1.21.1 el clickEvent sigue usando `value`."""
    d = {"text": texto, "color": color, "bold": True,
         "clickEvent": {"action": "run_command", "value": f"/function evento:{comando}"}}
    if ayuda:
        d["hoverEvent"] = {"action": "show_text", "contents": {"text": ayuda, "color": "gray"}}
    return d


def linea(*trozos):
    return json.dumps(["", *trozos], ensure_ascii=False)


def txt(t, color="gray", **extra):
    return {"text": t, "color": color, **extra}


def marcador(obj):
    return {"score": {"name": "#ev", "objective": obj}, "color": "white", "bold": True}


# Salto de linea de verdad: json.dumps ya se encarga de escaparlo a "\n" en el
# fichero. Escribirlo como escape aqui daria doble barra y Minecraft mostraria
# el texto "\n" en pantalla en vez de saltar.
NL = chr(10)
ESP = txt("  ")
_panel = [
    "# Panel pinchable. En pleno evento no se teclea: se hace clic.",
    "tellraw @s " + linea(
        txt(NL + "  -- EL RASTRO DE LUNA --" + NL, "gold", bold=True),
        txt("  Acto "), marcador("ev_estado"),
        txt("   Senales "), marcador("ev_senal"),
        txt("   Digitos "), marcador("ev_codigo"), txt(NL)),
    # Los botones van EN EL ORDEN EN QUE SE PULSAN el dia del evento. Antes
    # estaban por temas y habia que acordarse de la secuencia; asi el panel la
    # cuenta solo.
    "tellraw @s " + linea(
        txt(NL + "  1 · Preparar  " + NL, "dark_gray"),
        ESP, boton("[ REPARTIR LIBROS ]", "admin/repartir_libros", "light_purple", "Da el libro de misiones a todo el servidor"),
        ESP, boton("[ POBLAR ZONAS ]", "zonas/poblar_todas", "green", "Suelta los 48 Pokemon de las tres zonas"),
        ESP, boton("[ ACREDITADOS ]", "admin/revisar", "gold", "Quien ha terminado las misiones y quien no")),
    "tellraw @s " + linea(
        txt(NL + "  2 · Empezar  " + NL, "dark_gray"),
        ESP, boton("[ INVITAR ]", "admin/invitar", "aqua", "Manda la invitacion a todo el servidor"),
        ESP, boton("[ INICIAR ]", "admin/iniciar", "green", "Arranca el Acto I"),
        ESP, boton("[ ESTADO ]", "admin/estado", "aqua", "Detalle completo")),
    "tellraw @s " + linea(
        txt(NL + "  Si algo se atasca" + NL, "dark_gray"),
        ESP, boton("[ SALTAR ACTO ]", "admin/saltar", "yellow", "Fuerza el acto siguiente"),
        ESP, boton("[ REINICIAR ]", "admin/reiniciar", "red", "Todo a cero"),
        ESP, boton("[ SOLTAR A TODOS ]", "admin/soltar_a_todos", "red", "Saca a quien se quede encerrado")),
    "tellraw @s " + linea(
        txt(NL, "gray"),
        ESP, boton("[ MAS OPCIONES ]", "admin/mas", "dark_gray", "Pruebas, zonas, dialogos y cinematicas"),
        txt(NL)),
]
f("admin/panel", "\n".join(_panel))

# Todo lo que NO se toca el dia del evento.
#
# El panel llego a tener 28 botones y era inservible: para arrancar habia que
# buscar INICIAR entre cinematicas, ensayos y modos de prueba. Arriba se queda
# lo imprescindible; el resto vive aqui, a un clic.
_mas = [
    "tellraw @s " + linea(txt(NL + "  -- MAS OPCIONES --" + NL, "gray", bold=True)),
    "tellraw @s " + linea(
        txt("  Probar" + NL, "dark_gray"),
        ESP, boton("[ PRUEBA EN SOLITARIO ]", "admin/prueba_solo", "yellow", "Al grupo, acreditado, y jefes a nivel 5"),
        ESP, boton("[ MODO REAL ]", "admin/modo_real", "red", "Devuelve los jefes a sus niveles"),
        ESP, boton("[ COMPROBAR ]", "admin/comprobar", "green", "Repaso previo"),
        ESP, boton("[ LIMPIAR ZONAS ]", "zonas/limpiar", "red", "Recoge los Pokemon que sobren")),
    "tellraw @s " + linea(
        txt(NL + "  A mano, si el motor falla" + NL, "dark_gray"),
        ESP, boton("[ GUARDIAN CAIDO ]", "senales/completar", "gold", "Suma una senal"),
        ESP, boton("[ VEX CAIDA ]", "lab/vex_derrotada", "light_purple", "Pasa al Acto V"),
        ESP, boton("[ LUNA CAPTURADA ]", "actos/terminar", "light_purple", "Cierra el evento"),
        ESP, boton("[ RASTREADORES ]", "admin/dar_rastreadores", "aqua", "Uno para cada jugador")),
    "tellraw @s " + linea(
        txt(NL + "  Cinematicas" + NL, "dark_gray"),
        ESP, boton("[ APERTURA ]", "cine/apertura", "gold", "20 s"),
        ESP, boton("[ LABORATORIO ]", "cine/laboratorio", "dark_purple", "7 s"),
        ESP, boton("[ REVELACION ]", "cine/revelacion", "aqua", "26 s"),
        ESP, boton("[ CORTAR ]", "admin/cortar_cine", "red", "Aborta camara y voz")),
    "tellraw @s " + linea(
        txt(NL + "  El grupo" + NL, "dark_gray"),
        ESP, boton("[ VER GRUPO ]", "admin/grupo", "aqua", "Quien esta apuntado"),
        ESP, boton("[ VACIAR GRUPO ]", "admin/vaciar_grupo", "red", "Saca a todos del evento")),
    # Abren el dialogo de un NPC a todo el grupo desde donde estes. Utiles si un
    # NPC se pierde o alguien se salta una escena.
    "tellraw @s " + linea(
        txt(NL + "  Repetir una escena" + NL, "dark_gray"),
        ESP, boton("[ OAK ]", "dialogos/oak_todos", "gold", "La llamada"),
        ESP, boton("[ GRUM ]", "dialogos/grum_todos", "white", "El bosque"),
        ESP, boton("[ SABLE ]", "dialogos/sable_todos", "white", "La montana"),
        ESP, boton("[ NIX ]", "dialogos/nix_todos", "white", "La costa"),
        ESP, boton("[ VEX ]", "dialogos/vex_todos", "light_purple", "El laboratorio")),
    "tellraw @s " + linea(
        txt(NL + "  Otros" + NL, "dark_gray"),
        ESP, boton("[ MODO CORTO ]", "admin/modo_corto", "yellow", "Dos senales en vez de tres"),
        ESP, boton("[ PONER BALIZA ]", "admin/poner_baliza", "white", "Aqui donde estas"),
        ESP, boton("[ QUITAR BALIZAS ]", "admin/quitar_balizas", "red", "Recoge las balizas"),
        ESP, boton("[ AYUDA ]", "admin/ayuda", "gray", "Comandos escritos"),
        ESP, boton("[ VOLVER ]", "admin/panel", "green", "Al panel principal")),
]
f("admin/mas", "\n".join(_mas))

# ===========================================================================
#  Interfaz grafica: el Libro del Director
# ===========================================================================
#
# Un datapack no puede abrir pantallas propias, pero un libro escrito SI es una
# pantalla completa: tipografia, paginas que se pasan, y texto pinchable. Es la
# unica interfaz de verdad que se puede dar sin escribir un mod, y se lee mucho
# mejor que el chat en medio de un evento.
def pagina(*trozos) -> str:
    return json.dumps(["", *trozos], ensure_ascii=False)


def bl(texto, comando, color, ayuda) -> dict:
    """Boton de libro: mas grande y con marco, que se lee de un vistazo."""
    return {"text": f"  ▸ {texto}\n", "color": color, "bold": True,
            "clickEvent": {"action": "run_command", "value": f"/function evento:{comando}"},
            "hoverEvent": {"action": "show_text", "contents": {"text": ayuda, "color": "gray"}}}


def cab(t) -> dict:
    return {"text": f"{t}\n\n", "color": "dark_red", "bold": True, "underlined": True}


def sep() -> dict:
    return {"text": "\n─────────────\n", "color": "gray"}


PAGINAS = [
    pagina(cab("  EL RASTRO\n   DE LUNA"),
           {"text": "  Libro del Director\n", "color": "dark_gray", "italic": True},
           sep(),
           bl("INICIAR", "admin/iniciar", "dark_green", "Arranca el Acto I con su cinemática"),
           bl("ESTADO", "admin/estado", "dark_aqua", "Acto, señales y dígitos"),
           bl("COMPROBAR", "admin/comprobar", "dark_green", "Repaso previo"),
           sep(),
           {"text": "  Pasa la página\n  para el resto.", "color": "dark_gray", "italic": True}),

    pagina(cab("  DURANTE"),
           bl("GUARDIÁN CAÍDO", "senales/completar", "#8B4513", "Suma una señal del Acto II"),
           bl("VEX DERROTADA", "lab/vex_derrotada", "dark_purple", "Pasa al Acto V"),
           bl("LUNA CAPTURADA", "actos/terminar", "dark_purple", "Cierra el evento"),
           sep(),
           bl("SALTAR ACTO", "admin/saltar", "#B8860B", "Fuerza el acto siguiente")),

    pagina(cab("  CINEMÁTICAS"),
           bl("APERTURA", "cine/apertura", "#8B4513", "Cámara + voz de Oak · 20 s"),
           bl("LABORATORIO", "cine/laboratorio", "dark_purple", "Plano de entrada · 7 s"),
           bl("REVELACIÓN", "cine/revelacion", "dark_aqua", "Órbita sobre la cápsula · 26 s"),
           sep(),
           bl("CORTAR", "admin/cortar_cine", "dark_red", "Aborta cámara y voz")),

    pagina(cab("  PREPARAR"),
           bl("MONTAR ZONA", "admin/ensayo/montar", "dark_green", "6 NPCs y 5 balizas a tu alrededor"),
           bl("DESMONTAR", "admin/ensayo/desmontar", "dark_red", "Recoge solo lo del ensayo"),
           sep(),
           bl("RASTREADORES", "admin/dar_rastreadores", "dark_aqua", "Uno para cada jugador"),
           bl("PONER BALIZA", "admin/poner_baliza", "black", "Aquí donde estás")),

    pagina(cab("  EMERGENCIA"),
           bl("MODO CORTO", "admin/modo_corto", "#B8860B", "Salta la señal de la costa"),
           bl("MODO COMPLETO", "admin/modo_completo", "dark_gray", "Las tres señales"),
           sep(),
           bl("REINICIAR", "admin/reiniciar", "dark_red", "Todo a cero"),
           sep(),
           {"text": "  Si algo se atasca,\n  SALTAR ACTO nunca\n  falla.", "color": "dark_gray", "italic": True}),
]

_libro = ("give @s minecraft:written_book["
          "written_book_content={title:\"Libro del Director\",author:\"Profesor Oak\",pages:["
          + ",".join("'" + p.replace("\\", "\\\\").replace("'", "\\'") + "'" for p in PAGINAS)
          + "]},"
          "custom_name='{\"text\":\"Libro del Director\",\"color\":\"gold\",\"italic\":false}',"
          "enchantment_glint_override=true]")

f("admin/libro", f"""
    # La interfaz de verdad: se abre a pantalla completa, se pasan paginas y los
    # botones se pinchan. Se queda en el inventario, no se pierde en el chat.
    {_libro}
    tellraw @s {{"text":"[Evento] Libro del Director entregado. Ábrelo con clic derecho.","color":"gold"}}
""")


f("admin/comprobar", f"""
    # Repaso previo. Lo que no se puede comprobar desde aqui se dice claramente
    # en vez de darlo por bueno.
    tellraw @s ["",{{"text":"\\n  ── Comprobacion previa ──\\n","color":"gold","bold":true}}]

    execute if entity @e[type=cobblemon:npc] run tellraw @s {{"text":"  [OK]   Hay NPCs colocados en el mundo","color":"green"}}
    execute unless entity @e[type=cobblemon:npc] run tellraw @s {{"text":"  [!!]   No hay ningun NPC. Colocalos con /spawnnpc cobblemon:ev_oak","color":"red"}}

    execute if entity @e[type=armor_stand,tag=ev_baliza] run tellraw @s {{"text":"  [OK]   Hay balizas puestas","color":"green"}}
    execute unless entity @e[type=armor_stand,tag=ev_baliza] run tellraw @s {{"text":"  [!!]   No hay balizas. Ponlas con el panel (mision 5)","color":"red"}}

    execute if score #ev ev_estado matches 0 run tellraw @s {{"text":"  [OK]   Evento parado, listo para empezar","color":"green"}}
    execute unless score #ev ev_estado matches 0 run tellraw @s {{"text":"  [!!]   Hay un evento en curso. Reinicialo antes","color":"red"}}

    execute if score #ev ev_modo matches 0 run tellraw @s {{"text":"  [--]   Modo completo: 3 senales, unas 3h","color":"gray"}}
    execute if score #ev ev_modo matches 1 run tellraw @s {{"text":"  [--]   Modo corto: 2 senales, unas 2h 20min","color":"gray"}}

    tellraw @s ["",{{"text":"\\n  A mano, que esto no lo puedo ver:\\n","color":"gray"}},{{"text":"   · El resourcepack de voces esta en el pack del launcher?\\n","color":"dark_gray"}},{{"text":"   · Los escenarios estan construidos?\\n","color":"dark_gray"}},{{"text":"   · La lista blanca esta abierta?\\n","color":"dark_gray"}}]
""")

# ===========================================================================
#  Inscripcion al evento
# ===========================================================================
#
# Solo participa quien acepta. Quien no, sigue a lo suyo sin enterarse: ni voz,
# ni titulos, ni rotulos. Todo lo del evento apunta a @a[tag=ev_participa] en vez
# de a @a.
#
# Se usa `trigger` porque es el unico mecanismo que deja a un jugador sin
# permisos ejecutar algo. El objetivo hay que habilitarlo por jugador cada vez.
f("admin/invitar", """
    scoreboard players enable @a ev_unirse
    scoreboard players set @a ev_unirse 0

    tellraw @a ["",{"text":"\\n"},{"text":"  ── EL RASTRO DE LUNA ──\\n","color":"gold","bold":true},{"text":"  El Profesor Oak busca entrenadores para una expedicion.\\n","color":"white"},{"text":"  Unas tres horas. Se puede salir cuando quieras.\\n\\n","color":"gray"},{"text":"  [ ME APUNTO ]","color":"green","bold":true,"clickEvent":{"action":"run_command","value":"/trigger ev_unirse set 1"},"hoverEvent":{"action":"show_text","contents":{"text":"Te unes al grupo del evento","color":"gray"}}},{"text":"    "},{"text":"[ PASO ]","color":"dark_gray","clickEvent":{"action":"run_command","value":"/trigger ev_unirse set 2"},"hoverEvent":{"action":"show_text","contents":{"text":"Sigues a lo tuyo. No te llegara nada del evento","color":"gray"}}},{"text":"\\n"}]

    tellraw @s {"text":"[Evento] Invitacion enviada a todos.","color":"yellow"}
""")

f("util/inscribir", """
    # Alguien ha pulsado [ ME APUNTO ]
    tag @s add ev_participa
    scoreboard players set @s ev_unirse 0
    scoreboard players enable @s ev_unirse

    title @s times 5 45 12
    title @s subtitle {"text":"Estas dentro","color":"gray"}
    title @s title [{"text":"EL RASTRO DE LUNA","color":"gold","bold":true}]
    playsound minecraft:entity.player.levelup player @s ~ ~ ~ 1 1.3

    tellraw @a[tag=ev_participa] [{"selector":"@s","color":"green"}," se une a la expedicion.",{"text":"","color":"gray"}]
""")

f("util/renunciar", """
    # Ha pulsado [ PASO ], o se sale a mitad
    tag @s remove ev_participa
    scoreboard players set @s ev_unirse 0
    scoreboard players enable @s ev_unirse
    stopsound @s voice
    tellraw @s {"text":"[Evento] Fuera del grupo. No te llegara nada del evento.","color":"gray"}
""")

# Ojo con el `@s` de dentro: en `execute as @a[...] run tellraw @s`, el destino
# pasa a ser cada participante, no quien pulso el boton — la lista se repartia
# entre el grupo y el admin no veia nada. El tag temporal `ev_lector` marca al
# lector antes de cambiar de ejecutor, y el `{"selector":"@s"}` sigue
# resolviendo al participante, que es justo lo que hace falta.
f("admin/grupo", """
    tag @s add ev_lector
    tellraw @a[tag=ev_lector] ["",{"text":"\\n  -- Grupo del evento --\\n","color":"gold","bold":true}]
    execute as @a[tag=ev_participa] run tellraw @a[tag=ev_lector] [{"text":"   . ","color":"dark_gray"},{"selector":"@s","color":"white"}]
    execute unless entity @a[tag=ev_participa] run tellraw @a[tag=ev_lector] {"text":"   (nadie apuntado todavia)","color":"dark_gray"}
    tellraw @a[tag=ev_lector] {"text":"","color":"gray"}
    tag @a remove ev_lector
""")

f("admin/vaciar_grupo", """
    tag @a remove ev_participa
    tellraw @s {"text":"[Evento] Grupo vaciado.","color":"yellow"}
""")


# ===========================================================================
#  Cinematicas
# ===========================================================================
#
# La camara la lleva Cutscene API; la voz y los rotulos, el reloj de escenas que
# ya teniamos. Se lanzan juntos y cuadran solos porque las dos cosas miden lo
# mismo: la duracion real de los clips de audio.
f("cine/apertura", """
    # Acto I: plano de presentacion, SIN voz.
    #
    # La voz de Oak vive ahora en su dialogo de Easy NPC. Si la cinematica
    # tambien la reprodujera, la gente oiria las mismas lineas dos veces.
    # Aqui la camara solo establece el mundo; hablar es cosa de Oak.
    execute as @a[tag=ev_participa] at @s run cutscene start @s evento:apertura ~ ~ ~
    scoreboard players set #ev ev_cine_t 32
""")

f("cine/revelacion", """
    # Acto V. Orbita cerrada sobre la capsula. Lanzar con el grupo ya delante.
    execute as @a[tag=ev_participa] at @s run cutscene start @s evento:revelacion ~ ~ ~
    scoreboard players set #ev ev_esc 2
    scoreboard players set #ev ev_esc_p 0
    scoreboard players set #ev ev_esc_t 0
    scoreboard players set #ev ev_cine_t 38
""")

f("cine/laboratorio", """
    # Plano de establecimiento al abrirse la entrada. Corto y seco.
    execute as @a[tag=ev_participa] at @s run cutscene start @s evento:laboratorio ~ ~ ~
    execute as @a[tag=ev_participa] at @s run playsound minecraft:block.beacon.deactivate voice @s ~ ~ ~ 1 0.6
    scoreboard players set #ev ev_cine_t 18
""")

# --- red de seguridad de las cinematicas -----------------------------------
#
# Cutscene API bloquea las acciones del jugador mientras la camara vuela. Si la
# cinematica no termina limpiamente —el jugador se desconecta a mitad, el
# servidor reinicia, o se abre un dialogo encima— el bloqueo se queda pegado al
# jugador EN EL SERVIDOR: reinstalar el cliente no lo arregla, y la victima no
# puede ni escribir el comando que la liberaria.
#
# Por eso toda cinematica arranca un contador. Cuando se agota, se suelta a todo
# el mundo pase lo que pase. Mas vale cortar un plano por lo sano que dejar a
# alguien encerrado sin chat en mitad del evento.
f("cine/vigilar", """
    scoreboard players remove #ev ev_cine_t 1
    execute if score #ev ev_cine_t matches ..0 run return run function evento:cine/soltar
""")

f("cine/soltar", """
    scoreboard players set #ev ev_cine_t 0
    execute as @a run cutscene stop @s
""")

f("admin/soltar_a_todos", """
    # Boton de panico: saca a cualquiera de una cinematica o dialogo colgado.
    scoreboard players set #ev ev_cine_t 0
    execute as @a run cutscene stop @s
    execute as @a run easy_npc dialog close @s
    function evento:escenas/fin
    tellraw @s {"text":"[Evento] Todo el mundo liberado de cinematicas y dialogos.","color":"yellow"}
""")


f("admin/cortar_cine", """
    execute as @a[tag=ev_participa] run cutscene stop @s
    function evento:escenas/fin
    tellraw @s {"text":"[Evento] Cinematica cortada.","color":"yellow"}
""")


# ===========================================================================
#  Dialogos (Blabber)
# ===========================================================================
#
# El motor abre los dialogos, no el jugador. Antes habia que fiarlo a que
# alguien hiciera clic derecho en el NPC correcto en el momento correcto; los
# dialogos de Cobblemon no pueden ejecutar nada desde dentro porque run_command
# corre con permisos del jugador. `/blabber dialogue start` lo lanza el datapack,
# que si tiene permisos de servidor.
DIALOGOS = [
    ("oak", "oak_llamada", "Profesor Oak"),
    ("grum", "grum_reto", "Grum"),
    ("sable", "sable_reto", "Sable"),
    ("nix", "nix_reto", "Nix"),
    ("guardia", "guardia_alto", "Guardia"),
    ("vex", "vex_encuentro", "Doctora Vex"),
]

for corto, ident, nombre in DIALOGOS:
    f(f"dialogos/{corto}", f"""
    # Abre el dialogo de {nombre} a quien ejecute esto.
    # DESACTIVADO: Blabber trae fabric-permissions-api 0.3.3, que rompe
    # Vanish al conectarse un jugador. Ver docs/incidencia-blabber.md
    say [Evento] Dialogo de {nombre} (Blabber desactivado)
""")
    f(f"dialogos/{corto}_todos", f"""
    # A todo el mundo a la vez, para los momentos de grupo.
    say [Evento] Dialogo de {nombre} (Blabber desactivado)
""")


# ===========================================================================
#  Zona de ensayo
# ===========================================================================
#
# Planta el evento entero alrededor de quien lo lanza, en veinte bloques, para
# poder recorrerlo de punta a punta sin esperar a que esten construidos los
# escenarios de verdad. Los NPCs quedan marcados con el tag ev_npc, asi que se
# recogen sin tocar los NPCs de Cobblemon que haya por el mundo.
ENSAYO = [
    ("ev_oak", "~ ~ ~6", "Oak"),
    ("ev_grum", "~12 ~ ~", "Grum - senal 1"),
    ("ev_sable", "~ ~ ~-12", "Sable - senal 2"),
    ("ev_nix", "~-12 ~ ~", "Nix - senal 3"),
    ("ev_guardia", "~8 ~ ~14", "Guardia - lab sala 1"),
    ("ev_vex", "~-8 ~ ~14", "Vex - lab sala 3"),
]

_montar = ["# Se lanza desde donde quieras el centro de la zona de ensayo."]
for ident, pos, _ in ENSAYO:
    _montar.append(f'execute positioned {pos} run summon cobblemon:npc ~ ~ ~ {{NPCClass:"cobblemon:{ident}"}}')
    _montar.append(f"execute positioned {pos} run function evento:ensayo/marcar")
_montar += [
    "",
    "# Cinco balizas en circulo, para la mision 5.",
    "execute positioned ~20 ~ ~ run function evento:ensayo/baliza",
    "execute positioned ~6 ~ ~19 run function evento:ensayo/baliza",
    "execute positioned ~-16 ~ ~12 run function evento:ensayo/baliza",
    "execute positioned ~-16 ~ ~-12 run function evento:ensayo/baliza",
    "execute positioned ~6 ~ ~-19 run function evento:ensayo/baliza",
    "",
    'tellraw @s ["",{"text":"\\n  Zona de ensayo montada.\\n","color":"green","bold":true},'
    '{"text":"  6 NPCs y 5 balizas a tu alrededor.\\n","color":"gray"},'
    '{"text":"  Recogelo todo con [ DESMONTAR ] en el panel.\\n","color":"dark_gray"}]',
]
f("admin/ensayo/montar", "\n".join(_montar))

f("ensayo/marcar", """
    # El recien nacido es el NPC sin marcar mas cercano al punto de invocacion.
    # Marcarlos permite recogerlos luego sin barrer los de todo el mundo.
    tag @e[type=cobblemon:npc,tag=!ev_npc,distance=..4,limit=1,sort=nearest] add ev_npc
""")

f("ensayo/baliza", """
    summon armor_stand ~ ~ ~ {Tags:["ev_baliza","ev_npc"],Invisible:1b,Invulnerable:1b,NoGravity:1b,Marker:1b}
""")

f("admin/ensayo/desmontar", """
    # Solo lo del ensayo: los NPCs de Cobblemon que haya por el mundo se quedan.
    kill @e[type=cobblemon:npc,tag=ev_npc]
    kill @e[type=armor_stand,tag=ev_baliza]
    scoreboard players set @a ev_baliza 0
    tellraw @s {"text":"[Evento] Zona de ensayo recogida.","color":"yellow"}
""")

f("admin/ensayo/probar_todo", """
    # Recorrido rapido de los cinco actos para ver que la cadena entera responde.
    # No sustituye al ensayo con gente: solo comprueba el motor.
    function evento:admin/reiniciar
    function evento:admin/iniciar
    tellraw @s {"text":"[Ensayo] Acto I lanzado. Pulsa GUARDIAN CAIDO tres veces para llegar al III.","color":"aqua"}
""")


f("admin/soy_admin", """
    # Los avisos internos van a quien lleve este tag.
    tag @s add ev_admin
    tellraw @s {"text":"[Evento] Vas a recibir los avisos de administracion.","color":"yellow"}
    function evento:admin/libro
""")

f("admin/ayuda", """
    tellraw @s ["",{"text":"\\n  ── Evento: El Rastro de Luna ──\\n","color":"gold","bold":true},{"text":"  /function evento:admin/","color":"gray"},{"text":"iniciar","color":"white"},{"text":"        empieza el Acto I\\n","color":"dark_gray"},{"text":"  /function evento:admin/","color":"gray"},{"text":"estado","color":"white"},{"text":"         como va todo\\n","color":"dark_gray"},{"text":"  /function evento:admin/","color":"gray"},{"text":"saltar","color":"white"},{"text":"         fuerza el acto siguiente\\n","color":"dark_gray"},{"text":"  /function evento:admin/","color":"gray"},{"text":"reiniciar","color":"white"},{"text":"      todo a cero\\n","color":"dark_gray"},{"text":"  /function evento:admin/","color":"gray"},{"text":"modo_corto","color":"white"},{"text":"     salta la costa\\n","color":"dark_gray"},{"text":"  /function evento:admin/","color":"gray"},{"text":"modo_completo","color":"white"},{"text":"  las tres senales\\n","color":"dark_gray"},{"text":"\\n  Durante el evento:\\n","color":"gray"},{"text":"  evento:senales/completar","color":"white"},{"text":"   guardian derrotado\\n","color":"dark_gray"},{"text":"  evento:lab/vex_derrotada","color":"white"},{"text":"   cae Vex\\n","color":"dark_gray"},{"text":"  evento:actos/terminar","color":"white"},{"text":"      Luna capturada\\n","color":"dark_gray"},{"text":"  evento:misiones/m1","color":"white"},{"text":" … ","color":"dark_gray"},{"text":"m6","color":"white"},{"text":"      mision superada\\n","color":"dark_gray"}]
""")


# ===========================================================================
#  Empaquetado
# ===========================================================================
# ===========================================================================
#  Sala de espera
# ===========================================================================
#
# Retiene a la gente en un punto con la cuenta atras a la vista mientras se
# termina de preparar el evento. Se les repone la posicion en cada tick en vez
# de fiarlo solo a los efectos: la lentitud no impide caerse ni alejarse
# despacio, y aqui lo que interesa es que nadie se disperse.
#
# Los admin quedan fuera: hay que poder moverse para colocar cosas.

f("sala/abrir", """
    scoreboard players set #ev ev_sala 1
    bossbar set evento:sala visible true
    bossbar set evento:sala players @a
    effect give @a[tag=!ev_admin] minecraft:resistance 999999 4 true
    effect give @a[tag=!ev_admin] minecraft:saturation 999999 0 true
    effect give @a[tag=!ev_admin] minecraft:slowness 999999 6 true
    # La ceguera acerca la niebla hasta que no se ve el mundo: es lo mas parecido
    # a una pantalla de carga que se puede imponer desde el servidor.
    effect give @a[tag=!ev_admin] minecraft:blindness 999999 0 true
    tellraw @a[tag=ev_admin] {"text":"[Evento] Sala de espera abierta.","color":"green"}
    function evento:sala/latido
""")

f("sala/abrir5",  "scoreboard players set #ev ev_sala_t 300\nfunction evento:sala/abrir")
f("sala/abrir10", "scoreboard players set #ev ev_sala_t 600\nfunction evento:sala/abrir")
f("sala/abrir15", "scoreboard players set #ev ev_sala_t 900\nfunction evento:sala/abrir")

f("sala/retener", """
    execute as @a[tag=!ev_admin] at @s unless entity @s[distance=..1.5] run tp @s 1084.5 66 530.5
""")

f("sala/latido", """
    scoreboard players remove #ev ev_sala_t 1
    function evento:sala/pintar
    execute if score #ev ev_sala_t matches ..0 run function evento:sala/empezar
""")

f("sala/cuenta_grande", """
    title @a[tag=!ev_admin] times 0 25 5
    title @a[tag=!ev_admin] subtitle {"text":"segundos","color":"gray"}
    title @a[tag=!ev_admin] title [{"score":{"name":"#ev","objective":"ev_sala_t"},"color":"light_purple","bold":true}]
    execute as @a[tag=!ev_admin] at @s run playsound minecraft:block.note_block.pling voice @s ~ ~ ~ 1 1.5
""")

f("sala/pintar", """
    bossbar set evento:sala players @a
    execute store result bossbar evento:sala value run scoreboard players get #ev ev_sala_t

    # El nombre de la barra es el canal por el que viaja la senal al mod de la sala:
    # un datapack no puede mandar paquetes propios, pero si puede renombrar una barra.
    # Sin el mod instalado se ve una barra normal con la cuenta, que tampoco estorba.
    execute store result storage evento:sala seg int 1 run scoreboard players get #ev ev_sala_t
    function evento:sala/nombrar with storage evento:sala
    title @a[tag=!ev_admin] actionbar ["",{"text":"El evento empieza en ","color":"gray"},{"score":{"name":"#ev","objective":"ev_sala_t"},"color":"light_purple","bold":true},{"text":" s","color":"gray"}]

    # Aviso grande solo en los hitos: repetir el titulo cada segundo parpadea feo.
    execute if score #ev ev_sala_t matches 300 run function evento:sala/cuenta_grande
    execute if score #ev ev_sala_t matches 120 run function evento:sala/cuenta_grande
    execute if score #ev ev_sala_t matches 60 run function evento:sala/cuenta_grande
    execute if score #ev ev_sala_t matches 30 run function evento:sala/cuenta_grande
    execute if score #ev ev_sala_t matches 1..10 run function evento:sala/cuenta_grande
""")

f("sala/empezar", """
    scoreboard players set #ev ev_sala 0
    scoreboard players set #ev ev_sala_t 0
    bossbar set evento:sala visible false

    effect clear @a minecraft:slowness
    effect clear @a minecraft:blindness
    effect clear @a minecraft:resistance
    effect clear @a minecraft:saturation

    tp @a[tag=!ev_admin] 1084.5 66 530.5

    title @a times 10 70 20
    title @a subtitle {"text":"Buscad al Profesor Oak","color":"gray"}
    title @a title [{"text":"EL RASTRO DE LUNA","color":"light_purple","bold":true}]
    execute as @a at @s run playsound minecraft:block.beacon.activate voice @s ~ ~ ~ 1 1
    tellraw @a {"text":"  El evento ha comenzado. Hablad con el Profesor Oak.","color":"gold"}
""")

f("sala/nombrar", """
    $bossbar set evento:sala name {"text":"[[LUNA]] $(seg)"}
""")

f("sala/cerrar", """
    scoreboard players set #ev ev_sala 0
    bossbar set evento:sala visible false
    effect clear @a minecraft:slowness
    effect clear @a minecraft:blindness
    effect clear @a minecraft:resistance
    effect clear @a minecraft:saturation
    tellraw @a[tag=ev_admin] {"text":"[Evento] Sala cerrada sin empezar.","color":"yellow"}
""")


def avances() -> dict:
    """Genera los avances que detectan las misiones.

    Cobblemon filtra por **especie**, no por tipo: se comprobo leyendo
    PartyCheckCriterion, que trabaja sobre Species. Asi que «captura un
    siniestro» se escribe como una alternativa por cada especie siniestra, y la
    lista sale del propio jar del mod (evento/datos/tipos_cobblemon.json), no
    escrita a mano.
    """
    tipos = json.load(open(os.path.join(RAIZ, "datos", "tipos_cobblemon.json"), encoding="utf-8"))
    salida = {}

    def por_tipo(nombre, tipo, recompensa):
        especies = tipos[tipo]
        criterios = {
            e: {"trigger": "cobblemon:catch_pokemon",
                "conditions": {"count": 1, "species": f"cobblemon:{e}"}}
            for e in especies
        }
        salida[f"data/evento/advancement/{nombre}.json"] = json.dumps({
            "criteria": criterios,
            # Una sola lista = "cualquiera de estos vale".
            "requirements": [list(criterios)],
            "rewards": {"function": f"evento:misiones/paso_{recompensa}"},
        }, indent=1)
        return len(especies)

    n_dark = por_tipo("captura_siniestro", "dark", "captura_siniestro")
    n_ice = por_tipo("captura_hielo", "ice", "captura_hielo")

    # La captura de Luna cierra el evento sola.
    #
    # Aqui el filtro por especie —la unica limitacion de Cobblemon, que tanto
    # estorbo para "captura un siniestro"— es justo lo que hace falta: hay una
    # sola Luna y basta con nombrarla.
    salida["data/evento/advancement/captura_luna.json"] = json.dumps({
        "criteria": {"luna": {"trigger": "cobblemon:catch_pokemon",
                              "conditions": {"count": 1, "species": "pokereport:luna"}}},
        "rewards": {"function": "evento:actos/terminar"},
    }, indent=1)

    salida["data/evento/advancement/veterano.json"] = json.dumps({
        "criteria": {"combates": {"trigger": "cobblemon:battles_won", "conditions": {"count": 5}}},
        "rewards": {"function": "evento:misiones/paso_veterano"},
    }, indent=1)

    salida["data/evento/advancement/subir_nivel_40.json"] = json.dumps({
        "criteria": {"nivel": {"trigger": "cobblemon:level_up", "conditions": {"level": 40}}},
        "rewards": {"function": "evento:misiones/paso_subir_nivel_40"},
    }, indent=1)

    salida["data/evento/advancement/pescar.json"] = json.dumps({
        "criteria": {"pesca": {"trigger": "cobblemon:reel_in_pokemon", "conditions": {}}},
        "rewards": {"function": "evento:misiones/paso_pescar"},
    }, indent=1)

    print(f"   avances: siniestro({n_dark} especies), hielo({n_ice}), veterano, nivel_40, pescar")
    return salida


def main() -> int:
    otros = {
        "pack.mcmeta": json.dumps({
            "pack": {
                "pack_format": PACK_FORMAT,
                "description": "PokeReport · El Rastro de Luna — motor del evento",
            }
        }, indent=2, ensure_ascii=False),
        "data/minecraft/tags/function/load.json": json.dumps({"values": ["evento:cargar"]}, indent=2),
        "data/minecraft/tags/function/tick.json": json.dumps({"values": ["evento:reloj"]}, indent=2),
    }

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        av = avances()
        for ruta, texto in {**otros, **ficheros, **av}.items():
            z.writestr(ruta, texto)

    print(f"   {SALIDA}")
    print(f"   {len(ficheros)} funciones, {len(av)} avances, {os.path.getsize(SALIDA)/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
