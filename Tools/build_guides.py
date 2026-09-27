#!/usr/bin/env python3
"""Build Japanese/English guide cards from versioned real recordings.

Run from any directory: python3 Tools/build_guides.py [--check]
Media manifests live at kotori/assets/guides/<version>/{ja,en}/manifest.json.
Only complete MP4/poster/JA+EN caption sets can produce a playable card.
"""
import argparse
import html
import hashlib
import json
from pathlib import Path
import re
import sys
from l10n_terms import validate_copy

ROOT = Path(__file__).resolve().parent.parent
MEDIA_ROOT = ROOT / 'kotori/assets/guides/1.1.3'
REGISTRY = ROOT / '_versions/kotori/versions.json'
MARKER = re.compile(r'(    <!-- guide-library:start -->\n).*?(    <!-- guide-library:end -->)', re.S)
GROUPS = {
    'control-center': ('コントロールセンター', 'Control Center', 'ひとことで記録。未確認の件数も、ここから。', 'Record a quick entry and check your pending count.'),
    'record': ('記録する', 'Record', '一言入力から、内容の確認まで。', 'From your first entry to checking its details.'),
    'organize': ('整理・修正する', 'Organize & edit', '収支、カテゴリ、財布を使いやすく。', 'Keep transactions, categories, and wallets in order.'),
    'review': ('振り返る・予定を立てる', 'Review & plan', 'レポート、予算、固定費・定期収入。', 'Reports, budgets, and recurring expenses or income.'),
    'data': ('データ・設定', 'Data & settings', '取り込み、書き出し、日々の設定。', 'Import, export, and everyday preferences.'),
}
TEXT = {
    'ja': {'heading': 'やりたいことから探す', 'intro': '動画を選ぶと、操作の手順が開きます。自分のペースで再生・一時停止できます。',
           'search': '操作を検索', 'placeholder': '例：カテゴリ、予算、取り込み', 'clear': '検索をクリア', 'count': '本の操作動画',
           'play': '動画を再生', 'steps': '操作の手順', 'download': '動画ファイルを開く', 'empty': '該当する操作が見つかりません。別の言葉で検索してください。',
           'caption': 'アプリ {app_version}・日本語の画面／日本語・英語字幕', 'error': '動画を読み込めませんでした。下のリンクから動画を開けます。'},
    'en': {'heading': 'Find what you want to do', 'intro': 'Choose a video to see the steps. Play and pause whenever you need.',
           'search': 'Find a guide', 'placeholder': 'Try categories, budget, or import', 'clear': 'Clear search', 'count': 'how-to videos',
           'play': 'Play video', 'steps': 'Step by step', 'download': 'Open video file', 'empty': 'No matching guides. Try another word.',
           'caption': 'App {app_version} · Japanese interface · Japanese and English captions', 'error': 'The video could not load. Use the link below to open it.'},
}
SCOPE_NOTES = {
    '09-keywords': {
        'ja': '広告を読み込めない場合の案内を含みます。広告の再生は、この動画には含まれていません。',
        'en': 'This video includes the notice shown when an ad cannot load. It does not demonstrate ad playback.',
    },
    '15-export': {
        'ja': '動画では、ファイルを作成して共有・保存先を選ぶ画面まで進みます。保存先を選んで保存を完了する操作は含みません。',
        'en': 'This video creates the files and opens the share sheet. It stops before choosing a destination and saving a file there.',
    },
    '16-settings-and-shortcuts': {
        'ja': 'ショートカットの案内画面までを紹介します。Siri の実行は、お使いの iPhone で設定してお試しください。',
        'en': 'This video opens the shortcut setup guide. Set up and try Siri on your own iPhone.',
    },
    '17-voice-and-sharing-entry': {
        'ja': '音声入力への切り替えと、財布を共有する前の設定を紹介します。音声の認識結果や共有の完了は、この動画では実演していません。',
        'en': 'This video shows how to open voice input and the settings before sharing a wallet. It does not demonstrate speech recognition or a completed share.',
    },
    '20-shortcuts-siri-name': {
        'ja': '自分用のショートカットを作り、Siriに呼びかけやすい短い名前を付ける設定を紹介します。Siriからの実行や、マイクを使った音声認識は、この動画には含まれていません。',
        'en': 'This recording shows creating a personal shortcut and giving it a short name for Siri. It does not demonstrate running it with Siri or microphone-based speech recognition.',
    },
}

