import random
import sys
import pygame
from pygame.font import Font

from data import globalvars
from data.constants import AI_PLAYER_ON, FPS, INPUT_QUIT, RESOLUTIONS
from data.globalvars import CURRENT_RESOLUTION
from entities.car import Car
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager
from managers.raceselectionmanager import RaceSelectionManager
from utils.uiutils import Button, ImageAlign, DrawText, DrawSprite


def RaceSelectionLoop(font: Font, clock: pygame.time.Clock):
    # selection screen initialization
    screen_size = RESOLUTIONS[CURRENT_RESOLUTION][0]
    car_image_pos = (screen_size.x / 6, screen_size.y / 5)
    track_image_pos = (screen_size.x - screen_size.x / 6, screen_size.y / 5)
    if not RaceSelectionManager().is_setup:
        RaceSelectionManager().Setup()
        RaceSelectionManager().buttons["back"] = \
            Button("Back", font, (screen_size.x * 0.33, screen_size.y - screen_size.y / 10), 2, ImageAlign.CENTER)
        RaceSelectionManager().buttons["start"] = \
            Button("Start", font, (screen_size.x * 0.66, screen_size.y - screen_size.y / 10), 2, ImageAlign.CENTER)
        RaceSelectionManager().buttons["prev car"] = \
            Button("Prev", font, (car_image_pos[0], car_image_pos[1] + screen_size.y * 0.5))
        RaceSelectionManager().buttons["next car"] = \
            Button("Next", font, (car_image_pos[0] + 100, car_image_pos[1] + screen_size.y * 0.5))
        RaceSelectionManager().buttons["prev track"] = \
            Button("Prev", font,
                   (track_image_pos[0] - 100, track_image_pos[1] + screen_size.y * 0.5), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["next track"] = \
            Button("Next", font,
                   (track_image_pos[0], track_image_pos[1] + screen_size.y * 0.5), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["less laps"] = \
            Button("-", font, (car_image_pos[0], car_image_pos[1] + screen_size.y * 0.6))
        RaceSelectionManager().buttons["more laps"] = \
            Button("+", font, (car_image_pos[0] + 50, car_image_pos[1] + screen_size.y * 0.6))
        RaceSelectionManager().buttons["less ai"] = \
            Button("-", font,
                   (track_image_pos[0] - 50, track_image_pos[1] + screen_size.y * 0.6), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["more ai"] = \
            Button("+", font,
                   (track_image_pos[0], track_image_pos[1] + screen_size.y * 0.6), align=ImageAlign.TOP_RIGHT)

    globalvars.SCREEN.fill((33, 50, 50))
    car_model = RaceSelectionManager().GetCurrentCarModel()
    track = RaceSelectionManager().GetCurrentTrack()
    DrawSprite(car_model.sprite, globalvars.SCREEN, car_image_pos, scale=1)
    DrawSprite(track.thumbnail_path, globalvars.SCREEN, track_image_pos, align=ImageAlign.TOP_RIGHT, scale=1)
    DrawText(car_model.model_name, globalvars.SCREEN, font,
             (car_image_pos[0], car_image_pos[1] + screen_size.y * 0.45))
    DrawText(track.name, globalvars.SCREEN, font,
             (track_image_pos[0], track_image_pos[1] + screen_size.y * 0.45), align=ImageAlign.TOP_RIGHT)
    DrawText("Laps: " + str(RaceSelectionManager().current_lap_count),
             globalvars.SCREEN, font, (car_image_pos[0], car_image_pos[1] + screen_size.y * 0.55))
    DrawText("AIs: " + str(RaceSelectionManager().ai_count),
             globalvars.SCREEN, font, (track_image_pos[0], track_image_pos[1] + screen_size.y * 0.55), align=ImageAlign.TOP_RIGHT)

    if RaceSelectionManager().buttons["prev car"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_car_index -= 1
        if RaceSelectionManager().current_car_index < 0:
            RaceSelectionManager().current_car_index = len(RaceSelectionManager().available_cars) - 1
    if RaceSelectionManager().buttons["next car"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_car_index += 1
        if RaceSelectionManager().current_car_index >= len(RaceSelectionManager().available_cars):
            RaceSelectionManager().current_car_index = 0
    if RaceSelectionManager().buttons["prev track"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_track_index -= 1
        if RaceSelectionManager().current_track_index < 0:
            RaceSelectionManager().current_track_index = len(RaceSelectionManager().available_tracks) - 1
    if RaceSelectionManager().buttons["next track"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_track_index += 1
        if RaceSelectionManager().current_track_index >= len(RaceSelectionManager().available_tracks):
            RaceSelectionManager().current_track_index = 0

    if RaceSelectionManager().buttons["less laps"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_lap_count -= 1
        if RaceSelectionManager().current_lap_count <= 0:
            RaceSelectionManager().current_lap_count = 1
    if RaceSelectionManager().buttons["more laps"].Draw(globalvars.SCREEN):
        RaceSelectionManager().current_lap_count += 1

    if RaceSelectionManager().buttons["less ai"].Draw(globalvars.SCREEN):
        RaceSelectionManager().ai_count -= 1
        if RaceSelectionManager().ai_count < 0:
            RaceSelectionManager().ai_count = 0
    if RaceSelectionManager().buttons["more ai"].Draw(globalvars.SCREEN):
        RaceSelectionManager().ai_count += 1

    if RaceSelectionManager().buttons["back"].Draw(globalvars.SCREEN):
        GameManager().SetState(State.Main_Menu)
        return
    if RaceSelectionManager().buttons["start"].Draw(globalvars.SCREEN):
        pc = Car("Player", RaceSelectionManager().GetCurrentCarModel())
        cars = [pc]
        for i in range(RaceSelectionManager().ai_count):
            cars.append(
                Car("AI " + str(i),
                    RaceSelectionManager().available_cars[random.randint(0,
                                                          len(RaceSelectionManager().available_cars) - 1)]))
        RaceManager().Setup(
            RaceSelectionManager().GetCurrentTrack(), pc, RaceSelectionManager().current_lap_count, *cars)
        pc.agent.is_enabled = AI_PLAYER_ON
        for car_model in RaceManager().cars:
            car_model.Update()
        RaceSelectionManager().Free()
        GameManager().SetState(State.In_Race)
        return

    # handle inputs
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
    inputs = InputManager().get_inputs(events)
    if inputs[INPUT_QUIT]:
        GameManager().SetState(State.Main_Menu)
        return

    pygame.display.flip()
    clock.tick(FPS)
