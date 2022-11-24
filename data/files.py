import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    CWD = Path(os.path.abspath(os.path.dirname(sys.executable)))
    ASSETS_DIR = str(CWD.joinpath(Path("assets")))
else:
    ASSETS_DIR = str(Path(__file__).parent.parent.joinpath(Path("assets")))

# directories
SPRITES_DIR = "\\sprites\\"
CARS_DIR = "\\cars\\"
TRACKS_DIR = "\\tracks\\"
INPUTS_DIR = "\\inputs\\"

# fonts
FONT_ARIAL = ASSETS_DIR + "\\fonts\\arial.ttf"
