#!/usr/bin/env python3
"""
Atomic Claim Extractor — decomposes report sections into typed claims.

CLI subcommands:
  extract      Parse a markdown report into atomic claims (claims.jsonl)
  add          Manually add a single claim
  list         List claims, optionally filtered by section or type
  stats        Show claim statistics (counts by type/status)

Claim identity:
  claim_id = sha256(section_id + normalized_text)[:16]

Claim types (per GPT Pro's refinement of Codex's proposal):
  - factual: hard-fails on lack of support
  - synthesis: needs traceability, softer threshold
  - recommendation: needs traceability, softer threshold
  - speculation: labeled, no support gate
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Claim ID computation
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r'\s+')


def normalize_text(text: str) -> str:
    """Normalize for stable hashing."""
    return _WHITESPACE_RE.sub(' ', text.strip()).lower()


def compute_claim_id(section_id: str, text: str) -> str:
    """sha256(section_id + normalized_text)[:16] hex."""
    payload = section_id + normalize_text(text)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


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
# Report parsing helpers
# ---------------------------------------------------------------------------

# Section header patterns
SECTION_PATTERNS = [
    (re.compile(r'^##\s+Executive\s+Summary', re.I), 'executive_summary'),
    (re.compile(r'^##\s+Introduction', re.I), 'introduction'),
    (re.compile(r'^##\s+Finding\s+(\d+)', re.I), lambda m: f'finding_{m.group(1)}'),
    (re.compile(r'^##\s+Synthesis', re.I), 'synthesis'),
    (re.compile(r'^##\s+Limitations', re.I), 'limitations'),
    (re.compile(r'^##\s+Recommendations', re.I), 'recommendations'),
    (re.compile(r'^##\s+Conclusion', re.I), 'conclusion'),
    (re.compile(r'^##\s+(.+)', re.I), lambda m: re.sub(r'\W+', '_', m.group(1).strip().lower())[:30]),
]

# Citation pattern [N] or [N, M]
CITATION_RE = re.compile(r'\[(\d+(?:,\s*\d+)*)\]')

# Sentence splitting (basic but handles abbreviations)
SENTENCE_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')


def classify_claim(text: str, section_id: str) -> str:
    """Heuristic claim type classification."""
    lower = text.lower()

    # Recommendation indicators
    if any(w in lower for w in ['should', 'recommend', 'suggest', 'advise', 'consider']):
        if section_id == 'recommendations':
            return 'recommendation'
        return 'recommendation'

    # Speculation indicators
    if any(w in lower for w in ['might', 'could potentially', 'it is possible', 'may eventually',
                                 'hypothetically', 'speculatively']):
        return 'speculation'

    # Synthesis indicators (often in synthesis/conclusion sections)
    if section_id in ('synthesis', 'conclusion', 'limitations'):
        if any(w in lower for w in ['overall', 'taken together', 'collectively',
                                     'the evidence suggests', 'this implies']):
            return 'synthesis'

    # Default: factual
    return 'factual'


def parse_sections(markdown: str) -> list[tuple[str, str]]:
    """Parse markdown into (section_id, content) pairs."""
    lines = markdown.split('\n')
    sections = []
    current_id = 'preamble'
    current_lines = []

    for line in lines:
        matched = False
        for pattern, id_or_fn in SECTION_PATTERNS:
            m = pattern.match(line)
            if m:
                if current_lines:
                    sections.append((current_id, '\n'.join(current_lines)))
                current_id = id_or_fn(m) if callable(id_or_fn) else id_or_fn
                current_lines = []
                matched = True
                break
        if not matched:
            current_lines.append(line)

    if current_lines:
        sections.append((current_id, '\n'.join(current_lines)))

    return sections


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences, filtering noise."""
    # Remove markdown formatting noise
    text = re.sub(r'^[-*]\s+', '', text, flags=re.M)  # bullet points
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic

    sentences = SENTENCE_RE.split(text)
    result = []
    for s in sentences:
        s = s.strip()
        # Filter out very short fragments, headings, empty lines
        if len(s) > 30 and not s.startswith('#') and not s.startswith('|'):
            result.append(s)
    return result


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_extract(args: argparse.Namespace) -> None:
    """Extract atomic claims from a markdown report."""
    report_path = args.report
    if not os.path.exists(report_path):
        print(json.dumps({'error': f'Report not found: {report_path}'}), file=sys.stderr)
        sys.exit(1)

    with open(report_path, encoding='utf-8') as f:
        markdown = f.read()

    claims_path = os.path.join(args.dir, 'claims.jsonl')
    existing_ids = {r['claim_id'] for r in read_jsonl(claims_path)}

    sections = parse_sections(markdown)
    added = 0
    skipped = 0

    for section_id, content in sections:
        if section_id == 'preamble':
            continue
        sentences = extract_sentences(content)
        for sentence in sentences:
            claim_id = compute_claim_id(section_id, sentence)
            if claim_id in existing_ids:
                skipped += 1
                continue

            # Extract citation numbers from sentence
            citation_nums = []
            for m in CITATION_RE.finditer(sentence):
                nums = [int(n.strip()) for n in m.group(1).split(',')]
                citation_nums.extend(nums)

            claim = {
                'claim_id': claim_id,
                'section_id': section_id,
                'text': sentence,
                'claim_type': classify_claim(sentence, section_id),
                'cited_source_ids': [],  # Populated by linking step
                'evidence_ids': [],  # Populated by verify_claim_support
                'support_status': 'unverified',
                'extracted_at': datetime.now(timezone.utc).isoformat(),
                '_citation_numbers': citation_nums,  # Temporary, for linking
            }
            append_jsonl(claims_path, claim)
            existing_ids.add(claim_id)
            added += 1

    print(json.dumps({
        'status': 'ok',
        'claims_added': added,
        'claims_skipped': skipped,
        'total_claims': len(existing_ids),
    }))


