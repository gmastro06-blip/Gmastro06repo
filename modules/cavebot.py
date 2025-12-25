# Ruta: modules/cavebot.py

import json
import pyautogui
import time
import logging
import numpy as np
from heapq import heappop, heappush
from .utils import GameWindow
from .targeting import Targeting
from .looter import Looter  # Importamos Looter para integración

class Cavebot:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.waypoints = self.load_waypoints()
        self.obstacles = set()
        self.targeting = Targeting(game_window, config)
        self.looter = Looter(game_window, config)  # Inicializamos Looter

    def load_waypoints(self):
        waypoints_file = self.config.get('waypoints_file', 'waypoints/newhaven_exp.json')
        try:
            with open(waypoints_file, 'r', encoding='utf-8') as f:
                waypoints = json.load(f)
            logging.info(f"Waypoints cargados: {waypoints}")
            return waypoints
        except FileNotFoundError:
            logging.error(f"Archivo de waypoints no encontrado: {waypoints_file}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error al parsear JSON de waypoints: {e}")
            return []

    def get_current_position(self):
        """Obtiene posición actual con prioridad en player_dot y fallback OCR"""
        player_dot = self.config['regions'].get('player_dot')
        minimap_region = self.config['regions'].get('minimap_coords_text', self.config['regions']['minimap'])

        if player_dot:
            expected_color = self.config.get('player_dot_color', [255, 255, 255])
            tolerance = self.config.get('player_dot_tolerance', 30)

            color = self.game_window.get_pixel_color(player_dot[0], player_dot[1])
            if color and np.allclose(color, expected_color, atol=tolerance):
                logging.debug(f"Posición por color en player_dot: {color}")
                minimap = self.config['regions']['minimap']
                center_offset = self.config.get('minimap_center_offset', [minimap[2] // 2, minimap[3] // 2])
                base_x = self.config['base_position']['x']
                base_y = self.config['base_position']['y']
                current_x = base_x + (player_dot[0] - (minimap[0] + center_offset[0]))
                current_y = base_y + (player_dot[1] - (minimap[1] + center_offset[1]))
                return (int(current_x), int(current_y))

        ocr_config = '--psm 6 -c tessedit_char_whitelist=0123456789,'
        pos_text = self.game_window.read_ocr(minimap_region, ocr_config)
        if pos_text:
            try:
                cleaned = pos_text.strip().replace(' ', '').replace('\n', '')
                parts = cleaned.split(',')
                if len(parts) >= 2:
                    current_x = int(parts[0])
                    current_y = int(parts[1])
                    logging.info(f"Posición por OCR: ({current_x}, {current_y})")
                    return (current_x, current_y)
            except Exception as e:
                logging.warning(f"Error parseando OCR: {e}")

        logging.warning("No se obtuvo posición. Usando base_position.")
        return (self.config['base_position']['x'], self.config['base_position']['y'])

    def a_star_pathfinding(self, start, goal):
        """A* para grid de Tibia"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current_f, current = heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in self.obstacles:
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

        logging.warning(f"No hay camino de {start} a {goal}")
        return [goal]

    def move_to_position(self, current, target):
        dx = target[0] - current[0]
        dy = target[1] - current[1]

        if dx > 0:
            pyautogui.press('right')
            logging.info("Moviendo → derecha")
        elif dx < 0:
            pyautogui.press('left')
            logging.info("Moviendo ← izquierda")
        if dy > 0:
            pyautogui.press('down')
            logging.info("Moviendo ↓ abajo")
        elif dy < 0:
            pyautogui.press('up')
            logging.info("Moviendo ↑ arriba")

        time.sleep(0.5)

    def is_enemy_present(self):
        """Check if an enemy is in the battle list"""
        battle_region = self.config['regions'].get('battle_list')
        if not battle_region:
            return False

        img = self.game_window.capture_region(battle_region)
        if img is None:
            return False

        try:
            import cv2
            img_array = np.array(img)
            height, width = img_array.shape[:2]
            resized = cv2.resize(img_array, (width * 3, height * 3), interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)
            kernel = np.ones((3,3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

            from PIL import Image
            processed_img = Image.fromarray(cleaned)
            ocr_config = '--psm 6 --oem 3'
            text = pytesseract.image_to_string(processed_img, config=ocr_config).strip()
            logging.debug(f"Battle list OCR: '{text}'")

            if not text:
                return False

            text_lower = text.lower()
            for monster in self.config.get('monster_priority', []):
                if monster.lower() in text_lower:
                    return True
            return False
        except Exception as e:
            logging.error(f"Error en is_enemy_present: {e}")
            return False

    def navigate(self):
        if not self.waypoints:
            logging.warning("No hay waypoints. Navegación detenida.")
            return

        for wp in self.waypoints:
            logging.info(f"Navigando a waypoint: {wp}")

            while True:
                current = self.get_current_position()
                logging.info(f"Posición actual: {current}")

                # Check for enemies
                enemy_detected = self.targeting.detect()
                if enemy_detected:
                    logging.info("Enemigo detectado, atacando...")
                    while self.is_enemy_present():
                        self.targeting.detect()  # Keep attacking
                        time.sleep(0.5)
                    logging.info("Enemigo eliminado, intentando loot...")
                    # Attempt to loot after kill
                    looted = self.looter.loot(after_kill=True)
                    if looted:
                        time.sleep(self.config.get('loot_delay', 1.8))  # Wait to complete looting
                    continue  # Resume navigation after looting

                # Check if reached waypoint
                if (abs(wp[0] - current[0]) <= self.config.get('arrival_tolerance', 1) and
                    abs(wp[1] - current[1]) <= self.config.get('arrival_tolerance', 1)):
                    logging.info(f"¡Llegado a waypoint {wp}!")
                    break

                # Calculate path
                path = self.a_star_pathfinding(current, wp)
                if len(path) < 2:
                    logging.warning(f"No hay camino a {wp}. Pasando al siguiente.")
                    break

                next_step = path[1]
                self.move_to_position(current, next_step)

                # Check for obstacles
                new_pos = self.get_current_position()
                if new_pos == current:
                    logging.warning(f"Bloqueado en {current} hacia {next_step}. Añadiendo obstáculo.")
                    self.obstacles.add(next_step)
                    time.sleep(1)

            time.sleep(1)  # Pause between waypoints

        logging.info("Todos los waypoints completados.")