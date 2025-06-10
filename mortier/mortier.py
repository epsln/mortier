import json
import math

import svgwrite
from svgwrite import cm, mm   
import random
import configparser 

from coords import coords 
from math_utils import welzl

def in_bounds(x, y, d_welzl):
    if x > d_welzl and x < 1000 + d_welzl and y > d_welzl and y < 1000 + d_welzl:
        return True
    else:
        False

config = configparser.ConfigParser()
config.read('config.ini')
n_tiles = int(config['tesselation']['n_tiles'])
tess_id = config['tesselation']['id'] 
size_x = float(config['svg']['size_x'])
size_y = float(config['svg']['size_y'])
svg_name = config['svg']['filename']

with open('data/Galebach.json', 'r') as file:
        js = json.load(file)

index = 1

tess = js[tess_id]
T1 = coords(tess["T1"])
T2 = coords(tess["T2"])
seed = tess["Seed"]
svg_size = (
    size_x,
    size_y,
)
dwg = svgwrite.Drawing(
    f"{svg_name}.svg", size=(f"{svg_size[0]}mm", f"{svg_size[1]}mm")
)

polytype = [ -1, -1, 3, 4, 6, 12 ];
dir12 = []
dir12.append(coords([1, 0, 0, 0]))
dir12.append(coords([0, 1, 0, 0]))
dir12.append(coords([0, 0, 1, 0]))
dir12.append(coords([0, 0, 0, 1]))
dir12.append(coords([-1, 0, 1, 0]))
dir12.append(coords([0, -1, 0, 1]))
dir12.append(coords([-1, 0, 0, 0]))
dir12.append(coords([0, -1, 0, 0]))
dir12.append(coords([0, 0, -1, 0]))
dir12.append(coords([0, 0, 0, -1]))
dir12.append(coords([1, 0, -1, 0]))
dir12.append(coords([0, 1, 0, -1]))

neighbor_arr = {}
d_min = 1000

hull = []
for x in range(1):
    for y in range(1):
        translate = T1.scale(x).translate(T2.scale(y))
        for s in seed: 
            s = coords(s)
            WC = s.translate(translate);
            hull.append(WC)

#Use Welzl method to figure out the shape of the hull, and how much we will need to compute to fill the page
#-> Find the minimum enscribed circle means we know how much space is used per cycle (one cycle = one TS tick)
#Use this distance to compute the number of cycle needed 
#TODO: Use manhattan distance since we have a rectangular page (maybe bias with aspect ratio ?)
d_welzl = welzl(hull).r
TS_X = int(size_x/(size_x/n_tiles * d_welzl)) + 1
TS_Y = int(size_y/(size_y/n_tiles * d_welzl)) + 1
for x in range(-TS_X, TS_X):
    for y in range(-TS_X, TS_X):
        translate = T1.scale(x).translate(T2.scale(y))
        for s in seed: 
            s = coords(s)
            WC = s.translate(translate);
            neighbor_arr[str(WC.w)] = WC.w

for x in range(-TS_Y, TS_Y):
    for y in range(-TS_Y, TS_Y):
        translate = T1.scale(x).translate(T2.scale(y))
        for s in seed: 
            neighs = []
            s = coords(s)
            WC = s.translate(translate);
        
            for d in range(6): 
              neighbor = WC.translate(dir12[d])
              if str(neighbor.w) in neighbor_arr:
                  neighs.append(d)

            if len(neighs) <= 1:
                continue

            for n, next_n in zip(neighs, neighs[1:]):
              maxDist = 0;
              diff = next_n - n
              skip = int(12/polytype[diff])

              fc = WC
              F = coords([0, 0, 0, 0])
              for f in range(0, 12, skip): 

                F0 = F
                nfc = fc.translate(dir12[(n + f) % 12 ] )
                F = nfc
                fc = nfc
            
                if (f == 0):
                  FInit = F
                if f > 0 and f + skip < 12:
                  x1 = F.x * size_x/n_tiles + size_x/2 
                  y1 = F.y * size_y/n_tiles + size_y/2 
                  x2 = F0.x * size_x/n_tiles + size_x/2 
                  y2 = F0.y * size_y/n_tiles + size_y/2 
                  #F_init = coords(y1 - y0, x0 - x1)
                  if in_bounds(x1, y1, d_welzl) and in_bounds(x2, y2, d_welzl):
                      dwg.add(
                        dwg.line(
                            start = (x1 * mm, y1 * mm),
                            end = (x2 * mm, y2 * mm),
                            stroke="black",
                            stroke_width = 1
                        )
                    )    

    dwg.save()

