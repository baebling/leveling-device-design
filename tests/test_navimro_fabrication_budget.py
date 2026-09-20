import unittest

from calculations.navimro_fabrication_budget import budget_summary


class NavimroFabricationBudgetTests(unittest.TestCase):
    def test_plan_stays_below_user_cap(self):
        result = budget_summary()
        self.assertTrue(result["within_cap"])
        self.assertEqual(result["budget_cap_krw"], 4_000_000)
        self.assertGreaterEqual(result["headroom_krw"], 150_000)

    def test_all_bom_lines_have_prices(self):
        result = budget_summary()
        self.assertGreater(result["navimro_known_subtotal_krw"], 0)


if __name__ == "__main__":
    unittest.main()

