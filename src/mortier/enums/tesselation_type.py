import enum


class TesselationType(enum.Enum):
    REGULAR = enum.auto()
    PENROSE = enum.auto()
    HYPERBOLIC = enum.auto()
