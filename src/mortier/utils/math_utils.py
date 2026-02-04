import numpy as np
from noise import pnoise3, snoise3

from mortier.coords import LatticeCoords
from mortier.enums import ParamType


def in_bounds(face, size):
    for v in face:
        if v.x < size[0] or v.x > size[2] or v.y < size[1] or v.y > size[3]:
            return False
    return True


def map_num(x, min_in, max_in, min_out, max_out):
    return (((x - min_in) * (max_out - min_out)) / (max_in - min_in)) + min_out


def plane_coords(p, w):
    return LatticeCoords([p.w[i] * w[i] for i in range(4)]).sum()


def plane_to_tile_coords(tiling, w, x, y):
    t1 = LatticeCoords(tiling["T1"])
    t2 = LatticeCoords(tiling["T2"])
    z1 = plane_coords(t1, w)
    z2 = plane_coords(t2, w)

    a = z1.real
    b = z1.imag
    c = z2.real
    d = z2.imag

    det = a * d - b * c
    a = d / det
    b = -c / det
    c = -b / det
    d = a / det

    return complex(a * x + b * y, c * x + d * y)


def angle_parametrisation(point, mode, bounds, frame_num=[]):
    z = np.sin(map_num(frame_num[0], 0, frame_num[1], 0, 2 * np.pi))

    if mode == ParamType.CONSTANT:
        z = np.sin(map_num(frame_num[0], 0, frame_num[1], 0, 2 * np.pi))
        return map_num(z, -1, 1, 0.01, np.pi / 2)

    if mode == ParamType.SIN:
        return (np.sin(map_num(point.y, bounds[1], bounds[3], 0, 2 * np.pi)) + 1) / 2

    if mode == ParamType.PERLIN:
        x = map_num(point.x, bounds[0], bounds[2], 0, 2)
        y = map_num(point.y, bounds[1], bounds[3], 1, 2)
        angle = pnoise3(x, y, z, octaves=3)
        angle = map_num(angle, -1, 1, 0.01, np.pi / 2)
        return angle

    if mode == ParamType.SIMPLEX:
        x = map_num(point.x, bounds[0], bounds[2], -1, 0.5)
        y = map_num(point.y, bounds[1], bounds[3], 3, 4)
        angle = snoise3(x, y, z, octaves=4)
        angle = map_num(angle, -1, 1, 0.01, np.pi / 2)
        return angle

    raise ValueError(f"Missing or unrecognized mode: {mode}.") 
