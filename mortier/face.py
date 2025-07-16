from coords import LatticeCoords, EuclideanCoords
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
        for i in range(len(self.vertices) - 1):
            p0 = self.vertices[i]
            p1 = self.vertices[i + 1]
            p2 = self.vertices[(i + 2) % len(self.vertices)]
            p_mid_0 = p0.translate(p1).scale(1/2).numpy()
            p_mid_1 = p1.translate(p2).scale(1/2).numpy()
            theta_0 = p1.translate(p0.scale(-1)).angle() + np.pi/2
            theta_1 = p2.translate(p1.scale(-1)).angle() + np.pi/2
            ray_0 = np.array([p_mid_0 + np.sin(angle + theta_0), p_mid_0 + np.cos(angle + theta_0)]).T
            ray_1 = np.array([p_mid_0 + np.sin(angle - theta_0), p_mid_0 + np.cos(angle - theta_0)]).T
            ray_2 = np.array([p_mid_1 + np.sin(angle + theta_1), p_mid_1 + np.cos(angle + theta_1)]).T
            ray_3 = np.array([p_mid_1 + np.sin(angle - theta_1), p_mid_1 + np.cos(angle - theta_1)]).T
            x, _, _= np.linalg.lstsq(np.array([ray_0, -ray_3]).T, p_mid_1 - p_mid_0)[:3]
            vertices.append(EuclideanCoords(p_mid_0))
            vertices.append(EuclideanCoords(ray_0 * x[0] + p_mid_0))
            x, _, _= np.linalg.lstsq(np.array([ray_1, -ray_2]).T, p_mid_1 - p_mid_0)[:3]
            vertices.append(EuclideanCoords(p_mid_1))
            print(p_mid_0, ray_0)
            vertices.append(EuclideanCoords(ray_2 * x[0] + p_mid_1))

        return Face(vertices)
            
    def __str__(self):
      t = []
      for v in self.vertices:
        t.append(f"({round(v.x, 2)},{round(v.y, 3)})")
      return '->'.join(t)

