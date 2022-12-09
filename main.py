import pygame
from pygame import mixer

from data import globalvars
from data.constants import RESOLUTIONS, FONT_BASE_SIZE
from data.files import *
from data.globalvars import CURRENT_RESOLUTION, CURRENT_WINDOWED
from gameloops.mainmenuloop import MainMenuLoop
from gameloops.raceloop import RaceLoop
from gameloops.raceselectionloop import RaceSelectionLoop
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager


def main():
    # pygame initialization
    pygame.init()
    screen_size = RESOLUTIONS[CURRENT_RESOLUTION][0]
    globalvars.SCREEN = pygame.display.set_mode(screen_size, CURRENT_WINDOWED)
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_ARIAL, FONT_BASE_SIZE * RESOLUTIONS[CURRENT_RESOLUTION][1])
    mixer.init()

    # input initialization
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        InputManager().joystick = joystick

    # game loop
    while True:
        state = GameManager().GetState()
        if state == State.In_Race:
            RaceLoop(font, clock)
        elif state == State.Selection_Screen:
            RaceSelectionLoop(font, clock)
        elif state == State.Main_Menu:
            MainMenuLoop(font, clock)


if __name__ == "__main__":
    sys.exit(main())
