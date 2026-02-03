import math
import numpy as np
from mortier.coords import EuclideanCoords
from hypertiling.graphics.plot import geodesic_arc

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
        self.bezier_curve = False 
        self.hatch_fill_parameters = {"angle": None, "spacing": 20, "crosshatch": False} 
        assert not (self.bezier_curve and self.hatch_fill_parameters["angle"])
        assert not (self.lacing_mode and self.bands_mode)

    def set_band_angle(self, bands_angle):
        self.bands_angle = bands_angle

    def set_hatch_fill(self, hatch_fill_parameters):
        assert not (self.bezier_curve and hatch_fill_angle["angle"])
        self.hatch_fill_parameters = hatch_fill_parameters

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
        p_prev = p_prev.numpy()
        p_curr = p_curr.numpy()
        p_next = p_next.numpy()
        v_prev = p_curr - p_prev
        v_next = p_next - p_curr
        nv_prev = self.normalize(v_prev)
        nv_next = self.normalize(v_next)
        EPS = 1e-9

        if np.linalg.norm(nv_prev) < EPS and np.linalg.norm(nv_next) < EPS:
            return EuclideanCoords(p_curr + np.array([half_w, 0])), EuclideanCoords(p_curr - np.array([half_w, 0]))

        if np.linalg.norm(nv_prev) < EPS:
            n = self.normalize(self.perp(nv_next))
            d = self.normalize(nv_next)
            cut = half_w/np.tan(end + np.pi/2)
            return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(p_curr - n * half_w)

        if np.linalg.norm(nv_next) < EPS:
            n = self.normalize(self.perp(nv_prev))
            d = self.normalize(nv_prev)
            cut = -half_w/np.tan(end + np.pi/2)
            return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(p_curr - n * half_w)

        n1 = self.normalize(self.perp(nv_prev))
        n2 = self.normalize(self.perp(nv_next))
        bis = n1 + n2
        bis_len = np.linalg.norm(bis)
        if bis_len < 1e-6:
            return EuclideanCoords(p_curr + n2 * half_w), EuclideanCoords(p_curr - n2 * half_w)
        b = bis / bis_len
        denom = np.dot(b, n2)
        miter_len = half_w / denom
        pos = p_curr + b * miter_len
        neg = p_curr - b * miter_len
        return EuclideanCoords(pos), EuclideanCoords(neg)

    def offset_segment(self, p0, p1, cut_length, end_cut = False):
        """Return outer and inner offset lines for a single segment."""
        p0 = p0.numpy() 
        p1 = p1.numpy()
        dir_vec = p1 - p0
        n = self.normalize(self.perp(dir_vec))
        d = self.normalize(dir_vec)
        off = n * (self.bands_width / 2)
        l = p0 - p1
        if not end_cut:
            p0_cut = p0 + d * cut_length
            return EuclideanCoords(p0_cut - off)
        else:
            p1_cut = p1 - d * cut_length
            return EuclideanCoords(p1_cut - off)

    def compute_cut_length(self, theta, half_w):
        if theta < np.pi/4:
            theta_ = np.pi/2 - theta*2 
            add_length = -(half_w/ np.cos(theta_) - half_w * np.tan(theta_))
            cut_length = half_w / np.cos(theta_) + half_w* np.tan(theta_) 
        else:
            theta_ = theta * 2 - np.pi/2 
            add_length = -(half_w / np.cos(theta_) + half_w * np.tan(theta_))
            cut_length = half_w / np.cos(theta_) - half_w * np.tan(theta_)
        if self.bands_mode:
            add_length = cut_length
        return cut_length, add_length

    def hatch_fill(self, face, cross_hatch = False):
        lines = []
        angle = self.hatch_fill_parameters["angle"]
        if cross_hatch:
            angle += np.pi/2

        f_rotated = face.rotate(-angle)
        ys = [v.y for v in f_rotated.vertices]
        y_min, y_max = min(ys), max(ys)


        y = y_min + self.hatch_fill_parameters["spacing"] 
        while y < y_max:
            xs = []

            for j in range(len(f_rotated.vertices)):
                p0 = f_rotated.vertices[j]
                p1 = f_rotated.vertices[(j + 1) % len(f_rotated.vertices)]

                if p0.y == p1.y:
                    continue

                if (p0.y <= y < p1.y) or (p1.y <= y < p0.y):
                    t = (y - p0.y) / (p1.y - p0.y)
                    x = p0.x + t * (p1.x - p0.x)
                    xs.append(x)

            xs.sort()

            for k in range(0, len(xs), 2):
                if k + 1 < len(xs):
                    p_start = EuclideanCoords([xs[k], y])
                    p_end   = EuclideanCoords([xs[k + 1], y])
                    p_start = p_start.rotate(angle)
                    p_end   = p_end.rotate(angle)
        
                    lines.append((p_start, p_end))
                    self.line(p_start, p_end)

            y += self.hatch_fill_parameters["spacing"]

    def outline_lines(self, points):
        """
        Compute pairs of offset polylines (outer and inner) for a given polyline.
        """
        pts = points 
        n = len(pts) 
        if n < 2:
            return [], []

        half_w = self.bands_width / 2.0
        pos_ring = []
        neg_ring = []

        for i in range(n):
            p_prev = pts[(i - 1) % n]
            p_curr = pts[i]
            p_next = pts[(i + 1) % n]

            #p_curr = pts[i]
            #p_prev = pts[i - 1] if i > 0 else pts[i]
            #p_next = pts[i + 1] if i < n - 1 else pts[i]

            if i == 0 or i == n - 1:
                end = self.bands_angle
            else:
                end = False

            pos_midpoint, neg_midpoint = self.vertex_miter(p_prev, p_curr, p_next, half_w, end)

            if str(p_curr) in self.intersect_points:
                inter_p = self.intersect_points[str(p_curr)]
                cut_length, add_length = self.compute_cut_length(inter_p["angle"], half_w)
                beg_point = self.offset_segment(p_curr, p_next, cut_length)
                if inter_p['state'][0] == 1:
                    beg_point = self.offset_segment(p_curr, p_next, cut_length)
                else:
                    beg_point = self.offset_segment(p_curr, p_next, add_length)

            elif str(p_next) in self.intersect_points:
                inter_p = self.intersect_points[str(p_next)]
                cut_length, add_length = self.compute_cut_length(inter_p["angle"], half_w)
                end_point = self.offset_segment(p_curr, p_next, cut_length, end_cut = True)
                if inter_p['state'][1] == 1:
                    end_point = self.offset_segment(p_curr, p_next, cut_length, end_cut = True)
                else:
                    end_point = self.offset_segment(p_curr, p_next, add_length, end_cut = True)

                neg_ring.append(beg_point)
                neg_ring.append(neg_midpoint)
                neg_ring.append(end_point)

            pos_ring.append(pos_midpoint)
        
        #Hacky way to get the closing of the inside polygon 
        s0 = EuclideanCoords([pos_ring[0].x - pos_ring[1].x, pos_ring[0].y - pos_ring[1].y])
        s1 = EuclideanCoords([pos_ring[-2].x - pos_ring[-1].x, pos_ring[-2].y - pos_ring[-1].y])

        t = ( s1.x * (pos_ring[0].y - pos_ring[-2].y) - s1.y * (pos_ring[0].x - pos_ring[-2].x)) / (-s1.x * s0.y + s0.x * s1.y)
        
        x = EuclideanCoords([pos_ring[0].x + (t * s0.x), pos_ring[0].y + (t * s0.y)])

        pos_ring[0] = x 
        pos_ring[-1] = x 
        return pos_ring, neg_ring

    def draw_outline_lines(self, points, color="red"):
        pos_ring, neg_ring = self.outline_lines(points)
        for i in range(0, len(pos_ring) - 1, 2):
            p0 = pos_ring[i]
            p1 = pos_ring[i + 1]
            p2 = pos_ring[(i + 2) % len(pos_ring)]
            
            if self.bezier_curve:
                l = self.quadratic_bezier(p0, p1, p2)
                for j in range(len(l)- 1):
                    self.line(l[j], l[j + 1]) 
            else:
                self.line(p0, p1)
                self.line(p1, p2)
            
        for i in range(0, len(neg_ring) - 2, 3):
            p0 = neg_ring[i]
            p1 = neg_ring[i + 1]
            p2 = neg_ring[i + 2]
            
            if self.bezier_curve:
                l = self.quadratic_bezier(p0, p1, p2)
                for j in range(len(l) - 1):
                    self.line(l[j], l[j + 1]) 
            else:
                self.line(p0, p1)
                self.line(p1, p2)

    def circle(self, c, r, color = (255, 255, 255)):
        pass

    def point(self, p):
        pass

    def line(self, p0, p1):
        pass

    def quadratic_bezier(self, p0, p1, p2, steps=10):
        #TODO: Maybe N order bezier with all vertices ?
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t)**2 * p0.x + 2 * (1 - t) * t * p1.x + t**2 * p2.x
            y = (1 - t)**2 * p0.y + 2 * (1 - t) * t * p1.y + t**2 * p2.y
            points.append(EuclideanCoords([x, y]))
        return points
 
    def face(self, face, dotted = False, color = (255, 255, 255)):
        t = []
        pattern = ""
        n_vert = len(face.vertices)

        #TODO: Put this in its own function
        for p, angle in face.mid_points:
            if str(p) not in self.intersect_points:
                self.intersect_points[str(p)] = {"state": np.random.randint(2, size = 2),
                                                 "angle": angle}
            elif self.intersect_points[str(p)]["state"].sum() % 2 == 0:
                self.intersect_points[str(p)] = {"state": np.array([(x + 1) % 2 for x in self.intersect_points[str(p)]["state"]]),
                                                 "angle": angle} 

        if self.lacing_mode or self.bands_mode:
            self.draw_outline_lines(face.vertices)
        else:
            if self.bezier_curve:
                #TODO: Also own function
                for i in range(0, len(face.vertices) - 2, 2):
                    p0 = face.vertices[i] 
                    p1 = face.vertices[i + 1] 
                    p2 = face.vertices[i + 2] 
                    l = self.quadratic_bezier(p0, p1, p2)
                    for j in range(len(l) - 1):
                        self.line(l[j], l[j + 1]) 
            else:
                for i in range(len(face.vertices)):
                    self.line(face.vertices[i], face.vertices[(i + 1) % len(face.vertices)])
        if self.hatch_fill_parameters["angle"] is not None:
            self.hatch_fill(face)
            if self.hatch_fill_parameters["crosshatch"]:
                self.hatch_fill(face, self.hatch_fill_parameters["crosshatch"])

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
