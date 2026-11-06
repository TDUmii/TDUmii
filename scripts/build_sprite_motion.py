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


def reading_page():
    # The binding is the short cream-paper junction, not the tall amber spine.
    # A lifted leaf sits above the covers; the source covers are restored in front.
    # Bowed long edges flex; the short straight edge keeps paper corners crisp.
    # No perimeter stroke: an outlined straight sliver reads as a rigid pointer.
    poses = [
        'C866 557 912 534 950 530L968 540C926 546 875 566 848 580',
        'C858 550 906 518 943 525L950 540C909 545 872 567 848 580',
        'C844 547 867 516 889 516L895 532C876 548 859 567 848 580',
        'C824 550 818 527 830 514L849 518C858 539 854 559 848 580',
        'C813 550 774 516 754 519L748 533C779 549 817 568 848 580',
        'C806 551 753 528 716 532L713 543C752 548 806 567 848 580',
    ]
    shapes = ['M832 569' + poses[i] + 'Z' for i in [0, 0, 1, 2, 3, 4, 5, 5, 5]]
    times = '0;.22;.245;.28;.31;.34;.38;.40;1'
    return f'''<g class="reading-leaf" opacity="0">
<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.22;.40;1" calcMode="discrete" dur="7s" repeatCount="indefinite"/>
<path d="{shapes[0]}" fill="#faecd2">
<animate attributeName="d" values="{';'.join(shapes)}" keyTimes="{times}" dur="7s" repeatCount="indefinite"/>
<animate attributeName="fill" values="#faecd2;#faecd2;#f2e3c8;#fff0d4;#fff0d4" keyTimes="0;.25;.31;.35;1" dur="7s" repeatCount="indefinite"/>
</path></g><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXbook-covers)"/>'''


