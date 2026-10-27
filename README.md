# wwt-glyph-generator

This is a small Python script to generate text spritesheet images for [WorldWide Telescope](http://worldwidetelescope.org/home),
as well as associated XML files instructing the WWT renderer about the locations of the various glyphs on each image.

## Usage

To create the glyph files, simply install the package requirements in your environment and run this package as a module

```bash
# All command-line arguments are optional
python -m wwt_glyph_generator \
--ttf=<path-to-ttf>
--version=<version #>
--characters=<string of characters to generate glyphs for>
--output-dir=<output-dir>
--fail-on-missing  # Omit if you want to generate glyphs even if font does not include all requested characters
```

Running without arguments, will generate glyph files using our current defaults: version 2, in a `docs` subdirectory of the current
directory, using the default WWT font (Microsoft Sans Serif).
