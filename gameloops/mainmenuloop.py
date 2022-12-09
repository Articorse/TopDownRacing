import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import FPS, INPUT_QUIT, RESOLUTIONS, AUDIO_CANCEL
from data.globalvars import CURRENT_RESOLUTION
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from utils.uiutils import Button, ImageAlign


def MainMenuLoop(font: Font, clock: pygame.time.Clock):
    globalvars.SCREEN.fill((33, 50, 80))

    screen_size = RESOLUTIONS[CURRENT_RESOLUTION][0]
    start_button = Button("Start", font,
                          (screen_size.x / 2, screen_size.y / 2), 2, ImageAlign.CENTER)
    exit_button = Button("Exit", font,
                         (screen_size.x / 2, screen_size.y / 2 + screen_size.y / 8), 2, ImageAlign.CENTER, AUDIO_CANCEL)

    if start_button.Draw(globalvars.SCREEN):
        GameManager().SetState(State.Selection_Screen)
    if exit_button.Draw(globalvars.SCREEN):
        pygame.quit()
        sys.exit()

    # handle inputs
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
    inputs = InputManager().get_inputs(events)
    if inputs[INPUT_QUIT]:
        pygame.quit()
        sys.exit()

    # update last frame time
    globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

    # end draw step
    pygame.display.flip()
    clock.tick(FPS)
