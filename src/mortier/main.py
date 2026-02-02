from mortier.tesselation.regular_tesselation import RegularTesselation
from mortier.tesselation.hyperbolic import HyperbolicTesselate 
from mortier.tesselation.penrose import Penrose 
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
    writer = BitmapWriter(f"images/img_{i}.png", size, n_tiles = 80, bands_mode = False, bands_width = 2)
    #tesselation = RegularTesselation(writer, tess, tess_id)
    tesselation = HyperbolicTesselate(writer, 3, 8, 4)
    angle = np.random.uniform(low = 0.2, high = np.pi/2)
    tesselation.set_assym_angle = np.random.uniform(low=0.1, high=angle)
    tesselation.set_separated_site_mode(np.random.randint(3, 10))
    tesselation.set_angle(angle)
    print(f"Computing image {i} (tess_id: {tess_id} angle: {angle})")
    tesselation.draw_tesselation([i, 300])
