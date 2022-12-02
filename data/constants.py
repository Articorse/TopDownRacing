import math

from pygame import Vector2

# game
SCREEN_SIZE = Vector2(1920, 1080)
FPS = 60
CAMERA_MOVEMENT_SPEED = 0.93
CAMERA_OFFSET_MODIFIER = 2
INT_MAX_VALUE = 9999999999

# race
RACE_COUNTDOWN = 4
AI_COUNT = 4
PLACEMENT_UPDATE_TIMER = 250

# track
CAR_START_SEPARATION = Vector2(-26, -56)
CAR_START_OFFSET = Vector2(-4, 27)
DEFAULT_LAPS = 3
UP_ANGLE = math.pi * 1.5
RIGHT_ANGLE = 0
DOWN_ANGLE = math.pi / 2
LEFT_ANGLE = math.pi

# cars
MIN_SPEED = 3
GLOBAL_LINEAR_DRAG = 0.99
GLOBAL_DRIFT_DRAG = 0.96
GLOBAL_ANGULAR_DRAG = 0.9
CAR_STUN_MIN_IMPULSE = 500
CAR_STUN_DURATION = 0.2
CAR_SIZE_BUFFER = 10
CAR_SCALE = 3

# inputs
JOYSTICK_DEADZONE = 0.2
INPUT_FORWARD = "forward"
INPUT_RIGHT = "right"
INPUT_HANDBRAKE = "handbrake"
INPUT_QUIT = "quit"
INPUT_DEBUG_TOGGLE = "debug toggle"

# physics
PHYSICS_FPS = 60

# collision types
COLLTYPE_CAR = 0
COLLTYPE_TRACK = 1
COLLTYPE_CHECKPOINT = 2
COLLTYPE_AGENT_SQ = 3
COLLTYPE_LEFT_TURN_COLLIDER = 4
COLLTYPE_RIGHT_TURN_COLLIDER = 5
COLLTYPE_TURN_AUX_COLLIDER = 6

# shape filters
SF_WALL = 0b0001
SF_CAR = 0b0010
SF_CAR_INACTIVE = 0b0100
SF_CHECKPOINT = 0b1000

# ai
AI_RAY_LENGTH = 100
AI_SIDE_RAY_COUNT = 5
AI_RAY_ANGLE = 0.3
AI_RAY_DROPOFF = 15
AI_ANGLE_TO_GUIDEPOINT = 140
AI_ON = True
AI_PLAYER_ON = False
AI_GUIDEPOINT_VISUALIZATION_LENGTH = 300
AI_TURN_COLLIDER_RADIUS_MODIFIER = 350
AI_TURN_COLLIDER_OFFSET_MODIFIER = 330
AI_SQUARE_COLLIDER_OFFSET = 1.8
