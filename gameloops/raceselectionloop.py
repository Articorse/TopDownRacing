import random
import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import AI_PLAYER_ON, FPS, INPUT_QUIT, AUDIO_CANCEL, UI_SMALL_BUTTON, UI_BIG_BUTTON, AUDIO_BGM1
from entities.car import Car
from managers.audiomanager import AudioManager
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager
from managers.raceselectionmanager import RaceSelectionManager
from utils.uiutils import Button, ImageAlign, DrawText, DrawSprite


class RaceSelection:
    def __init__(self, font: Font):
        self.font = font
        self.UpdateScreen()

    def UpdateScreen(self):
        self.screen_size = GameManager().GetResolution()
        self.car_image_pos = (self.screen_size.x / 6, self.screen_size.y / 5)
        self.track_image_pos = (self.screen_size.x - self.screen_size.x / 6, self.screen_size.y / 5)
        self.buttons = {"back": Button(UI_BIG_BUTTON, "Back", self.font,
                                       (self.screen_size.x * 0.33, self.screen_size.y - self.screen_size.y / 10),
                                       1, 2, ImageAlign.CENTER, AUDIO_CANCEL),
                        "start": Button(UI_BIG_BUTTON, "Start", self.font,
                                        (self.screen_size.x * 0.66, self.screen_size.y - self.screen_size.y / 10),
                                        1, 2, ImageAlign.CENTER), "prev car": Button(UI_SMALL_BUTTON, "Prev", self.font,
                                                                                     (self.car_image_pos[0],
                                                                                      self.car_image_pos[
                                                                                          1] + self.screen_size.y * 0.5),
                                                                                     .5),
                        "next car": Button(UI_SMALL_BUTTON, "Next", self.font,
                                           (self.car_image_pos[0] + 200,
                                            self.car_image_pos[1] + self.screen_size.y * 0.5), .5),
                        "prev track": Button(UI_SMALL_BUTTON, "Prev", self.font,
                                             (self.track_image_pos[0] - 200,
                                              self.track_image_pos[1] + self.screen_size.y * 0.5),
                                             .5, align=ImageAlign.TOP_RIGHT),
                        "next track": Button(UI_SMALL_BUTTON, "Next", self.font,
                                             (self.track_image_pos[0],
                                              self.track_image_pos[1] + self.screen_size.y * 0.5),
                                             .5, align=ImageAlign.TOP_RIGHT),
                        "less laps": Button(UI_SMALL_BUTTON, "-", self.font,
                                            (self.car_image_pos[0],
                                             self.car_image_pos[1] + self.screen_size.y * 0.6), .25),
                        "more laps": Button(UI_SMALL_BUTTON, "+", self.font,
                                            (self.car_image_pos[0] + 100,
                                             self.car_image_pos[1] + self.screen_size.y * 0.6), .25),
                        "less ai": Button(UI_SMALL_BUTTON, "-", self.font,
                                          (self.track_image_pos[0] - 100,
                                           self.track_image_pos[1] + self.screen_size.y * 0.6),
                                          .25, align=ImageAlign.TOP_RIGHT),
                        "more ai": Button(UI_SMALL_BUTTON, "+", self.font,
                                          (self.track_image_pos[0], self.track_image_pos[1] + self.screen_size.y * 0.6),
                                          .25, align=ImageAlign.TOP_RIGHT)}

    def RaceSelectionLoop(self, font: Font, clock: pygame.time.Clock):
        # selection screen initialization
        if not RaceSelectionManager().is_setup:
            RaceSelectionManager().Setup()

        globalvars.SCREEN.fill((0, 0, 0))
        car_model = RaceSelectionManager().GetCurrentCarModel()
        track = RaceSelectionManager().GetCurrentTrack()
        DrawSprite(car_model.sprite, globalvars.SCREEN, self.car_image_pos, scale=1)
        DrawSprite(track.thumbnail_path, globalvars.SCREEN, self.track_image_pos, align=ImageAlign.TOP_RIGHT, scale=1)
        DrawText(car_model.model_name, globalvars.SCREEN, font,
                 (self.car_image_pos[0], self.car_image_pos[1] + self.screen_size.y * 0.45))
        DrawText(track.name, globalvars.SCREEN, font,
                 (self.track_image_pos[0], self.track_image_pos[1] + self.screen_size.y * 0.45),
                 align=ImageAlign.TOP_RIGHT)
        DrawText("Laps: " + str(RaceSelectionManager().current_lap_count), globalvars.SCREEN, font,
                 (self.car_image_pos[0], self.car_image_pos[1] + self.screen_size.y * 0.55))
        DrawText("AIs: " + str(RaceSelectionManager().ai_count), globalvars.SCREEN, font,
                 (self.track_image_pos[0], self.track_image_pos[1] + self.screen_size.y * 0.55),
                 align=ImageAlign.TOP_RIGHT)

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
        if self.buttons["more ai"].Draw(globalvars.SCREEN):
            RaceSelectionManager().ai_count += 1

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
