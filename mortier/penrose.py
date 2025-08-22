from coords import LatticeCoords, EuclideanCoords, Line
from math_utils import in_bounds, planeToTileCoords, planeCoords
from face import P2Penrose, Face
import numpy as np
import math
import random

class Penrose():
    def __init__(self, writer):
        self.writer = writer
    
    def draw(self, level, angle, x):
        pen = P2Penrose.initialise(0) 
        for i in range(level):
            triangle = []
            for p in pen:
                triangle.extend(p.inflate())
            pen = triangle   

        print(x)
        for i, p in enumerate(pen):
            #for p_ in pen[i + 1:] :
            #    if p.A.isclose(p_.A) and p.C.isclose(p_.C): 
            #        vertices = [p.A, p.B, p.C, p_.B]
            #        s = 0
            #        for i in range(4):
            #            s += (vertices[(i + 1)%4].x - vertices[i].x)/(vertices[(i + 1) % 4].y + vertices[i].y)
            #        if s < 0:
            #            vertices = vertices[::-1]
            #        f = Face(vertices)

            #        f_ = f.ray_transform(angle).translate_euclidean(EuclideanCoords([-600, -650])).scale(1.5)
            #        #f_ = f_.rotate(x/(30 * 10) * 2 * np.pi, 0)
            #        self.writer.face(f_)
            #        break
            for l in p.edges:
                print(l)
                self.writer.line(l.beg_pt, l.end_pt)
                    
        self.writer.write()
