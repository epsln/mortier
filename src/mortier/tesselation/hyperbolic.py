from hypertiling import HyperbolicTiling
from hypertiling.graphics.plot import convert_polygons_to_patches

from mortier.coords import EuclideanCoords
from mortier.face.face import Face
from mortier.tesselation.tesselation import Tesselation


class HyperbolicTesselation(Tesselation):
    """
    Hyperbolic polygonal tessellation based on the {p, q} tiling.

    This class wraps a ``HyperbolicTiling`` object and converts its output
    into ``Face`` objects suitable for rendering using a ``Tesselation``
    writer backend.
    """

    def __init__(self, writer, p, q, n_layers=7, angle=None):
        """
        Initialize a hyperbolic tessellation.

        Parameters
        ----------
        writer : object
            Rendering backend used by the base ``Tesselation`` class.
        p : int
            Number of sides of each polygon.
        q : int
            Number of polygons meeting at each vertex.
        n_layers : int, optional
            Number of layers of the hyperbolic tiling (default is 7).
        angle : float or None, optional
            Optional rotation angle applied to the tessellation.
        """
        super().__init__(writer)

        self.p = p
        self.q = q
        self.tess_id = f"{p}-gone, {q}-voisins"
        self.n_layers = n_layers

        self.tess = HyperbolicTiling(
            self.p,
            self.q,
            self.n_layers,
            kernel="SRS",
        )

        self.faces = []
        self.angle = angle

        self.scale = min(self.writer.size[3], self.writer.size[2]) / 2
        self.refine_level = 0
        self.half_plane = False
        self.draw_unit_circle = False

    def set_scale(self, scale):
        """
        Set the global scale factor for the tessellation.

        Parameters
        ----------
        scale : float
            Multiplicative scaling factor relative to the writer size.
        """
        self.scale = (
            min(self.writer.size[3], self.writer.size[2]) / 2 * scale
        )

    def convert_to_half_plane(self):
        """
        Convert all faces to the half-plane model.

        This replaces the current list of faces with their half-plane
        equivalents.
        """
        faces = []
        for face in self.faces:
            faces.append(face.half_plane())
        self.faces = faces

    def set_draw_unit_circle(self, draw):
        """
        Enable or disable drawing of the unit circle.

        Parameters
        ----------
        draw : bool
            If True, the unit circle will be drawn.
        """
        self.draw_unit_circle = draw

    def refine_tiling(self, iterations):
        """
        Refine the hyperbolic lattice and regenerate faces.

        Parameters
        ----------
        iterations : int
            Number of refinement iterations applied to the lattice.
        """
        self.tess.refine_lattice(iterations)
        self.tesselate_face()

    def tesselate_face(self):
        """
        Generate faces from the hyperbolic tiling.

        This method converts the internal ``HyperbolicTiling`` polygons
        into ``Face`` objects, applies scaling and translation, and
        optionally converts them to the half-plane model.
        """
        # Reference translation point (center of the canvas)
        z_point = EuclideanCoords(
            [self.writer.size[2] / 2, self.writer.size[3] / 2]
        )

        # Extract faces from a Matplotlib PolygonCollection
        convert_polygons_to_patches(self.tess)

        self.faces = []
        for polygon in self.tess:
            points = polygon[1:]
            vertices = [
                EuclideanCoords([p.real, p.imag]) for p in points
            ]
            face = Face(vertices)
            self.faces.append(face)

        if self.half_plane:
            self.convert_to_half_plane()
            z_point = EuclideanCoords(
                [self.writer.size[2] / 2, 0]
            )

        faces = []
        for face in self.faces:
            face = face.scale(self.scale).translate(z_point)
            faces.append(face)

        self.faces = faces

