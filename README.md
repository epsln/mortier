# Mortier 
## A Python-based tiling generator
![Mortier example](data/mortier.png)
Mortier is a powerful Python-based tiling generator. Mortier can generate regular, aperiodic and hyperbolic tilings. It is also able to generate an infnity of other tilings based on the "Polygon in Contact" technique. Mortier can output your tiling as a vector SVG, or a nice PNG. It even has support for Tikz figure generation.

The algorithm for constructing the regular polygon is described in Dr. Soto Sanchez's thesis $On Periodic Tilings with Regular Polygons$. Mortier uses Hypertiling to generate the Hyperbolic tesselations. 

Mortier also implements hatch filling (lines or dots) for your tilings, and is able to create "laceworks", where the sides of the faces are shown as "laces" going under and over each other, creating a style similar to Celtic laceworks.

## Features

- Tessellation types:
    - RegularTesselation: Lattice-based tilings from a database of predefined seeds.
    - PenroseTesselation: P2 and P3 aperiodic tilings with configurable inflation depth.
    - HyperbolicTesselation: {p, q} hyperbolic tilings with multiple layers and refinement.

- "Polygon in Contact" implementation: 
    - Fast 
    - Parametrisation of the angles with sinus, Perlin, or Simplex noise
    - Asymmetrical rays and separated projection sites

- Rendering backends:
    - BitmapWriter: Export as raster images (PNG, JPEG, etc.).
    - SVGWriter: Export scalable vector graphics.
    - TikzWriter: Export LaTeX TikZ figures.

- Even more customizations:
    - Bands and lace modes with configurable width
    - Bézier curve sides for smooth rendering
    - Hatch fill patterns with angle, spacing, and cross-hatching options
    - Optional half-plane conversion for hyperbolic tilings
    - Flexible scaling and output size

## Installation
```
git clone git@github.com:epsln/mortier.git
cd mortier
poetry install
```

## Usage 
Simply run:
```
poetry run python src/mortier/mortier.py
```

Now, to add some complexity (breathe in now):
Generate a random semi-regular paving, output on a file named foo.svg sized as 297x210mm, zoomed out slightly, with the Polygon in Contact method used with an angle equals 0.2, with sides represented as bands with a width of 1mm and hatch the faces with lines which are angled by 0.4 radians. 
```
python main.py --tesselation_type regular --tess_id "example_id" \
               --file_type bitmap --output img.png \
               --output_size 1920 1080 --scale 50 \
               --angle 0.2 --bands --hatch_type line --hatch_angle 0.4 
```

### CLI Options
As seen just above, Mortier provides extensive control over the generated tilings

- `--tesselation_type` : regular, hyperbolic, penrose
- `--tess_id` : ID of the tessellation in the database (data/database.json)
- `--file_type` : bitmap, svg, tikz
- `--output` : Output filename
- `--output_size` : Width and height in pixels
- `--scale` : Tessellation scale factor
- `--angle` : Global ray angle (0–π/2)
- `--parametrised`: Parametric angle type (sin, perlin, simplex)
- `--bands` : Enable bands mode
- `--lace` : Enable lace mode
- `--bezier` : Draw sides as Bézier curves
- `--bands_width` : Width of bands
- `--hatch_type` : Type of hatch fill
- `--hatch_angle` : Hatch angle in degrees
- `--hatch_spacing` : Distance between hatch lines
- `--cross_hatch` : Enable cross-hatching
- `--pq` : Sides and neighbors for hyperbolic tiling (p, q)
- `--tile` : Tile type for Penrose (P2, P3)
- `--depth` : Inflation depth for Penrose/hyperbolic
- `--half_plane` : Convert hyperbolic tiling to half-plane model
- `--refine` : Refinement level for hyperbolic tiling
- `--assym_angle` : Asymmetrical ray angle
- `--separated_sites` : Number of separated projection sites

## Tilings
### Regular Tilings
Mortier is able to produce semi-regular tilings, based on the database produced in Dr. Soto-Sanchez thesis (and it's algorithm). Those tilings are based on regular polygons, which are convex polygons with N sides and equiangle. Those tilings are the default one used when running  
### Penrose Tilings
Mortier also implements the two famous Penrose Tilings, P2 and P3. Those tilings are aperiodic, which means that they never truly repeats. 
### Hyperbolic Tilings
Mortier uses Hypertiling to produce P/Q tilings of the hyperbolic space. A PQ tiling is a tiling with polygons with P sides, which all have Q neighbors.
