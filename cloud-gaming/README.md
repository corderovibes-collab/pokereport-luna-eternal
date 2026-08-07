# cloud-gaming — reconstrucción transparente de Colab-Cloud-Gaming

Adaptación de [kmille36/Colab-Cloud-Gaming](https://github.com/kmille36/Colab-Cloud-Gaming)
a Minecraft + Cobbleverse, con todo el código a la vista.

El análisis de viabilidad y las alternativas están en [`docs/cloud-gaming.md`](../docs/cloud-gaming.md).
Esto es la parte ejecutable.

## Ficheros

| Fichero | Qué es |
|---|---|
| `diagnostico.py` | Comprueba si tu runtime de Colab puede hacer streaming. No instala nada |
| `build_notebook.py` | Genera el notebook. El diagnóstico se empotra desde su fichero, no se duplica |
| `PokeReport-Colab.ipynb` | El notebook para subir a Colab |

Para regenerar el notebook tras tocar el diagnóstico:

```bash
python build_notebook.py
```

## Por qué está reescrito y no se usa el original

Los dos ejecutables del repo original (`ColabSteam`, `colab-moonweb`) son **ELF x86-64 generados
con shc**, que cifra un script bash con RC4 dentro del binario. Se confirma por la firma
`E: neither argv[0] nor $_ works.` y por tener 61 cadenas, todas de libc, y ninguna de aplicación.

El notebook original te ofrece montar tu Google Drive **antes** de ejecutarlos como root. No digo
que hagan nada malo: digo que no hay forma de saberlo. Aquí no hay binarios.

## Empieza por el diagnóstico

```bash
python3 diagnostico.py
```

Tarda 30 s, no modifica el sistema, y responde a una sola pregunta: **¿puede salir el vídeo UDP
de este contenedor?** Devuelve uno de tres veredictos:

| Veredicto | Significado | Siguiente paso |
|---|---|---|
| `CAMINO ABIERTO` | Se pudo crear una interfaz TUN | Celda 3 del notebook |
| `NO VIABLE` | Sin `CAP_NET_ADMIN` no hay TUN, luego no hay VPN, luego no hay UDP | `docs/cloud-gaming.md` |
| `sin GPU` | No te asignaron T4 | Cambiar el tipo de entorno y repetir |

El resultado esperado hoy es **`NO VIABLE`**, por la cadena de restricciones explicada en el
informe. El diagnóstico existe precisamente para que no tengas que fiarte de eso: lo mide en tu
runtime, no en el mío.

Si algún día Colab cambia, este script lo detectará y el resto del notebook entra en juego.

## Qué hace el notebook si el diagnóstico pasa

1. **Audio anti-desconexión** — igual que el `silence.m4a` original.
2. **Diagnóstico** — la celda que decide.
3. **Entorno gráfico** — Xvfb (display) + **VirtualGL con backend EGL** (render en la T4) +
   Sunshine (captura y codifica con NVENC).
   Sin VirtualGL, Minecraft renderizaría con llvmpipe sobre 2 vCPU y no serviría de nada.
4. **Minecraft** — Java 21 + Prism Launcher + tu `.mrpack` **1.7.42 exacto** desde Drive.
5. **Túnel** — Tailscale. Falla a propósito si el diagnóstico dijo `NO VIABLE`, en vez de montar
   un túnel TCP que da 300 ms y aparenta funcionar hasta que intentas jugar.
6. **Emparejar Moonlight** — como `moon-pair.sh`, pero sin dejar la contraseña en `admin:admin`.
7. **Copia a Drive** — porque Colab borra el disco entero al cerrar.

## Dos avisos que no son opinión

**Tu launcher no funciona aquí.** `launcher/electron-builder.yml` solo compila target `nsis` para
Windows x64, y Colab es Linux. Por eso el notebook usa Prism Launcher, que es la *Opción B* de
[`docs/cliente.md`](../docs/cliente.md) y acepta el mismo `.mrpack`.

**Usa una cuenta de Google desechable.** El FAQ de Colab prohíbe *"using a remote desktop or SSH"*
y avisa de que esas sesiones *"may be terminated at any time without warning"*. La cuenta de Colab
es la cuenta de Google entera: Gmail, Drive, YouTube.

## Estado

El diagnóstico está verificado sintácticamente y su lógica es autocontenida (solo stdlib).
Las celdas de montaje (3 a 7) **no se han podido probar de extremo a extremo**, porque para
ejecutarlas hace falta un runtime de Colab con la restricción levantada. Están escritas para
fallar de forma ruidosa y explicada, no en silencio.
