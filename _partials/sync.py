#!/usr/bin/env python3
"""sync.py — kotori 各ページのヘッダー/フッターを真相源(_partials/kotori/)から同期する。

ページ側は <!-- kotori:nav:start --> … <!-- kotori:nav:end --> と
<!-- kotori:footer:start --> … <!-- kotori:footer:end --> のマーカーで区块を持ち、
区块の中身は「展開済みの完全な HTML」——ローカルで file:// 直開きしても、
GitHub Pages(純静的配信)でも、ビルドなしでそのまま正しく表示される。

使い方(リポジトリ内どこからでも):
  python3 _partials/sync.py --check   # 各ページの区块が真相源と一致するか検査(不一致は exit 1)
  python3 _partials/sync.py --write   # 真相源から各ページの区块を書き直して同期

ヘッダー/フッターを変えるときは _partials/kotori/ 側を編集して --write を実行する。
ページ側の区块を直接編集しても --check が漂移を検出し、--write で真相源に戻される。
依存なし(標準ライブラリのみ)。

サイトの記載が対応するアプリのバージョンは下の APP_VERSION が唯一の真相源。
アプリのリリースごとにここだけ書き換えて --write を実行すれば全ページのフッターが揃う。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # リポジトリルート
PARTIALS = Path(__file__).resolve().parent / 'kotori'
KOTORI = ROOT / 'kotori'

# このサイトの記載が対応するアプリのバージョン(フッターの __APP_VERSION__ に埋め込まれる)。
# アプリのリリースに合わせて更新する箇所はここ一か所だけ。
APP_VERSION = '1.1.0'

# 各ページの言語と「同じ内容の他言語版」へのリンク先(言語切替行の生成に使う)。
# 現在の言語は <strong>、他言語はリンク。存在する言語だけ並ぶ(順序は ja → en → zh 固定)。
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


def nav_lang_span(lang: str, links: dict) -> str:
    """言語切替行(<span class="nav-lang">…</span>)を生成する。"""
    current = LANG_KEY[lang]
    items = []
    for key, label in LANG_LABELS:
        if key == current:
            items.append(f'<strong>{label}</strong>')
        elif key in links:
            items.append(f'<a href="{links[key]}">{label}</a>')
    return '<span class="nav-lang">' + ' | '.join(items) + '</span>'


def render(block: str, page: str) -> str:
    """ページの指定区块(nav/footer)の期待 HTML を返す(末尾改行なし)。"""
    cfg = PAGES[page]
    tpl = (PARTIALS / f'{block}-{cfg["lang"]}.html').read_text(encoding='utf-8')
    if block == 'nav':
        tpl = tpl.replace('__NAV_LANG__', nav_lang_span(cfg['lang'], cfg['links']))
    tpl = tpl.replace('__APP_VERSION__', APP_VERSION)
    assert '__' not in tpl, f'{page}/{block}: unresolved placeholder'
    return tpl.rstrip('\n')


def block_re(block: str) -> re.Pattern:
    return re.compile(
        rf'(  <!-- kotori:{block}:start -->\n)(.*?)(  <!-- kotori:{block}:end -->)',
        re.DOTALL,
    )


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in ('--check', '--write'):
        print(__doc__)
        return 2
    drift = []
    for page in PAGES:
        path = KOTORI / page
        src = path.read_text(encoding='utf-8')
        for block in ('nav', 'footer'):
            m = block_re(block).search(src)
            if not m:
                drift.append(f'{page}: {block} マーカーが見つからない')
                continue
            expected = render(block, page) + '\n'
            if m.group(2) != expected:
                drift.append(f'{page}: {block} 区块が真相源と不一致')
                if mode == '--write':
                    src = src[:m.start(2)] + expected + src[m.end(2):]
        if mode == '--write':
            path.write_text(src, encoding='utf-8')
    if mode == '--check':
        if drift:
            print('漂移を検出:')
            for d in drift:
                print(f'  - {d}')
            return 1
        print(f'OK: {len(PAGES)} ページの nav/footer は真相源と一致')
        return 0
    # --write
    if drift:
        print('同期(書き直し)した区块:')
        for d in drift:
            print(f'  - {d}')
    else:
        print('全ページ既に一致(書き換えなし)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
