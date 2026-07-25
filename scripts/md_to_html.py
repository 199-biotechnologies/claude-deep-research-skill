#!/usr/bin/env python3
"""
Markdown to HTML converter for research reports
Properly converts markdown sections to HTML while preserving structure and formatting
"""

import re
from typing import Dict, Tuple
from pathlib import Path


def _extract_fenced_code_blocks(markdown: str) -> Tuple[str, Dict[str, str]]:
    """Pull ``` fenced code blocks out of the markdown before any other
    conversion runs, replacing each with a unique placeholder token.

    The header/bold/paragraph/table converters below all operate on raw
    text with regexes that know nothing about fenced code — left in place,
    a fence's ``` markers and any `**`/`#`/`|` characters inside it (very
    common in a mermaid gantt block, for example) get mangled into broken
    HTML. Stashing the blocks first and re-inserting them verbatim after
    conversion (see `_reinsert_fenced_code_blocks`) keeps their content
    byte-for-byte intact.

    Returns:
        (markdown_with_placeholders, {placeholder: (language, code)})
    """
    blocks: Dict[str, str] = {}

    def _stash(match: 're.Match') -> str:
        language = match.group(1).strip()
        code = match.group(2)
        token = f'@@FENCED_CODE_BLOCK_{len(blocks)}@@'
        blocks[token] = (language, code)
        return token

    pattern = re.compile(r'```([a-zA-Z0-9_-]*)\n(.*?)```', re.DOTALL)
    markdown = pattern.sub(_stash, markdown)
    return markdown, blocks


def _reinsert_fenced_code_blocks(html: str, blocks: Dict[str, str]) -> str:
    """Replace placeholder tokens from `_extract_fenced_code_blocks` with
    their final HTML. ```mermaid blocks become `<pre class="mermaid">` so
    mermaid.js (see `render_full_report_html`) can render them; anything
    else becomes a plain `<pre><code>` block.
    """
    for token, (language, code) in blocks.items():
        escaped = (
            code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        )
        if language.lower() == 'mermaid':
            replacement = f'<pre class="mermaid">\n{code}\n</pre>'
        elif language:
            replacement = f'<pre><code class="language-{language}">{escaped}</code></pre>'
        else:
            replacement = f'<pre><code>{escaped}</code></pre>'

        # The paragraph converter may have wrapped the bare token in <p></p>
        # since it looks like a plain text line at that point in the pipeline.
        html = html.replace(f'<p>{token}</p>', replacement)
        html = html.replace(token, replacement)
    return html


def has_mermaid_block(blocks: Dict[str, str]) -> bool:
    """True if any extracted fenced code block is a ```mermaid diagram."""
    return any(language.lower() == 'mermaid' for language, _ in blocks.values())


def convert_markdown_to_html(markdown_text: str) -> Tuple[str, str]:
    """
    Convert markdown to HTML in two parts: content and bibliography

    Args:
        markdown_text: Full markdown report text

    Returns:
        Tuple of (content_html, bibliography_html)
    """
    markdown_text, code_blocks = _extract_fenced_code_blocks(markdown_text)

    # Carve out only the "## Bibliography" section (from its heading up to,
    # but not including, the next top-level "## " heading) rather than
    # everything from "## Bibliography" to end-of-document. A naive
    # `.split('## Bibliography')` treats every section that happens to come
    # after Bibliography in the document (e.g. "## Appendix: Methodology",
    # "## Report Metadata" — both required by report_template.md) as part
    # of the bibliography, and _convert_bibliography_section() below only
    # understands `[N] Title - URL` citation lines, silently dropping or
    # mangling anything else it's given.
    bib_start = markdown_text.find('## Bibliography')
    if bib_start == -1:
        content_md = markdown_text
        bibliography_md = ''
    else:
        after_heading = bib_start + len('## Bibliography')
        next_heading = re.search(r'^## ', markdown_text[after_heading:], re.MULTILINE)
        bib_end = after_heading + next_heading.start() if next_heading else len(markdown_text)

        bibliography_md = markdown_text[after_heading:bib_end]
        content_md = markdown_text[:bib_start] + markdown_text[bib_end:]

    # Convert content (everything except the bibliography span)
    content_html = _convert_content_section(content_md)

    # Convert bibliography separately
    bibliography_html = _convert_bibliography_section(bibliography_md)

    content_html = _reinsert_fenced_code_blocks(content_html, code_blocks)
    bibliography_html = _reinsert_fenced_code_blocks(bibliography_html, code_blocks)

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
    """Convert bibliography section to HTML.

    Handles both citation styles seen in practice:
      - `[1] Title - https://...`                        (dash before a bare URL)
      - `[1] Author (Year). "Title". Publisher. https://...` (report_template.md's
        suggested APA-ish style, no dash)
      - `[1] (n.d.). [Title](https://...)`                (citation_manager.py's
        own `export-bibliography --style markdown` output, markdown link)

    The previous implementation only matched the first style via a single
    regex requiring a literal " - " immediately before the URL, so entries
    in either of the other two styles — including the tool's *own* export
    format — were never wrapped in `.bib-entry` and fell through to the
    generic bibliography div unformatted.
    """
    if not markdown.strip():
        return ""

    # One entry per non-blank line: wrap "[N] rest-of-line" before touching
    # any inline markdown, so the rest-of-line's own [text](url) links (if
    # any) survive untouched for the markdown-link pass below.
    wrapped_lines = []
    for line in markdown.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r'^\[(\d+)\]\s*(.*)$', stripped)
        if m:
            wrapped_lines.append(
                f'<div class="bib-entry"><span class="bib-number">[{m.group(1)}]</span> {m.group(2)}</div>'
            )
        else:
            wrapped_lines.append(line)
    html = '\n'.join(wrapped_lines)

    # Markdown links: [text](url) -> <a href="url">text</a>
    html = re.sub(
        r'\[([^\[\]]+)\]\((https?://[^\s\)]+)\)',
        r'<a href="\2" target="_blank">\1</a>',
        html
    )

    # Convert any remaining **bold** sections
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Linkify any bare URLs not already inside an href="..." attribute
    # (dash-style and APA-ish entries end in a plain https://... with no
    # markdown link syntax around it).
    html = re.sub(
        r'(?<!href=")(https?://[^\s<)]+)',
        r'<a href="\1" target="_blank">\1</a>',
        html
    )

    # Wrap in bibliography content div
    html = f'<div class="bibliography-content">{html}</div>'

    return html


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


