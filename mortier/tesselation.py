from coords import LatticeCoords, EuclideanCoords
from math_utils import in_bounds, planeToTileCoords, planeCoords
from face import Face
import math
import random

class Tesselate():
    def __init__(self, writer, tess, tess_id):
        self.writer = writer
        self.tess = tess
        self.tess_id = tess_id
        self.wpow = []

        self.wpow.append(LatticeCoords([1, 0, 0, 0]))
        self.wpow.append(LatticeCoords([0, 1, 0, 0]))
        self.wpow.append(LatticeCoords([0, 0, 1, 0]))
        self.wpow.append(LatticeCoords([0, 0, 0, 1]))
        self.wpow.append(LatticeCoords([-1, 0, 1, 0]))
        self.wpow.append(LatticeCoords([0, -1, 0, 1]))
        self.wpow.append(LatticeCoords([-1, 0, 0, 0]))
        self.wpow.append(LatticeCoords([0, -1, 0, 0]))
        self.wpow.append(LatticeCoords([0, 0, -1, 0]))
        self.wpow.append(LatticeCoords([0, 0, 0, -1]))
        self.wpow.append(LatticeCoords([1, 0, -1, 0]))
        self.wpow.append(LatticeCoords([0, 1, 0, -1]))
        
        self.set_tesselation(tess, tess_id)
        self.faces = self.tesselate()

        self.show_dual = False
        self.show_face = False
        self.show_base = False
        self.ray_tesselation = False

    def use_ray(self, use_ray):
        self.ray_tesselation = use_ray

    def fill_neighbor(self, faces):
        vertex_map = {}
        for face in faces:
            for v in face.vertices:
                if v in vertex_map:
                    vertex_map[v].append(face)
                else:
                    vertex_map[v] = [face]
        for v in vertex_map.keys():
            for f in vertex_map[v]:
                f.add_neigbors(vertex_map[v])

    def draw_seed(self):
        self.writer.face(self.cell, dotted = True)

        for s in self.seed:
            s = LatticeCoords(s)
            self.writer.point(s)

        caption = f"Cellule et Graines du pavage ${self.tess_id}$"
        label = f"seed"

        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write(caption, label)
            
    def draw_star(self):
        neighbor_arr = {}
        
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]: 
                f_ = self.cell.translate(self.T1, self.T2, x, y) 

                self.writer.face(f_, dotted = True)

                for s in self.seed: 
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1 
                    self.writer.point(p)
                    self.writer.point(s)

        for s in self.seed:
          s = LatticeCoords(s)

          for k in range(6):
            p = self.wpow[k];
            sk = s.translate(p)
            if str(sk.w) in neighbor_arr:
                self.writer.line(s, sk)
                self.writer.point(sk)

        caption = f"Graphe Étoile du pavage {self.tess_id}"
        label = f"star"
        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write()

    def draw_edge(self):
        neighbor_arr = {}

        self.writer.face(self.cell, dotted = True)
        
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]: 
                for s in self.seed: 
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1 

        for s in self.seed:
          s = LatticeCoords(s)

          for k in range(6):
            p = self.wpow[k];
            sk = s.translate(p)
            if str(sk.w) in neighbor_arr:
                self.writer.line(s, sk)

        caption = f"Squelette du pavage {self.tess_id} construit avec le voisinage immédiat"
        label = "edge"
        
        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write()

    def tesselate(self):
        neighbor_arr = {}

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for s in self.seed: 
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1 

        faces = []
        for s in self.seed:
          s = LatticeCoords(s)
          S = []

          for k in range(6):
            p = self.wpow[k];
            sk = s.translate(p)
            if str(sk.w) in neighbor_arr:
                S.append(k)

          for i in range(len(S) - 1):
            h = 6 - (S[i+1]-S[i]);
            m = 12/h;
            faces.append(Face.generate(s, S[i], m))
        
        self.fill_neighbor(faces)
        return faces
    
    def find_corners(self):
        W = [1, 
             0.8660254037844386 + 0.5* 1j,
             0.5 +  0.8660254037844386 * 1j,
             0 + 1j
         ]

        i_min = 1000
        i_max = -1000
        j_min = 1000
        j_max = -1000
        corners = [0, 
                   self.writer.size[0],
                   self.writer.size[1] * 1j,
                   (self.writer.size[0] + self.writer.size[1] * 1j)]
        lines = []

        for z in corners: 
            z_ = planeToTileCoords(self.tess, W, 
                                   z.real/self.writer.n_tiles, 
                                   z.imag/self.writer.n_tiles)

            i_min = min(i_min, z_.real)
            j_min = min(j_min, z_.imag)
            i_max = max(i_max, z_.real)
            j_max = max(j_max, z_.imag)

        i_min = math.floor(i_min - 2)
        i_max = math.ceil(i_max + 2)
        j_min = math.floor(j_min - 2)
        j_max = math.ceil(j_max + 2)
        
        return i_min, i_max, j_min, j_max
    
    def draw_tesselation(self, angle = None):
        faces = self.tesselate()
        i_min, i_max, j_min, j_max = self.find_corners()
        if self.show_base:
            i_min = -1
            i_max =  2
            j_min = -1
            j_max =  2

        for i in range(i_min, i_max): 
            for j in range(j_min, j_max): 
                if self.show_base:
                    f_ = self.cell.translate(self.T1, self.T2, i, j) 
                    self.writer.face(f_, dotted = True)

                for f in faces:
                    f_ = f.translate(self.T1, self.T2, i, j)
                    f_ = f_.scale(self.writer.n_tiles)
                    f_ = f_.ray_transform(angle)
                    self.writer.face(f_)

        caption = f"Pavage ${self.tess_id}$" 
        label = f"finished_{self.tess_id}"

        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        self.writer.write()
    

    def set_tesselation(self, tess, tess_id):
        self.tess = tess
        self.tess_id = tess_id
        self.T0 = LatticeCoords([0, 0, 0, 0])
        self.T1 = LatticeCoords(tess["T1"])
        self.T2 = LatticeCoords(tess["T2"])
        self.T3 = self.T1.translate(self.T2)
        self.seed = self.tess["Seed"]
        self.cell = Face([self.T0, self.T1, self.T3, self.T2])

    def set_writer(self, writer):
        self.writer = writer
