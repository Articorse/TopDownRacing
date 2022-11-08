import pymunk.pygame_util
import random
from pygame import Vector2
from data.enums import Direction
from data.files import *
from entities.car import Car
from managers.inputmanager import InputHelper
from callbacks.collisionhandlers import *


def main():
    # pygame initialization
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    # pymunk initialization
    space = pymunk.Space()
    pymunk_screen = pygame.Surface(MAP_SIZE)
    pymunk_screen.set_colorkey((12, 12, 12))
    pymunk_screen.fill((12, 12, 12))
    draw_options = pymunk.pygame_util.DrawOptions(pymunk_screen)
    collision_handler = space.add_collision_handler(COLLTYPE_CAR, COLLTYPE_TRACK)
    collision_handler.post_solve = car_track_collision_callback

    # input initialization
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    input_helper = InputHelper(joystick)

    # camera setup
    camera = pygame.Vector2((0, 0))

    # add cars
    p_sprite = pygame.sprite.Sprite()
    p_sprite.image = pygame.image.load(IMAGE_CAR)
    p_sprite.image = pygame.transform.scale(p_sprite.image, (60, 40))
    p = Car(1, 500, 5, 300, (50, 30), (200, 200), 0, color=(30, 30, 30, 0), angle=0, sprite=p_sprite)
    space.add(p.body, p.shape)
    cars.append(p)

    # add track colliders
    track = pymunk.Body(body_type=pymunk.Body.STATIC)
    track.position = (0, 0)
    track_points = []
    track_segments = [pymunk.Segment(track, (0, 0),
                                     (MAP_SIZE.x, 0), 5),
                      pymunk.Segment(track, (MAP_SIZE.x, 0),
                                     tuple(MAP_SIZE), 5),
                      pymunk.Segment(track, tuple(MAP_SIZE),
                                     (0, MAP_SIZE.y), 5),
                      pymunk.Segment(track, (0, MAP_SIZE.y),
                                     (0, 0), 5),
                      pymunk.Segment(track, (0, MAP_SIZE.y / 3),
                                     (MAP_SIZE.x * 2 / 3, MAP_SIZE.y / 3), 5),
                      pymunk.Segment(track, (MAP_SIZE.x / 3, MAP_SIZE.y * 2 / 3),
                                     (MAP_SIZE.x, MAP_SIZE.y * 2 / 3), 5)]
    for seg in track_segments:
        seg.friction = 1
        seg.elasticity = 1
        seg.collision_type = COLLTYPE_TRACK
    space.add(
        track,
        track_segments[0],
        track_segments[1],
        track_segments[2],
        track_segments[3],
        track_segments[4],
        track_segments[5])

    # add sprites to group
    sprites = pygame.sprite.Group()
    sprites.add(p.sprite)

    # DEBUG START
    # setup trail
    line_draw_timer = FPS / 30
    line_draw_points = [p.body.position]
    # setup background
    background = pygame.Surface(MAP_SIZE)
    background.fill((30, 30, 30))
    for _ in range(2000):
        bg_x, bg_y = random.randint(0, MAP_SIZE.x), random.randint(0, MAP_SIZE.y)
        pygame.draw.rect(background, pygame.Color('gray'), (bg_x, bg_y, 2, 2))
    # setup debug info
    font = pygame.font.Font(FONT_ARIAL, 32)
    handling_text = font.render("Handling: " + str(p.handling), True, (255, 255, 255))
    power_text = font.render("Power: " + str(p.power), True, (255, 255, 255))
    traction_text = font.render("Traction: " + str(p.traction), True, (255, 255, 255))
    mass_text = font.render("Mass: " + str(p.body.mass), True, (255, 255, 255))
    velocity_text = font.render("Speed: " + str(p.body.velocity.length), True, (255, 255, 255))
    handling_text_rect = handling_text.get_rect()
    power_text_rect = power_text.get_rect()
    mass_text_rect = mass_text.get_rect()
    traction_text_rect = traction_text.get_rect()
    velocity_text_rect = velocity_text.get_rect()
    handling_text_rect.topleft = (20, 20)
    power_text_rect.topleft = (20, 60)
    traction_text_rect.topleft = (20, 100)
    mass_text_rect.topleft = (20, 140)
    velocity_text_rect.topleft = (20, 180)
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
                    p.handling -= 0.1
                elif event.key == pygame.K_RIGHTBRACKET:
                    p.handling += 0.1
                elif event.key == pygame.K_o:
                    p.power -= 50
                elif event.key == pygame.K_p:
                    p.power += 50
                elif event.key == pygame.K_u:
                    p.traction -= 10
                elif event.key == pygame.K_i:
                    p.traction += 10
                elif event.key == pygame.K_k:
                    p.body.mass -= 0.1
                    p.body.center_of_gravity = (-p.size[0] * 0.4, 0)
                elif event.key == pygame.K_l:
                    p.body.mass += 0.1
                    p.body.center_of_gravity = (-p.size[0] * 0.4, 0)
        # camera follow player
        camera = Vector2(-p.body.position.x, -p.body.position.y) + SCREEN_SIZE / 2
        # camera clamp to map size
        if camera.x < -MAP_SIZE.x + SCREEN_SIZE.x:
            camera.x = -MAP_SIZE.x + SCREEN_SIZE.x
        if camera.x > 0:
            camera.x = 0
        if camera.y < -MAP_SIZE.y + SCREEN_SIZE.y:
            camera.y = -MAP_SIZE.y + SCREEN_SIZE.y
        if camera.y > 0:
            camera.y = 0
        # DEBUG END

        # handle inputs
        inputs = input_helper.get_inputs(events)
        if inputs["quit"]:
            pygame.quit()
            sys.exit()
        p.handbrake = inputs["handbrake"]
        if inputs["forward"].__abs__() > JOYSTICK_DEADZONE:
            p.move(Direction.Forward, inputs["forward"])
        if inputs["right"].__abs__() > JOYSTICK_DEADZONE:
            p.move(Direction.Right, inputs["right"])

        # reindex shapes after rotating
        space.reindex_shapes_for_body(p.body)

        # DEBUG START
        # populate Trail
        if line_draw_timer == 0:
            line_draw_timer = FPS / 30
        if line_draw_timer == FPS / 30:
            line_draw_points.append(p.body.position)
            if len(line_draw_points) > 200:
                line_draw_points.pop(0)
        line_draw_timer -= 1
        # DEBUG END

        # car mechanics
        for car in cars:
            car.update()

        # physics step
        space.step(1 / FPS)

        # start draw step
        screen.blit(background, camera)
        # pygame.draw.lines(screen, (255, 0, 0), False, line_draw_points)
        pymunk_screen.fill((12, 12, 12))
        space.debug_draw(draw_options)
        screen.blit(pymunk_screen, camera)
        sprites.update(events)
        for s in sprites:
            screen.blit(s.image, s.rect.move(*camera))

        # DEBUG START
        # draw debug info
        handling_text = font.render("Handling: " + str(round(p.handling, 1)), True, (255, 255, 255))
        power_text = font.render("Power: " + str(int(p.power)), True, (255, 255, 255))
        traction_text = font.render("Traction: " + str(p.traction), True, (255, 255, 255))
        mass_text = font.render("Mass: " + str(p.body.mass), True, (255, 255, 255))
        velocity_text = font.render("Speed: " + str(int(p.body.velocity.length)), True, (255, 255, 255))
        screen.blit(handling_text, handling_text_rect)
        screen.blit(power_text, power_text_rect)
        screen.blit(traction_text, traction_text_rect)
        screen.blit(mass_text, mass_text_rect)
        screen.blit(velocity_text, velocity_text_rect)
        # DEBUG END

        # end draw step
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    sys.exit(main())
