import math

import numpy as np

from mortier.coords import EuclideanCoords
from mortier.enums import HatchType


class Writer:
    """
    Base rendering backend for tessellations.

    This class provides geometric utilities (offsets, intersections,
    hatching, outlines) and defines the drawing interface to be
    implemented by concrete writer backends.
    """

    def __init__(
        self,
        filename,
        size=(0, 0, 1920, 1080),
        n_tiles=1,
        lacing_mode=False,
        bands_mode=False,
        bands_width=10,
        bands_angle=0,
    ):
        """
        Initialize a writer.

        Parameters
        ----------
        filename : str
            Output filename.
        size : tuple, optional
            Drawing bounds as (x, y, width, height).
        n_tiles : int, optional
            Global scaling factor for tessellations.
        lacing_mode : bool, optional
            Enable lacing (interleaving) rendering mode.
        bands_mode : bool, optional
            Enable band-based rendering mode.
        bands_width : float, optional
            Width of bands used in band mode.
        bands_angle : float, optional
            Angle used for band clipping at endpoints.
        """
        self.filename = filename
        self.n_tiles = int(n_tiles)
        self.size = size

        self.intersect_points = {}
        self.lacing_mode = lacing_mode
        self.bands_mode = bands_mode
        self.bands_width = bands_width
        self.bands_angle = bands_angle

        self.bezier_curve = False
        self.hatch_fill_parameters = {
            "angle": None,
            "spacing": 5,
            "crosshatch": False,
            "type": None,
        }

        assert not (self.bezier_curve and self.hatch_fill_parameters["angle"])
        assert not (self.lacing_mode and self.bands_mode)

    def set_band_angle(self, bands_angle):
        """
        Set the band clipping angle.

        Parameters
        ----------
        bands_angle : float
            Angle value in radians.
        """
        self.bands_angle = bands_angle

    def set_hatch_fill(self, hatch_fill_parameters):
        """
        Set hatch fill parameters.

        Parameters
        ----------
        hatch_fill_parameters : dict
            Hatch configuration dictionary.
        """
        assert not (self.bezier_curve and hatch_fill_parameters["angle"])
        self.hatch_fill_parameters = hatch_fill_parameters

    def line_offset(self, p1, p2, d):
        """
        Compute offset lines parallel to a base segment.

        Parameters
        ----------
        p1, p2 : EuclideanCoords
            Endpoints of the base segment.
        d : float
            Offset distance.

        Returns
        -------
        line_pos : tuple
            Offset segment at +d.
        line_neg : tuple
            Offset segment at -d.
        """
        dir_vec = p2.translate(p1.scale(-1))
        if dir_vec.len() < 1e-9:
            return (p1, p2), (p1, p2)

        perp = EuclideanCoords([-dir_vec.y, dir_vec.x]).normalise()

        return (
            (p1.translate(perp.scale(d)), p2.translate(perp.scale(d))),
            (p1.translate(perp.scale(-d)), p2.translate(perp.scale(-d))),
        )

    def intersect(self, p1, p2, p3, p4):
        """
        Compute intersection of two lines.

        Parameters
        ----------
        p1, p2 : EuclideanCoords
            Endpoints of the first line.
        p3, p4 : EuclideanCoords
            Endpoints of the second line.

        Returns
        -------
        ndarray
            Intersection point as a NumPy array.
        """
        a1 = p2.y - p1.y
        b1 = p1.x - p2.x
        c1 = a1 * p1.x + b1 * p1.y

        a2 = p4.y - p3.y
        b2 = p3.x - p4.x
        c2 = a2 * p3.x + b2 * p3.y

        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-8:
            return p2.translate(p3).scale(0.5).numpy()

        x = (b2 * c1 - b1 * c2) / det
        y = (a1 * c2 - a2 * c1) / det

        return EuclideanCoords([x, y]).numpy()

    def normalize(self, v):
        """
        Normalize a vector.

        Parameters
        ----------
        v : ndarray
            Input vector.

        Returns
        -------
        ndarray
            Normalized vector.
        """
        n = np.linalg.norm(v)
        if n < 1e-9:
            return np.zeros_like(v)
        return v / n

    def perp(self, v):
        """
        Compute a perpendicular vector.

        Parameters
        ----------
        v : ndarray
            Input vector.

        Returns
        -------
        ndarray
            Perpendicular vector.
        """
        return np.array([-v[1], v[0]])

    def vertex_miter(self, p_prev, p_curr, p_next, half_w, end=False):
        """
        Compute miter join offsets at a vertex.

        Parameters
        ----------
        p_prev, p_curr, p_next : EuclideanCoords
            Consecutive polyline vertices.
        half_w : float
            Half-width of the band.
        end : bool or float, optional
            Endpoint angle override.

        Returns
        -------
        pos : EuclideanCoords
            Positive offset point.
        neg : EuclideanCoords
            Negative offset point.
        """
        p_prev = p_prev.numpy()
        p_curr = p_curr.numpy()
        p_next = p_next.numpy()

        v_prev = p_curr - p_prev
        v_next = p_next - p_curr

        nv_prev = self.normalize(v_prev)
        nv_next = self.normalize(v_next)

        eps = 1e-9

        if np.linalg.norm(nv_prev) < eps and np.linalg.norm(nv_next) < eps:
            return (
                EuclideanCoords(p_curr + np.array([half_w, 0])),
                EuclideanCoords(p_curr - np.array([half_w, 0])),
            )

        if np.linalg.norm(nv_prev) < eps:
            n = self.normalize(self.perp(nv_next))
            d = self.normalize(nv_next)
            cut = half_w / np.tan(end + np.pi / 2)
            return (
                EuclideanCoords(p_curr + n * half_w - d * cut),
                EuclideanCoords(p_curr - n * half_w),
            )

        if np.linalg.norm(nv_next) < eps:
            n = self.normalize(self.perp(nv_prev))
            d = self.normalize(nv_prev)
            cut = -half_w / np.tan(end + np.pi / 2)
            return (
                EuclideanCoords(p_curr + n * half_w - d * cut),
                EuclideanCoords(p_curr - n * half_w),
            )

        n1 = self.normalize(self.perp(nv_prev))
        n2 = self.normalize(self.perp(nv_next))
        bis = n1 + n2

        if np.linalg.norm(bis) < 1e-6:
            return (
                EuclideanCoords(p_curr + n2 * half_w),
                EuclideanCoords(p_curr - n2 * half_w),
            )

        b = bis / np.linalg.norm(bis)
        denom = np.dot(b, n2)
        miter_len = half_w / denom

        return (
            EuclideanCoords(p_curr + b * miter_len),
            EuclideanCoords(p_curr - b * miter_len),
        )

    def offset_segment(self, p0, p1, cut_length, end_cut=False):
        """
        Compute an offset point along a segment with trimming.

        Parameters
        ----------
        p0, p1 : EuclideanCoords
            Segment endpoints.
        cut_length : float
            Length removed from the segment.
        end_cut : bool, optional
            If True, cut is applied at the end.

        Returns
        -------
        EuclideanCoords
            Offset point.
        """
        p0 = p0.numpy()
        p1 = p1.numpy()

        d = self.normalize(p1 - p0)
        n = self.normalize(self.perp(d))
        off = n * (self.bands_width / 2)

        if not end_cut:
            return EuclideanCoords(p0 + d * cut_length - off)

        return EuclideanCoords(p1 - d * cut_length - off)

    def compute_cut_length(self, theta, half_w):
        """
        Compute trimming lengths for band intersections.

        Parameters
        ----------
        theta : float
            Intersection angle.
        half_w : float
            Half band width.

        Returns
        -------
        cut_length : float
            Primary cut length.
        add_length : float
            Alternate cut length.
        """
        if theta < np.pi / 4:
            theta_ = np.pi / 2 - theta * 2
            add_length = -(half_w / np.cos(theta_) - half_w * np.tan(theta_))
            cut_length = half_w / np.cos(theta_) + half_w * np.tan(theta_)
        else:
            theta_ = theta * 2 - np.pi / 2
            add_length = -(half_w / np.cos(theta_) + half_w * np.tan(theta_))
            cut_length = half_w / np.cos(theta_) - half_w * np.tan(theta_)

        if self.bands_mode:
            add_length = cut_length

        return cut_length, add_length

    def hatch_fill(self, vertices, cross_hatch=False):
        """
        Fill a polygon with hatch or dot patterns.

        Parameters
        ----------
        vertices : list of EuclideanCoords
            Polygon vertices.
        cross_hatch : bool, optional
            Enable perpendicular hatch pass.
        """
        angle = self.hatch_fill_parameters["angle"]
        if cross_hatch:
            angle += np.pi / 2

        vertices_rotated = [v.rotate(-angle) for v in vertices]
        ys = [v.y for v in vertices_rotated]

        y = min(ys) + self.hatch_fill_parameters["spacing"]
        y_max = max(ys)

        while y < y_max:
            xs = []

            for j in range(len(vertices_rotated)):
                p0 = vertices_rotated[j]
                p1 = vertices_rotated[(j + 1) % len(vertices_rotated)]

                if p0.y == p1.y:
                    continue

                if (p0.y <= y < p1.y) or (p1.y <= y < p0.y):
                    t = (y - p0.y) / (p1.y - p0.y)
                    xs.append(p0.x + t * (p1.x - p0.x))

            xs.sort()

            for k in range(0, len(xs), 2):
                if k + 1 >= len(xs):
                    continue

                x0, x1 = xs[k], xs[k + 1]

                if self.hatch_fill_parameters["type"] != HatchType.dot:
                    self.line(
                        EuclideanCoords([x0, y]).rotate(angle),
                        EuclideanCoords([x1, y]).rotate(angle),
                    )
                else:
                    x = x0 + self.hatch_fill_parameters["spacing"] / 2
                    while x < x1:
                        self.point(EuclideanCoords([x, y]).rotate(angle))
                        x += self.hatch_fill_parameters["spacing"]

            y += self.hatch_fill_parameters["spacing"]

    def outline_lines(self, points):
        """
        Compute offset polylines for band or lacing rendering.

        Parameters
        ----------
        points : list of EuclideanCoords
            Input polyline.

        Returns
        -------
        pos_ring : list of EuclideanCoords
            Outer offset polyline.
        neg_ring : list of EuclideanCoords
            Inner offset polyline.
        """
        if len(points) < 2:
            return [], []

        half_w = self.bands_width / 2.0
        pos_ring = []
        neg_ring = []

        for i in range(len(points)):
            p_prev = points[(i - 1) % len(points)]
            p_curr = points[i]
            p_next = points[(i + 1) % len(points)]

            end = self.bands_angle if i in (0, len(points) - 1) else False

            pos_mid, neg_mid = self.vertex_miter(
                p_prev, p_curr, p_next, half_w, end
            )

            pos_ring.append(pos_mid)
            neg_ring.append(neg_mid)

        return pos_ring, neg_ring

    def draw_outline_lines(self, points, color="red"):
        """
        Draw offset outlines for a polygon.

        Parameters
        ----------
        points : list of EuclideanCoords
            Polygon vertices.
        color : str or tuple, optional
            Drawing color.

        Returns
        -------
        list of EuclideanCoords
            Outer outline vertices.
        """
        pos_ring, neg_ring = self.outline_lines(points)

        for i in range(len(pos_ring) - 1):
            self.line(pos_ring[i], pos_ring[i + 1])

        for i in range(len(neg_ring) - 1):
            self.line(neg_ring[i], neg_ring[i + 1])

        return pos_ring

    def circle(self, c, r, color=(255, 255, 255)):
        """
        Draw a circle.

        Parameters
        ----------
        c : EuclideanCoords
            Center.
        r : float
            Radius.
        color : tuple, optional
            RGB color.
        """
        pass

    def point(self, p):
        """
        Draw a point.

        Parameters
        ----------
        p : EuclideanCoords
            Point location.
        """
        pass

    def line(self, p0, p1):
        """
        Draw a line segment.

        Parameters
        ----------
        p0, p1 : EuclideanCoords
            Endpoints of the segment.
        """
        pass

    def quadratic_bezier(self, p0, p1, p2, steps=10):
        """
        Sample a quadratic Bézier curve.

        Parameters
        ----------
        p0, p1, p2 : EuclideanCoords
            Control points.
        steps : int, optional
            Number of samples.

        Returns
        -------
        list of EuclideanCoords
            Sampled curve points.
        """
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = (
                (1 - t) ** 2 * p0.x
                + 2 * (1 - t) * t * p1.x
                + t**2 * p2.x
            )
            y = (
                (1 - t) ** 2 * p0.y
                + 2 * (1 - t) * t * p1.y
                + t**2 * p2.y
            )
            points.append(EuclideanCoords([x, y]))
        return points

    def fill_intersect_points(self, face):
        """
        Register intersection metadata for a face.

        Parameters
        ----------
        face : Face
            Face containing midpoint information.
        """
        for p, angle in face.mid_points:
            key = str(p)
            if key not in self.intersect_points:
                self.intersect_points[key] = {
                    "state": np.random.randint(2, size=2),
                    "angle": angle,
                }
            elif self.intersect_points[key]["state"].sum() % 2 == 0:
                self.intersect_points[key] = {
                    "state": (self.intersect_points[key]["state"] + 1) % 2,
                    "angle": angle,
                }

    def draw_bezier_curves(self, face):
        """
        Draw Bézier curves along a face boundary.

        Parameters
        ----------
        face : Face
            Face to be rendered.
        """
        for i in range(0, len(face.vertices) - 2, 2):
            curve = self.quadratic_bezier(
                face.vertices[i],
                face.vertices[i + 1],
                face.vertices[i + 2],
            )
            for j in range(len(curve) - 1):
                self.line(curve[j], curve[j + 1])

    def face(self, face, dotted=False, color=(255, 255, 255)):
        """
        Draw a face.

        Parameters
        ----------
        face : Face
            Face to draw.
        dotted : bool, optional
            Draw edges as dotted lines.
        color : tuple, optional
            RGB color.
        """
        self.fill_intersect_points(face)

        if self.lacing_mode or self.bands_mode:
            inside_vertices = self.draw_outline_lines(face.vertices)
        else:
            inside_vertices = face.vertices
            if self.bezier_curve:
                self.draw_bezier_curves(face)
            else:
                for i in range(len(face.vertices)):
                    self.line(
                        face.vertices[i],
                        face.vertices[(i + 1) % len(face.vertices)],
                    )

        if self.hatch_fill_parameters["type"] is not None:
            self.hatch_fill(inside_vertices)
            if self.hatch_fill_parameters["crosshatch"]:
                self.hatch_fill(
                    inside_vertices,
                    self.hatch_fill_parameters["crosshatch"],
                )

    def in_bounds(self, v):
        """
        Test whether a point lies within the drawing bounds.

        Parameters
        ----------
        v : EuclideanCoords
            Point to test.

        Returns
        -------
        bool
            True if the point is valid and within bounds.
        """
        if (
            math.isnan(v.x)
            or math.isnan(v.y)
            or math.isinf(v.x)
            or math.isinf(v.y)
        ):
            return False

        return (
            self.size[0] < v.x < self.size[0] + self.size[2]
            and self.size[1] < v.y < self.size[1] + self.size[3]
        )

    def set_label(self, label):
        """
        Set a label for the output.

        Parameters
        ----------
        label : str
            Label text.
        """
        pass

    def set_caption(self, caption):
        """
        Set a caption for the output.

        Parameters
        ----------
        caption : str
            Caption text.
        """
        pass

    def new(self, filename, size=None, n_tiles=None):
        """
        Start a new output document.

        Parameters
        ----------
        filename : str
            New output filename.
        size : tuple, optional
            New drawing size.
        n_tiles : int, optional
            New tile scaling factor.
        """
        pass

