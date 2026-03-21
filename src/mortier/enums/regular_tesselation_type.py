from enum import Enum

# pylint: disable=invalid-name

import json


with open("data/output.json") as f:
    data = json.load(f)

RegularTesselationType = Enum(
    "RegularTesselationType", {k: k for k in data.keys() if k != "_failures"}, type=str
)
