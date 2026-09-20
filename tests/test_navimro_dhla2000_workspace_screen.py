import unittest

from calculations.navimro_dhla2000_workspace_screen import screen


class NavimroDhla2000WorkspaceScreenTest(unittest.TestCase):
    def test_selected_pin_lug_geometry_balances_end_reserves(self):
        selected = screen()
        a1 = screen("A1_PIN_END")
        a2 = screen("A2_PLATE_END")

        self.assertTrue(selected["passes_5_mm_planning_window"])
        self.assertTrue(a1["passes_5_mm_planning_window"])
        self.assertTrue(a2["passes_5_mm_planning_window"])
        self.assertAlmostEqual(a1["actuator_retracted_mm"], 255.0)
        self.assertAlmostEqual(a2["actuator_retracted_mm"], 265.0)
        self.assertAlmostEqual(selected["disconnected_collapsed_height_mm"], 270.0)
        self.assertGreater(selected["physical_retraction_margin_mm"], 18.0)
        self.assertGreater(selected["physical_extension_margin_mm"], 19.0)
        self.assertEqual(
            selected["selected_procurement_variant"], "PIN_LUG_END_ASSUMPTION"
        )


if __name__ == "__main__":
    unittest.main()
