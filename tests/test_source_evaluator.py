#!/usr/bin/env python3
"""Regression tests for source_evaluator.py credibility scoring."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from source_evaluator import SourceEvaluator


class TestRecency(unittest.TestCase):
    """Recency must score tz-aware ISO dates, not fall through to the default."""

    def setUp(self):
        self.evaluator = SourceEvaluator()

    def _recency(self, date: str) -> float:
        return self.evaluator.evaluate_source(
            url='https://www.nature.com/x', title='T', publication_date=date
        ).recency

    def test_zulu_date_scores_recent(self):
        # Z-suffixed (tz-aware) date used to raise inside the try and return 50.0
        self.assertGreaterEqual(self._recency('2025-10-15T00:00:00Z'), 85.0)

    def test_naive_date_still_scores_recent(self):
        self.assertGreaterEqual(self._recency('2025-10-15'), 85.0)

    def test_missing_date_returns_default(self):
        score = self.evaluator.evaluate_source(url='https://x.com', title='T').recency
        self.assertEqual(score, 50.0)


class TestDomainExtraction(unittest.TestCase):
    """www prefix must be stripped, but only as a prefix."""

    def setUp(self):
        self.evaluator = SourceEvaluator()

    def test_strips_www_prefix(self):
        self.assertEqual(self.evaluator._extract_domain('https://www.nature.com/x'), 'nature.com')

    def test_keeps_www_inside_domain(self):
        self.assertEqual(self.evaluator._extract_domain('https://api.www.gov'), 'api.www.gov')

    def test_does_not_corrupt_quadruple_w(self):
        self.assertEqual(self.evaluator._extract_domain('https://wwww.test.com'), 'wwww.test.com')


class TestExpertiseAuthor(unittest.TestCase):
    """Author credentials raise expertise without shadowing other params."""

    def setUp(self):
        self.evaluator = SourceEvaluator()

    def test_credential_boosts_expertise(self):
        base = self.evaluator.evaluate_source(url='https://x.com', title='Study').expertise
        with_cred = self.evaluator.evaluate_source(
            url='https://x.com', title='Study', author='Dr. Smith'
        ).expertise
        self.assertGreater(with_cred, base)


if __name__ == '__main__':
    unittest.main()
