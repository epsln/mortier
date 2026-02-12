import math
import pytest
import numpy as np

# Adjust this import to your actual module path
from mortier.writer.writer import Writer
from mortier.coords import EuclideanCoords 
from mortier.face import Face 


class RecordingWriter(Writer):
    """Subclass Writer to record draw calls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines_drawn = []
        self.points_drawn = []

    def line(self, p0, p1, color=(255, 255, 255)):
        self.lines_drawn.append((p0, p1, color))

    def point(self, p, color=(255, 255, 255)):
        self.points_drawn.append((p, color))


class FakeFace:
    def __init__(self, vertices):
        self.vertices = vertices


def test_constructor_assert_conflict():
    w = Writer("test.png", lacing_mode=True, bands_mode=False)
    # should fail because both True
    with pytest.raises(AssertionError):
        Writer("x", lacing_mode=True, bands_mode=True)


def test_set_band_angle():
    w = Writer("test.png")
    w.set_band_angle(42)
    assert w.bands_angle == 42


def test_in_bounds_valid():
    w = Writer("test.png", size=(0, 0, 100, 100))
    assert w.in_bounds(EuclideanCoords([50, 50])) is True


def test_in_bounds_invalid_nan():
    w = Writer("test.png", size=(0, 0, 100, 100))
    assert w.in_bounds(EuclideanCoords([math.nan, 0])) is False


def test_in_bounds_outside():
    w = Writer("test.png", size=(0, 0, 100, 100))
    assert w.in_bounds(EuclideanCoords([200, 50])) is False


def test_hatch_fill_draws_lines(monkeypatch):
    w = RecordingWriter("test.png")
    w.hatch_fill_parameters = {
        "angle": 0,
        "spacing": 5,
        "crosshatch": False,
        "type": None,
        "color": (1, 2, 3),
    }

    square = [
        EuclideanCoords([0, 0]),
        EuclideanCoords([10, 0]),
        EuclideanCoords([10, 10]),
        EuclideanCoords([0, 10]),
    ]

    w.hatch_fill(square)

    assert len(w.lines_drawn) > 0
    assert len(w.points_drawn) == 0


def test_hatch_fill_dot_mode(monkeypatch):
    from mortier.enums import HatchType

    w = RecordingWriter("test.png")
    w.hatch_fill_parameters = {
        "angle": 0,
        "spacing": 5,
        "crosshatch": False,
        "type": HatchType.DOT,
        "color": (1, 2, 3),
    }

    square = [
        EuclideanCoords([0, 0]),
        EuclideanCoords([10, 0]),
        EuclideanCoords([10, 10]),
        EuclideanCoords([0, 10]),
    ]

    w.hatch_fill(square)

    assert len(w.points_drawn) > 0
    assert len(w.lines_drawn) == 0


def test_face_draws_polygon_lines(monkeypatch):
    w = RecordingWriter("test.png")

    # prevent real fill_intersect_points
    monkeypatch.setattr(
        "mortier.utils.geometry.fill_intersect_points",
        lambda face, intersect: None
    )

    square = [
        EuclideanCoords([0, 0]),
        EuclideanCoords([10, 0]),
        EuclideanCoords([10, 10]),
        EuclideanCoords([0, 10]),
    ]

    face = Face(square)

    w.face(face)

    # should draw 4 edges
    assert len(w.lines_drawn) == 4


def test_face_with_hatching(monkeypatch):
    w = RecordingWriter("test.png")

    monkeypatch.setattr(
        "mortier.utils.geometry.fill_intersect_points",
        lambda face, intersect: None
    )

    w.hatch_fill_parameters = {
        "angle": 0,
        "spacing": 5,
        "crosshatch": False,
        "type": None,
        "color": (1, 2, 3),
    }

    square = [
        EuclideanCoords([0, 0]),
        EuclideanCoords([10, 0]),
        EuclideanCoords([10, 10]),
        EuclideanCoords([0, 10]),
    ]

    face = Face(square)

    w.face(face)

    # polygon edges + hatch lines
    assert len(w.lines_drawn) >= 4

