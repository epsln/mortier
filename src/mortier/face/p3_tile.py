import numpy as np

from mortier.coords import EuclideanCoords, Line
from mortier.face.p2_tile import P2Penrose


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
    def initialise(code=2, length=60, p=EuclideanCoords([0, 0])):
        """
        Generate a base level 0 tiling as a star  of P3 Tiles
        Parameters
        ----------
        length: float
            Length of the side
        p: EuclideanCoords
            Center of the star

        code: int
            Indicates which sub-tile this face belongs to.
        """
        output = []
        theta = 2 * np.pi / 5
        for i in range(10):
            angle1 = i * theta
            angle2 = (i + 1) * theta

            A = EuclideanCoords(
                [p.x + length * np.cos(angle1), p.y + length * np.sin(angle1)]
            )

            B = EuclideanCoords(
                [p.x + length * np.cos(angle2), p.y + length * np.sin(angle2)]
            )

            C = EuclideanCoords([A.x + (B.x - p.x), A.y + (B.y - p.y)])

            if i % 2:
                output.append(P3Penrose(p, A, C, 2))
            else:
                output.append(P3Penrose(p, B, C, 2))

        return output

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
