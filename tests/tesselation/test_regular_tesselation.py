from mortier.tesselation import RegularTesselation
from mortier.writer.writer import Writer 

def test_init():
    w = Writer("test", size = [0, 0, 10, 10])
    tess = {"T1": [2, 0, -1, 0], "T2": [-1, 0, 2, 0], "Seed": [[0,0,0,0],[0,0,1,0]]} 
    tess_id = "test"
    t = RegularTesselation(w, tess, tess_id)
