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

    def in_bounds(self, f):
        for v in f.vertices:
            if 0 > v.x or v.x > self.size[0] or 0 > v.y or v.y > self.size[1]:
                return False
        return True

    def set_label(self, label):
        pass

    def set_caption(self, caption):
        pass

    def new(self, filename, size = None, n_tiles = None):
        pass
