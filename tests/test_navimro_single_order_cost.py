import unittest

from calculations.navimro_single_order_cost import summarize_bom


class NavimroSingleOrderCostTest(unittest.TestCase):
    def test_bom_subtotals_and_required_rows(self):
        result = summarize_bom()
        self.assertGreaterEqual(result["line_count"], 40)
        self.assertGreater(result["priced_total_krw_vat_included"], 2_000_000)
        self.assertEqual(result["unknown_price_lines"], ())
        self.assertEqual(result["priced_total_krw_vat_included"], 2_687_993)
        self.assertIn("M001", result["hold_lines"])


if __name__ == "__main__":
    unittest.main()
