package com.pokereport.lunalobby;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * Pantalla de espera a pantalla completa.
 *
 * El fondo se dibuja opaco de lado a lado a proposito: es lo que oculta el mundo. No se usa el
 * fondo por defecto de las pantallas porque ese solo oscurece, y por debajo se seguiria viendo
 * el terreno y a los demas jugadores moverse.
 */
public class LobbyScreen extends Screen {

	private static final int FONDO_ARRIBA = 0xFF120A24;
	private static final int FONDO_ABAJO = 0xFF05030A;
	private static final int LUNA = 0xFFE8E2FF;
	private static final int MORADO = 0xFFB98CFF;

	public LobbyScreen() {
		super(Component.literal("El Rastro de Luna"));
	}

	/** Sin pausa: el mundo debe seguir corriendo mientras se espera. */
	@Override
	public boolean isPauseScreen() {
		return false;
	}

	/** No se cierra con ESC: la pantalla la quita el servidor, no el jugador. */
	@Override
	public boolean shouldCloseOnEsc() {
		return false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mouseX, int mouseY, float partial) {
		g.fillGradient(0, 0, this.width, this.height, FONDO_ARRIBA, FONDO_ABAJO);
		estrellas(g);
		luna(g, this.width / 2, this.height / 3, Math.min(this.width, this.height) / 7);
	}

	/**
	 * Estrellas colocadas con una secuencia determinista.
	 *
	 * Interesa que no parpadeen ni salten de sitio entre fotogramas, asi que la posicion se
	 * calcula a partir del indice y no de un generador aleatorio nuevo en cada render.
	 */
	private void estrellas(GuiGraphics g) {
		for (int i = 0; i < 140; i++) {
			int x = (int) ((i * 7919L) % Math.max(1, this.width));
			int y = (int) ((i * 6271L) % Math.max(1, this.height));
			int brillo = 120 + (i * 37) % 120;
			int color = (brillo << 24) | 0xFFFFFF;
			g.fill(x, y, x + 1, y + 1, color);
			if (i % 17 == 0) {
				g.fill(x, y + 1, x + 1, y + 2, color);
				g.fill(x + 1, y, x + 2, y + 1, color);
			}
		}
	}

	/** Disco lleno dibujado por franjas horizontales, con un halo suave alrededor. */
	private void luna(GuiGraphics g, int cx, int cy, int radio) {
		for (int capa = 3; capa >= 1; capa--) {
			int r = radio + capa * 6;
			int alfa = 0x10 * capa;
			franjas(g, cx, cy, r, (alfa << 24) | (MORADO & 0xFFFFFF));
		}
		franjas(g, cx, cy, radio, LUNA);
		franjas(g, cx - radio / 3, cy - radio / 4, (int) (radio * 0.85), FONDO_ARRIBA);
	}

	private void franjas(GuiGraphics g, int cx, int cy, int radio, int color) {
		for (int dy = -radio; dy <= radio; dy++) {
			int dx = (int) Math.sqrt((double) radio * radio - (double) dy * dy);
			g.fill(cx - dx, cy + dy, cx + dx, cy + dy + 1, color);
		}
	}

	@Override
	public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
		this.renderBackground(g, mouseX, mouseY, partial);

		int centro = this.width / 2;
		int base = this.height / 2 + this.height / 8;

		texto(g, "EL RASTRO DE LUNA", centro, base - 34, 2.0F, MORADO);

		int s = LunaLobby.segundos();
		if (s > 0) {
			texto(g, reloj(s), centro, base + 6, 4.0F, LUNA);
			g.drawCenteredString(this.font, Component.literal("El evento comienza en breve")
					.withStyle(ChatFormatting.GRAY), centro, base + 52, 0xFFFFFFFF);
		} else {
			texto(g, "YA", centro, base + 6, 4.0F, LUNA);
		}

		g.drawCenteredString(this.font, Component.literal("Esperando a los entrenadores...")
				.withStyle(ChatFormatting.DARK_GRAY), centro, this.height - 20, 0xFFFFFFFF);
	}

	private String reloj(int segundos) {
		return String.format("%d:%02d", segundos / 60, segundos % 60);
	}

	/** Dibuja centrado y escalado; el texto del juego solo tiene un tamano. */
	private void texto(GuiGraphics g, String txt, int cx, int cy, float escala, int color) {
		g.pose().pushPose();
		g.pose().translate(cx, cy, 0);
		g.pose().scale(escala, escala, 1.0F);
		g.drawCenteredString(this.font, txt, 0, 0, color);
		g.pose().popPose();
	}
}
