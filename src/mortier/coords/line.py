from mortier.coords.coords import Coords
from .euclidean_coords import EuclideanCoords 

import math
import numpy as np
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


