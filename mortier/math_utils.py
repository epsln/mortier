from coords import LatticeCoords
import noise
import numpy as np
import random

def in_bounds(face, size):
    for v in face:
        if v.x < size[0] or v.x > size[2] or v.y < size[1] or v.y > size[3]: 
            return False 
    return True 

def map_num(x, min_in, max_in, min_out, max_out):
    return (((x - min_in) * (max_out - min_out)) / (max_in - min_in)) + min_out 


def planeCoords(T, W):
    #TODO: Move to coords, and clean up
    return LatticeCoords([T.w[i] * W[i] for i in range(4)]).sum()

def planeToTileCoords(tiling, W, x, y):
    T1 = LatticeCoords(tiling['T1'])
    T2 = LatticeCoords(tiling['T2'])
    z1 = planeCoords(T1, W)
    z2 = planeCoords(T2, W)
    a = z1.real
    b = z1.imag
    c = z2.real
    d = z2.imag
  
    det = a * d - b * c;
    ai = d / det
    bi = -c / det
    ci = -b /det
    di = a / det
    
    return complex(ai * x + bi * y, ci * x + di * y)

def angle_parametrisation(point, mode, bounds):
    if mode == "sin":
        return (np.sin(map_num(point.y, bounds[1], bounds[3], 0, 2 * np.pi)) + 1)/2
    elif mode == "perlin":
        x = map_num(point.x, bounds[0], bounds[2], 0, 2)
        y = map_num(point.y, bounds[1], bounds[3], 1, 2)
        angle = noise.pnoise2(x, y,  octaves=3)
        angle += 1
        angle = np.clip(angle, 0.1, np.pi/2)
        return angle
    elif mode == "simplex":
        x = map_num(point.x, bounds[0], bounds[2], 0, 2)
        y = map_num(point.y, bounds[1], bounds[3], 1, 3)
        angle = noise.snoise2(x, y,  octaves=3)
        angle += 1
        angle = np.clip(angle, 0.1, np.pi/2)
        return angle
