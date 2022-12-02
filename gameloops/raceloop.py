import sys
import time
import pygame
import pymunk
from pygame.font import Font
from pygame.math import Vector2
from pymunk import Vec2d
from data import globalvars
from data.constants import RACE_COUNTDOWN, SCREEN_SIZE, CAMERA_MOVEMENT_SPEED, JOYSTICK_DEADZONE, \
    PHYSICS_FPS, FPS, INPUT_QUIT, INPUT_HANDBRAKE, INPUT_FORWARD, INPUT_RIGHT, CAMERA_OFFSET_MODIFIER
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from managers.racemanager import RaceManager
from utils.timerutils import FormatTime
from utils.uiutils import ImageAlign, DrawText, DrawSprite


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
        if inputs[INPUT_QUIT]:
            GameManager().SetState(State.Main_Menu)
            return
        RaceManager().countdown_time = RACE_COUNTDOWN - (time.perf_counter() - RaceManager().start_time)

    # race start
    if not RaceManager().is_started and RaceManager().countdown_time <= 1:
        RaceManager().StartRace()

    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
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
    RaceManager().camera = CenterCamera(RaceManager().camera,
                                        RaceManager().player_car.body.position +
                                        RaceManager().player_car.body.velocity / CAMERA_OFFSET_MODIFIER)

    if RaceManager().is_started:
        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs[INPUT_QUIT]:
            GameManager().SetState(State.Main_Menu)
            return
        if not RaceManager().player_car.has_finished:
            RaceManager().player_car.handbrake = inputs[INPUT_HANDBRAKE]
            if inputs[INPUT_FORWARD].__abs__() > JOYSTICK_DEADZONE:
                RaceManager().player_car.Accelerate(inputs[INPUT_FORWARD])
            if inputs[INPUT_RIGHT].__abs__() > JOYSTICK_DEADZONE:
                RaceManager().player_car.Steer(inputs[INPUT_RIGHT])

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
        DrawSprite(RaceManager().background, screen, RaceManager().camera)
    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
        RaceManager().pymunk_screen.fill((12, 12, 12))
        RaceManager().space.debug_draw(RaceManager().draw_options)
        screen.blit(RaceManager().pymunk_screen, RaceManager().camera)
    # DEBUG END

    RaceManager().sprites.update(events)
    for s in RaceManager().sprites:
        screen.blit(s.image, s.rect.move(*RaceManager().camera))
    if not RaceManager().is_started:
        DrawText(str(int(RaceManager().countdown_time)), screen, font, SCREEN_SIZE / 2, ImageAlign.CENTER, 5)

    if RaceManager().foreground:
        DrawSprite(RaceManager().foreground, screen, RaceManager().camera)

    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
        # draw debug info
        pc = RaceManager().player_car
        DrawText("Handling: " + str(round(pc.car_model.handling, 1)), screen, font, (20, 20))
        DrawText("Power: " + str(int(pc.car_model.power)), screen, font, (20, 60))
        DrawText("Traction: " + str(pc.car_model.traction), screen, font, (20, 100))
        DrawText("Mass: " + str(pc.body.mass), screen, font, (20, 140))
        DrawText("Speed: " + str(int(pc.body.velocity.length)), screen, font, (20, 180))
        DrawText("State: " + str(pc.agent.state), screen, font, (20, 260))
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
        for agent in RaceManager().agents:
            agent.DebugDrawRays(screen, RaceManager().camera)
        RaceManager().agents[0].DebugDrawInfo(screen, font)
    # DEBUG END

    if RaceManager().is_started:
        DrawText(FormatTime(RaceManager().GetTime()), screen, font, (SCREEN_SIZE.x / 2, 20), ImageAlign.CENTER)
        placement = RaceManager().GetPlayerPlacement(pygame.time.get_ticks() - globalvars.LAST_FRAME_TIME)
        DrawText(f"{placement[0]}/{placement[1]}", screen, font, (SCREEN_SIZE.x / 2, 60), ImageAlign.CENTER)
    else:
        DrawText(FormatTime(0), screen, font, (SCREEN_SIZE.x / 2, 20), ImageAlign.CENTER)

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

    # update last frame time
    globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

    # end draw step
    pygame.display.flip()
    clock.tick(FPS)
