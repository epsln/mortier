from .writer import Writer 

class TikzWriter(Writer):
    def __init__(self, filename, size, n_tiles = 1):
        super().__init__(filename, size, n_tiles)
        self.output = []
        self.header = "\\begin{tikzpicture}\n"
        self.header += f"\\clip(0,0) rectangle {self.size};"
        self.footer = "\\end{tikzpicture}"
        
    def point(self, p):
        self.output.append(f"\\filldraw[black] ({p.x}, {p.y}) circle (2pt);")

    def line(self, p0, p1):
        self.output.append(f"\\draw [draw=black] ({p0.x}, {p0.y}) -- ({p1.x}, {p1.y});")

    def face(self, face, dotted = False):
        t = []
        pattern = ""
        if not self.in_bounds(face):
            return

        for v in face.vertices:
            t.append(f"({v.x}, {v.y})")
        if dotted: #We are probably drawing the base cell so connect all sides
            t.append(f"({face.vertices[0].x}, {face.vertices[0].y})")
            pattern = ",dotted"
        t0 = '--'.join(t)
        self.output.append(f"\\draw[black {pattern}] {t0};")

    def set_caption(self, caption):
        self.header += "\\caption{" + caption + "}\n"

    def set_label(self, label):
        self.header += "\\label{fig:" + label + "}\n"

    def write(self, caption = None, label = None):
        self.output = '\n'.join(list(set(self.output)))
        with open(self.filename, "w+") as f:
            f.write(self.header)
            f.write(self.output)
            f.write(self.footer)

    def new(self, filename, size = None, n_tiles = None):
        if not size:
            size = self.size
        if not n_tiles:
            n_tiles = self.n_tiles
        super().__init__(filename, size, n_tiles)
        self.output = []
