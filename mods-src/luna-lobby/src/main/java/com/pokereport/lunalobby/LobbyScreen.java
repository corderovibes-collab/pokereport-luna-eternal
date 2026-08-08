package com.pokereport.lunalobby;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceLocation;

/**
 * Pantalla de espera a pantalla completa.
 *
 * El fondo se dibuja opaco de borde a borde: es lo que oculta el mundo. No se usa el fondo por
 * defecto de las pantallas porque ese solo oscurece, y por debajo se seguiria viendo el terreno
 * y a los demas jugadores moverse.
 *
 * Las medidas estan tomadas sobre un maquetado de 1920x1080 y se reescalan con la altura real,
 * de modo que la composicion se mantiene igual en cualquier resolucion.
 */
public class LobbyScreen extends Screen {

	private static final ResourceLocation FONDO =
			ResourceLocation.fromNamespaceAndPath("lunalobby", "textures/gui/fondo.png");

	private static final ResourceLocation FUENTE =
			ResourceLocation.fromNamespaceAndPath("lunalobby", "luna");

	private static final int ANCHO_ARTE = 1920;
	private static final int ALTO_ARTE = 1080;

	private static final int PLATA = 0xFFF6F2FF;
	private static final int LILA = 0xFFEFE6FF;
	private static final int GRIS = 0xFF9C93B8;

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

	/**
	 * Dibuja el arte cubriendo la pantalla entera.
	 *
	 * Se escala por el lado que mas falta cubrir y se recorta el sobrante en vez de estirar la
	 * imagen a la resolucion: en pantallas panoramicas, estirar un 16:9 deformaria a Luna.
	 */
	@Override
	public void renderBackground(GuiGraphics g, int mouseX, int mouseY, float partial) {
		float escala = Math.max((float) this.width / ANCHO_ARTE, (float) this.height / ALTO_ARTE);
		int ancho = Math.round(ANCHO_ARTE * escala);
		int alto = Math.round(ALTO_ARTE * escala);
		int x = (this.width - ancho) / 2;
		int y = (this.height - alto) / 2;

		g.blit(FONDO, x, y, ancho, alto, 0.0F, 0.0F, ANCHO_ARTE, ALTO_ARTE, ANCHO_ARTE, ALTO_ARTE);
	}

	@Override
	public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
		this.renderBackground(g, mouseX, mouseY, partial);

		float k = this.height / (float) ALTO_ARTE;
		int centro = this.width / 2;

		texto(g, espaciar("EL RASTRO DE LUNA"), centro, alto(0.359F), 1.9F * k, LILA);

		int s = LunaLobby.segundos();
		texto(g, s > 0 ? reloj(s) : "YA", centro, alto(0.800F), 7.0F * k, PLATA);

		texto(g, espaciar("EL EVENTO COMIENZA EN BREVE"), centro, alto(0.936F), 1.2F * k, GRIS);
	}

	private int alto(float proporcion) {
		return Math.round(this.height * proporcion);
	}

	private String reloj(int segundos) {
		return String.format("%d:%02d", segundos / 60, segundos % 60);
	}

	/** El juego no sabe separar letras, asi que el espaciado se compone a mano. */
	private String espaciar(String txt) {
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < txt.length(); i++) {
			if (i > 0) sb.append(' ');
			sb.append(txt.charAt(i));
		}
		return sb.toString();
	}

	/** Dibuja centrado y escalado; una fuente del juego solo tiene un tamano. */
	private void texto(GuiGraphics g, String txt, int cx, int cy, float escala, int color) {
		Component comp = Component.literal(txt).withStyle(Style.EMPTY.withFont(FUENTE));
		g.pose().pushPose();
		g.pose().translate(cx, cy, 0);
		g.pose().scale(escala, escala, 1.0F);
		g.drawCenteredString(this.font, comp, 0, 0, color);
		g.pose().popPose();
	}
}
