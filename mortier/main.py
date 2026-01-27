import json
import math
import numpy as np

import configparser 
import random
from multiprocessing import Pool

from tesselation import Tesselate 
from penrose import Penrose 
from writer import BitmapWriter, SVGWriter, TikzWriter

config = configparser.ConfigParser()
config.read('config.ini')

with open('data/database.json', 'r') as file:
        js = json.load(file)

if config['tesselation']['id'] != "random": 
    tess_id = config['tesselation']['id'] 
else:
    tess_id = random.choice(list(js.keys()))

tess_id = "t3003"
tess_id = random.choice(list(js.keys()))
tess = js[tess_id]
size = (0, 0, int(config['svg']['size_x']), int(config['svg']['size_y'])) 
tess_id = random.choice(list(js.keys()))

for i in range(300):
    tess = js[tess_id]
    size = (0, 0, int(config['svg']['size_x']), int(config['svg']['size_y'])) 
    writer = BitmapWriter(f"images/img_{i}.png", size, n_tiles = 100, lacing_mode = False, bands_width = 8) 
    #writer = BitmapWriter(f"images/img_{i}.png", size, n_tiles = 350, lacing_mode = False, bands_width = 16) 
    #writer = SVGWriter(f"images/img_{i}", size, n_tiles = 20, lacing_mode = True, bands_width = 4) 
    tesselation = Tesselate(writer, tess, tess_id)
    tesselation.set_tesselation(tess, tess_id)
    angle = np.random.uniform(low = 0.1, high = np.pi/2) 
    #if np.random.random() > 0.2:
    #    assym = np.random.uniform(low=0.1, high=angle)
    #else:
    #    assym = False
    #if np.random.random() > 0.2:
    #    separated_site = np.random.randint(3, 10) 
    #else:
    #    separated_site = False
    #tesselation.draw_n_ray(0, angle, assym = assym, separated_site = separated_site)
    tesselation.set_sin_mode("perlin")
    angle = np.random.uniform(low = 0.2, high = np.pi/2)
    angle = 0.4 
    print(f"Computing image {i} (tess_id: {tess_id} angle: {angle})")
    tesselation.set_angle(angle)
    tesselation.draw_tesselation(i)
    #tesselation.draw_tesselation(0.5)
#writer.new(f"figures/penrose_P2.tex")
#penrose = Penrose(writer, "P2")
#penrose.draw(8)
#writer.new(f"figures/penrose_P3.tex")
#penrose = Penrose(writer, "P3")
#penrose.draw(8)
