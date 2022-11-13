import json
import time
from typing import Optional

import pygame
from enum import Enum

import pymunk
from pygame.font import Font
from data.constants import *
from data.enums import Direction
from data.files import *
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track
from utils.timerutils import FormatTime
from utils.uiutils import DrawText, Button, TextAlign
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager


class State(Enum):
    Main_Menu = 0
    In_Race = 1


def CenterCamera(camera: pygame.Vector2, target: pymunk.Vec2d, smoothing: bool = True):
    camera_target_pos = pygame.Vector2(-target.x, -target.y) + SCREEN_SIZE / 2
    if smoothing:
        camera = camera_target_pos + (camera - camera_target_pos) * CAMERA_MOVEMENT_SPEED
    else:
        camera = camera_target_pos
    if camera.x < -RaceManager().track.size.x + SCREEN_SIZE.x:
        camera.x = -RaceManager().track.size.x + SCREEN_SIZE.x
    if camera.x > 0:
        camera.x = 0
    if camera.y < -RaceManager().track.size.y + SCREEN_SIZE.y:
        camera.y = -RaceManager().track.size.y + SCREEN_SIZE.y
    if camera.y > 0:
        camera.y = 0
    return camera


def RaceLoop(screen: pygame.Surface, font: Font, clock: pygame.time.Clock):
    # race initialization
    if not RaceManager().is_initialized:
        player_index = 0
        RaceManager().SetupRace(
            Track(**json.load(open(TRACKS_2))),
            [
                Car("Player", **json.load((open(CAR_1)))),
                Car("AI 1", **json.load((open(CAR_2)))),
                Car("AI 2", **json.load((open(CAR_2)))),
                Car("AI 3", **json.load((open(CAR_2))))],
            player_index)
        RaceManager().cars[player_index].agent.is_enabled = False
        for car in RaceManager().cars:
            car.Update()

    # handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)

    # countdown
    if not RaceManager().is_started and RaceManager().countdown_time > 1:
        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs["quit"]:
            GameManager().SetState(State.Main_Menu)
            return
        RaceManager().countdown_time = RACE_COUNTDOWN - (time.perf_counter() - RaceManager().start_time)

    # race start
    if not RaceManager().is_started and RaceManager().countdown_time <= 1:
        RaceManager().StartRace()

    # DEBUG START
    if ENVIRONMENT_DEBUG:
        # modify player car stats
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    RaceManager().player_car.handling -= 0.1
                elif event.key == pygame.K_RIGHTBRACKET:
                    RaceManager().player_car.handling += 0.1
                elif event.key == pygame.K_o:
                    RaceManager().player_car.power -= 50
                elif event.key == pygame.K_p:
                    RaceManager().player_car.power += 50
                elif event.key == pygame.K_u:
                    RaceManager().player_car.traction -= 10
                elif event.key == pygame.K_i:
                    RaceManager().player_car.traction += 10
                elif event.key == pygame.K_k:
                    RaceManager().player_car.body.mass -= 0.1
                    RaceManager().player_car.body.center_of_gravity = (-RaceManager().player_car.size[0] * 0.4, 0)
                elif event.key == pygame.K_l:
                    RaceManager().player_car.body.mass += 0.1
                    RaceManager().player_car.body.center_of_gravity = (-RaceManager().player_car.size[0] * 0.4, 0)
                elif event.key == pygame.K_m:
                    RaceManager().agents[0].is_enabled = not RaceManager().agents[0].is_enabled
    # DEBUG END

    # camera follow player & clamp to map size
    RaceManager().camera = CenterCamera(RaceManager().camera, RaceManager().player_car.body.position)

    if RaceManager().is_started:
        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs["quit"]:
            GameManager().SetState(State.Main_Menu)
            return
        if not RaceManager().player_car.has_finished:
            RaceManager().player_car.handbrake = inputs["handbrake"]
            if inputs["forward"].__abs__() > JOYSTICK_DEADZONE:
                RaceManager().player_car.Move(Direction.Forward, inputs["forward"])
            if inputs["right"].__abs__() > JOYSTICK_DEADZONE:
                RaceManager().player_car.Move(Direction.Right, inputs["right"])

            # reindex shapes after rotating
            for car in RaceManager().cars:
                RaceManager().space.reindex_shapes_for_body(car.body)

    if RaceManager().is_started:
        # car update
        for car in RaceManager().cars:
            car.Update()
        # ai update
        for agent in RaceManager().agents:
            agent.Update()

        # physics step
        RaceManager().space.step(1 / PHYSICS_FPS)

    # start draw step
    # DEBUG START
    if ENVIRONMENT_DEBUG:
        if RaceManager().background:
            screen.blit(RaceManager().background, RaceManager().camera)
        RaceManager().pymunk_screen.fill((12, 12, 12))
        RaceManager().space.debug_draw(RaceManager().draw_options)
    # DEBUG END
    screen.blit(RaceManager().pymunk_screen, RaceManager().camera)
    RaceManager().sprites.update(events)
    for s in RaceManager().sprites:
        screen.blit(s.image, s.rect.move(*RaceManager().camera))
    if not RaceManager().is_started:
        DrawText(str(int(RaceManager().countdown_time)), screen, font, SCREEN_SIZE / 2, TextAlign.CENTER, 5)

    # DEBUG START
    if ENVIRONMENT_DEBUG:
        # draw debug info
        DrawText("Handling: " + str(round(RaceManager().player_car.handling, 1)), screen, font, (20, 20))
        DrawText("Power: " + str(int(RaceManager().player_car.power)), screen, font, (20, 60))
        DrawText("Traction: " + str(RaceManager().player_car.traction), screen, font, (20, 100))
        DrawText("Mass: " + str(RaceManager().player_car.body.mass), screen, font, (20, 140))
        DrawText("Speed: " + str(int(RaceManager().player_car.body.velocity.length)), screen, font, (20, 180))
        if RaceManager().is_started:
            DrawText(FormatTime(RaceManager().GetTime()), screen, font, (SCREEN_SIZE.x / 2, 20), TextAlign.CENTER)
        else:
            DrawText(FormatTime(0), screen, font, (SCREEN_SIZE.x / 2, 20), TextAlign.CENTER)
        RaceManager().agents[0].DebugDrawRays(screen, RaceManager().camera)
        RaceManager().agents[0].DebugDrawInfo(screen, font)
        if not RaceManager().is_over:
            RaceManager().DebugDrawInfo(screen, font, RaceManager().player_car)
        else:
            if list(RaceManager().final_lineup.keys())[0] == RaceManager().player_car:
                win_pos = SCREEN_SIZE / 2
                DrawText("You Win!", screen, font, win_pos, TextAlign.CENTER)
                DrawText("Press Escape", screen, font, (win_pos.x, win_pos.y + 30), TextAlign.CENTER)
            else:
                lose_pos = SCREEN_SIZE / 2
                DrawText("You Lose!", screen, font, (lose_pos.x, lose_pos.y + 30), TextAlign.CENTER)
            leaderboard_pos = (SCREEN_SIZE.x - 20, 20)
            for car, finish_time in RaceManager().final_lineup.items():
                DrawText(car.name + " " + FormatTime(finish_time), screen, font, leaderboard_pos, TextAlign.TOP_RIGHT)
                leaderboard_pos = (leaderboard_pos[0], leaderboard_pos[1] + 40)
    # DEBUG END

    # end draw step
    pygame.display.flip()
    clock.tick(FPS)


def MainMenuLoop(screen: pygame.Surface, font: Font, clock: pygame.time.Clock):
    screen.fill((33, 50, 80))

    start_button = Button("Start", font, (SCREEN_SIZE.x / 2, SCREEN_SIZE.y / 2), 2, TextAlign.CENTER)
    exit_button = Button("Exit", font, (SCREEN_SIZE.x / 2, SCREEN_SIZE.y / 2 + 200), 2, TextAlign.CENTER)

    if start_button.Draw(screen):
        GameManager().SetState(State.In_Race)
    if exit_button.Draw(screen):
        pygame.quit()
        sys.exit()

    # handle inputs
    events = pygame.event.get()
    inputs = InputManager().get_inputs(events)
    if inputs["quit"]:
        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(FPS)


class GameManager(metaclass=Singleton):
    def __init__(self):
        self._state = State.Main_Menu

    def GetState(self):
        return self._state

    def SetState(self, state: State):
        if self._state == State.Main_Menu:
            if state == State.In_Race:
                self._state = state
        if self._state == State.In_Race:
            if state == State.Main_Menu:
                RaceManager().Free()
                self._state = state
