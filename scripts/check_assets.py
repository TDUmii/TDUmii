"""Check the shipped C1 profile: real data, original media and native links."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from xml.etree import ElementTree as ET
import base64
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = {'svg': 'http://www.w3.org/2000/svg'}
XLINK = '{http://www.w3.org/1999/xlink}href'
def image_href(node):
    return node.attrib.get('href', node.attrib.get(XLINK, ''))
data = json.loads((ASSETS / 'profile-data.json').read_text(encoding='utf-8'))
assert sum(day['count'] for day in data['contributions']) == data['contribution_total']
assert sum(day['count'] > 0 for day in data['contributions']) == data['active_days']

readme = (ROOT / 'README.md').read_text(encoding='utf-8')
assert readme.count('<picture>') == 11
for repo in ['umi-bridge', 'QuietShare', 'BackgroundAutomationStudio']:
    assert readme.count('href="https://github.com/TDUmii/' + repo + '"') == 1
assert 'aoe' not in readme.lower()
roots = {}
for ref in re.findall(r'(?:src|srcset)="([^"]+)"', readme):
    url = urlsplit(ref)
    assert url.netloc == 'raw.githubusercontent.com', 'Redirect would discard the cache version'
    path = ASSETS / url.path.rsplit('/', 1)[1]
    assert path.is_file()
    assert parse_qs(url.query)['v'][0] == hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    roots[path.name] = ET.parse(path)
    assert chr(194) + chr(183) not in path.read_text(encoding='utf-8'), 'Broken text encoding in native art'
    for image in roots[path.name].findall('.//svg:image', NS):
        assert image_href(image).startswith('data:image/'), 'Native art must be self-contained'

for name, compact in [('activity.svg', False), ('calendar.svg', False), ('activity-mobile.svg', True)]:
    tree = ET.parse(ASSETS / name)
    mask = tree.find('.//svg:mask[@id="orbit-active"]', NS)
    assert mask is not None and mask.attrib['maskUnits'] == 'userSpaceOnUse'
    days = data['contributions'][-182:] if compact else data['contributions']
    assert len(mask.findall('svg:rect', NS)) == sum(day['count'] > 0 for day in days), 'Orbit highlights inactive dates'
    assert tree.find('.//svg:g[@class="orbit-motion"]', NS) is not None
    assert '@media(prefers-reduced-motion:reduce){.orbit-motion{display:none}}' in (ASSETS / name).read_text()
assert 'orbit-motion' not in (ASSETS / 'calendar-static.svg').read_text()

all_gifs = set()
for name, tree in roots.items():
    for image in tree.findall('.//svg:image', NS):
        href = image_href(image)
        if href.startswith('data:image/gif;base64,'):
            all_gifs.add(base64.b64decode(href.split(',', 1)[1]))
            assert image.attrib['preserveAspectRatio'] == 'xMidYMid meet'
    if name.startswith('profile-hero'):
        source = (ASSETS / name).read_text(encoding='utf-8')
        assert 'class="nyan-live"' in source and 'class="nyan-still"' in source
        assert '.moving,.nyan-live{display:none}.nyan-still{display:inline}' in source
expected = {(ASSETS / (name + '.gif')).read_bytes() for name in ['nyan-cat', 'pixel-planet', 'pixel-robot', 'pixel-flame']}
assert all_gifs == expected, 'Native GIFs no longer match the original downloads'
meta = json.loads((ASSETS / 'nyan-cat-source.json').read_text(encoding='utf-8'))
assert hashlib.sha256((ASSETS / 'nyan-cat.gif').read_bytes()).hexdigest() == meta['sha256']
for source in json.loads((ASSETS / 'pixel-assets-source.json').read_text()):
    path = ASSETS / source['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    assert path.stat().st_size == source['bytes'] and source['license'] == 'CC0-1.0'
for source in json.loads((ASSETS / 'c1-art-source.json').read_text()):
    path = ASSETS / source['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    slug = {'c1-bridge-art.png': 'bridge', 'c1-quiet-art.png': 'quietshare', 'c1-automation-art.png': 'automation'}[source['file']]
    for suffix in ['', '-mobile']:
        tree = roots['project-row-' + slug + suffix + '.svg']
        images = tree.findall('.//svg:image', NS)
        assert len(images) == 1
        assert base64.b64decode(image_href(images[0]).split(',', 1)[1]) == path.read_bytes(), 'Native art payload differs from its approved illustration'
for name in ['footer-lab', 'footer-code']:
    for suffix, width in [('', 414.5), ('-mobile', 150.9)]:
        root = roots[name + suffix + '.svg'].getroot()
        height = width * float(root.attrib['height']) / float(root.attrib['width'])
        assert 44 <= height <= 60, 'Native footer control is too small or oversized'
print('PASS: real dated totals, active-date orbit masks, static calendar and reduced-motion fallbacks.')
print('PASS: three independent native project links, exact original GIFs/illustrations and versioned self-contained SVGs.')
print('PASS: native footer action dimensions and original download provenance.')

motion = json.loads((ASSETS / 'c1-motion-source.json').read_text())
for sprite in motion['sprites']:
    source = ASSETS / sprite['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == sprite['source_sha256']
    path = ASSETS / sprite['output']
    tree = ET.parse(path)
    images = tree.findall('.//svg:image', NS)
    assert len(images) == 1, 'A rig must embed the original art only once'
    assert base64.b64decode(image_href(images[0]).split(',', 1)[1]) == source.read_bytes()
    assert tree.find('.//svg:g[@class="sprite-motion"]', NS) is not None
    assert tree.find('.//svg:use[@class="sprite-still"]', NS) is not None
    assert tree.findall('.//svg:animateTransform', NS) or tree.findall('.//svg:animate', NS), 'Missing internal sprite motion'
    assert 'prefers-reduced-motion:reduce' in path.read_text(encoding='utf-8')
print('PASS: three internal sprite rigs, unchanged PNG payloads and native reduced-motion stills.')
