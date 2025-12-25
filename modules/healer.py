# modules/healer.py
import time
import threading

import modules.utils as utils
import modules.game_window as game_window


class Healer:
    def __init__(self):
        self.running = False
        self.thread = None

        self.hp_threshold = utils.CONFIG.get("hp_threshold", 70)
        self.mp_threshold = utils.CONFIG.get("mp_threshold", 40)
        self.hotkeys = utils.CONFIG.get("hotkeys", {})

        self.heal_spell_light = self.hotkeys.get("heal_spell_light", "f1")
        self.heal_spell_strong = self.hotkeys.get("heal_spell_strong", "f2")
        self.uh_hotkey = self.hotkeys.get("uh_hotkey", "f3")
        self.mana_potion_hotkey = self.hotkeys.get("mana_potion", "f4")
        self.eat_food_hotkey = self.hotkeys.get("eat_food", "f8")

        self.strong_heal_below = utils.CONFIG.get("strong_heal_below", 40)
        self.use_mana_potion = utils.CONFIG.get("use_mana_potion", True)

        utils.logger.info("[Healer] Inicializado")

    def get_best_hp_mp(self, screen=None):
        """
        Devuelve HP y MP usando barras primarias o secundarias.
        IMPORTANTE PARA TESTS:
          - Si 'screen' se pasa como argumento (mock), NO debe recapturar.
          - Solo captura pantalla si screen es None.
        """
        # Si no nos pasan pantalla, capturamos aquí
        if screen is None:
            gw = game_window.getGameWindowPositionAndSize()
            if gw:
                screen = utils.capture_screen(region=gw)
            else:
                screen = utils.capture_screen()

        # Seguridad
        if screen is None:
            return 100.0, 100.0

        hp_primary = utils.get_hp_percentage(screen, utils.CONFIG["hp_bar_region_primary"])
        mp_primary = utils.get_mp_percentage(screen, utils.CONFIG["mp_bar_region_primary"])

        # Si las primarias parecen válidas, usarlas
        if 0 <= hp_primary <= 100 and 0 <= mp_primary <= 100:
            return float(hp_primary), float(mp_primary)

        # Fallback a secundarias
        utils.logger.info("[Healer] Barras primarias no válidas. Usando secundarias (inventario abierto?)")
        hp_secondary = utils.get_hp_percentage(screen, utils.CONFIG["hp_bar_region_secondary"])
        mp_secondary = utils.get_mp_percentage(screen, utils.CONFIG["mp_bar_region_secondary"])
        return float(hp_secondary), float(mp_secondary)

    def heal(self, screen=None):
        hp, mp = self.get_best_hp_mp(screen)
        healed = False

        if hp < self.strong_heal_below:
            hotkey = self.uh_hotkey if self.uh_hotkey else self.heal_spell_strong
            utils.simulate_key_press(hotkey)
            utils.logger.info(f"[Healer] HP crítico ({hp:.1f}%) → {hotkey}")
            healed = True
        elif hp < self.hp_threshold:
            utils.simulate_key_press(self.heal_spell_light)
            utils.logger.info(f"[Healer] HP bajo ({hp:.1f}%) → {self.heal_spell_light}")
            healed = True

        if self.use_mana_potion and mp < self.mp_threshold:
            utils.simulate_key_press(self.mana_potion_hotkey)
            utils.logger.info(f"[Healer] Mana baja ({mp:.1f}%) → Mana potion")
            healed = True

        eat_threshold = utils.CONFIG.get("eat_food_threshold", 50)
        if hp < eat_threshold and self.eat_food_hotkey:
            utils.simulate_key_press(self.eat_food_hotkey)
            utils.logger.info(f"[Healer] HP bajo ({hp:.1f}%) → Comiendo comida ({self.eat_food_hotkey})")
            healed = True

        if healed:
            utils.random_delay(0.3, 0.8)

        return hp, mp

    def _run(self):
        utils.logger.info("[Healer] Thread iniciado - Monitoreando HP/MP...")
        while self.running:
            try:
                # aquí sí capturamos porque es el loop real del bot
                hp, mp = self.heal(None)
                time.sleep(0.3)
            except Exception as e:
                utils.logger.error(f"[Healer] Error en loop: {e}")
                time.sleep(1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            utils.logger.info("[Healer] ACTIVADO")

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2)
            utils.logger.info("[Healer] DETENIDO")
