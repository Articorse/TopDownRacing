import pygame
from data.constants import SCREEN_SIZE
from data.files import *
from managers.gamemanager import GameManager, State, RaceLoop, MainMenuLoop, RaceSelectionLoop
from managers.inputmanager import InputManager


def main():
    # pygame initialization
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_ARIAL, 32)

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
            RaceLoop(screen, font, clock)
        elif state == State.Selection_Screen:
            RaceSelectionLoop(screen, font, clock)
        elif state == State.Main_Menu:
            MainMenuLoop(screen, font, clock)


if __name__ == "__main__":
    sys.exit(main())
