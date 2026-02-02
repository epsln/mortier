import math
import numpy as np

class Coords:
  def translate(self, wc):
      pass

  def scale(self, k):
      pass

  def sum(self):
      pass


  def angle(self):
      return math.atan2(self.y, self.x) 

  def numpy(self):
      return np.array([self.x, self.y])

  def __str__(self):
      return f"{np.round(self.x, 2)}, {np.round(self.y, 2)}" 

  def normal(self):
      return EuclideanCoords([-self.y, self.x])

  def toEuclidean(self):
      return EuclideanCoords([self.x, self.y])
  
class LatticeCoords(Coords):
  def __init__(self, w): 

    self.w = []
    self.w.append(w[0]) 
    self.w.append(w[1]) 
    self.w.append(w[2]) 
    self.w.append(w[3]) 

    self.x = w[0] + 0.5 * 3**0.5 * w[1] + 0.5 * w[2]; 
    self.y = 0.5 * w[1] + 0.5 * 3**0.5 * w[2] + w[3]; 
    #TODO: Return x,y as tuple for easy access
  
  def translate(self, wc):
    c = [(w_ + wc_) for w_, wc_ in zip(self.w, wc.w)]
    return LatticeCoords(c) 

  def scale(self, k):
    c = [(w_ * k) for w_ in self.w]
    return LatticeCoords(c) 

  def sum(self):
      return sum(self.w)

class EuclideanCoords(Coords):
  def __init__(self, p): 
    self.x = p[0] 
    self.y = p[1] 
    #TODO: Return x,y as tuple for easy access

  def isclose(self, p):
      if abs(self.x - p.x) < 0.0001 and abs(self.y - p.y) < 0.0001:
          return True
      else:
          return False
  
  def translate(self, wc):
    return EuclideanCoords([self.x + wc.x, self.y + wc.y]) 

  def scale(self, k):
    return EuclideanCoords([self.x * k, self.y * k]) 

  def sum(self):
      return self.x + self.y 

  def heading(self):
      return np.atan2(self.y, self.x) % np.pi

  def len(self):
      return np.sqrt(self.x ** 2 + self.y ** 2) 

  def normalise(self):
      return EuclideanCoords([self.x/self.len(), self.y/self.len()])

  def rotate(self, angle):
    x_rotated = self.x * np.cos(angle) - self.y * np.sin(angle)
    y_rotated = self.x * np.sin(angle) + self.y * np.cos(angle)
    return EuclideanCoords([x_rotated, y_rotated])

  def rotate_around(self, dx, dy, angle):
    x_rotated = ((self.x - dx) * np.cos(angle)) - ((self.y - dy) * np.sin(angle)) + dx
    y_rotated = ((self.x - dx) * np.sin(angle)) + ((self.y - dy) * np.cos(angle)) + dy
    return EuclideanCoords([x_rotated, y_rotated])

class Line(Coords):
  def __init__(self, p0, p1):
      self.beg_pt = p0
      self.end_pt = p1
      self.vec = p1.translate(p0.scale(-1))
  
  def heading(self):
      return np.atan2(self.vec.y, self.vec.x)
  
  def len(self):
      return self.vec.len() 
  
  def get_midpoint(self):
      return self.beg_pt.translate(self.end_pt).scale(1/2).toEuclidean()
  
  def get_pq_point(self, p, q ):
      x = self.beg_pt.x + p * (self.end_pt.x - self.beg_pt.x)/q
      y = self.beg_pt.y + p * (self.end_pt.y - self.beg_pt.y)/q
      return EuclideanCoords([x, y])
  
  def heading(self):
    return np.atan2(self.vec.y, self.vec.x) % np.pi

  def translate(self, wc):
    return Line(self.beg_pt.translate(wc), self.end_pt.translate(wc)) 

  def scale(self, k):
    return Line(self.beg_pt.scale(k), self.end_pt.scale(k)) 

  def rotate_around(self, x, y, theta):
      p0 = self.beg_pt.rotate_around(x, y, theta)
      p1 = self.beg_pt.rotate_around(x, y, theta)
      return Line(p0, p1)

  def __str__(self):
      return f"{self.beg_pt}->{self.end_pt}" 


