#!/usr/bin/env python3
"""Tests for verify_html.py, focused on the `_has_class()` fix.

Bug: `'class="bibliography"' not in html` is a literal substring check on
the exact attribute value. It false-negatives on `class="section bibliography"`
(multiple space-separated classes on the same element) even though the
section is present and correctly classed — which is exactly what
md_to_html.py's real generated bibliography wrapper can look like.
"""

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))
from verify_html import _has_class, HTMLVerifier  # noqa: E402


class TestHasClass(unittest.TestCase):
    def test_single_class_matches(self):
        self.assertTrue(_has_class('<div class="bibliography">', 'bibliography'))

    def test_multi_class_matches(self):
        self.assertTrue(_has_class('<div class="section bibliography">', 'bibliography'))
        self.assertTrue(_has_class('<div class="bibliography section">', 'bibliography'))

    def test_absent_class_does_not_match(self):
        self.assertFalse(_has_class('<div class="section">', 'bibliography'))

    def test_does_not_match_substring_of_another_class(self):
        # "bibliography-content" must not satisfy a check for "bibliography"
        # as a distinct token — token-boundary matching, not substring.
        self.assertFalse(_has_class('<div class="bibliography-content">', 'bibliography'))

    def test_bib_entry_class_token(self):
        self.assertTrue(_has_class('<div class="bib-entry">', 'bib-entry'))
        self.assertFalse(_has_class('<div class="bib-entry-extra">', 'bib-entry'))


class TestBibliographyCheckEndToEnd(unittest.TestCase):
    """`_check_bibliography` / `_check_structure` should pass on a
    multi-class bibliography wrapper and still correctly fail when the
    bibliography is genuinely missing.
    """

    def _verifier(self):
        # HTMLVerifier only needs paths for its constructor; the checks
        # exercised here take html/md strings directly.
        return HTMLVerifier(Path('unused.html'), Path('unused.md'))

    def test_passes_with_multi_class_wrapper(self):
        v = self._verifier()
        html = (
            '<div class="section bibliography">'
            '<h2 class="section-title">Bibliography</h2>'
            '<p class="bib-entry"><span class="bib-number">[1]</span> Example</p>'
            '</div>'
        )
        md = '## Bibliography\n\n[1] Example - https://example.com\n'
        v._check_bibliography(html, md)
        self.assertEqual(v.errors, [])
        self.assertEqual(v.warnings, [])

    def test_fails_when_bibliography_truly_absent(self):
        v = self._verifier()
        html = '<div class="section"><h2 class="section-title">Executive Summary</h2></div>'
        md = '## Bibliography\n\n[1] Example - https://example.com\n'
        v._check_bibliography(html, md)
        self.assertEqual(len(v.errors), 1)
        self.assertIn('Bibliography section missing', v.errors[0])

    def test_warns_when_entries_not_formatted(self):
        v = self._verifier()
        html = '<div class="bibliography"><h2 class="section-title">Bibliography</h2>[1] raw text</div>'
        md = '## Bibliography\n\n[1] Example - https://example.com\n'
        v._check_bibliography(html, md)
        self.assertEqual(v.errors, [])
        self.assertEqual(len(v.warnings), 1)


if __name__ == '__main__':
    unittest.main()
