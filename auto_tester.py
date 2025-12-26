# Ruta: auto_tester.py - Prueba QA DEFINITIVA con valores reales de HP, Mana y Minimap

import json
import time
import logging
import numpy as np
from modules.utils import GameWindow
from modules.healer import Healer
from modules.targeting import Targeting
from modules.cavebot import Cavebot
from modules.looter import Looter
from modules.level_up import LevelUp
from modules.refill import Refill

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

def run_qa_test():
    print("\n" + "="*80)
    print("🎄 TIBIABOT QA TEST DEFINITIVA - NAVIDAD 2025 🎄")
    print("="*80 + "\n")

    # 1. Cargar config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info("✓ config.json cargado correctamente")
        print(f"   Base position: {config.get('base_position')}")
        print(f"   Player dot: {config['regions'].get('player_dot')}")
        print(f"   HP bar region: {config['regions'].get('hp_bar')}")
        print(f"   Mana bar region: {config['regions'].get('mana_bar')}")
        print(f"   Minimap: {config['regions'].get('minimap')}")
    except Exception as e:
        logging.error(f"✗ Error cargando config.json: {e}")
        input("\nPulsa Enter para salir...")
        return

    # 2. GameWindow
    try:
        gw = GameWindow(config)
        logging.info("✓ GameWindow inicializado")
    except Exception as e:
        logging.error(f"✗ Error GameWindow: {e}")
        input("\nPulsa Enter para salir...")
        return

    # 3. Módulos
    try:
        healer = Healer(gw, config)
        targeting = Targeting(gw, config)
        looter = Looter(gw, config)
        cavebot = Cavebot(gw, config)
        level_up = LevelUp(gw, config)
        refill = Refill(gw, config)

        logging.info("✓ Todos los módulos inicializados")
        cavebot.load_waypoints()
    except Exception as e:
        logging.error(f"✗ Error inicializando módulos: {e}")
        input("\nPulsa Enter para salir...")
        return

    print("\n" + "-"*70)
    print("PRUEBAS REALES DETALLADAS (HP, Mana, Minimap, Player Dot)")
    print("-"*70)

    # === TEST MINIMAP Y PLAYER DOT ===
    try:
        pos = cavebot.get_current_position()
        if pos == (config['base_position']['x'], config['base_position']['y']):
            logging.warning("⚠ Posición: Fallback a base_position (player_dot no detectado)")
        else:
            logging.info(f"✓ Posición detectada correctamente: {pos}")

        # Color del player_dot
        dot = config['regions'].get('player_dot')
        if dot:
            color = gw.get_pixel_color(dot[0], dot[1])
            expected = config.get('player_dot_color', [255,255,255])
            tolerance = config.get('player_dot_tolerance', 30)
            match = np.allclose(color, expected, atol=tolerance)
            logging.info(f"Color player_dot: {color} (esperado: {expected}) → {'MATCH ✓' if match else 'NO MATCH ✗'}")
    except Exception as e:
        logging.error(f"Error en test minimap/player_dot: {e}")

    # === TEST HP Y MANA REALES ===
    try:
        hp_region = config['regions']['hp_bar']
        mana_region = config['regions']['mana_bar']

        hp_raw = gw.read_ocr(hp_region)
        mana_raw = gw.read_ocr(mana_region)

        # Parsear porcentaje
        hp_val = 100.0
        mana_val = 100.0

        if hp_raw:
            try:
                hp_val = float(''.join(filter(str.isdigit, hp_raw)))
            except:
                hp_val = 100.0

        if mana_raw:
            try:
                mana_val = float(''.join(filter(str.isdigit, mana_raw)))
            except:
                mana_val = 100.0

        logging.info(f"HP detectado: {hp_val:.1f}% (OCR: '{hp_raw}')")
        logging.info(f"Mana detectado: {mana_val:.1f}% (OCR: '{mana_raw}')")

        if hp_val < 100 or mana_val < 100:
            logging.info("✓ OCR de HP/Mana funcionando (valores reales)")
        else:
            logging.warning("HP/Mana 100% → posible calibración incorrecta o personaje full")

    except Exception as e:
        logging.error(f"Error en test HP/Mana: {e}")

    # === TEST BATTLE LIST ===
    try:
        battle_region = config['regions']['battle_list']
        battle_raw = gw.read_ocr(battle_region)
        logging.info(f"Battle list OCR: '{battle_raw}'")
        enemy = targeting.detect()
        logging.info(f"Detección de enemigos: {'Sí' if enemy else 'No'}")
    except Exception as e:
        logging.error(f"Error en battle list: {e}")

    # === WAYPOINTS ===
    if cavebot.waypoints:
        logging.info(f"Waypoints: {len(cavebot.waypoints)} puntos")
        logging.info(f"Primer: {cavebot.waypoints[0]}")
        logging.info(f"Último: {cavebot.waypoints[-1]}")
    else:
        logging.warning("No hay waypoints")

    print("\n" + "="*80)
    logging.critical("¡QA COMPLETADA!")
    logging.critical("Si ves posición real, HP/Mana reales y color MATCH → ¡TODO PERFECTO!")
    logging.critical("¡Feliz Navidad 2025 y feliz loot épico! 🎄🏹💎")
    print("="*80)

    input("\nPulsa Enter para cerrar...")

if __name__ == "__main__":
    run_qa_test()