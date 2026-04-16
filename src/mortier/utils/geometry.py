import numpy as np

from mortier.coords import EuclideanCoords
from mortier.enums import OrnementsType
from mortier.face import Face


def line_offset(p1, p2, d):
    """Return the two offset lines at distance ±d from the base line."""
    dir_vec = p2.translate(p1.scale(-1))
    if dir_vec.len() < 1e-9:
        return (p1, p2), (p1, p2)
    perp = EuclideanCoords([-dir_vec.y, dir_vec.x]).normalise()
    return (p1.translate(perp.scale(d)), p2.translate(perp.scale(d))), (
        p1.translate(perp.scale(-d)),
        p2.translate(perp.scale(-d)),
    )


def intersect(p1, p2, p3, p4):
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
        return p2.translate(p3).scale(1 / 2).numpy()
    x = (B2 * C1 - B1 * C2) / det
    y = (A1 * C2 - A2 * C1) / det
    return EuclideanCoords([x, y]).numpy()


def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-9:
        return np.zeros_like(v)
    return v / n


def perp(v):
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


def vertex_miter(p_prev, p_curr, p_next, ornements, end=False):
    """Compute offset points (left/right) at vertex p_curr using miter join."""
    half_w = ornements.width / 2.0
    p_prev = p_prev.numpy()
    p_curr = p_curr.numpy()
    p_next = p_next.numpy()
    v_prev = p_curr - p_prev
    v_next = p_next - p_curr
    nv_prev = normalize(v_prev)
    nv_next = normalize(v_next)
    EPS = 1e-9

    if np.linalg.norm(nv_prev) < EPS and np.linalg.norm(nv_next) < EPS:
        return EuclideanCoords(p_curr + np.array([half_w, 0])), EuclideanCoords(
            p_curr - np.array([half_w, 0])
        )

    if np.linalg.norm(nv_prev) < EPS:
        n = normalize(perp(nv_next))
        d = normalize(nv_next)
        cut = half_w / np.tan(end + np.pi / 2)
        return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(
            p_curr - n * half_w
        )

    if np.linalg.norm(nv_next) < EPS:
        n = normalize(perp(nv_prev))
        d = normalize(nv_prev)
        cut = -half_w / np.tan(end + np.pi / 2)
        return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(
            p_curr - n * half_w
        )

    n1 = normalize(perp(nv_prev))
    n2 = normalize(perp(nv_next))
    bis = n1 + n2
    bis_len = np.linalg.norm(bis)
    if bis_len < 1e-6:
        return EuclideanCoords(p_curr + n2 * half_w), EuclideanCoords(
            p_curr - n2 * half_w
        )
    b = bis / bis_len
    denom = np.dot(b, n2)
    miter_len = half_w / denom
    pos = p_curr + b * miter_len
    neg = p_curr - b * miter_len
    return EuclideanCoords(pos), EuclideanCoords(neg)


def offset_segment(p0, p1, cut_length, ornements, end_cut=False):
    """Return outer and inner offset lines for a single segment."""
    p0 = p0.numpy()
    p1 = p1.numpy()
    dir_vec = p1 - p0
    n = normalize(perp(dir_vec))
    d = normalize(dir_vec)
    off = n * (ornements.width / 2)
    if not end_cut:
        p0_cut = p0 + d * cut_length
        return EuclideanCoords(p0_cut - off)
    else:
        p1_cut = p1 - d * cut_length
        return EuclideanCoords(p1_cut - off)


def compute_cut_length(theta, ornements):
    half_w = ornements.width / 2
    if theta < np.pi / 4:
        theta_ = np.pi / 2 - theta * 2
        add_length = -(half_w / np.cos(theta_) - half_w * np.tan(theta_))
        cut_length = half_w / np.cos(theta_) + half_w * np.tan(theta_)
    else:
        theta_ = theta * 2 - np.pi / 2
        add_length = -(half_w / np.cos(theta_) + half_w * np.tan(theta_))
        cut_length = half_w / np.cos(theta_) - half_w * np.tan(theta_)
    if ornements.type == OrnementsType.BANDS:
        add_length = cut_length
    return cut_length, add_length

