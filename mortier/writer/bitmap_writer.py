from .writer import Writer 
from PIL import Image, ImageDraw
import numpy as np

class BitmapWriter(Writer):
    def __init__(self, filename, size, n_tiles = 1):
        super().__init__(filename, size, n_tiles)
        self.image = Image.new("RGB", (size[2], size[3]))
        self.output = ImageDraw.Draw(self.image)
        
    def point(self, p):
        self.output.point((p.x, p.y))

    def line(self, p0, p1, fill = (255, 255, 255)):
        #if not self.in_bounds(p0) or not self.in_bounds(p1):
        #    return
        self.output.line([(p0.x, p0.y), (p1.x, p1.y)], fill = fill)

    def face(self, face, dotted = False):
        t = []
        
        
        if dotted:
            fill = (255, 0, 0)
        else:
            fill = (255, 255, 255)
        
        for i in range(len(face.vertices)):
            self.line(face.vertices[i], face.vertices[(i + 1) % len(face.vertices)], fill = fill)
            #self.point(face.vertices[i])
            #self.point(face.vertices[(i + 1) % len(face.vertices)])

    def write(self):
        self.image.save(self.filename) 

    def new(self, filename, size = None, n_tiles = None):
        if not size:
            size = self.size
        if not n_tiles:
            n_tiles = self.n_tiles
        super().__init__(filename, size, n_tiles)
        self.image = Image.new("RGB", (size[2], size[3]))
        self.output = ImageDraw.Draw(self.image)
