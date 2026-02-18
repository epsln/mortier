import pytest
import json
import random

from mortier.coords import LatticeCoords
from mortier.face.face import Face
from mortier.tesselation.regular_tesselation import RegularTesselation
from mortier.writer import BitmapWriter, SVGWriter, TikzWriter

with open("data/database.json", "r") as file:
    js = json.load(file)

class MockWriter:
    def __init__(self):
        self.calls = []
        self.size = (0, 0, 100, 100)
        self.n_tiles = 50
        self.ornements = None

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

@pytest.mark.benchmark
def test_tesselate_face_bench(tessellation):
    tess, writer = tessellation
    tess.find_corners = lambda: (-5, 5, -5, 5)
    tess.tesselate_face()

@pytest.mark.benchmark
def test_draw_tesselation_bench():
    output_size = (1080, 1080)  
    writer = MockWriter()
    writer.size = (0, 0, 1080, 1080)
    tess_dict = js['PU_4']

    tess = RegularTesselation(writer, tess_dict, "TestTess")
    tess.draw_tesselation()

@pytest.mark.benchmark
def test_draw_tesselation_angled_bench():
    output_size = (1080, 1080)  
    writer = MockWriter()
    writer.size = (0, 0, 1080, 1080)
    tess_dict = js['PU_4']

    tess = RegularTesselation(writer, tess_dict, "TestTess")
    tess.set_angle(0.3)
    tess.draw_tesselation()


