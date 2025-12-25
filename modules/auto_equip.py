# modules/auto_equip.py
import time
from modules.utils import capture_screen, template_matching, simulate_key_press, random_delay, CONFIG, logger
from modules.game_window import getGameWindowPositionAndSize

class AutoEquip:
    def __init__(self):
        self.running = True
        self.gear_templates = CONFIG.get("gear_templates", {})
        self.equip_hotkeys = CONFIG.get("equip_hotkeys", {})
        self.inventory_slots = CONFIG.get("inventory_slots", {})
        self.check_interval = CONFIG.get("equip_check_interval", 300)
        self.last_check = 0
        logger.info("[AutoEquip] Módulo inicializado")

    def find_best_gear(self, screen):
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return

        game_window = getGameWindowPositionAndSize()
        if game_window:
            screen = capture_screen(region=game_window)

        inventory_region = CONFIG.get("inventory_region", [1550, 600, 350, 400])
        x, y, w, h = inventory_region
        inventory = screen[y:y+h, x:x+w]

        for gear_type, template_path in self.gear_templates.items():
            pos = template_matching(inventory, template_path, threshold=0.8)
            if pos:
                hotkey = self.equip_hotkeys.get(gear_type)
                if hotkey:
                    simulate_key_press(hotkey)
                    logger.info(f"[AutoEquip] Equipado mejor {gear_type} con {hotkey}")
                    random_delay(0.5, 1.0)

        self.last_check = current_time

    def run_check(self, screen):
        if not self.running or not CONFIG.get("auto_equip", False):
            return
        self.find_best_gear(screen)

    def stop(self):
        self.running = False
        logger.info("[AutoEquip] Detenido")