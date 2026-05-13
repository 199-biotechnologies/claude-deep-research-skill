#!/usr/bin/env python3
"""
Markdown to HTML converter for research reports
Properly converts markdown sections to HTML while preserving structure and formatting
"""

import re
from typing import Tuple
from pathlib import Path


def convert_markdown_to_html(markdown_text: str) -> Tuple[str, str]:
    """
    Convert markdown to HTML in two parts: content and bibliography.

    Splits the markdown into three regions:
      - body:        everything up to '## Bibliography'
      - bibliography: between '## Bibliography' and '## Appendix' (if any)
      - appendix:    from '## Appendix' onwards

    Body and Appendix go through the same content converter; the Appendix is
    appended to the returned content_html so its headings, tables, and
    paragraphs survive print rendering.

    Args:
        markdown_text: Full markdown report text

    Returns:
        Tuple of (content_html, bibliography_html)
    """
    bib_match = re.search(r'^## Bibliography\s*$', markdown_text, flags=re.MULTILINE)
    if bib_match:
        body_md = markdown_text[:bib_match.start()]
        rest = markdown_text[bib_match.end():]
        appendix_match = re.search(r'^## Appendix', rest, flags=re.MULTILINE)
        if appendix_match:
            bibliography_md = rest[:appendix_match.start()]
            appendix_md = rest[appendix_match.start():]
        else:
            bibliography_md = rest
            appendix_md = ""
    else:
        body_md = markdown_text
        bibliography_md = ""
        appendix_md = ""

    content_html = _convert_content_section(body_md)
    if appendix_md.strip():
        content_html += "\n" + _convert_content_section(appendix_md)

    bibliography_html = _convert_bibliography_section(bibliography_md)
    return content_html, bibliography_html


def _convert_content_section(markdown: str) -> str:
    """Convert main content sections to HTML"""
    html = markdown

    # Remove title and front matter (first ## heading is handled separately)
    lines = html.split('\n')
    processed_lines = []
    skip_until_first_section = True

    for line in lines:
        # Skip everything until we hit "## Executive Summary" or first major section
        if skip_until_first_section:
            if line.startswith('## ') and not line.startswith('### '):
                skip_until_first_section = False
                processed_lines.append(line)
            continue
        processed_lines.append(line)

    html = '\n'.join(processed_lines)

    # Convert headers
    # ## Section Title → <div class="section"><h2 class="section-title">Section Title</h2></div>
    html = re.sub(
        r'^## (.+)$',
        r'<div class="section"><h2 class="section-title">\1</h2>',
        html,
        flags=re.MULTILINE
    )

    # ### Subsection → <h3 class="subsection-title">Subsection</h3>
    html = re.sub(
        r'^### (.+)$',
        r'<h3 class="subsection-title">\1</h3>',
        html,
        flags=re.MULTILINE
    )

    # #### Subsubsection → <h4 class="subsubsection-title">Title</h4>
    html = re.sub(
        r'^#### (.+)$',
        r'<h4 class="subsubsection-title">\1</h4>',
        html,
        flags=re.MULTILINE
    )

    # Horizontal rules: '---', '***' or '___' on their own line → <hr>
    html = re.sub(
        r'^(?:-{3,}|\*{3,}|_{3,})\s*$',
        '<hr class="section-divider">',
        html,
        flags=re.MULTILINE,
    )

    # Convert **bold** text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert *italic* text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert inline code `code`
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Convert unordered lists
    html = _convert_lists(html)

    # Convert tables
    html = _convert_tables(html)

    # Convert paragraphs (wrap non-HTML lines in <p> tags)
    html = _convert_paragraphs(html)

    # Close all open sections
    html = _close_sections(html)

    # Wrap executive summary if present
    html = html.replace(
        '<h2 class="section-title">Executive Summary</h2>',
        '<div class="executive-summary"><h2 class="section-title">Executive Summary</h2>'
    )
    if '<div class="executive-summary">' in html:
        # Close executive summary at the next section
        html = html.replace(
            '</h2>\n<div class="section">',
            '</h2></div>\n<div class="section">',
            1
        )

    return html


