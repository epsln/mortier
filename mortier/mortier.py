import json
import math

import configparser 
import random

from tesselation import Tesselate 
from writer import BitmapWriter 

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
tesselation = Tesselate(writer, tess, tess_id)

for i in range(100):
    tess = js[tess_id]
    writer.new(f"images/images_{i}.png")
    tesselation.set_tesselation(tess, tess_id)
    tesselation.draw_tesselation(i * 1.0/300 * 3.1415926/2)
