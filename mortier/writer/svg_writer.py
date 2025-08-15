from .writer import Writer 
import svgwrite
from svgwrite import cm, mm   

class SVGWriter(Writer):
    def __init__(self, filename, size, n_tiles = 1):
        super().__init__(filename, size, n_tiles)
        svg_size = (
            size[0],
            size[1],
        )
        self.dwg = svgwrite.Drawing(
            f"{filename}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
        )

        self.dwg.viewbox(width=size[0], height=size[1])


    def line(self, p0, p1):
        self.dwg.add(
          self.dwg.line(
            start = (p0.x, p0.y),
            end = (p0.x, p0.y),

            stroke = "black",
            stroke_width = 0.05
            )
          )

    def face(self, face):
        f = [(f.x * 4, f.y * 4) for f in face.vertices]
        self.dwg.add(
          self.dwg.polygon(
            points=f,
            fill = "none",
            stroke="black",
            stroke_width = 0.5
            )
        )        

    def write(self):
        self.dwg.save()

    def new(self, filename, size = None, n_tiles = None):
        if not size:
            size = self.size
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

