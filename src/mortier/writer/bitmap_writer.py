from mortier.writer.writer import Writer 
from mortier.coords import EuclideanCoords
from PIL import Image, ImageDraw
import random
import numpy as np

class BitmapWriter(Writer):
    def __init__(self, filename, size = (0, 0, 1920, 1080), n_tiles = 100, lacing_mode = False, lacing_angle = False, bands_mode = False, bands_width = 10, bands_angle = 0):
        super().__init__(filename, size, n_tiles, lacing_mode, bands_angle, bands_mode, bands_width)
        self.image = Image.new("RGB", (size[2], size[3]))
        self.output = ImageDraw.Draw(self.image)
       
    def point(self, p, color = (255, 255, 255)):
        self.output.point((p.x, p.y), color = color)

    def arc(self, bbox, start, end):
        self.output.arc(bbox, start = start, end = end)

    def circle(self, c, r, color = (255, 255, 255)):
        p0 = (c.x - r, c.y - r)
        p1 = (c.x + r, c.y + r)
        plist = [p0, p1]
        self.output.ellipse(plist, outline=color)

    def line(self, p0, p1, color = (255, 255, 255)):
        if color == "red":
            color = (255, 0, 0)
        if color == "green":
            color = (0, 255, 0)
        if color == "green":
            color = (0, 0, 255)
        if color == "cyan":
            color = (0, 128, 200)
        if color == "cyan":
            color = (255, 227, 0)
        self.output.line([(p0.x, p0.y), (p1.x, p1.y)], fill = color, width = 1)

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
