import unittest

from src.analytics.ratios import *


class TestProfitability(unittest.TestCase):

    def test_net_profit_margin(self):
        self.assertAlmostEqual(
            net_profit_margin(100, 1000),
            10
        )

    def test_zero_sales(self):
        self.assertIsNone(
            net_profit_margin(100, 0)
        )

    def test_operating_margin(self):
        self.assertAlmostEqual(
            operating_profit_margin(250, 1000),
            25
        )

    def test_opm_match(self):
        self.assertTrue(
            opm_matches_source(
                250,
                1000,
                25
            )
        )

    def test_opm_mismatch(self):
        self.assertFalse(
            opm_matches_source(
                250,
                1000,
                20
            )
        )

    def test_roe(self):
        self.assertAlmostEqual(
            return_on_equity(
                100,
                400,
                600
            ),
            10
        )

    def test_negative_equity(self):
        self.assertIsNone(
            return_on_equity(
                100,
                -100,
                50
            )
        )

    def test_roa(self):
        self.assertAlmostEqual(
            return_on_assets(
                100,
                500
            ),
            20
        )


if __name__ == "__main__":
    unittest.main()