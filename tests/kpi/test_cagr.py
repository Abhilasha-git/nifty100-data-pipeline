import unittest

from src.analytics.cagr import (
    cagr,
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


class TestCAGR(unittest.TestCase):

    def test_normal_cagr(self):
        value, flag = cagr(100, 200, 5)
        self.assertAlmostEqual(value, 14.87, places=2)
        self.assertIsNone(flag)

    def test_zero_base(self):
        value, flag = cagr(0, 100, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "ZERO_BASE")

    def test_turnaround(self):
        value, flag = cagr(-100, 100, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "TURNAROUND")

    def test_decline_to_loss(self):
        value, flag = cagr(100, -100, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "DECLINE_TO_LOSS")

    def test_both_negative(self):
        value, flag = cagr(-100, -50, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "BOTH_NEGATIVE")

    def test_insufficient_years(self):
        value, flag = cagr(100, 200, 0)
        self.assertIsNone(value)
        self.assertEqual(flag, "INSUFFICIENT")

    def test_revenue_cagr(self):
        value, flag = revenue_cagr(100, 200, 5)
        self.assertAlmostEqual(value, 14.87, places=2)
        self.assertIsNone(flag)

    def test_pat_cagr(self):
        value, flag = pat_cagr(100, 150, 5)
        self.assertAlmostEqual(value, 8.45, places=2)
        self.assertIsNone(flag)

    def test_eps_cagr(self):
        value, flag = eps_cagr(10, 20, 5)
        self.assertAlmostEqual(value, 14.87, places=2)
        self.assertIsNone(flag)

    def test_same_values(self):
        value, flag = cagr(100, 100, 5)
        self.assertAlmostEqual(value, 0.0, places=2)
        self.assertIsNone(flag)


if __name__ == "__main__":
    unittest.main()