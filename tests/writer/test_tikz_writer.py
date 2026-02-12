import pytest
import numpy as np

from mortier.writer import TikzWriter



class FakePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x},{self.y}"


class FakeFace:
    def __init__(self, vertices, mid_points=None):
        self.vertices = vertices
        self.mid_points = mid_points or []



def test_initialization_defaults():
    w = TikzWriter("out.tex", size=(0, 0, 10, 20))

    assert "\\begin{tikzpicture}" in w.header
    assert "\\clip" in w.header
    assert w.footer.strip() == "\\end{tikzpicture}"
    assert w.output == []


def test_draw_borders_enabled():
    w = TikzWriter("out.tex", size=(0, 0, 10, 20), draw_borders=True)
    assert "\\draw (0, 0) rectangle" in w.header


def test_circle_output():
    w = TikzWriter("out.tex")
    p = FakePoint(1, 2)

    w.circle(p, 3)

    assert "\\filldraw[black] (1, 2) circle (3);" in w.output


def test_point_output():
    w = TikzWriter("out.tex")
    p = FakePoint(5, 6)

    w.point(p)

    assert "\\filldraw[black] (5, 6) circle (2pt);" in w.output


def test_line_in_bounds():
    w = TikzWriter("out.tex", size=(0, 0, 100, 100))

    p0 = FakePoint(10, 10)
    p1 = FakePoint(20, 20)

    w.line(p0, p1, dotted=True, color="red")

    assert any("draw=red, dotted" in line for line in w.output)


def test_line_out_of_bounds():
    w = TikzWriter("out.tex", size=(0, 0, 10, 10))

    p0 = FakePoint(50, 50)
    p1 = FakePoint(60, 60)

    w.line(p0, p1)

    assert w.output == []


def test_line_rounding():
    w = TikzWriter("out.tex", size=(0, 0, 100, 100))

    p0 = FakePoint(1.1234, 2.9876)
    p1 = FakePoint(3.5555, 4.4444)

    w.line(p0, p1)

    line = w.output[0]
    assert "(1.12, 2.99)" in line
    assert "(3.56, 4.44)" in line


def test_face_simple_polygon(monkeypatch):
    w = TikzWriter("out.tex", size=(0, 0, 100, 100))

    # deterministic random
    monkeypatch.setattr(np.random, "randint", lambda *args, **kwargs: np.array([0, 1]))

    vertices = [
        FakePoint(10, 10),
        FakePoint(20, 10),
        FakePoint(20, 20),
    ]

    face = FakeFace(vertices, mid_points=[FakePoint(0, 0)])

    w.face(face)

    assert any("\\draw[black" in line for line in w.output)


def test_face_dotted():
    w = TikzWriter("out.tex", size=(0, 0, 100, 100))

    vertices = [
        FakePoint(10, 10),
        FakePoint(20, 10),
    ]

    face = FakeFace(vertices)

    w.face(face, dotted=True)

    assert any("dotted" in line for line in w.output)


def test_set_scale():
    w = TikzWriter("out.tex")
    w.set_scale(2.5)

    assert "[scale = 2.5]" in w.header


def test_set_caption_and_label():
    w = TikzWriter("out.tex")

    w.set_caption("My Caption")
    w.set_label("test")

    assert "\\caption{My Caption}" in w.footer
    assert "\\label{fig:test}" in w.footer


def test_set_bounds():
    w = TikzWriter("out.tex", size=(0, 0, 10, 20))

    assert "\\clip (1,1) rectangle +" in w.header


def test_no_clip():
    w = TikzWriter("out.tex")
    w.no_clip()

    assert w.header == "\\begin{tikzpicture}\n"



def test_write(monkeypatch):
    w = TikzWriter("out.tex")
    w.output = ["line1;", "line2;"]

    written = {}

    class FakeFile:
        def write(self, data):
            written.setdefault("content", "")
            written["content"] += data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: FakeFile())

    w.write()

    assert "\\begin{tikzpicture}" in written["content"]
    assert "line1;" in written["content"]
    assert "\\end{tikzpicture}" in written["content"]


def test_new_resets_state():
    w = TikzWriter("old.tex", size=(0, 0, 10, 20))
    w.output.append("something")

    w.new("new.tex", size=(0, 0, 20, 30))

    assert w.filename == "new.tex"
    assert w.output == []
    assert "\\clip" in w.header

