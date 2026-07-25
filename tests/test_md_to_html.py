#!/usr/bin/env python3
"""Tests for md_to_html.py: markdown->HTML conversion and the McKinsey
template CLI.

Covers three bugs found while running an actual ultradeep research report
on Windows:
  1. `convert_markdown_to_html()` used to drop/mangle every section that
     came after "## Bibliography" (e.g. "## Appendix: Methodology",
     "## Report Metadata" — both required by report_template.md).
  2. Fenced ```code blocks (particularly ```mermaid diagrams) were not
     recognized at all and came out as garbled inline text.
  3. `main()` never actually wrote an HTML file — it printed a 1000-char
     preview of the content and stopped, despite reference/html-generation.md
     documenting `python scripts/md_to_html.py report.md` as the way to
     produce the report's HTML output.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / 'scripts'
SCRIPT = SCRIPT_DIR / 'md_to_html.py'
TEMPLATE = Path(__file__).parent.parent / 'templates' / 'mckinsey_report_template.html'

sys.path.insert(0, str(SCRIPT_DIR))
from md_to_html import (  # noqa: E402
    convert_markdown_to_html,
    render_full_report_html,
    has_mermaid_block,
    _extract_fenced_code_blocks,
)


SAMPLE_REPORT = """# Research Report: Example Topic

## Executive Summary

Summary text citing a source [1].

## Main Analysis

### Finding 1: Something

Body text with **bold** and a table:

| Col A | Col B |
|---|---|
| x | y |

A diagram:

```mermaid
gantt
    title Example
    section A
    Task one :a1, 2026-01-01, 30d
```

## Bibliography

[1] Example Org (2026). "Example Title". https://example.com/a (Retrieved: 2026-07-25)

[2] Another Org (2026). "Second Title". https://example.com/b (Retrieved: 2026-07-25)

## Appendix: Methodology

### Research Process

Some methodology text [1].

| Claim ID | Major Claim | Sources |
|---|---|---|
| C1 | Example claim | [1], [2] |

## Report Metadata

