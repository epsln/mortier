from coords import LatticeCoords, EuclideanCoords, Line
from math_utils import in_bounds, planeToTileCoords, planeCoords
from face import P3Penrose, P2Penrose, Face
import numpy as np
import math
import random

class Penrose():
    def __init__(self, writer, tile = "P2", level = 7):
        self.writer = writer
        self.level = level
        self.tile = tile
        if tile == "P2":
            self.pen = P2Penrose.initialise(0)
        else:
            self.pen = P3Penrose.initialise(0)
    
    def draw_n_ray(self, n_iter, angle = np.random.uniform(0, np.pi/2), sin = False, assym = False, separated_site = False, skip_face = False):
        for i in range(self.level):
            triangle = []
            for p in self.pen:
                triangle.extend(p.inflate())
            self.pen = triangle   

        if angle:
            for i, p in enumerate(self.pen):
                for p_ in self.pen[i + 1:] :
                    if (p.A.isclose(p_.A) and p.C.isclose(p_.C)) or (p.A.isclose(p_.C) and p.C.isclose(p_.A)): 
                        vertices = [p.A, p.B, p.C, p_.B]
                        s = 0
                        for i in range(4):
                            s += (vertices[(i + 1)%4].x - vertices[i].x)/(vertices[(i + 1) % 4].y + vertices[i].y)
                        if s < 0:
                            vertices = vertices[::-1]
                        f = Face(vertices)

                        #f_ = f.ray_transform(angle).scale(1.8).translate_euclidean(EuclideanCoords([-800, -950]))
                        f_ = f.ray_transform(angle, assym = assym, sin = sin, separated_site = separated_site)
                        #f_ = f_.rotate(x/(30 * 10) * 2 * np.pi, 0)
                        self.writer.face(f_)
                        break

        else:
            for p in self.pen:
                for l in p.edges:
                    self.writer.line(l.beg_pt, l.end_pt)
                self.writer.line(l.beg_pt, l.end_pt)
                        
        caption = f"Pavage ${self.tile}$" 
        if assym: 
            caption += ", angles assymétrique"
        if sin:
            caption += ", angle paramétrisé"
        if separated_site:
            caption += ", site séparé"
        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write()
