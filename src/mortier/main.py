import json
import random

import click
import numpy as np

from mortier.enums import (FileType, HatchType, ParamType, TesselationType,
                           TileType)
from mortier.tesselation import (HyperbolicTesselation, PenroseTesselation,
                                 RegularTesselation)
from mortier.writer import BitmapWriter, SVGWriter, TikzWriter

with open("data/database.json", "r") as file:
    js = json.load(file)


@click.command()
@click.option(
    "--tesselation_type",
    default="regular",
    type=click.Choice(TesselationType, case_sensitive=False),
    help="Tesselation type.",
)
@click.option(
    "--tess_id",
    default=random.choice(list(js.keys())),
    help="Tesselation ID in the database.",
)
@click.option(
    "--file_type",
    default="bitmap",
    type=click.Choice(FileType, case_sensitive=False),
    help="Output Type.",
)
@click.option("--output", default="img.png", help="Output file name.", type=str)
@click.option(
    "--output_size", nargs=2, default=(1920, 1080), type=(int, int), help="Output size."
)
@click.option("--scale", default=50, type=int, help="Tesselation scale.")
@click.option(
    "--angle",
    default=None,
    type=click.FloatRange(0, np.pi / 2, clamp=True),
    help="Angle of the rays.",
)
@click.option(
    "--parametrised",
    default=None,
    type=click.Choice(ParamType, case_sensitive=False),
    help="Apply a type of noise to the rays angle.",
)
@click.option("--bands", is_flag=True, help="Bands mode")
@click.option("--lace", is_flag=True, help="Lace mode")
@click.option("--bezier", is_flag=True, help="Sides are drawn as bezier curves")
@click.option("--bands_width", default = 2, type=click.FloatRange(0, clamp=True), help="Bands width")
@click.option(
    "--hatch_type",
    default=None,
    type=click.Choice(HatchType, case_sensitive=False),
    help="Type of Hatch filling",
)
@click.option("--hatch_angle", default=0.0, type=float, help="Hatch angle in degrees")
@click.option(
    "--hatch_spacing",
    default=10.0,
    type=click.FloatRange(min=1),
    help="Hatch angle in degrees",
)
@click.option("--cross_hatch", is_flag=True, help="Cross hatching")
@click.option(
    "--pq",
    default=(3, 7),
    type=(int, int),
    help="Number of sides and number of neighbors of Hyperbolic Tesselation",
)
@click.option("--tile", default="P2", type=click.Choice(TileType, case_sensitive=False))
@click.option("--depth", default=4, type=click.IntRange(min=2), help="Inflation depth")
@click.option("--half_plane", is_flag=True, help="Inflation depth")
@click.option("--refine", default=0, type=click.IntRange(min=0), help="Inflation depth")
@click.option(
    "--assym_angle",
    default=None,
    type=click.FloatRange(min=0),
    help="Use an assymetrical angle for ray projection",
)
@click.option(
    "--separated_sites",
    default=None,
    type=click.IntRange(min=2, max=10),
    help="Use separated ray projection sites",
)
@click.option(
    "--color",
    default=(255, 255, 255),
    type=(int, int, int),
    help="Color of sides",
)
@click.option(
    "--color_bg",
    default=None,
    type=(int, int, int),
    help="Color of the background",
)
@click.option(
    "--color_hatch",
    default=None,
    type=(int, int, int),
    help="Color of the hatching",
)
def tess_param(
    tesselation_type,
    tess_id,
    file_type,
    output,
    output_size,
    scale,
    angle,
    parametrised,
    bands,
    lace,
    bands_width,
    bezier,
    hatch_type,
    hatch_angle,
    hatch_spacing,
    cross_hatch,
    tile,
    pq,
    depth,
    refine,
    half_plane,
    assym_angle,
    separated_sites,
    color,
    color_bg,
    color_hatch
):
    tess = js[tess_id]
    if file_type == FileType.BITMAP:
        writer = BitmapWriter(f"{output}", size = (0, 0, output_size[0], output_size[1]))
    elif file_type == FileType.SVG:
        writer = SVGWriter(f"{output}", size = (0, 0, output_size[0], output_size[1]))
    else:
        writer = TikzWriter(f"{output}")
    writer.n_tiles = scale
    writer.size = (0, 0, output_size[0], output_size[1])
    writer.bands_mode = bands 
    writer.lacing_mode = lace
    writer.bands_width = bands_width
    writer.bezier_curve = bezier
    writer.color_line = color 
    writer.set_color_bg(color_bg)
    writer.hatch_fill_parameters["angle"] = hatch_angle
    writer.hatch_fill_parameters["spacing"] = hatch_spacing
    writer.hatch_fill_parameters["crosshatch"] = cross_hatch
    writer.hatch_fill_parameters["type"] = hatch_type
    if color_hatch:
        writer.hatch_fill_parameters["color"] = color_hatch 

    if tesselation_type == TesselationType.REGULAR:
        tesselation = RegularTesselation(writer, tess, tess_id)
    elif tesselation_type == TesselationType.HYPERBOLIC:
        tesselation = HyperbolicTesselation(writer, pq[0], pq[1], depth)
        tesselation.half_plane = half_plane
        tesselation.refine_tiling(refine)
    else:
        tesselation = PenroseTesselation(writer, tile=tile, level=depth)
    tesselation.set_angle(angle)
    tesselation.set_param_mode(parametrised)
    tesselation.set_assym_angle = assym_angle
    tesselation.set_separated_site_mode(separated_sites)
    tesselation.draw_tesselation()


if __name__ == "__main__":
    tess_param()
