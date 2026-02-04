import numpy as np
from hypertiling import HyperbolicTiling
from hypertiling.graphics.plot import convert_polygons_to_patches, plot_tiling

from mortier.coords import EuclideanCoords
from mortier.face.face import Face
from mortier.tesselation.tesselation import Tesselation
from mortier.utils.math_utils import map_num


class HyperbolicTesselation(Tesselation):
    def __init__(self, writer, p, q, n_layers = 7, angle = None):
        super().__init__(writer)
        self.p = p
        self.q = q
        self.tess_id = f"{p}-gone, {q}-voisins"
        self.n_layers = n_layers 
        self.T = HyperbolicTiling(self.p, self.q, self.n_layers, kernel = "SRS")
        self.faces = []
        self.angle = angle
        self.scale = min(self.writer.size[3], self.writer.size[2])/2
        self.refine_level = 0
        self.half_plane = False
        self.draw_unit_circle = False

    def set_scale(self, scale):
        self.scale = min(self.writer.size[3], self.writer.size[2])/2 * scale

    def convert_to_half_plane(self):
        faces = []
        for f in self.faces:
            faces.append(f.half_plane())
        self.faces = faces

    def set_draw_unit_circle(self, draw):
        self.draw_unit_circle = draw

    def refine_tiling(self, iterations):
        self.T.refine_lattice(iterations)
        self.tesselate_face()

    def tesselate_face(self):
        #Extract faces from a Matplotlib polygoncollection
        z_point = EuclideanCoords([self.writer.size[2]/2, self.writer.size[3]/2])
        pgoncollec = convert_polygons_to_patches(self.T)
        faces = []
        for polygon in self.T:
            u = polygon[1:]
            v = [EuclideanCoords([p.real, p.imag]) for p in u]
            f = Face(v)
            self.faces.append(f)

        if self.half_plane:
            self.convert_to_half_plane()
            z_point = EuclideanCoords([self.writer.size[2]/2, 0])

        for f in self.faces:
            f = f.scale(self.scale).translate(z_point)
            faces.append(f)
        self.faces = faces 
