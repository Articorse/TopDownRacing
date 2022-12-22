import ctypes

import pygame
from pygame import mixer

from data import globalvars
from data.constants import FONT_BASE_SIZE, AUDIO_BGM_MENU
from data.files import *
from gameloops.mainmenuloop import MainMenu
from gameloops.optionsloop import OptionsScreen
from gameloops.raceloop import RaceLoop
from gameloops.raceselectionloop import RaceSelection
from managers.audiomanager import AudioManager
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager


def main():
    app_id = "helicalstudios.helixhorizon"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # pygame initialization
    pygame.init()
    pygame.display.set_icon(pygame.image.load(DIR_ASSETS + "\\icon.png"))
    pygame.display.set_caption("Helix Horizon")
    GameManager().SetResolution(GameManager().GetOptions().current_resolution)
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_JOYSTIX, FONT_BASE_SIZE)
    mixer.init()

    # input initialization
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        InputManager().joystick = joystick

    GameManager().main_menu = MainMenu(font)
    GameManager().race_selection_menu = RaceSelection(font)
    GameManager().options_menu = OptionsScreen(font)

    AudioManager().Play_Music(AUDIO_BGM_MENU)

    globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

    # game loop
    while True:
        state = GameManager().GetState()
        if state == State.In_Race:
            RaceLoop(font, clock)
        elif state == State.Options:
            GameManager().options_menu.OptionsLoop(font, clock)
        elif state == State.Selection_Screen:
            GameManager().race_selection_menu.RaceSelectionLoop(font, clock)
        elif state == State.Main_Menu:
            GameManager().main_menu.MainMenuLoop(font, clock)
        else:
            pygame.quit()
            sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
