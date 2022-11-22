from enum import Enum
from entities.singleton import Singleton
from managers.racemanager import RaceManager


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
            if state == State.In_Race:
                self._state = state
            if state == State.Selection_Screen:
                self._state = state
        if self._state == State.Selection_Screen:
            if state == State.Main_Menu:
                self._state = state
            if state == State.In_Race:
                self._state = state
        if self._state == State.In_Race:
            if state == State.Main_Menu:
                RaceManager().Free()
                self._state = state
            if state == State.Selection_Screen:
                return
