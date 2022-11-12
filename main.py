import pygame.draw_py
import random
from data.constants import SCREEN_SIZE, MAP_SIZE, ENVIRONMENT_DEBUG
from data.files import *
from managers.gamemanager import GameManager, State, RaceLoop, MainMenuLoop
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

    # DEBUG START
    if ENVIRONMENT_DEBUG:
        # setup background
        background = pygame.Surface(MAP_SIZE)
        background.fill((30, 30, 30))
        for _ in range(2000):
            bg_x, bg_y = random.randint(0, MAP_SIZE.x), random.randint(0, MAP_SIZE.y)
            pygame.draw.rect(background, pygame.Color('gray'), (bg_x, bg_y, 2, 2))
    # DEBUG END

    # game loop
    while True:
        state = GameManager().GetState()
        if state == State.In_Race:
            if ENVIRONMENT_DEBUG:
                # DEBUG START
                RaceLoop(screen, font, clock, background)
                # DEBUG END
            else:
                RaceLoop(screen, font, clock)
        elif state == State.Main_Menu:
            MainMenuLoop(screen, font, clock)


if __name__ == "__main__":
    sys.exit(main())
