import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    assets_dir = str(Path(sys._MEIPASS).joinpath(Path("assets")))
else:
    assets_dir = str(Path(__file__).parent.parent.joinpath(Path("assets")))

# images
IMAGE_CAR = assets_dir + "\\sprites\\car.png"
IMAGE_WHITECAR = assets_dir + "\\sprites\\carwhite.png"

# fonts
FONT_ARIAL = assets_dir + "\\fonts\\arial.ttf"

# tracks
TRACKS_1 = assets_dir + "\\tracks\\track1.json"
TRACKS_2 = assets_dir + "\\tracks\\track2.json"