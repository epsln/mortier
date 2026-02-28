import io

import svgwrite

from mortier.writer.writer import Writer


class SVGWriter(Writer):
    """
    SVG-based writer using the svgwrite library.

    This writer outputs vector graphics in SVG format and can optionally
    return the SVG content as a string for API usage.
    """

    def __init__(
        self,
        filename,
        size=(0, 0, 210, 297),
        n_tiles=1,
    ):
        """
        Initialize an SVG writer.

        Parameters
        ----------
        filename : str
            Output filename (without extension).
        size : tuple of float, optional
            Drawing bounds as (x, y, width, height), in millimeters.
        n_tiles : int, optional
            Number of tiles used for scaling or repetition.
        """
        super().__init__(
            filename,
            size,
            n_tiles,
        )

        svg_size = (size[2], size[3])

        self.dwg = svgwrite.Drawing(
            f"{filename}.svg",
            size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm"),
        )
        clip = self.dwg.clipPath(id="clip_area")
        clip.add(self.dwg.rect(insert=(0, 0), size=(self.size[2], self.size[3])))

        self.dwg.defs.add(clip)
        self.main_group = self.dwg.g(clip_path="url(#clip_area)")

        self.dwg.viewbox(width=size[2], height=size[3])

        self.api_mode = False

    def circle(self, c, r, color=(0, 0, 0)):
        """
        Draw a circle.

        Parameters
        ----------
        c : EuclideanCoords
            Center of the circle.
        r : float
            Radius of the circle.
        color : str, optional
            Stroke color.

        Returns
        -------
        None
        """
        if not self.in_bounds(c):
            return

        self.main_group.add(
            self.dwg.circle(
                center=(c.x, c.y),
                r=r,
                fill="none",
                stroke=f"rgb({color[0]}, {color[1]}, {color[2]})",
            )
        )

    def point(self, p, color=(0, 0, 0)):
        """
        Draw a point, which is simply a very small circle.

        Parameters
        ----------
        c : EuclideanCoords
            Center of the point.
        color : str, optional
            Stroke color.

        Returns
        -------
        None
        """
        self.circle(p, 0.001, color)

    def line(self, p0, p1, color=(0, 0, 0)):
        """
        Draw a line segment.

        Parameters
        ----------
        p0 : EuclideanCoords
            Starting point.
        p1 : EuclideanCoords
            Ending point.
        color : str, optional
            Stroke color.

        Returns
        -------
        None
        """
        if not self.in_bounds(p0) and not self.in_bounds(p1):
            return

        self.main_group.add(
            self.dwg.line(
                start=(p0.x, p0.y),
                end=(p1.x, p1.y),
                stroke=f"rgb({self.color_line[0]}, {self.color_line[1]}, {self.color_line[2]})",
                stroke_width=0.1,
            )
        )

    def write(self):
        """
        Write the SVG output.

        Returns
        -------
        str or None
            SVG content as a string if `api_mode` is enabled,
            otherwise None.
        """
        if self.api_mode:
            buf = io.StringIO()
            self.dwg.write(buf)
            return buf.getvalue()
        self.dwg.add(self.main_group)
        self.dwg.save()
        return None

    def polygon(self, points, outline, fill = None):
        if fill:
            fill_opacity = "1"
        else:
            fill_opacity = "0"
            fill = [0, 0, 0]

        self.main_group.add(
            self.dwg.polygon(
                points,
                fill=f"rgb({fill[0]}, {fill[1]}, {fill[2]})",
                fill_opacity = fill_opacity,
                stroke=f"rgb({outline[0]}, {outline[1]}, {outline[2]})",
                stroke_width = 0.1
            )
        )

    def set_color_bg(self, color):
        if color:
            self.color_bg = color
            self.dwg.add(
                self.dwg.rect(
                    insert=(0, 0),
                    rx=None,
                    ry=None,
                    size=("100%", "100%"),
                    fill=f"rgb({self.color_bg[0]}, {self.color_bg[1]}, {self.color_bg[2]})",
                )
            )

    def new(self, filename, size=None, n_tiles=None):
        """
        Reset the writer for a new SVG output.

        Parameters
        ----------
        filename : str
            New output filename (without extension).
        size : tuple of float, optional
            New drawing bounds.
        n_tiles : int, optional
            Updated tile count.

        Returns
        -------
        None
        """
        if size is None:
            size = self.size

        if n_tiles is None:
            n_tiles = self.n_tiles

        svg_size = (size[2], size[3])

        super().__init__(filename, size, n_tiles)

        self.dwg = svgwrite.Drawing(
            f"{filename}.svg",
            size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm"),
        )
        self.dwg.viewbox(width=size[2], height=size[3])
