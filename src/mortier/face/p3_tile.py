import copy

import numpy as np

from mortier.coords import EuclideanCoords, LatticeCoords, Line
from mortier.face.p2_tile import P2Penrose
from mortier.utils.math_utils import angle_parametrisation

class P3Penrose(P2Penrose):
    """
    Class that implement the P3 tile from Penrose
    """
    def __init__(self, A, B, C, code):
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
    def initialise(code=2, length=60, x_offset=-5, y_offset=2):
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
        y = 0
        A = EuclideanCoords([p0, y])
        B = EuclideanCoords([length / 2, y - np.tan(0.62) * length / 2])
        B0 = EuclideanCoords([length / 2, y + np.tan(0.62) * length / 2])
        C = EuclideanCoords([length, y])
        A = A.translate(EuclideanCoords([x_offset, y_offset]))
        B = B.translate(EuclideanCoords([x_offset, y_offset]))
        B0 = B0.translate(EuclideanCoords([x_offset, y_offset]))
        C = C.translate(EuclideanCoords([x_offset, y_offset]))
        return [P3Penrose(A, B, C, 2), P3Penrose(A, B0, C, 2)]

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

        raise ValueError("No code found... Check your initialisation !")