# Videos begin after navigation; keep the way to reach each screen explicit.
ENTRY_POINTS = {
    '01-quick-entry': ('記録', 'Record'),
    '02-manual-entry': ('記録 → ＋', 'Record → +'),
    '03-pending-confirmation': ('記録', 'Record'),
    '04-transaction-actions': ('収支／復元は「その他 → 最近削除した取引」', 'Transactions / restore from More → Recently Deleted'),
    '05-category-editor': ('その他 → カテゴリ管理', 'More → Categories'),
    '06-category-order': ('その他 → カテゴリ管理', 'More → Categories'),
    '07-wallets': ('その他 → 財布', 'More → Wallets'),
    '08-transfers': ('その他 → 財布 → 振替', 'More → Wallets → Transfer'),
    '09-keywords': ('その他 → キーワード管理', 'More → Keyword Management'),
    '10-reports': ('レポート', 'Reports'),
    '11-budget': ('その他 → 予算管理', 'More → Budget'),
    '12-recurring': ('その他 → 固定費・定期収入', 'More → Recurring'),
    '13-import-and-undo': ('その他 → データを読み込む', 'More → Import Data'),
    '14-batch-input': ('その他 → 一括入力', 'More → Batch Entry'),
    '15-export': ('その他 → データを書き出す', 'More → Export Data'),
    '16-settings-and-shortcuts': ('その他', 'More'),
    '17-voice-and-sharing-entry': ('音声入力は「記録」／共有は「その他 → 財布」', 'Voice input: Record / sharing: More → Wallets'),
}
# The original 17 recordings stay mandatory and in their original order.
REQUIRED_RECORDING_IDS = tuple(ENTRY_POINTS)
ENTRY_POINTS.update({
    '19-shortcuts-home-screen': ('Kotori → その他 → 記録を追加 / Siri', 'Kotori → More → Record Entry / Siri'),
    '20-shortcuts-siri-name': ('Kotori → その他 → 記録を追加 / Siri', 'Kotori → More → Record Entry / Siri'),
})
PROVENANCE_FIELDS = ('app_version', 'app_build', 'source_commit', 'runtime')
LEGACY_RECORDING_IDS = tuple(ENTRY_POINTS)
ENTRY_POINTS['25-appearance'] = ('その他 → カスタマイズ', 'More → Appearance')
ENTRY_POINTS['26-bookkeeping-reminders'] = ('その他 → 記録リマインダー', 'More → Reminders')
SCOPE_NOTES['26-bookkeeping-reminders'] = {
    'ja': '時刻と曜日はiCloudで同期できます。通知のオン・オフは端末ごとに保存され、新しいリマインダーはオフで追加されます。この動画では設定操作を紹介します。',
    'en': 'Times and weekdays can sync with iCloud. Notification switches stay on each device, and new reminders start off. This video demonstrates the settings.'
}
ENTRY_POINTS['21-chat-recurring'] = ('記録', 'Record')
ENTRY_POINTS['22-exchange-rates'] = ('レポート → 為替レート', 'Reports → Exchange Rate')
ENTRY_POINTS['24-control-center-record'] = ('iPhoneのコントロールセンター → コントロールを追加 → ショートカットを実行', 'iPhone Control Center → Add a Control → Run Shortcut')
SCOPE_NOTES['24-control-center-record'] = {
    'ja': '「ショートカットを実行」で、ことりの「記録を追加」を選びます。次回からはこのボタンで入力し、アプリを開かずに保存できます。',
    'en': 'In Run Shortcut, choose Kotori’s Record Entry action. Next time, tap this button to enter and save a record without opening the app.',
}
ENTRY_POINTS['23-control-center-pending'] = ('iPhoneのコントロールセンター', 'iPhone Control Center')


def esc(value):
    return html.escape(str(value), quote=True)


def group_for(clip):
    if clip.get('group') in GROUPS:
        return clip['group']
    identity = clip['id'].lower()
    # Precise slugs can override this without changing the public manifest schema.
    if any(word in identity for word in ('import', 'export', 'backup', 'restore-backup', 'setting', 'preference', 'currency', 'language', 'icloud', 'sync', 'reminder', 'appearance')):
        return 'data'
    if any(word in identity for word in ('report', 'budget', 'recurring')):
        return 'review'
    if any(word in identity for word in ('categor', 'wallet', 'transfer', 'keyword', 'transaction', 'swipe', 'restore', 'delete')):
        return 'organize'
    return 'record'


def duration_label(seconds):
    total = max(1, int(round(float(seconds))))
    return f'{total // 60}:{total % 60:02d}'