**Total Sources:** 2
"""


class TestFencedCodeBlocks(unittest.TestCase):
    def test_mermaid_block_extracted_and_flagged(self):
        stripped, blocks = _extract_fenced_code_blocks(SAMPLE_REPORT)
        self.assertTrue(has_mermaid_block(blocks))
        self.assertNotIn('```', stripped)

    def test_non_mermaid_code_block_not_flagged_as_mermaid(self):
        md = "```python\nprint('hi')\n```\n"
        _, blocks = _extract_fenced_code_blocks(md)
        self.assertFalse(has_mermaid_block(blocks))

    def test_content_html_contains_rendered_mermaid_pre(self):
        content_html, _ = convert_markdown_to_html(SAMPLE_REPORT)
        self.assertIn('<pre class="mermaid">', content_html)
        self.assertIn('gantt', content_html)
        # No leftover placeholder tokens or stray backticks.
        self.assertNotIn('@@FENCED_CODE_BLOCK', content_html)
        self.assertNotIn('```', content_html)


class TestSectionsSurviveBibliographySplit(unittest.TestCase):
    """Regression test for the "everything after ## Bibliography is lost"
    bug: Appendix and Report Metadata must both come through as their own
    properly-headed sections, not get absorbed into the bibliography blob.
    """

    def setUp(self):
        self.content_html, self.bibliography_html = convert_markdown_to_html(SAMPLE_REPORT)

    def test_appendix_heading_present_in_content(self):
        self.assertIn('Appendix: Methodology', self.content_html)

    def test_report_metadata_heading_present_in_content(self):
        self.assertIn('Report Metadata', self.content_html)

    def test_appendix_table_converted_not_dropped(self):
        self.assertIn('<table>', self.content_html)
        self.assertIn('Example claim', self.content_html)

    def test_bibliography_heading_not_duplicated_in_content(self):
        # The heading itself belongs to the template's own bibliography
        # wrapper, not to content_html.
        self.assertNotIn('<h2 class="section-title">Bibliography</h2>', self.content_html)

    def test_bibliography_entries_present(self):
        self.assertIn('Example Title', self.bibliography_html)
        self.assertIn('Second Title', self.bibliography_html)

    def test_bibliography_entries_wrapped_as_bib_entry(self):
        self.assertIn('class="bib-entry"', self.bibliography_html)
        self.assertEqual(self.bibliography_html.count('class="bib-entry"'), 2)

    def test_no_document_without_bibliography_regresses(self):
        """A report with no '## Bibliography' at all must still convert the
        rest of the document normally (empty bibliography, non-empty content).
        """
        md = "# Title\n\n## Executive Summary\n\nText here.\n"
        content_html, bibliography_html = convert_markdown_to_html(md)
        self.assertIn('Executive Summary', content_html)
        self.assertEqual(bibliography_html, "")


class TestBibliographyEntryStyles(unittest.TestCase):
    """The old regex only matched `[N] Title - URL`. Both of the citation
    styles this skill actually produces (report_template.md's APA-ish
    style, and citation_manager.py's own markdown-link export style) must
    also be recognized.
    """

    def test_apa_style_dash_free_entry(self):
        md = '## Bibliography\n\n[1] Org (2026). "Title". Site. https://example.com/x (Retrieved: 2026-07-25)\n'
        _, bib_html = convert_markdown_to_html(md)
        self.assertIn('class="bib-entry"', bib_html)
        self.assertIn('href="https://example.com/x"', bib_html)

    def test_markdown_link_style_entry(self):
        md = '## Bibliography\n\n[1] (2026). [Title Text](https://example.com/y)\n'
        _, bib_html = convert_markdown_to_html(md)
        self.assertIn('class="bib-entry"', bib_html)
        self.assertIn('href="https://example.com/y"', bib_html)
        self.assertIn('>Title Text</a>', bib_html)

    def test_dash_style_entry_still_works(self):
        md = '## Bibliography\n\n[1] Title - https://example.com/z\n'
        _, bib_html = convert_markdown_to_html(md)
        self.assertIn('class="bib-entry"', bib_html)
        self.assertIn('href="https://example.com/z"', bib_html)


class TestUnicodeRoundTrip(unittest.TestCase):
    """Multi-language content must survive conversion byte-for-byte; this
    is a pure in-process string test (no file I/O), separate from the
    encoding bugs covered by test_citation_manager_encoding.py.
    """

    def test_cjk_arabic_cyrillic_diacritics_preserved(self):
        md = (
            "## Executive Summary\n\n"
            "中文标题测试, اختبار العنوان العربي, "
            "Проверка кириллицы, Straße München, "
            "zamestnávateľa ľúbozvučný.\n"
        )
        content_html, _ = convert_markdown_to_html(md)
        for needle in (
            '中文标题测试', 'اختبار العنوان العربي', 'Проверка кириллицы',
            'Straße München', 'zamestnávateľa ľúbozvučný',
        ):
            self.assertIn(needle, content_html)


class TestRenderFullReportHtml(unittest.TestCase):
    def setUp(self):
        self.template_text = TEMPLATE.read_text(encoding='utf-8')

    def test_all_placeholders_replaced(self):
        html = render_full_report_html(
            SAMPLE_REPORT, self.template_text,
            title='Example', date='2026-07-25', source_count='2',
        )
        for placeholder in ('{{TITLE}}', '{{DATE}}', '{{CONTENT}}', '{{BIBLIOGRAPHY}}', '{{SOURCE_COUNT}}'):
            self.assertNotIn(placeholder, html)

    def test_title_defaults_to_first_h1(self):
        html = render_full_report_html(SAMPLE_REPORT, self.template_text)
        self.assertIn('Research Report: Example Topic', html)

    def test_mermaid_js_injected_when_diagram_present(self):
        html = render_full_report_html(SAMPLE_REPORT, self.template_text)
        self.assertIn('mermaid.min.js', html)
        self.assertIn('mermaid.initialize', html)

    def test_mermaid_js_not_injected_when_no_diagram(self):
        md = "# Title\n\n## Executive Summary\n\nNo diagrams here.\n"
        html = render_full_report_html(md, self.template_text)
        self.assertNotIn('mermaid.min.js', html)

    def test_bibliography_class_present_for_verify_html(self):
        html = render_full_report_html(
            SAMPLE_REPORT, self.template_text, title='Example', date='x', source_count='2',
        )
        self.assertIn('class="bibliography"', html)
        self.assertIn('class="bib-entry"', html)


class TestCliWritesFile(unittest.TestCase):
    """End-to-end: the documented `python scripts/md_to_html.py report.md`
    invocation must produce a real .html file, not just stdout output.
    """

    def test_cli_produces_html_file(self):
        with tempfile.TemporaryDirectory() as d:
            md_path = Path(d) / 'report.md'
            md_path.write_text(SAMPLE_REPORT, encoding='utf-8')
            out_path = Path(d) / 'report.html'

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(md_path), '--out', str(out_path),
                 '--date', '2026-07-25', '--source-count', '2'],
                capture_output=True, text=True, encoding='utf-8',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out_path.exists())

            html = out_path.read_text(encoding='utf-8')
            self.assertIn('<pre class="mermaid">', html)
            self.assertIn('Appendix: Methodology', html)
            self.assertIn('Report Metadata', html)
            self.assertNotIn('{{CONTENT}}', html)

    def test_cli_preview_mode_does_not_write_file(self):
        with tempfile.TemporaryDirectory() as d:
            md_path = Path(d) / 'report.md'
            md_path.write_text(SAMPLE_REPORT, encoding='utf-8')

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(md_path), '--preview'],
                capture_output=True, text=True, encoding='utf-8',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('=== CONTENT HTML ===', result.stdout)
            self.assertFalse((Path(d) / 'report.html').exists())

    def test_cli_default_out_path(self):
        with tempfile.TemporaryDirectory() as d:
            md_path = Path(d) / 'report.md'
            md_path.write_text(SAMPLE_REPORT, encoding='utf-8')

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(md_path)],
                capture_output=True, text=True, encoding='utf-8',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(d) / 'report.html').exists())


if __name__ == '__main__':
    unittest.main()
