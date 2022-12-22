import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import FPS, INPUT_QUIT, RESOLUTIONS, UI_DYNAMIC_BUTTON_ALT, UI_TEXTBOX, UI_COPYRIGHT_INFO, \
    AUDIO_INCREMENT, AUDIO_VOLUME_MIN, AUDIO_VOLUME_MAX
from data.files import DIR_UI
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.raceselectionmanager import RaceSelectionManager
from utils.mathutils import ClosestNumber
from utils.uiutils import ImageAlign, DrawSprite, ScaledButton, DrawText, TextBox


class OptionsScreen:
    def __init__(self, font: Font):
        self.font = font
        self.UpdateScreen()

    def UpdateScreen(self):
        # setup
        self.new_options = GameManager().GetOptions().Copy()
        screen_size = GameManager().GetResolution()
        res_scale = GameManager().GetResolutionScale()
        min_offset = ClosestNumber(screen_size.y / 16, res_scale)

        # background
        bg_sp = pygame.sprite.Sprite()
        bg_image = pygame.image.load(DIR_UI + "OptionsMenuBg.png").convert_alpha()
        scale = res_scale
        bg_sp.image = pygame.transform.scale(bg_image,
                                             (bg_image.get_width() * scale, bg_image.get_height() * scale))
        bg_sp.rect = bg_sp.image.get_rect()
        self.background_sprite = bg_sp

        # text boxes
        res = RESOLUTIONS[self.new_options.current_resolution][0]
        res_text = f"{int(res[0])} x {int(res[1])}"
        self.resolution_textbox = TextBox(UI_TEXTBOX, res_text, self.font,
                                          (screen_size.x / 2 + min_offset * 5, min_offset * 2),
                                          1, 2, ImageAlign.CENTER, 200)
        self.border_textbox = TextBox(UI_TEXTBOX, "Border", self.font,
                                      (screen_size.x / 2 + min_offset * 1, min_offset * 4),
                                      1, 2, ImageAlign.CENTER, 155)
        self.ui_volume_textbox = TextBox(UI_TEXTBOX, "UI Volume", self.font,
                                         (screen_size.x / 4 + min_offset * 1, screen_size.y - 4 * min_offset),
                                         width=130)
        self.ui_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.ui_volume * 10)), self.font,
                                               (screen_size.x / 4 + min_offset * 5, screen_size.y - 4 * min_offset),
                                               width=34)
        self.sfx_volume_textbox = TextBox(UI_TEXTBOX, "SFX Volume", self.font,
                                          (screen_size.x / 4 + min_offset * 3, screen_size.y - 6 * min_offset),
                                          width=130)
        self.sfx_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.sfx_volume * 10)), self.font,
                                                (screen_size.x / 4 + min_offset * 7, screen_size.y - 6 * min_offset),
                                                width=34)
        self.music_volume_textbox = TextBox(UI_TEXTBOX, "Music Volume", self.font,
                                            (screen_size.x / 4 + min_offset * 5, screen_size.y - 8 * min_offset),
                                            width=130)
        self.music_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.music_volume * 10)), self.font,
                                                  (screen_size.x / 4 + min_offset * 9, screen_size.y - 8 * min_offset),
                                                  width=34)

        # buttons
        button_pos = (screen_size.x / 2, screen_size.y / 2)
        self.accept_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Accept", self.font,
                                          (button_pos[0] - min_offset * 8, button_pos[1] + min_offset * 6),
                                          1, 2, ImageAlign.CENTER)
        self.cancel_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Cancel", self.font,
                                          (button_pos[0], button_pos[1] + min_offset * 6),
                                          1, 2, ImageAlign.CENTER)
        res_box_width_half = int(self.resolution_textbox.width / 2) * GameManager().GetResolutionScale()
        self.res_lower_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                             (self.resolution_textbox.pos[0] - int(res_box_width_half) - min_offset,
                                              self.resolution_textbox.pos[1]),
                                             1, 2, ImageAlign.CENTER, decals_on=False)
        self.res_raise_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                             (self.resolution_textbox.pos[0] + int(res_box_width_half) + min_offset,
                                              self.resolution_textbox.pos[1]),
                                             1, 2, ImageAlign.CENTER, decals_on=False)
        self.border_toggle = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "x", self.font,
                                          (self.resolution_textbox.pos[0] + int(res_box_width_half) - min_offset * 4 + 20,
                                           self.resolution_textbox.pos[1] + min_offset * 2),
                                          1, 2, ImageAlign.CENTER, decals_on=False, toggle_type=True)
        self.border_toggle.toggled = GameManager().GetBorder()
        self.ui_volume_lower_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                   (screen_size.x / 4 + min_offset * 7, screen_size.y - 4 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)
        self.ui_volume_raise_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                   (screen_size.x / 4 + min_offset * 9, screen_size.y - 4 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)
        self.sfx_volume_lower_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                   (screen_size.x / 4 + min_offset * 9, screen_size.y - 6 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)
        self.sfx_volume_raise_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                   (screen_size.x / 4 + min_offset * 11, screen_size.y - 6 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)
        self.music_volume_lower_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                   (screen_size.x / 4 + min_offset * 11, screen_size.y - 8 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)
        self.music_volume_raise_button = ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                   (screen_size.x / 4 + min_offset * 13, screen_size.y - 8 * min_offset),
                                                   1, 2, ImageAlign.CENTER, decals_on=False)

    def UpdateTexts(self):
        # update button values
        res = RESOLUTIONS[self.new_options.current_resolution][0]
        res_text = f"{int(res[0])} x {int(res[1])}"
        self.resolution_textbox = TextBox(UI_TEXTBOX, res_text, self.font,
                                          self.resolution_textbox.pos, 1, 2,
                                          self.resolution_textbox.align, self.resolution_textbox.width)
        self.ui_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.ui_volume * 10)), self.font,
                                               self.ui_volume_value_textbox.pos,
                                               width=self.ui_volume_value_textbox.width)
        self.sfx_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.sfx_volume * 10)), self.font,
                                                self.sfx_volume_value_textbox.pos,
                                                width=self.sfx_volume_value_textbox.width)
        self.music_volume_value_textbox = TextBox(UI_TEXTBOX, str(int(self.new_options.music_volume * 10)), self.font,
                                                  self.music_volume_value_textbox.pos,
                                                  width=self.music_volume_value_textbox.width)

    def OptionsLoop(self, font: Font, clock: pygame.time.Clock):
        globalvars.SCREEN.fill((0, 0, 0))
        screen_size = GameManager().GetResolution()
        res_scale = GameManager().GetResolutionScale()

        DrawSprite(self.background_sprite, globalvars.SCREEN, (0, 0))
        min_offset = ClosestNumber(screen_size.y / 32, res_scale)
        DrawText(UI_COPYRIGHT_INFO, globalvars.SCREEN, font,
                 (screen_size.x / 4 + min_offset * 6, screen_size.y - min_offset), ImageAlign.CENTER)

        self.resolution_textbox.Draw(globalvars.SCREEN)
        self.border_textbox.Draw(globalvars.SCREEN)
        self.ui_volume_textbox.Draw(globalvars.SCREEN)
        self.ui_volume_value_textbox.Draw(globalvars.SCREEN)
        self.sfx_volume_textbox.Draw(globalvars.SCREEN)
        self.sfx_volume_value_textbox.Draw(globalvars.SCREEN)
        self.music_volume_textbox.Draw(globalvars.SCREEN)
        self.music_volume_value_textbox.Draw(globalvars.SCREEN)

        if self.cancel_button.Draw(globalvars.SCREEN):
            self.new_options = GameManager().GetOptions().Copy()
            self.UpdateTexts()
            GameManager().SetState(State.Main_Menu)

        if self.res_lower_button.Draw(globalvars.SCREEN):
            self.new_options.current_resolution -= 1
            if self.new_options.current_resolution < 0:
                self.new_options.current_resolution = 0
            self.UpdateTexts()

        if self.res_raise_button.Draw(globalvars.SCREEN):
            self.new_options.current_resolution += 1
            if self.new_options.current_resolution >= len(RESOLUTIONS):
                self.new_options.current_resolution = len(RESOLUTIONS) - 1
            self.UpdateTexts()

        if self.ui_volume_lower_button.Draw(globalvars.SCREEN):
            self.new_options.ui_volume -= AUDIO_INCREMENT
            if self.new_options.ui_volume < AUDIO_VOLUME_MIN:
                self.new_options.ui_volume = AUDIO_VOLUME_MIN
            self.UpdateTexts()

        if self.ui_volume_raise_button.Draw(globalvars.SCREEN):
            self.new_options.ui_volume += AUDIO_INCREMENT
            if self.new_options.ui_volume > AUDIO_VOLUME_MAX:
                self.new_options.ui_volume = AUDIO_VOLUME_MAX
            self.UpdateTexts()

        if self.sfx_volume_lower_button.Draw(globalvars.SCREEN):
            self.new_options.sfx_volume -= AUDIO_INCREMENT
            if self.new_options.sfx_volume < AUDIO_VOLUME_MIN:
                self.new_options.sfx_volume = AUDIO_VOLUME_MIN
            self.UpdateTexts()

        if self.sfx_volume_raise_button.Draw(globalvars.SCREEN):
            self.new_options.sfx_volume += AUDIO_INCREMENT
            if self.new_options.sfx_volume > AUDIO_VOLUME_MAX:
                self.new_options.sfx_volume = AUDIO_VOLUME_MAX
            self.UpdateTexts()

        if self.music_volume_lower_button.Draw(globalvars.SCREEN):
            self.new_options.music_volume -= AUDIO_INCREMENT
            if self.new_options.music_volume < AUDIO_VOLUME_MIN:
                self.new_options.music_volume = AUDIO_VOLUME_MIN
            self.UpdateTexts()

        if self.music_volume_raise_button.Draw(globalvars.SCREEN):
            self.new_options.music_volume += AUDIO_INCREMENT
            if self.new_options.music_volume > AUDIO_VOLUME_MAX:
                self.new_options.music_volume = AUDIO_VOLUME_MAX
            self.UpdateTexts()

        if self.border_toggle.Draw(globalvars.SCREEN):
            self.new_options.current_windowed = pygame.NOEVENT
        else:
            self.new_options.current_windowed = pygame.NOFRAME

        if self.accept_button.Draw(globalvars.SCREEN):
            GameManager().SetOptions(self.new_options)
            GameManager().GetOptions().Save()
            GameManager().SetResolution(self.new_options.current_resolution)
            GameManager().options_menu.UpdateScreen()
            GameManager().main_menu.UpdateScreen()
            GameManager().race_selection_menu.UpdateScreen()
            GameManager().SetState(State.Main_Menu)
            pygame.mixer.music.set_volume(self.new_options.music_volume)
            RaceSelectionManager().Free()

        # handle inputs
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit(0)
        inputs = InputManager().get_inputs(events)
        if inputs[INPUT_QUIT]:
            GameManager().SetState(State.Main_Menu)

        # update last frame time
        globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

        # end draw step
        pygame.display.flip()
        clock.tick(FPS)
