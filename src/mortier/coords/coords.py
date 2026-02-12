import copy
import math

import numpy as np


class Coords:
    """
    Base class representing a 2D coordinate.
    """

    def __init__(self):
        """
        Initialize a coordinate at the origin (0,0).
        """
        self.x = 0
        self.y = 0

    def translate(self, wc):
        """
        Translate this coordinate by another coordinate.

        Parameters
        ----------
        wc : Coords
            Coordinate to add.

        Returns
        -------
        Coords
            Translated coordinate.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def scale(self, k):
        """
        Scale this coordinate by a factor.

        Parameters
        ----------
        k : float
            Scaling factor.

        Returns
        -------
        Coords
            Scaled coordinate.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def sum(self):
        """
        Sum of the x and y components.

        Returns
        -------
        float
            Sum of x and y.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def angle(self):
        """
        Angle of the vector relative to the positive x-axis.

        Returns
        -------
        float
            Angle in radians.
        """
        return math.atan2(self.y, self.x)

    def numpy(self):
        """
        Convert coordinate to a NumPy array.

        Returns
        -------
        np.ndarray
            Array of shape (2,) containing [x, y].
        """
        return np.array([self.x, self.y])

    def __str__(self):
        """
        String representation of the coordinate.

        Returns
        -------
        str
            Rounded string "x, y".
        """
        return f"{np.round(self.x, 2)}, {np.round(self.y, 2)}"

    def normal(self):
        """
        Return a perpendicular vector (rotated 90 degrees counterclockwise).

        Returns
        -------
        Coords
            Perpendicular coordinate.
        """
        new_c = copy.copy(self)
        new_c.x = -self.y
        new_c.y = self.x
        return new_c

    def to_euclidean(self):
        """
        Convert to Euclidean coordinates (identity for base class).

        Returns
        -------
        Coords
            Corresponding Euclidean coordinate.
        """
        raise NotImplementedError("Subclasses should implement this method.")
