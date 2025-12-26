# Ruta: modules/cavebot.py - Cavebot optimizado para Tibia oficial v15.20

import json
import pyautogui
import time
import logging
import numpy as np
import random
from heapq import heappop, heappush
from .utils import GameWindow
from .targeting import Targeting
from .looter import Looter

class Cavebot:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.waypoints = self.load_waypoints()
        self.obstacles = set()  # Almacena posiciones donde se atascó
        self.targeting = Targeting(game_window, config)
        self.looter = Looter(game_window, config)
        self.tolerance = config.get('arrival_tolerance', 1)
        self.base_position = (config['base_position']['x'], config['base_position']['y'])

    def load_waypoints(self):
        """Carga los waypoints desde el archivo especificado."""
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
        """Obtiene la posición actual priorizando player_dot, con fallback a base_position."""
        player_dot = self.config['regions'].get('player_dot')
        minimap_region = self.config['regions'].get('minimap')

        if player_dot:
            expected_color = self.config.get('player_dot_color', [255, 255, 255])
            tolerance = self.config.get('player_dot_tolerance', 30)
            color = self.game_window.get_pixel_color(player_dot[0], player_dot[1])
            if color and np.allclose(color, expected_color, atol=tolerance):
                minimap = self.config['regions']['minimap']
                center_offset = self.config.get('minimap_center_offset', [minimap[2] // 2, minimap[3] // 2])
                current_x = self.base_position[0] + (player_dot[0] - (minimap[0] + center_offset[0]))
                current_y = self.base_position[1] + (player_dot[1] - (minimap[1] + center_offset[1]))
                logging.debug(f"Posición por player_dot: ({current_x}, {current_y})")
                return (int(current_x), int(current_y))

        logging.warning("No se detectó player_dot. Usando base_position.")
        return self.base_position

    def a_star_pathfinding(self, start, goal):
        """A* optimizado para movimiento en 8 direcciones en Tibia."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current_f, current = heappop(open_set)
            if abs(current[0] - goal[0]) <= self.tolerance and abs(current[1] - goal[1]) <= self.tolerance:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            # Movimiento en 8 direcciones (cruz + diagonales)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in self.obstacles:
                    continue

                tentative_g = g_score[current] + (1.4 if dx * dy != 0 else 1)  # Costo diagonal 1.4
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

        logging.warning(f"No se encontró camino a {goal}. Usando ruta directa.")
        return [goal]

    def move_to_position(self, current, target):
        """Mueve al personaje hacia la siguiente posición."""
        dx = target[0] - current[0]
        dy = target[1] - current[1]

        if abs(dx) > abs(dy):
            if dx > 0:
                pyautogui.press('right')
                logging.debug("Moviendo → derecha")
            else:
                pyautogui.press('left')
                logging.debug("Moviendo ← izquierda")
        else:
            if dy > 0:
                pyautogui.press('down')
                logging.debug("Moviendo ↓ abajo")
            else:
                pyautogui.press('up')
                logging.debug("Moviendo ↑ arriba")

        time.sleep(random.uniform(0.3, 0.7))  # Pausa humana

    def is_blocked(self, current, next_step):
        """Verifica si el movimiento está bloqueado."""
        old_pos = current
        self.move_to_position(current, next_step)
        time.sleep(0.5)
        new_pos = self.get_current_position()
        if new_pos == old_pos:
            self.obstacles.add(next_step)
            logging.warning(f"Bloqueado en {current}. Añadiendo {next_step} como obstáculo.")
            return True
        return False

    def navigate(self):
        """Navega por los waypoints integrando targeting y looting."""
        if not self.waypoints:
            logging.warning("No hay waypoints. Navegación detenida.")
            return

        for wp in self.waypoints:
            logging.info(f"Navigando a waypoint: {wp}")

            while True:
                current = self.get_current_position()
                logging.info(f"Posición actual: {current}")

                # Detección de enemigos
                enemy_detected = self.targeting.detect()
                if enemy_detected:
                    logging.info("Enemigo detectado, atacando...")
                    while self.targeting.is_enemy_present():
                        self.targeting.attack_target()
                        time.sleep(0.5)
                    logging.info("Enemigo eliminado, intentando loot...")
                    self.looter.loot(after_kill=True)
                    time.sleep(self.config.get('loot_delay', 1.8))
                    continue  # Continúa navegación tras loot

                # Verifica si llegó al waypoint
                if (abs(wp[0] - current[0]) <= self.tolerance and
                    abs(wp[1] - current[1]) <= self.tolerance):
                    logging.info(f"¡Llegado a waypoint {wp}!")
                    break

                # Calcula el mejor camino
                path = self.a_star_pathfinding(current, wp)
                if not path or len(path) < 2:
                    logging.warning(f"No hay camino válido a {wp}. Pasando al siguiente.")
                    break

                # Mueve paso a paso
                for next_step in path[1:]:
                    if self.is_blocked(current, next_step):
                        break  # Reintenta si está bloqueado
                    self.move_to_position(current, next_step)
                    current = self.get_current_position()
                    time.sleep(0.2)  # Pequeña pausa para estabilidad

            time.sleep(random.uniform(0.5, 1.0))  # Pausa entre waypoints

        logging.info("Todos los waypoints completados.")
