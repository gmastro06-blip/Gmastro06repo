# modules/depositer.py
import time
from modules.utils import capture_screen, template_matching, simulate_key_press, random_delay, CONFIG

class Depositer:
    def __init__(self, cavebot):
        self.cavebot = cavebot
        self.running = True
        self.full_inventory_template = CONFIG.get("templates", {}).get("full_inventory", "templates/full_inventory.png")
        self.depot_waypoints_file = CONFIG.get("depot_waypoints", "waypoints/depot_path.json")
        self.deposit_hotkey = CONFIG.get("hotkeys", {}).get("deposit", "d")  # Ejemplo: tecla para depositar todo

    def check_inventory_full(self, screen):
        """
        Detecta si el inventario está lleno o casi lleno.
        """
        result = template_matching(screen, self.full_inventory_template, threshold=0.75)
        return result is not None

    def go_to_deposit(self):
        """
        Navegación al depot y depósito automático.
        """
        print("[Depositer] Inventario lleno. Iniciando depósito...")
        self.cavebot.stop()
        random_delay(1, 3)

        # Simulación: abrir depot y depositar (puedes mejorar con clicks específicos)
        simulate_key_press(self.deposit_hotkey)
        random_delay(2, 4)

        print("[Depositer] Depósito completado.")
        time.sleep(2)
        self.cavebot.start()

    def check_and_deposit(self, screen=None):
        if not self.running:
            return

        if screen is None:
            screen = capture_screen(region=CONFIG.get("window_region"))

        if self.check_inventory_full(screen):
            self.go_to_deposit()
            random_delay(3, 7)  # Pausa después de depositar