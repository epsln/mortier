import pytest
from mortier.coords import EuclideanCoords
from mortier.face import Face
from mortier.tesselation import HyperbolicTesselation


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

    def set_band_angle(self, angle):
        self.calls.append(("set_band_angle", angle))

    def set_caption(self, caption):
        self.calls.append(("set_caption", caption))

    def set_label(self, caption):
        self.calls.append(("set_label", caption))

    def write(self):
        self.calls.append(("write",))
        return "output"


@pytest.fixture
def hyperbolic_tess():
    writer = MockWriter()
    tess = HyperbolicTesselation(writer, p=7, q=3, n_layers=2, angle=0.5)
    return tess, writer


def test_initialization(hyperbolic_tess):
    tess, _ = hyperbolic_tess
    assert tess.p == 7
    assert tess.q == 3
    assert tess.n_layers == 2
    assert tess.angle == 0.5
    assert isinstance(tess.faces, list)
    assert tess.scale == 50  # min(writer.size)/2


def test_set_scale(hyperbolic_tess):
    tess, _ = hyperbolic_tess
    tess.set_scale(2.0)
    assert tess.scale == 100  # 50*2


def test_set_draw_unit_circle(hyperbolic_tess):
    tess, _ = hyperbolic_tess
    tess.set_draw_unit_circle(True)
    assert tess.draw_unit_circle is True
    tess.set_draw_unit_circle(False)
    assert tess.draw_unit_circle is False


def test_tesselate_face_creates_faces(hyperbolic_tess):
    tess, _ = hyperbolic_tess
    tess.tesselate_face()
    assert len(tess.faces) > 0
    # All faces are Face instances
    assert all(isinstance(f, Face) for f in tess.faces)
    # Vertices are EuclideanCoords
    for f in tess.faces:
        for v in f.vertices:
            assert isinstance(v, EuclideanCoords)


def test_convert_to_half_plane(hyperbolic_tess):
    tess, _ = hyperbolic_tess
    tess.tesselate_face()
    original_vertices = [v.vertices.copy() for v in tess.faces]
    tess.half_plane = True
    tess.convert_to_half_plane()
    # Vertices changed after half-plane conversion
    for f, orig in zip(tess.faces, original_vertices):
        assert f.vertices != orig


def test_refine_tiling_calls_tesselate(hyperbolic_tess, monkeypatch):
    tess, _ = hyperbolic_tess
    called = []

    def fake_refine_lattice(iterations):
        called.append(iterations)

    tess.tess.refine_lattice = fake_refine_lattice
    tess.tesselate_face = lambda: called.append("tesselate_face")

    tess.refine_tiling(3)
    assert called[0] == 3
    assert called[1] == "tesselate_face"

