import json
import os.path
import sys
import xml.etree.ElementTree as elementTree
import tkinter
from enum import Enum
from os.path import isfile
from tkinter import filedialog
from data.files import DIR_ASSETS, DIR_TRACKS
from enums.racedirection import RaceDirection
from models.trackmodel import TrackModel


class _TrackElementType(Enum):
    Wall = 0,
    Checkpoint = 1,
    Guidepath = 2


root = tkinter.Tk()
root.withdraw()

filepath = filedialog.askopenfilename()
if filepath == "":
    sys.exit()
filename = os.path.basename(filepath)
new_filepath = DIR_ASSETS + DIR_TRACKS + filename[:-3] + "json"

k_input = ""
overwrite = False
if isfile(new_filepath):
    while k_input not in ["y", "n"]:
        print(f"Track already exists. Overwrite? (y/n)")
        k_input = input()
    if k_input == "y":
        overwrite = True
    else:
        sys.exit()

track = TrackModel()

print("Track Name: ")
track.name = input()

print("Credits: ")
track.credits = input()

print("Thumbnail Filename: ")
track.thumbnail_filename = input()

print("Background Filename: ")
track.background_filename = input()

print("Foreground Filename: ")
track.foreground_filename = input()

print("Direction (Up,Right,Down,Left): ")
k_input = ""
while not RaceDirection.has_value(k_input):
    k_input = input()
track.direction = k_input

tree = elementTree.parse(filepath)
root = tree.getroot()
for child in root:
    if len(child) > 0 and ("polygon" in child.tag or "line" in child.tag):
        if "Wall" in child[0].text:
            points_str = child.attrib["points"]
            points_split = points_str.split(" ")
            points_list = []
            for i in range(0, len(points_split), 2):
                t = (int(float(points_split[i])), int(float(points_split[i + 1])))
                points_list.append(t)
            track.track_segments.append(points_list)
        elif "Checkpoint" in child[0].text:
            a_tuple = (int(float(child.attrib["x1"])), int(float(child.attrib["y1"])))
            b_tuple = (int(float(child.attrib["x2"])), int(float(child.attrib["y2"])))
            t = (a_tuple, b_tuple)
            track.checkpoints.append(t)
        elif "Guidepath" in child[0].text:
            points_str = child.attrib["points"]
            points_split = points_str.split(" ")
            points_list = []
            for i in range(0, len(points_split), 2):
                t = (int(float(points_split[i])), int(float(points_split[i + 1])))
                points_list.append(t)
            track.guidepath = points_list
with open(new_filepath, 'w') as outfile:
    json.dump(track.__dict__, outfile, indent=4)
