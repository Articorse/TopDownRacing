import random
import time
import pygame
import pymunk
from enum import Enum
from pygame.font import Font
from pymunk import Vec2d
from data.constants import *
from data.enums import Direction
from data.files import *
from entities.car import Car
from entities.singleton import Singleton
from managers.raceselectionmanager import RaceSelectionManager
from utils.timerutils import FormatTime
from utils.uiutils import DrawText, Button, ImageAlign, DrawImage
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager


class State(Enum):
    Main_Menu = 0
    Selection_Screen = 1
    In_Race = 2


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
                    RaceManager().player_car.car_model.handling -= 0.1
                elif event.key == pygame.K_RIGHTBRACKET:
                    RaceManager().player_car.car_model.handling += 0.1
                elif event.key == pygame.K_o:
                    RaceManager().player_car.car_model.power -= 50
                elif event.key == pygame.K_p:
                    RaceManager().player_car.car_model.power += 50
                elif event.key == pygame.K_u:
                    RaceManager().player_car.car_model.traction -= 10
                elif event.key == pygame.K_i:
                    RaceManager().player_car.car_model.traction += 10
                elif event.key == pygame.K_k:
                    RaceManager().player_car.body.mass -= 0.1
                    RaceManager().player_car.body.center_of_gravity = (-RaceManager().player_car.car_model.size[0] * 0.4, 0)
                elif event.key == pygame.K_l:
                    RaceManager().player_car.body.mass += 0.1
                    RaceManager().player_car.body.center_of_gravity = (-RaceManager().player_car.car_model.size[0] * 0.4, 0)
                elif event.key == pygame.K_m:
                    RaceManager().agents[0].is_enabled = not RaceManager().agents[0].is_enabled
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            RaceManager().camera = Vector2(RaceManager().camera.x + 20, RaceManager().camera.y)
        if pressed_keys[pygame.K_UP]:
            RaceManager().camera = Vector2(RaceManager().camera.x, RaceManager().camera.y + 20)
        if pressed_keys[pygame.K_RIGHT]:
            RaceManager().camera = Vector2(RaceManager().camera.x - 20, RaceManager().camera.y)
        if pressed_keys[pygame.K_DOWN]:
            RaceManager().camera = Vector2(RaceManager().camera.x, RaceManager().camera.y - 20)
        if RaceManager().camera.x < -RaceManager().track.size.x + SCREEN_SIZE.x:
            RaceManager().camera.x = -RaceManager().track.size.x + SCREEN_SIZE.x
        if RaceManager().camera.x > 0:
            RaceManager().camera.x = 0
        if RaceManager().camera.y < -RaceManager().track.size.y + SCREEN_SIZE.y:
            RaceManager().camera.y = -RaceManager().track.size.y + SCREEN_SIZE.y
        if RaceManager().camera.y > 0:
            RaceManager().camera.y = 0
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
    if RaceManager().background:
        screen.blit(RaceManager().background, RaceManager().camera)
    # DEBUG START
    if ENVIRONMENT_DEBUG:
        RaceManager().pymunk_screen.fill((12, 12, 12))
        RaceManager().space.debug_draw(RaceManager().draw_options)
    # DEBUG END

    screen.blit(RaceManager().pymunk_screen, RaceManager().camera)
    RaceManager().sprites.update(events)
    for s in RaceManager().sprites:
        screen.blit(s.image, s.rect.move(*RaceManager().camera))
    if not RaceManager().is_started:
        DrawText(str(int(RaceManager().countdown_time)), screen, font, SCREEN_SIZE / 2, ImageAlign.CENTER, 5)

    # DEBUG START
    if ENVIRONMENT_DEBUG:
        # draw debug info
        pc = RaceManager().player_car
        DrawText("Handling: " + str(round(pc.car_model.handling, 1)), screen, font, (20, 20))
        DrawText("Power: " + str(int(pc.car_model.power)), screen, font, (20, 60))
        DrawText("Traction: " + str(pc.car_model.traction), screen, font, (20, 100))
        DrawText("Mass: " + str(pc.body.mass), screen, font, (20, 140))
        DrawText("Speed: " + str(int(pc.body.velocity.length)), screen, font, (20, 180))
        for car in RaceManager().cars:
            if car.agent:
                car_offset = car.body.position + RaceManager().camera
                rx = 50
                ry = 50
                sx = 20
                sy = 20
                red = (255, 0, 0)
                green = (0, 255, 0)
                rect_lf = pygame.Rect((rx, -ry) + car_offset, (sx, sy))
                rect_lf.center = (Vec2d(rect_lf.center[0], rect_lf.center[1]) - car_offset).rotated(
                    car.body.angle) + car_offset
                rect_rf = pygame.Rect((rx, ry) + car_offset, (sx, sy))
                rect_rf.center = (Vec2d(rect_rf.center[0], rect_rf.center[1]) - car_offset).rotated(
                    car.body.angle) + car_offset
                rect_lb = pygame.Rect((-rx, -ry) + car_offset, (sx, sy))
                rect_lb.center = (Vec2d(rect_lb.center[0], rect_lb.center[1]) - car_offset).rotated(
                    car.body.angle) + car_offset
                rect_rb = pygame.Rect((-rx, ry) + car_offset, (sx, sy))
                rect_rb.center = (Vec2d(rect_rb.center[0], rect_rb.center[1]) - car_offset).rotated(
                    car.body.angle) + car_offset
                if car.agent.left_front_collision[0]:
                    color_lf = red
                else:
                    color_lf = green
                if car.agent.right_front_collision[0]:
                    color_rf = red
                else:
                    color_rf = green
                if car.agent.left_back_collision[0]:
                    color_lb = red
                else:
                    color_lb = green
                if car.agent.right_back_collision[0]:
                    color_rb = red
                else:
                    color_rb = green
                pygame.draw.rect(screen, color_lf, rect_lf)
                pygame.draw.rect(screen, color_rf, rect_rf)
                pygame.draw.rect(screen, color_lb, rect_lb)
                pygame.draw.rect(screen, color_rb, rect_rb)
        if RaceManager().is_started:
            DrawText(FormatTime(RaceManager().GetTime()), screen, font, (SCREEN_SIZE.x / 2, 20), ImageAlign.CENTER)
        else:
            DrawText(FormatTime(0), screen, font, (SCREEN_SIZE.x / 2, 20), ImageAlign.CENTER)
        for agent in RaceManager().agents:
            agent.DebugDrawRays(screen, RaceManager().camera)
        RaceManager().agents[0].DebugDrawInfo(screen, font)
    # DEBUG END
    if not RaceManager().is_over:
        RaceManager().DebugDrawInfo(screen, font, RaceManager().player_car)
    else:
        if list(RaceManager().final_lineup.keys())[0] == RaceManager().player_car:
            win_pos = SCREEN_SIZE / 2
            DrawText("You Win!", screen, font, win_pos, ImageAlign.CENTER)
            DrawText("Press Escape", screen, font, (win_pos.x, win_pos.y + 30), ImageAlign.CENTER)
        else:
            lose_pos = SCREEN_SIZE / 2
            DrawText("You Lose!", screen, font, lose_pos, ImageAlign.CENTER)
            DrawText("Press Escape", screen, font, (lose_pos.x, lose_pos.y + 30), ImageAlign.CENTER)
        leaderboard_pos = (SCREEN_SIZE.x - 20, 20)
        for car, finish_time in RaceManager().final_lineup.items():
            DrawText(car.name + " " + FormatTime(finish_time), screen, font, leaderboard_pos, ImageAlign.TOP_RIGHT)
            leaderboard_pos = (leaderboard_pos[0], leaderboard_pos[1] + 40)

    # end draw step
    pygame.display.flip()
    clock.tick(FPS)


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
    car = RaceSelectionManager().GetCurrentCar()
    track = RaceSelectionManager().GetCurrentTrack()
    DrawImage(car.sprite_path, screen, car_image_pos, scale=1)
    DrawImage(track.thumbnail_path, screen, track_image_pos, align=ImageAlign.TOP_RIGHT, scale=1)
    DrawText(car.model_name, screen, font, (car_image_pos[0], car_image_pos[1] + 500))
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
        pc = Car("Player", RaceSelectionManager().GetCurrentCar())
        cars = [pc]
        for i in range(RaceSelectionManager().ai_count):
            cars.append(
                Car("AI " + str(i),
                    RaceSelectionManager().available_cars[random.randint(0,
                                                          len(RaceSelectionManager().available_cars) - 1)]))
        RaceManager().Setup(
            RaceSelectionManager().GetCurrentTrack(), pc, RaceSelectionManager().current_lap_count, *cars)
        pc.agent.is_enabled = AI_PLAYER_ON
        for car in RaceManager().cars:
            car.Update()
        RaceSelectionManager().Free()
        GameManager().SetState(State.In_Race)
        return

    # handle inputs
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
    inputs = InputManager().get_inputs(events)
    if inputs["quit"]:
        GameManager().SetState(State.Main_Menu)
        return

    pygame.display.flip()
    clock.tick(FPS)


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
            if state == State.Selection_Screen:
                self._state = state
        if self._state == State.Selection_Screen:
            if state == State.Main_Menu:
                self._state = state
            if state == State.In_Race:
                self._state = state
        if self._state == State.In_Race:
            if state == State.Main_Menu:
                RaceManager().Free()
                self._state = state
            if state == State.Selection_Screen:
                return
