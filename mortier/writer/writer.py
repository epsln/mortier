import math
import numpy as np
from mortier.coords import EuclideanCoords

class Writer():
    def __init__(self, filename, size, n_tiles = 1, lacing_mode = False, lacing_angle = False, bands_mode = False, bands_width = 10, bands_angle = 0):
        self.filename = filename
        self.n_tiles = int(n_tiles)
        self.size = size
        self.intersect_points = {}
        self.lacing_mode = lacing_mode 
        self.bands_mode = bands_mode
        self.bands_width = bands_width 
        self.bands_angle = bands_angle 
        assert not (self.lacing_mode and self.bands_mode)

    def set_band_angle(self, bands_angle):
        self.bands_angle = bands_angle

    def line_offset(self, p1, p2, d):
        """Return the two offset lines at distance ±d from the base line."""
        dir_vec = p2.translate(p1.scale(-1))
        if dir_vec.len() < 1e-9:
            return (p1, p2), (p1, p2)
        perp = EuclideanCoords([-dir_vec.y, dir_vec.x]).normalise()
        return (p1.translate(perp.scale(d)), p2.translate(perp.scale(d))), \
               (p1.translate(perp.scale(-d)), p2.translate(perp.scale(-d)))

    def intersect(self, p1, p2, p3, p4):
        """Find intersection of two lines (p1,p2) and (p3,p4)."""
        A1 = p2.y - p1.y
        B1 = p1.x - p2.x
        C1 = A1 * p1.x + B1 * p1.y

        A2 = p4.y - p3.y
        B2 = p3.x - p4.x
        C2 = A2 * p3.x + B2 * p3.y

        det = A1 * B2 - A2 * B1
        if abs(det) < 1e-8:
            # Lines are parallel; return midpoint approximation
            return p2.translate(p3).scale(1/2).numpy()
        x = (B2 * C1 - B1 * C2) / det
        y = (A1 * C2 - A2 * C1) / det
        return EuclideanCoords([x, y]).numpy()

    def normalize(self, v):
        n = np.linalg.norm(v)
        if n < 1e-9:
            return np.zeros_like(v)
        return v / n

    def perp(self, v):
        return np.array([-v[1], v[0]])

    def clean_points(points, eps=1e-6):
        pts = [np.array(p, dtype=float) for p in points]
        if not pts:
            return []
        out = [pts[0]]
        for p in pts[1:]:
            if np.linalg.norm(p - out[-1]) > eps:
                out.append(p)
        return out

    def vertex_miter(self, p_prev, p_curr, p_next, half_w, end = False):
        """Compute offset points (left/right) at vertex p_curr using miter join."""
        v_prev = p_curr - p_prev
        v_next = p_next - p_curr
        nv_prev = self.normalize(v_prev)
        nv_next = self.normalize(v_next)
        EPS = 1e-9

        if np.linalg.norm(nv_prev) < EPS and np.linalg.norm(nv_next) < EPS:
            return p_curr + np.array([half_w, 0]), p_curr - np.array([half_w, 0])

        if np.linalg.norm(nv_prev) < EPS:
            n = self.normalize(self.perp(nv_next))
            d = self.normalize(nv_next)
            cut = half_w/np.tan(end + np.pi/2)
            return p_curr + n * half_w - d * cut, p_curr - n * half_w

        if np.linalg.norm(nv_next) < EPS:
            n = self.normalize(self.perp(nv_prev))
            d = self.normalize(nv_prev)
            cut = -half_w/np.tan(end + np.pi/2)
            return p_curr + n * half_w - d * cut, p_curr - n * half_w

        n1 = self.normalize(self.perp(nv_prev))
        n2 = self.normalize(self.perp(nv_next))
        bis = n1 + n2
        bis_len = np.linalg.norm(bis)
        if bis_len < 1e-6:
            return p_curr + n2 * half_w, p_curr - n2 * half_w
        b = bis / bis_len
        denom = np.dot(b, n2)
        miter_len = half_w / denom
        pos = p_curr + b * miter_len
        neg = p_curr - b * miter_len
        return pos, neg

    def offset_segment(self, p0, p1, direction, cut_length = 5):
        """Return outer and inner offset lines for a single segment."""
        p0 = p0.numpy() 
        p1 = p1.numpy()
        dir_vec = p1 - p0
        n = self.normalize(self.perp(dir_vec))
        d = self.normalize(dir_vec)
        off = n * (self.bands_width / 2)
        l = p0 - p1
        #print(p0, p1, (l[0]**2 + l[1]**2)**0.5, cut_length)
        if direction == "left":
            p0_cut = p0 + d * cut_length
            #print("left", p0, p0_cut, off, p0_cut - off, n)
            return tuple(p0_cut - off)
        else:
            p1_cut = p1 - d * cut_length
            #print("right", p1, p1_cut, off, p1_cut - off, n)
            return tuple(p1_cut - off)


    def outline_lines(self, points, mid_points, closed=True):
        """
        Compute pairs of offset polylines (outer and inner) for a given polyline.
        """
        #pts = clean_points(points)
        pts = points 
        n = len(pts) 
        if n < 2:
            return [], []

        half_w = self.bands_width / 2.0
        pos_ring = []
        neg_ring = []

        for i in range(n):
            if closed:
                p_prev = pts[(i - 1) % n]
                p_curr = pts[i]
                p_next = pts[(i + 1) % n]
            else:
                p_curr = pts[i]
                p_prev = pts[i - 1] if i > 0 else pts[i]
                p_next = pts[i + 1] if i < n - 1 else pts[i]

            if i == 0 or i == n - 1:
                end = self.bands_angle
            else:
                end = False

            pos, inner= self.vertex_miter(p_prev.numpy(), p_curr.numpy(), p_next.numpy(), half_w, end)
            theta = self.bands_angle 
            if theta < np.pi/4:
                theta_ = np.pi/2 - theta*2 
                add_length = -(half_w/ np.cos(theta_) - half_w * np.tan(theta_))
                cut_length = half_w / np.cos(theta_) + half_w* np.tan(theta_) 
            else:
                theta_ = theta * 2 - np.pi/2 
                add_length = -(half_w / np.cos(theta_) + half_w * np.tan(theta_))
                cut_length = half_w / np.cos(theta_) - half_w * np.tan(theta_)

            if str(p_curr) in self.intersect_points:
                cut = self.offset_segment(p_curr, p_next, "left", cut_length = cut_length)

                if self.intersect_points[str(p_curr)][0] == 1 and not self.bands_mode:
                    cut = self.offset_segment(p_curr, p_next, "left", cut_length = cut_length)
                    col_r = "red"
                else:
                    cut = self.offset_segment(p_curr, p_next, "left", cut_length = add_length)
                    col_r = "orange"
                if self.bands_mode:
                    cut = self.offset_segment(p_curr, p_next, "left", cut_length = cut_length)

            elif str(p_next) in self.intersect_points:
                #print("green")
                cut_ = self.offset_segment(p_curr, p_next, "right", cut_length = cut_length)
                col_l = "green"
                if self.intersect_points[str(p_next)][1] == 1:
                    cut_ = self.offset_segment(p_curr, p_next, "right", cut_length = cut_length)
                    col_l = "green"
                else:
                    #print("cyan")
                    cut_ = self.offset_segment(p_curr, p_next,  "right", cut_length = add_length)
                    col_l = "cyan"
                if self.bands_mode: 
                    cut_ = self.offset_segment(p_curr, p_next, "right", cut_length = cut_length)

                cut = EuclideanCoords([cut[0], cut[1]])
                inner = EuclideanCoords(inner)
                cut_ = EuclideanCoords([cut_[0], cut_[1]])
                self.line(cut, inner)
                self.line(inner, cut_)

            pos_ring.append(pos)
            neg_ring.append(inner)

        return pos_ring, neg_ring

    def draw_outline_lines(self, points, mid_points, color="red", closed=True):
        pos_ring, neg_ring = self.outline_lines(points, mid_points, closed)

        for i in range(len(pos_ring) - 1):
            p0 = EuclideanCoords([pos_ring[i][0], pos_ring[i][1]])
            p1 = EuclideanCoords([pos_ring[i + 1][0], pos_ring[i + 1][1]])
            self.line(p0, p1)

    def point(self, p):
        pass

    def line(self, p0, p1):
        pass

    def face(self, face, dotted = False, color = (255, 255, 255)):
        #Put me in writer...
        t = []
        pattern = ""

        for p in face.mid_points:
            if str(p) not in self.intersect_points:
                self.intersect_points[str(p)] = np.random.randint(2, size = 2) 
            elif self.intersect_points[str(p)].sum() % 2 == 0:
                self.intersect_points[str(p)] = [(x + 1) % 2 for x in self.intersect_points[str(p)]] 
        if self.lacing_mode or self.bands_mode:
            self.draw_outline_lines(face.vertices, face.mid_points)
        else:
            for i in range(len(face.vertices)):
                self.line(face.vertices[i], face.vertices[(i + 1) % len(face.vertices)], color = color)

    def in_bounds(self, v):
        if math.isnan(v.x) or math.isnan(v.y) or math.isinf(v.x) or math.isinf(v.y):
            return False
        if not (self.size[0] < v.x < self.size[0] + self.size[2] and self.size[1] < v.y < self.size[1] + self.size[3]):
            return False
        return True

    def set_label(self, label):
        pass

    def set_caption(self, caption):
        pass

    def new(self, filename, size = None, n_tiles = None):
        pass
