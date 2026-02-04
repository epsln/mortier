from mortier.coords import EuclideanCoords, LatticeCoords
from mortier.face.face import Face


class Tesselation:
    """
    Base class for geometric tessellations.

    This class defines the common interface and rendering logic for
    tessellations. Concrete subclasses are expected to implement the
    geometry-specific methods.
    """

    def __init__(self, writer):
        """
        Initialize a tessellation.

        Parameters
        ----------
        writer : object
            Rendering backend responsible for drawing primitives
            (faces, lines, points, etc.).
        """
        self.writer = writer
        self.faces = []

        self.show_dual = False
        self.show_face = False
        self.show_base = False
        self.draw_unit_circle = False
        self.ray_tesselation = False
        self.angle = False
        self.assym_angle = False
        self.param_mode = False
        self.show_underlying = False
        self.separated_site_mode = False
        self.lacing_mode = False
        self.tile = None

    def fill_neighbor(self, faces):
        """
        Populate neighbor relationships between faces.

        This method is intended to be overridden by subclasses.

        Parameters
        ----------
        faces : list of Face
            Faces for which neighbor relationships should be computed.
        """
        pass

    def draw_seed(self):
        """
        Draw the seed configuration of the tessellation.

        This method is intended to be overridden by subclasses.
        """
        pass

    def draw_cell(self):
        """
        Draw the fundamental cell of the tessellation.

        This method is intended to be overridden by subclasses.
        """
        pass

    def draw_star(self):
        """
        Draw a star-shaped neighborhood around the seed.

        This method is intended to be overridden by subclasses.
        """
        pass

    def draw_edge(self):
        """
        Draw edges connecting neighboring elements.

        This method is intended to be overridden by subclasses.
        """
        pass

    def tesselate_face(self):
        """
        Generate the faces composing the tessellation.

        This method is responsible for populating ``self.faces`` and
        must be implemented by subclasses.
        """
        pass

    def find_corners(self):
        """
        Compute the bounding indices of the tessellation domain.

        This method must be implemented by subclasses.

        Returns
        -------
        i_min : int
            Minimum index along the first lattice axis.
        i_max : int
            Maximum index along the first lattice axis.
        j_min : int
            Minimum index along the second lattice axis.
        j_max : int
            Maximum index along the second lattice axis.
        """
        pass

    def set_param_mode(self, mode=False):
        """
        Enable or disable parametric angle mode.

        Parameters
        ----------
        mode : bool or str, optional
            Parametric mode identifier (e.g. ``False``, ``"sin"``,
            ``"perlin"``, ``"simplex"``).
        """
        self.param_mode = mode

    def set_angle(self, angle=False):
        """
        Set the global ray deformation angle.

        Parameters
        ----------
        angle : float or bool, optional
            Angle value or False to disable the transformation.
        """
        self.angle = angle
        self.writer.set_band_angle(angle)

    def set_assym_angle(self, angle=False):
        """
        Set an asymmetric angle for ray deformation.

        Parameters
        ----------
        angle : float or bool, optional
            Secondary angle value or False to disable.
        """
        self.assym_angle = angle

    def set_show_underlying(self, show_underlying=False):
        """
        Toggle rendering of the underlying tessellation structure.

        Parameters
        ----------
        show_underlying : bool, optional
            If True, the underlying geometry is drawn.
        """
        self.show_underlying = show_underlying

    def set_separated_site_mode(self, separated_site=False):
        """
        Enable or disable separated site mode.

        Parameters
        ----------
        separated_site : bool, optional
            If True, sites are rendered independently.
        """
        self.separated_site_mode = separated_site

    def draw_tesselation(self, frame_num=0):
        """
        Draw the complete tessellation.

        Parameters
        ----------
        frame_num : int, optional
            Frame index used for animated transformations.

        Returns
        -------
        output : object
            Output produced by the writer backend.
        """
        self.tesselate_face()

        if self.show_base:
            self.draw_cell()

        for face in self.faces:
            if self.show_underlying:
                self.writer.face(face, dotted=True)

            f = face
            if self.angle:
                f = f.ray_transform(
                    self.angle,
                    self.writer.size,
                    frame_num,
                )

            self.writer.face(f)

        if self.draw_unit_circle:
            self.writer.circle(
                EuclideanCoords(
                    [
                        self.writer.size[2] / 2,
                        self.writer.size[3] / 2,
                    ]
                ),
                self.scale,
            )

        caption = ""
        if self.tess_id:
            caption = f"Pavage ${self.tess_id}$"
        elif self.tile:
            caption = f"Pavage ${self.tile}$"

        if self.angle and not self.assym_angle:
            caption += f", avec $\\theta \\approx {round(self.angle, 3)}$"

        if self.separated_site_mode:
            caption += ", sites séparés"

        if self.param_mode == "sin":
            caption += ", angle paramétrisé (sinus)"
        elif self.param_mode == "perlin":
            caption += ", angle paramétrisé (bruit de Perlin)"
        elif self.param_mode == "simplex":
            caption += ", angle paramétrisé (bruit Simplex)"

        if self.assym_angle:
            caption += (
                f", angles assymétrique "
                f"$\\theta_0 \\approx {round(self.angle, 3)}, "
                f"\\theta_1 \\approx {round(self.assym_angle, 3)}$"
            )

        if self.writer.lacing_mode:
            caption += ", entrelacements"

        if self.writer.bands_mode:
            caption += ", bandeaux"

        self.writer.set_caption(caption)
        self.writer.set_label(caption)

        output = self.writer.write()
        return output

    def set_tesselation(self):
        """
        Set or update the tessellation definition.

        This method must be implemented by subclasses.
        """
        pass

    def set_writer(self, writer):
        """
        Set the rendering backend.

        Parameters
        ----------
        writer : object
            Writer instance used for rendering.
        """
        self.writer = writer

