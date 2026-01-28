from coords import EuclideanCoords
from math_utils import map_num
from face import Face

import matplotlib.pyplot as plt
import numpy as np
from hypertiling import HyperbolicTiling
from hypertiling.graphics.plot import plot_tiling, convert_polygons_to_patches

class HyperbolicTesselate:
    def __init__(self, writer, p, q, n_layers = 5):
        self.writer = writer
        self.p = p
        self.q = q
        self.n_layers = 5
        self.T = HyperbolicTiling(self.p, self.q, self.n_layers)
        self.fig = plt.figure(figsize=(8,8), dpi = 300)
        self.figname = "hypertest.png"
        self.faces = self.extract_faces()

    def extract_faces(self):
        #Extract faces from a Matplotlib polygoncollection
        pgoncollec = convert_polygons_to_patches(self.T)
        faces = []
        for polygon in self.T:
            u = polygon[1:]
            v = [EuclideanCoords([map_num(p.real, -1, 1, 0, self.writer.size[2]), 
                                  map_num(p.imag, -1, 1, 0, self.writer.size[3])]) for p in u]
            faces.append(Face(v))
        return faces

    def draw_tesselation(self, frame_num = 0): 
        for f in self.faces:
            self.writer.face(f)
        self.writer.write()

