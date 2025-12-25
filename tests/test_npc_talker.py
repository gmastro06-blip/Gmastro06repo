# tests/test_npc_talker.py
import pytest
from modules.npc_talker import NPCTalker

def test_npc_talker_init():
    talker = NPCTalker()
    assert talker.running == True
    talker.stop()
    assert talker.running == False

def test_find_npc(mocker, mock_screen):
    talker = NPCTalker()
    mocker.patch('modules.game_window.getGameWindowPositionAndSize', return_value=None)
    mocker.patch('modules.utils.template_matching', return_value=(100, 100))
    pos = talker.find_npc("gustavo", mock_screen)
    assert pos is not None