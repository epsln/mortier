import math

def cyclic_variants(seq: tuple) -> list[tuple]:
    """Return all rotations of a tuple."""
    n = len(seq)
    return [tuple(seq[(i + j) % n] for j in range(n)) for i in range(n)]


def canonical_cyclic(seq: tuple) -> tuple:
    """
    Canonical form of a cyclic sequence up to rotation AND reflection.
    Used as the orbit signature for a vertex configuration.
    """
    forward  = min(cyclic_variants(seq))
    backward = min(cyclic_variants(seq[::-1]))
    return min(forward, backward)


def angle_of(center, point) -> float:
    """Angle (radians) from center to point, in [-π, π]."""
    cx, cy = center
    px, py = point
    return math.atan2(py - cy, px - cx)


def sort_faces_around_vertex(vertex_pt, face_indices, faces) -> list[int]:
    """
    Return face indices sorted in counter-clockwise angular order
    around vertex_pt, using each face's centroid as reference direction.
    """
    def centroid(face):
        verts = face.vertices
        n = len(verts)
        cx = sum(float(v.x) for v in verts) / n
        cy = sum(float(v.y) for v in verts) / n
        return cx, cy

    vx, vy = float(vertex_pt[0]), float(vertex_pt[1])

    def angle_key(fi):
        cx, cy = centroid(faces[fi])
        return math.atan2(cy - vy, cx - vx)

    return sorted(face_indices, key=angle_key)
