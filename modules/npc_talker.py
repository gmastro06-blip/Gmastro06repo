# modules/npc_talker.py
import time

import modules.utils as utils
import modules.game_window as game_window


class NPCTalker:
    def __init__(self):
        self.running = True
        self.npcs = utils.CONFIG.get("npcs", {})
        self.dialog_delay = utils.CONFIG.get("dialog_delay", 1.5)
        self.enter_key = utils.CONFIG.get("hotkeys", {}).get("enter_chat", "enter")
        utils.logger.info("[NPCTalker] Módulo inicializado")

    def find_npc(self, npc_name, screen):
        npc_config = self.npcs.get(npc_name)
        if not npc_config or "template" not in npc_config:
            utils.logger.warning(
                f"[NPCTalker] Configuración o template no encontrada para {npc_name}"
            )
            return None

        gw = game_window.getGameWindowPositionAndSize()
        if gw:
            screen = utils.capture_screen(region=gw)

        pos = utils.template_matching(screen, npc_config["template"], threshold=0.75)
        if pos:
            return (
                pos[0] + (gw[0] if gw else 0),
                pos[1] + (gw[1] if gw else 0),
            )
        return None

    def type_message(self, message):
        for char in message.lower():
            utils.simulate_key_press(char)
            utils.random_delay(0.05, 0.15)
        utils.simulate_key_press(self.enter_key)
        utils.logger.info(f"[NPCTalker] Enviado: {message}")

    def talk_to_npc(self, npc_name, screen=None):
        if not self.running:
            return False

        if screen is None:
            screen = utils.capture_screen()

        npc_pos = self.find_npc(npc_name, screen)
        if not npc_pos:
            utils.logger.warning(f"[NPCTalker] NPC {npc_name} no detectado")
            return False

        utils.logger.info(f"[NPCTalker] Hablando con {npc_name} en {npc_pos}")
        utils.simulate_mouse_click(npc_pos, button="right")
        utils.random_delay(0.8, 1.5)

        npc_config = self.npcs.get(npc_name, {})
        dialog = npc_config.get("dialog", [])

        for message in dialog:
            if not self.running:
                return False
            self.type_message(message)
            utils.random_delay(self.dialog_delay - 0.5, self.dialog_delay + 0.8)

        buy_items = npc_config.get("buy", {})
        if buy_items:
            utils.logger.info(f"[NPCTalker] Abriendo trade con {npc_name}")
            self.type_message("trade")
            utils.random_delay(2.0, 3.0)
            utils.logger.info(
                f"[NPCTalker] Trade abierto - Items a comprar: {buy_items}"
            )

        return True

    def stop(self):
        self.running = False
        utils.logger.info("[NPCTalker] Detenido")
