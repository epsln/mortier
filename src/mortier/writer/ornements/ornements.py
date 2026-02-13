from dataclasses import dataclass

import numpy as np

from mortier.enums import OrnementsType


@dataclass
class Ornements:
    """
    Dataclass holding ornements parameters.
    Ornements are ways to draw the sides of
    """

    angle: float = np.pi / 2
    width: float = 5
    type: OrnementsType = OrnementsType.BANDS
