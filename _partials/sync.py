#!/usr/bin/env python3
"""Synchronize version source navigation/footer without rewriting historical snapshots.

Default target is registry.working (currently the preview source). Historical
versions use their own frozen _partials, never the current global templates.
After --write, run Tools/build_versions.py to regenerate static output routes.

python3 _partials/sync.py --check [--all | --version 1.1.2]
python3 _partials/sync.py --write [--version 1.1.3]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIALS = ROOT / '_partials/kotori'
VERSIONS = ROOT / '_versions/kotori'

PAGES = {
    'index.html':           {'lang': 'ja',      'links': {'en': 'index-en.html'}},
    'features.html':        {'lang': 'ja',      'links': {'en': 'features-en.html'}},
    'privacy-ja.html':      {'lang': 'ja',      'links': {'en': 'privacy.html', 'zh': 'privacy-zh-Hant.html'}},
    'support-ja.html':      {'lang': 'ja',      'links': {'en': 'support.html'}},
    'index-en.html':        {'lang': 'en',      'links': {'ja': 'index.html'}},
    'features-en.html':     {'lang': 'en',      'links': {'ja': 'features.html'}},
    'privacy.html':         {'lang': 'en',      'links': {'ja': 'privacy-ja.html', 'zh': 'privacy-zh-Hant.html'}},
    'support.html':         {'lang': 'en',      'links': {'ja': 'support-ja.html'}},
    'privacy-zh-Hant.html': {'lang': 'zh-hant', 'links': {'ja': 'privacy-ja.html', 'en': 'privacy.html'}},
}

LANG_LABELS = [('ja', '日本語'), ('en', 'English'), ('zh', '繁體中文')]
LANG_KEY = {'ja': 'ja', 'en': 'en', 'zh-hant': 'zh'}  # PAGES.lang → LANG_LABELS のキー

def load_registry():
    return json.loads((VERSIONS / 'versions.json').read_text())


def nav_lang_span(lang: str, links: dict) -> str:
    current = LANG_KEY[lang]
    items = []
    for key, label in LANG_LABELS:
        if key == current:
            items.append(f'<strong>{label}</strong>')
        elif key in links:
            items.append(f'<a href="{links[key]}">{label}</a>')
    return '<span class="nav-lang">' + ' | '.join(items) + '</span>'


def render(block: str, page: str, version: dict, working: str) -> str:
    cfg = PAGES[page]
    templates = PARTIALS if version['version'] == working else VERSIONS / version['source'] / '_partials'
    tpl = (templates / f'{block}-{cfg["lang"]}.html').read_text()
    if block == 'nav':
        tpl = tpl.replace('__NAV_LANG__', nav_lang_span(cfg['lang'], cfg['links']))
    tpl = tpl.replace('__APP_VERSION__', version['version'])
    if '__' in tpl:
        raise ValueError(f'{version["version"]}/{page}/{block}: unresolved placeholder')
    return tpl.rstrip('\n')


def block_re(block: str) -> re.Pattern:
    return re.compile(rf'(  <!-- kotori:{block}:start -->\n)(.*?)(  <!-- kotori:{block}:end -->)', re.DOTALL)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true'); mode.add_argument('--write', action='store_true')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--version'); selection.add_argument('--all', action='store_true')
    args = parser.parse_args()
    data = load_registry()
    wanted = args.version or data['working']
    selected = data['versions'] if args.all else [v for v in data['versions'] if v['version'] == wanted]
    if not selected:
        parser.error('Unknown version: ' + wanted)
    drift = []
    for version in selected:
        source_dir = VERSIONS / version['source']
        for page in PAGES:
            path = source_dir / page
            src = path.read_text()
            for block in ('nav', 'footer'):
                match = block_re(block).search(src)
                if not match:
                    raise ValueError(f'{path}: missing {block} marker')
                expected = render(block, page, version, data['working']) + '\n'
                if match[2] != expected:
                    drift.append(f'{version["version"]}/{page}: {block}')
                    if args.write:
                        src = src[:match.start(2)] + expected + src[match.end(2):]
            if args.write and path.read_text() != src:
                path.write_text(src)
        if args.write and version['version'] == data['working']:
            for template in PARTIALS.glob('*.html'):
                target = source_dir / '_partials' / template.name
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or target.read_bytes() != template.read_bytes():
                    target.write_bytes(template.read_bytes())
    if args.check and drift:
        print('Partial drift:\n' + '\n'.join('  ' + d for d in drift)); return 1
    print(f'OK: {len(selected) * len(PAGES)} version source pages; historical templates remain isolated.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print('Partial sync failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
