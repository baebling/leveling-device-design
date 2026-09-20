import json
import tempfile
import unittest
from pathlib import Path

from fusion_scripts.ProfileRadialRevD import revd_data


class ReveForwardKinematicsTests(unittest.TestCase):
    def test_forward_solution_reproduces_known_pose(self):
        from calculations.reve_forward_kinematics import solve_pose_from_lengths

        lengths = revd_data.pin_lengths(25.0, 3.0, -3.0)
        solved = solve_pose_from_lengths(
            lengths,
            seed=(0.0, 0.0, 25.0, 3.0, -3.0, 0.0),
        )
        self.assertTrue(solved.converged)
        self.assertLess(solved.residual_mm, 1e-6)
        self.assertAlmostEqual(solved.lift_mm, 25.0, places=4)
        self.assertAlmostEqual(solved.pitch_deg, 3.0, places=4)
        self.assertAlmostEqual(solved.roll_deg, -3.0, places=4)

    def test_forward_solution_round_trips_approved_corner_poses(self):
        from calculations.reve_forward_kinematics import solve_pose_from_lengths

        for lift_mm, pitch_deg, roll_deg in (
            (0.0, -3.0, -3.0),
            (0.0, 3.0, 3.0),
            (50.0, -3.0, 3.0),
            (50.0, 3.0, -3.0),
        ):
            lengths = revd_data.pin_lengths(lift_mm, pitch_deg, roll_deg)
            solved = solve_pose_from_lengths(
                lengths,
                seed=(0.0, 0.0, lift_mm, pitch_deg, roll_deg, 0.0),
            )
            self.assertTrue(solved.converged)
            self.assertAlmostEqual(solved.lift_mm, lift_mm, places=4)
            self.assertAlmostEqual(solved.pitch_deg, pitch_deg, places=4)
            self.assertAlmostEqual(solved.roll_deg, roll_deg, places=4)


