import json
from typing import Optional

import pygame
from enum import Enum
from pygame.font import Font
from data.constants import *
from data.enums import Direction
from data.files import *
from entities.car import Car
from entities.singleton import Singleton
from entities.track import Track
from utils.uiutils import DrawText, Button, TextAlign
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager


class State(Enum):
    Main_Menu = 0
    In_Race = 1


def RaceLoop(screen: pygame.Surface, font: Font, clock: pygame.time.Clock, background: Optional[pygame.Surface] = None):
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

    # handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)

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
    camera_target_pos = pygame.Vector2(
        -RaceManager().player_car.body.position.x,
        -RaceManager().player_car.body.position.y) + SCREEN_SIZE / 2
    RaceManager().camera = camera_target_pos + (RaceManager().camera - camera_target_pos) * CAMERA_MOVEMENT_SPEED
    if RaceManager().camera.x < -MAP_SIZE.x + SCREEN_SIZE.x:
        RaceManager().camera.x = -MAP_SIZE.x + SCREEN_SIZE.x
    if RaceManager().camera.x > 0:
        RaceManager().camera.x = 0
    if RaceManager().camera.y < -MAP_SIZE.y + SCREEN_SIZE.y:
        RaceManager().camera.y = -MAP_SIZE.y + SCREEN_SIZE.y
    if RaceManager().camera.y > 0:
        RaceManager().camera.y = 0

    # handle inputs
    inputs = InputManager().get_inputs(events)
    if inputs["quit"]:
        GameManager().SetState(State.Main_Menu)
        return
    RaceManager().player_car.handbrake = inputs["handbrake"]
    if inputs["forward"].__abs__() > JOYSTICK_DEADZONE:
        RaceManager().player_car.Move(Direction.Forward, inputs["forward"])
    if inputs["right"].__abs__() > JOYSTICK_DEADZONE:
        RaceManager().player_car.Move(Direction.Right, inputs["right"])

    # reindex shapes after rotating
    for car in RaceManager().cars:
        RaceManager().space.reindex_shapes_for_body(car.body)

    # car update
    for car in RaceManager().cars:
        car.Update()
    for agent in RaceManager().agents:
        agent.Update()

    # physics step
    RaceManager().space.step(1 / PHYSICS_FPS)

    # start draw step
    # DEBUG START
    if ENVIRONMENT_DEBUG:
        screen.blit(background, RaceManager().camera)
        RaceManager().pymunk_screen.fill((12, 12, 12))
        RaceManager().space.debug_draw(RaceManager().draw_options)
    # DEBUG END
    screen.blit(RaceManager().pymunk_screen, RaceManager().camera)
    RaceManager().sprites.update(events)
    for s in RaceManager().sprites:
        screen.blit(s.image, s.rect.move(*RaceManager().camera))

    # DEBUG START
    if ENVIRONMENT_DEBUG:
        # draw debug info
        DrawText("Handling: " + str(round(RaceManager().player_car.handling, 1)), screen, font, (20, 20))
        DrawText("Power: " + str(int(RaceManager().player_car.power)), screen, font, (20, 60))
        DrawText("Traction: " + str(RaceManager().player_car.traction), screen, font, (20, 100))
        DrawText("Mass: " + str(RaceManager().player_car.body.mass), screen, font, (20, 140))
        DrawText("Speed: " + str(int(RaceManager().player_car.body.velocity.length)), screen, font, (20, 180))
        RaceManager().agents[0].DebugDrawRays(screen, RaceManager().camera)
        RaceManager().agents[0].DebugDrawInfo(screen, font)
        RaceManager().DebugDrawInfo(screen, font, RaceManager().cars)
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
