# modules/targeting.py
import time
import threading
from modules.utils import capture_screen, template_matching, simulate_mouse_click, simulate_key_press, random_delay, CONFIG, logger
from modules.game_window import getGameWindowPositionAndSize

class Targeting:
    def __init__(self):
        self.running = False
        self.thread = None
        self.active = False
        self.templates = {k: v for k, v in CONFIG.get("templates", {}).items() if k in CONFIG.get("monster_priority", [])}
        self.priority = CONFIG.get("monster_priority", [])
        self.hotkeys = CONFIG.get("hotkeys", {})
        self.attack_spell_default = self.hotkeys.get("attack_spell_default", "f5")
        self.battle_list_region = CONFIG.get("battle_list_region", [50, 150, 250, 600])
        self.slot_size = CONFIG.get("battle_list_slot_size", [250, 20])
        logger.info(f"[Targeting] Inicializado - Prioridad: {self.priority}")

    def find_monster_in_battle_list(self, screen):
        if not self.active:
            return None

        x, y, w, h = self.battle_list_region
        battle_list = screen[y:y+h, x:x+w]

        best_match = None
        best_priority = -1
        best_slot = None

        for i in range(h // self.slot_size[1]):  # Iterar por slots
            slot_y = y + (i * self.slot_size[1])
            slot_region = screen[slot_y:slot_y + self.slot_size[1], x:x + w]

            for monster_type, template_path in self.templates.items():
                pos = template_matching(slot_region, template_path, threshold=0.75)
                if pos:
                    priority_index = self.priority.index(monster_type)
                    if priority_index > best_priority:
                        best_match = pos
                        best_priority = priority_index
                        best_slot = (x + pos[0], slot_y + pos[1])
                        best_type = monster_type

        if best_slot:
            logger.info(f"[Targeting] Monstruo detectado en battle list: {best_type} en {best_slot}")
            return best_slot, best_type
        return None

    def attack(self, monster_type="default"):
        simulate_key_press(self.attack_spell_default)
        logger.info(f"[Targeting] Atacando {monster_type} con {self.attack_spell_default}")

    def target_and_attack(self, screen):
        if not self.active:
            return False

        game_window = getGameWindowPositionAndSize()
        if game_window:
            screen = capture_screen(region=game_window)

        result = self.find_monster_in_battle_list(screen)
        if result:
            pos, monster_type = result
            simulate_mouse_click(pos, button='right')
            random_delay(0.1, 0.3)
            self.attack(monster_type)
            random_delay(0.4, 0.8)
            return True
        return False

    def _run(self):
        logger.info("[Targeting] Thread iniciado")
        while self.running:
            try:
                screen = capture_screen()
                self.target_and_attack(screen)
                time.sleep(0.4)
            except Exception as e:
                logger.error(f"[Targeting] Error: {e}")
                time.sleep(1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("[Targeting] ACTIVADO")

    def stop(self):
        if self.running:
            self.running = False
            self.active = False
            if self.thread:
                self.thread.join(timeout=2)
            logger.info("[Targeting] DETENIDO")

    def set_active(self, state):
        self.active = state
        logger.info(f"[Targeting] Estado cambiado a {'ACTIVO' if state else 'INACTIVO'}")