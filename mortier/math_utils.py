from coords import LatticeCoords
import random

def in_bounds(face, size_x, size_y):
    for v in face:
        if v.x < 0 or v.x > size_x or v.y < 0 or v.y > size_y: 
            return False 
    return True 

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
