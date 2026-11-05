"""Regression checks for the observed connector, motion and footer defects."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from xml.etree import ElementTree as ET
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}
bridge = ET.parse(ROOT / 'assets/project-bridge.svg')
nodes = [(29, 150, 115, 57), (196, 143, 133, 70), (382, 150, 88, 57)]
packet_count = 0
for packet in bridge.findall('.//svg:circle', NS):
    motion = packet.find('svg:animateMotion', NS)
    if motion is None:
        continue
    match = re.fullmatch(r'M([\d.]+) ([\d.]+)H([\d.]+)', motion.attrib['path'])
    assert match, 'Packet regression check expects a horizontal connector path'
    start, y, end = map(float, match.groups())
    radius = float(packet.attrib['r'])
    for n in range(101):
        x = start + (end - start) * n / 100
        assert not any(x + radius > nx and x - radius < nx + w and y + radius > ny and y - radius < ny + h for nx, ny, w, h in nodes), 'Animated packet crosses a node'
    packet_count += 1
assert packet_count == 2
for variant in ['', '-mobile']:
    source = (ROOT / f'assets/profile-hero{variant}.svg').read_text(encoding='utf-8')
    assert 'class="nyan-live"' in source and 'class="nyan-still"' in source
    assert '.moving,.nyan-live{display:none}.nyan-still{display:inline}' in source
for name in ['footer-lab', 'footer-code']:
    for suffix, rendered_width in [('', 414.5), ('-mobile', 150.9)]:
        image = ET.parse(ROOT / f'assets/{name}{suffix}.svg').getroot()
        rendered_height = rendered_width * float(image.attrib['height']) / float(image.attrib['width'])
        assert 44 <= rendered_height <= 56, 'Footer action is undersized or oversized'
readme = (ROOT / 'README.md').read_text(encoding='utf-8')
for ref in re.findall(r'(?:src|srcset)="([^"]+)"', readme):
    url = urlsplit(ref)
    assert url.netloc == 'raw.githubusercontent.com', 'Redirect would discard the cache version'
    path = ROOT / 'assets' / url.path.rsplit('/', 1)[1]
    assert path.is_file()
    assert parse_qs(url.query)['v'][0] == hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    ET.parse(path)
assert 'aoe' not in readme.lower()
print('PASS: 202 packet positions, two motion fallbacks, four footer sizes, and all versioned README assets.')
