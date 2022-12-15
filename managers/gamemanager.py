from enum import Enum

from data import globalvars
from data.constants import AUDIO_BGM1, AUDIO_BGM_MENU
from entities.singleton import Singleton
from managers.audiomanager import AudioManager


class State(Enum):
    Main_Menu = 0
    Selection_Screen = 1
    In_Race = 2


class GameManager(metaclass=Singleton):
    def __init__(self):
        self._state = State.Main_Menu

    def GetState(self):
        return self._state

    def SetState(self, state: State):
        if self._state == State.Main_Menu:
            if state == State.Selection_Screen:
                self._state = state
        if self._state == State.Selection_Screen:
            if state == State.Main_Menu:
                self._state = state
            if state == State.In_Race:
                AudioManager().Play_Music(AUDIO_BGM1)
                self._state = state
        if self._state == State.In_Race:
            if state == State.Main_Menu:
                AudioManager().Play_Music(AUDIO_BGM_MENU)
                globalvars.RaceManager = None
                self._state = state
            if state == State.Selection_Screen:
                return
