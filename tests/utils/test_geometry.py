import numpy as np
import pytest
from mortier.utils.geometry import (
    line_offset,
    intersect,
    normalize,
    perp,
    clean_points,
    vertex_miter,
    offset_segment,
    compute_cut_length,
    outline_lines,
    quadratic_bezier,
    fill_intersect_points
)
from mortier.coords import EuclideanCoords
from mortier.face import Face

from mortier.writer.ornements import Ornements 


def test_line_offset_basic():
    p1 = EuclideanCoords([0, 0])
    p2 = EuclideanCoords([1, 0])
    d = 1.0
    (p1a, p2a), (p1b, p2b) = line_offset(p1, p2, d)
    # Perpendicular offset in y direction
    assert np.allclose([p1a.x, p1a.y], [0, 1])
    assert np.allclose([p2a.x, p2a.y], [1, 1])
    assert np.allclose([p1b.x, p1b.y], [0, -1])
    assert np.allclose([p2b.x, p2b.y], [1, -1])


def test_line_offset_zero_length():
    p1 = EuclideanCoords([0, 0])
    p2 = EuclideanCoords([0, 0])
    (p1a, p2a), (p1b, p2b) = line_offset(p1, p2, 1.0)
    # Should return original points
    assert p1a.x == 0 and p1a.y == 0
    assert p2a.x == 0 and p2a.y == 0


def test_intersect_basic():
    p1 = EuclideanCoords([0, 0])
    p2 = EuclideanCoords([1, 1])
    p3 = EuclideanCoords([0, 1])
    p4 = EuclideanCoords([1, 0])
    inter = intersect(p1, p2, p3, p4)
    assert np.allclose(inter, [0.5, 0.5])


def test_intersect_parallel():
    p1 = EuclideanCoords([0, 0])
    p2 = EuclideanCoords([1, 1])
    p3 = EuclideanCoords([0, 1])
    p4 = EuclideanCoords([1, 2])
    inter = intersect(p1, p2, p3, p4)
    # Midpoint approximation
    assert np.allclose(inter, [0.5, 1.0])


def test_normalize_nonzero():
    v = np.array([3.0, 4.0])
    n = normalize(v)
    assert np.allclose(np.linalg.norm(n), 1.0)


def test_normalize_zero():
    v = np.array([0.0, 0.0])
    n = normalize(v)
    assert np.allclose(n, [0.0, 0.0])


def test_perp_vector():
    v = np.array([1.0, 0.0])
    p = perp(v)
    assert np.allclose(p, [0.0, 1.0])


def test_clean_points():
    points = [[0, 0], [0, 0], [1, 0], [1, 0], [2, 0]]
    cleaned = clean_points(points)
    assert len(cleaned) == 3
    assert np.allclose(cleaned[0], [0, 0])
    assert np.allclose(cleaned[-1], [2, 0])


def test_vertex_miter_basic():
    ornements = Ornements(width = 0.5)
    p_prev = EuclideanCoords([0, 0])
    p_curr = EuclideanCoords([1, 0])
    p_next = EuclideanCoords([1, 1])
    pos, neg = vertex_miter(p_prev, p_curr, p_next, ornements)
    # Offset points should be different from original
    assert np.linalg.norm(pos.numpy() - p_curr.numpy()) > 0
    assert np.linalg.norm(neg.numpy() - p_curr.numpy()) > 0


def test_offset_segment_basic():
    ornements = Ornements()
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([1, 0])
    off = offset_segment(p0, p1, 0.1, ornements)
    # Returns a EuclideanCoords
    assert isinstance(off, EuclideanCoords)


def test_compute_cut_length_values():
    ornements = Ornements(width = 1.0)
    cut, add = compute_cut_length(np.pi/6, ornements)
    assert cut > 0
    cut2, add2 = compute_cut_length(np.pi/3, ornements)
    assert cut2 > 0


def test_outline_lines_simple():
    pts = [EuclideanCoords([0, 0]), EuclideanCoords([1, 0]), EuclideanCoords([1, 1])]
    intersect_points = {}
    ornements = Ornements()
    pos, neg = outline_lines(pts, intersect_points, ornements)
    assert len(pos) > 0

def test_fill_intersect_points_and_outline():
    # Simple Square for testing
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([0, 1])
    p2 = EuclideanCoords([1, 1])
    p3 = EuclideanCoords([1, 0])

    vertices = [p0, p1, p2, p3]
    # Create a fake "face" with mid_points (p, angle)

    face = Face(vertices)
    angle = 0.1
    face = face.ray_transform(angle)
    print(face.mid_points)
    intersect_points = {}

    # Fill intersect points
    fill_intersect_points(face, intersect_points)

    # Test that each midpoint is in intersect_points with proper keys
    for p, angle in face.mid_points:
        key = str(p)
        assert key in intersect_points
        assert "state" in intersect_points[key]
        assert "angle" in intersect_points[key]
        assert intersect_points[key]["angle"] == angle
        assert intersect_points[key]["state"].shape == (2,)

    # Now test outline_lines using these intersect points
    bands_width = 0.2
    ornements = Ornements(type = "bands")
    pos_ring, neg_ring = outline_lines(face.vertices, intersect_points, ornements)

    # Basic checks: output lists not empty
    assert len(pos_ring) > 0
    assert len(neg_ring) > 0

    # The first and last point of pos_ring should match (closed polygon)
    assert np.allclose([pos_ring[0].x, pos_ring[0].y], [pos_ring[-1].x, pos_ring[-1].y])

    # Check that offset points are indeed offset from original triangle
    for pt in pos_ring:
        distances = [np.linalg.norm(pt.numpy() - p.numpy()) for p in face.vertices]
        assert any(d > 0.05 for d in distances)  # should be offset

def test_quadratic_bezier():
    # Simple curve
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([1, 2])
    p2 = EuclideanCoords([2, 0])

    bezier_pts = quadratic_bezier(p0, p1, p2, steps=10)

    # Check number of points
    assert len(bezier_pts) == 11

    # Start and end points match
    assert np.allclose(bezier_pts[0].numpy(), p0.numpy())
    assert np.allclose(bezier_pts[-1].numpy(), p2.numpy())

    # Points are between start and end
    for pt in bezier_pts:
        x, y = pt.x, pt.y
        assert 0 <= x <= 2
        assert 0 <= y <= 2

def test_line_offset_basic():
    # Simple horizontal line
    p0 = EuclideanCoords([0, 0])
    p1 = EuclideanCoords([1, 0])
    d = 0.1
    (p0a, p1a), (p0b, p1b) = line_offset(p0, p1, d)

    # Offsets in y direction
    assert np.isclose(p0a.y - p0.y, d)
    assert np.isclose(p1a.y - p1.y, d)
    assert np.isclose(p0b.y - p0.y, -d)
    assert np.isclose(p1b.y - p1.y, -d)
