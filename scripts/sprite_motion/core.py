"""Build self-contained SVG rigs from byte-identical approved C1 artwork.

Only SVG masks, clipped source instances and vector overlays are animated.
The PNG payload is read without decoding or modifying it. Run from any cwd.
"""
import base64
import hashlib
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]


def build(name, clips, holes, rig, duration):
    source = ROOT / 'assets' / f'c1-{name}-art.png'
    raw = source.read_bytes()
    width, height = struct.unpack('>II', raw[16:24])
    prefix = f'c1-{name}-'
    # Each asset has exactly one embedded copy of its original PNG.
    defs = ''.join(f'<clipPath id="{prefix}{key}">{shape}</clipPath>' for key, shape in clips.items())
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-hidden="true">
<title>{name.title()} animated sprite</title>
<style>.sprite-still{{display:none}}@media(prefers-reduced-motion:reduce){{.sprite-motion{{display:none}}.sprite-still{{display:inline}}}}</style>
<defs><image id="{prefix}source" width="{width}" height="{height}" xlink:href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>{defs}
<mask id="{prefix}base" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect width="{width}" height="{height}" fill="white"/><g fill="black">{holes}</g></mask></defs>
<use class="sprite-still" xlink:href="#{prefix}source"/>
<g class="sprite-motion"><use xlink:href="#{prefix}source" mask="url(#{prefix}base)"/>{rig.replace('PREFIX', prefix)}</g>
</svg>'''
    target = ROOT / 'assets' / f'c1-{name}-motion.svg'
    target.write_text(svg, encoding='utf-8', newline='\n')
    return {'source': source.name, 'output': target.name, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'width': width, 'height': height, 'loop_seconds': duration}


def blink(shapes, cy, duration='3.2s'):
    # Two-state pixel blink. Overscan covers antialiased source-eye edges;
    # the untouched original remains visible between blinks.
    return f'''<g opacity="0" fill="#171e27" stroke="#171e27" stroke-width="8" stroke-linejoin="miter">{shapes}<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.429;.43;.50;1" calcMode="discrete" dur="{duration}" repeatCount="indefinite"/></g>'''