def main():
    entries = []
    bridge_eyes = '<path d="M1019 521L1079 512L1087 570L1027 579Z M1170 499L1231 490L1239 548L1178 557Z"/>'
    # Head and antenna move together around the neck; torso and rays stay put.
    bridge_head = '<path d="M1065 200H1210V312L1328 310L1350 360L1390 360L1400 418L1450 418L1500 575L1469 600L1420 611L1420 651L1370 667L1303 650L1040 685L965 720L928 677L879 680L842 530L864 504L864 489L896 482L896 416L927 407L927 386L943 375L943 351L1100 327L1093 321L1065 328Z"/>'
    # Foreground torso uses original pixels and the actual slanted silver top.
    # It occludes the neck underlap, keeping the white chest continuous.
    bridge_torso = '<path d="M1040 685L1303 650L1307 677H1337V696H1361V741H1306V856H1070V812H1042V784H1018V710H1040Z"/>'
    entries.append(build('bridge', {'eyes': bridge_eyes, 'head': bridge_head, 'torso': bridge_torso, 'caret': '<rect x="516" y="643" width="100" height="32"/>'}, bridge_head + '<rect x="516" y="643" width="100" height="32"/>',
        '<path d="M1005 650L1338 629L1355 704L1020 741Z" fill="#06101b"/><g><animateTransform attributeName="transform" type="rotate" values="0 1170 653;0 1170 653;-3 1170 653;-3 1170 653;1.5 1170 653;0 1170 653;0 1170 653" keyTimes="0;.20;.30;.48;.60;.69;1" dur="6.4s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXhead)"/>' + blink(bridge_eyes, 535) + '</g><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXtorso)"/>' +
        '''<rect x="516" y="643" width="100" height="32" fill="#172330"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcaret)"><animate attributeName="opacity" values="1;0;1" calcMode="discrete" dur="1.2s" repeatCount="indefinite"/></use>
<g fill="#9cf1aa"><path d="M532 552H571V569H532Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.16;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path><path d="M585 552H626V569H585Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.29;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path><path d="M640 552H681V569H640Z" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.42;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/></path></g>
''', 6.4))
    quiet_eyes = '<rect x="915" y="345" width="86" height="53"/><rect x="1034" y="345" width="85" height="53"/>'
    book_covers = '<path d="M697 548H766V560H799V572H829V581L840 621H721Z M849 581H861V574H889V560H913V554H944V546L975 539L998 621H860Z M829 581H849L861 621H840Z"/>'
    entries.append(build('quiet', {'eyes': quiet_eyes, 'book-covers': book_covers}, '',
        blink(quiet_eyes, 381, '3.8s') +
        reading_page() +
        '''<rect x="1084" y="172" width="28" height="22" fill="#ff9b8f" opacity="0"><animate attributeName="opacity" values="0;0;.70;0;0" keyTimes="0;.40;.44;.50;1" dur="7s" repeatCount="indefinite"/></rect>''', 7))
    auto_eyes = '<path d="M1035 413L1095 421L1088 479L1028 472Z M1180 430L1243 438L1235 498L1173 490Z"/>'
    # Trace the gear's own stepped outline, excluding adjacent replay arrows.
    gear = '<path d="M530 350H613V376H661V396L680 396L697 415V445L680 452H715V525L694 541V578L677 596H662V615H614V636H529V615H481V596H463L447 579V548L462 540H434L421 525V469L434 454H463L447 440V415L465 396H482V375H530Z"/>'
    cursor = '<rect x="219" y="514" width="249" height="403"/>'
    # The two original replay arrows take a small turn together, independently
    # from the faster inner gear, then settle into their original pose.
    replay_top = '<path d="M308 481V381H329V348H351V317H375V292H401V269H430V244H457V225H490V206H650V225H687V244H714V265H741V285H765L785 264H810V422L667 389L711 345L685 320H652V303H615V285H525V304H484V323H455V348H431V373H415V399H399V481Z"/>'
    replay_bottom = '<path d="M742 471H838V582H818V621H797V652H772V680H746V708H720V733H692V756H656V780H578L529 816L460 678L601 625L597 660H643V643H669V622H691V600H713V576H736V471Z"/>'
    entries.append(build('automation', {'eyes': auto_eyes, 'gear': gear, 'cursor': cursor, 'replay': replay_top + replay_bottom}, gear + cursor + replay_top + replay_bottom,
        blink(auto_eyes, 454, '3.4s') +
        '''<g><animateTransform attributeName="transform" type="rotate" values="0 570 494;0 570 494;5 570 494;5 570 494;0 570 494;0 570 494" keyTimes="0;.12;.30;.48;.65;1" dur="4s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXreplay)"/></g>
<g><animateTransform attributeName="transform" type="rotate" from="0 570 494" to="360 570 494" dur="8s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXgear)"/></g>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;8 -8;0 0;0 0" keyTimes="0;.32;.38;.44;1" dur="2s" repeatCount="indefinite"/><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcursor)"/></g>
<g fill="none" stroke="#ffbf3e" stroke-width="9" opacity="0"><path d="M245 488V463M203 510L184 491M281 501L300 482"/><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.34;.39;.52;1" dur="2s" repeatCount="indefinite"/></g>
<path d="M1182 159L1231 165L1225 209L1176 203Z" fill="#ff9b8f" opacity="0"><animate attributeName="opacity" values="0;0;.75;0;0" keyTimes="0;.42;.48;.57;1" dur="2s" repeatCount="indefinite"/></path>''', 8))
    (ROOT / 'assets' / 'c1-motion-source.json').write_text(json.dumps({'version': 3, 'generator': 'scripts/build_sprite_motion.py', 'method': 'Original PNG payload plus SVG source-part rigs; no raster edits', 'sprites': entries}, indent=2) + '\n', encoding='utf-8')
    for item in entries:
        print(f"{item['output']}: {item['width']}x{item['height']} source SHA256 {item['source_sha256']}")


if __name__ == '__main__':
    main()
