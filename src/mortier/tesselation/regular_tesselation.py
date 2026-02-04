import math


from mortier.coords import LatticeCoords
from mortier.face.face import Face
from mortier.tesselation.tesselation import Tesselation
from mortier.utils.math_utils import planeToTileCoords


class RegularTesselation(Tesselation):
    # TODO: Make class more generic removing tess parameters
    def __init__(self, writer, tess, tess_id):
        super().__init__(writer)
        self.writer = writer
        self.tess = tess
        self.tess_id = tess_id
        self.wpow = []

        self.wpow.append(LatticeCoords([1, 0, 0, 0]))
        self.wpow.append(LatticeCoords([0, 1, 0, 0]))
        self.wpow.append(LatticeCoords([0, 0, 1, 0]))
        self.wpow.append(LatticeCoords([0, 0, 0, 1]))
        self.wpow.append(LatticeCoords([-1, 0, 1, 0]))
        self.wpow.append(LatticeCoords([0, -1, 0, 1]))
        self.wpow.append(LatticeCoords([-1, 0, 0, 0]))
        self.wpow.append(LatticeCoords([0, -1, 0, 0]))
        self.wpow.append(LatticeCoords([0, 0, -1, 0]))
        self.wpow.append(LatticeCoords([0, 0, 0, -1]))
        self.wpow.append(LatticeCoords([1, 0, -1, 0]))
        self.wpow.append(LatticeCoords([0, 1, 0, -1]))

        self.set_tesselation(tess, tess_id)

        self.show_dual = False
        self.show_face = False
        self.show_base = False
        self.ray_tesselation = False
        self.angle = False
        self.assym_angle = False
        self.param_mode = False
        self.show_underlying = False
        self.separated_site_mode = False
        self.lacing_mode = False

    def fill_neighbor(self, faces):
        vertex_map = {}
        for face in faces:
            for v in face.vertices:
                if v in vertex_map:
                    vertex_map[v].append(face)
                else:
                    vertex_map[v] = [face]
        for v in vertex_map.keys():
            for f in vertex_map[v]:
                f.add_neigbors(vertex_map[v])

    def draw_seed(self):
        self.writer.face(self.cell, dotted=True)

        for s in self.seed:
            s = LatticeCoords(s)
            self.writer.point(s)

        self.writer.write()

    def draw_cell(self):
        for x in range(-2, 2):
            t = self.T1.translate(self.T1.scale(x))
            t = t.translate(self.T2.scale(-1))
            t1 = self.T1.translate(self.T1.scale(x))
            t1 = t1.translate(self.T2.scale(2))
            self.writer.line(t, t1, dotted=True)

        for x in range(-1, 3):
            t = self.T1.translate(self.T1.scale(-2))
            t = t.translate(self.T2.scale(x))
            t1 = self.T1.translate(self.T1.scale(1))
            t1 = t1.translate(self.T2.scale(x))
            self.writer.line(t, t1, dotted=True)

    def draw_star(self):
        neighbor_arr = {}
        self.draw_cell()

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                f = self.cell.translate(self.T1, self.T2, x, y)
                self.writer.face(f)

                for s in self.seed:
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1
                    self.writer.point(p)
                    self.writer.point(s)

        for s in self.seed:
            s = LatticeCoords(s)

            for k in range(6):
                p = self.wpow[k]
                sk = s.translate(p)
                if str(sk.w) in neighbor_arr:
                    self.writer.line(s, sk)
                    self.writer.point(sk)

        self.writer.write()

    def draw_edge(self):
        neighbor_arr = {}

        self.writer.face(self.cell, dotted=True)
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for s in self.seed:
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1

        for s in self.seed:
            s = LatticeCoords(s)

            for k in range(6):
                p = self.wpow[k]
                sk = s.translate(p)
                if str(sk.w) in neighbor_arr:
                    self.writer.line(s, sk)

        self.writer.write()

    def tesselate_face(self):
        i_min, i_max, j_min, j_max = self.find_corners()
        neighbor_arr = {}

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for s in self.seed:
                    s = LatticeCoords(s)
                    p = s.translate(self.T1.scale(x).translate(self.T2.scale(y)))
                    neighbor_arr[str(p.w)] = 1

        faces = []
        for s in self.seed:
            s = LatticeCoords(s)
            S = []

            for k in range(6):
                p = self.wpow[k]
                sk = s.translate(p)
                if str(sk.w) in neighbor_arr:
                    S.append(k)

            for i in range(len(S) - 1):
                h = 6 - (S[i + 1] - S[i])
                m = 12 / h
                faces.append(
                    Face.generate(
                        s,
                        S[i],
                        m,
                        param_mode=self.param_mode,
                        assym_mode=self.assym_angle,
                        separated_site_mode=self.separated_site_mode,
                    )
                )

        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                for f in faces:
                    f = f.translate(self.T1, self.T2, i, j)
                    f = f.scale(self.writer.n_tiles)
                    self.faces.append(f)

        self.fill_neighbor(faces)

    def find_corners(self):
        W = [1, 0.8660254037844386 + 0.5 * 1j, 0.5 + 0.8660254037844386 * 1j, 0 + 1j]

        if self.show_base:
            i_min = -1
            i_max = 2
            j_min = -1
            j_max = 2
            return i_min, i_max, j_min, j_max

        i_min = 1000
        i_max = -1000
        j_min = 1000
        j_max = -1000
        corners = [
            0,
            self.writer.size[2],
            self.writer.size[3] * 1j,
            (self.writer.size[2] + self.writer.size[3] * 1j),
        ]

        for z in corners:
            z_ = planeToTileCoords(
                self.tess, W, z.real / self.writer.n_tiles, z.imag / self.writer.n_tiles
            )

            i_min = min(i_min, z_.real)
            j_min = min(j_min, z_.imag)
            i_max = max(i_max, z_.real)
            j_max = max(j_max, z_.imag)

        i_min = math.floor(i_min - 1)
        i_max = math.ceil(i_max + 2)
        j_min = math.floor(j_min - 1)
        j_max = math.ceil(j_max + 2)

        return i_min, i_max, j_min, j_max

    def set_param_mode(self, mode=False):
        self.param_mode = mode

    def set_angle(self, angle=False):
        self.angle = angle
        self.writer.set_band_angle(angle)

    def set_assym_angle(self, angle=False):
        self.assym_angle = angle

    def set_show_underlying(self, show_underlying=False):
        self.show_underlying = show_underlying

    def set_separated_site_mode(self, separated_site=False):
        self.separated_site_mode = separated_site

    def set_tesselation(self, tess, tess_id):
        self.tess = tess
        self.tess_id = tess_id
        self.T0 = LatticeCoords([0, 0, 0, 0])
        self.T1 = LatticeCoords(tess["T1"])
        self.T2 = LatticeCoords(tess["T2"])
        self.T3 = self.T1.translate(self.T2)
        self.seed = self.tess["Seed"]
        self.cell = Face([self.T0, self.T1, self.T3, self.T2])

    def set_writer(self, writer):
        self.writer = writer
