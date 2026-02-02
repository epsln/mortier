from mortier.coords import LatticeCoords, EuclideanCoords, Line
import numpy as np

def approx_point(p, q, eps=1e-6):
    return abs(p.x - q.x) < eps and abs(p.y - q.y) < eps

def test_init_line():
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([0, 1])
    l = Line(p0, p1)
    assert l.beg_pt == p0
    assert l.end_pt == p1
    assert approx_point(l.vec, EuclideanCoords([0, 1]))

def test_heading():
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([0, 1])
    l = Line(p0, p1)
    h = l.heading()
    assert np.isclose(h, np.pi/2)

def test_len():
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([0, 1])
    l = Line(p0, p1).len()
    assert np.isclose(l, 1)

def test_mid_point():
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([0, 1])
    l = Line(p0, p1)
    assert approx_point(l.get_midpoint(), EuclideanCoords([0, 0.5]))
