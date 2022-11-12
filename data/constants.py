from pygame import Vector2

# game
SCREEN_SIZE = Vector2(1920, 1080)
FPS = 60
CAMERA_MOVEMENT_SPEED = 0.93
ENVIRONMENT_DEBUG = True

# track
CAR_SEPARATION = Vector2(-70, 70)

# cars
MIN_SPEED = 3
GLOBAL_LINEAR_DRAG = 0.99
GLOBAL_ANGULAR_DRAG = 0.9
CAR_STUN_MIN_IMPULSE = 500
CAR_STUN_DURATION = 1

# inputs
JOYSTICK_DEADZONE = 0.2
INPUT_FORWARD = "forward"
INPUT_RIGHT = "right"
INPUT_HANDBRAKE = "handbrake"
INPUT_QUIT = "quit"
INPUT_EXIT_RACE = "exit race"

# physics
PHYSICS_FPS = 60

# collision types
COLLTYPE_CAR = 0
COLLTYPE_TRACK = 1
COLLTYPE_GUIDEPOINT = 2

# shape filters
SF_WALL = 0b010
SF_CAR = 0b001
SF_GUIDEPOINT = 0b100

# ai
AI_RAY_LENGTH = 300
AI_SIDE_RAY_COUNT = 5
AI_RAY_ANGLE = 0.2
AI_RAY_DROPOFF = 40

# debug
MAP_SIZE = SCREEN_SIZE * 2
