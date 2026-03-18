from enum import Enum
# pylint: disable=invalid-name

import json
from enum import Enum

import json
from enum import Enum

with open("data/output.json") as f:
    data = json.load(f)

RegularTesselationType = Enum(
    "RegularTesselationType",
    {k: k for k in data.keys() if k != "_failures"},
    type=str
)
