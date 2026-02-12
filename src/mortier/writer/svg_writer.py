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
        lacing_mode=False,
        bands_mode=False,
        bands_width=10,
        bands_angle=0,
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
        lacing_mode : bool, optional
            Enable lacing mode.
        bands_mode : bool, optional
            Enable band rendering mode.
        bands_width : float, optional
            Width of rendered bands.
        bands_angle : float, optional
            Angle used for band rendering.
        """
        super().__init__(
            filename,
            size,
            n_tiles,
            lacing_mode,
            bands_angle,
            bands_mode,
            bands_width,
        )

        svg_size = (size[2], size[3])

        self.dwg = svgwrite.Drawing(
            f"{filename}.svg",
            size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm"),
        )
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

        self.dwg.add(
            self.dwg.circle(
                center=(c.x, c.y),
                r=r,
                fill="none",
                stroke=f"rgb({color[0]}, {color[1]}, {color[2]})",
            )
        )

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

        self.dwg.add(
            self.dwg.line(
                start=(p0.x, p0.y),
                end=(p1.x, p1.y),
                stroke=f"rgb({color[0]}, {color[1]}, {color[2]})",
                stroke_width=0.5,
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

        self.dwg.save()
        return None

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
