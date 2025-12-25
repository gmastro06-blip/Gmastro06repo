# modules/cavebot.py
import json
import time
import threading
import os
from modules.utils import capture_screen, simulate_mouse_click, simulate_key_press, random_delay, detect_player_position, detect_stair_type, a_star_pathfinding, CONFIG, logger
from modules.game_window import getGameWindowPositionAndSize

class Cavebot:
    def __init__(self):
        self.running = False
        self.thread = None
        self.waypoints = []
        self.current_index = 0
        self.waypoints_file = CONFIG.get("default_waypoints", "waypoints/newhaven_exp.json")
        self.arrival_tolerance = CONFIG.get("arrival_tolerance", 1)

        self.load_waypoints()
        logger.info(f"[Cavebot] Inicializado - {len(self.waypoints)} waypoints cargados desde {self.waypoints_file}")

    def load_waypoints(self):
        if not os.path.exists(self.waypoints_file):
            logger.error(f"[Cavebot] Archivo no encontrado: {self.waypoints_file}")
            self.waypoints = []
            return

        try:
            with open(self.waypoints_file, 'r', encoding='utf-8') as f:
                self.waypoints = json.load(f)
            self.current_index = 0
            logger.info(f"[Cavebot] Waypoints cargados: {len(self.waypoints)} puntos")
        except Exception as e:
            logger.error(f"[Cavebot] Error cargando waypoints: {e}")
            self.waypoints = []

    def get_current_waypoint(self):
        if not self.waypoints:
            return None
        return self.waypoints[self.current_index % len(self.waypoints)]

    def is_near_waypoint(self, current_pos, target_x, target_y):
        if current_pos is None:
            return False
        dist = ((current_pos[0] - target_x) ** 2 + (current_pos[1] - target_y) ** 2) ** 0.5
        return dist <= self.arrival_tolerance

    def move_to_waypoint(self, target_x, target_y):
        logger.info(f"[Cavebot] Moviendo a waypoint {self.current_index + 1}: ({target_x}, {target_y})")
        attempts = 0
        max_attempts = 50

        while self.running and attempts < max_attempts:
            attempts += 1

            pos_tuple = detect_player_position()
            if pos_tuple is None:
                logger.warning("[Cavebot] Posición no detectada. Reintentando...")
                random_delay(1.5, 3)
                continue

            current_x, current_y, current_z = pos_tuple
            current_pos = (current_x, current_y)

            if self.is_near_waypoint(current_pos, target_x, target_y):
                logger.info(f"[Cavebot] ¡Llegamos al waypoint {self.current_index + 1}!")
                return True

            game_window = getGameWindowPositionAndSize()
            if game_window:
                screen = capture_screen(region=game_window)
            else:
                screen = capture_screen()

            path = a_star_pathfinding(current_pos, (target_x, target_y))
            if not path:
                logger.warning(f"[Cavebot] Sin camino directo. Reintentando...")
                random_delay(2, 4)
                continue

            logger.info(f"[Cavebot] Camino calculado: {len(path)} pasos")
            steps = min(5, len(path))

            for i in range(steps):
                if not self.running:
                    return False

                step_x, step_y = path[i]
                dx = (step_x - current_x) * CONFIG["sqm_size_pixels"]
                dy = (step_y - current_y) * CONFIG["sqm_size_pixels"]

                minimap_x = CONFIG["minimap_region"][0] + CONFIG["minimap_center_offset"][0] + dx
                minimap_y = CONFIG["minimap_region"][1] + CONFIG["minimap_center_offset"][1] + dy

                screen_x = int(minimap_x + (game_window[0] if game_window else CONFIG["window_region"][0]))
                screen_y = int(minimap_y + (game_window[1] if game_window else CONFIG["window_region"][1]))

                if not (CONFIG["minimap_region"][0] <= minimap_x <= CONFIG["minimap_region"][0] + CONFIG["minimap_region"][2] and
                        CONFIG["minimap_region"][1] <= minimap_y <= CONFIG["minimap_region"][1] + CONFIG["minimap_region"][3]):
                    logger.warning(f"[Cavebot] Click fuera del minimapa. Saltando paso.")
                    continue

                simulate_mouse_click((screen_x, screen_y))
                logger.debug(f"[Cavebot] Click → SQM ({step_x}, {step_y}) | Pixel ({screen_x}, {screen_y})")
                random_delay(0.7, 1.4)
                time.sleep(0.5)

                new_pos = detect_player_position()
                if new_pos:
                    current_x, current_y, current_z = new_pos

                if self.is_near_waypoint((current_x, current_y), target_x, target_y):
                    logger.info(f"[Cavebot] Llegada durante seguimiento")
                    return True

            random_delay(0.6, 1.2)

        logger.error(f"[Cavebot] No se pudo llegar tras {max_attempts} intentos")
        return False

    def execute_action(self, wp):
        action = wp.get("action", "hunt")
        if action == "hunt":
            wait = wp.get("wait_time", 30)
            logger.info(f"[Cavebot] Cazando {wait} segundos")
            time.sleep(wait)
        elif action == "refill":
            logger.info("[Cavebot] Refill iniciado")
        elif action == "deposit":
            logger.info("[Cavebot] Depósito iniciado")
        elif action == "mine_enter":
            screen = capture_screen()
            stair_type = detect_stair_type(screen)
            if stair_type in ["down_stair", "hole", "rope_spot"]:
                key = "use_rope" if stair_type == "rope_spot" else "use_shovel"
                logger.info(f"[Cavebot] Usando {stair_type} → {key}")
                simulate_key_press(CONFIG["hotkeys"].get(key, "f6"))
                random_delay(1.5, 2.5)
        elif action == "mine_exit":
            screen = capture_screen()
            stair_type = detect_stair_type(screen)
            if stair_type == "up_stair":
                logger.info("[Cavebot] Subiendo escalera")
                simulate_key_press(CONFIG["hotkeys"].get("use_shovel", "f7"))
                random_delay(1.5, 2.5)
        elif action == "talk":
            npc_name = wp.get("npc", "gustavo")
            screen = capture_screen()
            from modules.npc_talker import NPCTalker
            talker = NPCTalker()
            talker.talk_to_npc(npc_name, screen)
            logger.info(f"[Cavebot] Diálogo completado con {npc_name}")
        elif action == "bank":
            from modules.npc_talker import NPCTalker
            talker = NPCTalker()
            talker.talk_to_npc(CONFIG["bank_npc"], screen)
            logger.info("[Cavebot] Auto-bank ejecutado")
        elif action == "return":
            logger.info("[Cavebot] Volviendo al inicio")
        else:
            logger.info(f"[Cavebot] Acción personalizada: {action}")

    def _run(self):
        logger.info("[Cavebot] MÓDULO INICIADO - Pathfinding real activado")
        while self.running:
            try:
                wp = self.get_current_waypoint()
                if wp:
                    if wp.get("action") == "hunt":
                        from modules.targeting import Targeting
                        if not hasattr(self, 'targeting_instance'):
                            self.targeting_instance = Targeting()
                            self.targeting_instance.start()
                        self.targeting_instance.set_active(True)
                    else:
                        if hasattr(self, 'targeting_instance'):
                            self.targeting_instance.set_active(False)

                    if self.move_to_waypoint(wp["x"], wp["y"]):
                        self.execute_action(wp)
                        self.current_index += 1
                else:
                    logger.warning("[Cavebot] Sin waypoints. Esperando...")
                    time.sleep(5)
            except Exception as e:
                logger.error(f"[Cavebot] Excepción: {e}")
                time.sleep(3)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("[Cavebot] ACTIVADO")

    def stop(self):
        if self.running:
            self.running = False
            if hasattr(self, 'targeting_instance'):
                self.targeting_instance.stop()
            if self.thread:
                self.thread.join(timeout=3)
            logger.info("[Cavebot] DETENIDO")

    def reload_waypoints(self, new_file=None):
        if new_file:
            self.waypoints_file = new_file
        self.load_waypoints()
        self.current_index = 0
        logger.info("[Cavebot] Waypoints recargados")