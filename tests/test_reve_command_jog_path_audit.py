import json
import tempfile
import unittest
from pathlib import Path


class ReveCommandJogPathAuditTests(unittest.TestCase):
    def test_default_home_eligible_paths_stay_inside_finite_limits(self):
        from calculations.reve_command_jog_path_audit import (
            audit_home_eligible_command_jog_paths,
        )

        result = audit_home_eligible_command_jog_paths()

        self.assertEqual(result["dense_pose_count"], 1859)
        self.assertEqual(result["park_segment_count"], 1859)
        self.assertEqual(result["jog_segment_count"], 5122)
        self.assertGreater(result["sampled_state_count"], 7000)
        self.assertGreaterEqual(result["minimum_pin_mm"], 210.0)
        self.assertLessEqual(result["maximum_pin_mm"], 280.0)
        self.assertLessEqual(result["maximum_tilt_deg"], 5.0)
        self.assertLessEqual(result["maximum_phs_articulation_deg"], 13.0)
        self.assertTrue(result["finite_screen_pass"])
        self.assertFalse(result["release_ready"])

    def test_command_jog_json_preserves_nonrelease_scope(self):
        from calculations.reve_command_jog_path_audit import (
            write_command_jog_audit_json,
        )

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "command_jog.json"
            payload = write_command_jog_audit_json(destination)
            loaded = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(payload, loaded)
        self.assertEqual(
            loaded["scope"],
            "DENSE_GRID_TO_HOME_PARK_AND_DENSE_ADJACENT_JOG_SEGMENTS",
        )
        self.assertFalse(loaded["continuous_workspace_proven"])
        self.assertFalse(loaded["full_path_cad_collision_audited"])


if __name__ == "__main__":
    unittest.main()
