"""Build one private HTML file from the same finished profile page."""
from pathlib import Path
import base64
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
MIME = {'gif': 'image/gif', 'png': 'image/png', 'svg': 'image/svg+xml', 'woff2': 'font/woff2'}
assets = {}
html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'styles.css').read_text(encoding='utf-8')
script = (ROOT / 'profile.js').read_text(encoding='utf-8')
# Package only assets used by the website; native README SVGs already embed art.
used = set(re.findall(r'assets/[A-Za-z0-9_.-]+', html + css + script))
for name in sorted(used):
    path = ROOT / name
    ext = path.suffix.removeprefix('.')
    if ext in MIME:
        assets['assets/' + path.name] = 'data:' + MIME[ext] + ';base64,' + base64.b64encode(path.read_bytes()).decode()
def version_asset(match):
    attr, name = match[1], match[2]
    path = ROOT / name
    if not path.is_file():
        return match[0]
    version = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    return attr + '="' + name + '?v=' + version + '"'
html = re.sub(r'(src|srcset|href)="((?:assets/[^"?]+|styles\.css|profile\.js))(?:\?[^"\s]*)?"', version_asset, html)
(ROOT / 'index.html').write_text(html, encoding='utf-8')
css = re.sub(r"url\('([^']+)'\)", lambda match: "url('" + assets.get(match[1], match[1]) + "')", css)
html = re.sub(r'<link rel="stylesheet" href="styles\.css(?:\?[^"]*)?">', lambda match: '<style>' + css + '</style>', html)
html = re.sub(r'(src|srcset|href)="(assets/[^"? ]+)(?:\?[^" ]*)?"', lambda match: match[1] + '="' + assets.get(match[2], match[2]) + '"', html)
data = (ROOT / 'assets/profile-data.js').read_text(encoding='utf-8')
html = re.sub(r'<script src="assets/profile-data\.js(?:\?[^"]*)?"></script>', lambda match: '<script>' + data + '</script>', html)
# Dynamic paths in data-live-src/data-still-src are embedded above too.
# Avoid duplicating every large sprite in a second JSON asset dictionary.
code = script
html = re.sub(r'<script src="profile\.js(?:\?[^"]*)?"></script>', lambda match: '<script>' + code + '</script>', html)
out = ROOT / 'output'
out.mkdir(exist_ok=True)
(out / 'Umi-Profile.html').write_text(html, encoding='utf-8')
print('Standalone profile built with the original animated GIF and real public activity.')
