from mortier.coords import LatticeCoords, EuclideanCoords, Line
from mortier.utils.math_utils import in_bounds, planeToTileCoords, planeCoords
from mortier.face.face import P3Penrose, P2Penrose, Face
from mortier.tesselation.tesselation import Tesselation 

import numpy as np
import math
import random

class PenroseTesselation(Tesselation):
    def __init__(self, writer, tile = "P2", level = 8, sin_mode = False, assym = False, separated_site = False):
        super().__init__(writer, sin_mode, assym, separated_site_mode)
        self.level = level
        self.tile = tile
        if tile == "P2":
            self.pen = P2Penrose.initialise(0)
        else:
            self.pen = P3Penrose.initialise(0)
            
    def draw_tesselation(self):
        for i in range(self.level):
            triangle = []
            for p in self.pen:
                triangle.extend(p.inflate())
            self.pen = triangle   

        if self.angle:
            for i, p in enumerate(self.pen):
                for p_ in self.pen[i + 1:] :
                    if (p.A.isclose(p_.A) and p.C.isclose(p_.C)) or (p.A.isclose(p_.C) and p.C.isclose(p_.A)): 
                        vertices = [p.A, p.B, p.C, p_.B]
                        s = 0
                        for i in range(4):
                            s += (vertices[(i + 1)%4].x - vertices[i].x)/(vertices[(i + 1) % 4].y + vertices[i].y)
                        if s < 0:
                            vertices = vertices[::-1]
                        f = Face(vertices, sin_mode = self.sin_mode, assym_mode = self.assym_angle, separated_site_mode = self.separated_site_mode)
                        f_ = f.ray_transform(self.angle)
                        self.writer.face(f_, outline = False)
                        break

        else:
            for p in self.pen:
                for l in p.edges:
                    self.writer.line(l.beg_pt, l.end_pt)
                self.writer.line(l.beg_pt, l.end_pt)
                        
        caption = f"Pavage ${self.tile}$, avec $\\theta = {round(self.angle, 3)}$" 
        if self.separated_site_mode: 
            caption += ", sites séparés"
        if self.sin_mode:
            caption += ", angle paramétrisé"
        if self.assym_angle:
            caption += ", angle assymétrique"
        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write()
