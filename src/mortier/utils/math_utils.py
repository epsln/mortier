import numpy as np
from noise import pnoise3, snoise3

from mortier.coords import LatticeCoords
from mortier.enums import ParamType


def in_bounds(face, size):
    """
    Check whether all vertices of a face lie within given bounds.

    Parameters
    ----------
    face : iterable
        Iterable of vertices with `x` and `y` attributes.
    size : tuple of float
        Bounding box defined as (xmin, ymin, xmax, ymax).

    Returns
    -------
    bool
        True if all vertices are inside the bounds, False otherwise.
    """
    for v in face:
        if v.x < size[0] or v.x > size[2] or v.y < size[1] or v.y > size[3]:
            return False
    return True


def map_num(x, min_in, max_in, min_out, max_out):
    """
    Linearly map a value from one interval to another.

    Parameters
    ----------
    x : float
        Input value.
    min_in : float
        Minimum of the input range.
    max_in : float
        Maximum of the input range.
    min_out : float
        Minimum of the output range.
    max_out : float
        Maximum of the output range.

    Returns
    -------
    float
        Mapped value in the output range.
    """
    return ((x - min_in) * (max_out - min_out)) / (max_in - min_in) + min_out


def plane_coords(p, w):
    """
    Convert lattice coordinates to complex plane coordinates.

    Parameters
    ----------
    p : LatticeCoords
        Lattice coordinate vector.
    w : array-like
        Weight vector of length 4.

    Returns
    -------
    complex
        Complex number representing the plane coordinates.
    """
    return LatticeCoords([p.w[i] * w[i] for i in range(4)]).sum()


def plane_to_tile_coords(tiling, w, x, y):
    """
    Convert plane coordinates to tile coordinates.

    Parameters
    ----------
    tiling : dict
        Tiling definition containing lattice vectors "T1" and "T2".
    w : array-like
        Weight vector used for plane projection.
    x : float
        X-coordinate in the plane.
    y : float
        Y-coordinate in the plane.

    Returns
    -------
    complex
        Tile-space coordinates as a complex number.
    """
    t1 = LatticeCoords(tiling["T1"])
    t2 = LatticeCoords(tiling["T2"])

    z1 = plane_coords(t1, w)
    z2 = plane_coords(t2, w)

    a = z1.real
    b = z1.imag
    c = z2.real
    d = z2.imag

    det = a * d - b * c

    a_ = d / det
    b_ = -c / det
    c_ = -b / det
    d_ = a / det

    return complex(a_ * x + b_ * y, c_ * x + d_ * y)


def angle_parametrisation(point, mode, bounds, frame_num=[0, 1]):
    """
    Compute an angle value using different parametrisation modes.

    Parameters
    ----------
    point : EuclideanCoords
        Point used for spatial parametrisation.
    mode : ParamType
        Type of parametrisation to use.
    bounds : tuple of float
        Bounding box as (xmin, ymin, xmax, ymax).
    frame_num : list of int, optional
        Animation frame information as [current_frame, total_frames].

    Returns
    -------
    float
        Computed angle value in radians.

    Raises
    ------
    ValueError
        If the parametrisation mode is not recognized.
    """
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
        return map_num(angle, -1, 1, 0.01, np.pi / 2)

    if mode == ParamType.SIMPLEX:
        x = map_num(point.x, bounds[0], bounds[2], -1, 0.5)
        y = map_num(point.y, bounds[1], bounds[3], 3, 4)
        angle = snoise3(x, y, z, octaves=4)
        return map_num(angle, -1, 1, 0.01, np.pi / 2)

    raise ValueError(f"Missing or unrecognized mode: {mode}.")
