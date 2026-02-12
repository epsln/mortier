import pytest

from mortier.writer import BitmapWriter

class FakePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class RecordingDraw:
    def __init__(self):
        self.calls = []

    def point(self, coords, fill=None):
        self.calls.append(("point", coords, fill))

    def arc(self, bbox, start=None, end=None):
        self.calls.append(("arc", bbox, start, end))

    def ellipse(self, bbox, outline=None):
        self.calls.append(("ellipse", bbox, outline))

    def line(self, coords, fill=None, width=None):
        self.calls.append(("line", coords, fill, width))


def test_initialization():
    w = BitmapWriter("test.png", size=(0, 0, 100, 200))

    assert w.filename == "test.png"
    assert w.size == (0, 0, 100, 200)
    assert w.image.size == (100, 200)


def test_point_draw(monkeypatch):
    w = BitmapWriter("test.png")
    recorder = RecordingDraw()
    w.output = recorder

    p = FakePoint(10, 20)
    w.point(p, color=(1, 2, 3))

    assert recorder.calls == [
        ("point", (10, 20), (1, 2, 3))
    ]


def test_arc_draw(monkeypatch):
    w = BitmapWriter("test.png")
    recorder = RecordingDraw()
    w.output = recorder

    w.arc((0, 0, 10, 10), 0, 180)

    assert recorder.calls == [
        ("arc", (0, 0, 10, 10), 0, 180)
    ]


def test_circle_draw(monkeypatch):
    w = BitmapWriter("test.png")
    recorder = RecordingDraw()
    w.output = recorder

    p = FakePoint(50, 50)
    w.circle(p, 10, color=(5, 6, 7))

    assert recorder.calls == [
        ("ellipse", [(40, 40), (60, 60)], (5, 6, 7))
    ]



def test_set_color_bg(monkeypatch):
    w = BitmapWriter("test.png")

    called = {}

    def fake_paste(color, box):
        called["color"] = color
        called["box"] = box

    monkeypatch.setattr(w.image, "paste", fake_paste)

    w.set_color_bg((10, 20, 30))

    assert called["color"] == (10, 20, 30)
    assert called["box"] == (0, 0, w.image.size[0], w.image.size[1])


def test_set_color_bg_none():
    w = BitmapWriter("test.png")
    # Should not crash
    w.set_color_bg(None)



@pytest.mark.parametrize(
    "color_input, expected",
    [
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("cyan", (0, 128, 200)),
        ("yellow", (255, 227, 0)),
        ((1, 2, 3), (1, 2, 3)),
    ],
)
def test_line_color_conversion(monkeypatch, color_input, expected):
    w = BitmapWriter("test.png")
    recorder = RecordingDraw()
    w.output = recorder

    p0 = FakePoint(0, 0)
    p1 = FakePoint(10, 10)

    w.line(p0, p1, color=color_input)

    assert recorder.calls == [
        ("line", [(0, 0), (10, 10)], expected, 1)
    ]



def test_write_saves_file(monkeypatch):
    w = BitmapWriter("test.png")

    called = {}

    def fake_save(filename):
        called["filename"] = filename

    monkeypatch.setattr(w.image, "save", fake_save)

    w.write()

    assert called["filename"] == "test.png"



def test_new_resets_image():
    w = BitmapWriter("test.png", size=(0, 0, 100, 100))

    old_image = w.image

    w.new("new.png", size=(0, 0, 200, 200))

    assert w.filename == "new.png"
    assert w.size == (0, 0, 200, 200)
    assert w.image.size == (200, 200)
    assert w.image is not old_image

