from mortier.writer.writer import Writer 
import svgwrite
from svgwrite import cm, mm   

class SVGWriter(Writer):
    def __init__(self, filename, size = (0, 0, 210, 297), n_tiles = 1, lacing_mode = False, lacing_angle = False, bands_mode = False, bands_width = 10, bands_angle = 0):
        super().__init__(filename, size, n_tiles, lacing_mode, bands_angle, bands_mode, bands_width)
        svg_size = (
            size[2],
            size[3],
        )
        self.dwg = svgwrite.Drawing(
            f"{filename}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
        )

        self.dwg.viewbox(width=size[2], height=size[3])
    
    def circle(self, c, r):
        if not self.in_bounds(c):
            return
        self.dwg.add(
            self.dwg.circle(
                center = (c.x, c.y),
                r = r,
                fill = "none",
                stroke = "black")
            )


    def line(self, p0, p1, color = "black"):
        if not self.in_bounds(p0) and not self.in_bounds(p1):
            return
        self.dwg.add(
          self.dwg.line(
            start = (p0.x, p0.y),
            end = (p1.x, p1.y),

            stroke = color,
            stroke_width = 0.5
            )
          )

    def write(self):
        self.dwg.save()

    def new(self, filename, size = None, n_tiles = None):
        if not size:
            size = self.svg_size
            svg_size = (
                size[0],
                size[1],
            )
        if not n_tiles:
            n_tiles = self.n_tiles
        super().__init__(filename, size, n_tiles)
        self.dwg = svgwrite.Drawing(
            f"{filename}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
        )

