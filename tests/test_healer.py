# tests/test_healer.py
import pytest
from modules.healer import Healer

def test_healer_init():
    healer = Healer()
    assert healer.hp_threshold == 75
    healer.start()
    assert healer.running == True
    healer.stop()
    assert healer.running == False

def test_heal_with_mock_screen(mocker, mock_screen):
    healer = Healer()
    mocker.patch('modules.game_window.getGameWindowPositionAndSize', return_value=None)

    hp, mp = healer.heal(mock_screen)
    assert 40 < hp < 60  # Mock tiene ~50% HP (mitad verde mitad rojo)
    assert mp > 70  # MP ~70%