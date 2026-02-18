import pytest
from mortier.coords import LatticeCoords
from mortier.face.face import Face
from mortier.tesselation.regular_tesselation import RegularTesselation
import numpy as np


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
def tessellation():
    writer = MockWriter()
    tess_dict = {
        "T1": [1, 0, 0, 0],
        "T2": [0, 1, 0, 0],
        "Seed": [[0, 0, 0, 0], [1, 0, 0, 0]]
    }
    tess = RegularTesselation(writer, tess_dict, "TestTess")
    return tess, writer


def test_initialization(tessellation):
    tess, writer = tessellation
    # Check lattice vectors
    assert isinstance(tess.T1, LatticeCoords)
    assert isinstance(tess.T2, LatticeCoords)
    assert isinstance(tess.T3, LatticeCoords)
    # Check seed and cell
    assert tess.seed == tess.tess["Seed"]
    assert isinstance(tess.cell, Face)
    # Check wpow length
    assert len(tess.wpow) == 12


def test_setters(tessellation):
    tess, _ = tessellation
    tess.set_param_mode(True)
    assert tess.param_mode is True
    tess.set_show_underlying(True)
    assert tess.show_underlying is True

    new_tess_dict = {
        "T1": [0, 1, 0, 0],
        "T2": [1, 0, 0, 0],
        "Seed": [[0, 0, 0, 0]]
    }
    tess.set_tesselation(new_tess_dict, "NewID")
    assert tess.tess_id == "NewID"
    np.testing.assert_allclose(tess.T1.w, new_tess_dict["T1"])
    np.testing.assert_allclose(tess.T2.w, new_tess_dict["T2"])


def test_draw_seed_calls_writer(tessellation):
    tess, writer = tessellation
    tess.draw_seed()
    # cell should be drawn dotted
    assert any(call[0] == "face" and call[2] is True for call in writer.calls)
    # seed points should be drawn
    seed_points_calls = [c for c in writer.calls if c[0] == "point"]
    assert len(seed_points_calls) == len(tess.seed)
    # write should be called
    assert any(call[0] == "write" for call in writer.calls)


def test_draw_cell_and_draw_star_call_lines_and_points(tessellation):
    tess, writer = tessellation
    tess.draw_cell()
    assert any(call[0] == "line" for call in writer.calls)
    writer.calls.clear()
    tess.draw_star()
    # star should call face, line, point, and write
    assert any(call[0] == "face" for call in writer.calls)
    assert any(call[0] == "point" for call in writer.calls)
    assert any(call[0] == "line" for call in writer.calls)
    assert any(call[0] == "write" for call in writer.calls)


def test_draw_edge_calls_line_and_face(tessellation):
    tess, writer = tessellation
    tess.draw_edge()
    # edges should be lines
    assert any(call[0] == "line" for call in writer.calls)
    # cell should be drawn dotted
    assert any(call[0] == "face" for call in writer.calls)


def test_tesselate_face_adds_faces(tessellation):
    tess, writer = tessellation
    # Override find_corners to fixed small range
    tess.find_corners = lambda: (0, 1, 0, 1)
    tess.tesselate_face()
    assert len(tess.faces) > 0
    # All faces added should be Face instances
    assert all(isinstance(f, Face) for f in tess.faces)


def test_find_corners_bounds(tessellation):
    tess, _ = tessellation
    # By default show_base=False, so corners computed
    i_min, i_max, j_min, j_max = tess.find_corners()
    assert isinstance(i_min, int)
    assert isinstance(i_max, int)
    assert isinstance(j_min, int)
    assert isinstance(j_max, int)
    # If show_base=True, returns fixed range
    tess.show_base = True
    assert tess.find_corners() == (-1, 2, -1, 2)

