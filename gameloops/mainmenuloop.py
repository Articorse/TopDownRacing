import sys
import pygame
from pygame.font import Font
from data.constants import SCREEN_SIZE, FPS, INPUT_QUIT
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from utils.uiutils import Button, ImageAlign


def MainMenuLoop(screen: pygame.Surface, font: Font, clock: pygame.time.Clock):
    screen.fill((33, 50, 80))

    start_button = Button("Start", font, (SCREEN_SIZE.x / 2, SCREEN_SIZE.y / 2), 2, ImageAlign.CENTER)
    exit_button = Button("Exit", font, (SCREEN_SIZE.x / 2, SCREEN_SIZE.y / 2 + 200), 2, ImageAlign.CENTER)

    if start_button.Draw(screen):
        GameManager().SetState(State.Selection_Screen)
    if exit_button.Draw(screen):
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

    pygame.display.flip()
    clock.tick(FPS)
