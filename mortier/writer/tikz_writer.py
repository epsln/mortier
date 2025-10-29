from .writer import Writer 
import numpy as np

class TikzWriter(Writer):
    def __init__(self, filename, size, n_tiles = 1):
        super().__init__(filename, size, n_tiles)
        self.output = []
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"
        self.set_bounds(size) 
        
    def point(self, p):
        self.output.append(f"\\filldraw[black] ({p.x}, {p.y}) circle (2pt);")

    def line(self, p0, p1):
        self.output.append(f"\\draw [draw=black] ({np.round(p0.x, 2)}, {np.round(p0.y, 2)}) -- ({np.round(p1.x, 2)}, {np.round(p1.y, 2)});")

    def face(self, face, dotted = False):
        t = []
        pattern = ""

        for v in face.vertices:
            if not self.in_bounds(v):
                continue
            t.append(f"({np.round(v.x, 2)}, {np.round(v.y, 2)})")
        if dotted: #We are probably drawing the base cell so connect all sides (WRONG)
            #t.append(f"({face.vertices[0].x}, {face.vertices[0].y})")
            pattern = ",dotted"
        t0 = '--'.join(t)
        self.output.append(f"\\draw[black {pattern}] {t0};")

    def set_caption(self, caption):
        self.footer += "\\caption{" + caption + "}\n"

    def set_label(self, label):
        self.footer += "\\label{fig:" + label + "}\n"

    def set_bounds(self, size):
        self.header += "\\clip ("+ str(size[0]) + ","+ str(size[1]) + ")"
        self.header += "rectangle + (" + str(size[2]) + "," + str(size[3])+");\n"

    def no_clip(self):
        self.header = "\\begin{tikzpicture}\n"

    def write(self, caption = None, label = None):
        self.output = '\n'.join(list(set(self.output)))
        with open(self.filename, "w+") as f:
            f.write(self.header)
            f.write(self.output)
            f.write(self.footer)

    def new(self, filename, size = None, n_tiles = None):
        self.header = "\\begin{tikzpicture}\n"
        self.footer = "\n\\end{tikzpicture}\n"
        if not size:
            size = self.size
        if not n_tiles:
            n_tiles = self.n_tiles
        super().__init__(filename, size, n_tiles)
        self.set_bounds(size) 
        self.output = []
