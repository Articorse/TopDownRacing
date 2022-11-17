import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = str(Path(sys._MEIPASS).joinpath(Path("assets")))
else:
    ASSETS_DIR = str(Path(__file__).parent.parent.joinpath(Path("assets")))

# directories
SPRITES_DIR = "\\sprites\\"
CARS_DIR = "\\cars\\"
TRACKS_DIR = "\\tracks\\"

# images
IMAGE_CAR = ASSETS_DIR + SPRITES_DIR + "carorange.png"
IMAGE_WHITECAR = ASSETS_DIR + SPRITES_DIR + "carwhite.png"
IMAGE_PLACEHOLDER = ASSETS_DIR + SPRITES_DIR + "test.png"
IMAGE_TRACK1_BG = ASSETS_DIR + SPRITES_DIR + "track1bg.png"

# fonts
FONT_ARIAL = ASSETS_DIR + "\\fonts\\arial.ttf"

# tracks
TRACKS_1 = ASSETS_DIR + TRACKS_DIR + "track1.json"

# cars
CAR_1 = ASSETS_DIR + CARS_DIR + "orange.json"
CAR_2 = ASSETS_DIR + CARS_DIR + "white.json"
