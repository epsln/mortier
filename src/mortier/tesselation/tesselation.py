import math
import random

import numpy as np

from mortier.coords import EuclideanCoords, LatticeCoords, Line
from mortier.face.face import Face
from mortier.utils.math_utils import in_bounds, planeCoords, planeToTileCoords


class Tesselation():
    def __init__(self, writer):
        self.writer = writer
        self.faces = []

        self.show_dual = False
        self.show_face = False
        self.show_base = False
        self.draw_unit_circle = False
        self.ray_tesselation = False
        self.angle = False
        self.assym_angle = False
        self.param_mode = False
        self.show_underlying = False
        self.separated_site_mode = False
        self.lacing_mode = False

    def fill_neighbor(self, faces):
        pass

    def draw_seed(self):
        pass

    def draw_cell(self):
        pass  
    
    def draw_star(self):
        pass 

    def draw_edge(self):
        pass 

    def tesselate_face(self):
        pass  

    def find_corners(self):
        pass

    def set_param_mode(self, mode = False):
        self.param_mode = mode 

    def set_angle(self, angle = False):
        self.angle = angle 
        self.writer.set_band_angle(angle)

    def set_assym_angle(self, angle = False):
        self.assym_angle = angle 

    def set_show_underlying(self, show_underlying = False):
        self.show_underlying = show_underlying 

    def set_separated_site_mode(self, separated_site = False):
        self.separated_site_mode = separated_site

    def draw_tesselation(self, frame_num = 0):
        self.tesselate_face()
        if self.show_base:
            self.draw_cell()

        tess_arr = []
        for f in self.faces:
            if self.show_underlying:
                self.writer.face(f, dotted = True)
            if self.angle:
                f = f.ray_transform(self.angle, self.writer.size, frame_num)
            self.writer.face(f)

        if self.draw_unit_circle:
            self.writer.circle(EuclideanCoords([self.writer.size[2]/2, self.writer.size[3]/2]),
                               self.scale)

        if self.tess_id: 
            caption = f"Pavage ${self.tess_id}$" 
        elif self.tile:
            caption = f"Pavage ${self.tile}$" 
        if self.angle and not self.assym_angle: 
            caption += f", avec $\\theta \\approx {round(self.angle, 3)}$"
        if self.separated_site_mode: 
            caption += ", sites séparés"
        if self.param_mode == "sin":
            caption += ", angle paramétrisé (sinus)"
        if self.param_mode == "perlin":
            caption += ", angle paramétrisé (bruit de Perlin)"
        if self.param_mode == "simplex":
            caption += ", angle paramétrisé (bruit Simplex)"
        if self.assym_angle:
            caption += f", angles assymétrique $\\theta_0 \\approx {round(self.angle, 3)}, \\theta_1 \\approx {round(self.assym_angle, 3)}$"
        if self.writer.lacing_mode:
            caption += ", entrelacements"
        if self.writer.bands_mode:
            caption += ", bandeaux"

        self.writer.set_caption(caption)
        self.writer.set_label(caption)
        output = self.writer.write()
        return output 

    def set_tesselation(self, tess, tess_id):
        self.tess = tess
        self.tess_id = tess_id
        self.T0 = LatticeCoords([0, 0, 0, 0])
        self.T1 = LatticeCoords(tess["T1"])
        self.T2 = LatticeCoords(tess["T2"])
        self.T3 = self.T1.translate(self.T2)
        self.seed = self.tess["Seed"]
        self.cell = Face([self.T0, self.T1, self.T3, self.T2])

    def set_writer(self, writer):
        self.writer = writer
