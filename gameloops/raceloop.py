import sys
import pygame
from pygame.font import Font
from pygame.math import Vector2
from pymunk import Vec2d
from data import globalvars
from data.constants import JOYSTICK_DEADZONE, \
    PHYSICS_FPS, FPS, INPUT_QUIT, INPUT_HANDBRAKE, INPUT_FORWARD, INPUT_RIGHT, CAMERA_OFFSET_MODIFIER, RESOLUTIONS, \
    FPS_UPDATE_TIMER_DEFAULT, PHYSICS_SCREEN_SCALE, AUDIO_ENGINE_NOISE_TIMER, AUDIO_COUNTDOWN, \
    AUDIO_RACE_START, PLACEMENT_UPDATE_TIMER
from data.globalvars import CURRENT_RESOLUTION
from managers.audiomanager import AudioManager
from managers.gamemanager import GameManager, State
from managers.inputmanager import InputManager
from utils.camerautils import CenterCamera
from utils.timerutils import FormatTime, WaitTimer
from utils.uiutils import ImageAlign, DrawText, DrawSprite


def ExitRace():
    globalvars.RACE_MANAGER.Reset()
    globalvars.RACE_MANAGER = None
    GameManager().SetState(State.Main_Menu)


def RaceLoop(font: Font, clock: pygame.time.Clock):
    screen_size = RESOLUTIONS[CURRENT_RESOLUTION][0]

    # handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)

    # countdown
    if not globalvars.RACE_MANAGER.is_started:
        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs[INPUT_QUIT]:
            ExitRace()
            return
        if WaitTimer("Race Start Countdown", 1000, clock):
            globalvars.RACE_MANAGER.countdown_time -= 1
            if globalvars.RACE_MANAGER.countdown_time == 0:
                AudioManager().Play_Sound(AUDIO_RACE_START)
            else:
                AudioManager().Play_Sound(AUDIO_COUNTDOWN)

    # race start
    if not globalvars.RACE_MANAGER.is_started and globalvars.RACE_MANAGER.countdown_time <= 0:
        globalvars.RACE_MANAGER.StartRace()

    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
        # modify player car stats
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    globalvars.RACE_MANAGER.player_car.car_model.handling -= 0.1
                elif event.key == pygame.K_RIGHTBRACKET:
                    globalvars.RACE_MANAGER.player_car.car_model.handling += 0.1
                elif event.key == pygame.K_o:
                    globalvars.RACE_MANAGER.player_car.car_model.power -= 50
                elif event.key == pygame.K_p:
                    globalvars.RACE_MANAGER.player_car.car_model.power += 50
                elif event.key == pygame.K_u:
                    globalvars.RACE_MANAGER.player_car.car_model.traction -= 10
                elif event.key == pygame.K_i:
                    globalvars.RACE_MANAGER.player_car.car_model.traction += 10
                elif event.key == pygame.K_k:
                    globalvars.RACE_MANAGER.player_car.body.mass -= 0.1
                    globalvars.RACE_MANAGER.player_car.body.center_of_gravity = \
                        (-globalvars.RACE_MANAGER.player_car.car_model.size[0] * 0.4, 0)
                elif event.key == pygame.K_l:
                    globalvars.RACE_MANAGER.player_car.body.mass += 0.1
                    globalvars.RACE_MANAGER.player_car.body.center_of_gravity = \
                        (-globalvars.RACE_MANAGER.player_car.car_model.size[0] * 0.4, 0)
                elif event.key == pygame.K_m:
                    globalvars.RACE_MANAGER.agents[0].is_enabled = not globalvars.RACE_MANAGER.agents[0].is_enabled
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            globalvars.RACE_MANAGER.camera = Vector2(
                globalvars.RACE_MANAGER.camera.x + 20, globalvars.RACE_MANAGER.camera.y)
        if pressed_keys[pygame.K_UP]:
            globalvars.RACE_MANAGER.camera = Vector2(
                globalvars.RACE_MANAGER.camera.x, globalvars.RACE_MANAGER.camera.y + 20)
        if pressed_keys[pygame.K_RIGHT]:
            globalvars.RACE_MANAGER.camera = Vector2(
                globalvars.RACE_MANAGER.camera.x - 20, globalvars.RACE_MANAGER.camera.y)
        if pressed_keys[pygame.K_DOWN]:
            globalvars.RACE_MANAGER.camera = Vector2(
                globalvars.RACE_MANAGER.camera.x, globalvars.RACE_MANAGER.camera.y - 20)
        if globalvars.RACE_MANAGER.camera.x < -globalvars.RACE_MANAGER.track.size.x + screen_size.x:
            globalvars.RACE_MANAGER.camera.x = -globalvars.RACE_MANAGER.track.size.x + screen_size.x
        if globalvars.RACE_MANAGER.camera.x > 0:
            globalvars.RACE_MANAGER.camera.x = 0
        if globalvars.RACE_MANAGER.camera.y < -globalvars.RACE_MANAGER.track.size.y + screen_size.y:
            globalvars.RACE_MANAGER.camera.y = -globalvars.RACE_MANAGER.track.size.y + screen_size.y
        if globalvars.RACE_MANAGER.camera.y > 0:
            globalvars.RACE_MANAGER.camera.y = 0
    # DEBUG END

    # camera follow player & clamp to map size
    globalvars.RACE_MANAGER.camera = CenterCamera(globalvars.RACE_MANAGER.camera, globalvars.RACE_MANAGER,
                                                  globalvars.RACE_MANAGER.player_car.body.position *
                                                  RESOLUTIONS[CURRENT_RESOLUTION][1] / PHYSICS_SCREEN_SCALE +
                                                  globalvars.RACE_MANAGER.player_car.body.velocity /
                                                  CAMERA_OFFSET_MODIFIER)

    if globalvars.RACE_MANAGER.is_started:
        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs[INPUT_QUIT]:
            ExitRace()
            return
        if not globalvars.RACE_MANAGER.player_car.has_finished:
            globalvars.RACE_MANAGER.player_car.handbrake = inputs[INPUT_HANDBRAKE]
            if inputs[INPUT_FORWARD].__abs__() > JOYSTICK_DEADZONE:
                globalvars.RACE_MANAGER.player_car.Accelerate(inputs[INPUT_FORWARD])
            if inputs[INPUT_RIGHT].__abs__() > JOYSTICK_DEADZONE:
                globalvars.RACE_MANAGER.player_car.Steer(inputs[INPUT_RIGHT])

            # reindex shapes after rotating
            for car in globalvars.RACE_MANAGER.cars:
                globalvars.RACE_MANAGER.space.reindex_shapes_for_body(car.body)

    if globalvars.RACE_MANAGER.is_started:
        # car update
        for car in globalvars.RACE_MANAGER.cars:
            car.Update()
        # ai update
        for agent in globalvars.RACE_MANAGER.agents:
            agent.Update()

        # physics step
        globalvars.RACE_MANAGER.space.step(1 / PHYSICS_FPS)

    # start draw step
    if globalvars.RACE_MANAGER.background:
        DrawSprite(globalvars.RACE_MANAGER.background, globalvars.SCREEN, globalvars.RACE_MANAGER.camera)
    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
        globalvars.RACE_MANAGER.pymunk_screen.fill((12, 12, 12))
        globalvars.RACE_MANAGER.space.debug_draw(globalvars.RACE_MANAGER.draw_options)
        globalvars.SCREEN.blit(globalvars.RACE_MANAGER.pymunk_screen, globalvars.RACE_MANAGER.camera)
    # DEBUG END

    globalvars.RACE_MANAGER.sprites.update(events)
    for s in globalvars.RACE_MANAGER.sprites:
        globalvars.SCREEN.blit(s.image, s.rect.move(*globalvars.RACE_MANAGER.camera))
    if not globalvars.RACE_MANAGER.is_started:
        DrawText(str(int(globalvars.RACE_MANAGER.countdown_time)),
                 globalvars.SCREEN, font, screen_size / 2, ImageAlign.CENTER, 5)

    if globalvars.RACE_MANAGER.foreground:
        DrawSprite(globalvars.RACE_MANAGER.foreground, globalvars.SCREEN, globalvars.RACE_MANAGER.camera)

    # DEBUG START
    if globalvars.ENVIRONMENT_DEBUG:
        # draw debug info
        pc = globalvars.RACE_MANAGER.player_car
        DrawText("Handling: " + str(round(pc.car_model.handling, 1)), globalvars.SCREEN, font, (20, 20))
        DrawText("Power: " + str(int(pc.car_model.power)), globalvars.SCREEN, font, (20, 60))
        DrawText("Traction: " + str(pc.car_model.traction), globalvars.SCREEN, font, (20, 100))
        DrawText("Mass: " + str(pc.body.mass), globalvars.SCREEN, font, (20, 140))
        DrawText("Speed: " + str(int(pc.body.velocity.length)), globalvars.SCREEN, font, (20, 180))
        DrawText("State: " + str(pc.agent.state), globalvars.SCREEN, font, (20, 260))
        for car in globalvars.RACE_MANAGER.cars:
            if car.agent:
                car_offset = car.body.position + globalvars.RACE_MANAGER.camera
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
                pygame.draw.rect(globalvars.SCREEN, color_lf, rect_lf)
                pygame.draw.rect(globalvars.SCREEN, color_rf, rect_rf)
                pygame.draw.rect(globalvars.SCREEN, color_lb, rect_lb)
                pygame.draw.rect(globalvars.SCREEN, color_rb, rect_rb)
        for agent in globalvars.RACE_MANAGER.agents:
            agent.DebugDrawRays(globalvars.SCREEN, globalvars.RACE_MANAGER.camera)
        globalvars.RACE_MANAGER.agents[0].DebugDrawInfo(globalvars.SCREEN, font)
    # DEBUG END

    if globalvars.RACE_MANAGER.is_started:
        DrawText(FormatTime(globalvars.RACE_MANAGER.GetTime()),
                 globalvars.SCREEN, font, (screen_size.x / 2, 20), ImageAlign.CENTER)
        if WaitTimer("Player Placement Refresh Timer", PLACEMENT_UPDATE_TIMER, clock):
            globalvars.RACE_MANAGER.player_placement = globalvars.RACE_MANAGER.GetPlayerPlacement()
        DrawText(f"{globalvars.RACE_MANAGER.player_placement[0]}/{globalvars.RACE_MANAGER.player_placement[1]}",
                 globalvars.SCREEN, font, (screen_size.x / 2, 60), ImageAlign.CENTER)

        elapsed_ticks = pygame.time.get_ticks() - globalvars.LAST_FRAME_TIME
        fps_this_frame = round(1000 / elapsed_ticks)
        globalvars.RECENT_FPS_VALUES.append(fps_this_frame)
        if WaitTimer("FPS Display Refresh", FPS_UPDATE_TIMER_DEFAULT, clock):
            globalvars.CURRENT_FPS = sum(globalvars.RECENT_FPS_VALUES) / len(globalvars.RECENT_FPS_VALUES)
            globalvars.RECENT_FPS_VALUES.clear()
        DrawText(f"FPS: {int(globalvars.CURRENT_FPS)}", globalvars.SCREEN, font, (20, 20))
    else:
        DrawText(FormatTime(0), globalvars.SCREEN, font, (screen_size.x / 2, 20), ImageAlign.CENTER)

    # engine noise
    if WaitTimer("Engine Noise Delay", AUDIO_ENGINE_NOISE_TIMER, clock):
        AudioManager().Play_Engine_Noise(globalvars.RACE_MANAGER.player_car.body.velocity)

    if not globalvars.RACE_MANAGER.is_over:
        globalvars.RACE_MANAGER.DebugDrawInfo(globalvars.SCREEN, font, globalvars.RACE_MANAGER.player_car)
    else:
        if list(globalvars.RACE_MANAGER.final_lineup.keys())[0] == globalvars.RACE_MANAGER.player_car:
            win_pos = screen_size / 2
            DrawText("You Win!", globalvars.SCREEN, font, win_pos, ImageAlign.CENTER)
            DrawText("Press Escape", globalvars.SCREEN, font, (win_pos.x, win_pos.y + 30), ImageAlign.CENTER)
        else:
            lose_pos = screen_size / 2
            DrawText("You Lose!", globalvars.SCREEN, font, lose_pos, ImageAlign.CENTER)
            DrawText("Press Escape", globalvars.SCREEN, font, (lose_pos.x, lose_pos.y + 30), ImageAlign.CENTER)
        leaderboard_pos = (screen_size.x - 20, 20)
        for car, finish_time in globalvars.RACE_MANAGER.final_lineup.items():
            DrawText(car.name + " " + FormatTime(finish_time),
                     globalvars.SCREEN, font, leaderboard_pos, ImageAlign.TOP_RIGHT)
            leaderboard_pos = (leaderboard_pos[0], leaderboard_pos[1] + 40)

    # update last frame time
    globalvars.LAST_FRAME_TIME = pygame.time.get_ticks()

    # end draw step
    pygame.display.flip()
    clock.tick(FPS)
