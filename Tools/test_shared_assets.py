"""Versions share identical images and fonts by URL, and stay isolated when one of them changes."""
import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import build_versions as build

# The two newest versions that start out with the same screenshot.
EDITED, OTHER = 'v1.2.3', 'v1.2.2'
IMAGE = 'assets/screens/ja/01-conversation.jpg'


class SharedAssetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.sources = Path(self.directory.name) / 'kotori'
        shutil.copytree(build.SOURCES, self.sources)
        sources = patch.object(build, 'SOURCES', self.sources)
        sources.start(); self.addCleanup(sources.stop)
        self.data = build.registry()

    def build(self):
        return build.expected_files(self.data)

    def page_images(self, files, route):
        doc = build.Links(); doc.feed(files[route + '/index.html'].decode())
        return [ref for ref in doc.refs if urlsplit(ref).path.endswith(('.jpg', '.png'))]

    def test_identical_versions_use_the_same_urls(self):
        shutil.rmtree(self.sources / EDITED / 'assets/screens')
        shutil.copytree(self.sources / OTHER / 'assets/screens', self.sources / EDITED / 'assets/screens')
        for page in build.PAGES:
            shutil.copy(self.sources / OTHER / page, self.sources / EDITED / page)
        files = self.build()
        first, second = self.page_images(files, 'kotori/' + OTHER), self.page_images(files, 'kotori/' + EDITED)
        self.assertTrue(first)
        self.assertEqual(first, second)
        for name in files:
            if Path(name).suffix in build.SHARED_TYPES:
                self.assertTrue(name.startswith(build.SHARED + '/'), name)

    def test_each_shared_file_is_published_once(self):
        shared = [content for name, content in self.build().items() if name.startswith(build.SHARED + '/')]
        self.assertEqual(len(shared), len(set(shared)))

    def test_changing_one_version_leaves_every_other_version_unchanged(self):
        before = self.build()
        image = self.sources / EDITED / IMAGE
        image.write_bytes(image.read_bytes() + b'replacement')
        css = self.sources / EDITED / 'assets/site.css'
        css.write_text(css.read_text() + '\n/* changed */\n')
        after = self.build()
        changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
        route = 'kotori/' + EDITED + '/'
        self.assertTrue(changed)
        for name in changed:
            self.assertTrue(name.startswith((route, build.SHARED + '/')), name)
        # The previous image is still published for the versions that use it.
        self.assertTrue(set(self.page_images(before, 'kotori/' + OTHER)) == set(self.page_images(after, 'kotori/' + OTHER)))
        for ref in self.page_images(after, 'kotori/' + OTHER):
            self.assertIn(posix(ref, 'kotori/' + OTHER), after)

    def test_missing_source_image_fails(self):
        (self.sources / EDITED / IMAGE).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing source asset'):
            self.build()


class CheckTests(unittest.TestCase):
    def test_check_reports_missing_altered_and_leftover_shared_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'kotori').mkdir()
            # Read the real sources, but generate into an isolated output root.
            (root / '_versions').symlink_to(build.SOURCES.parent)
            (root / 'kotori/assets').mkdir()
            (root / 'kotori/assets/guides').symlink_to(build.GUIDES)
            registry = root / 'generated-files.json'
            with patch.object(build, 'ROOT', root), patch.object(build, 'GENERATED', registry), \
                 patch.object(build, 'GUIDES', root / 'kotori/assets/guides'):
                def run(*arguments):
                    with patch.object(sys, 'argv', ['build_versions.py', *arguments]), \
                         contextlib.redirect_stderr(io.StringIO()) as error, contextlib.redirect_stdout(io.StringIO()):
                        return build.main(), error.getvalue()
                self.assertEqual(run()[0], 0)
                self.assertEqual(run('--check')[0], 0)
                shared = sorted((root / build.SHARED).iterdir())[0]
                content = shared.read_bytes()
                shared.write_bytes(content + b'x')
                self.assertIn(shared.name, run('--check')[1])
                shared.unlink()
                self.assertIn(shared.name, run('--check')[1])
                shared.write_bytes(content)
                leftover = root / build.SHARED / '00000000000000000000.png'
                leftover.write_bytes(b'unused')
                self.assertIn(leftover.name, run('--check')[1])


def posix(ref, route):
    return build.posixpath.normpath(build.posixpath.join(route, urlsplit(ref).path))


if __name__ == '__main__':
    unittest.main()
