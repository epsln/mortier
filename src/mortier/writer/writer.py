import math
import numpy as np
from mortier.coords import EuclideanCoords
from mortier.enums import HatchType 
from mortier.utils.geometry import outline_lines, fill_intersect_points, quadratic_bezier 

from hypertiling.graphics.plot import geodesic_arc

class Writer():
    def __init__(self, filename, size = (0, 0, 1920, 1080), n_tiles = 1, lacing_mode = False, lacing_angle = False, bands_mode = False, bands_width = 10, bands_angle = 0):
        self.filename = filename
        self.n_tiles = int(n_tiles)
        self.size = size
        self.intersect_points = {}
        self.lacing_mode = lacing_mode 
        self.bands_mode = bands_mode
        self.bands_width = bands_width 
        self.bands_angle = bands_angle 
        self.bezier_curve = False 
        self.color_line = (255, 255, 255)
        self.color_bg   = (0, 0, 0)
        self.hatch_fill_parameters = {"angle": None, "spacing": 5, 
                                      "crosshatch": False, "type": None, "color": self.color_line} 
        assert not (self.bezier_curve and self.hatch_fill_parameters["angle"])
        assert not (self.lacing_mode and self.bands_mode)

    def set_band_angle(self, bands_angle):
        self.bands_angle = bands_angle

    def set_hatch_fill(self, hatch_fill_parameters):
        assert not (self.bezier_curve and hatch_fill_angle["angle"])
        self.hatch_fill_parameters = hatch_fill_parameters

    def hatch_fill(self, vertices, cross_hatch = False):
        lines = []
        angle = self.hatch_fill_parameters["angle"]
        if cross_hatch:
            angle += np.pi/2
        
        vertices_rotated = [v.rotate(-angle) for v in vertices]
        ys = [v.y for v in vertices_rotated]
        y_min, y_max = min(ys), max(ys)


        y = y_min + self.hatch_fill_parameters["spacing"] 
        while y < y_max:
            xs = []

            for j in range(len(vertices_rotated)):
                p0 = vertices_rotated[j]
                p1 = vertices_rotated[(j + 1) % len(vertices_rotated)]

                if p0.y == p1.y:
                    continue

                if (p0.y <= y < p1.y) or (p1.y <= y < p0.y):
                    t = (y - p0.y) / (p1.y - p0.y)
                    x = p0.x + t * (p1.x - p0.x)
                    xs.append(x)

            xs.sort()

            for k in range(0, len(xs), 2):
                if k + 1 >= len(xs):
                    continue

                x0, x1 = xs[k], xs[k + 1]

                if not self.hatch_fill_parameters["type"] == HatchType.DOT:
                    a = EuclideanCoords([x0, y]).rotate(angle)
                    b = EuclideanCoords([x1, y]).rotate(angle)
                    self.line(a, b, self.hatch_fill_parameters["color"])
                else:
                    x = x0 + self.hatch_fill_parameters["spacing"] / 2
                    while x < x1:
                        c = EuclideanCoords([x, y]).rotate(angle)
                        self.point(c, self.hatch_fill_parameters["color"])
                        x += self.hatch_fill_parameters["spacing"] 

            y += self.hatch_fill_parameters["spacing"]

    def draw_outline_lines(self, points):
        pos_ring, neg_ring = outline_lines(points, self.intersect_points, self.bands_width, self.bands_angle, self.bands_mode)
        
        for i in range(0, len(pos_ring) - 1, 2):
            p0 = pos_ring[i]
            p1 = pos_ring[i + 1]
            p2 = pos_ring[(i + 2) % len(pos_ring)]
            
            if self.bezier_curve:
                l = quadratic_bezier(p0, p1, p2)
                for j in range(len(l)- 1):
                    self.line(l[j], l[j + 1], self.color_line) 
            else:
                self.line(p0, p1, self.color_line)
                self.line(p1, p2, self.color_line)
            
        for i in range(0, len(neg_ring) - 2, 3):
            p0 = neg_ring[i]
            p1 = neg_ring[i + 1]
            p2 = neg_ring[i + 2]
            
            if self.bezier_curve:
                l = self.quadratic_bezier(p0, p1, p2)
                for j in range(len(l) - 1):
                    self.line(l[j], l[j + 1], self.color_line) 
            else:
                self.line(p0, p1, self.color_line)
                self.line(p1, p2, self.color_line)

        return pos_ring

    def circle(self, c, r, color = (255, 255, 255)):
        pass

    def point(self, p, color = (255, 255, 255)):
        pass

    def line(self, p0, p1, color = (255, 255, 255)):
        pass

    def draw_bezier_curves(self, face):
        for i in range(0, len(face.vertices) - 2, 2):
            p0 = face.vertices[i] 
            p1 = face.vertices[i + 1] 
            p2 = face.vertices[i + 2] 
            l = self.quadratic_bezier(p0, p1, p2)
            for j in range(len(l) - 1):
                self.line(l[j], l[j + 1]) 
 
    def face(self, face, dotted = False):
        t = []
        pattern = ""
        n_vert = len(face.vertices)

        fill_intersect_points(face, self.intersect_points)
        inside_vertices = face.vertices

        if self.lacing_mode or self.bands_mode:
            inside_vertices = self.draw_outline_lines(face.vertices)
        else:
            if self.bezier_curve:
                self.draw_bezier_curves(face)
            else:
                for i in range(len(face.vertices)):
                    self.line(face.vertices[i], face.vertices[(i + 1) % len(face.vertices)], self.color_line)
        if self.hatch_fill_parameters["type"] is not None:
            self.hatch_fill(inside_vertices)
            if self.hatch_fill_parameters["crosshatch"]:
                self.hatch_fill(inside_vertices, self.hatch_fill_parameters["crosshatch"])

    def in_bounds(self, v):
        if math.isnan(v.x) or math.isnan(v.y) or math.isinf(v.x) or math.isinf(v.y):
            return False
        if not (self.size[0] < v.x < self.size[0] + self.size[2] and self.size[1] < v.y < self.size[1] + self.size[3]):
            return False
        return True

    def set_label(self, label):
        pass

    def set_caption(self, caption):
        pass

    def set_color_bg(self, color):
        pass

    def new(self, filename, size = None, n_tiles = None):
        pass
