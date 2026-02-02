from mortier.tesselation import Tesselate 
from mortier.hyperbolic import HyperbolicTesselate 
from mortier.penrose import Penrose 
from mortier.writer import BitmapWriter, SVGWriter, TikzWriter

import json
import math
import numpy as np

import configparser 
import random
from multiprocessing import Pool

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
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]
    size = (0, 0, int(config['svg']['size_x']), int(config['svg']['size_y'])) 
    writer = SVGWriter(f"images/img_{i}", size, n_tiles = 10, bands_mode = False, bands_width = 2)
    tesselation = HyperbolicTesselate(writer, 7, 4, 4)
    tesselation.refine_tiling(3)
    tesselation.set_scale(1.75)
    angle = np.random.uniform(low = 0.2, high = np.pi/2)
    tesselation.set_assym_angle = np.random.uniform(low=0.1, high=angle)
    tesselation.set_separated_site_mode(np.random.randint(3, 10))
    tesselation.set_angle(angle)
    print(f"Computing image {i} (tess_id: {tess_id} angle: {angle})")
    tesselation.draw_tesselation([i, 300])
