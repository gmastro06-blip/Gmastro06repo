# tests/test_level_up.py
import pytest
from modules.level_up import LevelUp
from modules.utils import CONFIG

def test_level_up_init():
    level_up = LevelUp()
    assert level_up.running == True
    level_up.stop()
    assert level_up.running == False

def test_check_level_up():
    level_up = LevelUp()
    assert level_up.check_level_up(None) == False  # Asegura no crashea