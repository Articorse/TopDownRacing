import math

from pygame import Vector2

# game
RESOLUTIONS = [
    (Vector2(640, 360), 1),
    (Vector2(1280, 720), 2),
    (Vector2(1920, 1080), 3),
    (Vector2(2560, 1440), 4)
]
FPS = 60
FPS_UPDATE_TIMER_DEFAULT = 250
CAMERA_MOVEMENT_SPEED = 0.93
CAMERA_OFFSET_MODIFIER = 2
INT_MAX_VALUE = 9999999999
FONT_BASE_SIZE = 10

# race
RACE_COUNTDOWN = 3
AI_COUNT = 4
PLACEMENT_UPDATE_TIMER = 250
MAX_AI_COUNT = 8
MAX_LAP_COUNT = 9

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
CAR_SIZE_PADDING = 5

# inputs
JOYSTICK_DEADZONE = 0.2
INPUT_FORWARD = "forward"
INPUT_RIGHT = "right"
INPUT_HANDBRAKE = "handbrake"
INPUT_QUIT = "quit"
INPUT_DEBUG_TOGGLE = "debug toggle"

# physics
PHYSICS_FPS = 60
PHYSICS_SCREEN_SCALE = 3

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

# audio settings
AUDIO_MIN_SQUARED_DISTANCE = 8000
AUDIO_MAX_SQUARED_DISTANCE = 1500000
AUDIO_MIN_ENGINE_HZ = 25
AUDIO_MAX_ENGINE_HZ = 50
AUDIO_MAX_VELOCITY = 1000
AUDIO_ENGINE_NOISE_TIMER = 25
AUDIO_ENGINE_NOISE_MIN_VOLUME = 0.01
AUDIO_ENGINE_NOISE_MAX_VOLUME = 0.03
AUDIO_VOLUME_MIN = 0.0
AUDIO_VOLUME_MAX = 1.0
AUDIO_INCREMENT = 0.1

# audio string constants
AUDIO_CLICK = "click"
AUDIO_CANCEL = "cancel"
AUDIO_COUNTDOWN = "countdown"
AUDIO_RACE_START = "race start"
AUDIO_CAR_HIT = "car hit"
AUDIO_BGM1 = "bgm1"
AUDIO_BGM_MENU = "menu bgm"

# ui string constants
UI_BIG_BUTTON = "big button"
UI_BIGALT_BUTTON = "big button alt"
UI_SMALL_BUTTON = "small button"
UI_DYNAMIC_BUTTON = "dynamic button"
UI_DYNAMIC_BUTTON_ALT = "dynamic button alt"
UI_TEXTBOX = "Textbox"
UI_NORMAL = "Normal"
UI_HOVER = "Hover"
UI_CLICK = "Click"
UI_LEFT = "Left"
UI_MIDDLE = "Mid"
UI_RIGHT = "Right"
UI_COPYRIGHT_INFO = "©2022 Helical Studios"

# ui adjustments
UI_BIG_BUTTON_TEXT_ADJUSTMENT = [(0, -1), (-1, -1), (-1, -2)]
