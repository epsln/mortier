from .writer import Writer 
import svgwrite
from svgwrite import cm, mm   

class SVGWriter(Writer):
    def __init__(self, filename, size, n_tiles = 1):
        super().__init__(filename, size, n_tiles)
        svg_size = (
            size[2],
            size[3],
        )
        self.dwg = svgwrite.Drawing(
            f"{filename}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
        )

        self.dwg.viewbox(width=size[2], height=size[3])


    def line(self, p0, p1, color):
        self.dwg.add(
          self.dwg.line(
            start = (p0.x, p0.y),
            end = (p1.x, p1.y),

            stroke = color,
            stroke_width = 0.5
            )
          )

    def face(self, face, color = "black", stroke_width = 1):
        f = [(f.x, f.y) for f in face.vertices]
        self.dwg.add(
          self.dwg.polygon(
            points=f,
            fill = "none",
            stroke= color,
            stroke_width = stroke_width 
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

