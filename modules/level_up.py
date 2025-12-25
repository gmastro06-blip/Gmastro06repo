# modules/level_up.py
from modules.utils import capture_screen, template_matching, simulate_key_press, random_delay, CONFIG, logger
from modules.game_window import getGameWindowPositionAndSize

class LevelUp:
    def __init__(self):
        self.running = True
        self.level_up_template = CONFIG.get("templates", {}).get("level_up", "templates/statsBar/level_up.png")
        self.skill_hotkeys = CONFIG.get("skill_hotkeys", {})
        self.skill_priority = CONFIG.get("skill_priority", {})
        logger.info("[LevelUp] Módulo inicializado con auto-level up stats")

    def check_level_up(self, screen):
        pos = template_matching(screen, self.level_up_template, threshold=0.8)
        if pos:
            logger.critical("[LevelUp] ¡Subida de nivel detectada!")
            return True
        return False

    def distribute_points(self, screen):
        total_points = 10  # Tibia da 10 puntos por nivel (ajustable)
        sorted_skills = sorted(self.skill_priority.items(), key=lambda x: x[1], reverse=True)

        remaining_points = total_points
        for skill, priority in sorted_skills:
            if not remaining_points:
                break
            hotkey = self.skill_hotkeys.get(skill)
            if hotkey:
                points = int((priority / 100) * total_points)
                points = min(points, remaining_points)
                for _ in range(points):
                    simulate_key_press(hotkey)
                    random_delay(0.1, 0.3)
                logger.info(f"[LevelUp] +{points} puntos en {skill}")
                remaining_points -= points

        simulate_key_press("enter")  # Confirmar
        logger.info("[LevelUp] Puntos distribuidos automáticamente")

    def run_check(self, screen):
        if not self.running or not CONFIG.get("auto_level_up", False):
            return
        game_window = getGameWindowPositionAndSize()
        if game_window:
            screen = capture_screen(region=game_window)
        if self.check_level_up(screen):
            self.distribute_points(screen)

    def stop(self):
        self.running = False
        logger.info("[LevelUp] Detenido")