import unittest

from src.analytics.cashflow_kpis import (
    capital_allocation_pattern
)


class TestCapitalAllocation(unittest.TestCase):

    def test_reinvestor(self):
        self.assertEqual(
            capital_allocation_pattern(10, -5, -2),
            "Reinvestor"
        )

    def test_shareholder_returns(self):
        self.assertEqual(
            capital_allocation_pattern(
                10,
                -5,
                -2,
                cfo_pat_ratio=1.2
            ),
            "Shareholder Returns"
        )

    def test_liquidating_assets(self):
        self.assertEqual(
            capital_allocation_pattern(
                10,
                5,
                -2
            ),
            "Liquidating Assets"
        )

    def test_distress(self):
        self.assertEqual(
            capital_allocation_pattern(
                -10,
                5,
                3
            ),
            "Distress Signal"
        )

    def test_growth_debt(self):
        self.assertEqual(
            capital_allocation_pattern(
                -10,
                -5,
                4
            ),
            "Growth Funded by Debt"
        )

    def test_cash_accumulator(self):
        self.assertEqual(
            capital_allocation_pattern(
                10,
                5,
                2
            ),
            "Cash Accumulator"
        )

    def test_pre_revenue(self):
        self.assertEqual(
            capital_allocation_pattern(
                -10,
                -5,
                -2
            ),
            "Pre-Revenue"
        )

    def test_mixed(self):
        self.assertEqual(
            capital_allocation_pattern(
                10,
                -5,
                2
            ),
            "Mixed"
        )


if __name__ == "__main__":
    unittest.main()