from coords import coords
import random

def in_bounds(x, y, size_x, size_y):
    if x > 0 and x < size_x and y > 0 and y < size_y: 
        return True
    else:
        False

def planeCoords(T, W):
    #TODO: Move to coords, and clean up
    return coords([T.w[i] * W[i] for i in range(4)]).sum()

def planeToTileCoords(tiling, W, x, y):
    T1 = coords(tiling['T1'])
    T2 = coords(tiling['T2'])
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
