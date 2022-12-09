import random
from array import array
from enum import Enum

from pygame.mixer import Sound, get_init


class WaveForm(Enum):
    Sine = 0,
    Random = 1,
    Mixed = 2


class Note(Sound):
    def __init__(self, frequency, wave_form=WaveForm.Sine, volume=.1):
        self.frequency = frequency
        self.wave_form = wave_form
        self.volume = volume
        if self.volume < 0:
            self.volume = 0
        if self.volume > 1:
            self.volume = 1
        Sound.__init__(self, self.build_samples())

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = int((2 ** (abs(get_init()[1]) - 1) - 1) * self.volume)
        for time in range(period):
            if self.wave_form == WaveForm.Mixed:
                amp = int(amplitude / 2)
            else:
                amp = amplitude
            if self.wave_form in [WaveForm.Sine, WaveForm.Mixed]:
                if time < period * 0.5:
                    samples[time] += amp
                else:
                    samples[time] += -amp
            if self.wave_form in [WaveForm.Random, WaveForm.Mixed]:
                if random.randint(0, 1) == 0:
                    samples[time] += amp
                else:
                    samples[time] += -amp
        return samples
