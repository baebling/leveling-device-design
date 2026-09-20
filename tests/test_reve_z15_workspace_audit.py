import json
import tempfile
import unittest
from pathlib import Path


class ReveZ15WorkspaceAuditTests(unittest.TestCase):
    def test_required_grid_and_kinematics_are_screened(self):
        from calculations.reve_z15_workspace_audit import (
            PHYSICAL_Z_GRID_MM,
            PITCH_GRID_DEG,
            ROLL_GRID_DEG,
            audit_reve_z15_workspace,
        )

        calls = []

        def fake_collision(pose):
            calls.append(pose)
            return {"pose": pose.label, "maximum_volume_mm3": 0.0, "passes": True}

        progress = []
        result = audit_reve_z15_workspace(
            collision_check=fake_collision, progress_callback=progress.append
        )

        self.assertIn(15.0, PHYSICAL_Z_GRID_MM)
        self.assertIn(65.0, PHYSICAL_Z_GRID_MM)
        self.assertIn(-3.0, PITCH_GRID_DEG)
        self.assertIn(3.0, PITCH_GRID_DEG)
        self.assertIn(-3.0, ROLL_GRID_DEG)
        self.assertIn(3.0, ROLL_GRID_DEG)
        self.assertEqual(result["grid_cardinality"]["pose_samples"], 11 * 13 * 13)
        self.assertGreaterEqual(
            result["kinematic_pin_length_screen"]["minimum_pin_length_mm"], 221.0
        )
        self.assertLessEqual(
            result["kinematic_pin_length_screen"]["maximum_pin_length_mm"], 290.0
        )
        self.assertEqual(len(calls), 9)
        self.assertEqual(
            [(pose.lift_mm, pose.pitch_deg, pose.roll_deg) for pose in calls],
            [
                (65.0, pitch_deg, roll_deg)
                for pitch_deg in (-3.0, 0.0, 3.0)
                for roll_deg in (-3.0, 0.0, 3.0)
            ],
        )
        self.assertEqual(
            progress,
            [
                f"collision {index}/9: physical Z=65 mm, "
                f"pitch={pitch_deg:+.1f} deg, roll={roll_deg:+.1f} deg"
                for index, (pitch_deg, roll_deg) in enumerate(
                    (
                        (pitch_deg, roll_deg)
                        for pitch_deg in (-3.0, 0.0, 3.0)
                        for roll_deg in (-3.0, 0.0, 3.0)
                    ),
                    start=1,
                )
            ],
        )
        self.assertTrue(result["maximum_physical_z_collision_screen"]["passes"])
        self.assertTrue(
            all(
                row["collision"]["passes"]
                for row in result["maximum_physical_z_collision_screen"]["results"]
            )
        )

    def test_artifact_writer_is_kernel_free_with_monkeypatched_collision(self):
        from calculations.reve_z15_workspace_audit import (
            render_markdown_report,
            write_workspace_audit_artifacts,
        )

        def fake_collision(pose):
            return {"pose": pose.label, "maximum_volume_mm3": 0.0, "passes": True}

        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "audit.json"
            markdown_path = Path(directory) / "audit.md"
            result = write_workspace_audit_artifacts(
                json_path, markdown_path, collision_check=fake_collision
            )
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            rendered = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(result, loaded)
        self.assertTrue(rendered.startswith("# Rev E physical Z=15--65 mm workspace audit\n"))
        self.assertNotIn("\n+##", rendered)
        self.assertNotIn("\n+|", rendered)
        self.assertNotIn("\n+-", rendered)
        self.assertIn("11 × 13 × 13", rendered)
        self.assertIn("not a continuous-workspace proof", rendered)
        self.assertIn("no fabrication or purchase release", rendered)
        self.assertEqual(rendered, render_markdown_report(result))


if __name__ == "__main__":
    unittest.main()