def _convert_paragraphs(html: str) -> str:
    """Wrap non-HTML lines in paragraph tags"""
    lines = html.split('\n')
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
            continue

        # Skip lines that are already HTML tags
        if (stripped.startswith('<') and stripped.endswith('>')) or \
           stripped.startswith('</') or \
           '<h' in stripped or '<div' in stripped or '<ul' in stripped or \
           '<ol' in stripped or '<li' in stripped or '<table' in stripped or \
           '</div>' in stripped or '</ul>' in stripped or '</ol>' in stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
            continue

        # Regular text line - wrap in paragraph
        if not in_paragraph:
            result.append('<p>' + line)
            in_paragraph = True
        else:
            result.append(line)

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


DEFAULT_TEMPLATE = Path(__file__).parent.parent / 'templates' / 'mckinsey_report_template.html'

MERMAID_SCRIPT = (
    '\n<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
    '\n<script>mermaid.initialize({ startOnLoad: true });</script>\n'
)


def _guess_title(markdown_text: str) -> str:
    """First `# H1` heading, or `## Executive Summary`'s parent doc has none,
    so fall back to a generic label rather than leaving `{{TITLE}}` unfilled.
    """
    m = re.search(r'^# (.+)$', markdown_text, re.MULTILINE)
    return m.group(1).strip() if m else 'Research Report'


def render_full_report_html(
    markdown_text: str,
    template_text: str,
    *,
    title: str = None,
    date: str = '',
    source_count: str = '',
    metrics_html: str = '',
) -> str:
    """Convert `markdown_text` and splice it into the McKinsey report
    template, returning a complete, ready-to-save HTML document.

    This is the piece `reference/html-generation.md` describes ("Step 3
    convert MD to HTML" -> "Step 5 replace template placeholders") but that
    previously had no corresponding code — `main()` only ever printed a
    1000-character preview of the converted content and never touched the
    template or wrote a file.
    """
    # Re-run the same fence extraction convert_markdown_to_html() does
    # internally, purely to inspect whether a mermaid block is present (for
    # the mermaid.js injection below) without duplicating conversion logic.
    _, code_blocks = _extract_fenced_code_blocks(markdown_text)
    content_html, bibliography_html = convert_markdown_to_html(markdown_text)

    html = template_text
    html = html.replace('{{TITLE}}', title if title is not None else _guess_title(markdown_text))
    html = html.replace('{{DATE}}', date)
    html = html.replace('{{SOURCE_COUNT}}', str(source_count))
    html = html.replace('{{METRICS_DASHBOARD}}', metrics_html)
    html = html.replace('{{CONTENT}}', content_html)
    html = html.replace('{{BIBLIOGRAPHY}}', bibliography_html)

    if has_mermaid_block(code_blocks) and '</body>' in html:
        html = html.replace('</body>', MERMAID_SCRIPT + '</body>')

    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert a deep-research markdown report to a complete HTML file.'
    )
    parser.add_argument('markdown_file', type=Path, help='Path to the source .md report')
    parser.add_argument(
        '--template', type=Path, default=DEFAULT_TEMPLATE,
        help=f'HTML template with {{{{PLACEHOLDER}}}} slots (default: {DEFAULT_TEMPLATE})',
    )
    parser.add_argument(
        '--out', type=Path, default=None,
        help='Output .html path (default: same name as markdown_file with .html extension)',
    )
    parser.add_argument('--title', default=None, help='Report title (default: first # heading)')
    parser.add_argument('--date', default='', help='Date string shown in the header')
    parser.add_argument('--source-count', default='', help='Source count shown in the header')
    parser.add_argument(
        '--preview', action='store_true',
        help='Print a short preview instead of writing a file (legacy debug mode)',
    )
    args = parser.parse_args()

    if not args.markdown_file.exists():
        print(f"Error: File {args.markdown_file} not found")
        raise SystemExit(1)

    markdown_text = args.markdown_file.read_text(encoding='utf-8')

    if args.preview:
        content_html, bib_html = convert_markdown_to_html(markdown_text)
        print("=== CONTENT HTML ===")
        print(content_html[:1000])
        print("\n=== BIBLIOGRAPHY HTML ===")
        print(bib_html[:500])
        return

    if not args.template.exists():
        print(f"Error: Template not found: {args.template}")
        raise SystemExit(1)

    template_text = args.template.read_text(encoding='utf-8')
    html = render_full_report_html(
        markdown_text, template_text,
        title=args.title, date=args.date, source_count=args.source_count,
    )

    out_path = args.out or args.markdown_file.with_suffix('.html')
    out_path.write_text(html, encoding='utf-8')
    print(f"Written: {out_path} ({len(html)} chars)")


if __name__ == "__main__":
    from _console import ensure_utf8_console
    ensure_utf8_console()
    main()
