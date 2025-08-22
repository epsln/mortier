import json
from tesselation import Tesselate 
from writer import TikzWriter, BitmapWriter 
import random
import numpy as np

with open('/home/epsilon/dev/mortier/data/database.json', 'r') as f:
    js = json.load(f)

tess_id = random.choice(list(js.keys()))
tess = js[tess_id]
while len(tess["Seed"]) > 5:
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]

text = """
\\begin{table}[h]
	\caption{Coefficients du pavage $""" + tess_id + """$}
\\begin{tabular}{lllll}
       $1$ & $w$ & $w_2$ & $w_3$ \\\\ \hline \n
"""

text += '&'.join([str(c) for c in tess['T1']]) + "\\\\ \n"
text += '&'.join([str(c) for c in tess['T2']]) + "\\\\ \hline \n"

for l in tess["Seed"]:
    text += '&'.join([str(c) for c in l]) + "\\\\ \n"

text += "\end{tabular}\n\end{table}"

with open('tables/exemple_0.tex', 'w+') as f:
    f.write(text)


writer = TikzWriter("figures/etape_0.tex", size = (-5, -5, 10, 10))
tesselation = Tesselate(writer, tess, tess_id)
tesselation.draw_seed()

writer.new("figures/etape_1.tex")
tesselation.draw_star()

writer.new("figures/etape_2.tex")
tesselation.draw_edge()

writer.new("figures/etape_3.tex")
tesselation.show_base = True
tesselation.draw_tesselation()
tesselation.show_base = False 


writer.new("figures/finished.tex", size = (0, 0, 15, 20), n_tiles = 1)
tesselation.draw_tesselation()

bounds = (2, 2, 15, 22)
for i in range(5):
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]
    writer.new(f"figures/exemple_{i}.tex", size = bounds, n_tiles = 1)
    tesselation.set_tesselation(tess, tess_id)
    tesselation.draw_tesselation()

for i in range(2):
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]
    writer.new(f"figures/exemple_ray_dot_{i}.tex", bounds, n_tiles = 2)
    tesselation.set_tesselation(tess, tess_id)
    tesselation.draw_tesselation(np.random.uniform(low=0.1, high=np.pi/2), show_underlying = True)

for i in range(5):
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]
    writer.new(f"figures/exemple_ray_{i}.tex", size = bounds, n_tiles = 1)
    tesselation.set_tesselation(tess, tess_id)
    tesselation.draw_tesselation(np.random.uniform(low=0.1, high=np.pi/2))

bounds = (0, 0, 15, 5)
tess_id = random.choice(list(js.keys()))
tess = js[tess_id]
writer.new(f"figures/exemple_ray_sin.tex", size = bounds, n_tiles = 1)
tesselation.set_tesselation(tess, tess_id)
tesselation.draw_tesselation(np.random.uniform(low=0.1, high=np.pi/2), sin = True)

bounds = (0, 0, 15, 5)
tess_id = random.choice(list(js.keys()))
tess = js[tess_id]
writer.new(f"figures/exemple_ray_assym.tex", size = bounds, n_tiles = 1)
tesselation.set_tesselation(tess, tess_id)
tesselation.draw_tesselation(np.random.uniform(low=0.1, high=np.pi/2), assym = np.random.uniform(low=0.1, high=np.pi/2))

for i in range(30 * 30):
    bounds = (2, 2, 15, 22)
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]

    writer.new(f"figures/gallery_{i}.tex", size = bounds)
    tesselation.set_tesselation(tess, tess_id)
    if np.random.random() < 0.2:
        assym = np.random.uniform(low=0.1, high=np.pi/2)
        assym = 0.8 
    else:
        assym = False 
    if np.random.random() < 0.2:
        sin = True
    else:
        sin = False 
    if np.random.random() < 0.2:
        separated_site = True
    else:
        separated_site = False 
    #if np.random.random() < 0.1:
    #    n_iter = np.random.randint(1, 2)
    #else:
    #    n_iter = 0
    n_iter = 0
    #tesselation.draw_tesselation(np.random.uniform(low=0.1, high=np.pi/2), sin = sin, assym = assym, separated_site = separated_site)
    #tesselation.draw_n_ray(n_iter, i, np.random.uniform(low=0.1, high=np.pi/2), sin = sin, assym = assym, separated_site = separated_site)
    tesselation.draw_n_ray(n_iter, i, i/(30 * 30) * np.pi/2, sin = sin, assym = assym, separated_site = separated_site)
