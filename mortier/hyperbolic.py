from coords import EuclideanCoords
from math_utils import map_num
from face import Face
from tesselation import Tesselate 

import numpy as np
from hypertiling import HyperbolicTiling
from hypertiling.graphics.plot import plot_tiling, convert_polygons_to_patches

class HyperbolicTesselate(Tesselate):
    def __init__(self, writer, p, q, n_layers = 7, angle = None):
        self.writer = writer
        self.p = p
        self.q = q
        self.n_layers = n_layers 
        self.T = HyperbolicTiling(self.p, self.q, self.n_layers, kernel = "SRS")
        self.angle = angle
        #TODO: handle aspect ratio 
        self.scale = self.writer.size[2] / 2
        self.faces = self.extract_faces()
        self.draw_unit_circle = False

    def set_draw_unit_circle(self, draw):
        self.draw_unit_circle = draw

    def refine_tiling(self, iterations):
        self.T.refine_lattice(iterations)
        self.faces = self.extract_faces()

    def extract_faces(self):
        #Extract faces from a Matplotlib polygoncollection
        pgoncollec = convert_polygons_to_patches(self.T)
        faces = []
        for polygon in self.T:
            u = polygon[1:]
            v = [EuclideanCoords([p.real, p.imag]) for p in u]
            faces.append(Face(v))
        return faces

    def draw_tesselation(self, frame_num = 0): 
        z_point = EuclideanCoords([1, 1])
        for f in self.faces:
            f = f.translate_euclidean(z_point).scale(self.scale)
            if self.angle:
                f = f.ray_transform(self.angle, self.writer.size, frame_num)
            self.writer.face(f)
        if self.draw_unit_circle:
            self.writer.circle(EuclideanCoords([self.writer.size[2]/2, self.writer.size[3]/2]),
                               min(self.writer.size[2], self.writer.size[3])/2)
        self.writer.write()

