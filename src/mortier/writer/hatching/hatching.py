from dataclasses import dataclass
from typing import Tuple

import numpy as np

from mortier.enums import HatchType


@dataclass
class Hatching:
    "Dataclass holding hatching parameters"

    angle: float = np.pi / 2
    spacing: float = 5
    crosshatch: bool = False
    type: HatchType = HatchType.LINE
    color: Tuple[int, int, int] = (255, 255, 255)
