from mortier.coords.euclidean_coords import EuclideanCoords
from mortier.coords.lattice_coords import LatticeCoords

def test_init():
    p = LatticeCoords([0, 0, 0, 1])

def test_translate():
    p = LatticeCoords([0, 0, 0, 1])
    p1 = LatticeCoords([0, 1, 0, 1])

    p2 = p.translate(p1)

    assert p2.w == [0, 1, 0, 2]

def test_scale():
    p = LatticeCoords([1, 2, 0, 1])
    p1 = p.scale(2)
    assert p1.w == [2, 4, 0, 2] 

def toEuclidean(self):
    p = LatticeCoords([1, 2, 0, 1])
    p1 = p.toEuclidean()
    assert p1.x == 1
    assert p1.y == 1
