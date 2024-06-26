import random
from os import listdir
from os.path import isfile

from pygame import mixer

from data.constants import AUDIO_CLICK, AUDIO_CANCEL, AUDIO_CAR_HIT, AUDIO_BGM1, AUDIO_MAX_VELOCITY, \
    AUDIO_MIN_ENGINE_HZ, AUDIO_MAX_ENGINE_HZ, AUDIO_ENGINE_NOISE_MIN_VOLUME, AUDIO_ENGINE_NOISE_MAX_VOLUME, \
    AUDIO_COUNTDOWN, AUDIO_RACE_START, AUDIO_BGM_MENU
from data.files import DIR_AUDIO, DIR_AUDIO_HIT, DIR_AUDIO_BGM
from entities.singleton import Singleton
from managers.gamemanager import GameManager
from utils import mathutils
from utils.audioutils import Note, WaveForm


class AudioManager(metaclass=Singleton):
    def __init__(self):
        car_hit_files = [(DIR_AUDIO_HIT + f) for f
                         in listdir(DIR_AUDIO_HIT)
                         if isfile(DIR_AUDIO_HIT + f) and f[-3:] == "wav"]
        car_hit_sounds = []
        for f in car_hit_files:
            car_hit_sounds.append(mixer.Sound(f))

        self.engine_waveform = WaveForm.Sine
        self.engine_noise = Note(1, self.engine_waveform, 0.1)

        self._sound_dict: dict[str, list[mixer.Sound]] = {
            AUDIO_CLICK: [mixer.Sound(DIR_AUDIO + "click.wav")],
            AUDIO_CANCEL: [mixer.Sound(DIR_AUDIO + "cancel.wav")],
            AUDIO_COUNTDOWN: [mixer.Sound(DIR_AUDIO + "count.wav")],
            AUDIO_RACE_START: [mixer.Sound(DIR_AUDIO + "start.wav")],
            AUDIO_CAR_HIT: car_hit_sounds
        }
        self._sound_volume_dict: dict[str, float] = {
            AUDIO_CLICK: .5,
            AUDIO_CANCEL: .2,
            AUDIO_COUNTDOWN: .2,
            AUDIO_RACE_START: .2,
            AUDIO_CAR_HIT: .5
        }

        self._music_dict: dict[str, list[str]] = {
            AUDIO_BGM1: [DIR_AUDIO_BGM + "bgm1.wav"],
            AUDIO_BGM_MENU: [DIR_AUDIO_BGM + "menu.wav"]
        }
        self._music_volume_dict: dict[str, float] = {
            AUDIO_BGM1: .8,
            AUDIO_BGM_MENU: .8
        }

    def Play_Sound(self, sound: str, volume: float = 1, ui_sound: bool = True):
        if sound in self._sound_dict.keys():
            s = self._sound_dict[sound]
            r = random.randint(0, len(s) - 1)
            if ui_sound:
                volume_modifier = GameManager().GetOptions().ui_volume
            else:
                volume_modifier = GameManager().GetOptions().sfx_volume
            s[r].set_volume(self._sound_volume_dict[sound] * volume_modifier * volume)
            s[r].play()

    def Play_Music(self, music: str, volume: float = 1):
        if music in self._music_dict.keys():
            m = self._music_dict[music]
            r = random.randint(0, len(m) - 1)
            mixer.music.load(m[r])
            mixer.music.set_volume(self._music_volume_dict[music] * GameManager().GetOptions().music_volume * volume)
            mixer.music.play(-1)

    def Play_Engine_Noise(self, velocity: int):
        percent = mathutils.GetPercentageValue(
            abs(velocity), 0, AUDIO_MAX_VELOCITY)
        freq = mathutils.GetValueFromPercentage(percent, AUDIO_MIN_ENGINE_HZ, AUDIO_MAX_ENGINE_HZ)
        vol = mathutils.GetValueFromPercentage(
            percent, AUDIO_ENGINE_NOISE_MIN_VOLUME, AUDIO_ENGINE_NOISE_MAX_VOLUME) *\
            GameManager().GetOptions().sfx_volume
        self.engine_noise.stop()
        self.engine_noise = Note(freq, self.engine_waveform, vol)
        self.engine_noise.play(-1)

    def Stop_Music(self):
        mixer.music.stop()

    def Stop_Sounds(self):
        mixer.stop()
        self.engine_noise.stop()
