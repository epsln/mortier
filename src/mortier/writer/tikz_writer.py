import numpy as np

from mortier.writer.writer import Writer


class TikzWriter(Writer):
    """
    TikZ-based writer for vector graphics output.

    This writer generates LaTeX/TikZ code for rendering tessellations
    as vector graphics.
    """

    def __init__(
        self,
        filename,
        size=(0, 0, 14, 20),
        n_tiles=1,
        draw_borders=False,
    ):
        """
        Initialize a TikZ writer.

        Parameters
        ----------
        filename : str
            Output .tex filename.
        size : tuple of float, optional
            Drawing bounds as (x, y, width, height).
        n_tiles : int, optional
            Number of tiles used for scaling or repetition.
        draw_borders : bool, optional
            Whether to draw bounding borders.
        """
        super().__init__(
            filename,
            size,
        )

        self.output = []
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"
        self.draw_borders = draw_borders
        self.set_bounds(size)
        self.color = "black"
        self.bands_width = 1
        self.seen_line = {}

    def circle(self, p, r, color="black"):
        """
        Draw a circle.

        Parameters
        ----------
        p : EuclideanCoords
            Center of the circle.
        r : float
            Radius of the circle.
        color : str, optional
            TikZ color name.

        Returns
        -------
        None
        """
        self.output.append(f"\\filldraw[{self.color}] ({p.x}, {p.y}) circle ({r});")

    def point(self, p):
        """
        Draw a point.

        Parameters
        ----------
        p : EuclideanCoords
            Point location.

        Returns
        -------
        None
        """
        self.output.append(f"\\filldraw[{self.color}] ({p.x}, {p.y}) circle (2pt);")

    def line(self, p0, p1, dotted=False, color="black"):
        """
        Draw a line segment.

        Parameters
        ----------
        p0 : EuclideanCoords
            Starting point.
        p1 : EuclideanCoords
            Ending point.
        dotted : bool, optional
            Draw the line as dotted.
        color : str, optional
            TikZ color name.

        Returns
        -------
        None
        """
        pattern = ", dotted" if dotted else ""

        if self.in_bounds(p0) and self.in_bounds(p1):
            self.output.append(
                "\\draw [draw="
                f"{color}{pattern}] "
                f"({np.round(p0.x, 2)}, {np.round(p0.y, 2)}) -- "
                f"({np.round(p1.x, 2)}, {np.round(p1.y, 2)});"
            )

    def face(self, face, dotted=False):
        """
        Draw a polygonal face.

        Parameters
        ----------
        face : Face
            Face to draw.
        dotted : bool, optional
            Draw the face edges as dotted.

        Returns
        -------
        None
        """
        path = []
        pattern = ",dotted" if dotted else ""

        for p in face.mid_points:
            if str(p) not in self.intersect_points:
                self.intersect_points[str(p)] = np.random.randint(2, size=2)
            elif self.intersect_points[str(p)].sum() % 2 == 0:
                self.intersect_points[str(p)] = np.array(
                    [(x + 1) % 2 for x in self.intersect_points[str(p)]]
                )

        if self.ornements:
            self.draw_outline_lines(face.vertices, face.mid_points)
        # TODO: Bezier MODE !!
        else:
            for v in face.vertices:
                if not self.in_bounds(v):
                    if path:
                        self.output.append(
                            f"\\draw[{self.color} {pattern}] {'--'.join(path)};"
                        )
                        path = []
                    continue

                path.append(f"({np.round(v.x, 2)}, {np.round(v.y, 2)})")

            if path:
                self.output.append(f"\\draw[{self.color} {pattern}] {'--'.join(path)};")

    def set_scale(self, scale):
        """
        Set the TikZ scale factor.

        Parameters
        ----------
        scale : float
            Scaling factor.

        Returns
        -------
        None
        """
        self.header = f"\\begin{{tikzpicture}}[scale = {scale}]\n"

    def set_caption(self, caption):
        """
        Add a LaTeX caption.

        Parameters
        ----------
        caption : str
            Caption text.

        Returns
        -------
        None
        """
        self.footer += f"\\caption{{{caption}}}\n"

    def set_label(self, label):
        """
        Add a LaTeX label.

        Parameters
        ----------
        label : str
            Label identifier.

        Returns
        -------
        None
        """
        self.footer += f"\\label{{fig:{label}}}\n"

    def set_bounds(self, size):
        """
        Define drawing bounds and clipping region.

        Parameters
        ----------
        size : tuple of float
            Bounds as (x, y, width, height).

        Returns
        -------
        None
        """
        if self.draw_borders:
            self.header += (
                "\\draw (0, 0) rectangle + (" f"{size[2] - 2},{size[3] - 2});\n"
            )

        self.header += (
            f"\\clip ({size[0] + 1},{size[1] + 1}) rectangle + "
            f"({size[2] - 2},{size[3] - 2});\n"
        )

    def no_clip(self):
        """
        Disable clipping.

        Returns
        -------
        None
        """
        self.header = "\\begin{tikzpicture}\n"

    def write(self):
        """
        Write the TikZ output to file.

        Returns
        -------
        None
        """
        self.output = "\n".join(set(self.output))

        with open(self.filename, "w+", encoding="utf-8") as f:
            f.write(self.header)
            f.write(self.output)
            f.write(self.footer)

    def new(self, filename, size=None, n_tiles=None):
        """
        Reset the writer for a new output file.

        Parameters
        ----------
        filename : str
            New output filename.
        size : tuple of float, optional
            New drawing bounds.
        n_tiles : int, optional
            Updated tile count.

        Returns
        -------
        None
        """
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"

        if size is None:
            size = self.size
        if n_tiles is None:
            n_tiles = self.n_tiles

        super().__init__(filename, size, n_tiles)
        self.set_bounds(size)
        self.seen_line = {}
        self.output = []
