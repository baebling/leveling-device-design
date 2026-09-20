import unittest

from calculations.revb_assembly_reaudit import run_audit


class RevBAssemblyReauditTests(unittest.TestCase):
    def test_reaudit_rejects_revb(self):
        audit = run_audit()
        self.assertFalse(audit["passes"])
        self.assertFalse(audit["fabrication_release"])
        self.assertFalse(audit["purchase_release"])

    def test_neutral_joint_axis_error_is_exposed(self):
        audit = run_audit()["joint_axis_alignment"]
        self.assertGreater(audit["neutral_maximum_error_deg"], 3.5)
        self.assertFalse(audit["passes"])

    def test_layout_is_not_mislabeled_as_120_degree_radial(self):
        audit = run_audit()["support_azimuth"]
        self.assertEqual(audit["lower"]["circular_gaps_deg"], (90.0, 90.0, 180.0))
        self.assertEqual(audit["upper"]["circular_gaps_deg"], (90.0, 90.0, 180.0))
        self.assertFalse(audit["passes"])

    def test_connector_fastener_axis_error_is_exposed(self):
        audit = run_audit()["connector_fastener_axes"]
        self.assertFalse(audit["lower_4035"]["passes"])
        self.assertFalse(audit["upper_DCB3025"]["passes"])


if __name__ == "__main__":
    unittest.main()