class ReveHomePathTests(unittest.TestCase):
    def test_sequential_and_alternating_generators_reach_common_low_limit(self):
        from calculations.reve_home_path_audit import (
            alternating_length_path,
            sequential_length_path,
        )

        start = (208.5, 207.2, 206.0)
        for path in (
            sequential_length_path(start, (0, 1, 2), low_limit_mm=205.0),
            alternating_length_path(start, (0, 1, 2), low_limit_mm=205.0),
        ):
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], (205.0, 205.0, 205.0))
            for first, second in zip(path, path[1:]):
                changed = [
                    axis
                    for axis in range(3)
                    if abs(second[axis] - first[axis]) > 1e-12
                ]
                self.assertEqual(len(changed), 1)
                axis = changed[0]
                self.assertLess(second[axis], first[axis])
                self.assertLessEqual(first[axis] - second[axis], 1.0 + 1e-12)

    def test_alternating_home_avoids_flat_z50_sequential_tilt_excursion(self):
        from calculations.reve_home_path_audit import (
            alternating_length_path,
            audit_length_path,
            sequential_length_path,
        )

        start = revd_data.pin_lengths(50.0, 0.0, 0.0)
        seed = (0.0, 0.0, 50.0, 0.0, 0.0, 0.0)
        sequential = audit_length_path(
            sequential_length_path(start, (0, 1, 2)),
            seed=seed,
        )
        alternating = audit_length_path(
            alternating_length_path(start, (0, 1, 2)),
            seed=seed,
        )

        self.assertFalse(sequential["kinematic_pass"])
        self.assertIn("TILT_LIMIT", sequential["failure_reasons"])
        self.assertTrue(alternating["kinematic_pass"])
        self.assertLessEqual(alternating["maximum_tilt_deg"], 5.0)

    def test_common_home_selector_falls_back_to_alternating_policy(self):
        from calculations.reve_home_path_audit import audit_home_sequences

        result = audit_home_sequences(
            start_poses=((0.0, 0.0, 0.0), (50.0, 0.0, 0.0)),
            step_mm=1.0,
        )

        self.assertEqual(result["start_pose_count"], 2)
        self.assertFalse(any(row["common_pass"] for row in result["sequential_orders"]))
        self.assertEqual(result["selected_method"], "ALTERNATING")
        self.assertTrue(result["selected_order_summary"]["common_pass"])
        self.assertFalse(result["release_ready"])

    def test_home_json_records_preliminary_nonrelease_status(self):
        from calculations.reve_home_path_audit import write_home_audit_json

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "home.json"
            payload = write_home_audit_json(
                destination,
                start_poses=((0.0, 0.0, 0.0), (50.0, 0.0, 0.0)),
            )
            loaded = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(payload, loaded)
        self.assertEqual(loaded["selected_method"], "ALTERNATING")
        self.assertIn("phase_reset_restart_witness", loaded)
        self.assertIn("selected_home_policy_status", loaded)
        self.assertFalse(loaded["release_ready"])
        self.assertFalse(loaded["full_path_cad_collision_audited"])

    def test_phase_reset_restart_witness_rejects_fresh_cycle_restart(self):
        from calculations.reve_home_path_audit import phase_reset_restart_witness

        order_summary = {
            "order": (3, 2, 1),
            "worst_tilt": {
                "path_worst": {
                    "lengths_mm": (
                        205.35633109200546,
                        230.49917169120414,
                        212.75251716081982,
                    ),
                    "pose": {
                        "x_mm": 0.474951096509438,
                        "y_mm": 0.017208328064877793,
                        "lift_mm": -11.204674137040033,
                        "pitch_deg": 3.691025551364776,
                        "roll_deg": -3.3658636466565994,
                        "yaw_rad": -0.002003689803117402,
                    },
                }
            },
        }
        result = phase_reset_restart_witness(order_summary, step_mm=1.0)

        self.assertFalse(result["phase_reset_restart_pass"])
        self.assertGreater(result["maximum_tilt_deg"], 5.0)
        self.assertEqual(result["failure_reasons"], ["TILT_LIMIT"])

    def test_phase_preserving_resume_reproduces_the_original_suffix(self):
        from calculations.reve_home_path_audit import alternating_length_path

        order = (2, 1, 0)
        full_path = alternating_length_path(
            (208.0, 208.0, 208.0),
            order,
            step_mm=1.0,
        )
        interrupted_step = 2
        resumed = alternating_length_path(
            full_path[interrupted_step],
            order,
            step_mm=1.0,
            start_phase_index=2,
        )

        self.assertEqual(resumed, full_path[interrupted_step:])

    def test_normal_window_escape_raises_one_axis_per_step(self):
        from calculations.reve_home_path_audit import alternating_extension_path

        path = alternating_extension_path(
            (205.0, 205.0, 205.0),
            (0, 1, 2),
            target_mm=210.0,
            step_mm=1.0,
        )

        self.assertEqual(path[0], (205.0, 205.0, 205.0))
        self.assertEqual(path[-1], (210.0, 210.0, 210.0))
        for first, second in zip(path, path[1:]):
            changed = [
                axis
                for axis in range(3)
                if abs(second[axis] - first[axis]) > 1e-12
            ]
            self.assertEqual(len(changed), 1)
            axis = changed[0]
            self.assertGreater(second[axis], first[axis])
            self.assertLessEqual(second[axis] - first[axis], 1.0 + 1e-12)

    def test_equal_low_escape_audits_all_six_orders_below_five_degrees(self):
        from calculations.reve_home_path_audit import audit_normal_window_escape

        result = audit_normal_window_escape()

        self.assertEqual(len(result["orders"]), 6)
        self.assertTrue(all(row["kinematic_pass"] for row in result["orders"]))
        self.assertIsNotNone(result["selected_order_summary"])
        self.assertEqual(result["selected_order_summary"]["order"], (3, 2, 1))
        self.assertLessEqual(
            result["selected_order_summary"]["maximum_tilt_deg"],
            5.0,
        )
        self.assertFalse(result["release_ready"])

    def test_escape_json_records_nominal_nonrelease_status(self):
        from calculations.reve_home_path_audit import write_home_escape_json

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "escape.json"
            payload = write_home_escape_json(destination)
            loaded = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(payload, loaded)
        self.assertTrue(loaded["all_orders_pass"])
        self.assertEqual(loaded["low_limit_status"], "NOMINAL_UNVERIFIED")
        self.assertFalse(loaded["release_ready"])

    def test_phase_preserving_resume_closure_matches_every_suffix(self):
        from calculations.reve_home_path_audit import (
            audit_phase_preserving_resume_closure,
        )

        result = audit_phase_preserving_resume_closure(
            start_poses=((0.0, 0.0, 0.0), (50.0, 3.0, -3.0)),
            order=(2, 1, 0),
        )

        self.assertEqual(result["start_pose_count"], 2)
        self.assertGreater(result["restart_state_count"], 2)
        self.assertEqual(result["failed_restart_state_count"], 0)
        self.assertTrue(result["common_pass"])
        self.assertFalse(result["power_loss_resume_allowed"])

    def test_resume_closure_json_keeps_power_loss_restart_blocked(self):
        from calculations.reve_home_path_audit import write_home_resume_closure_json

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "resume.json"
            payload = write_home_resume_closure_json(
                destination,
                start_poses=((0.0, 0.0, 0.0),),
            )
            loaded = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(payload, loaded)
        self.assertTrue(loaded["common_pass"])
        self.assertFalse(loaded["power_loss_resume_allowed"])
        self.assertEqual(loaded["power_loss_action"], "HOME_START_UNVERIFIED")
        self.assertTrue(loaded["command_jog_finite_audit_recorded_separately"])
        self.assertFalse(loaded["continuous_workspace_proven"])
        self.assertFalse(
            any(
                "not yet included" in blocker
                for blocker in loaded["release_blockers"]
            )
        )
        self.assertTrue(
            any(
                "arbitrary endpoint-to-endpoint" in blocker
                for blocker in loaded["release_blockers"]
            )
        )

    def test_home_json_annotation_records_live_resume_and_escape_results(self):
        from calculations.reve_home_path_audit import (
            annotate_home_json_with_resume_and_escape,
        )

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            home_path = directory / "home.json"
            resume_path = directory / "resume.json"
            escape_path = directory / "escape.json"
            home_path.write_text(
                json.dumps(
                    {
                        "release_blockers": [
                            "Allowed command/JOG samples are not yet included in the HOME start set.",
                            "LDK PHS 6 articulation limit and actual geometry are not verified.",
                        ],
                        "restart_closure_audited": False,
                    }
                ),
                encoding="utf-8",
            )
            resume_path.write_text(
                json.dumps(
                    {
                        "common_pass": True,
                        "restart_state_count": 216951,
                        "failed_restart_state_count": 0,
                        "power_loss_resume_allowed": False,
                        "power_loss_action": "HOME_START_UNVERIFIED",
                    }
                ),
                encoding="utf-8",
            )
            escape_path.write_text(
                json.dumps(
                    {
                        "all_orders_pass": True,
                        "selection_basis": "SAME_AS_SELECTED_HOME_RETRACTION_ORDER",
                        "selected_order_summary": {"order": [3, 2, 1]},
                    }
                ),
                encoding="utf-8",
            )
            payload = annotate_home_json_with_resume_and_escape(
                home_path,
                resume_path,
                escape_path,
            )

        self.assertTrue(payload["dense_grid_phase_preserving_resume_closed"])
        self.assertFalse(payload["restart_closure_audited"])
        self.assertFalse(payload["power_loss_resume_allowed"])
        self.assertEqual(
            payload["selected_home_policy_status"],
            "PRELIMINARY_LIVE_SESSION_RESUME_CLOSED_POWER_LOSS_BLOCKED",
        )
        self.assertTrue(
            any(
                "Arbitrary endpoint-to-endpoint command paths" in blocker
                for blocker in payload["release_blockers"]
            )
        )
        self.assertFalse(
            any(
                "Allowed command/JOG samples are not yet included" in blocker
                for blocker in payload["release_blockers"]
            )
        )
        self.assertTrue(
            any(
                "Final LDK PHS 6 geometry" in blocker
                for blocker in payload["release_blockers"]
            )
        )

    def test_cad_spotcheck_extracts_declared_representative_states(self):
        from calculations.reve_home_cad_spotcheck import extract_pose_records

        payload = json.loads(
            (Path(__file__).resolve().parents[1]
             / "verification"
             / "reve_home_path_audit_2026-09-17.json").read_text(encoding="utf-8")
        )
        records = extract_pose_records(payload)

        self.assertEqual(
            [record["label"] for record in records],
            [
                "HOME_WORST_TILT",
                "HOME_WORST_ARTICULATION",
                "HOME_STATELESS_RESTART_FAILURE",
                "HOME_EQUAL_LOW_NOMINAL",
            ],
        )


if __name__ == "__main__":
    unittest.main()