def outline_lines(points, intersect_points, ornements, use_crossing_logic = True):
    pts = points
    n = len(pts)
    if n < 2:
        return [], []

    pos_ring = []
    neg_ring = []
    beg_point = None

    for i in range(n):
        p_prev = pts[(i - 1) % n]
        p_curr = pts[i]
        p_next = pts[(i + 1) % n]

        if i == 0 or i == n - 1:
            end = ornements.angle
        else:
            end = False

        pos_midpoint, neg_midpoint = vertex_miter(
            p_prev, p_curr, p_next, ornements, end
        )

        if vertex_key(p_curr) in intersect_points:
            inter_p = intersect_points[vertex_key(p_curr)]
            cut_length, add_length = compute_cut_length(
                inter_p["angle"], ornements)
            if inter_p["state"][0] == 1:
                beg_point = offset_segment(
                    p_curr, p_next, cut_length, ornements)
            else:
                beg_point = offset_segment(
                    p_curr, p_next, add_length, ornements)

        elif vertex_key(p_next) in intersect_points:
            inter_p = intersect_points[vertex_key(p_next)]
            cut_length, add_length = compute_cut_length(
                inter_p["angle"], ornements)
            if inter_p["state"][1] == 1:
                end_point = offset_segment(
                    p_curr, p_next, cut_length, ornements, end_cut=True)
            else:
                end_point = offset_segment(
                    p_curr, p_next, add_length, ornements, end_cut=True)
            if beg_point is not None:
                neg_ring.append(beg_point)
                neg_ring.append(neg_midpoint)
                neg_ring.append(end_point)
            beg_point = None

        pos_ring.append(pos_midpoint)

    # Close the ring
    if len(pos_ring) >= 2:
        closing = EuclideanCoords(
            intersect(pos_ring[-2], pos_ring[-1], pos_ring[0], pos_ring[1])
        )
        pos_ring[0] = closing
        pos_ring[-1] = closing

    return pos_ring, neg_ring

def quadratic_bezier(p0, p1, p2, steps=10):
    # TODO: Maybe N order bezier with all vertices ?
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * p1.x + t**2 * p2.x
        y = (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * p1.y + t**2 * p2.y
        points.append(EuclideanCoords([x, y]))
    return points


def fill_intersect_points(face, intersect_points):
    for p, angle in face.mid_points:
        if vertex_key(p) not in intersect_points:
            intersect_points[vertex_key(p)] = {
                "state": np.random.randint(2, size=2),
                "angle": angle,
            }
        elif intersect_points[vertex_key(p)]["state"].sum() % 2 == 0:
            intersect_points[vertex_key(p)] = {
                "state": np.array(
                    [(x + 1) % 2 for x in intersect_points[vertex_key(p)]["state"]]
                ),
                "angle": angle,
            }

def vertex_key(v, precision=2):
    return (round(float(v.x), precision), round(float(v.y), precision))

def build_negative_space_faces(transformed_faces):
    from collections import defaultdict

    # For each original vertex, collect ordered (launch_1, intersection, launch_0)
    # triplets from each face that has that vertex
    vertex_to_triplets = defaultdict(list)

    for tf in transformed_faces:
        if not hasattr(tf, 'intersection_points'):
            continue
        for ip in tf.intersection_points:
            orig = ip["original_vertex"]
            p = ip["point"]
            l0 = ip["launch_0"]
            l1 = ip["launch_1"]

            # Skip invalid points
            if not (np.isfinite(p.x) and np.isfinite(p.y)):
                continue
            if not (np.isfinite(l0.x) and np.isfinite(l0.y)):
                continue
            if not (np.isfinite(l1.x) and np.isfinite(l1.y)):
                continue

            key = (round(orig.x, 2), round(orig.y, 2))
            vertex_to_triplets[key].append({
                "launch_0": l0,   # root on edge coming into p1
                "intersection": p,
                "launch_1": l1,   # root on edge going out of p1
                "angle_to_orig": np.arctan2(
                    p.y - orig.y, p.x - orig.x
                )
            })

    negative_faces = []
    for key, triplets in vertex_to_triplets.items():
        if len(triplets) < 2:
            continue

        # Sort triplets by angle of their intersection point around the
        # original vertex — this gives correct winding order
        triplets.sort(key=lambda t: t["angle_to_orig"])

        # Build face vertices: for each triplet in order,
        # add launch_1 then intersection then launch_0
        # This traces the boundary of the negative space face
        pts = []
        for t in triplets:
            pts.append(t["launch_1"])
            pts.append(t["intersection"])
            pts.append(t["launch_0"])

        # Remove consecutive duplicates
        unique_pts = [pts[0]]
        for p in pts[1:]:
            prev = unique_pts[-1]
            if not (abs(p.x - prev.x) < 1e-3 and abs(p.y - prev.y) < 1e-3):
                unique_pts.append(p)

        if len(unique_pts) < 3:
            continue

        # Validate
        if not all(np.isfinite(p.x) and np.isfinite(p.y) for p in unique_pts):
            continue

        # Check not degenerate
        v1 = np.array([unique_pts[1].x - unique_pts[0].x,
                        unique_pts[1].y - unique_pts[0].y])
        v2 = np.array([unique_pts[2].x - unique_pts[0].x,
                        unique_pts[2].y - unique_pts[0].y])
        if abs(v1[0]*v2[1] - v1[1]*v2[0]) < 1e-6:
            continue

        negative_faces.append(Face(unique_pts))

    return negative_faces
