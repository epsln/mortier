import numpy as np

from mortier.writer.writer import Writer


class TikzWriter(Writer):
    def __init__(
        self,
        filename,
        size=(0, 0, 14, 20),
        n_tiles=1,
        lacing_mode=False,
        bands_mode=False,
        bands_width=10,
        bands_angle=0,
        draw_borders=False,
    ):
        super().__init__(
            filename, size, n_tiles, lacing_mode, bands_angle, bands_mode, bands_width
        )
        self.output = []
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"
        self.draw_borders = draw_borders
        self.set_bounds(size)
        self.color = "black"
        self.bands_width = 1
        self.seen_line = {}

    def circle(self, p, r, color = "black"):
        self.output.append(f"\\filldraw[{self.color}] ({p.x}, {p.y}) circle ({r});")

    def point(self, p):
        self.output.append(f"\\filldraw[{self.color}] ({p.x}, {p.y}) circle (2pt);")

    def line(self, p0, p1, dotted=False, color="black"):
        pattern = ""
        if dotted:
            pattern = ", dotted"
        if self.in_bounds(p0) and self.in_bounds(p1):
            self.output.append(
                f"\\draw [draw={color}{pattern}] ({np.round(p0.x, 2)}, {np.round(p0.y, 2)}) -- ({np.round(p1.x, 2)}, {np.round(p1.y, 2)});"
            )

    def face(self, face, dotted=False):
        t = []
        pattern = ""
        if dotted:
            pattern = ",dotted"

        for p in face.mid_points:
            if str(p) not in self.intersect_points:
                self.intersect_points[str(p)] = np.random.randint(2, size=2)
            elif self.intersect_points[str(p)].sum() % 2 == 0:
                self.intersect_points[str(p)] = np.array(
                    [(x + 1) % 2 for x in self.intersect_points[str(p)]]
                )
        if self.lacing_mode or self.bands_mode:
            self.draw_outline_lines(face.vertices, face.mid_points)
        else:
            for _, v in enumerate(face.vertices):
                if not self.in_bounds(v):
                    t0 = "--".join(t)
                    self.output.append(f"\\draw[{self.color} {pattern}] {t0};")
                    t = []
                    continue
                t.append(f"({np.round(v.x, 2)}, {np.round(v.y, 2)})")
            if (dotted):  
                # We are probably drawing the base cell so connect all sides (WRONG)
                # t.append(f"({np.round(face.vertices[0].x, 2)}, {np.round(face.vertices[0].y, 2)})")
                pattern = ",dotted"
            t0 = "--".join(t)
            self.output.append(f"\\draw[{self.color} {pattern}] {t0};")

    def set_scale(self, scale):
        self.header = "\\begin{tikzpicture}[scale = " + str(scale) + "]\n"

    def set_caption(self, caption):
        self.footer += "\\caption{" + caption + "}\n"

    def set_label(self, label):
        self.footer += "\\label{fig:" + label + "}\n"

    def set_bounds(self, size):
        if self.draw_borders:
            self.header += (
                "\\draw (0, 0) rectangle + ("
                + str(size[2] - 2)
                + ","
                + str(size[3] - 2)
                + ");\n"
            )
        self.header += "\\clip (" + str(size[0] + 1) + "," + str(size[1] + 1) + ")"
        self.header += (
            "rectangle + (" + str(size[2] - 2) + "," + str(size[3] - 2) + ");\n"
        )

    def no_clip(self):
        self.header = "\\begin{tikzpicture}\n"

    def write(self):
        self.output = "\n".join(list(set(self.output)))
        with open(self.filename, "w+") as f:
            f.write(self.header)
            f.write(self.output)
            f.write(self.footer)

    def new(self, filename, size=None, n_tiles=None):
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"
        if not size:
            size = self.size
        if not n_tiles:
            n_tiles = self.n_tiles
        super().__init__(filename, size, n_tiles)
        self.set_bounds(size)
        self.seen_line = {}
        self.output = []
