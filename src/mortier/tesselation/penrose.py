from mortier.face.face import Face, P2Penrose, P3Penrose
from mortier.enums import TileType
from mortier.tesselation.tesselation import Tesselation


class PenroseTesselation(Tesselation):
    """
    Penrose (aperiodic) tessellation.

    This class generates Penrose tilings (P2 or P3) using recursive
    inflation rules and converts matching triangle pairs into faces.
    """

    def __init__(self, writer, tile=TileType.P2, level=8):
        """
        Initialize a Penrose tessellation.

        Parameters
        ----------
        writer : object
            Rendering backend used by the base ``Tesselation`` class.
        tile : str or TileType, optional
            Type of Penrose tiling to generate (``TileType.P2`` or
            ``TileType.P3``). Default is ``TileType.P2``.
        level : int, optional
            Number of inflation iterations applied to the initial seed.
        """
        super().__init__(writer)

        self.level = level
        self.tile = tile
        self.tess_id = None
        self.faces = []

        if tile == TileType.P2:
            self.pen = P2Penrose.initialise(
                length=writer.size[2] * (2.0 + writer.n_tiles / 10),
                x_offset=-writer.size[2] / 5,
                y_offset=-writer.size[3] / 6,
            )
        else:
            self.pen = P3Penrose.initialise(
                length=writer.size[2] * (3.5 + writer.n_tiles / 10),
                x_offset=-writer.size[2] / 2,
                y_offset=writer.size[3] / 2,
            )

    def tesselate_face(self):
        """
        Generate faces of the Penrose tessellation.

        This method recursively inflates the Penrose triangles and
        identifies adjacent triangle pairs that can be merged into
        quadrilateral faces.
        """
        # Apply recursive inflation
        for _ in range(self.level):
            triangles = []
            for penrose_triangle in self.pen:
                triangles.extend(penrose_triangle.inflate())
            self.pen = triangles

        # Merge compatible triangle pairs into faces
        for i, p in enumerate(self.pen):
            for p_ in self.pen[i + 1:]:
                if (
                    p.A.isclose(p_.A) and p.C.isclose(p_.C)
                ) or (
                    p.A.isclose(p_.C) and p.C.isclose(p_.A)
                ):
                    vertices = [p.A, p.B, p.C, p_.B]

                    # Orientation test (shoelace-like criterion)
                    s = 0.0
                    for j in range(4):
                        s += (
                            vertices[(j + 1) % 4].x - vertices[j].x
                        ) / (
                            vertices[(j + 1) % 4].y + vertices[j].y
                        )

                    if s < 0:
                        vertices = vertices[::-1]

                    face = Face(
                        vertices,
                        param_mode=self.param_mode,
                        assym_mode=self.assym_angle,
                        separated_site_mode=self.separated_site_mode,
                    )
                    self.faces.append(face)

