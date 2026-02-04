import copy
import math
import random

import noise
import numpy as np

import mortier.utils.math_utils
from mortier.coords import EuclideanCoords, LatticeCoords, Line


class Face:
    def __init__(
        self,
        vertices,
        mid_points=[],
        barycenter=None,
        param_mode=False,
        assym_mode=False,
        separated_site_mode=False,
    ):
        self.vertices = vertices
        self.mid_points = mid_points
        self.barycenter = barycenter
        self.param_mode = param_mode
        self.assym_mode = assym_mode

        self.separated_site_mode = separated_site_mode
        if self.separated_site_mode:
            self.separated_site = self.separated_site_mode
        self.neighbors = []

    @staticmethod
    def generate(
        v, k, m, param_mode=False, assym_mode=False, separated_site_mode=False
    ):
        wpow = []
        wpow.append(LatticeCoords([1, 0, 0, 0]))
        wpow.append(LatticeCoords([0, 1, 0, 0]))
        wpow.append(LatticeCoords([0, 0, 1, 0]))
        wpow.append(LatticeCoords([0, 0, 0, 1]))
        wpow.append(LatticeCoords([-1, 0, 1, 0]))
        wpow.append(LatticeCoords([0, -1, 0, 1]))
        wpow.append(LatticeCoords([-1, 0, 0, 0]))
        wpow.append(LatticeCoords([0, -1, 0, 0]))
        wpow.append(LatticeCoords([0, 0, -1, 0]))
        wpow.append(LatticeCoords([0, 0, 0, -1]))
        wpow.append(LatticeCoords([1, 0, -1, 0]))
        wpow.append(LatticeCoords([0, 1, 0, -1]))

        vertices = [v, v.translate(wpow[k])]

        for i in range(2, int(m)):
            k = int((k + 12 / m) % 12)
            vertices.append(vertices[i - 1].translate(wpow[k]))

        return Face(
            vertices,
            param_mode=param_mode,
            assym_mode=assym_mode,
            separated_site_mode=separated_site_mode,
        )

    def translate(self, T1, T2=None, i=None, j=None):
        new_face = copy.copy(self)
        if type(self.vertices[0]).__name__ == "LatticeCoords":
            TI = T1.scale(i)
            TIJ = TI.translate(T2.scale(j))
            new_face.vertices = [v.translate(TIJ) for v in self.vertices]
        else:
            new_face.vertices = [v.translate(T1) for v in self.vertices]

        if self.barycenter:
            # TODO: Remove me
            b = self.barycenter.translate(TIJ)
            new_face.barycenter = b
            return new_face
        else:
            return new_face

    def scale(self, n):
        new_face = copy.copy(self)
        new_face.vertices = [v.scale(n) for v in self.vertices]

        if self.barycenter:
            # TODO: Remove
            b = self.barycenter.scale(n)
            new_face.barycenter = b
            return new_face
        else:
            return new_face

    def rotate(self, theta):
        new_face = copy.copy(self)
        vertices = []
        for v in self.vertices:
            v = EuclideanCoords([v.x, v.y])
            v_r = v.rotate(theta)
            vertices.append(v_r)
        new_face.vertices = vertices
        return new_face

    def add_neigbors(self, face):
        self.neighbors = [f for f in face if f.vertices != self.vertices]

    def ray_transform(self, angle, bounds=[], frame_num=0):
        new_face = copy.copy(self)
        vertices = []
        mid_points = []

        if self.param_mode:
            angle = math_utils.angle_parametrisation(
                self.vertices[0], self.param_mode, bounds, frame_num
            )

        for i in range(len(self.vertices)):
            # TODO: Put sides in faces instead of using vertices
            p0 = self.vertices[i]
            p1 = self.vertices[(i + 1) % len(self.vertices)]
            p2 = self.vertices[(i + 2) % len(self.vertices)]

            side_0 = Line(p0, p1)
            side_1 = Line(p1, p2)

            p_mid_0 = side_0.get_midpoint()
            p_mid_1 = side_1.get_midpoint()

            if self.separated_site_mode:
                p_mid_0 = side_0.get_pq_point(1, self.separated_site)
                p_mid_1 = side_1.get_pq_point(
                    self.separated_site - 1, self.separated_site
                )
            angle_0 = side_0.heading() + angle
            angle_1 = side_1.heading() - angle

            if self.assym_mode:
                angle_1 = side_1.heading() - self.assym_mode

            end_pt_0 = EuclideanCoords([np.cos(angle_0), np.sin(angle_0)])
            end_pt_1 = EuclideanCoords([np.cos(angle_1), np.sin(angle_1)])

            end_pt_0 = p_mid_0.translate(end_pt_0)
            end_pt_1 = p_mid_1.translate(end_pt_1)

            s0 = EuclideanCoords([p_mid_0.x - end_pt_0.x, p_mid_0.y - end_pt_0.y])
            s1 = EuclideanCoords([p_mid_1.x - end_pt_1.x, p_mid_1.y - end_pt_1.y])

            t = (s1.x * (p_mid_0.y - p_mid_1.y) - s1.y * (p_mid_0.x - p_mid_1.x)) / (
                -s1.x * s0.y + s0.x * s1.y
            )

            x = EuclideanCoords([p_mid_0.x + (t * s0.x), p_mid_0.y + (t * s0.y)])

            vertices.append(p_mid_0)
            mid_points.append((p_mid_0, angle))
            vertices.append(x)
            if self.separated_site_mode:
                vertices.append(p_mid_1)
                if self.assym_mode:
                    mid_points.append((p_mid_1, assym_mode))
                else:
                    mid_points.append((p_mid_1, angle))

        vertices.append(vertices[0])
        new_face.vertices = vertices
        new_face.mid_points = mid_points
        return new_face

    def half_plane(self):
        vertices = []
        for v in self.vertices:
            z = v.x + 1j * v.y
            z = (-1j * z - 1j) / (z - 1)
            vertices.append(EuclideanCoords([z.real, z.imag]))
        self.vertices = vertices
        return self

    def __str__(self):
        t = []
        for v in self.vertices:
            t.append(f"({round(v.x, 2)},{round(v.y, 3)})")
        return "->".join(t)


