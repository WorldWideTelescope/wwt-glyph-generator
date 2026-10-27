from dataclasses import dataclass

@dataclass
class WWTGlyphGeneratorConfig:
    ttf: str
    characters: str
    version: int
    output_dir: str
    fail_on_missing: bool
