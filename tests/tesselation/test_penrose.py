import pytest
import numpy as np
from mortier.coords import EuclideanCoords
from mortier.face import Face, P2Penrose, P3Penrose
from mortier.tesselation.penrose import PenroseTesselation
from mortier.enums import TileType


class MockWriter:
    def __init__(self):
        self.calls = []
        self.size = (0, 0, 100, 100)
        self.n_tiles = 1
        self.lacing_mode = False
        self.bands_mode = False

    def face(self, face, dotted=False):
        self.calls.append(("face", face, dotted))

    def point(self, p):
        self.calls.append(("point", p))

    def line(self, p1, p2, dotted=False):
        self.calls.append(("line", p1, p2, dotted))

    def write(self):
        self.calls.append(("write",))
        return "output"


@pytest.fixture
def penrose_tess_p2():
    writer = MockWriter()
    tess = PenroseTesselation(writer, tile=TileType.P2, level=1)
    return tess, writer


@pytest.fixture
def penrose_tess_p3():
    writer = MockWriter()
    tess = PenroseTesselation(writer, tile=TileType.P3, level=1)
    return tess, writer


def test_initialization_p2(penrose_tess_p2):
    tess, writer = penrose_tess_p2
    # pen list should be initialized with 2 Penrose triangles
    assert all(isinstance(p, P2Penrose) for p in tess.pen)
    # level and tile
    assert tess.level == 1
    assert tess.tile == TileType.P2


def test_initialization_p3(penrose_tess_p3):
    tess, writer = penrose_tess_p3
    # pen list should be initialized with 2 Penrose triangles
    assert all(isinstance(p, P3Penrose) for p in tess.pen)
    # level and tile
    assert tess.level == 1
    assert tess.tile == TileType.P3


def test_tesselate_face_creates_faces(penrose_tess_p2):
    tess, writer = penrose_tess_p2
    tess.param_mode = True
    tess.assym_angle = 0.1
    tess.angle = 0.2
    tess.separated_site_mode = True

    tess.tesselate_face()
    # After inflation and merging, faces should be added
    assert len(tess.faces) > 0
    # All faces should be instances of Face
    assert all(isinstance(f, Face) for f in tess.faces)
    # All faces should have 3 or 4 vertices (triangles may be merged)
    for f in tess.faces:
        assert len(f.vertices) in (3, 4)


def test_face_vertices_orientation(penrose_tess_p2):
    tess, _ = penrose_tess_p2
    tess.tesselate_face()
    # Ensure vertices are EuclideanCoords instances
    for f in tess.faces:
        for v in f.vertices:
            assert isinstance(v, EuclideanCoords)


def test_state_setters_inherited(penrose_tess_p2):
    tess, _ = penrose_tess_p2
    tess.param_mode = "sin"
    tess.assym_angle = 0.2
    tess.separated_site_mode = True
    assert tess.param_mode == "sin"
    assert tess.assym_angle == 0.2
    assert tess.separated_site_mode is True

