import math
class Writer():
    def __init__(self, filename, size, n_tiles = 1):
        self.filename = filename
        self.n_tiles = int(n_tiles)
        self.size = size

    def point(self, p):
        pass

    def line(self, p0, p1):
        pass

    def face(self, face, dotted = False):
        pass

    def in_bounds(self, v):
        
        if math.isnan(v.x) or math.isnan(v.y) or math.isinf(v.x) or math.isinf(v.y):
            return False
        if not (self.size[0] < v.x < self.size[0] + 1.1 * self.size[2] and self.size[1] < v.y < self.size[1] + self.size[3]):
            return False
        return True

    def set_label(self, label):
        pass

    def set_caption(self, caption):
        pass

    def new(self, filename, size = None, n_tiles = None):
        pass
