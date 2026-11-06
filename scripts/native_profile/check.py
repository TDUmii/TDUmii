"""Run without writing assets: python scripts/native_profile/check.py."""
import base64
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_profile import activity, details
from native_profile.core import ASSETS, shell


def check():
    outputs = {}
    def capture(name, w, h, body, title):
        outputs[name] = ET.fromstring(shell(w, h, body, title))
    data = json.loads((ASSETS / 'profile-data.json').read_text())
    with patch.object(activity, 'write', capture), patch.object(details, 'write', capture):
        activity.render(data)
        details.render(data)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    original = (ASSETS / 'pixel-flame.gif').read_bytes()
    for name in ('activity.svg', 'activity-mobile.svg'):
        tree = outputs[name]
        flame = next(node for node in tree.findall('.//s:image', ns)
                     if node.get('href', '').startswith('data:image/gif;'))
        assert base64.b64decode(flame.get('href').split(',', 1)[1]) == original
        assert float(flame.get('width')) / float(flame.get('height')) == 15 / 20
        assert float(flame.get('y')) + float(flame.get('height')) < 90
        expected = data['contributions'] if name == 'activity.svg' else data['contributions'][-182:]
        mask = tree.find('.//s:mask', ns)
        assert len(mask) == sum(day['count'] > 0 for day in expected)
        assert sum(1 for node in tree.findall('.//s:rect', ns) if node.find('s:title', ns) is not None) == len(expected)
        copy = ' '.join(node.text or '' for node in tree.findall('.//s:text', ns))
        for key in ('contribution_total', 'active_days', 'recent_contributions', 'best_day', 'date_label'):
            assert str(data[key]) in copy
    assert len(outputs) == 12
    print('PASS: 12 SVGs parse; calendar dates and active-cell masks match data; header flame bytes and ratio preserved; real totals remain visible.')


if __name__ == '__main__':
    check()
