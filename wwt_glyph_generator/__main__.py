from argparse import ArgumentParser
import argparse
from os.path import join

from .config import WWTGlyphGeneratorConfig
from .constants import GLYPHS_V2
from .glyphs import create_glyphs


if __name__ == "__main__":

    default_font_path = join("fonts", "microsoft-sans-serif", "micross.ttf")

    parser = ArgumentParser(description="A tool for generating glyph images and associated XML for WorldWide Telescope")

    parser.add_argument("--output-dir", type=str, default="docs", help="The location to put the generated image and XML files")
    parser.add_argument("--version", type=int, default=2, help="The version number to tag the generated files with")
    parser.add_argument("--characters", type=str, default=GLYPHS_V2, help="The list of characters to include on the generated images")
    parser.add_argument("--ttf", type=str, default=default_font_path, help="The path of the TTF file to use")
    parser.add_argument("--fail-on-missing", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    create_glyphs(WWTGlyphGeneratorConfig(**vars(args)))
