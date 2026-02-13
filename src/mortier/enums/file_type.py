from enum import Enum


class FileType(str, Enum):
    SVG = "svg" 
    PNG = "png" 
    JPG = "jpg" 
    tikz = "tex" 
