"""Regression check for replacing a recording without changing its public filename."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import build_guides


class MediaReferences(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.urls = []
        self.feed(markup)

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name in ('src', 'data-src', 'data-poster', 'href') and value.startswith('assets/guides/'):
                self.urls.append(value)


class RecordingCacheTests(unittest.TestCase):
    def test_replacing_each_asset_updates_only_its_urls(self):
        source = build_guides.MEDIA_ROOT
        with tempfile.TemporaryDirectory() as directory:
            media = Path(directory)
            # Use the real validated manifests, with isolated links to the media.
            for language in ('ja', 'en'):
                folder = media / language
                folder.mkdir()
                for path in (source / language).iterdir():
                    if path.is_file():
                        (folder / path.name).symlink_to(path)
            with patch.object(build_guides, 'MEDIA_ROOT', media):
                for language in ('ja', 'en'):
                    def urls():
                        clips = build_guides.read_clips(language)
                        return [MediaReferences(build_guides.card(c, language)).urls for c in clips]
                    baseline = urls()
                    self.assertEqual(baseline, urls(), 'An unchanged build must keep stable media URLs')
                    clip_index = next(i for i, clip in enumerate(build_guides.read_clips(language))
                                      if clip['id'] == '20-shortcuts-siri-name')
                    references = baseline[clip_index]
                    self.assertEqual(len(references), 6)
                    for url in references:
                        parsed = urlsplit(url)
                        self.assertTrue(parse_qs(parsed.query).get('v'), url)
                    self.assertEqual(references[0], references[1], 'Poster and player must use the same image')
                    self.assertEqual(references[2], references[5], 'Player and direct link must use the same video')
                    for suffix in ('.mp4', '.jpg', '.ja.vtt', '.en.vtt'):
                        with self.subTest(language=language, suffix=suffix):
                            asset = media / language / ('20-shortcuts-siri-name' + suffix)
                            original = asset.resolve()
                            content = bytearray(asset.read_bytes())
                            # Same filename and byte count; modify content without touching source media.
                            if suffix.endswith('.vtt'):
                                position = content.index(b'-->') - 2
                                content[position] = ord('1') if content[position] != ord('1') else ord('2')
                            else:
                                content[-1] ^= 1
                            asset.unlink()
                            asset.write_bytes(content)
                            try:
                                changed = urls()
                                for i, (before, after) in enumerate(zip(baseline, changed)):
                                    for old, new in zip(before, after):
                                        if i == clip_index and urlsplit(old).path.endswith(suffix):
                                            self.assertNotEqual(old, new, 'Changed asset must get a new URL')
                                            self.assertEqual(urlsplit(old).path, urlsplit(new).path)
                                        else:
                                            self.assertEqual(old, new, 'Unchanged assets must keep their URLs')
                            finally:
                                asset.unlink()
                                asset.symlink_to(original)
                    self.assertEqual(baseline, urls())


if __name__ == '__main__':
    unittest.main()
