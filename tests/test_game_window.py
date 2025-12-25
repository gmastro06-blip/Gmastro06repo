# tests/test_game_window.py
import pytest
from modules.game_window import getLeftArrowPosition, getRightArrowPosition, getGameWindowPositionAndSize

def test_get_left_arrow(mocker, mock_screen):
    mocker.patch('modules.game_window.locate', return_value=(100, 100, 150, 150))
    pos = getLeftArrowPosition(mock_screen)
    assert pos == (100, 100, 150, 150)

def test_get_right_arrow(mocker, mock_screen):
    mocker.patch('modules.game_window.locate', return_value=(200, 200, 250, 250))
    pos = getRightArrowPosition(mock_screen)
    assert pos == (200, 200, 250, 250)

def test_get_game_window(mocker, mock_screen):
    mocker.patch('modules.game_window.getLeftArrowPosition', return_value=(100, 100, 150, 150))
    mocker.patch('modules.game_window.getRightArrowPosition', return_value=(600, 100, 650, 150))
    pos = getGameWindowPositionAndSize()
    assert pos is not None