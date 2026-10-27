import os
import warnings

from fontTools.ttLib import TTFont
from lxml.etree import Element, SubElement, tostring
from wand.drawing import Color, Drawing
from wand.image import Image

from wwt_glyph_generator.constants import DEFAULT_FONT

from .config import WWTGlyphGeneratorConfig


def check_char_in_font(char: str, font: TTFont) -> bool:

    # Check the Unicode cmap table
    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            if ord(char) in cmap.cmap:
                return True
    return False


def get_size_width(extent_width: float, horizontal_spacing: float, n_cols: int) -> float:
    column_spacing_term = 2 * horizontal_spacing / (n_cols + 1)
    return extent_width + column_spacing_term


def get_size_height(extent_height: float, image_height: float) -> float:
    return extent_height + round((image_height * 0.01), 1)


def batches(characters, batch_size):
    for i in range(0, len(characters), batch_size):
        yield characters[i:i + batch_size]


def _font_string(font_name: str | None, prefix="-"):
    return f"{prefix}{font_name.replace(' ', '')}" if font_name else ""


def glyph_filename(version: int, index: int, font_name: str | None, extension: str) -> str:
    font_str = _font_string(font_name)
    return f"glyphs{version}-{index}{font_str}.{extension}"


def summary_filename(version: int, font_name: str | None) -> str:
    font_str = _font_string(font_name, prefix="_")
    return f"glyphs{version}{font_str}_summary.xml"


def write_xml(root: Element, filepath: str):
    with open(filepath, 'w') as f:
        f.write(tostring(root, pretty_print=True).decode())


def create_glyphs(options: WWTGlyphGeneratorConfig):
    # Create the output directory, if it doesn't already exist
    output_folder = options.output_dir
    os.makedirs(output_folder, exist_ok=True)

    version = options.version
    characters = options.characters

    image_width = 2048
    font_height = 171
    
    n_cols = 8
    n_rows = 8
    row_height = 256
    image_height = row_height * n_rows
    
    padding = 32
    horizontal_spacing = int(image_width / n_cols)
    vertical_padding = padding
    vertical_spacing = row_height - font_height

    font = TTFont(options.ttf)
    font_name_table = font["name"]
    font_full_name = font_name_table.getBestFullName()
    font_display_name = None if font_full_name == DEFAULT_FONT else font_name_table.getDebugName(4)

    # Batch the glyphs into n_rows x n_cols batches
    batch_size = n_rows * n_cols
    batches_data = []
    for index, batch in enumerate(batches(characters, batch_size)):
    
        image_file = os.path.join(output_folder, glyph_filename(version, index, font_display_name, "png"))
        xml_file = os.path.join(output_folder, glyph_filename(version, index, font_display_name, "xml"))
    
        # Draw the glyph image
        character_data = {}
        horizontal_start = 29
        x = horizontal_start
        y0 = int(font_height - (vertical_spacing / 2)) + vertical_padding  # Note that the y position is the glyph baseline
        y = y0
        with Drawing() as draw, Image(width=image_width, height=image_height, background=Color('transparent'), format="PNG32") as image:
            draw.font_size = font_height 
            draw.font_family = font_full_name
            draw.fill_color = Color("rgba(255, 255, 255, 1)")
            draw.font_style = "normal"
            draw.font_weight = 1
            for char in batch:
                
                in_font = check_char_in_font(char, font)
                if not in_font:
                    error_message = f"Character {char} is not in f{font_display_name}"
                    if options.fail_on_missing:
                        raise ValueError(error_message)
                    else:
                        warnings.warn(error_message)
    
                metrics = draw.get_font_metrics(image, char)
                if x >= image_width:
                    x = horizontal_start
                    y += row_height
                width = round(metrics.text_width) + 3 if char != ' ' else 0
                character_data[char] = (x, y, width, round(metrics.text_height))
                draw.text(x, y, char)
                x += horizontal_spacing
        
            draw(image)
            image.alpha_channel = True
            image.save(filename=f"PNG32:{image_file}")
        
        # Create the XML file
        precision = 8
        root = Element("GlyphItems")
        for char, (x, y, width, height) in character_data.items():
            element = SubElement(root, "GlyphItem")
            is_space = char == ' '
            uv_height = 0 if is_space else round(height / image_height, precision)
            uv_width = round(width / image_width, precision)
            uv_left = round(x / image_width, 7)
            uv_top = round((y - y0) / image_height, precision)
            size_width = round(get_size_width(width, horizontal_spacing, n_cols), 4)
            size_height = round(get_size_height(height, image_height), 4)
            width = size_width if is_space else width
        
            element.set("Glyph", char)
            element.set("UVHeight", str(uv_height))
            element.set("UVWidth", str(uv_width))
            element.set("UVTop", str(uv_top))
            element.set("UVLeft", str(uv_left))
            element.set("ExtentsWidth", str(width))
            element.set("ExtentsHeight", str(height))
            element.set("SizeWidth", str(size_width))
            element.set("SizeHeight", str(size_height))
        
        write_xml(root, xml_file)
        batches_data.append(character_data)
    
    # Write out the summary metadata file
    root = Element("GlyphFiles")
    for index, data in enumerate(batches_data):
        element = SubElement(root, "GlyphFile")
        element.set("ImagePath", glyph_filename(version, index, font_display_name, "png"))
        element.set("XMLPath", glyph_filename(version, index, font_display_name, "xml"))
        element.set("Index", str(index))
    
        for character in data.keys():
            glyph = SubElement(element, "Glyph")
            glyph.set("Character", character)
    
    summary_output = os.path.join(output_folder, summary_filename(options.version, font_display_name))
    write_xml(root, summary_output)


