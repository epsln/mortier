import copy
from typing import List

import numpy as np

from mortier.coords import Coords, EuclideanCoords, LatticeCoords, Line
from mortier.utils.math_utils import angle_parametrisation


class Face:
    """
    Class representing a closed Polygon, used to tile the space.
    """

    def __init__(
        self,
        vertices,
        mid_points=[],
        param_mode=False,
        assym_mode=False,
        separated_site_mode=False,
    ):
        """
        Initialize a face with a list of points.

        Parameters
        ----------
        vertices : List[Coords]
            List of vertices defining a polygon.
        mid_points: List[EuclideanCoords]
            List of points that lies in the middle of each segment
        param_mode: ParamType
            Type of angle parametrisation to be used
        assym_mode: bool
            If true, induce an assymetry in the ray angles
        separated_site_mode: bool
            If True, separate the launch sites of the rays
        """
        self.vertices = vertices
        if type(self.vertices[0]) == LatticeCoords:
            self._vertices = np.array([v.w for v in self.vertices], dtype=complex)

        self.mid_points = mid_points
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
        """
        Generate a face using the Soto-Sanchez method.

        Parameters
        ----------
        v: LatticeCoords
           Anchor point
        k: int
        m: int
            Number of vertex in the face
        param_mode: ParamType
            Type of angle parametrisation to be used
        assym_mode: bool
            If true, induce an assymetry in the ray angles
        separated_site_mode: bool
            If True, separate the launch sites of the rays
        Returns
        -------
        new_face: Face
            Generated face
        """
        vertices: List[Coords]
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

    def translate(self, dir_vec_1, dir_vec_2=None, mult_i=None, mult_j=None):
        """
        Translate a face. Works with both Euclidean and Lattice Coordinates.

        Parameters
        ----------
        dir_vec_1: Coords
            Unity vector to translate with
        dir_vec_2: Coords
            Unity vector to translate with
        multi_i: int
            Multiplication factor to use with the first unity vector
        multi_j: int
            Multiplication factor to use with the second unity vector
        Returns
        -------
        new_face: Face
            Translated face
        """
        new_face = copy.copy(self)
        if type(self.vertices[0]).__name__ == "LatticeCoords":
            translation = mult_i * dir_vec_1.w + mult_j * dir_vec_2.w   # both complex
            new_face._vertices += translation
        else:
            self.vertices = [v.translate(dir_vec_1) for v in self.vertices]

        return new_face 

    def scale(self, n):
        """
        Scale a face. Works with both Euclidean and Lattice Coordinates.

        Parameters
        ----------
        n: float
            Scaling factor
        Returns
        -------
        new_face: Face
            Scaled face
        """
        new_face = copy.copy(self)
        #new_face.vertices = [v.scale(n) for v in self.vertices]
        new_face.vertices *= n 

        return new_face

    def rotate(self, theta):
        """
        Rotate a face. Works with both Euclidean and Lattice Coordinates.

        Parameters
        ----------
        theta: float
            Angle by which to rotate the face
        Returns
        -------
        new_face: Face
            Rotated face
        """
        new_face = copy.copy(self)
        vertices = []
        for v in self.vertices:
            v = EuclideanCoords([v.x, v.y])
            v_r = v.rotate(theta)
            vertices.append(v_r)
        new_face.vertices = vertices
        return new_face

    def add_neigbors(self, face):
        """
        Add direct neighbors of the face in the tesselation

        Parameters
        ----------
        face: Face
            Current face
        """
        self.neighbors = [f for f in face if f.vertices != self.vertices]

    def ray_transform(self, angle, bounds=[0, 0, 1, 1], frame_num=0):
        """
        Apply the Polygon In Contact technique to the face.
        (https://dl.acm.org/doi/10.5555/1089508.1089538)
        This techniques creates a new face by shooting two "rays" from each sides
        with an angle and finding the intersection. The new face vertices are composed of the
        shooting sites and the ray intersection.

        Parameters
        ----------
        angle: float
            Angle from the normal of the side, toward which the rays are shot.
        bounds: list[float]
            Bounds of the images. Should be the same as writer.size
        frame_num: int
            Num of the generated images, useful to create animation
        Returns
        -------
        face: Face
            Computed face.
        """
        new_face = copy.copy(self)
        vertices = []
        mid_points = []

        if self.param_mode:
            angle = angle_parametrisation(
                self.vertices[0], self.param_mode, bounds, frame_num
            )

        for i in range(len(self.vertices)):
            # TODO: Put sides in faces instead of using vertices
            p0 = self.vertices[i]
            p1 = self.vertices[(i + 1) % len(self.vertices)]
            p2 = self.vertices[(i + 2) % len(self.vertices)]

            dx = p1.x - p0.x
            dy = p1.y - p0.y

            p_mid_0x = (p0.x + p1.x) * 0.5
            p_mid_0y = (p0.y + p1.y) * 0.5

            heading_0 = np.arctan2(dy, dx)

            dx = p2.x - p1.x
            dy = p2.y - p1.y

            p_mid_1x = (p1.x + p2.x) * 0.5
            p_mid_1y = (p1.y + p2.y) * 0.5

            heading_1 = np.arctan2(dy, dx)

            if self.separated_site_mode:
                p_mid_0x = (p0.x + p1.x) * 1/self.separated_site 
                p_mid_0y = (p0.y + p1.y) * 1/self.separated_site
                p_mid_1x = (p1.x + p2.x) * (self.separated_site - 1)/self.separated_site 
                p_mid_1y = (p1.y + p2.y) * (self.separated_site - 1)/self.separated_site

            angle_0 = heading_0 + angle
            angle_1 = heading_1 - angle

            if self.assym_mode:
                angle_1 = heading_1 - self.assym_mode

            end_pt_0x, end_pt_0y = np.cos(angle_0), np.sin(angle_0)
            end_pt_1x, end_pt_1y = np.cos(angle_1), np.sin(angle_1)

            end_pt_0x = p_mid_0x + end_pt_0x
            end_pt_0y = p_mid_0y + end_pt_0y
            end_pt_1x = p_mid_1x + end_pt_1x
            end_pt_1y = p_mid_1y + end_pt_1y

            s0x, s0y = p_mid_0x - end_pt_0x, p_mid_0y - end_pt_0y
            s1x, s1y = p_mid_1x - end_pt_1x, p_mid_1y - end_pt_1y

            t = (s1x * (p_mid_0y - p_mid_1y) - s1y * (p_mid_0x - p_mid_1x)) / (
                -s1x * s0y + s0x * s1y
            )

            cx, cy = p_mid_0x + (t * s0x), p_mid_0y + (t * s0y)

            vertices.append(EuclideanCoords([p_mid_0x, p_mid_0y]))
            mid_points.append((EuclideanCoords([p_mid_0x, p_mid_0y]), angle))
            #if self.point_inside(x):
            #    vertices.append(x)
            if self.separated_site_mode:
                vertices.append(EuclideanCoords([p_mid_1x, p_mid_1y]))
                if self.assym_mode:
                    mid_points.append((EuclideanCoords([p_mid_1x, p_mid_1y]), self.assym_mode))
                else:
                    mid_points.append((EuclideanCoords([p_mid_1x, p_mid_1y]), angle))

        vertices.append(vertices[0])
        new_face.vertices = vertices
        new_face.mid_points = mid_points
        return new_face

    def half_plane(self):
        """
        Transform a Hyperbolic Face from the disk model to the half plane model
        Returns
        -------
        face: Face
            Computed face.
        """

        vertices = []
        for v in self.vertices:
            z = v.x + 1j * v.y
            z = (-1j * z - 1j) / (z - 1)
            vertices.append(EuclideanCoords([z.real, z.imag]))
        self.vertices = vertices
        return self

    def point_inside(self, p):
        """
        Check if point p lies inside polygon defined by vertices.

        Parameters
        ----------
        p : EuclideanCoords
            Point to test
        Returns
        -------
        bool
            True if inside (or on edge), False otherwise
        """

        inside = False
        n = len(self.vertices)

        x, y = p.x, p.y

        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % n]

            x1, y1 = v1.x, v1.y
            x2, y2 = v2.x, v2.y

            # Check if edge crosses horizontal ray to the right of p
            intersects = ((y1 > y) != (y2 > y)) and (
                x < (x2 - x1) * (y - y1) / (y2 - y1) + x1
            )

            if intersects:
                inside = not inside

        return inside
            

    def __str__(self):
        """
        Helper function to print a face vertices.

        Returns
        -------
        str:
            The vertices of the current faces, with the euclidean coordinates rounded.
        """
        t = []
        for v in self.vertices:
            #t.append(f"({round(v.x, 2)},{round(v.y, 3)})")
            t.append(f"({v.x},{v.y})")
        return "->".join(t)
