import enum


class ParamType(enum.Enum):
    CONSTANT = enum.auto()
    PERLIN = enum.auto()
    SIN = enum.auto()
    SIMPLEX = enum.auto()
