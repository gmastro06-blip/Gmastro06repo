import pyautogui
import logging
from .utils import GameWindow

class NPCTalker:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def talk_if_needed(self):
        chat_region = (200, 400, 300, 100)  # Ajusta a chat area
        text = self.game_window.read_ocr(chat_region, '--psm 6')
        if 'npc' in text.lower() or 'gustavo' in text.lower():  # Detecta NPC
            pyautogui.typewrite('hi')
            pyautogui.press(self.config['hotkeys']['talk_hi'])
            logging.info("Hablando con NPC")