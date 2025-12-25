# modules/refiller.py
import time
from modules.utils import capture_screen, template_matching, simulate_key_press, random_delay, CONFIG

class Refiller:
    def __init__(self, cavebot):
        self.cavebot = cavebot  # Para pausar/reanudar el cavebot si es necesario
        self.running = True
        self.low_supplies_template = CONFIG.get("templates", {}).get("low_mana_potion", "templates/low_mana_potion.png")
        self.npc_waypoints_file = CONFIG.get("refill_waypoints", "waypoints/refill_path.json")
        self.buy_hotkey = CONFIG.get("hotkeys", {}).get("buy_npc", "b")
        self.talk_hotkey = CONFIG.get("hotkeys", {}).get("talk_npc", "enter")

    def check_supplies(self, screen):
        """
        Detecta si las supplies (ej. mana potions) están bajas usando template matching.
        """
        result = template_matching(screen, self.low_supplies_template, threshold=0.8)
        return result is not None

    def go_to_refill(self):
        """
        Función placeholder: aquí iría la navegación al NPC usando waypoints específicos.
        Por ahora, simula una pausa y acciones manuales (puedes expandirlo con cavebot temporal).
        """
        print("[Refiller] Supplies bajas detectadas. Iniciando reabastecimiento...")
        self.cavebot.stop()  # Pausar caza principal
        random_delay(1, 3)

        # Simulación simple: hablar con NPC y comprar
        simulate_key_press(self.talk_hotkey)
        random_delay(0.5, 1.5)
        simulate_key_press(self.buy_hotkey)
        random_delay(1, 2)

        # Aquí podrías agregar más pasos: decir "hi", "trade", seleccionar cantidad, etc.
        print("[Refiller] Reabastecimiento completado.")
        time.sleep(2)
        self.cavebot.start()  # Reanudar cavebot

    def check_and_refill(self, screen=None):
        """
        Método llamado desde main.py en el main_loop.
        """
        if not self.running:
            return

        if screen is None:
            screen = capture_screen(region=CONFIG.get("window_region"))

        if self.check_supplies(screen):
            self.go_to_refill()
            random_delay(2, 5)  # Pausa extra después de refill