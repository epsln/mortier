from coords import LatticeCoords, EuclideanCoords, Line
import numpy as np

class Face():
    def __init__(self, vertices, barycenter = None):
        self.vertices = vertices
        self.barycenter = barycenter 
        self.neighbors = []

    @staticmethod
    def generate(v, k, m): 
        wpow = []
        wpow.append(LatticeCoords([1, 0, 0, 0]))
        wpow.append(LatticeCoords([0, 1, 0, 0]))
        wpow.append(LatticeCoords([0, 0, 1, 0]))
        wpow.append(LatticeCoords([0, 0, 0, 1]))
        wpow.append(LatticeCoords([-1, 0, 1, 0]))
        wpow.append(LatticeCoords([0, -1, 0, 1]))
        wpow.append(LatticeCoords([-1, 0, 0, 0]))
        wpow.append(LatticeCoords([0, -1, 0, 0]))
        wpow.append(LatticeCoords([0, 0, -1, 0]))
        wpow.append(LatticeCoords([0, 0, 0, -1]))
        wpow.append(LatticeCoords([1, 0, -1, 0]))
        wpow.append(LatticeCoords([0, 1, 0, -1]))

        vertices = [v, v.translate(wpow[k])]
        
        for i in range(2, int(m)): 
          k = int((k + 12/m) % 12)
          vertices.append(vertices[i - 1].translate(wpow[k]))

        k = int(k)
        if m == 3: #Triangle
            d = v.translate(wpow[k + 1].scale(1/3))    
        if m == 4: #Quad
            d = v.translate(wpow[k].translate(wpow[k].translate(wpow[k + 3])).scale(1/2))
        if m == 6: #Hexagon
            d = v.translate(wpow[k + 2])
        if m == 12: #Dodecagon
            d = v.translate(wpow[(k + 2) % len(wpow)].translate(wpow[(k + 3) % len(wpow)]))

        return Face(vertices, d) 

    def translate(self, T1, T2, i, j):
      vertices = []
      TI  = T1.scale(i)
      TIJ = TI.translate(T2.scale(j))
      for v in self.vertices:
          vertices.append(v.translate(TIJ))

      if self.barycenter:
          b = self.barycenter.translate(TIJ)
          return Face(vertices, b)
      else:
          return Face(vertices)

    def scale(self, n):
      vertices = []
      for v in self.vertices:
          vertices.append(v.scale(n))

      if self.barycenter:
          b = self.barycenter.scale(n)
          return Face(vertices, b)
      else:
          return Face(vertices)

    def add_neigbors(self, face):
        self.neighbors = [f for f in face if f.vertices != self.vertices]

    def ray_transform(self, angle):
        #TODO: Create line class and move midpoint logic in there
        vertices = []

        for i in range(len(self.vertices)):
            #TODO: Put sides in faces instead of using vertices
            p0 = self.vertices[i]
            p1 = self.vertices[(i + 1) % len(self.vertices)]
            p2 = self.vertices[(i + 2) % len(self.vertices)]

            side_0 = Line(p0, p1)
            side_1 = Line(p1, p2)

            p_mid_0 = side_0.get_midpoint()
            p_mid_1 = side_1.get_midpoint() 

            angle_0 = side_0.heading() + angle
            angle_1 = side_1.heading() - angle

            end_pt_0 = EuclideanCoords([np.cos(angle_0),  np.sin(angle_0)]) 
            end_pt_1 = EuclideanCoords([np.cos(angle_1), np.sin(angle_1)]) 

            end_pt_0 = p_mid_0.translate(end_pt_0)
            end_pt_1 = p_mid_1.translate(end_pt_1)

            s0 = EuclideanCoords([p_mid_0.x - end_pt_0.x, p_mid_0.y - end_pt_0.y])
            s1 = EuclideanCoords([p_mid_1.x - end_pt_1.x, p_mid_1.y - end_pt_1.y])

            s = (-s0.y * (p_mid_0.x - p_mid_1.x) + s0.x * (p_mid_0.y - p_mid_1.y)) / (-s1.x * s0.y + s0.x * s1.y)
            t = ( s1.x * (p_mid_0.y - p_mid_1.y) - s1.y * (p_mid_0.x - p_mid_1.x)) / (-s1.x * s0.y + s0.x * s1.y)
            
            x = EuclideanCoords([p_mid_0.x + (t * s0.x), p_mid_0.y + (t * s0.y)])

            vertices.append(p_mid_0)
            vertices.append(x)

        return Face(vertices)
            
    def __str__(self):
      t = []
      for v in self.vertices:
        t.append(f"({round(v.x, 2)},{round(v.y, 3)})")
      return '->'.join(t)

