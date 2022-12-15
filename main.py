import pygame
from pygame import mixer

from data import globalvars
from data.constants import RESOLUTIONS, FONT_BASE_SIZE, AUDIO_BGM_MENU
from data.files import *
from data.globalvars import CURRENT_RESOLUTION, CURRENT_WINDOWED
from gameloops.mainmenuloop import MainMenu
from gameloops.raceloop import RaceLoop
from gameloops.raceselectionloop import RaceSelection
from managers.audiomanager import AudioManager
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager


def main():
    # pygame initialization
    pygame.init()
    pygame.display.set_icon(pygame.image.load(DIR_ASSETS + "\\icon.png"))
    pygame.display.set_caption("Helix Horizon")
    screen_size = RESOLUTIONS[CURRENT_RESOLUTION][0]
    globalvars.SCREEN = pygame.display.set_mode(screen_size, CURRENT_WINDOWED)
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_JOYSTIX, FONT_BASE_SIZE)
    mixer.init()

    # input initialization
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        InputManager().joystick = joystick

    main_menu = MainMenu(font)
    race_selection = RaceSelection(font)

    AudioManager().Play_Music(AUDIO_BGM_MENU)

    globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

    # game loop
    while True:
        state = GameManager().GetState()
        if state == State.In_Race:
            RaceLoop(font, clock)
        elif state == State.Selection_Screen:
            race_selection.RaceSelectionLoop(font, clock)
        elif state == State.Main_Menu:
            main_menu.MainMenuLoop(font, clock)


if __name__ == "__main__":
    sys.exit(main())
