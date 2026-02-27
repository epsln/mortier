import copy
import math

import numpy as np

from mortier.coords import LatticeCoords
from mortier.face.face import Face
from mortier.tesselation.tesselation import Tesselation
from mortier.utils.math_utils import plane_to_tile_coords


class RegularTesselation(Tesselation):
    """
    Regular tessellation based on a lattice description.

    This class builds faces from a lattice seed and translation vectors,
    supports multiple visualization modes, and generates neighboring
    relationships between faces.
    """

    def __init__(self, writer, tess, tess_id):
        """
        Initialize a regular tessellation.

        Parameters
        ----------
        writer : object
            Rendering backend used by the base ``Tesselation`` class.
        tess : dict
            Dictionary describing the tessellation lattice (translations,
            seed, etc.).
        tess_id : str
            Identifier string for the tessellation.
        """
        super().__init__(writer)

        self.writer = writer
        self.tess = tess
        self.tess_id = tess_id

        self.seed = None
        self.cell = None
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
        """
        Populate neighbor relationships between faces.

        Two faces are considered neighbors if they share a vertex.

        Parameters
        ----------
        faces : list of Face
            Faces for which neighbor relationships are computed.
        """
        vertex_map = {}

        for face in faces:
            for vertex in face.vertices:
                if vertex in vertex_map:
                    vertex_map[vertex].append(face)
                else:
                    vertex_map[vertex] = [face]

        for vertex in vertex_map:
            for face in vertex_map[vertex]:
                face.add_neigbors(vertex_map[vertex])

    def draw_seed(self):
        """
        Draw the fundamental cell and seed points.
        """
        self.writer.face(self.cell, dotted=True)

        for s in self.seed:
            s = LatticeCoords(s)
            self.writer.point(s)

        self.writer.write()

    def draw_cell(self):
        """
        Draw the lattice cell boundaries.
        """
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
        """
        Draw a star-shaped neighborhood around the seed.
        """
        neighbor_arr = {}
        self.draw_cell()

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                face = self.cell.translate(self.T1, self.T2, x, y)
                self.writer.face(face)

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
        """
        Draw edges connecting neighboring seed points.
        """
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
        """
        Generate all faces covering the visible region.
        """
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
            neighbors = []

            for k in range(6):
                p = self.wpow[k]
                sk = s.translate(p)
                if str(sk.w) in neighbor_arr:
                    neighbors.append(k)

            for i in range(len(neighbors) - 1):
                h = 6 - (neighbors[i + 1] - neighbors[i])
                m = 12 / h
                faces.append(
                    Face.generate(
                        s,
                        neighbors[i],
                        m,
                        param_mode=self.param_mode,
                        assym_mode=self.assym_angle,
                        separated_site_mode=self.separated_site_mode,
                    )
                )
        i_vals = np.arange(i_min, i_max)
        j_vals = np.arange(j_min, j_max)

        I_grid, J_grid = np.meshgrid(i_vals, j_vals, indexing="ij")

        translations = (
            I_grid[..., None] * self.T1.w + J_grid[..., None] * self.T2.w
        ).reshape(-1, 4)

        for face in faces:
            verts = face._vertices  # (Vf, 4)

            transformed = verts[None, :, :] + translations[:, None, :]

            transformed *= self.writer.n_tiles
            for tv in transformed:
                new_face = copy.copy(face)
                new_face.vertices = [LatticeCoords(t) for t in tv]
                self.faces.append(new_face)

    def find_corners(self):
        """
        Compute lattice bounds covering the visible canvas.

        Returns
        -------
        i_min : int
            Minimum lattice index along the first axis.
        i_max : int
            Maximum lattice index along the first axis.
        j_min : int
            Minimum lattice index along the second axis.
        j_max : int
            Maximum lattice index along the second axis.
        """
        W = [
            1,
            0.8660254037844386 + 0.5j,
            0.5 + 0.8660254037844386j,
            1j,
        ]

        if self.show_base:
            return -1, 2, -1, 2

        i_min = 1000
        i_max = -1000
        j_min = 1000
        j_max = -1000

        corners = [
            0,
            self.writer.size[2],
            self.writer.size[3] * 1j,
            self.writer.size[2] + self.writer.size[3] * 1j,
        ]

        for z in corners:
            z_ = plane_to_tile_coords(
                self.tess,
                W,
                z.real / self.writer.n_tiles,
                z.imag / self.writer.n_tiles,
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
        """
        Enable or disable parametric face generation.

        Parameters
        ----------
        mode : bool, optional
            If True, parametric mode is enabled.
        """
        self.param_mode = mode

    def set_show_underlying(self, show_underlying=False):
        """
        Toggle display of the underlying lattice.

        Parameters
        ----------
        show_underlying : bool, optional
            If True, underlying structure is shown.
        """
        self.show_underlying = show_underlying

    def set_tesselation(self, tess, tess_id):
        """
        Set the tessellation definition and initialize lattice vectors.

        Parameters
        ----------
        tess : dict
            Tessellation description dictionary.
        tess_id : str
            Identifier string for the tessellation.
        """
        self.tess = tess
        self.tess_id = tess_id

        self.T0 = LatticeCoords([0, 0, 0, 0])
        self.T1 = LatticeCoords(tess["T1"])
        self.T2 = LatticeCoords(tess["T2"])
        self.T3 = self.T1.translate(self.T2)

        self.seed = self.tess["Seed"]
        self.cell = Face([self.T0, self.T1, self.T3, self.T2])

    def set_writer(self, writer):
        """
        Set the rendering backend.

        Parameters
        ----------
        writer : object
            Writer instance used for rendering.
        """
        self.writer = writer
