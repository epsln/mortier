import json
import math
import numpy as np

import configparser 
import random

from tesselation import Tesselate 
from writer import BitmapWriter, SVGWriter

config = configparser.ConfigParser()
config.read('config.ini')

with open('data/database.json', 'r') as file:
        js = json.load(file)

if config['tesselation']['id'] != "random": 
    tess_id = config['tesselation']['id'] 
else:
    tess_id = random.choice(list(js.keys()))

tess = js[tess_id]
size = (int(config['svg']['size_x']), int(config['svg']['size_y']))

writer = BitmapWriter("images/images_0.png", size, n_tiles = config['tesselation']['n_tiles'])
#writer = SVGWriter("images/images_0.png", size, n_tiles = config['tesselation']['n_tiles'])
tesselation = Tesselate(writer, tess, tess_id)

for i in range(50):
    tess_id = random.choice(list(js.keys()))
    tess = js[tess_id]
    writer.new(f"images/images_{i}.png")
    tesselation.set_tesselation(tess, tess_id)
    tesselation.draw_tesselation(np.random.random() * np.pi/2)
