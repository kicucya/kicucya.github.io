#!/usr/bin/env python3
"""Build all static Kotori version routes from _versions/kotori/versions.json.

python3 Tools/build_versions.py [--check]
No network, Git checkout, packages, or server-side routing is needed.
"""
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit
from l10n_terms import validate_copy

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / '_versions/kotori'
GENERATED = SOURCES / 'generated-files.json'
SITE = 'https://kicucya.github.io'
PAGES = {'index.html': 'ja', 'index-en.html': 'en', 'features.html': 'ja',
         'features-en.html': 'en', 'support-ja.html': 'ja', 'support.html': 'en',
         'privacy-ja.html': 'ja', 'privacy.html': 'en', 'privacy-zh-Hant.html': 'zh-hant'}
TEXT = {
 'ja': {'label': 'アプリのバージョン', 'latest': '最新', 'preview': 'プレビュー', 'history': '過去のバージョン',
        'notes': 'このバージョンの更新内容', 'restored': 'このページは 1.1.0 のサイト内容をもとに再構成しています。1.1.1 の主な修正は次のとおりです。'},
 'en': {'label': 'App version', 'latest': 'Latest', 'preview': 'Preview', 'history': 'Past version',
        'notes': 'Changes in this version', 'restored': 'This page was reconstructed from the 1.1.0 website. The main fixes in 1.1.1 are listed below.'},
 'zh-hant': {'label': 'App 版本', 'latest': '最新', 'preview': '預覽', 'history': '歷史版本',
        'notes': '此版本的更新內容', 'restored': '此頁以 1.1.0 的網站內容重建。1.1.1 的主要修正如下。'},
}


def registry():
 data = json.loads((SOURCES / 'versions.json').read_text())
 versions = data['versions']
 names = [v['version'] for v in versions]
 if len(names) != len(set(names)) or any(not re.fullmatch(r'\d+\.\d+\.\d+', v) for v in names):
  raise ValueError('Invalid or duplicate version')
 if data['latest'] not in names or data['working'] not in names:
  raise ValueError('latest/working must name a registered version')
 if next(v for v in versions if v['version'] == data['latest'])['status'] != 'released':
  raise ValueError('latest must be a released version')
 for v in versions:
  if v['source'] != 'v' + v['version'] or v['status'] not in ('released', 'preview'):
   raise ValueError('Invalid source or status: ' + v['version'])
 return data


def esc(value):
 return html.escape(str(value), quote=True)


def relative(target, route):
 return posixpath.relpath(target, route)


def anchors(version, page):
 text = (SOURCES / version['source'] / page).read_text()
 return re.findall(r'\bid=["\']([^"\']+)["\']', text)


def version_bar(data, version, page, route):
 t = TEXT[PAGES[page]]
 status = t['preview'] if version['status'] == 'preview' else t['latest'] if version['version'] == data['latest'] else t['history']
 links = []
 options = [(t['latest'] + ' · ' + data['latest'], 'kotori', next(v for v in data['versions'] if v['version'] == data['latest']))]
 options += [(v['version'] + (' · ' + t['preview'] if v['status'] == 'preview' else ''), 'kotori/v' + v['version'], v) for v in reversed(data['versions'])]
 for label, target, v in options:
  current = ' aria-current="page"' if route == target else ''
  valid = json.dumps(anchors(v, page), ensure_ascii=False, separators=(',', ':'))
  links.append(f'<li><a href="{esc(relative(target + "/" + page, route))}" data-version-link data-anchors="{esc(valid)}"{current}>{esc(label)}</a></li>')
 notes = ''
 if version.get('reconstructed_from'):
  items = ''.join('<li>' + esc(line) + '</li>' for line in version['release_notes'][PAGES[page]])
  notes = f'<details class="kotori-version-notes"><summary>{esc(t["notes"])}</summary><p>{esc(t["restored"])}</p><ul>{items}</ul></details>'
 return f'''  <!-- kotori:version:start -->
  <aside class="kotori-version-bar" aria-label="{esc(t['label'])}">
    <div class="kotori-version-inner"><span>{esc(t['label'])}</span><details class="kotori-version-menu"><summary>{esc(version['version'])} · {esc(status)}</summary><nav aria-label="{esc(t['label'])}"><ul>{''.join(links)}</ul></nav></details>{notes}</div>
  </aside>
  <!-- kotori:version:end -->'''


def render(data, version, page, route):
 source = (SOURCES / version['source'] / page).read_text()
 if 'kotori:version:start' in source:
  raise ValueError('Generated version UI must not be stored in source: ' + version['source'] + '/' + page)
 # Metadata and any absolute same-site links must resolve within this snapshot.
 source = source.replace(SITE + '/kotori/', SITE + '/' + route + '/')
 source = re.sub(r'(["\'])assets/guides/', lambda m: m[1] + relative('kotori/assets/guides', route) + '/', source)
 source = source.replace('</head>', '  <link rel="stylesheet" href="assets/version-ui.css">\n  <script src="assets/version-ui.js" defer></script>\n</head>')
 marker = '  <!-- kotori:nav:end -->'
 if source.count(marker) != 1:
  raise ValueError('Missing unique navigation marker: ' + page)
 source = source.replace(marker, marker + '\n\n' + version_bar(data, version, page, route), 1)
 validate_copy(source, PAGES[page], version['source'] + '/' + page)
 return source.encode()


