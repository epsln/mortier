import math

import numpy as np

from mortier.coords import EuclideanCoords
from mortier.enums import HatchType
from mortier.utils.geometry import (fill_intersect_points, outline_lines,
                                    quadratic_bezier)


class Writer:
    def __init__(
        self,
        filename,
        size=(0, 0, 1920, 1080),
        n_tiles=1,
    ):
        self.filename = filename
        self.n_tiles = int(n_tiles)
        self.size = size
        self.intersect_points = {}
        self.ornements = None
        self.hatching = None
        self.bezier = False
        self.color_line = (0, 0, 0)
        self.color_bg = (0, 0, 0)
        self.polygon_fill = {}
        assert not (self.bezier and self.hatching)

    def set_ornements(self, ornements):
        assert not (self.bezier and self.hatching)
        self.ornements = ornements

    def set_hatching(self, hatching):
        assert not (self.bezier and self.hatching)
        self.hatching = hatching

    def set_bezier(self, bezier):
        # TODO: Set the number of control points
        assert not (bezier and self.hatching)
        self.bezier = bezier

    def hatch_fill(self, vertices, cross_hatch=None):
        angle = self.hatching.angle
        if cross_hatch:
            angle += np.pi / 2

        vertices_rotated = [v.rotate(-angle) for v in vertices]
        ys = [v.y for v in vertices_rotated]
        y_min, y_max = min(ys), max(ys)

        y = y_min + self.hatching.spacing
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

                if not self.hatching.type == HatchType.DOT:
                    a = EuclideanCoords([x0, y]).rotate(angle)
                    b = EuclideanCoords([x1, y]).rotate(angle)
                    self.line(a, b, self.hatching.color)
                else:
                    x = x0 + self.hatching.spacing / 2
                    while x < x1:
                        c = EuclideanCoords([x, y]).rotate(angle)
                        self.point(c, self.hatching.color)
                        x += self.hatching.spacing

            y += self.hatching.spacing

    def draw_outline_lines(self, points):
        pos_ring, neg_ring = outline_lines(
            points, self.intersect_points, self.ornements
        )

        xy = []
        for i in range(0, len(pos_ring) - 1, 2):
            p0 = pos_ring[i]
            p1 = pos_ring[i + 1]
            p2 = pos_ring[(i + 2) % len(pos_ring)]

            xy.append(tuple(p0.numpy()))
            xy.append(tuple(p1.numpy()))
            xy.append(tuple(p2.numpy()))

            if self.bezier:
                lines = quadratic_bezier(p0, p1, p2)
                for j in range(len(lines) - 1):
                    self.line(lines[j], lines[j + 1], self.color_line)
            # else:
            #    self.line(p0, p1, self.color_line)
            #    self.line(p1, p2, self.color_line)
        if not self.bezier:
            self.polygon(
                xy, fill=self.polygon_fill[len(points)], outline=self.color_line
            )

        xy = []
        for i in range(0, len(neg_ring) - 2, 3):
            p0 = neg_ring[i]
            p1 = neg_ring[i + 1]
            p2 = neg_ring[i + 2]

            xy.append(tuple(p0.numpy()))
            xy.append(tuple(p1.numpy()))
            xy.append(tuple(p2.numpy()))

            if self.bezier:
                lines = quadratic_bezier(p0, p1, p2)
                for j in range(len(lines) - 1):
                    self.line(lines[j], lines[j + 1], self.color_line)
            else:
                self.line(p0, p1, self.color_line)
                self.line(p1, p2, self.color_line)

        return pos_ring

    def circle(self, c, r, color=(255, 255, 255)):
        raise NotImplementedError

    def point(self, p, color=(255, 255, 255)):
        raise NotImplementedError

    def line(self, p0, p1, color=(0, 0, 0)):
        raise NotImplementedError

    def polygon(self, points, fill, outline):
        raise NotImplementedError

    def draw_beziers(self, face):
        for i in range(0, len(face.vertices) - 2, 2):
            p0 = face.vertices[i]
            p1 = face.vertices[i + 1]
            p2 = face.vertices[i + 2]
            lines = quadratic_bezier(p0, p1, p2)
            for j in range(len(lines) - 1):
                self.line(lines[j], lines[j + 1], self.color_line)

    def face(self, face, dotted=False):
        n_vert = len(face.vertices)
        if n_vert not in self.polygon_fill:
            self.polygon_fill[n_vert] = tuple(
                [int(c * 255) for c in self.colormap(np.random.randint(255))[:3]]
            )

        fill_intersect_points(face, self.intersect_points)
        inside_vertices = face.vertices

        if self.ornements:
            inside_vertices = self.draw_outline_lines(face.vertices)
        else:
            if self.bezier:
                self.draw_beziers(face)
            else:
                xy = []
                for i in range(n_vert + 1):
                    xy.append(tuple(face.vertices[i % n_vert].numpy()))
                self.polygon(
                    xy, fill=self.polygon_fill[n_vert], outline=self.color_line
                )

        if self.hatching:
            self.hatch_fill(inside_vertices)
            if self.hatching.crosshatch:
                self.hatch_fill(inside_vertices, self.hatching.crosshatch)

    def in_bounds(self, v):
        if math.isnan(v.x) or math.isnan(v.y) or math.isinf(v.x) or math.isinf(v.y):
            return False
        if not (
            self.size[0] < v.x < self.size[0] + self.size[2]
            and self.size[1] < v.y < self.size[1] + self.size[3]
        ):
            return False
        return True

    def set_label(self, label):
        pass

    def set_caption(self, caption):
        pass

    def set_color_bg(self, color):
        pass

    def set_colormap(self, colormap):
        self.colormap = colormap

    def new(self, filename, size=None, n_tiles=None):
        pass
