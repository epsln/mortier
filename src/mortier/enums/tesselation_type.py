from enum import Enum


class TesselationType(str, Enum):
    REGULAR = "regular"
    PENROSE = "penrose"
    HYPERBOLIC = "hyperbolic"
