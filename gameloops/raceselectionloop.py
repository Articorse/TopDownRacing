import random
import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import AI_PLAYER_ON, FPS, INPUT_QUIT, AUDIO_CANCEL, UI_SMALL_BUTTON, UI_BIG_BUTTON, AUDIO_BGM1, \
    UI_TEXTBOX, UI_DYNAMIC_BUTTON_ALT
from data.files import DIR_UI
from entities.car import Car
from managers.audiomanager import AudioManager
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager
from managers.raceselectionmanager import RaceSelectionManager
from utils.uiutils import Button, ImageAlign, DrawText, DrawSprite, TextBox, ScaledButton


class RaceSelection:
    def __init__(self, font: Font):
        self.font = font
        if not RaceSelectionManager().is_setup:
            RaceSelectionManager().Setup()
        self.UpdateScreen()

    def UpdateScreen(self):
        # setup
        res_scale = GameManager().GetResolutionScale()
        car_model = RaceSelectionManager().GetCurrentCarModel()
        track = RaceSelectionManager().GetCurrentTrack()

        # background
        bg_sp = pygame.sprite.Sprite()
        bg_image = pygame.image.load(DIR_UI + "RaceSelectionBg.png").convert_alpha()
        bg_sp.image = pygame.transform.scale(bg_image,
                                             (bg_image.get_width() * res_scale, bg_image.get_height() * res_scale))
        bg_sp.rect = bg_sp.image.get_rect()
        self.background_sprite = bg_sp

        # static ui
        frame_image = pygame.image.load(DIR_UI + "LargePanel.png").convert_alpha()
        car_frame_sp = pygame.sprite.Sprite()
        car_frame_sp.image = pygame.transform.scale(frame_image,
                                                    (frame_image.get_width() * res_scale,
                                                     frame_image.get_height() * res_scale))
        car_frame_sp.rect = car_frame_sp.image.get_rect()
        self.car_frame = car_frame_sp

        track_frame_sp = pygame.sprite.Sprite()
        track_frame_sp.image = pygame.transform.scale(frame_image,
                                                      (frame_image.get_width() * res_scale,
                                                       frame_image.get_height() * res_scale))
        track_frame_sp.rect = track_frame_sp.image.get_rect()
        self.track_frame = track_frame_sp

        self.car_textbox = TextBox(UI_TEXTBOX, car_model.model_name, self.font,
                                   (116 * res_scale, 171 * res_scale),
                                   1, 1, ImageAlign.TOP_LEFT, 155)

        self.track_textbox = TextBox(UI_TEXTBOX, track.name, self.font,
                                     (369 * res_scale, 171 * res_scale),
                                     1, 1, ImageAlign.TOP_LEFT, 155)

        self.laps_textbox = TextBox(UI_TEXTBOX, "laps", self.font,
                                    (76 * res_scale, 218 * res_scale),
                                    1, 2, ImageAlign.TOP_LEFT, 117)

        self.ai_textbox = TextBox(UI_TEXTBOX, "ais", self.font,
                                  (329 * res_scale, 218 * res_scale),
                                  1, 2, ImageAlign.TOP_LEFT, 117)

        self.lap_count_textbox = TextBox(UI_TEXTBOX, str(RaceSelectionManager().current_lap_count), self.font,
                                         (197 * res_scale, 218 * res_scale),
                                         1, 2, ImageAlign.TOP_LEFT, 34)

        self.ai_count_textbox = TextBox(UI_TEXTBOX, str(RaceSelectionManager().ai_count), self.font,
                                        (450 * res_scale, 218 * res_scale),
                                        1, 2, ImageAlign.TOP_LEFT, 34)

        self.car_image_pos = (192 * res_scale, 99 * res_scale)
        self.track_image_pos = (445 * res_scale, 99 * res_scale)

        # dynamic ui

        self.buttons = {"back": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Back", self.font,
                                             (140 * res_scale, 281 * res_scale),
                                             1, 2, ImageAlign.TOP_LEFT, action_sound=AUDIO_CANCEL),
                        "start": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "Start", self.font,
                                              (399 * res_scale, 281 * res_scale),
                                              1, 2, ImageAlign.TOP_LEFT),
                        "prev car": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                 (76 * res_scale, 172 * res_scale), 1, 2,
                                                 align=ImageAlign.TOP_LEFT, decals_on=False),
                        "next car": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                 (275 * res_scale, 172 * res_scale), 1, 2,
                                                 align=ImageAlign.TOP_LEFT, decals_on=False),
                        "prev track": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                   (329 * res_scale, 172 * res_scale), 1, 2,
                                                   align=ImageAlign.TOP_LEFT, decals_on=False),
                        "next track": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                   (528 * res_scale, 172 * res_scale), 1, 2,
                                                   align=ImageAlign.TOP_LEFT, decals_on=False),
                        "less laps": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                  (235 * res_scale, 219 * res_scale), 1, 2,
                                                  align=ImageAlign.TOP_LEFT, decals_on=False),
                        "more laps": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                  (275 * res_scale, 219 * res_scale), 1, 2,
                                                  align=ImageAlign.TOP_LEFT, decals_on=False),
                        "less ai": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "-", self.font,
                                                (488 * res_scale, 219 * res_scale), 1, 2,
                                                align=ImageAlign.TOP_LEFT, decals_on=False),
                        "more ai": ScaledButton(UI_DYNAMIC_BUTTON_ALT, "+", self.font,
                                                (528 * res_scale, 219 * res_scale), 1, 2,
                                                align=ImageAlign.TOP_LEFT, decals_on=False)}

    def UpdateTexts(self):
        # update button values
        car_model = RaceSelectionManager().GetCurrentCarModel()
        track = RaceSelectionManager().GetCurrentTrack()
        self.car_textbox = TextBox(UI_TEXTBOX, car_model.model_name, self.font,
                                   self.car_textbox.pos, 1, 1,
                                   self.car_textbox.align, self.car_textbox.width)
        self.track_textbox = TextBox(UI_TEXTBOX, track.name, self.font,
                                     self.track_textbox.pos, 1, 1,
                                     self.track_textbox.align, self.track_textbox.width)
        self.lap_count_textbox = TextBox(UI_TEXTBOX, str(RaceSelectionManager().current_lap_count), self.font,
                                         self.lap_count_textbox.pos, 1, 2,
                                         self.lap_count_textbox.align, self.lap_count_textbox.width)
        self.ai_count_textbox = TextBox(UI_TEXTBOX, str(RaceSelectionManager().ai_count), self.font,
                                        self.ai_count_textbox.pos, 1, 2,
                                        self.ai_count_textbox.align, self.ai_count_textbox.width)

    def RaceSelectionLoop(self, font: Font, clock: pygame.time.Clock):
        # setup
        if not RaceSelectionManager().is_setup:
            RaceSelectionManager().Setup()
        res_scale = GameManager().GetResolutionScale()
        car_model = RaceSelectionManager().GetCurrentCarModel()
        track = RaceSelectionManager().GetCurrentTrack()

        # background
        globalvars.SCREEN.fill((0, 0, 0))
        DrawSprite(self.background_sprite, globalvars.SCREEN, (0, 0))

        # static ui
        DrawSprite(self.car_frame, globalvars.SCREEN, (116 * res_scale, 45 * res_scale))
        DrawSprite(self.track_frame, globalvars.SCREEN, (369 * res_scale, 45 * res_scale))
        self.car_textbox.Draw(globalvars.SCREEN)
        self.track_textbox.Draw(globalvars.SCREEN)
        self.ai_textbox.Draw(globalvars.SCREEN)
        self.ai_count_textbox.Draw(globalvars.SCREEN)
        self.laps_textbox.Draw(globalvars.SCREEN)
        self.lap_count_textbox.Draw(globalvars.SCREEN)
        DrawSprite(car_model.sprite, globalvars.SCREEN, self.car_image_pos, align=ImageAlign.CENTER)
        DrawSprite(track.thumbnail_path, globalvars.SCREEN, self.track_image_pos, align=ImageAlign.CENTER)

        # dynamic ui
        if self.buttons["prev car"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_car_index -= 1
            if RaceSelectionManager().current_car_index < 0:
                RaceSelectionManager().current_car_index = len(RaceSelectionManager().available_cars) - 1
        if self.buttons["next car"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_car_index += 1
            if RaceSelectionManager().current_car_index >= len(RaceSelectionManager().available_cars):
                RaceSelectionManager().current_car_index = 0
        if self.buttons["prev track"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_track_index -= 1
            if RaceSelectionManager().current_track_index < 0:
                RaceSelectionManager().current_track_index = len(RaceSelectionManager().available_tracks) - 1
        if self.buttons["next track"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_track_index += 1
            if RaceSelectionManager().current_track_index >= len(RaceSelectionManager().available_tracks):
                RaceSelectionManager().current_track_index = 0

        if self.buttons["less laps"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_lap_count -= 1
            if RaceSelectionManager().current_lap_count <= 0:
                RaceSelectionManager().current_lap_count = 1
        if self.buttons["more laps"].Draw(globalvars.SCREEN):
            RaceSelectionManager().current_lap_count += 1

        if self.buttons["less ai"].Draw(globalvars.SCREEN):
            RaceSelectionManager().ai_count -= 1
            if RaceSelectionManager().ai_count < 0:
                RaceSelectionManager().ai_count = 0
            self.UpdateTexts()
        if self.buttons["more ai"].Draw(globalvars.SCREEN):
            RaceSelectionManager().ai_count += 1

        self.UpdateTexts()

        if self.buttons["back"].Draw(globalvars.SCREEN):
            GameManager().SetState(State.Main_Menu)
            return
        if self.buttons["start"].Draw(globalvars.SCREEN):
            pc = Car("Player", RaceSelectionManager().GetCurrentCarModel())
            cars = [pc]
            for i in range(RaceSelectionManager().ai_count):
                cars.append(
                    Car("AI " + str(i),
                        RaceSelectionManager().available_cars[random.randint(0,
                                                              len(RaceSelectionManager().available_cars) - 1)]))
            globalvars.RACE_MANAGER = RaceManager()
            globalvars.RACE_MANAGER.Setup(
                RaceSelectionManager().GetCurrentTrack(), pc, RaceSelectionManager().current_lap_count, *cars)
            pc.agent.is_enabled = AI_PLAYER_ON
            for car_model in globalvars.RACE_MANAGER.cars:
                car_model.Update()
            RaceSelectionManager().Free()
            AudioManager().Play_Music(AUDIO_BGM1)
            GameManager().SetState(State.In_Race)
            return

        # handle inputs
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit(0)
        inputs = InputManager().get_inputs(events)
        if inputs[INPUT_QUIT]:
            AudioManager().Play_Sound(AUDIO_CANCEL)
            GameManager().SetState(State.Main_Menu)
            return

        # update last frame time
        globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

        # end draw step
        pygame.display.flip()
        clock.tick(FPS)
