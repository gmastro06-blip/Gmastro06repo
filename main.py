# Ruta: main.py

import logging
import time
import keyboard  # Nueva dependencia: pip install keyboard
from config import load_config
from modules.utils import GameWindow
from modules.healer import Healer
from modules.cavebot import Cavebot
from modules.targeting import Targeting
from modules.macros import Macros
from modules.looter import Looter
from modules.npc_talker import NPCTalker
from modules.level_up import LevelUp
from modules.refill import Refill  # Si lo usas

# Configuración del logging
logging.basicConfig(
    filename='logs/bot_log.txt',
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)

# Tecla para detener el bot (puedes cambiarla a "esc", "f12", etc.)
STOP_HOTKEY = "Esc"

def main():
    logging.info("=== INICIANDO TIBIABOT v2.1 - Modo sin templates ===")
    logging.info(f"Presiona {STOP_HOTKEY.upper()} para detener el bot en cualquier momento.")

    # Cargar configuración
    config = load_config('config.json')

    # Inicializar ventana del juego
    game_window = GameWindow(config)

    # Inicializar módulos
    healer = Healer(game_window, config)
    cavebot = Cavebot(game_window, config)
    targeting = Targeting(game_window, config)
    macros = Macros(game_window, config)
    looter = Looter(game_window, config)
    npc_talker = NPCTalker(game_window, config)
    level_up = LevelUp(game_window, config)
    refill = Refill(game_window, config)  # Si lo usas

    logging.info("Bot inicializado correctamente. Iniciando bucle principal...")

    try:
        while True:
            # Comprobar si se presionó la tecla de parada
            if keyboard.is_pressed(STOP_HOTKEY):
                logging.info(f"Tecla {STOP_HOTKEY.upper()} presionada → Deteniendo el bot de forma segura.")
                break

            # Ejecutar módulos
            healer.monitor()
            cavebot.navigate()
            targeting.detect()
            macros.auto_equip()
            looter.loot()
            npc_talker.talk_if_needed()
            level_up.check()
            refill.refill_if_low()

            time.sleep(0.2)  # Pequeño delay para no saturar CPU

    except KeyboardInterrupt:
        logging.info("Bot detenido por interrupción manual (Ctrl+C).")
    except Exception as e:
        logging.error(f"Error crítico en el bucle principal: {e}")
    finally:
        logging.info("=== BOT DETENIDO ===")
        print(f"\nBot detenido. Revisa logs/bot_log.txt para más detalles.")

# Al final de main.py
def run_bot():
    # Tu código actual del bucle principal aquí
    from modules.bot import Bot  # o como lo tengas estructurado
    config = load_config()  # tu función
    game_window = GameWindow(config)
    bot = Bot(game_window, config)
    bot.start()  # o como inicies el bucle

if __name__ == "__main__":
    run_bot()