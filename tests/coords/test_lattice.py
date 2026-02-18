import numpy as np

from mortier.coords.euclidean_coords import EuclideanCoords
from mortier.coords.lattice_coords import LatticeCoords

def test_init():
    p = LatticeCoords([0, 0, 0, 1])

def test_translate():
    p = LatticeCoords([0, 0, 0, 1])
    p1 = LatticeCoords([0, 1, 0, 1])

    p2 = p.translate(p1)
    print(p2.w)
    np.testing.assert_allclose(p2.w, [0 + 0j, 1 + 0j, 0 + 0j, 2 + 0j])

def test_scale():
    p = LatticeCoords([1, 2, 0, 1])
    p1 = p.scale(2)
    np.testing.assert_allclose(p1.w, [2 + 0j, 4 + 0j, 0 + 0j, 2 + 0j])

def toEuclidean(self):
    p = LatticeCoords([1, 2, 0, 1])
    p1 = p.toEuclidean()
    assert p1.x == 1
    assert p1.y == 1
