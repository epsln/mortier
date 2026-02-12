import io
import pytest

# Adjust to your real module path
from mortier.writer import SVGWriter
from mortier.coords import EuclideanCoords
from mortier.face import Face


class FakePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_svgwriter_initialization():
    w = SVGWriter("testfile", size=(0, 0, 100, 200))

    assert w.filename == "testfile"
    assert w.size == (0, 0, 100, 200)
    assert w.dwg is not None
    assert w.api_mode is False


def test_svgwriter_viewbox():
    w = SVGWriter("testfile", size=(0, 0, 100, 200))
    assert w.dwg['viewBox'] == "0,0,100,200"


def test_circle_in_bounds():
    w = SVGWriter("testfile", size=(0, 0, 100, 100))

    p = FakePoint(50, 50)
    w.circle(p, 10, color=(255, 0, 0))

    # One element added
    assert len(w.dwg.elements) > 0

    circle = w.dwg.elements[-1]
    assert circle['stroke'] == "rgb(255, 0, 0)"
    assert circle['fill'] == "none"


def test_circle_out_of_bounds():
    w = SVGWriter("testfile", size=(0, 0, 100, 100))

    p = FakePoint(200, 200)
    w.circle(p, 10)

    # Nothing added
    assert len(w.dwg.elements) == 1  # only defs element exists


# ------------------------------------------------------------------
# line()
# ------------------------------------------------------------------

def test_line_drawn_if_one_point_in_bounds():
    w = SVGWriter("testfile", size=(0, 0, 100, 100))

    p0 = FakePoint(50, 50)
    p1 = FakePoint(200, 200)

    w.line(p0, p1, color=(0, 255, 0))

    line = w.dwg.elements[-1]
    assert line['stroke'] == "rgb(0, 255, 0)"
    assert line['stroke-width'] == 0.5


def test_line_not_drawn_if_both_out_of_bounds():
    w = SVGWriter("testfile", size=(0, 0, 100, 100))

    p0 = FakePoint(200, 200)
    p1 = FakePoint(300, 300)

    initial_len = len(w.dwg.elements)
    w.line(p0, p1)

    assert len(w.dwg.elements) == initial_len


# ------------------------------------------------------------------
# write()
# ------------------------------------------------------------------

def test_write_api_mode_returns_string():
    w = SVGWriter("testfile")
    w.api_mode = True

    result = w.write()

    assert isinstance(result, str)
    assert "<svg" in result


def test_write_file_mode(monkeypatch):
    w = SVGWriter("testfile")

    called = {}

    def fake_save():
        called["saved"] = True

    monkeypatch.setattr(w.dwg, "save", fake_save)

    result = w.write()

    assert result is None
    assert called.get("saved") is True


# ------------------------------------------------------------------
# set_color_bg()
# ------------------------------------------------------------------

def test_set_color_bg_adds_rect():
    w = SVGWriter("testfile")

    w.set_color_bg((10, 20, 30))

    rect = w.dwg.elements[-1]

    assert rect['fill'] == "rgb(10, 20, 30)"
    assert rect['width'] == '100%'
    assert rect['height'] == '100%'


def test_set_color_bg_none():
    w = SVGWriter("testfile")

    initial_len = len(w.dwg.elements)
    w.set_color_bg(None)

    assert len(w.dwg.elements) == initial_len


# ------------------------------------------------------------------
# new()
# ------------------------------------------------------------------

def test_new_resets_drawing():
    w = SVGWriter("testfile", size=(0, 0, 100, 100))
    w.circle(FakePoint(50, 50), 10)

    assert len(w.dwg.elements) > 1

    w.new("newfile", size=(0, 0, 200, 200))

    # New drawing object created
    assert w.filename == "newfile"
    assert w.size == (0, 0, 200, 200)
    assert w.dwg['viewBox'] == "0,0,200,200"
