"""Build self-contained SVG rigs from byte-identical approved C1 artwork.

Only SVG masks, clipped source instances and vector overlays are animated.
The PNG payload is read without decoding or modifying it. Run from any cwd.
"""
import base64
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


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


def main():
    entries = []
    bridge_eyes = '<path d="M1019 521L1079 512L1087 570L1027 579Z M1170 499L1231 490L1239 548L1178 557Z"/>'
    entries.append(build('bridge', {'eyes': bridge_eyes, 'caret': '<rect x="516" y="643" width="100" height="32"/>'}, '<rect x="516" y="643" width="100" height="32"/>',
        blink(bridge_eyes, 535) +
        '''<rect x="516" y="643" width="100" height="32" fill="#172330"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcaret)"><animate attributeName="opacity" values="1;0;1" calcMode="discrete" dur="1.2s" repeatCount="indefinite"/></use>
<g fill="#9cf1aa"><path d="M532 552H571V569H532Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.16;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path><path d="M585 552H626V569H585Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.29;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path><path d="M640 552H681V569H640Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.42;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path></g>
<path d="M1109 246L1159 240L1163 284L1113 290Z" fill="#ff8c87" opacity="0"><animate attributeName="opacity" values="0;0;.65;0;0" keyTimes="0;.70;.76;.84;1" dur="4.8s" repeatCount="indefinite"/></path>''', 4.8))
    quiet_eyes = '<rect x="915" y="345" width="86" height="53"/><rect x="1034" y="345" width="85" height="53"/>'
    book_surface = '<path d="M698 524H758L831 568H848L916 524H966L995 621H720Z"/>'
    entries.append(build('quiet', {'eyes': quiet_eyes, 'book-surface': book_surface}, '',
        blink(quiet_eyes, 381, '3.8s') +
        '''<g clip-path="url(#PREFIXbook-surface)" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.25;.28;.44;.47;1" dur="5.2s" repeatCount="indefinite"/>
<path d="M839 579L850 620L972 611L954 535Z" fill="#fff0d2" stroke="#e9c58d" stroke-width="3" stroke-linejoin="miter"><animate attributeName="d" values="M839 579L850 620L972 611L954 535Z;M839 579L850 620L972 611L954 535Z;M839 579L850 620L972 611L954 535Z;M839 579L850 620L867 614L851 551Z;M839 579L850 620L725 611L714 540Z;M839 579L850 620L725 611L714 540Z" keyTimes="0;.25;.28;.36;.44;1" dur="5.2s" repeatCount="indefinite"/></path><path d="M839 579L850 620" fill="none" stroke="#ad773d" stroke-width="4" opacity=".45"/></g>
<rect x="1084" y="172" width="28" height="22" fill="#ff9b8f" opacity="0"><animate attributeName="opacity" values="0;0;.70;0;0" keyTimes="0;.45;.49;.55;1" dur="5.2s" repeatCount="indefinite"/></rect>''', 5.2))
    auto_eyes = '<path d="M1035 413L1095 421L1088 479L1028 472Z M1180 430L1243 438L1235 498L1173 490Z"/>'
    # Trace the gear's own stepped outline, excluding adjacent replay arrows.
    gear = '<path d="M530 350H613V376H661V396L680 396L697 415V445L680 452H715V525L694 541V578L677 596H662V615H614V636H529V615H481V596H463L447 579V548L462 540H434L421 525V469L434 454H463L447 440V415L465 396H482V375H530Z"/>'
    cursor = '<rect x="219" y="514" width="249" height="403"/>'
    entries.append(build('automation', {'eyes': auto_eyes, 'gear': gear, 'cursor': cursor}, gear + cursor,
        blink(auto_eyes, 454, '3.4s') +
        '''<g><animateTransform attributeName="transform" type="rotate" from="0 570 494" to="360 570 494" dur="8s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXgear)"/></g>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;8 -8;0 0;0 0" keyTimes="0;.32;.38;.44;1" dur="2s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcursor)"/></g>
<g fill="none" stroke="#ffbf3e" stroke-width="9" opacity="0"><path d="M245 488V463M203 510L184 491M281 501L300 482"/><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.34;.39;.52;1" dur="2s" repeatCount="indefinite"/></g>
<path d="M1182 159L1231 165L1225 209L1176 203Z" fill="#ff9b8f" opacity="0"><animate attributeName="opacity" values="0;0;.75;0;0" keyTimes="0;.42;.48;.57;1" dur="2s" repeatCount="indefinite"/></path>''', 8))
    (ROOT / 'assets' / 'c1-motion-source.json').write_text(json.dumps({'version': 2, 'generator': 'scripts/build_sprite_motion.py', 'method': 'Original PNG payload plus SVG source-part rigs; no raster edits', 'sprites': entries}, indent=2) + '\n', encoding='utf-8')
    for item in entries:
        print(f"{item['output']}: {item['width']}x{item['height']} source SHA256 {item['source_sha256']}")


if __name__ == '__main__':
    main()
