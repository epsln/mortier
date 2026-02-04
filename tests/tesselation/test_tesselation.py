import pytest
from mortier.coords import EuclideanCoords
from mortier.face.face import Face
from mortier.tesselation.tesselation import Tesselation

class MockWriter:
    def __init__(self):
        self.calls = []
        self.size = (0, 0, 100, 100)
        self.lacing_mode = False
        self.bands_mode = False
        self._band_angle = None

    def face(self, face, dotted=False):
        self.calls.append(("face", face, dotted))

    def circle(self, center, radius):
        self.calls.append(("circle", center, radius))

    def set_caption(self, caption):
        self.calls.append(("caption", caption))

    def set_label(self, label):
        self.calls.append(("label", label))

    def write(self):
        self.calls.append(("write",))
        return "output"

    def set_band_angle(self, angle):
        self._band_angle = angle
        self.calls.append(("band_angle", angle))


def test_state_setters():
    writer = MockWriter()
    tess = Tesselation(writer)

    tess.set_param_mode("sin")
    assert tess.param_mode == "sin"

    tess.set_angle(0.5)
    assert tess.angle == 0.5
    assert writer._band_angle == 0.5

    tess.set_assym_angle(0.7)
    assert tess.assym_angle == 0.7

    tess.set_show_underlying(True)
    assert tess.show_underlying is True

    tess.set_separated_site_mode(True)
    assert tess.separated_site_mode is True


def test_draw_tesselation_basic():
    writer = MockWriter()
    tess = Tesselation(writer)

    # override methods to add dummy faces
    tess.tesselate_face = lambda: setattr(tess, "faces", [Face([EuclideanCoords([0, 0]), EuclideanCoords([1, 0]), EuclideanCoords([1, 1])])])
    tess.draw_cell = lambda: writer.calls.append(("draw_cell",))

    tess.show_base = True
    tess.show_underlying = True
    tess.angle = 0.1
    tess.separated_site_mode = True
    tess.param_mode = "sin"
    tess.writer.lacing_mode = True
    tess.writer.bands_mode = True
    tess.tile = "TileA"

    output = tess.draw_tesselation(frame_num=0)

    # writer.write() should have been called and output returned
    assert output == "output"
    assert any(call[0] == "face" for call in writer.calls)
    assert any(call[0] == "caption" for call in writer.calls)
    assert any(call[0] == "label" for call in writer.calls)

    # check caption contains all active flags
    caption_call = next(call[1] for call in writer.calls if call[0] == "caption")
    assert "TileA" in caption_call
    assert "sites séparés" in caption_call
    assert "angle paramétrisé (sinus)" in caption_call
    assert "entrelacements" in caption_call
    assert "bandeaux" in caption_call

    # draw_cell should have been called
    assert ("draw_cell",) in writer.calls


def test_draw_tesselation_with_unit_circle():
    writer = MockWriter()
    tess = Tesselation(writer)
    tess.tesselate_face = lambda: None
    tess.draw_unit_circle = True
    tess.scale = 10

    tess.draw_tesselation()
    # check that a circle is drawn
    assert any(call[0] == "circle" for call in writer.calls)
    circle_call = next(call for call in writer.calls if call[0] == "circle")
    assert circle_call[2] == 10  # radius
