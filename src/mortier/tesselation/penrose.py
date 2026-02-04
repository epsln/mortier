

from mortier.face.face import Face, P2Penrose, P3Penrose
from mortier.tesselation.tesselation import Tesselation


class PenroseTesselation(Tesselation):
    def __init__(
        self,
        writer,
        tile="P2",
        level=8,
        param_mode=False,
        assym=False,
        separated_site_mode=False,
    ):
        super().__init__(writer)
        self.level = level
        self.tile = tile
        self.tess_id = None
        if tile == "P2":
            self.pen = P2Penrose.initialise(
                0,
                l=writer.size[2] * 2.5,
                x_offset=-writer.size[2] / 2,
                y_offset=-writer.size[3] / 4,
            )
        else:
            self.pen = P3Penrose.initialise(
                0,
                l=writer.size[2] * 3.5,
                x_offset=-writer.size[2] / 1,
                y_offset=-writer.size[3] / 4,
            )
        self.faces = []

    def tesselate_face(self):
        for i in range(self.level):
            triangle = []
            for p in self.pen:
                triangle.extend(p.inflate())
            self.pen = triangle
        for i, p in enumerate(self.pen):
            for p_ in self.pen[i + 1 :]:
                if (p.A.isclose(p_.A) and p.C.isclose(p_.C)) or (
                    p.A.isclose(p_.C) and p.C.isclose(p_.A)
                ):
                    vertices = [p.A, p.B, p.C, p_.B]
                    s = 0
                    for i in range(4):
                        s += (vertices[(i + 1) % 4].x - vertices[i].x) / (
                            vertices[(i + 1) % 4].y + vertices[i].y
                        )
                    if s < 0:
                        vertices = vertices[::-1]
                    f = Face(
                        vertices,
                        param_mode=self.param_mode,
                        assym_mode=self.assym_angle,
                        separated_site_mode=self.separated_site_mode,
                    )
                    self.faces.append(f)
