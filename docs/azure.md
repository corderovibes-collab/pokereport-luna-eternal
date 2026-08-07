# Azure: activar el inicio de sesión con Minecraft original

## Antes de nada: para este servidor probablemente NO te hace falta

El servidor está en **modo offline** (`online-mode=false`). Ahí Mojang no valida a
nadie, así que iniciar sesión con Microsoft **no aporta ningún privilegio**.

Lo único que da el login de Microsoft es el nombre y la skin automáticos, y eso
**ya está resuelto sin Azure**:

- Quien tenga el juego comprado crea una **cuenta offline con su nombre de siempre**.
- El launcher busca ese nombre en Mojang y **le pone su skin de verdad**.
- El servidor hace lo mismo con SkinRestorer, para que los demás también la vean.
- La identidad la protege **EasyAuth** con contraseña, que en modo offline es lo que
  de verdad importa.

Con eso, un jugador premium entra con su nombre y su skin sin tocar Azure. **Mi
recomendación es que te ahorres todo lo de abajo**, salvo que algún día pongas el
servidor en `online-mode=true`.

## Y si aun así lo quieres montar: ya no son 5 minutos

Microsoft cambió las reglas. Ahora **una aplicación de Azure recién creada no puede
usar la API de Minecraft hasta que Mojang la apruebe**: `api.minecraftservices.com`
devuelve **403** hasta entonces.

Hay que rellenar el formulario de revisión (**<https://aka.ms/mce-reviewappid>**) y
esperar respuesta. Las apps creadas antes de ese cambio siguen funcionando, pero una
nueva no. O sea: registro rápido, pero **aprobación que puede tardar días**.

Sabiendo eso, si quieres seguir:

- Vale cualquier cuenta de Microsoft; **no** hace falta tarjeta ni suscripción de Azure.
- Lo haces **tú una sola vez**. Tus amigos no tienen que hacer nada de esto.

### Si portal.azure.com no te deja entrar con tu correo personal

Es lo normal: el portal empuja a contratar una suscripción. Dos salidas:

1. Entra por **<https://entra.microsoft.com>** (centro de administración de Microsoft
   Entra). Los registros de aplicaciones están ahí y **no piden suscripción**.
2. O ve directo a la sección con este enlace:
   <https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade>

Si te dice que la cuenta no existe, es que ese correo **no está dado de alta como
cuenta de Microsoft**. Se crea gratis en <https://signup.live.com> con el correo que ya
tienes; no hace falta cambiar de dirección ni que sea de empresa.

## Paso a paso

### 1. Entrar al portal

Ve a **[portal.azure.com](https://portal.azure.com)** e inicia sesión con tu cuenta de
Microsoft.

Si te pide crear una suscripción o meter una tarjeta, **ignóralo**: para registrar una
aplicación no hace falta.

### 2. Ir a registros de aplicaciones

En el buscador de arriba escribe **`Microsoft Entra ID`** y entra.
(Antes se llamaba *Azure Active Directory*; si tu portal aún lo llama así, es lo mismo.)

En el menú de la izquierda: **Registros de aplicaciones** → **+ Nuevo registro**.

### 3. Rellenar el registro

| Campo | Qué poner |
|---|---|
| **Nombre** | `PokeReport Launcher` (lo ves solo tú) |
| **Tipos de cuenta compatibles** | **Cuentas de cualquier directorio y cuentas personales de Microsoft** |
| **URI de redirección** | Déjalo **vacío** |

> El tipo de cuenta importa: las de Minecraft son **cuentas personales**. Si eliges
> "solo cuentas de este directorio", tus amigos no podrán entrar.
>
> El launcher pide el token contra el inquilino `consumers` (no `common` ni el id de
> tu directorio), que es lo único que acepta el permiso `XboxLive.signin`. Eso ya está
> así en el código, no tienes que configurarlo.

Dale a **Registrar**.

### 4. Activar el flujo de cliente público ← el paso que se olvida

En el menú de la izquierda de la aplicación recién creada: **Autenticación**.

1. Baja hasta **Configuración avanzada**.
2. En **Permitir flujos de cliente público**, pon **Sí**.
3. **Guardar**.

Sin esto, el código que sale en el launcher se genera pero Microsoft rechaza el login
al final. Es el fallo más habitual.

### 5. Copiar el Client ID

Vuelve a **Información general** de la aplicación. Copia el
**Id. de aplicación (cliente)**. Es algo así:

```
4f1c2b8e-9a3d-4c7e-b012-6d8f5a1e3c94
```

### 6. Pegarlo en el launcher

Abre el launcher → **Ajustes** → **Client ID de Azure** → pega y sal del campo (se
guarda solo).

### 7. Pedir la aprobación a Mojang

Rellena **<https://aka.ms/mce-reviewappid>** con el Client ID. Hasta que te respondan,
el login fallará con **403** al llegar a `api.minecraftservices.com`. Cuando lo
aprueben, pueden tardar otras 24 h en aplicarse los cambios.

## Comprobar que funciona

1. **Cuentas** → **Iniciar sesión con Microsoft**.
2. Sale un código de 8 caracteres y un enlace a `microsoft.com/link`.
3. Se abre el navegador, metes el código, inicias sesión y aceptas.
4. El launcher lo detecta solo y añade la cuenta con su nombre real.
5. En **Tu personaje** aparece la skin de esa cuenta, cargada de Mojang.

## Si algo falla

| Lo que ves | Qué pasa |
|---|---|
| `Falta el Client ID de Azure` | No lo has pegado en Ajustes, o se pegó con espacios |
| El código caduca sin hacer nada | No autorizaste a tiempo (hay ~15 min). Vuelve a darle |
| `AADSTS7000218` o similar | Falta el paso 4: **Permitir flujos de cliente público → Sí** |
| `Esta cuenta de Microsoft no tiene Minecraft: Java Edition` | La cuenta no tiene el juego comprado, o es Bedrock (que no vale). **Ojo**: también sale así si Mojang aún no ha aprobado tu app (responde 403) |
| `Xbox Live rechazó la cuenta` | Esa cuenta no tiene perfil de Xbox creado. Se crea gratis entrando una vez en [xbox.com](https://www.xbox.com) |
| Cuenta de menor de edad | Tiene que estar en un **grupo familiar** de Microsoft con un adulto |

## Una cosa importante sobre este servidor

El servidor está en **modo offline** (`online-mode=false`), que es lo que permite
entrar a quien no tiene el juego comprado.

Consecuencia a tener clara: **en modo offline, el servidor no distingue** entre una
cuenta original y una offline. Iniciar sesión con Microsoft en el launcher sirve para:

- Tener tu nombre y tu skin correctos automáticamente.
- Que el UUID sea el de tu cuenta real.

…pero no da ningún privilegio dentro del servidor. Quien entre con el mismo nombre por
offline entraría igual. Para eso está **EasyAuth**, que pide contraseña a cada jugador
(ver [operacion.md](operacion.md)).

Si algún día quieres que **solo** entren cuentas originales, se cambia
`online-mode=true` en `server.properties`, y entonces sí que Mojang valida a cada
jugador. Perderías la posibilidad de que entren los que no lo tienen comprado.
