import json
import math
import numpy as np

import configparser 
import random
from multiprocessing import Pool

from tesselation import Tesselate 
from penrose import Penrose 
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
size = (0, 0, int(config['svg']['size_x']), int(config['svg']['size_y']))

writer = BitmapWriter("images/images_0.png", size, n_tiles = config['tesselation']['n_tiles'])
#writer = SVGWriter("images/images_0.png", size, n_tiles = config['tesselation']['n_tiles'])
tesselation = Tesselate(writer, tess, tess_id)

#for i in range(50):
#    tess_id = random.choice(list(js.keys()))
#    tess = js[tess_id]
#    writer.new(f"images/recursive_{i}_iters.png")
#    tesselation.set_tesselation(tess, tess_id)
#    tesselation.draw_n_ray(np.random.randint(3), np.random.uniform(0.1, np.pi/2))

#tess_id = random.choice(list(js.keys()))
#tess = js[tess_id]
#for i in range(30 * 15):
#    #tess_id = random.choice(list(js.keys()))
#    #tess = js["t3003"]
#    writer.new(f"images/images_{i}.png")
#    tesselation.set_tesselation(tess, tess_id)
#    angle =  (np.sin(i/(30 * 7.5) * 2 * np.pi)/2 + 0.5) * (np.pi/2 - 0.01)
#    tesselation.draw_tesselation(i, angle, sin = False)
    #tess_id = random.choice(list(js.keys()))
    #tess = js["t3003"]

#def f(i):
i = 0
writer = SVGWriter("penrose_red", size, n_tiles = config['tesselation']['n_tiles'])
writer = BitmapWriter("penrose_red.png", size, n_tiles = config['tesselation']['n_tiles'])
tesselation = Tesselate(writer, tess, tess_id)
#writer.new(f"images/pen_{i}.png")
penrose = Penrose(writer)
angle =  (np.sin(i/(30 * 5) * 2 * np.pi)/2 + 0.5) * np.pi/8
penrose.draw(9, angle, i)

#with Pool(8) as p:
#    p.map(f, [i for i in range(450)])
