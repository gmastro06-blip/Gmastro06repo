# Ruta: modules/cavebot.py - Cavebot CORREGIDO y estable

import json
import pyautogui
import time
import logging
import numpy as np
import random
import threading  # ← IMPORT AÑADIDO
from .utils import GameWindow
from .targeting import Targeting
from .looter import Looter

class Cavebot:
    def __init__(self, game_window, config, stop_event=None):
        self.game_window = game_window
        self.config = config
        self.stop_event = stop_event or threading.Event()
        self.waypoints = self.load_waypoints()
        self.obstacles = set()
        self.targeting = Targeting(game_window, config)
        self.looter = Looter(game_window, config)
        self.tolerance = config.get('arrival_tolerance', 1)
        self.base_position = (config['base_position']['x'], config['base_position']['y'], config['base_position']['z'])
        self.max_retries = 5
        self.retry_delay = 1.0
        self.use_item_key = config['hotkeys'].get('use_item', 'f6')

    def load_waypoints(self):
        file = self.config.get('waypoints_file', 'waypoints/newhaven_exp.json')
        try:
            with open(file, 'r') as f:
                wps = json.load(f)
            logging.info(f"Waypoints cargados: {len(wps)} puntos")
            return [tuple(wp) for wp in wps]
        except Exception as e:
            logging.error(f"Error waypoints: {e}")
            return []

    def get_current_position(self):
        dot = self.config['regions'].get('player_dot')
        if not dot:
            return self.base_position

        color = self.game_window.get_pixel_color(dot[0], dot[1])
        if color and np.allclose(color, self.config.get('player_dot_color', [255,255,255]), atol=self.config.get('player_dot_tolerance', 30)):
            m = self.config['regions']['minimap']
            off = self.config.get('minimap_center_offset', [m[2]//2, m[3]//2])
            x = self.base_position[0] + (dot[0] - (m[0] + off[0]))
            y = self.base_position[1] + (dot[1] - (m[1] + off[1]))
            z = self.base_position[2]
            return (int(x), int(y), z)
        return self.base_position

    def move_to_position(self, current, target):
        if current[2] != target[2]:
            logging.info(f"Cambio de nivel z={current[2]} → z={target[2]}")
            pyautogui.press(self.use_item_key)
            time.sleep(1.0)

        dx, dy = target[0] - current[0], target[1] - current[1]
        if abs(dx) > abs(dy):
            key = 'right' if dx > 0 else 'left'
        else:
            key = 'down' if dy > 0 else 'up'

        duration = random.uniform(0.1, 0.3)
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

        time.sleep(random.uniform(0.05, 0.15))

    def navigate(self):
        if not self.waypoints:
            logging.warning("No waypoints.")
            return

        for wp in self.waypoints:
            if self.stop_event.is_set():
                logging.info("Stop detectado antes de waypoint")
                return

            logging.info(f"→ Waypoint: {wp}")
            retries = 0
            while retries < self.max_retries and not self.stop_event.is_set():
                current = self.get_current_position()

                if self.stop_event.is_set():
                    return

                if self.targeting.detect():
                    while self.targeting.is_enemy_present() and not self.stop_event.is_set():
                        self.targeting.attack_target()
                        time.sleep(0.4)
                    if not self.stop_event.is_set():
                        self.looter.loot(after_kill=True)
                        time.sleep(self.config.get('loot_delay', 1.5))
                    continue

                # Llegado (incluye z)
                if all(abs(wp[i] - current[i]) <= self.tolerance for i in range(3)):
                    logging.info(f"✓ Llegado a {wp}")
                    break

                # Calcular diferencia
                dx = wp[0] - current[0]
                dy = wp[1] - current[1]
                dz = wp[2] - current[2]

                # Cambiar nivel si necesario
                if dz != 0:
                    logging.info(f"Cambio de nivel z={current[2]} → z={wp[2]}")
                    pyautogui.press(self.use_item_key)
                    time.sleep(1.5)
                    continue

                # Determinar dirección principal
                if abs(dx) > abs(dy):
                    key = 'right' if dx > 0 else 'left'
                else:
                    key = 'down' if dy > 0 else 'up'

                # Mantener presionada la tecla proporcional a la distancia (más rápido para largas distancias)
                steps_needed = max(abs(dx), abs(dy))
                hold_duration = min(0.1 * steps_needed, 1.0)  # Máx 1 segundo
                hold_duration = random.uniform(hold_duration * 0.8, hold_duration * 1.2)

                pyautogui.keyDown(key)
                time.sleep(hold_duration)
                pyautogui.keyUp(key)

                time.sleep(random.uniform(0.1, 0.3))

                # Si no avanzó nada, cuenta como retry
                new_pos = self.get_current_position()
                if new_pos == current:
                    retries += 1
                    logging.debug(f"Retry {retries}/{self.max_retries} - no avanzó")

            if retries >= self.max_retries:
                logging.error(f"Waypoint {wp} no alcanzable.")

            time.sleep(random.uniform(0.5, 1.2))

        logging.info("Waypoints completados.")