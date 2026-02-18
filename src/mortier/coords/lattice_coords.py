import numpy as np

from mortier.coords import Coords
from mortier.coords.euclidean_coords import EuclideanCoords


class LatticeCoords(Coords):
    """
    Represents a 4D lattice coordinate with a mapping to 2D Euclidean space.
    """

    def __init__(self, w):
        """
        Initialize a lattice coordinate.

        Parameters
        ----------
        w : array-like of length 4
            Lattice vector [w0, w1, w2, w3].
        """
        self.w = np.array([w[0], w[1], w[2], w[3]], dtype = complex)

        # Map 4D lattice to 2D Euclidean coordinates
        self.x = (w[0] + 0.5 * np.sqrt(3) * w[1] + 0.5 * w[2]).real
        self.y = (0.5 * w[1] + 0.5 * np.sqrt(3) * w[2] + w[3]).real

    def translate(self, wc):
        """
        Translate this lattice point by another lattice vector.

        Parameters
        ----------
        wc : LatticeCoords
            Lattice coordinate to add.

        Returns
        -------
        LatticeCoords
            Translated lattice coordinate.
        """
        c = [w_ + wc_ for w_, wc_ in zip(self.w, wc.w)]
        return LatticeCoords(c)

    def scale(self, k):
        """
        Scale this lattice vector by a factor.

        Parameters
        ----------
        k : float
            Scaling factor.

        Returns
        -------
        LatticeCoords
            Scaled lattice coordinate.
        """
        c = [w_ * k for w_ in self.w]
        return LatticeCoords(c)

    def sum(self):
        """
        Sum of all lattice components.

        Returns
        -------
        float
            Sum of the four components.
        """
        return sum(self.w)

    def rotate(self, angle):
        """
        Rotate the mapped Euclidean coordinates around the origin.

        Parameters
        ----------
        angle : float
            Angle in radians.

        Returns
        -------
        EuclideanCoords
            Rotated Euclidean coordinates.
        """
        x_rotated = self.x * np.cos(angle) - self.y * np.sin(angle)
        y_rotated = self.x * np.sin(angle) + self.y * np.cos(angle)
        return EuclideanCoords([x_rotated, y_rotated])

    def to_euclidean(self):
        """
        Convert lattice coordinate to Euclidean 2D coordinates.

        Returns
        -------
        EuclideanCoords
            Corresponding 2D point.
        """
        return EuclideanCoords([self.x, self.y])
