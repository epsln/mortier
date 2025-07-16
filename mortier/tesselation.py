from coords import coords 
from math_utils import in_bounds, planeToTileCoords, planeCoords
import math
import svgwrite
from svgwrite import cm, mm   

def tesselate(config, tess):
    n_tiles = int(config['tesselation']['n_tiles'])
    size_x = float(config['svg']['size_x'])
    size_y = float(config['svg']['size_y'])
    svg_name = config['svg']['filename']

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
    
    W = [1, 
         0.8660254037844386 + 0.5* 1j,
         0.5, 0.8660254037844386 * 1j,
         0 + 1j
     ]

    neighbor_arr = {}

    i_min = 0
    i_max = 0
    j_min = 0
    j_max = 0

    corners = [0, size_x, size_y * 1j, size_x + size_y * 1j]

    for z in corners: 
        z_ = planeToTileCoords(tess, W, z.real / n_tiles , z.imag / n_tiles)

        i_min = min(i_min, z_.real)
        j_min = min(j_min, z_.imag)
        i_max = max(i_max, z_.real)
        j_max = max(j_max, z_.imag)

    i_min = math.floor(i_min - 1);
    i_max = math.ceil(i_max + 1);
    j_min = math.floor(j_min - 1);
    j_max = math.ceil(j_max + 1);

    for x in range(i_min, i_max):
        for y in range(j_min, j_max):
            translate = T1.scale(x).translate(T2.scale(y))
            for s in seed: 
                s = coords(s)
                WC = s.translate(translate);
                neighbor_arr[str(WC.w)] = WC.w

    for x in range(i_min, i_max):
        for y in range(j_min, j_max):
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
                    F = nfc.scale(n_tiles)
                    fc = nfc
                
                    if (f == 0):
                      FInit = F
                    if f > 0 and f + skip < 12:
                      x1 = F.x
                      y1 = F.y
                      x2 = F0.x
                      y2 = F0.y
                      #F_init = coords(y1 - y0, x0 - x1)
                      if in_bounds(x1, y1, size_x, size_y) and in_bounds(x2, y2, size_x, size_y):
                          dwg.add(
                            dwg.line(
                                start = (x1 * mm, y1 * mm),
                                end = (x2 * mm, y2 * mm),
                                stroke="black",
                                stroke_width = 1
                            )
                        )    

        dwg.save()

