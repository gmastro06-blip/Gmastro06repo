# tests/test_macros.py
import pytest
from modules.macros import Macros

def test_macros_init():
    macros = Macros()
    assert macros.running == True
    macros.stop()
    assert macros.running == False

def test_get_current_level(mocker, mock_screen):
    macros = Macros()
    mocker.patch('modules.game_window.getGameWindowPositionAndSize', return_value=None)
    mocker.patch('pytesseract.image_to_string', return_value="42")
    level = macros.get_current_level(mock_screen)
    assert level == 42