def cmd_add(args: argparse.Namespace) -> None:
    """Manually add a single claim."""
    data = json.loads(args.json)
    section_id = data.get('section_id', 'unknown')
    text = data.get('text', '')
    if not text:
        print(json.dumps({'error': 'text is required'}), file=sys.stderr)
        sys.exit(1)

    claim_id = compute_claim_id(section_id, text)
    claims_path = os.path.join(args.dir, 'claims.jsonl')

    existing = read_jsonl(claims_path)
    for row in existing:
        if row.get('claim_id') == claim_id:
            print(json.dumps({'status': 'duplicate', 'claim_id': claim_id}))
            return

    valid_types = {'factual', 'synthesis', 'recommendation', 'speculation'}
    claim_type = data.get('claim_type', 'factual')
    if claim_type not in valid_types:
        claim_type = 'factual'

    claim = {
        'claim_id': claim_id,
        'section_id': section_id,
        'text': text,
        'claim_type': claim_type,
        'cited_source_ids': data.get('cited_source_ids', []),
        'evidence_ids': data.get('evidence_ids', []),
        'support_status': 'unverified',
        'extracted_at': datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(claims_path, claim)
    print(json.dumps({'status': 'added', 'claim_id': claim_id}))


def cmd_list(args: argparse.Namespace) -> None:
    """List claims with optional filters."""
    claims_path = os.path.join(args.dir, 'claims.jsonl')
    rows = read_jsonl(claims_path)

    if args.section:
        rows = [r for r in rows if r.get('section_id') == args.section]
    if args.type:
        rows = [r for r in rows if r.get('claim_type') == args.type]
    if args.status:
        rows = [r for r in rows if r.get('support_status') == args.status]

    # Deduplicate
    seen = set()
    unique = []
    for r in rows:
        cid = r.get('claim_id')
        if cid not in seen:
            seen.add(cid)
            unique.append(r)

    print(json.dumps({'count': len(unique), 'claims': unique}, indent=2, ensure_ascii=False))


def cmd_stats(args: argparse.Namespace) -> None:
    """Show claim statistics."""
    claims_path = os.path.join(args.dir, 'claims.jsonl')
    rows = read_jsonl(claims_path)

    # Deduplicate
    seen = set()
    unique = []
    for r in rows:
        cid = r.get('claim_id')
        if cid not in seen:
            seen.add(cid)
            unique.append(r)

    by_type = {}
    by_status = {}
    by_section = {}
    for r in unique:
        t = r.get('claim_type', 'unknown')
        s = r.get('support_status', 'unknown')
        sec = r.get('section_id', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
        by_status[s] = by_status.get(s, 0) + 1
        by_section[sec] = by_section.get(sec, 0) + 1

    print(json.dumps({
        'total': len(unique),
        'by_type': by_type,
        'by_status': by_status,
        'by_section': by_section,
    }, indent=2))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='extract_claims',
        description='Atomic claim extraction and ledger for deep-research v3.0',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # extract
    p_ext = sub.add_parser('extract', help='Extract claims from markdown report')
    p_ext.add_argument('--report', required=True, help='Path to report.md')
    p_ext.add_argument('--dir', required=True, help='Run directory containing claims.jsonl')

    # add
    p_add = sub.add_parser('add', help='Manually add a single claim')
    p_add.add_argument('--json', required=True, help='JSON with section_id, text, claim_type')
    p_add.add_argument('--dir', required=True, help='Run directory')

    # list
    p_list = sub.add_parser('list', help='List claims')
    p_list.add_argument('--dir', required=True, help='Run directory')
    p_list.add_argument('--section', default=None, help='Filter by section_id')
    p_list.add_argument('--type', default=None, help='Filter by claim_type')
    p_list.add_argument('--status', default=None, help='Filter by support_status')

    # stats
    p_stats = sub.add_parser('stats', help='Claim statistics')
    p_stats.add_argument('--dir', required=True, help='Run directory')

    args = parser.parse_args()
    dispatch = {
        'extract': cmd_extract,
        'add': cmd_add,
        'list': cmd_list,
        'stats': cmd_stats,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    from _console import ensure_utf8_console
    ensure_utf8_console()
    main()
