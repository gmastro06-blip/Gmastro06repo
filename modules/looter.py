# modules/looter.py
import time
from modules.utils import (
    capture_screen,
    template_matching,
    simulate_mouse_click,
    simulate_key_press,
    simulate_mouse_drag,  # ← Ahora sí está importado
    random_delay,
    CONFIG,
    logger
)
from modules.game_window import getGameWindowPositionAndSize
from pynput.keyboard import Key, Controller as KeyboardController

keyboard = KeyboardController()

class Looter:
    def __init__(self):
        self.running = True
        self.corpse_template = CONFIG.get("templates", {}).get("corpse", "templates/inventory/corpse.png")
        self.quick_loot_mode = CONFIG.get("quick_loot_mode", "premium")
        self.priority_templates = CONFIG.get("quick_loot_templates", {})
        self.inventory_region = CONFIG.get("inventory_region", [1550, 600, 350, 400])
        self.loot_delay = CONFIG.get("loot_delay", 1.8)
        logger.info(f"[Looter] Inicializado - Modo Quick Loot: {self.quick_loot_mode}")

    def find_corpse(self, screen):
        pos = template_matching(screen, self.corpse_template, threshold=0.75)
        if pos:
            return (pos[0] + CONFIG["window_region"][0], pos[1] + CONFIG["window_region"][1])
        return None

    def perform_quick_loot(self, corpse_pos):
        logger.info("[Looter] Ejecutando Quick Loot...")
        if self.quick_loot_mode == "premium":
            with keyboard.pressed(Key.alt):
                simulate_mouse_click(corpse_pos, button='left')
            logger.info("[Looter] Quick Loot premium (Alt + Left Click)")
        elif self.quick_loot_mode == "classic":
            simulate_mouse_click(corpse_pos, button='right')
            logger.info("[Looter] Quick Loot clásico")
        elif self.quick_loot_mode == "regular":
            with keyboard.pressed(Key.shift):
                simulate_mouse_click(corpse_pos, button='right')
            logger.info("[Looter] Quick Loot regular")

        random_delay(0.8, 1.5)

    def loot_priority_items(self, screen):
        x, y, w, h = self.inventory_region
        inventory = screen[y:y+h, x:x+w]
        for item_name, template_path in self.priority_templates.items():
            pos = template_matching(inventory, template_path, threshold=0.8)
            if pos:
                item_pos = (x + pos[0], y + pos[1])
                inv_center = (x + w // 2, y + h // 2)
                simulate_mouse_drag(item_pos, inv_center)
                logger.info(f"[Looter] Prioridad: {item_name} looteado")
                random_delay(0.5, 1.0)

    def open_and_loot(self, screen=None):
        if not self.running or not CONFIG.get("quick_loot", False):
            return

        if screen is None:
            screen = capture_screen()

        game_window = getGameWindowPositionAndSize()
        if game_window:
            screen = capture_screen(region=game_window)

        corpse_pos = self.find_corpse(screen)
        if corpse_pos:
            logger.info(f"[Looter] Cadáver detectado en {corpse_pos}")
            self.perform_quick_loot(corpse_pos)
            self.loot_priority_items(screen)
            random_delay(self.loot_delay, self.loot_delay + 1.0)

    def stop(self):
        self.running = False
        logger.info("[Looter] Detenido")