def _convert_bibliography_section(markdown: str) -> str:
    """Convert a markdown bibliography to one styled <p> per entry.

    Each entry starts at the beginning of a line with a '[N]' citation marker
    and continues until the next entry or end-of-section. URLs are linkified;
    inline markdown emphasis is preserved.
    """
    if not markdown.strip():
        return ""

    # Drop HTML comments and horizontal-rule separators
    cleaned = re.sub(r'<!--.*?-->', '', markdown, flags=re.DOTALL)
    cleaned = re.sub(r'^(?:-{3,}|\*{3,}|_{3,})\s*$', '', cleaned, flags=re.MULTILINE)

    entries = []
    pattern = re.compile(
        r'^\[(\d+)\]\s*(.*?)(?=^\[\d+\]\s|\Z)',
        flags=re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(cleaned):
        num = m.group(1)
        text = re.sub(r'\s+', ' ', m.group(2).strip())
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
        text = re.sub(
            r'(https?://[^\s)\]]+)',
            r'<a href="\1" target="_blank" rel="noopener">\1</a>',
            text,
        )
        entries.append(
            f'<p class="bib-entry" style="margin:0 0 10px 0; padding-left:2.2em; '
            f'text-indent:-2.2em; line-height:1.45;">'
            f'<span class="bib-number" style="font-weight:600;">[{num}]</span> '
            f'{text}</p>'
        )

    if not entries:
        return ""
    return (
        '<div class="bibliography-content" '
        'style="font-size:12.5px; word-break:break-word;">'
        + '\n'.join(entries) +
        '</div>'
    )


def _convert_lists(html: str) -> str:
    """Convert markdown lists to HTML lists"""
    lines = html.split('\n')
    result = []
    in_list = False
    list_level = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for unordered list item
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
                list_level = len(line) - len(line.lstrip())

            # Get the content after the marker
            content = stripped[2:]
            result.append(f'<li>{content}</li>')

        # Check for ordered list item
        elif re.match(r'^\d+\.\s', stripped):
            if not in_list:
                result.append('<ol>')
                in_list = True
                list_level = len(line) - len(line.lstrip())

            # Get the content after the number and period
            content = re.sub(r'^\d+\.\s', '', stripped)
            result.append(f'<li>{content}</li>')

        else:
            # Not a list item
            if in_list:
                # Check if we're still in the list (indented continuation)
                current_level = len(line) - len(line.lstrip())
                if current_level > list_level and stripped:
                    # Continuation of previous list item
                    if result[-1].endswith('</li>'):
                        result[-1] = result[-1][:-5] + ' ' + stripped + '</li>'
                    continue
                else:
                    # End of list
                    result.append('</ul>' if '<ul>' in '\n'.join(result[-10:]) else '</ol>')
                    in_list = False
                    list_level = 0

            result.append(line)

    # Close any remaining open list
    if in_list:
        result.append('</ul>' if '<ul>' in '\n'.join(result[-10:]) else '</ol>')

    return '\n'.join(result)


def _convert_tables(html: str) -> str:
    """Convert markdown tables to HTML tables"""
    lines = html.split('\n')
    result = []
    in_table = False

    for i, line in enumerate(lines):
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                result.append('<table>')
                in_table = True
                # This is the header row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                result.append('<thead><tr>')
                for cell in cells:
                    result.append(f'<th>{cell}</th>')
                result.append('</tr></thead>')
                result.append('<tbody>')
            elif '---' in line:
                # Skip separator row
                continue
            else:
                # Data row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                result.append('<tr>')
                for cell in cells:
                    result.append(f'<td>{cell}</td>')
                result.append('</tr>')
        else:
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            result.append(line)

    if in_table:
        result.append('</tbody></table>')

    return '\n'.join(result)


_KEY_VALUE_PREFIX = re.compile(r'^\s*<strong>[^<]+:</strong>')


def _convert_paragraphs(html: str) -> str:
    """Wrap non-HTML lines in paragraph tags.

    When two consecutive non-blank text lines both look like
    '<strong>Key:</strong> value' (i.e. metadata pairs), insert <br> between
    them so they render on separate visual lines instead of collapsing into
    one run-on paragraph.
    """
    lines = html.split('\n')
    result = []
    in_paragraph = False
    prev_was_kv = False

    for line in lines:
        stripped = line.strip()

        # Blank line: close paragraph if open
        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            prev_was_kv = False
            result.append(line)
            continue

        # Already-HTML block: close paragraph and emit raw
        if (stripped.startswith('<') and stripped.endswith('>')) or \
           stripped.startswith('</') or \
           '<h' in stripped or '<div' in stripped or '<ul' in stripped or \
           '<ol' in stripped or '<li' in stripped or '<table' in stripped or \
           '<hr' in stripped or \
           '</div>' in stripped or '</ul>' in stripped or '</ol>' in stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            prev_was_kv = False
            result.append(line)
            continue

        # Regular text line
        is_kv = bool(_KEY_VALUE_PREFIX.match(stripped))
        if not in_paragraph:
            result.append('<p>' + line)
            in_paragraph = True
        else:
            # Continuation of an open paragraph. If both this and the previous
            # line look like 'Key: value' metadata, insert a <br>.
            if is_kv and prev_was_kv:
                result.append('<br>' + line)
            else:
                result.append(line)
        prev_was_kv = is_kv

    if in_paragraph:
        result.append('</p>')

    return '\n'.join(result)


def _close_sections(html: str) -> str:
    """Close all open section divs"""
    # Count open and closed divs
    open_divs = html.count('<div class="section">')
    closed_divs = html.count('</div>')

    # Add closing divs for sections
    # Each section should be closed before the next section starts
    lines = html.split('\n')
    result = []
    section_open = False

    for i, line in enumerate(lines):
        if '<div class="section">' in line:
            if section_open:
                result.append('</div>')  # Close previous section
            section_open = True
        result.append(line)

    # Close final section if still open
    if section_open:
        result.append('</div>')

    return '\n'.join(result)


_DEFAULT_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "templates"
    / "mckinsey_report_template.html"
)


