import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    CWD = Path(os.path.abspath(os.path.dirname(sys.executable)))
    DIR_ASSETS = str(CWD.joinpath(Path("assets")))
else:
    DIR_ASSETS = str(Path(__file__).parent.parent.joinpath(Path("assets")))

# directories
DIR_SPRITES = "\\sprites\\"
DIR_CARS = "\\cars\\"
DIR_TRACKS = "\\tracks\\"
DIR_INPUTS = "\\inputs\\"
DIR_AUDIO = "\\audio\\"
DIR_AUDIO_HIT = "hit\\"
DIR_AUDIO_BGM = "bgm\\"

# fonts
FONT_ARIAL = DIR_ASSETS + "\\fonts\\arial.ttf"

# audio
FILE_AUDIO_CLICK = "click.wav"
FILE_AUDIO_CANCEL = "cancel.wav"
