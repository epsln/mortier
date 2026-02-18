import math
import pytest
import numpy as np

from mortier.coords import LatticeCoords, EuclideanCoords, Line
from mortier.face import Face, P2Penrose, P3Penrose

@pytest.mark.benchmark
def test_benchmark_ray_transform():
    face = Face([
        EuclideanCoords([0, 0]),
        EuclideanCoords([1, 0]),
        EuclideanCoords([1, 1]),
    ])

    result = face.ray_transform(angle=0.3)
