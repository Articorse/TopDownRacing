import os
import sys
from pathlib import Path

from data.constants import UI_BIG_BUTTON, UI_SMALL_BUTTON, UI_BIGALT_BUTTON, UI_DYNAMIC_BUTTON, UI_DYNAMIC_BUTTON_ALT, \
    UI_TEXTBOX

if getattr(sys, 'frozen', False):
    DIR_BASE = str(os.path.abspath(os.path.dirname(sys.executable)))
else:
    DIR_BASE = str(Path(__file__).parent.parent)

DIR_ASSETS = str(Path(DIR_BASE).joinpath(Path("assets")))

# directories
DIR_SPRITES = DIR_ASSETS + "\\sprites\\"
DIR_UI = DIR_ASSETS + "\\sprites\\ui\\"
DIR_CARS = DIR_ASSETS + "\\cars\\"
DIR_TRACKS = DIR_ASSETS + "\\tracks\\"
DIR_INPUTS = DIR_ASSETS + "\\inputs\\"
DIR_AUDIO = DIR_ASSETS + "\\audio\\"
DIR_AUDIO_HIT = DIR_ASSETS + "\\audio\\hit\\"
DIR_AUDIO_BGM = DIR_ASSETS + "\\audio\\bgm\\"

# fonts
FONT_ARIAL = DIR_ASSETS + "\\fonts\\arial.ttf"
FONT_JOYSTIX = DIR_ASSETS + "\\fonts\\joystix monospace.ttf"

# audio
FILE_AUDIO_CLICK = "click.wav"
FILE_AUDIO_CANCEL = "cancel.wav"
FILE_AUDIO_BGM_MENU = "menu.wav"

# options
DIR_OPTIONS = DIR_BASE + "\\config"
FILE_OPTIONS = DIR_OPTIONS + "\\options.json"

# ui images
UI_ELEMENT_DICT = {
    UI_BIG_BUTTON: ["BigButtonNormal.png", "BigButtonHover.png", "BigButtonClick.png"],
    UI_BIGALT_BUTTON: ["BigButtonAltNormal.png", "BigButtonAltHover.png", "BigButtonAltClick.png"],
    UI_SMALL_BUTTON: ["SmallButtonNormal.png", "SmallButtonHover.png", "SmallButtonClick.png"],
    UI_DYNAMIC_BUTTON: [["ButtonNormalLeft.png", "ButtonNormalMid.png", "ButtonNormalRight.png"],
                        ["ButtonHoverLeft.png", "ButtonHoverMid.png", "ButtonHoverRight.png"],
                        ["ButtonClickLeft.png", "ButtonClickMid.png", "ButtonClickRight.png"],
                        "ButtonShine.png"],
    UI_DYNAMIC_BUTTON_ALT: [["ButtonNormalLeftAlt.png", "ButtonNormalMid.png", "ButtonNormalRightAlt.png"],
                            ["ButtonHoverLeftAlt.png", "ButtonHoverMid.png", "ButtonHoverRightAlt.png"],
                            ["ButtonClickLeftAlt.png", "ButtonClickMid.png", "ButtonClickRightAlt.png"],
                            "ButtonShine.png"],
    UI_TEXTBOX: ["TextBoxLeft.png", "TextBoxMid.png", "TextBoxRight.png"]
}
