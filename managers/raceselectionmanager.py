import json
from os import listdir
from os.path import isfile
from typing import List
from data.constants import DEFAULT_LAPS, AI_COUNT
from data.files import ASSETS_DIR, CARS_DIR, TRACKS_DIR
from entities.carmodel import CarModel
from entities.singleton import Singleton
from entities.track import Track
from models.trackmodel import TrackModel


class RaceSelectionManager(metaclass=Singleton):
    def __init__(self):
        self.Free()

    def Free(self):
        self.available_cars: List[CarModel] = []
        self.available_tracks: List[Track] = []
        self.current_car_index = 0
        self.current_track_index = 0
        self.current_lap_count = DEFAULT_LAPS
        self.ai_count = AI_COUNT
        self.is_setup = False
        self.buttons = {}

    def Setup(self):
        car_files = [(ASSETS_DIR + CARS_DIR + f) for f
                     in listdir(ASSETS_DIR + CARS_DIR)
                     if isfile(ASSETS_DIR + CARS_DIR + f) and f[-4:] == "json"]
        track_files = [(ASSETS_DIR + TRACKS_DIR + f) for f
                       in listdir(ASSETS_DIR + TRACKS_DIR)
                       if isfile(ASSETS_DIR + TRACKS_DIR + f) and f[-4:] == "json"]
        for f in car_files:
            self.available_cars.append(CarModel(**json.load(open(f))))
        for f in track_files:
            track_model: TrackModel = TrackModel.FromDict(json.load(open(f)))
            self.available_tracks.append(Track(track_model))
        self.is_setup = True

    def GetCurrentCarModel(self):
        if self.is_setup:
            return self.available_cars[self.current_car_index]
        else:
            return None

    def GetCurrentTrack(self):
        if self.is_setup:
            return self.available_tracks[self.current_track_index]
        else:
            return None
