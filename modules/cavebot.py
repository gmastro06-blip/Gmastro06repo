# Ruta: modules/cavebot.py - Cavebot con Waypoints Avanzados (labels, actions, rope)

import json
import pyautogui
import time
import logging
import numpy as np
import random
import threading
import cv2  # Agregado para detección
from typing import Tuple, List, Optional
from .utils import GameWindow
from .targeting import Targeting
from .looter import Looter

class StopException(Exception):
    pass

class Cavebot:
    """
    Módulo de navegación por waypoints con manejo de combate y stop seguro.
    """
    def __init__(self, game_window: GameWindow, config: dict, stop_event: threading.Event):
        self.game_window: GameWindow = game_window
        self.config: dict = config
        self.stop_event: threading.Event = stop_event  # Compartido desde engine
        self.waypoints: List[dict] = self.load_waypoints()
        self.obstacles: set = set()  # Para futuro manejo de obstáculos
        self.targeting: Targeting = Targeting(game_window, config)
        self.looter: Looter = Looter(game_window, config)
        self.tolerance: int = config.get('arrival_tolerance', 1)
        self.base_position: Tuple[int, int, int] = (
            config['base_position']['x'], config['base_position']['y'], config['base_position']['z']
        )
        self.max_retries: int = 5
        self.retry_delay: float = 1.0
        self.use_item_key: str = config['hotkeys'].get('use_item', 'f6')
        self.loop_waypoints: bool = config.get('loop_waypoints', True)  # Nuevo: loop infinito

        # Dict de actions (placeholder - ajusta con lógica real)
        self.actions = {
            'bank': self.do_bank,
            'deposit': self.do_deposit,
            'sell': self.do_sell,
            'buy_potions': self.do_buy_potions,
            'check_supplies': self.check_supplies,
            'check': self.check_general,
            'check_time': self.check_time,
            'logout': self.do_logout,
            'end': self.do_end
        }

    def load_waypoints(self) -> List[dict]:
        """Carga waypoints desde archivo."""
        file: str = self.config.get('waypoints_file', 'waypoints/newhaven_exp.json')
        try:
            with open(file, 'r') as f:
                wps = json.load(f)
            logging.info(f"Waypoints avanzados cargados: {len(wps)} items")
            return wps
        except Exception as e:
            logging.error(f"Error cargando waypoints: {e}")
            return []

    def get_current_position(self) -> Tuple[int, int, int]:
        """Obtiene posición actual del jugador vía minimapa, buscando el dot."""
        minimap_region = self.config['regions'].get('minimap')
        if not minimap_region:
            logging.warning("No hay región de minimap definida. Retornando base.")
            return self.base_position

        img = self.game_window.capture_region(minimap_region)
        if img is None:
            logging.warning("Fallo en captura del minimap. Retornando base.")
            return self.base_position

        try:
            gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
            if max_val < 150:  # Umbral bajado para dots menos brillantes
                logging.debug(f"No dot brillante encontrado (max_val={max_val}).")
                return self.base_position

            off_x, off_y = max_loc
            center_off = self.config.get('minimap_center_offset', (minimap_region[2]//2, minimap_region[3]//2))

            dx = off_x - center_off[0]
            dy = off_y - center_off[1]

            x = self.base_position[0] + dx
            y = self.base_position[1] + dy
            z = self.base_position[2]

            logging.debug(f"Posición detectada: ({x}, {y}, {z}) via dot en ({off_x}, {off_y})")
            return (int(x), int(y), z)

        except Exception as e:
            logging.error(f"Error detectando posición: {e}")
            return self.base_position

    def move_one_step(self, direction: str) -> None:
        """Mueve un solo paso en la dirección dada."""
        if self.stop_event.is_set():
            raise StopException
        duration = random.uniform(0.1, 0.3)
        pyautogui.keyDown(direction)
        time.sleep(duration)
        pyautogui.keyUp(direction)
        if self.stop_event.is_set():
            raise StopException
        time.sleep(random.uniform(0.05, 0.15))

    def navigate_to(self, wp: Tuple[int, int, int]) -> bool:
        """Navega a un waypoint específico con movimiento step-by-step."""
        if self.stop_event.is_set():
            return False

        logging.info(f"-> Navegando a waypoint: {wp}")
        retries: int = 0
        while retries < self.max_retries:
            if self.stop_event.is_set():
                return False

            current: Tuple[int, int, int] = self.get_current_position()

            # Manejo de combate
            if self.targeting.detect():
                while self.targeting.is_enemy_present() and not self.stop_event.is_set():
                    self.targeting.attack_target()
                    time.sleep(0.4)
                if not self.stop_event.is_set():
                    self.looter.loot(after_kill=True)
                    time.sleep(self.config.get('loot_delay', 1.5))
                continue

            # Chequeo de llegada (incluye z)
            if all(abs(wp[i] - current[i]) <= self.tolerance for i in range(3)):
                logging.info(f"V Llegado a waypoint {wp}")
                return True

            # Cambio de nivel si dz != 0
            dz = wp[2] - current[2]
            if dz != 0:
                logging.info(f"Cambio de nivel z={current[2]} -> z={wp[2]}")
                pyautogui.press(self.use_item_key)
                time.sleep(1.5)
                if self.stop_event.is_set():
                    return False
                continue

            # Movimiento step-by-step: elige dirección y mueve 1 tile
            dx = wp[0] - current[0]
            dy = wp[1] - current[1]
            if abs(dx) > abs(dy):
                key = 'right' if dx > 0 else 'left'
            else:
                key = 'down' if dy > 0 else 'up'

            try:
                self.move_one_step(key)
            except StopException:
                return False

            # Chequea si avanzó
            time.sleep(0.3)
            if self.stop_event.is_set():
                return False
            new_pos = self.get_current_position()
            if new_pos == current:
                retries += 1
                logging.debug(f"Retry {retries}/{self.max_retries} - Posición no cambió. Posible stuck.")
                if retries > 3:
                    alt_key = 'up' if key in ['left', 'right'] else 'left'
                    logging.info(f"Anti-stuck: Intentando {alt_key}")
                    try:
                        self.move_one_step(alt_key)
                    except StopException:
                        return False
                    time.sleep(0.3)
                    if self.stop_event.is_set():
                        return False
            else:
                retries = 0  # Reset si avanzó

        if retries >= self.max_retries:
            logging.error(f"Waypoint {wp} no alcanzable después de {self.max_retries} retries.")
            return False
        return True

    def process_waypoints(self) -> None:
        """Procesa waypoints avanzados con labels, actions, jumps."""
        if not self.waypoints:
            logging.warning("No hay waypoints cargados.")
            return

        i = 0
        while self.loop_waypoints and not self.stop_event.is_set():
            while i < len(self.waypoints) and not self.stop_event.is_set():
                item = self.waypoints[i]

                tp = item.get('type')
                if tp in ['node', 'stand']:
                    success = self.navigate_to(tuple(item['pos']))
                    if not success:
                        break
                elif tp == 'rope':
                    self.navigate_to(tuple(item['pos']))
                    pyautogui.press(self.use_item_key)
                    time.sleep(1.5)
                    if self.stop_event.is_set():
                        return
                elif tp == 'action':
                    if item['name'] in self.actions:
                        jump_label = self.actions[item['name']]()
                        if jump_label:
                            for j, lbl in enumerate(self.waypoints):
                                if lbl['type'] == 'label' and lbl['name'] == jump_label:
                                    i = j - 1  # Para procesar desde label next
                                    break
                elif tp == 'label':
                    pass  # Skip labels

                i += 1
                time.sleep(random.uniform(0.5, 1.2))
                if self.stop_event.is_set():
                    return

            logging.info("Ciclo de waypoints completado. Reiniciando si loop activado...")
            i = 0  # Reset para loop

        if not self.loop_waypoints:
            logging.info("Waypoints completados (modo no-loop).")

    # === ACTIONS ===
    def do_bank(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: bank - Interactuando con NPC bank")
        pyautogui.typewrite('hi\nbank\ndeposit all\nyes\n')
        time.sleep(random.uniform(2, 3))
        return None

    def do_deposit(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: deposit")
        pyautogui.typewrite('deposit all\nyes\n')
        time.sleep(random.uniform(1, 2))
        return None

    def do_sell(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: sell")
        pyautogui.typewrite('hi\ntrade\nsell all\nyes\n')
        time.sleep(random.uniform(2, 3))
        return None

    def do_buy_potions(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: buy_potions")
        pyautogui.typewrite('hi\nbuy 100 mana potion\nyes\n')
        time.sleep(random.uniform(2, 3))
        return None

    def check_supplies(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        # Placeholder: Chequea HP/Mana o inventory via OCR (ajusta)
        hp = self.game_window.read_ocr(self.config['regions']['hp_bar'])
        if hp and float(hp.strip('%')) < 50:  # Ejemplo
            logging.info("Check supplies: Low - Jumping to refill")
            return 'refill'
        logging.info("Check supplies: OK")
        return None

    def check_general(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Check general: Todo OK")
        return None

    def check_time(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        # Placeholder: Si tiempo > limit, logout
        if random.random() < 0.1:  # Simula
            logging.info("Check time: Timeout - Jumping to logout")
            return 'logout'
        return None

    def do_logout(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: logout")
        pyautogui.typewrite('logout\n')
        time.sleep(1)
        return None

    def do_end(self) -> Optional[str]:
        self._human_delay(0.5, 1.0)
        logging.info("Action: end - Deteniendo bot")
        self.stop_event.set()
        return None