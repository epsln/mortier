import json
import math

import configparser 
import random

from tesselation import tesselate

config = configparser.ConfigParser()
config.read('config.ini')

with open('data/Galebach.json', 'r') as file:
        js = json.load(file)

if config['tesselation']['id'] != "random": 
    tess_id = config['tesselation']['id'] 
else:
    tess_id = random.choice(list(js.keys()))

tess = js[tess_id]
tesselate(config, tess)
