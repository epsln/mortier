import abc

from mortier.coords import EuclideanCoords
from mortier.enums import OrnementsType
from mortier.utils.geometry import build_negative_space_faces


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
        self.tess_id = None
        self.depth = 1

    @abc.abstractmethod
    def tesselate_face(self):
        """
        Generate the faces composing the tessellation.

        This method is responsible for populating ``self.faces`` and
        must be implemented by subclasses.
        """
        raise NotImplementedError

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
        if self.writer.ornements:
            self.writer.ornements.angle = angle

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

    def set_caption(self):
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

        if self.writer.ornements:
            if self.writer.ornements.type == OrnementsType.LACES:
                caption += ", entrelacements"
            else:
                caption += ", bandeaux"

        self.writer.set_caption(caption)
        # self.writer.set_label(caption)

    def draw_tesselation(self, frame_num=[0, 1]):
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

        faces = self.faces
        if self.angle:
            for i in range(self.depth):
                new_faces = []
                for face in faces:
                    if self.angle:
                        f = face.ray_transform(
                            self.angle,
                            self.writer.size,
                            frame_num,
                        )
                    new_faces.append(f)
                    if self.show_underlying:
                        self.writer.face(face, dotted=True)
                    if i == self.depth - 1:
                        self.writer.face(f)
                        #self.writer.color_line = (255, 0, 0)
                    #pr = 1
                    #for v in f.vertices:
                    #    if 0 > v.x or v.x > 1920 or v.y < 0 or v.y > 1920:
                    #        pr = 0
                    #        break
                    #if pr == 1:
                    #    print("Face") 
                    #    print(f)
                    #    for o in f.intersection_points:
                    #        print(f"l0: {o['launch_0']} -> {o['end_pt0']}, l1: {o['launch_1']} -> {o['end_pt1']}")

                    #    self.writer.color_line = (255, 255, 255)
                    #if i == self.depth - 1:
                    #    for o in f.intersection_points:
                    #        self.writer.line(o['launch_0'], o['end_pt0'], color = (0, 255, 0)) 
                    #        self.writer.line(o['launch_1'], o['end_pt1'], color = (0, 0, 255)) 
                    #        self.writer.circle(o['point'], 10, color = (0, 0, 255)) 

                negatives = build_negative_space_faces(new_faces)
                faces = new_faces + negatives

        else:
            self.writer.regular = True
            for face in self.faces:
                self.writer.face(face)

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

        self.set_caption()
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