# CSS injected into the template <head> so Chrome's headless print engine
# produces a clean PDF (no URL/date/page-number header or footer).
_PRINT_CSS = """
<style>
  @page { margin: 14mm 12mm; size: A4; }
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .header, .metrics-dashboard { break-inside: avoid; }
    .section { break-inside: auto; }
    h2.section-title, h3.subsection-title { break-after: avoid; }
    p.bib-entry { break-inside: avoid; }
  }
  hr.section-divider {
    border: none;
    border-top: 1px solid #d1d5db;
    margin: 18px 0;
  }
</style>
"""


def _build_metrics_dashboard(metrics: dict[str, str]) -> str:
    """Render a dashboard tile row from a {label: value} dict."""
    if not metrics:
        return ""
    tiles = []
    for label, value in metrics.items():
        tiles.append(
            f'<div class="metric">'
            f'<span class="metric-number">{value}</span>'
            f'<span class="metric-label">{label}</span>'
            f'</div>'
        )
    return '<div class="metrics-dashboard">' + "".join(tiles) + '</div>'


def build_report(
    markdown_path: Path | str,
    output_html_path: Path | str,
    *,
    title: str,
    date: str,
    source_count: int | str,
    metrics: dict[str, str] | None = None,
    template_path: Path | str | None = None,
) -> Path:
    """End-to-end: read markdown, convert, fill template, write HTML.

    Used by per-report wrappers so each report has a one-call build step
    and any future fix to rendering happens in one shared place.
    """
    markdown_path = Path(markdown_path)
    output_html_path = Path(output_html_path)
    template_path = Path(template_path) if template_path else _DEFAULT_TEMPLATE

    md = markdown_path.read_text()
    template = template_path.read_text()
    content_html, bib_html = convert_markdown_to_html(md)

    # Inject print CSS into the template <head> if not already present.
    if 'hr.section-divider' not in template:
        template = template.replace('</head>', _PRINT_CSS + '\n</head>', 1)

    metrics_html = _build_metrics_dashboard(metrics or {})

    out = (template
           .replace("{{TITLE}}", title)
           .replace("{{DATE}}", date)
           .replace("{{SOURCE_COUNT}}", str(source_count))
           .replace("{{METRICS_DASHBOARD}}", metrics_html)
           .replace("{{CONTENT}}", content_html)
           .replace("{{BIBLIOGRAPHY}}", bib_html))

    output_html_path.write_text(out)
    return output_html_path


def main():
    """Test the converter with a sample markdown file"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <markdown_file>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"Error: File {md_file} not found")
        sys.exit(1)

    markdown_text = md_file.read_text()
    content_html, bib_html = convert_markdown_to_html(markdown_text)

    print("=== CONTENT HTML ===")
    print(content_html[:1000])
    print("\n=== BIBLIOGRAPHY HTML ===")
    print(bib_html[:500])


if __name__ == "__main__":
    main()
