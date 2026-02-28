from PIL import Image, ImageDraw

from mortier.writer.writer import Writer


class BitmapWriter(Writer):
    """
    Bitmap-based writer using PIL for raster rendering.

    This writer outputs drawings to a bitmap image (PNG, JPG, etc.)
    using the Pillow (PIL) library.
    """

    def __init__(
        self,
        filename,
        size=(0, 0, 1920, 1080),
        n_tiles=100,
    ):
        """
        Initialize a bitmap writer.

        Parameters
        ----------
        filename : str
            Output image filename.
        size : tuple of int, optional
            Drawing bounds as (x, y, width, height).
        n_tiles : int, optional
            Number of tiles used for scaling or repetition.
        """
        super().__init__(
            filename,
            size,
            n_tiles,
        )

        self.image = Image.new("RGB", (size[2], size[3]))
        self.output = ImageDraw.Draw(self.image)

    def point(self, p, color=(255, 255, 255)):
        """
        Draw a point on the bitmap.

        Parameters
        ----------
        p : EuclideanCoords
            Point to draw.
        color : tuple of int, optional
            RGB color of the point.

        Returns
        -------
        None
        """
        self.output.point((p.x, p.y), fill=color)

    def arc(self, bbox, start, end):
        """
        Draw an arc on the bitmap.

        Parameters
        ----------
        bbox : tuple
            Bounding box (x0, y0, x1, y1).
        start : float
            Starting angle in degrees.
        end : float
            Ending angle in degrees.

        Returns
        -------
        None
        """
        self.output.arc(bbox, start=start, end=end)

    def circle(self, c, r, color=(255, 255, 255)):
        """
        Draw a circle.

        Parameters
        ----------
        c : EuclideanCoords
            Center of the circle.
        r : float
            Radius of the circle.
        color : tuple of int, optional
            RGB color of the outline.

        Returns
        -------
        None
        """
        p0 = (c.x - r, c.y - r)
        p1 = (c.x + r, c.y + r)
        self.output.ellipse([p0, p1], outline=color)

    def set_color_bg(self, color):
        if color:
            self.color_bg = color
            self.image.paste(color, (0, 0, self.image.size[0], self.image.size[1]))

    def line(self, p0, p1, color=(255, 255, 255)):
        """
        Draw a line segment.

        Parameters
        ----------
        p0 : EuclideanCoords
            Starting point.
        p1 : EuclideanCoords
            Ending point.
        color : tuple or str, optional
            Line color (RGB tuple or named string).

        Returns
        -------
        None
        """
        self.output.line(
            [(p0.x, p0.y), (p1.x, p1.y)],
            fill=color,
            width=1,
        )

    def polygon(self, points, outline, fill = None):
        self.output.polygon(points, fill=fill, outline=outline)

    def write(self):
        """
        Save the bitmap image to disk.

        Returns
        -------
        None
        """
        self.image.save(self.filename)

    def new(self, filename, size=None, n_tiles=None):
        """
        Reset the writer with a new output file.

        Parameters
        ----------
        filename : str
            New output filename.
        size : tuple of int, optional
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

        super().__init__(filename, size, n_tiles)
        self.image = Image.new("RGB", (size[2], size[3]))
        self.output = ImageDraw.Draw(self.image)
