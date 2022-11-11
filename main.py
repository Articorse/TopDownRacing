import json
import pygame.draw_py
import pymunk.pygame_util
import random
from pygame import Vector2
from data.enums import Direction
from data.files import *
from helpers.timerhelper import FormatTime
from managers.inputmanager import InputManager
from callbacks.collisionhandlers import *
from managers.racemanager import RaceManager


def main():
    # pygame initialization
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_ARIAL, 32)

    # pymunk initialization
    space = pymunk.Space()
    space.collision_bias = 0
    space.iterations = 30
    pymunk_screen = pygame.Surface(MAP_SIZE)
    pymunk_screen.set_colorkey((12, 12, 12))
    pymunk_screen.fill((12, 12, 12))
    draw_options = pymunk.pygame_util.DrawOptions(pymunk_screen)
    collision_handler = space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_TRACK)
    collision_handler.post_solve = car_track_collision_callback
    checkpoint_handler = space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_GUIDEPOINT)
    checkpoint_handler.begin = checkpoint_reached_callback

    # input initialization
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        InputManager().joystick = joystick

    # load track
    RaceManager().SetTrack(json.load(open(TRACKS_2)), space)

    # add cars
    RaceManager().AddCars([
        ("Player", json.load((open(CAR_1)))),
        ("AI 1", json.load((open(CAR_2)))),
        ("AI 2", json.load((open(CAR_2)))),
        ("AI 3", json.load((open(CAR_2))))],
        space)
    player_car = RaceManager().cars[0]

    # camera initialization
    camera = Vector2(-player_car.body.position.x, -player_car.body.position.y) + SCREEN_SIZE / 2

    # add sprites to group
    sprites = pygame.sprite.Group()
    for car in RaceManager().cars:
        sprites.add(car.sprite)

    # DEBUG START
    # setup background
    background = pygame.Surface(MAP_SIZE)
    background.fill((30, 30, 30))
    for _ in range(2000):
        bg_x, bg_y = random.randint(0, MAP_SIZE.x), random.randint(0, MAP_SIZE.y)
        pygame.draw.rect(background, pygame.Color('gray'), (bg_x, bg_y, 2, 2))
    # setup debug info
    handling_text = font.render("Handling: " + str(player_car.handling), True, (255, 255, 255))
    power_text = font.render("Power: " + str(player_car.power), True, (255, 255, 255))
    traction_text = font.render("Traction: " + str(player_car.traction), True, (255, 255, 255))
    mass_text = font.render("Mass: " + str(player_car.body.mass), True, (255, 255, 255))
    velocity_text = font.render("Speed: " + str(player_car.body.velocity.length), True, (255, 255, 255))
    timer_text = font.render(str(int(RaceManager().current_time)), True, (255, 255, 255))
    handling_text_rect = handling_text.get_rect()
    power_text_rect = power_text.get_rect()
    mass_text_rect = mass_text.get_rect()
    traction_text_rect = traction_text.get_rect()
    velocity_text_rect = velocity_text.get_rect()
    timer_text_rect = timer_text.get_rect()
    handling_text_rect.topleft = (20, 20)
    power_text_rect.topleft = (20, 60)
    traction_text_rect.topleft = (20, 100)
    mass_text_rect.topleft = (20, 140)
    velocity_text_rect.topleft = (20, 180)
    timer_text_rect.center = (SCREEN_SIZE.x / 2, 30)
    # DEBUG END

    # game loop
    while True:
        # handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit(0)

        # DEBUG START
        # modify player car stats
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    player_car.handling -= 0.1
                elif event.key == pygame.K_RIGHTBRACKET:
                    player_car.handling += 0.1
                elif event.key == pygame.K_o:
                    player_car.power -= 50
                elif event.key == pygame.K_p:
                    player_car.power += 50
                elif event.key == pygame.K_u:
                    player_car.traction -= 10
                elif event.key == pygame.K_i:
                    player_car.traction += 10
                elif event.key == pygame.K_k:
                    player_car.body.mass -= 0.1
                    player_car.body.center_of_gravity = (-player_car.size[0] * 0.4, 0)
                elif event.key == pygame.K_l:
                    player_car.body.mass += 0.1
                    player_car.body.center_of_gravity = (-player_car.size[0] * 0.4, 0)
                elif event.key == pygame.K_m:
                    RaceManager().agents[0].is_enabled = not RaceManager().agents[0].is_enabled
        # DEBUG END

        # camera follow player & clamp to map size
        camera_target_pos = Vector2(
            -player_car.body.position.x,
            -player_car.body.position.y) + SCREEN_SIZE / 2
        camera = camera_target_pos + (camera - camera_target_pos) * CAMERA_MOVEMENT_SPEED
        if camera.x < -MAP_SIZE.x + SCREEN_SIZE.x:
            camera.x = -MAP_SIZE.x + SCREEN_SIZE.x
        if camera.x > 0:
            camera.x = 0
        if camera.y < -MAP_SIZE.y + SCREEN_SIZE.y:
            camera.y = -MAP_SIZE.y + SCREEN_SIZE.y
        if camera.y > 0:
            camera.y = 0

        # handle inputs
        inputs = InputManager().get_inputs(events)
        if inputs["quit"]:
            pygame.quit()
            sys.exit()
        player_car.handbrake = inputs["handbrake"]
        if inputs["forward"].__abs__() > JOYSTICK_DEADZONE:
            player_car.Move(Direction.Forward, inputs["forward"])
        if inputs["right"].__abs__() > JOYSTICK_DEADZONE:
            player_car.Move(Direction.Right, inputs["right"])

        # reindex shapes after rotating
        for car in RaceManager().cars:
            space.reindex_shapes_for_body(car.body)

        # car update
        for car in RaceManager().cars:
            car.Update()
        for agent in RaceManager().agents:
            agent.Update()

        # physics step
        space.step(1 / PHYSICS_FPS)

        # start draw step
        screen.blit(background, camera)
        pymunk_screen.fill((12, 12, 12))
        space.debug_draw(draw_options)
        screen.blit(pymunk_screen, camera)
        sprites.update(events)
        for s in sprites:
            screen.blit(s.image, s.rect.move(*camera))

        # DEBUG START
        # draw debug info
        handling_text = font.render(
            "Handling: " + str(round(player_car.handling, 1)), True, (255, 255, 255))
        power_text = font.render(
            "Power: " + str(int(player_car.power)), True, (255, 255, 255))
        traction_text = font.render(
            "Traction: " + str(player_car.traction), True, (255, 255, 255))
        mass_text = font.render(
            "Mass: " + str(player_car.body.mass), True, (255, 255, 255))
        velocity_text = font.render(
            "Speed: " + str(int(player_car.body.velocity.length)), True, (255, 255, 255))
        timer_text = font.render(FormatTime(RaceManager().current_time), True, (255, 255, 255))
        screen.blit(handling_text, handling_text_rect)
        screen.blit(power_text, power_text_rect)
        screen.blit(traction_text, traction_text_rect)
        screen.blit(mass_text, mass_text_rect)
        screen.blit(velocity_text, velocity_text_rect)
        screen.blit(timer_text, timer_text_rect)
        RaceManager().agents[0].DebugDrawRays(screen, camera)
        RaceManager().agents[0].DebugDrawInfo(screen, font)
        RaceManager().DebugDrawInfo(screen, font, RaceManager().cars)
        # DEBUG END

        # end draw step
        pygame.display.flip()
        RaceManager().current_time += clock.tick(FPS)


if __name__ == "__main__":
    sys.exit(main())
