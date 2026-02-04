import numpy as np

from mortier.coords.coords import Coords


class EuclideanCoords(Coords):
    def __init__(self, p):
        self.x = p[0]
        self.y = p[1]
        # TODO: Return x,y as tuple for easy access

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
        return np.sqrt(self.x**2 + self.y**2)

    def normalise(self):
        return EuclideanCoords([self.x / self.len(), self.y / self.len()])

    def rotate(self, angle):
        x_rotated = self.x * np.cos(angle) - self.y * np.sin(angle)
        y_rotated = self.x * np.sin(angle) + self.y * np.cos(angle)
        return EuclideanCoords([x_rotated, y_rotated])

    def rotate_around(self, dx, dy, angle):
        x_rotated = (
            ((self.x - dx) * np.cos(angle)) - ((self.y - dy) * np.sin(angle)) + dx
        )
        y_rotated = (
            ((self.x - dx) * np.sin(angle)) + ((self.y - dy) * np.cos(angle)) + dy
        )
        return EuclideanCoords([x_rotated, y_rotated])

    def toEuclidean(self):
        return self
