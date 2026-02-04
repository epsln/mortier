import copy

import numpy as np

from mortier.coords import EuclideanCoords, LatticeCoords, Line
from mortier.face.face import Face 
from mortier.utils.math_utils import angle_parametrisation

class P2Penrose(Face):
    """
    Class that implement the P2 tile from Penrose
    """
    def __init__(self, A, B, C, code):
        #TODO: Use the normal face vertices.
        """
        Parameters
        ----------
        A: EuclideanCoords
            First Point of the tile
        B: EuclideanCoords
            Second Point of the tile
        C: EuclideanCoords
            Second Point of the tile
        code: int
            Indicates which sub-tile this face belongs to. 
        """
        self.A = A
        self.B = B
        self.C = C
        self.edges = [Line(A, B), Line(B, C)]
        self.code = code

    @staticmethod
    def initialise(code=2, length=70, x_offset=-15, y_offset=-5):
        """
        Generate a base level 0 tiling, using two P2 tiles.
        Parameters
        ----------
        length: float 
            Length of the side 
        x_offset: float 
            Offset the tiling in the x axis 
        y_offset: float 
            Offset the tiling in the y axis 
        code: int
            Indicates which sub-tile this face belongs to. 
        """
        p0 = -0
        y = -0
        A = EuclideanCoords([p0, y])
        B = EuclideanCoords([length, y])
        C = EuclideanCoords([length / 2, y + np.tan(0.62) * length / 2])
        C1 = EuclideanCoords(
            [length * np.cos(72 / 360 * 2 * np.pi), length * np.sin(72 / 360 * 2 * np.pi)]
        )
        A = A.translate(EuclideanCoords([x_offset, y_offset]))
        B = B.translate(EuclideanCoords([x_offset, y_offset]))
        C = C.translate(EuclideanCoords([x_offset, y_offset]))
        C1 = C1.translate(EuclideanCoords([x_offset, y_offset]))
        return [P2Penrose(A, B, C, 3), P2Penrose(A, C1, C, 2)]

    def __str__(self):
        """
        Helper function to print a face vertices.

        Returns
        -------
        str:
            The vertices of the current faces, with the euclidean coordinates rounded.    
        """
        return f"{self.A} -> {self.B} -> {self.C} ({self.code})"

    def inflate(self):
        """
        Inflate the current tile, which subdivide it into different tiles. 
        The specific tilings are based on the current tile code.
        Returns
        -------
        result: List[P2Penrose]
            List of subtiles 
        """
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
