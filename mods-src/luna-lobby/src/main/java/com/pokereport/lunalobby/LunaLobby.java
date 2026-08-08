package com.pokereport.lunalobby;

import com.pokereport.lunalobby.mixin.BossOverlayAccessor;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.LerpingBossEvent;

/**
 * Abre y cierra la pantalla de espera siguiendo una barra de jefe del servidor.
 *
 * Un datapack no puede enviar paquetes propios, asi que en vez de inventar un canal se aprovecha
 * algo que el servidor ya sabe mandar: una barra de jefe cuyo nombre lleva un prefijo acordado y
 * los segundos que faltan. El mod la lee, la reconoce y abre la pantalla; cuando el servidor la
 * oculta, la pantalla se cierra sola.
 */
public class LunaLobby implements ClientModInitializer {

	/** Prefijo que marca la barra como "senal de sala", no como un jefe de verdad. */
	public static final String MARCA = "[[LUNA]]";

	private static int segundos = -1;

	@Override
	public void onInitializeClient() {
		ClientTickEvents.END_CLIENT_TICK.register(LunaLobby::tick);
	}

	private static void tick(Minecraft client) {
		if (client.level == null) {
			cerrar(client);
			return;
		}

		int leidos = leerSegundos(client);
		if (leidos < 0) {
			cerrar(client);
			return;
		}

		segundos = leidos;
		if (!(client.screen instanceof LobbyScreen)) {
			client.setScreen(new LobbyScreen());
		}
	}

	/** Devuelve los segundos que anuncia la barra, o -1 si no hay ninguna barra de sala. */
	private static int leerSegundos(Minecraft client) {
		BossOverlayAccessor overlay = (BossOverlayAccessor) client.gui.getBossOverlay();
		for (LerpingBossEvent evento : overlay.lunalobby$getEvents().values()) {
			String nombre = evento.getName().getString();
			if (!nombre.startsWith(MARCA)) continue;

			try {
				return Integer.parseInt(nombre.substring(MARCA.length()).trim());
			} catch (NumberFormatException ignorado) {
				return 0;
			}
		}
		return -1;
	}

	private static void cerrar(Minecraft client) {
		segundos = -1;
		if (client.screen instanceof LobbyScreen) {
			client.setScreen(null);
		}
	}

	public static int segundos() {
		return segundos;
	}
}
