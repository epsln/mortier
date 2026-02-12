import numpy as np

from mortier.coords.coords import Coords


class EuclideanCoords(Coords):
    """
    Represents a 2D point in Euclidean space with utility operations.
    """

    def __init__(self, p):
        """
        Initialize a Euclidean coordinate.

        Parameters
        ----------
        p : array-like of float
            List or array with 2 elements [x, y].
        """
        self.x = p[0]
        self.y = p[1]

    def isclose(self, p):
        """
        Check if two points are approximately equal.

        Parameters
        ----------
        p : EuclideanCoords
            Another Euclidean coordinate.

        Returns
        -------
        bool
            True if the points are very close, else False.
        """
        return abs(self.x - p.x) < 1e-4 and abs(self.y - p.y) < 1e-4

    def translate(self, wc):
        """
        Translate this point by another vector.

        Parameters
        ----------
        wc : EuclideanCoords
            Translation vector.

        Returns
        -------
        EuclideanCoords
            New translated point.
        """
        return EuclideanCoords([self.x + wc.x, self.y + wc.y])

    def scale(self, k):
        """
        Scale this point by a factor.

        Parameters
        ----------
        k : float
            Scaling factor.

        Returns
        -------
        EuclideanCoords
            Scaled point.
        """
        return EuclideanCoords([self.x * k, self.y * k])

    def sum(self):
        """
        Sum of the x and y coordinates.

        Returns
        -------
        float
            x + y
        """
        return self.x + self.y

    def heading(self):
        """
        Angle of the vector from the origin in radians (mod pi).

        Returns
        -------
        float
            Heading angle in radians.
        """
        return np.arctan2(self.y, self.x) % np.pi

    def len(self):
        """
        Euclidean length (magnitude) of the vector.

        Returns
        -------
        float
            Vector length.
        """
        return np.sqrt(self.x**2 + self.y**2)

    def normalise(self):
        """
        Normalize the vector to unit length.

        Returns
        -------
        EuclideanCoords
            Unit vector in the same direction.
        """
        length = self.len()
        if length < 1e-9:
            return EuclideanCoords([0.0, 0.0])
        return EuclideanCoords([self.x / length, self.y / length])

    def rotate(self, angle):
        """
        Rotate the point around the origin.

        Parameters
        ----------
        angle : float
            Angle in radians.

        Returns
        -------
        EuclideanCoords
            Rotated point.
        """
        x_rotated = self.x * np.cos(angle) - self.y * np.sin(angle)
        y_rotated = self.x * np.sin(angle) + self.y * np.cos(angle)
        return EuclideanCoords([x_rotated, y_rotated])

    def rotate_around(self, dx, dy, angle):
        """
        Rotate the point around an arbitrary point (dx, dy).

        Parameters
        ----------
        dx : float
            X-coordinate of the rotation center.
        dy : float
            Y-coordinate of the rotation center.
        angle : float
            Rotation angle in radians.

        Returns
        -------
        EuclideanCoords
            Rotated point.
        """
        x_rotated = (
            ((self.x - dx) * np.cos(angle)) - ((self.y - dy) * np.sin(angle)) + dx
        )
        y_rotated = (
            ((self.x - dx) * np.sin(angle)) + ((self.y - dy) * np.cos(angle)) + dy
        )
        return EuclideanCoords([x_rotated, y_rotated])

    def to_euclidean(self):
        """
        Return self (compatibility with other coordinate systems).

        Returns
        -------
        EuclideanCoords
            Self.
        """
        return self