def expected_files(data):
 expected = {}
 latest = next(v for v in data['versions'] if v['version'] == data['latest'])
 routes = [('kotori', latest), ('kotori/main', latest)] + [('kotori/v' + v['version'], v) for v in data['versions']]
 for route, version in routes:
  source = SOURCES / version['source']
  found = {p.name for p in source.glob('*.html')}
  if found != set(PAGES):
   raise ValueError(f'{version["version"]}: expected all nine complete pages, found {sorted(found)}')
  for page in PAGES:
   expected[route + '/' + page] = render(data, version, page, route)
  for asset in (source / 'assets').rglob('*'):
   if asset.is_file():
    rel = asset.relative_to(source).as_posix()
    if rel.startswith('assets/guides/'):
     raise ValueError('Public guide media must be shared, not copied into source snapshots')
    expected[route + '/' + rel] = asset.read_bytes()
  for name in ('version-ui.css', 'version-ui.js'):
   expected[route + '/assets/' + name] = (SOURCES / name).read_bytes()
 return expected


class Links(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids = []; self.refs = []
 def handle_starttag(self, tag, attrs):
  attrs = dict(attrs)
  if 'id' in attrs: self.ids.append(attrs['id'])
  for key in ('href', 'src', 'data-src', 'data-poster', 'poster'):
   if attrs.get(key): self.refs.append(attrs[key])


def validate(expected):
 docs = {}
 for name, content in expected.items():
  if name.endswith('.html'):
   doc = Links(); doc.feed(content.decode()); docs[name] = doc
   if len(doc.ids) != len(set(doc.ids)): raise ValueError('Duplicate HTML id: ' + name)
 count = 0
 for name, content in expected.items():
  refs = docs[name].refs if name in docs else re.findall(r'url\(["\']?([^\)"\']+)', content.decode()) if name.endswith('.css') else []
  for ref in refs:
   url = urlsplit(ref)
   if url.scheme or url.netloc:
    if url.netloc != 'kicucya.github.io': continue
    path = unquote(url.path).lstrip('/')
   elif url.path.startswith('/'):
    path = unquote(url.path).lstrip('/')
   else:
    path = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(url.path))) if url.path else name
   if path.endswith('/'): path += 'index.html'
   if path not in expected:
    # A stale generated asset must never hide a missing source snapshot.
    shared_media = path.startswith('kotori/assets/guides/')
    outside_site = not path.startswith('kotori/')
    if not (shared_media or outside_site) or not (ROOT / path).is_file():
     raise ValueError(f'Missing local target: {name} -> {ref}')
   if url.fragment and path in docs and unquote(url.fragment) not in docs[path].ids:
    raise ValueError(f'Missing anchor: {name} -> {ref}')
   count += 1
 return len(docs), count


def previous_outputs():
 if not GENERATED.exists(): return set()
 names = json.loads(GENERATED.read_text())
 if not isinstance(names, list): raise ValueError('Invalid generated file registry')
 for name in names:
  if not isinstance(name, str) or not name.startswith('kotori/') or '..' in name.split('/') or name.startswith('kotori/assets/guides/'):
   raise ValueError('Unsafe generated file registry entry')
 return set(names)


def main():
 parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true');args = parser.parse_args()
 try:
  data = registry(); expected = expected_files(data); pages, refs = validate(expected)
  previous = previous_outputs()
  obsolete = sorted(previous - set(expected))
  file_registry = (json.dumps(sorted(expected), indent=2) + '\n').encode()
  registry_changed = not GENERATED.is_file() or GENERATED.read_bytes() != file_registry
  drift = [name for name, contents in expected.items() if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != contents]
  if args.check:
   if drift or obsolete or registry_changed:
    print('Generated version drift:\n' + '\n'.join('  ' + name for name in drift + obsolete) + ('\n  generated file registry' if registry_changed else ''), file=sys.stderr);return 1
  else:
   for name in drift:
    path = ROOT / name;path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(expected[name])
   # Only previously registered generated files are eligible for removal.
   for name in obsolete:
    path = ROOT / name
    if path.is_file() or path.is_symlink(): path.unlink()
   if registry_changed: GENERATED.write_bytes(file_registry)
  print(f'OK: {pages} pages, {refs} local references; latest={data["latest"]}; ' + ('generated files match.' if args.check else f'{len(drift)} files updated.'))
  return 0
 except (OSError, ValueError, KeyError, TypeError) as error:
  print('Version build failed: ' + str(error), file=sys.stderr);return 1

if __name__ == '__main__':
 sys.exit(main())