def read_clips(ui_language, media_version='1.1.3'):
    media = (MEDIA_ROOT if media_version == '1.1.3' else MEDIA_ROOT.parent / media_version) / ui_language
    manifest_path = media / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('app_version') != media_version or manifest.get('ui_language') != ui_language:
        raise ValueError(f'Expected app_version={media_version} and ui_language={ui_language}')
    expected_ids = list(LEGACY_RECORDING_IDS) if media_version == '1.1.3' else ['21-chat-recurring', '22-exchange-rates', '23-control-center-pending', '24-control-center-record', '25-appearance', '26-bookkeeping-reminders', '19-shortcuts-home-screen']
    minimum_count = len(REQUIRED_RECORDING_IDS) if media_version == '1.1.3' else 2
    recording_ids = [clip['id'] for clip in manifest['clips']]
    expected_present = [identity for identity in expected_ids if identity in recording_ids]
    valid_order = (recording_ids == expected_ids[:len(recording_ids)] if media_version == '1.1.3'
                   else recording_ids[:2] == expected_ids[:2] and recording_ids == expected_present)
    if not minimum_count <= len(recording_ids) <= len(expected_ids) or not valid_order:
        raise ValueError(f'{ui_language}/{media_version}: incomplete or unexpected recording order')
    ids = set()
    clips = []
    for clip in manifest['clips']:
        slug = clip['id']
        # Original JA manifests predate per-clip language metadata. Keep them
        # valid, but never relabel an explicitly different UI language.
        if 'ui_language' in clip and clip['ui_language'] != ui_language:
            raise ValueError(f'{slug}: clip UI language does not match {ui_language}')
        provenance = {key: clip.get(key, manifest.get(key)) for key in PROVENANCE_FIELDS}
        for key in PROVENANCE_FIELDS:
            if key in clip and (not isinstance(clip[key], (str, int)) or isinstance(clip[key], bool)
                                or not str(clip[key]).strip()):
                raise ValueError(f'{slug}: invalid recording {key}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in ids:
            raise ValueError(f'Invalid or duplicate clip id: {slug}')
        ids.add(slug)
        required = [media / f'{slug}{suffix}' for suffix in ('.mp4', '.jpg', '.ja.vtt', '.en.vtt')]
        if any(not p.is_file() or p.stat().st_size == 0 for p in required):
            raise ValueError(f'Incomplete media set: {slug}')
        if not clip.get('title_ja') or not clip.get('title_en') or not clip.get('steps'):
            raise ValueError(f'Missing title or steps: {slug}')
        if float(clip['duration']) <= 0 or int(clip['bytes']) != required[0].stat().st_size:
            raise ValueError(f'Invalid duration or stale video byte count: {slug}')
        validate_copy(clip['title_ja'], 'ja', f'{ui_language}/{slug}: title_ja')
        previous = -1
        for step in clip['steps']:
            if not step.get('ja') or not step.get('en'):
                raise ValueError(f'Missing step translation: {slug}')
            validate_copy(step['ja'], 'ja', f'{ui_language}/{slug}: step')
            time = float(step['time'])
            if not 0 <= time <= float(clip['duration']) or time < previous:
                raise ValueError(f'Invalid step time: {slug}')
            previous = time
        for path in required[2:]:
            validate_copy(path.read_text(), 'ja' if path.name.endswith('.ja.vtt') else 'en', str(path))
            if not path.read_text().lstrip('\ufeff').startswith('WEBVTT'):
                raise ValueError(f'Invalid caption header: {path.name}')
        # Re-recordings keep their filenames; content-derived URLs invalidate
        # each changed asset without evicting unchanged videos or captions.
        media_urls = {path.name[len(slug):]:
                      f'assets/guides/{media_version}/{ui_language}/{path.name}?v={hashlib.sha256(path.read_bytes()).hexdigest()[:12]}'
                      for path in required}
        clips.append({**clip, '_ui_language': ui_language, '_provenance': provenance,
                      '_media_urls': media_urls})
    return clips


def check_matching_provenance(japanese, english):
    if [clip['id'] for clip in japanese] != [clip['id'] for clip in english]:
        raise ValueError('Japanese and English recording IDs must match')
    # Legacy metadata may omit build provenance. When both recordings declare
    # it, each translated guide must describe the same app version/build/source.
    # Runtime can differ because it describes the device used for each take.
    for ja_clip, en_clip in zip(japanese, english):
        for key in ('app_version', 'app_build', 'source_commit'):
            values = [clip['_provenance'][key] for clip in (ja_clip, en_clip)]
            if all(value is not None and value != '' for value in values):
                if str(values[0]) != str(values[1]):
                    raise ValueError(f'{ja_clip["id"]}: Japanese and English recording {key} must match')


def card(clip, lang):
    t = TEXT[lang]
    slug = clip['id']
    title = clip[f'title_{lang}']
    ui_language = clip['_ui_language']
    media_urls = clip['_media_urls']
    app_version = clip['_provenance']['app_version']
    caption = t['caption'].format(app_version=app_version)
    if ui_language == 'en':
        caption = (f'アプリ {app_version}・英語の画面／日本語・英語字幕' if lang == 'ja'
                   else f'App {app_version} · English interface · Japanese and English captions')
    entry = ENTRY_POINTS[slug][0 if lang == 'ja' else 1]
    entry_label = '開く場所' if lang == 'ja' else 'Where to start'
    search = ' '.join([title, entry] + [s[lang] for s in clip['steps']])
    steps = ''.join(f'<li><span>{esc(s[lang])}</span></li>' for s in clip['steps'])
    scope_note = (f'<p class="guide-scope-note">{esc(SCOPE_NOTES[slug][lang])}</p>'
                  if slug in SCOPE_NOTES else '')
    # Explain visible 1.1.3 limitations beside the affected English recording.
    english_ui_notes = {
        '13-import-and-undo': 'This build shows preset category names in Japanese in the import menu. The video maps Food to 食費 (Food).',
        '14-batch-input': 'In this build, use single-entry recording for amounts with cents. Opening the batch preview editor can also change an amount, so check and correct it before importing. This video shows that correction using whole-dollar amounts.',
    }
    if ui_language == 'en' and lang == 'en' and slug in english_ui_notes:
        scope_note += f'<p class="guide-scope-note">{esc(english_ui_notes[slug])}</p>'
    seconds = int(round(float(clip['duration'])))
    duration_a11y = f'動画の長さ {seconds} 秒' if lang == 'ja' else f'Video duration: {seconds} seconds'
    tracks = ''.join(
        f'<track kind="captions" data-src="{esc(media_urls[f".{code}.vtt"])}" srclang="{code}" label="{label}"' + (' default' if code == lang else '') + '>'
        for code, label in [('ja', '日本語'), ('en', 'English')])
    return f'''          <details class="guide-card" id="guide-{slug}" data-guide-card data-search="{esc(search)}">
            <summary><span class="guide-card-title">{esc(title)}</span><span class="guide-duration"><span aria-hidden="true">{duration_label(clip['duration'])}</span><span class="guide-sr-only">{duration_a11y}</span></span><span class="guide-chevron" aria-hidden="true"></span></summary>
            <div class="guide-card-body">
              <div class="guide-media">
                <button class="guide-play" type="button" data-guide-play disabled aria-label="{esc(t['play'] + ': ' + title)}">
                  <img src="{esc(media_urls['.jpg'])}" width="450" height="978" loading="lazy" decoding="async" alt="">
                  <span class="guide-play-label"><span aria-hidden="true">▶</span> {t['play']}</span>
                </button>
                <video hidden controls playsinline preload="none" tabindex="0" data-guide-video data-poster="{esc(media_urls['.jpg'])}" aria-label="{esc(title)}">
                  <source data-src="{esc(media_urls['.mp4'])}" type="video/mp4">
                  {tracks}
                </video>
                <p class="guide-video-error" hidden>{t['error']}</p>
                <p class="guide-media-note">{esc(caption)}</p>
                <a class="guide-download" href="{esc(media_urls['.mp4'])}">{t['download']}</a>
              </div>
              <div class="guide-instructions"><p class="guide-entry"><strong>{entry_label}</strong><br>{esc(entry)}</p><h4>{t['steps']}</h4>{scope_note}<ol>{steps}</ol></div>
            </div>
          </details>'''


def library(clips, lang, shortcuts_first=False):
    t = TEXT[lang]
    if not clips:
        return ''
    if shortcuts_first:
        clips = [{**c, 'group': 'control-center'} if c['id'] in ('24-control-center-record', '23-control-center-pending') else c for c in clips]
        priority = {'24-control-center-record': 0, '23-control-center-pending': 1, '19-shortcuts-home-screen': 2, '20-shortcuts-siri-name': 3}
        clips = sorted(clips, key=lambda clip: priority.get(clip['id'], 4))
    grouped = {key: [c for c in clips if group_for(c) == key] for key in GROUPS}
    toc = ''.join(f'<a href="#guide-group-{key}"><span>{labels[0 if lang == "ja" else 1]}</span><span aria-hidden="true">{len(grouped[key])}</span></a>'
                  for key, labels in GROUPS.items() if grouped[key])
    groups = []
    for key, labels in GROUPS.items():
        if not grouped[key]:
            continue
        groups.append(f'''      <section class="guide-group" id="guide-group-{key}" data-guide-group aria-labelledby="guide-heading-{key}">
        <div class="guide-group-heading"><h3 id="guide-heading-{key}">{labels[0 if lang == 'ja' else 1]}</h3><p>{labels[2 if lang == 'ja' else 3]}</p></div>
        <div class="guide-cards">
{chr(10).join(card(c, lang) for c in grouped[key])}
        </div>
      </section>''')
    return f'''    <section class="guide-library" aria-labelledby="guide-library-heading">
      <div class="guide-library-heading"><div><h2 id="guide-library-heading">{t['heading']}</h2><p>{t['intro']}</p></div><span class="guide-total">{len(clips)} {t['count']}</span></div>
      <nav class="guide-toc" aria-label="{esc(t['heading'])}">{toc}</nav>
      <div class="guide-search" hidden data-guide-search-controls>
        <label for="guide-search">{t['search']}</label>
        <div><input id="guide-search" type="search" placeholder="{t['placeholder']}" autocomplete="off"><button type="button" data-guide-clear>{t['clear']}</button></div>
      </div>
      <p class="guide-search-status" data-guide-status role="status" aria-live="polite" data-count-label="{t['count']}" data-empty-label="{t['empty']}"></p>
{chr(10).join(groups)}
    </section>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--version', help='Target website version; defaults to registry working version')
    parser.add_argument('--require-english', action='store_true', help='Fail unless all English interface recordings are present')
    args = parser.parse_args()
    try:
        registry = json.loads(REGISTRY.read_text())
        version = args.version or registry['working']
        entry = next((item for item in registry['versions'] if item['version'] == version), None)
        if entry is None:
            raise ValueError(f'Unknown website version: {version}')
        source_root = ROOT / '_versions/kotori' / entry['source']
        shortcuts_first = tuple(int(part) for part in version.split('.')) >= (1, 2, 0)
        japanese = read_clips('ja')
        has_english = (MEDIA_ROOT / 'en/manifest.json').is_file()
        if args.require_english and not has_english:
            raise ValueError('English interface recordings are required')
        if len(japanese) > len(REQUIRED_RECORDING_IDS) and not has_english:
            raise ValueError('Recordings 19–20 require matching Japanese and English interface recordings')
        english = read_clips('en') if has_english else list(japanese)
        if has_english:
            check_matching_provenance(japanese, english)
        if shortcuts_first:
            extra_ja = read_clips('ja', '1.2.0')
            extra_en = read_clips('en', '1.2.0')
            check_matching_provenance(extra_ja, extra_en)
            # Put each new feature beside the existing related guide.
            for clips, additions in ((japanese, extra_ja), (english, extra_en)):
                for addition in additions:
                    if addition['id'] == '19-shortcuts-home-screen':
                        index = next(i for i, clip in enumerate(clips) if clip['id'] == addition['id'])
                        clips[index] = addition
                        continue
                    predecessor = {'21-chat-recurring': '12-recurring', '22-exchange-rates': '10-reports',
                                   '23-control-center-pending': '03-pending-confirmation', '24-control-center-record': '23-control-center-pending', '26-bookkeeping-reminders': '16-settings-and-shortcuts', '25-appearance': '16-settings-and-shortcuts'}[addition['id']]
                    index = next(i for i, clip in enumerate(clips) if clip['id'] == predecessor)
                    clips.insert(index + 1, addition)
        changed = []
        for lang, name in [('ja', 'support-ja.html'), ('en', 'support.html')]:
            clips = japanese if lang == 'ja' else english
            path = source_root / name
            source = path.read_text()
            if len(MARKER.findall(source)) != 1:
                raise ValueError(f'Missing unique guide markers: {name}')
            output = MARKER.sub(lambda m: m[1] + library(clips, lang, shortcuts_first) + m[2], source)
            if output != source:
                changed.append(name)
                if not args.check:
                    path.write_text(output)
        if args.check and changed:
            print('Guide content drift: ' + ', '.join(changed), file=sys.stderr)
            return 1
        print(f'OK: {len(japanese)} Japanese / {len(english) if has_english else 0} English recording sets; guide sources ' + ('match.' if args.check else 'generated.'))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Guide build failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
