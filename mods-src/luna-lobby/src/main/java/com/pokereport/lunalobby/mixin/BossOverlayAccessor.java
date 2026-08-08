package com.pokereport.lunalobby.mixin;

import java.util.Map;
import java.util.UUID;
import net.minecraft.client.gui.components.BossHealthOverlay;
import net.minecraft.client.gui.components.LerpingBossEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Acceso a las barras de jefe que el cliente tiene dibujadas.
 *
 * El servidor no puede abrir una pantalla en el cliente: un datapack solo manda cosas que el
 * juego ya entiende. Por eso la senal viaja dentro de una barra de jefe corriente, que el
 * datapack sabe crear, y este accesor permite leerla sin inventar ningun paquete nuevo.
 */
@Mixin(BossHealthOverlay.class)
public interface BossOverlayAccessor {
	@Accessor("events")
	Map<UUID, LerpingBossEvent> lunalobby$getEvents();
}
