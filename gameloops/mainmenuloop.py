import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import FPS, INPUT_QUIT, UI_DYNAMIC_BUTTON_ALT, UI_COPYRIGHT_INFO
from data.files import DIR_UI
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from utils.mathutils import ClosestNumber
from utils.uiutils import ImageAlign, DrawSprite, ScaledButton, DrawText


class MainMenu:
    def __init__(self, font: Font):
        self.font = font
        self.UpdateScreen()

    def UpdateScreen(self):
        screen_size = GameManager().GetResolution()

        bg_sp = pygame.sprite.Sprite()
        bg_image = pygame.image.load(DIR_UI + "MainMenuBg.png").convert_alpha()
        scale = GameManager().GetResolutionScale()
        bg_sp.image = pygame.transform.scale(bg_image,
                                             (bg_image.get_width() * scale, bg_image.get_height() * scale))
        bg_sp.rect = bg_sp.image.get_rect()
        self.background_sprite = bg_sp

        button_pos = (screen_size.x / 2, screen_size.y / 2)
        min_offset = ClosestNumber(screen_size.y / 8, GameManager().GetResolutionScale())
        self.start_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Start", self.font,
                                         (button_pos[0], button_pos[1] + min_offset),
                                         1, 2, ImageAlign.CENTER)
        self.options_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Options", self.font,
                                           (button_pos[0], button_pos[1] + 2 * min_offset),
                                           1, 2, ImageAlign.CENTER)
        self.exit_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Exit", self.font,
                                        (button_pos[0], button_pos[1] + 3 * min_offset),
                                        1, 2, ImageAlign.CENTER)


    def MainMenuLoop(self, font: Font, clock: pygame.time.Clock):
        globalvars.SCREEN.fill((0, 0, 0))
        screen_size = GameManager().GetResolution()

        DrawSprite(self.background_sprite, globalvars.SCREEN, (0, 0))
        min_offset = ClosestNumber(screen_size.y / 32, GameManager().GetResolutionScale())
        DrawText(UI_COPYRIGHT_INFO, globalvars.SCREEN, font,
                 (screen_size.x / 2, screen_size.y - min_offset), ImageAlign.CENTER)

        if self.start_button.Draw(globalvars.SCREEN):
            GameManager().SetState(State.Selection_Screen)
        if self.options_button.Draw(globalvars.SCREEN):
            GameManager().SetState(State.Options)
        if self.exit_button.Draw(globalvars.SCREEN):
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
