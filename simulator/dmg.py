from ..entity import Player

import pathlib

Player.fromJSON(pathlib.Path("../data/characters/fvtt-Actor-Bertilak.json").read_text())
