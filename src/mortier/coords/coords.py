import copy
import math

import numpy as np


class Coords:
    def __init__():
        self.x = 0
        self.y = 0

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
        new_c = copy.copy(self)
        new_c.x = -self.y
        new_c.y = self.x
        return new_c

    def to_euclidean(self):
        pass
