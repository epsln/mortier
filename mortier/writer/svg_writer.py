from .writer import Writer 
import svgwrite
from svgwrite import cm, mm   

class SVGWriter(Writer):
    def __init__(self, filename, size):
        super().__init__(filename, size)
        svg_size = (
            size_x,
            size_y,
        )
        self.dwg = svgwrite.Drawing(
            f"{svg_name}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
        )

        dwg.viewbox(width=size_x, height=size_y)


    def line(self, p0, p1):
        self.dwg.add(
          dwg.line(
            start = (p0.x, p0.y),
            end = (p0.x, p0.y)

            stroke = "black",
            stroke_width = 0.05
            )

    def face(self, face):
        dwg.add(
          dwg.polygon(
            points=f,
            fill = "none",
            stroke="black",
            stroke_width = 0.5
            )
        )        

    def write(self):
        dwg.save()
