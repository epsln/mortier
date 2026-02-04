import json
import random

import numpy as np
from penrose import Penrose
from tesselation import Tesselate
from writer import TikzWriter

ROOT_DIR = "/home/epsilon/misc/tesselation_alt_layout/"
BROKEN_FIGS = [36]

with open("/home/epsilon/dev/mortier/data/database.json", "r") as f:
    js = json.load(f)

tess_id = "t3003"
tess = js[tess_id]
writer = TikzWriter(f"{ROOT_DIR}/figures/etape_0.tex", size=(-5, -5, 15, 15))
tesselation = Tesselate(writer, tess, tess_id)

bounds = (-1, -1, 14, 20)
for i in BROKEN_FIGS:
    writer.draw_borders = True
    writer.new(f"{ROOT_DIR}/figures/gallery_{i}.tex", size=bounds, n_tiles=2)
    writer.bands_width = 0.1
    if np.random.random() < 0.0:
        if np.random.random() < 0.5:
            p = "P2"
        else:
            p = "P3"
        tesselation = Penrose(writer, p)
    else:
        tess_id = random.choice(list(js.keys()))
        tess = js[tess_id]
        tesselation = Tesselate(writer, tess, tess_id)
    angle = np.random.uniform(
        low=writer.bands_width, high=np.pi / 2 - writer.bands_width
    )
    tesselation.set_angle(angle)
    writer.lacing_mode = True
    if np.random.random() < 0.5:
        if np.random.random() < 0.2:
            tesselation.set_sin_mode("sin")
        else:
            tesselation.set_sin_mode("perlin")
        writer.lacing_mode = False
    if np.random.random() < 0.3:
        tesselation.set_assym_angle(np.random.uniform(low=0.01, high=angle))
        writer.lacing_mode = False
        tesselation.set_sin_mode(True)
        if angle > np.pi / 4:
            tesselation.set_assym_angle(angle - np.random.uniform(high=angle / 10))
            tesselation.set_sin_mode(True)
    if np.random.random() < 0.3:
        tesselation.set_separated_site_mode(np.random.randint(3, 10))
        tesselation.set_sin_mode(True)
        writer.lacing_mode = False
    writer.lacing_mode = False

    writer.lacing_angle = angle
    tesselation.draw_tesselation()
