#!/usr/bin/env python3
"""
Citation Manager — stable source identity and run manifest management.

CLI subcommands:
  init-run             Create run_manifest.json + empty artifact JSONL files
  register-source      Append a source to sources.jsonl, return source_id
  assign-display-numbers  Generate stable_id -> display_number mapping
  export-bibliography   Render bibliography from sources.jsonl

Source identity:
  source_id = sha256(canonical_locator)[:16]
  canonical_locator = doi:..., arxiv:..., or normalized URL

All state is append-only JSONL. No mutable citation numbers in state files.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse


# ---------------------------------------------------------------------------
# Canonical locator normalization
# ---------------------------------------------------------------------------

DOI_RE = re.compile(r'(?:https?://(?:dx\.)?doi\.org/|doi:)(10\.\d{4,}/\S+)', re.IGNORECASE)
ARXIV_RE = re.compile(r'(?:https?://arxiv\.org/abs/|arxiv:)(\d{4}\.\d{4,}(?:v\d+)?)', re.IGNORECASE)

# URL query params that are tracking noise, not content identifiers
TRACKING_PARAMS = frozenset([
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'ref', 'source', 'fbclid', 'gclid', 'mc_cid', 'mc_eid',
])


def canonicalize_locator(raw_url: str) -> str:
    """Derive a canonical locator from a raw URL or identifier string.

    Priority: DOI > arXiv > normalized URL.
    """
    # DOI
    m = DOI_RE.search(raw_url)
    if m:
        return f'doi:{m.group(1).rstrip(".")}'

    # arXiv
    m = ARXIV_RE.search(raw_url)
    if m:
        return f'arxiv:{m.group(1)}'

    # Normalized URL: lowercase scheme+host, strip fragment and tracking params
    parsed = urlparse(raw_url)
    scheme = (parsed.scheme or 'https').lower()
    host = (parsed.hostname or '').lower()
    path = parsed.path.rstrip('/')
    # Filter query params
    if parsed.query:
        pairs = []
        for part in parsed.query.split('&'):
            kv = part.split('=', 1)
            if kv[0].lower() not in TRACKING_PARAMS:
                pairs.append(part)
        query = '&'.join(sorted(pairs))
    else:
        query = ''
    return urlunparse((scheme, host, path, '', query, ''))


def compute_source_id(canonical_locator: str) -> str:
    """sha256(canonical_locator)[:16] hex."""
    return hashlib.sha256(canonical_locator.encode('utf-8')).hexdigest()[:16]


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------

def append_jsonl(path: str, obj: dict) -> None:
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def read_jsonl(path: str) -> list[dict]:
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_init_run(args: argparse.Namespace) -> None:
    """Create run_manifest.json and empty JSONL artifact files."""
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    artifact_paths = {
        'sources': 'sources.jsonl',
        'evidence': 'evidence.jsonl',
        'claims': 'claims.jsonl',
        'report': 'report.md',
    }

    manifest = {
        'version': '3.0.0',
        'query': args.query or '',
        'mode': args.mode,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'finished_at': None,
        'assumptions': [],
        'provider_config': {
            'primary': 'search-cli',
            'scholarly': None,
        },
        'report_dir': out_dir,
        'artifact_paths': artifact_paths,
        'continuation': None,
    }

    manifest_path = os.path.join(out_dir, 'run_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # Create empty artifact files
    for name in ('sources', 'evidence', 'claims'):
        p = os.path.join(out_dir, artifact_paths[name])
        if not os.path.exists(p):
            open(p, 'w', encoding='utf-8').close()

    print(json.dumps({'status': 'ok', 'manifest': manifest_path, 'dir': out_dir}))


def cmd_register_source(args: argparse.Namespace) -> None:
    """Register a source, append to sources.jsonl, print source_id."""
    data = json.loads(args.json)
    raw_url = data.get('raw_url', data.get('url', ''))
    if not raw_url:
        print(json.dumps({'error': 'raw_url is required'}), file=sys.stderr)
        sys.exit(1)

    canonical = data.get('canonical_locator') or canonicalize_locator(raw_url)
    source_id = compute_source_id(canonical)

    sources_path = os.path.join(args.dir, 'sources.jsonl')

    # Check for duplicate
    existing = read_jsonl(sources_path)
    for row in existing:
        if row.get('source_id') == source_id:
            print(json.dumps({
                'status': 'duplicate',
                'source_id': source_id,
                'canonical_locator': canonical,
            }))
            return

    source = {
        'source_id': source_id,
        'canonical_locator': canonical,
        'raw_url': raw_url,
        'title': data.get('title', ''),
        'authors': data.get('authors'),
        'year': data.get('year'),
        'source_type': data.get('source_type', 'web'),
        'metadata_status': data.get('metadata_status', 'unverified'),
        'registered_at': datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(sources_path, source)
    print(json.dumps({
        'status': 'registered',
        'source_id': source_id,
        'canonical_locator': canonical,
    }))


def cmd_assign_display_numbers(args: argparse.Namespace) -> None:
    """Read sources.jsonl, assign stable display numbers in registration order."""
    sources_path = os.path.join(args.dir, 'sources.jsonl')
    sources = read_jsonl(sources_path)

    mapping = {}
    for i, src in enumerate(sources, 1):
        sid = src['source_id']
        if sid not in mapping:
            mapping[sid] = i

    print(json.dumps(mapping, indent=2))


def cmd_export_bibliography(args: argparse.Namespace) -> None:
    """Generate bibliography from sources.jsonl."""
    sources_path = os.path.join(args.dir, 'sources.jsonl')
    sources = read_jsonl(sources_path)

    # Deduplicate by source_id, preserve order
    seen = set()
    unique = []
    for src in sources:
        if src['source_id'] not in seen:
            seen.add(src['source_id'])
            unique.append(src)

    style = args.style

    if style == 'markdown':
        lines = ['## Bibliography', '']
        for i, src in enumerate(unique, 1):
            author_str = ''
            if src.get('authors'):
                authors = src['authors']
                if len(authors) == 1:
                    author_str = f'{authors[0]}. '
                elif len(authors) == 2:
                    author_str = f'{authors[0]} & {authors[1]}. '
                else:
                    author_str = f'{authors[0]} et al. '

            year_str = f'({src["year"]})' if src.get('year') else '(n.d.)'
            title = src.get('title', 'Untitled')
            url = src.get('raw_url', '')
            lines.append(f'[{i}] {author_str}{year_str}. [{title}]({url})')
        print('\n'.join(lines))

    elif style == 'json':
        out = []
        for i, src in enumerate(unique, 1):
            out.append({
                'display_number': i,
                'source_id': src['source_id'],
                'canonical_locator': src['canonical_locator'],
                'title': src.get('title', ''),
                'authors': src.get('authors'),
                'year': src.get('year'),
                'raw_url': src.get('raw_url', ''),
            })
        print(json.dumps(out, indent=2, ensure_ascii=False))

    else:
        print(f'Unknown style: {style}', file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='citation_manager',
        description='Stable source identity and run manifest management for deep-research v3.0',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # init-run
    p_init = sub.add_parser('init-run', help='Create run manifest and empty artifact files')
    p_init.add_argument('--out-dir', required=True, help='Output directory for the research run')
    p_init.add_argument('--query', default='', help='Original research question')
    p_init.add_argument('--mode', default='standard', choices=['quick', 'standard', 'deep', 'ultradeep'])

    # register-source
    p_reg = sub.add_parser('register-source', help='Register a source and return its stable ID')
    p_reg.add_argument('--json', required=True, help='JSON object with at least raw_url and title')
    p_reg.add_argument('--dir', required=True, help='Run directory containing sources.jsonl')

    # assign-display-numbers
    p_num = sub.add_parser('assign-display-numbers', help='Map stable source IDs to display numbers')
    p_num.add_argument('--dir', required=True, help='Run directory containing sources.jsonl')

    # export-bibliography
    p_bib = sub.add_parser('export-bibliography', help='Generate bibliography from sources')
    p_bib.add_argument('--dir', required=True, help='Run directory containing sources.jsonl')
    p_bib.add_argument('--style', default='markdown', choices=['markdown', 'json'])

    args = parser.parse_args()

    dispatch = {
        'init-run': cmd_init_run,
        'register-source': cmd_register_source,
        'assign-display-numbers': cmd_assign_display_numbers,
        'export-bibliography': cmd_export_bibliography,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    from _console import ensure_utf8_console
    ensure_utf8_console()
    main()
