import math
import pytest
import numpy as np

from mortier.coords import LatticeCoords, EuclideanCoords, Line
from mortier.face import Face, P2Penrose, P3Penrose

def approx_point(p, q, eps=1e-6):
    return abs(p.x - q.x) < eps and abs(p.y - q.y) < eps

@pytest.mark.parametrize("m,expected_vertices", [
    (3, 3),
    (4, 4),
    (6, 6),
    (12, 12),
])
def test_face_generate_vertex_count(m, expected_vertices):
    v = LatticeCoords([0, 0, 0, 0])
    face = Face.generate(v, k=0, m=m)

    assert len(face.vertices) == expected_vertices


def test_face_generate_vertices_are_latticecoords():
    v = LatticeCoords([0, 0, 0, 0])
    face = Face.generate(v, k=2, m=6)

    for vert in face.vertices:
        assert isinstance(vert, LatticeCoords)


def test_face_translate_preserves_vertex_count():
    v = LatticeCoords([0, 0, 0, 0])
    face = Face.generate(v, k=0, m=4)

    T1 = LatticeCoords([1, 0, 0, 0])
    T2 = LatticeCoords([0, 1, 0, 0])

    moved = face.translate(T1, T2, 2, 3)

    assert len(moved.vertices) == len(face.vertices)


def test_face_scale_scales_all_vertices():
    face = Face([
        EuclideanCoords([1, 2]),
        EuclideanCoords([3, 4]),
    ])

    scaled = face.scale(2)

    assert approx_point(scaled.vertices[0], EuclideanCoords([2, 4]))
    assert approx_point(scaled.vertices[1], EuclideanCoords([6, 8]))


def test_face_rotate_90_deg():
    face = Face([
        EuclideanCoords([1, 0]),
        EuclideanCoords([0, 1]),
    ])

    rotated = face.rotate(math.pi / 2)

    assert approx_point(rotated.vertices[0], EuclideanCoords([0, 1]))
    assert approx_point(rotated.vertices[1], EuclideanCoords([-1, 0]))


def test_ray_transform_returns_closed_face():
    face = Face([
        EuclideanCoords([0, 0]),
        EuclideanCoords([1, 0]),
        EuclideanCoords([1, 1]),
    ])

    result = face.ray_transform(angle=0.3)

    assert isinstance(result, Face)
    assert len(result.vertices) > len(face.vertices)

    # Closed polygon
    assert approx_point(result.vertices[0], result.vertices[-1])


def test_ray_transform_midpoints_exist():
    face = Face([
        EuclideanCoords([0, 0]),
        EuclideanCoords([2, 0]),
        EuclideanCoords([1, 2]),
    ])

    result = face.ray_transform(angle=0.2)

    assert len(result.mid_points) > 0
    for p, a in result.mid_points:
        assert isinstance(p, EuclideanCoords)
        assert isinstance(a, float)


def test_half_plane_modifies_vertices_in_place():
    face = Face([
        EuclideanCoords([1, 1]),
        EuclideanCoords([2, 1]),
    ])

    out = face.half_plane()

    assert out is face
    assert all(isinstance(v, EuclideanCoords) for v in face.vertices)

def test_p2penrose_initialise():
    tiles = P2Penrose.initialise()

    assert len(tiles) == 2
    for t in tiles:
        assert isinstance(t, P2Penrose)
        assert t.code in {2, 3}


@pytest.mark.parametrize("code,expected", [
    (0, 3),
    (1, 3),
    (2, 2),
    (3, 2),
])
def test_p2penrose_inflate_count(code, expected):
    A = EuclideanCoords([0, 0])
    B = EuclideanCoords([1, 0])
    C = EuclideanCoords([0.5, 1])

    tile = P2Penrose(A, B, C, code)
    children = tile.inflate()

    assert len(children) == expected
    for c in children:
        assert isinstance(c, P2Penrose)

def test_p3penrose_initialise():
    tiles = P3Penrose.initialise()

    assert len(tiles) == 2
    for t in tiles:
        assert isinstance(t, P3Penrose)


@pytest.mark.parametrize("code,expected", [
    (0, 2),
    (1, 2),
    (2, 3),
    (3, 3),
])
def test_p3penrose_inflate_count(code, expected):
    A = EuclideanCoords([0, 0])
    B = EuclideanCoords([1, 0])
    C = EuclideanCoords([0.5, 1])

    tile = P3Penrose(A, B, C, code)
    children = tile.inflate()

    assert len(children) == expected
    for c in children:
        assert isinstance(c, P3Penrose)

