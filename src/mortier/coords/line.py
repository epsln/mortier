import numpy as np

from mortier.coords.coords import Coords
from .euclidean_coords import EuclideanCoords


class Line(Coords):
    """
    Class representing a line segment defined by two points.
    """

    def __init__(self, p0, p1):
        """
        Initialize a line with a start point and an end point.

        Parameters
        ----------
        p0 : Coords
            Starting point of the line.
        p1 : Coords
            Ending point of the line.
        """
        self.beg_pt = p0
        self.end_pt = p1
        self.vec = p1.translate(p0.scale(-1))

    def len(self):
        """
        Compute the length of the line.

        Returns
        -------
        float
            Length of the line.
        """
        return self.vec.len()

    def get_midpoint(self):
        """
        Compute the midpoint of the line.

        Returns
        -------
        EuclideanCoords
            Midpoint as a Euclidean coordinate.
        """
        midpoint = self.beg_pt.translate(self.end_pt).scale(0.5)
        return midpoint.toEuclidean()

    def get_pq_point(self, p, q):
        """
        Compute a point along the line at fraction p/q.

        Parameters
        ----------
        p : float
            Numerator of the fraction along the line.
        q : float
            Denominator of the fraction along the line.

        Returns
        -------
        EuclideanCoords
            Point at fraction p/q along the line.
        """
        x = self.beg_pt.x + p * (self.end_pt.x - self.beg_pt.x) / q
        y = self.beg_pt.y + p * (self.end_pt.y - self.beg_pt.y) / q
        return EuclideanCoords([x, y])

    def heading(self):
        """
        Compute the angle of the line relative to the x-axis.

        Returns
        -------
        float
            Angle in radians, modulo pi.
        """
        return np.atan2(self.vec.y, self.vec.x) % np.pi

    def translate(self, wc):
        """
        Translate the line by a coordinate vector.

        Parameters
        ----------
        wc : Coords
            Translation vector.

        Returns
        -------
        Line
            Translated line.
        """
        return Line(self.beg_pt.translate(wc), self.end_pt.translate(wc))

    def scale(self, k):
        """
        Scale the line by a factor relative to the origin.

        Parameters
        ----------
        k : float
            Scaling factor.

        Returns
        -------
        Line
            Scaled line.
        """
        return Line(self.beg_pt.scale(k), self.end_pt.scale(k))

    def rotate_around(self, x, y, theta):
        """
        Rotate the line around a given point by a given angle.

        Parameters
        ----------
        x : float
            X-coordinate of rotation center.
        y : float
            Y-coordinate of rotation center.
        theta : float
            Rotation angle in radians.

        Returns
        -------
        Line
            Rotated line.
        """
        p0 = self.beg_pt.rotate_around(x, y, theta)
        p1 = self.end_pt.rotate_around(x, y, theta)  # fixed self.beg_pt -> self.end_pt
        return Line(p0, p1)

    def __str__(self):
        """
        String representation of the line.

        Returns
        -------
        str
            "beg_pt -> end_pt"
        """
        return f"{self.beg_pt} -> {self.end_pt}"

