import numpy as np

from mortier.coords import EuclideanCoords, Line
from mortier.face.face import Face


class P2Penrose(Face):
    """
    Class that implement the P2 tile from Penrose
    """

    def __init__(self, A, B, C, code):
        # TODO: Use the normal face vertices.
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
    def initialise(code=2, length=70, p=EuclideanCoords([0, 0])):
        """
        Generate a base level 0 tiling as a star of P2 Tiles
        Parameters
        ----------
        length: float
            Length of the side
        p: float
            Center of the penrose tesselation
        code: int
            Indicates which sub-tile this face belongs to.
        """
        output = []
        for i in range(10):
            A = EuclideanCoords(
                [
                    p.x + length * np.cos(i / 10 * np.pi * 2),
                    p.y + length * np.sin(i / 10 * np.pi * 2),
                ]
            )
            B = EuclideanCoords(
                [
                    p.x + length * np.cos((i + 1) / 10 * np.pi * 2),
                    p.y + length * np.sin((i + 1) / 10 * np.pi * 2),
                ]
            )
            if i % 2:
                output.append(P2Penrose(p, B, A, (i + 1) % 2))
            else:
                output.append(P2Penrose(p, A, B, (i + 1) % 2))

        return output

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
