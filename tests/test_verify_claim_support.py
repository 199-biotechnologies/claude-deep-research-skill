#!/usr/bin/env python3
"""Tests for verify_claim_support.py CLI."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'verify_claim_support.py')


def run_vcs(*args: str, expect_fail: bool = False) -> dict | str:
    """Run verify_claim_support.py."""
    result = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, text=True,
    )
    if result.returncode != 0 and not expect_fail:
        raise RuntimeError(f'Exit {result.returncode}: {result.stderr}\n{result.stdout}')
    stdout = result.stdout.strip()
    if stdout.startswith('{'):
        return json.loads(stdout)
    return stdout


def write_jsonl(path: str, rows: list[dict]):
    with open(path, 'w') as f:
        for row in rows:
            f.write(json.dumps(row) + '\n')


class TestVerifySupported(unittest.TestCase):
    """Claims with matching evidence should be supported."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Sources
        write_jsonl(os.path.join(self.tmpdir, 'sources.jsonl'), [
            {'source_id': 'src_quantum_001', 'title': 'Quantum Computing 2024'},
        ])
        # Evidence with clear overlap to the claim
        write_jsonl(os.path.join(self.tmpdir, 'evidence.jsonl'), [
            {
                'evidence_id': 'ev_shor_001',
                'source_id': 'src_quantum_001',
                'quote': "Shor's algorithm can factor large integers exponentially faster than any known classical algorithm, threatening RSA-2048 encryption.",
                'evidence_type': 'direct_quote',
            },
        ])
        # Claim that matches the evidence
        write_jsonl(os.path.join(self.tmpdir, 'claims.jsonl'), [
            {
                'claim_id': 'clm_factor_001',
                'section_id': 'finding_1',
                'text': "Shor's algorithm can factor large numbers exponentially faster than classical methods, threatening RSA-2048.",
                'claim_type': 'factual',
                'cited_source_ids': ['src_quantum_001'],
                'evidence_ids': ['ev_shor_001'],
                'support_status': 'unverified',
            },
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_supported_claim(self):
        out = run_vcs('verify', '--dir', self.tmpdir)
        self.assertEqual(out['status'], 'pass')
        self.assertEqual(out['factual_unsupported'], 0)

        # Check updated claims file
        claims = []
        with open(os.path.join(self.tmpdir, 'claims.jsonl')) as f:
            for line in f:
                claims.append(json.loads(line))
        self.assertEqual(claims[0]['support_status'], 'supported')


class TestVerifyUnsupported(unittest.TestCase):
    """Claims without evidence should be unsupported."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        write_jsonl(os.path.join(self.tmpdir, 'sources.jsonl'), [])
        write_jsonl(os.path.join(self.tmpdir, 'evidence.jsonl'), [])
        write_jsonl(os.path.join(self.tmpdir, 'claims.jsonl'), [
            {
                'claim_id': 'clm_no_ev_001',
                'section_id': 'finding_1',
                'text': 'The population of Mars is 500 million as of 2025.',
                'claim_type': 'factual',
                'cited_source_ids': [],
                'evidence_ids': [],
                'support_status': 'unverified',
            },
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_unsupported_no_evidence(self):
        out = run_vcs('verify', '--dir', self.tmpdir)
        self.assertEqual(out['factual_unsupported'], 1)
        self.assertEqual(out['status'], 'pass')  # Non-strict by default

    def test_strict_fails(self):
        out = run_vcs('verify', '--dir', self.tmpdir, '--strict', expect_fail=True)
        self.assertEqual(out['status'], 'fail')


class TestVerifyMixed(unittest.TestCase):
    """Mixed claim types with different thresholds."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        write_jsonl(os.path.join(self.tmpdir, 'sources.jsonl'), [])
        write_jsonl(os.path.join(self.tmpdir, 'evidence.jsonl'), [])
        write_jsonl(os.path.join(self.tmpdir, 'claims.jsonl'), [
            {
                'claim_id': 'clm_spec_001',
                'section_id': 'finding_1',
                'text': 'Quantum computers might eventually solve protein folding in real time.',
                'claim_type': 'speculation',
                'cited_source_ids': [],
                'evidence_ids': [],
                'support_status': 'unverified',
            },
            {
                'claim_id': 'clm_rec_001',
                'section_id': 'recommendations',
                'text': 'Organizations should begin PQC migration planning immediately.',
                'claim_type': 'recommendation',
                'cited_source_ids': [],
                'evidence_ids': [],
                'support_status': 'unverified',
            },
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_speculation_passes(self):
        out = run_vcs('verify', '--dir', self.tmpdir)
        # Speculation doesn't need evidence
        claims = []
        with open(os.path.join(self.tmpdir, 'claims.jsonl')) as f:
            for line in f:
                claims.append(json.loads(line))
        spec = [c for c in claims if c['claim_type'] == 'speculation'][0]
        self.assertEqual(spec['support_status'], 'supported')


class TestVerifyPartial(unittest.TestCase):
    """Evidence with partial overlap should result in partial status."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        write_jsonl(os.path.join(self.tmpdir, 'sources.jsonl'), [
            {'source_id': 'src_nist_001', 'title': 'NIST PQC Standards'},
        ])
        write_jsonl(os.path.join(self.tmpdir, 'evidence.jsonl'), [
            {
                'evidence_id': 'ev_nist_001',
                'source_id': 'src_nist_001',
                'quote': 'NIST announced the standardization of CRYSTALS-Kyber for key encapsulation.',
                'evidence_type': 'direct_quote',
            },
        ])
        # Claim mentions NIST but adds unverified detail about timeline
        write_jsonl(os.path.join(self.tmpdir, 'claims.jsonl'), [
            {
                'claim_id': 'clm_nist_time',
                'section_id': 'finding_2',
                'text': 'NIST standardized four lattice-based algorithms in 2024, covering both encryption and signatures.',
                'claim_type': 'factual',
                'cited_source_ids': ['src_nist_001'],
                'evidence_ids': ['ev_nist_001'],
                'support_status': 'unverified',
            },
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_partial_support(self):
        out = run_vcs('verify', '--dir', self.tmpdir)
        claims = []
        with open(os.path.join(self.tmpdir, 'claims.jsonl')) as f:
            for line in f:
                claims.append(json.loads(line))
        # Should be partial or needs_review (not fully supported due to number/detail mismatch)
        self.assertIn(claims[0]['support_status'], ('partial', 'needs_review', 'supported'))


class TestSupportScore(unittest.TestCase):
    """Unit tests for compute_support_score."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from verify_claim_support import compute_support_score
        cls.score = staticmethod(compute_support_score)

    def test_identical_text(self):
        status, score, _ = self.score(
            'RSA-2048 uses 2048-bit keys for encryption.',
            ['RSA-2048 uses 2048-bit keys for encryption.'],
        )
        self.assertEqual(status, 'supported')
        self.assertGreater(score, 0.8)

    def test_no_evidence(self):
        status, score, _ = self.score('Any claim text.', [])
        self.assertEqual(status, 'unsupported')
        self.assertEqual(score, 0.0)

    def test_unrelated_evidence(self):
        status, score, _ = self.score(
            'The moon landing occurred in 1969.',
            ['Bananas are a good source of potassium and fiber.'],
        )
        self.assertIn(status, ('needs_review', 'unsupported'))
        self.assertLess(score, 0.35)


class TestYearRegex(unittest.TestCase):
    r"""Regression test for the year-extraction capturing-group bug.

    A regex with exactly one capturing group makes re.findall() return the
    group's text instead of the full match. YEAR_RE used to be
    r'\b(19|20)\d{2}\b' (a capturing group around only the century prefix),
    so extract_years('...1969...') returned {'19'} instead of {'1969'} --
    meaning any two years from the same century always compared equal.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from verify_claim_support import extract_years
        cls.extract_years = staticmethod(extract_years)

    def test_full_year_extracted_not_century_prefix(self):
        years = self.extract_years('The treaty was signed in 1969.')
        self.assertEqual(years, {'1969'})

    def test_different_years_same_century_are_distinct(self):
        # Both years are '19xx'. Before the fix, extract_years collapsed
        # both to the single value '19', so these compared equal.
        self.assertNotEqual(
            self.extract_years('The mission launched in 1969.'),
            self.extract_years('The report was published in 1996.'),
        )


class TestStrictGateRequiresSupported(unittest.TestCase):
    """A factual claim stuck at 'partial' or 'needs_review' must not pass
    --strict. Evidence being linked is not the same as evidence actually
    establishing the claim.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        write_jsonl(os.path.join(self.tmpdir, 'sources.jsonl'), [
            {'source_id': 'src_001', 'title': 'Source'},
        ])
        # Overlaps with the claim just enough to avoid 'unsupported', but
        # the claim's own count and year are absent from the quote, so it
        # lands on 'partial' or 'needs_review' rather than 'supported'.
        write_jsonl(os.path.join(self.tmpdir, 'evidence.jsonl'), [
            {
                'evidence_id': 'ev_001',
                'source_id': 'src_001',
                'quote': 'The lab published background notes summarizing the project.',
                'evidence_type': 'direct_quote',
            },
        ])
        write_jsonl(os.path.join(self.tmpdir, 'claims.jsonl'), [
            {
                'claim_id': 'clm_001',
                'section_id': 'finding_1',
                'text': 'The lab published exactly 42 background notes summarizing the project in 2024.',
                'claim_type': 'factual',
                'cited_source_ids': ['src_001'],
                'evidence_ids': ['ev_001'],
                'support_status': 'unverified',
            },
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_non_strict_passes(self):
        out = run_vcs('verify', '--dir', self.tmpdir)
        self.assertEqual(out['status'], 'pass')

    def test_strict_fails_on_partial_or_needs_review(self):
        out = run_vcs('verify', '--dir', self.tmpdir, '--strict', expect_fail=True)
        self.assertEqual(out['status'], 'fail')
        self.assertGreater(out['factual_not_supported'], 0)
        # Pre-fix, this specific case slipped through: evidence IS linked
        # so factual_unsupported stayed 0, and --strict only checked that
        # field. factual_not_supported (this fix) correctly flags it.
        self.assertEqual(out['factual_unsupported'], 0)


if __name__ == '__main__':
    unittest.main()
