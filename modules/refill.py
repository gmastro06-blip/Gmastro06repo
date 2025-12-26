# Ruta: modules/refill.py - Auto-Refill completo con NPC

import pyautogui
import time
import random
import logging
from .utils import GameWindow

class Refill:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.npc_name = config.get('bank_npc', 'supplier').lower()
        self.buy_items = config.get('npcs', {}).get(self.npc_name, {}).get('buy', {})
        self.dialog = config.get('npcs', {}).get(self.npc_name, {}).get('dialog', ["hi", "trade"])
        self.npc_position = config.get('npcs', {}).get(self.npc_name, {}).get('position', None)

    def is_low_on_supplies(self):
        """Verifica si necesitamos refill (basado en mana potions o HP potions en inventory)"""
        # Por simplicidad, siempre refill cada X minutos o cuando mana < threshold
        # Puedes mejorarlo con OCR de backpack más adelante
        return True  # Temporal: siempre va a refill cuando se llame

    def go_to_npc(self):
        if not self.npc_position:
            logging.warning("No hay posición del NPC configurada. Refill cancelado.")
            return False

        logging.info(f"Dirigiéndose al NPC {self.npc_name.capitalize()} para refill...")
        # Aquí usarías cavebot para ir a la posición del NPC
        # Por ahora, simulamos con waypoints temporales
        # En el futuro: cavebot.add_temporary_waypoint(self.npc_position)

        # Simulación simple
        time.sleep(random.uniform(3, 6))
        logging.info("Llegó al NPC.")
        return True

    def talk_to_npc(self):
        logging.info(f"Hablando con {self.npc_name.capitalize()}...")
        for line in self.dialog:
            pyautogui.typewrite(line)
            pyautogui.press('enter')
            time.sleep(random.uniform(1.2, 2.5))

    def buy_potions(self):
        if not self.buy_items:
            logging.warning("No hay items configurados para comprar.")
            return

        logging.info("Comprando pociones...")
        for item, amount in self.buy_items.items():
            pyautogui.typewrite(f"buy {amount} {item}")
            pyautogui.press('enter')
            time.sleep(random.uniform(1.5, 3.0))
            pyautogui.typewrite("yes")
            pyautogui.press('enter')
            time.sleep(random.uniform(1.0, 2.2))

        logging.info("Compra completada.")

    def refill_if_low(self):
        # Puedes llamar esto en el bucle principal cada X minutos
        # Por ahora, lo llamamos manual o cada ciclo para testing
        if not self.is_low_on_supplies():
            return

        if not self.go_to_npc():
            return

        self.talk_to_npc()
        self.buy_potions()

        # Volver al hunt (simulación)
        logging.info("Volviendo al hunt...")
        time.sleep(random.uniform(4, 8))