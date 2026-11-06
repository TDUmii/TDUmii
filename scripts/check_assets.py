"""Regression checks for the observed connector, motion and footer defects."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from xml.etree import ElementTree as ET
import hashlib
import base64
import json
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
data = json.loads((ROOT / 'assets/profile-data.json').read_text())
for filename, compact in [('activity.svg', False), ('calendar.svg', False), ('activity-mobile.svg', True)]:
    calendar = ET.parse(ROOT / 'assets' / filename)
    mask = calendar.find('.//svg:mask[@id="orbit-active"]', NS)
    assert mask is not None and mask.attrib['maskUnits'] == 'userSpaceOnUse'
    days = data['contributions'][-182:] if compact else data['contributions']
    assert len(mask.findall('svg:rect', NS)) == sum(day['count'] > 0 for day in days), 'Calendar glow may highlight inactive dates'
    assert calendar.find('.//svg:g[@class="orbit-motion"]', NS) is not None
    assert '@media(prefers-reduced-motion:reduce){.orbit-motion{display:none}}' in (ROOT / 'assets' / filename).read_text()
assert 'orbit-motion' not in (ROOT / 'assets/calendar-static.svg').read_text(), 'Static calendar must have no orbit sweep'
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
assert '<table' not in readme.lower(), 'The native profile must use readable full-width project rows'
approved = ['nyan-cat', 'pixel-planet', 'pixel-robot']
for variant in ['', '-mobile']:
    hero = ET.parse(ROOT / f'assets/profile-hero{variant}.svg')
    payloads = {base64.b64decode(node.attrib['href'].split(',', 1)[1]) for node in hero.findall('.//svg:image', NS) if node.attrib.get('href', '').startswith('data:image/gif;base64,')}
    assert payloads == {(ROOT / f'assets/{name}.gif').read_bytes() for name in approved}, 'Native hero changed or lost an original GIF'
for source in json.loads((ROOT / 'assets/pixel-assets-source.json').read_text()):
    path = ROOT / 'assets' / source['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], 'Downloaded GIF no longer matches its original'
    assert path.stat().st_size == source['bytes'] and source['license'] == 'CC0-1.0'
for source in json.loads((ROOT / 'assets/work-sources.json').read_text()):
    path = ROOT / 'assets' / source['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    slug = 'bridge' if source['file'] == 'work-bridge.png' else 'quietshare'
    for suffix in ['', '-mobile']:
        poster = ET.parse(ROOT / f'assets/project-row-{slug}{suffix}.svg')
        images = poster.findall('.//svg:image', NS)
        assert len(images) == 1
        assert base64.b64decode(images[0].attrib['href'].split(',', 1)[1]) == path.read_bytes(), 'Project poster changed the actual interface image'
print('PASS: 202 packet positions, active-date orbit masks, static calendar, motion fallbacks, footer sizes and versioned README assets.')
print('PASS: full-width native rows and exact original GIF payloads with recorded provenance.')
print('PASS: native desktop/mobile product posters embed the exact source interface captures.')
