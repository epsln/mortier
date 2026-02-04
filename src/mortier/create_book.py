import json
import random

import numpy as np

from mortier.penrose import Penrose
from mortier.tesselation.tesselation import Tesselate
from mortier.writer import TikzWriter

ROOT_DIR = "/home/epsilon/misc/tesselation_alt_layout/"

with open("/home/epsilon/dev/mortier/data/database.json", "r") as f:
    js = json.load(f)

tess_id = "t3003"
tess = js[tess_id]

text = (
    """
\\begin{table}[h]
\\centering
	\caption{Coefficients du pavage $"""
    + tess_id
    + """$}
\\begin{tabular}{lllll}
       $1$ & $w$ & $w_2$ & $w_3$ \\\\ \hline \n
"""
)

text += "&".join([str(c) for c in tess["T1"]]) + "\\\\ \n"
text += "&".join([str(c) for c in tess["T2"]]) + "\\\\ \hline \n"

for tesselation in tess["Seed"]:
    text += "&".join([str(c) for c in tesselation]) + "\\\\ \n"

text += "\end{tabular}\n\end{table}"

with open(f"{ROOT_DIR}/tables/exemple_0.tex", "w+") as f:
    f.write(text)


writer = TikzWriter(f"{ROOT_DIR}/figures/etape_0.tex", size=(-5, -5, 15, 15))
tesselation = Tesselate(writer, tess, tess_id)
# writer.set_caption(f"Cellule et graines de ${tess_id}$")
# writer.no_clip()
# writer.set_scale(0.6)
# tesselation.draw_seed()
#
# writer.new(f"{ROOT_DIR}/figures/etape_1.tex")
# writer.no_clip()
# writer.set_scale(0.6)
# tesselation.draw_star()
#
# writer.new(f"{ROOT_DIR}/figures/etape_2.tex")
# writer.no_clip()
# writer.set_scale(0.6)
# tesselation.draw_edge()
#
# writer.new(f"{ROOT_DIR}/figures/etape_3.tex")
# writer.no_clip()
# writer.set_scale(0.6)
# tesselation.show_base = True
# tesselation.draw_tesselation()
# tesselation.show_base = False
#
# writer.draw_borders = True
# writer.new(f"{ROOT_DIR}/figures/finished.tex", size = (-1, -1, 14, 20), n_tiles = 1)
# tesselation.draw_tesselation()
#
# tess_id = random.choice(list(js.keys()))
# tess = js[tess_id]
# bounds = (-1, -1, 14, 5)
# writer.new(f"{ROOT_DIR}/figures/exemple_delete_vertex.tex", size = bounds, n_tiles = 1)
# tesselation.set_tesselation(tess, tess_id)
# tesselation.draw_tesselation()
bounds = (-1, -1, 14, 20)
#
# for i in range(5):
#    tess_id = random.choice(list(js.keys()))
#    tess = js[tess_id]
#    writer.new(f"{ROOT_DIR}/figures/exemple_{i}.tex", size = bounds, n_tiles = 1)
#    tesselation.set_tesselation(tess, tess_id)
#    tesselation.draw_tesselation()
#
# for i in range(2):
#    tess_id = random.choice(list(js.keys()))
#    tess = js[tess_id]
#    writer.new(f"{ROOT_DIR}/figures/exemple_ray_dot_{i}.tex", bounds, n_tiles = 2)
#    tesselation.set_tesselation(tess, tess_id)
#    tesselation.set_show_underlying(True)
#    tesselation.set_angle(np.random.uniform(low=0.1, high=np.pi/2))
#    tesselation.draw_tesselation()
#
# tesselation.set_show_underlying(False)
#
# for i in range(5):
#    tess_id = random.choice(list(js.keys()))
#    tess = js[tess_id]
#    writer.new(f"{ROOT_DIR}/figures/exemple_ray_{i}.tex", size = bounds, n_tiles = 1.5)
#    tesselation.set_tesselation(tess, tess_id)
#    tesselation.set_angle(np.random.uniform(low=0.1, high=np.pi/2))
#    tesselation.draw_tesselation()
#
for i in range(20):
    print(i)
    writer.draw_borders = True
    bounds = (-1, -1, 14, 20)
    writer.new(f"{ROOT_DIR}/figures/gallery_{i}.tex", size=bounds, n_tiles=2)
    writer.bands_width = np.random.uniform(low=0.1, high=0.3)
    angle = np.random.uniform(
        low=writer.bands_width, high=np.pi / 2 - writer.bands_width
    )
    if np.random.random() < 0.2:
        if np.random.random() < 1.0:
            p = "P2"
        else:
            p = "P3"  # P3 is bugged, can't find a quick fix
        writer.bands_mode = False
        writer.lacing_mode = False
        angle = np.random.uniform(low=0.1, high=0.5)
        tesselation = Penrose(writer, p)
    else:
        tess_id = random.choice(list(js.keys()))
        tess = js[tess_id]
        tesselation = Tesselate(writer, tess, tess_id)
        test_r = np.random.uniform()
        if test_r < 0.2:
            writer.bands_mode = True
            writer.lacing_mode = False
        elif 0.2 < test_r < 0.8:
            writer.bands_mode = False
            writer.lacing_mode = True
        else:
            writer.bands_mode = False
            writer.lacing_mode = False
        if np.random.random() < 0.2:
            writer.n_tiles = 1
            if np.random.random() < 0.2:
                tesselation.set_sin_mode("sin")
            else:
                tesselation.set_sin_mode("perlin")
            writer.lacing_mode = False
            writer.bands_mode = False
        if np.random.random() < 0.2:
            writer.n_tiles = 2
            tesselation.set_assym_angle(
                angle + np.random.uniform(low=-angle / 4, high=angle / 4)
            )
            writer.lacing_mode = False
            writer.bands_mode = False
            tesselation.set_sin_mode(True)
        if np.random.random() < 0.2:
            writer.n_tiles = 2
            tesselation.set_separated_site_mode(np.random.randint(3, 10))
            tesselation.set_sin_mode(True)
            writer.lacing_mode = False
            writer.bands_mode = False
    tesselation.set_angle(angle)
    writer.lacing_angle = angle
    tesselation.draw_tesselation()
