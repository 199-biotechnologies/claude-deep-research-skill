#!/usr/bin/env python3
"""Regression tests for Windows-encoding bugs found running an actual
research report end-to-end on Windows (Python 3.13, default console code
page cp1252, no PYTHONUTF8/PYTHONIOENCODING set).

Two distinct root causes, both covered here:
  1. File I/O (`append_jsonl`/`read_jsonl`/manifest writes) opened files
     without `encoding='utf-8'`. Registering a source whose title contains
     non-cp1252 characters (Slovak diacritics, CJK, Arabic, Cyrillic, ...)
     raised UnicodeEncodeError *after* partially writing the JSONL line,
     corrupting `sources.jsonl` for every subsequent call.
  2. stdout itself defaults to the console code page on Windows. Commands
     that print report data back out (`export-bibliography` in particular)
     crashed with UnicodeEncodeError the moment a title fell outside
     cp1252, independent of the file-encoding fix in (1).

These tests intentionally do NOT set PYTHONUTF8/PYTHONIOENCODING in the
subprocess environment — the whole point is that the scripts must work
without that undocumented workaround.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'citation_manager.py')

# Deliberately excludes the workaround env vars so these tests reproduce
# the exact conditions that used to crash on stock Windows Python.
CLEAN_ENV = {k: v for k, v in os.environ.items()
             if k not in ('PYTHONUTF8', 'PYTHONIOENCODING')}

MULTI_LANGUAGE_TITLES = [
    "Zmena zamestnávateľa počas pobytu — ľúbozvučný test",  # Slovak diacritics
    "中文标题测试 — 计算机网络工程师",                              # Chinese
    "اختبار العنوان العربي للتوظيف",                            # Arabic (RTL)
    "Проверка кириллицы: бакалавр компьютерных сетей",         # Cyrillic
    "Straße München Prüfung für Ingenieure",                   # German diacritics
    "日本語のタイトルテスト",                                        # Japanese
]


def run_cm(*args, env=None):
    result = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, text=True, encoding='utf-8',
        env=env if env is not None else CLEAN_ENV,
    )
    return result


class TestNonAsciiTitlesDoNotCrash(unittest.TestCase):
    """Bug (1): registering a non-cp1252 title used to throw
    UnicodeEncodeError mid-write and corrupt sources.jsonl.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        run_cm('init-run', '--out-dir', self.tmpdir, '--query', 'test', env=CLEAN_ENV)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_register_each_language_without_crash(self):
        for i, title in enumerate(MULTI_LANGUAGE_TITLES):
            with self.subTest(title=title):
                result = run_cm(
                    'register-source', '--json',
                    json.dumps({'raw_url': f'https://example.com/{i}', 'title': title}),
                    '--dir', self.tmpdir,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                out = json.loads(result.stdout)
                self.assertEqual(out['status'], 'registered')

    def test_sources_jsonl_round_trips_all_titles(self):
        for i, title in enumerate(MULTI_LANGUAGE_TITLES):
            run_cm(
                'register-source', '--json',
                json.dumps({'raw_url': f'https://example.com/{i}', 'title': title}),
                '--dir', self.tmpdir,
            )

        sources_path = os.path.join(self.tmpdir, 'sources.jsonl')
        with open(sources_path, encoding='utf-8') as f:
            rows = [json.loads(line) for line in f]

        self.assertEqual(len(rows), len(MULTI_LANGUAGE_TITLES))
        self.assertEqual({r['title'] for r in rows}, set(MULTI_LANGUAGE_TITLES))

    def test_a_later_ascii_registration_is_not_corrupted_by_an_earlier_unicode_one(self):
        """Before the fix, a crash while registering a non-ASCII title left
        a truncated line in sources.jsonl, which then broke
        read_jsonl()'s json.loads() on the *next* call (even for a plain
        ASCII source).
        """
        run_cm(
            'register-source', '--json',
            json.dumps({'raw_url': 'https://example.com/0', 'title': MULTI_LANGUAGE_TITLES[1]}),
            '--dir', self.tmpdir,
        )
        result = run_cm(
            'register-source', '--json',
            json.dumps({'raw_url': 'https://example.com/1', 'title': 'Plain ASCII Title'}),
            '--dir', self.tmpdir,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'registered')


class TestExportBibliographyStdoutEncoding(unittest.TestCase):
    """Bug (2): `export-bibliography` prints titles straight to stdout;
    on Windows that stream defaults to the console code page, so a title
    outside cp1252 crashed the print() itself even after fix (1) made the
    underlying file I/O safe.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        run_cm('init-run', '--out-dir', self.tmpdir, '--query', 'test', env=CLEAN_ENV)
        for i, title in enumerate(MULTI_LANGUAGE_TITLES):
            run_cm(
                'register-source', '--json',
                json.dumps({'raw_url': f'https://example.com/{i}', 'title': title}),
                '--dir', self.tmpdir,
            )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_markdown_export_does_not_crash_and_contains_all_titles(self):
        result = run_cm('export-bibliography', '--dir', self.tmpdir, '--style', 'markdown')
        self.assertEqual(result.returncode, 0, result.stderr)
        for title in MULTI_LANGUAGE_TITLES:
            self.assertIn(title, result.stdout)

    def test_json_export_does_not_crash(self):
        result = run_cm('export-bibliography', '--dir', self.tmpdir, '--style', 'json')
        self.assertEqual(result.returncode, 0, result.stderr)
        titles = {row['title'] for row in json.loads(result.stdout)}
        self.assertEqual(titles, set(MULTI_LANGUAGE_TITLES))


if __name__ == '__main__':
    unittest.main()
