import random
import sys
import pygame
from pygame.font import Font
from data.constants import SCREEN_SIZE, AI_PLAYER_ON, FPS, INPUT_QUIT
from entities.car import Car
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager
from managers.raceselectionmanager import RaceSelectionManager
from utils.uiutils import Button, ImageAlign, DrawText, DrawSprite


def RaceSelectionLoop(screen: pygame.Surface, font: Font, clock: pygame.time.Clock):
    # selection screen initialization
    car_image_pos = (300, 200)
    track_image_pos = (SCREEN_SIZE.x - 300, 200)
    if not RaceSelectionManager().is_setup:
        RaceSelectionManager().Setup()
        RaceSelectionManager().buttons["back"] = \
            Button("Back", font, (SCREEN_SIZE.x * 0.33, SCREEN_SIZE.y - 100), 2, ImageAlign.CENTER)
        RaceSelectionManager().buttons["start"] = \
            Button("Start", font, (SCREEN_SIZE.x * 0.66, SCREEN_SIZE.y - 100), 2, ImageAlign.CENTER)
        RaceSelectionManager().buttons["prev car"] = \
            Button("Prev", font, (car_image_pos[0], car_image_pos[1] + 550))
        RaceSelectionManager().buttons["next car"] = \
            Button("Next", font, (car_image_pos[0] + 100, car_image_pos[1] + 550))
        RaceSelectionManager().buttons["prev track"] = \
            Button("Prev", font, (track_image_pos[0] - 100, track_image_pos[1] + 550), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["next track"] = \
            Button("Next", font, (track_image_pos[0], track_image_pos[1] + 550), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["less laps"] = \
            Button("-", font, (car_image_pos[0], car_image_pos[1] + 650))
        RaceSelectionManager().buttons["more laps"] = \
            Button("+", font, (car_image_pos[0] + 50, car_image_pos[1] + 650))
        RaceSelectionManager().buttons["less ai"] = \
            Button("-", font, (track_image_pos[0] - 50, track_image_pos[1] + 650), align=ImageAlign.TOP_RIGHT)
        RaceSelectionManager().buttons["more ai"] = \
            Button("+", font, (track_image_pos[0], track_image_pos[1] + 650), align=ImageAlign.TOP_RIGHT)

    screen.fill((33, 50, 50))
    car_model = RaceSelectionManager().GetCurrentCarModel()
    track = RaceSelectionManager().GetCurrentTrack()
    DrawSprite(car_model.sprite, screen, car_image_pos, scale=1)
    DrawSprite(track.thumbnail_path, screen, track_image_pos, align=ImageAlign.TOP_RIGHT, scale=1)
    DrawText(car_model.model_name, screen, font, (car_image_pos[0], car_image_pos[1] + 500))
    DrawText(track.name, screen, font, (track_image_pos[0], track_image_pos[1] + 500), align=ImageAlign.TOP_RIGHT)
    DrawText("Laps: " + str(RaceSelectionManager().current_lap_count),
             screen, font, (car_image_pos[0], car_image_pos[1] + 600))
    DrawText("AIs: " + str(RaceSelectionManager().ai_count),
             screen, font, (track_image_pos[0], track_image_pos[1] + 600), align=ImageAlign.TOP_RIGHT)

    if RaceSelectionManager().buttons["prev car"].Draw(screen):
        RaceSelectionManager().current_car_index -= 1
        if RaceSelectionManager().current_car_index < 0:
            RaceSelectionManager().current_car_index = len(RaceSelectionManager().available_cars) - 1
    if RaceSelectionManager().buttons["next car"].Draw(screen):
        RaceSelectionManager().current_car_index += 1
        if RaceSelectionManager().current_car_index >= len(RaceSelectionManager().available_cars):
            RaceSelectionManager().current_car_index = 0
    if RaceSelectionManager().buttons["prev track"].Draw(screen):
        RaceSelectionManager().current_track_index -= 1
        if RaceSelectionManager().current_track_index < 0:
            RaceSelectionManager().current_track_index = len(RaceSelectionManager().available_tracks) - 1
    if RaceSelectionManager().buttons["next track"].Draw(screen):
        RaceSelectionManager().current_track_index += 1
        if RaceSelectionManager().current_track_index >= len(RaceSelectionManager().available_tracks):
            RaceSelectionManager().current_track_index = 0

    if RaceSelectionManager().buttons["less laps"].Draw(screen):
        RaceSelectionManager().current_lap_count -= 1
        if RaceSelectionManager().current_lap_count <= 0:
            RaceSelectionManager().current_lap_count = 1
    if RaceSelectionManager().buttons["more laps"].Draw(screen):
        RaceSelectionManager().current_lap_count += 1

    if RaceSelectionManager().buttons["less ai"].Draw(screen):
        RaceSelectionManager().ai_count -= 1
        if RaceSelectionManager().ai_count < 0:
            RaceSelectionManager().ai_count = 0
    if RaceSelectionManager().buttons["more ai"].Draw(screen):
        RaceSelectionManager().ai_count += 1

    if RaceSelectionManager().buttons["back"].Draw(screen):
        GameManager().SetState(State.Main_Menu)
        return
    if RaceSelectionManager().buttons["start"].Draw(screen):
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
