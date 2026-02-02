from mortier.coords import EuclideanCoords
import numpy as np

def test_init():
    p = EuclideanCoords([0, 1])
    assert p.x == 0
    assert p.y == 1


def approx_point(p, q, eps=1e-6):
    return abs(p.x - q.x) < eps and abs(p.y - q.y) < eps

def test_angle():
    p = EuclideanCoords([0, 1]).angle()
    assert np.isclose(p, np.pi/2)

def test_to_numpy():
    p = EuclideanCoords([0, 1]).numpy()
    assert type(p) == np.ndarray

def test_normal():
    p = EuclideanCoords([0, 1])
    n = EuclideanCoords([-1, 0])
    assert approx_point(p.normal(), n)