class P2Penrose(Face):
    def __init__(self, A, B, C, code):
        self.A = A
        self.B = B
        self.C = C
        self.edges = [Line(A, B), Line(B, C)]
        self.code = code

    @staticmethod
    def initialise(code=2, l=70, x_offset=-15, y_offset=-5):
        p0 = -0
        y = -0
        A = EuclideanCoords([p0, y])
        B = EuclideanCoords([l, y])
        C = EuclideanCoords([(l) / 2, y + np.tan(0.62) * (l) / 2])
        C0 = EuclideanCoords([(l) / 2, y + np.tan(0.62) * (l) / 2])
        C1 = EuclideanCoords(
            [l * np.cos(72 / 360 * 2 * np.pi), l * np.sin(72 / 360 * 2 * np.pi)]
        )
        A = A.translate(EuclideanCoords([x_offset, y_offset]))
        B = B.translate(EuclideanCoords([x_offset, y_offset]))
        C = C.translate(EuclideanCoords([x_offset, y_offset]))
        C1 = C1.translate(EuclideanCoords([x_offset, y_offset]))
        return [P2Penrose(A, B, C, 3), P2Penrose(A, C1, C, 2)]

    def __str__(self):
        return f"{self.A} -> {self.B} -> {self.C} ({self.code})"

    def inflate(self):
        result = []
        if self.code == 0:
            p0 = Line(self.B, self.A).get_pq_point(2, (1 + np.sqrt(5)))
            p1 = Line(self.A, self.C).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P2Penrose(self.A, p1, p0, 2))
            result.append(P2Penrose(self.B, p0, p1, 1))
            result.append(P2Penrose(self.B, self.C, p1, 0))
            return result

        if self.code == 1:
            p0 = Line(self.B, self.A).get_pq_point(2, (1 + np.sqrt(5)))
            p1 = Line(self.A, self.C).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P2Penrose(self.A, p1, p0, 3))
            result.append(P2Penrose(self.B, p0, p1, 0))
            result.append(P2Penrose(self.B, self.C, p1, 1))
            return result

        if self.code == 2:
            p0 = Line(self.A, self.B).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P2Penrose(self.A, p0, self.C, 1))
            result.append(P2Penrose(self.B, self.C, p0, 2))
            return result

        if self.code == 3:
            p0 = Line(self.A, self.B).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P2Penrose(self.A, p0, self.C, 0))
            result.append(P2Penrose(self.B, self.C, p0, 3))
            return result


class P3Penrose(P2Penrose):
    def __init__(self, A, B, C, code):
        self.A = A
        self.B = B
        self.C = C
        self.edges = [Line(A, B), Line(B, C)]
        self.code = code

    @staticmethod
    def initialise(code=2, l=60, x_offset=-5, y_offset=2):
        p0 = -0
        y = 0
        A = EuclideanCoords([p0, y])
        B = EuclideanCoords([(l) / 2, y - np.tan(0.62) * (l) / 2])
        B0 = EuclideanCoords([(l) / 2, y + np.tan(0.62) * (l) / 2])
        C = EuclideanCoords([l, y])
        A = A.translate(EuclideanCoords([x_offset, y_offset]))
        B = B.translate(EuclideanCoords([x_offset, y_offset]))
        B0 = B0.translate(EuclideanCoords([x_offset, y_offset]))
        C = C.translate(EuclideanCoords([x_offset, y_offset]))
        return [P3Penrose(A, B, C, 2), P3Penrose(A, B0, C, 2)]

    def inflate(self):
        result = []
        if self.code == 0:
            p0 = Line(self.B, self.A).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P3Penrose(p0, self.C, self.A, 0))
            result.append(P3Penrose(self.B, p0, self.C, 3))
            return result

        if self.code == 1:
            p0 = Line(self.B, self.C).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P3Penrose(self.C, self.A, p0, 1))
            result.append(P3Penrose(self.A, p0, self.B, 2))
            return result

        if self.code == 2:
            p0 = Line(self.A, self.B).get_pq_point(2, (1 + np.sqrt(5)))
            p1 = Line(self.A, self.C).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P3Penrose(self.A, p0, p1, 3))
            result.append(P3Penrose(p0, p1, self.B, 0))
            result.append(P3Penrose(self.C, p1, self.B, 2))
            return result

        if self.code == 3:
            p0 = Line(self.C, self.B).get_pq_point(2, (1 + np.sqrt(5)))
            p1 = Line(self.C, self.A).get_pq_point(2, (1 + np.sqrt(5)))

            result.append(P3Penrose(self.B, p1, self.A, 3))
            result.append(P3Penrose(self.B, p1, p0, 1))
            result.append(P3Penrose(p1, p0, self.C, 2))
            return result
