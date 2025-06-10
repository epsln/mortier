# Mortier 
## A Python-based SVG tiling generator
Python implementation of the tiling algorithm described in Dr. Soto Sanchez's thesis $On Periodic Tilings
with Regular Polygons$. 

## Installation
With poetry, simply run 
```
poetry install
```

## Usage 
In the config file, enter the desired id of the tiling then run
```
poetry run mortier/mortier.py
```

You can control the output size (in mm) and filename in the [svg] section.
