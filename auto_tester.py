# auto_tester.py
import time
from modules.healer import Healer
from modules.targeting import Targeting
from modules.cavebot import Cavebot
from modules.macros import Macros
from modules.level_up import LevelUp
from modules.npc_talker import NPCTalker
from modules.utils import logger

def run_qa_test():
    logger.info("=== INICIANDO PRUEBA QA - NAVIDAD 2025 ===")
    time.sleep(2)

    healer = Healer()
    healer.start()
    time.sleep(2)
    healer.stop()

    targeting = Targeting()
    targeting.start()
    time.sleep(2)
    targeting.stop()

    cavebot = Cavebot()
    cavebot.load_waypoints()

    macros = Macros()
    level_up = LevelUp()
    talker = NPCTalker()

    logger.critical("=== ¡QA COMPLETADA! Todos los módulos cargados correctamente ===")
    logger.critical("¡Tu bot está listo para conquistar Tibia! 🎄🎅")

if __name__ == "__main__":
    run_qa_test()