import unittest

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage,
    icr_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover
)


class TestLeverage(unittest.TestCase):

    def test_debt_to_equity_normal(self):
        self.assertEqual(
            debt_to_equity(200, 100, 100),
            1
        )

    def test_debt_to_equity_debt_free(self):
        self.assertEqual(
            debt_to_equity(0, 100, 100),
            0
        )

    def test_debt_to_equity_negative_equity(self):
        self.assertIsNone(
            debt_to_equity(100, -100, 0)
        )

    def test_high_leverage_flag(self):
        self.assertTrue(
            high_leverage_flag(6)
        )

    def test_interest_coverage(self):
        self.assertEqual(
            interest_coverage(100, 20, 20),
            6
        )

    def test_interest_coverage_interest_zero(self):
        self.assertIsNone(
            interest_coverage(100, 20, 0)
        )

    def test_icr_label(self):
        self.assertEqual(
            icr_label(0),
            "Debt Free"
        )

    def test_asset_turnover(self):
        self.assertEqual(
            asset_turnover(500, 250),
            2
        )


if __name__ == "__main__":
    unittest.main()