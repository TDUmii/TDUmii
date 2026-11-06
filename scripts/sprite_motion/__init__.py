"""Build the three approved sprite rigs and their source manifest."""
import json

from . import automation, bridge, quiet
from .core import ROOT


def main():
    entries = [bridge.build_sprite(), quiet.build_sprite(), automation.build_sprite()]
    (ROOT / 'assets' / 'c1-motion-source.json').write_text(json.dumps({'version': 3, 'generator': 'scripts/build_sprite_motion.py', 'method': 'Original PNG payload plus SVG source-part rigs; no raster edits', 'sprites': entries}, indent=2) + '\n', encoding='utf-8')
    for item in entries:
        print(f"{item['output']}: {item['width']}x{item['height']} source SHA256 {item['source_sha256']}")
