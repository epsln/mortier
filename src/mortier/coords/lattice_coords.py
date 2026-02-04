import numpy as np

from mortier.coords import Coords
from mortier.coords.euclidean_coords import EuclideanCoords


class LatticeCoords(Coords):
    def __init__(self, w):
        self.w = []
        self.w.append(w[0])
        self.w.append(w[1])
        self.w.append(w[2])
        self.w.append(w[3])

        self.x = w[0] + 0.5 * 3**0.5 * w[1] + 0.5 * w[2]
        self.y = 0.5 * w[1] + 0.5 * 3**0.5 * w[2] + w[3]

    def translate(self, wc):
        c = [(w_ + wc_) for w_, wc_ in zip(self.w, wc.w)]
        return LatticeCoords(c)

    def scale(self, k):
        c = [(w_ * k) for w_ in self.w]
        return LatticeCoords(c)

    def sum(self):
        return sum(self.w)

    def rotate(self, angle):
        x_rotated = self.x * np.cos(angle) - self.y * np.sin(angle)
        y_rotated = self.x * np.sin(angle) + self.y * np.cos(angle)
        return EuclideanCoords([x_rotated, y_rotated])

    def to_euclidean(self):
        return EuclideanCoords([self.x, self.y])
