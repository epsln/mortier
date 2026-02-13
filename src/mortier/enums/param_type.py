from enum import Enum


class ParamType(str, Enum):
    CONSTANT = "constant"
    PERLIN = "perlin" 
    SIN = "sin" 
    SIMPLEX = "simplex" 
