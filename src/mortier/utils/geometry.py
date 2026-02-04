import numpy as np

from mortier.coords import EuclideanCoords

def line_offset(p1, p2, d):
    """Return the two offset lines at distance ±d from the base line."""
    dir_vec = p2.translate(p1.scale(-1))
    if dir_vec.len() < 1e-9:
        return (p1, p2), (p1, p2)
    perp = EuclideanCoords([-dir_vec.y, dir_vec.x]).normalise()
    return (p1.translate(perp.scale(d)), p2.translate(perp.scale(d))), \
           (p1.translate(perp.scale(-d)), p2.translate(perp.scale(-d)))

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
        return p2.translate(p3).scale(1/2).numpy()
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

def vertex_miter(p_prev, p_curr, p_next, half_w, end = False):
    """Compute offset points (left/right) at vertex p_curr using miter join."""
    p_prev = p_prev.numpy()
    p_curr = p_curr.numpy()
    p_next = p_next.numpy()
    v_prev = p_curr - p_prev
    v_next = p_next - p_curr
    nv_prev = normalize(v_prev)
    nv_next = normalize(v_next)
    EPS = 1e-9

    if np.linalg.norm(nv_prev) < EPS and np.linalg.norm(nv_next) < EPS:
        return EuclideanCoords(p_curr + np.array([half_w, 0])), EuclideanCoords(p_curr - np.array([half_w, 0]))

    if np.linalg.norm(nv_prev) < EPS:
        n = normalize(perp(nv_next))
        d = normalize(nv_next)
        cut = half_w/np.tan(end + np.pi/2)
        return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(p_curr - n * half_w)

    if np.linalg.norm(nv_next) < EPS:
        n = normalize(perp(nv_prev))
        d = normalize(nv_prev)
        cut = -half_w/np.tan(end + np.pi/2)
        return EuclideanCoords(p_curr + n * half_w - d * cut), EuclideanCoords(p_curr - n * half_w)

    n1 = normalize(perp(nv_prev))
    n2 = normalize(perp(nv_next))
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

def offset_segment(p0, p1, cut_length, bands_width, end_cut = False):
    """Return outer and inner offset lines for a single segment."""
    p0 = p0.numpy() 
    p1 = p1.numpy()
    dir_vec = p1 - p0
    n = normalize(perp(dir_vec))
    d = normalize(dir_vec)
    off = n * (bands_width / 2)
    l = p0 - p1
    if not end_cut:
        p0_cut = p0 + d * cut_length
        return EuclideanCoords(p0_cut - off)
    else:
        p1_cut = p1 - d * cut_length
        return EuclideanCoords(p1_cut - off)

def compute_cut_length(theta, half_w, bands_mode = False):
    if theta < np.pi/4:
        theta_ = np.pi/2 - theta*2 
        add_length = -(half_w/ np.cos(theta_) - half_w * np.tan(theta_))
        cut_length = half_w / np.cos(theta_) + half_w* np.tan(theta_) 
    else:
        theta_ = theta * 2 - np.pi/2 
        add_length = -(half_w / np.cos(theta_) + half_w * np.tan(theta_))
        cut_length = half_w / np.cos(theta_) - half_w * np.tan(theta_)
    if bands_mode:
        add_length = cut_length
    return cut_length, add_length

def outline_lines(points, intersect_points, bands_width, bands_angle, bands_mode):
    """
    Compute pairs of offset polylines (outer and inner) for a given polyline.
    """
    pts = points 
    n = len(pts) 
    if n < 2:
        return [], []

    half_w = bands_width / 2.0
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
            end = bands_angle
        else:
            end = False

        pos_midpoint, neg_midpoint = vertex_miter(p_prev, p_curr, p_next, half_w, end)

        if str(p_curr) in intersect_points:
            inter_p = intersect_points[str(p_curr)]
            cut_length, add_length = compute_cut_length(inter_p["angle"], half_w, bands_mode)
            beg_point = offset_segment(p_curr, p_next, cut_length, bands_width)
            if inter_p['state'][0] == 1:
                beg_point = offset_segment(p_curr, p_next, cut_length, bands_width)
            else:
                beg_point = offset_segment(p_curr, p_next, add_length, bands_width)

        elif str(p_next) in intersect_points:
            inter_p = intersect_points[str(p_next)]
            cut_length, add_length = compute_cut_length(inter_p["angle"], half_w)
            end_point = offset_segment(p_curr, p_next, cut_length, bands_width, end_cut = True)
            if inter_p['state'][1] == 1:
                end_point = offset_segment(p_curr, p_next, cut_length, bands_width, end_cut = True)
            else:
                end_point = offset_segment(p_curr, p_next, add_length, bands_width, end_cut = True)

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

def quadratic_bezier(p0, p1, p2, steps=10):
    #TODO: Maybe N order bezier with all vertices ?
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**2 * p0.x + 2 * (1 - t) * t * p1.x + t**2 * p2.x
        y = (1 - t)**2 * p0.y + 2 * (1 - t) * t * p1.y + t**2 * p2.y
        points.append(EuclideanCoords([x, y]))
    return points

def fill_intersect_points(face, intersect_points):
    for p, angle in face.mid_points:
        if str(p) not in intersect_points:
            intersect_points[str(p)] = {"state": np.random.randint(2, size = 2),
                                             "angle": angle}
        elif intersect_points[str(p)]["state"].sum() % 2 == 0:
            intersect_points[str(p)] = {"state": np.array([(x + 1) % 2 for x in intersect_points[str(p)]["state"]]),
                                             "angle": angle} 
