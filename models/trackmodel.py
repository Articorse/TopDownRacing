from enums.racedirection import RaceDirection


class TrackModel:
    def __init__(self):
        self.name = ""
        self.credits = ""
        self.thumbnail_filename = ""
        self.background_filename = ""
        self.foreground_filename = ""
        self.direction = RaceDirection.Right
        self.track_segments: list[list[tuple[int, int]]] = []
        self.checkpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
        self.guidepath: list[tuple[int, int]] = []

    @staticmethod
    def FromDict(json_dict: dict):
        tm = TrackModel()
        tm.name = json_dict["name"]
        tm.credits = json_dict["credits"]
        tm.thumbnail_filename = json_dict["thumbnail_filename"]
        tm.background_filename = json_dict["background_filename"]
        tm.foreground_filename = json_dict["foreground_filename"]
        tm.direction = json_dict["direction"]
        tm.track_segments = json_dict["track_segments"]
        tm.checkpoints = json_dict["checkpoints"]
        tm.guidepath = json_dict["guidepath"]
        return tm
