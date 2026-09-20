"""Preliminary HOME path screens for the retained Rev E 3-RPS geometry."""

from __future__ import annotations

import json
import sys
from itertools import permutations
from math import acos, degrees
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculations.reve_forward_kinematics import solve_pose_from_lengths
from calculations.reve_approved_workspace import dense_pose_grid
from fusion_scripts.ProfileRadialRevD import revd_data


def _validated_path_inputs(start_lengths_mm, order, low_limit_mm, step_mm):
    lengths = tuple(float(value) for value in start_lengths_mm)
    axis_order = tuple(int(value) for value in order)
    if len(lengths) != 3 or any(value < low_limit_mm for value in lengths):
        raise ValueError("start lengths must contain three values at or above low limit")
    if sorted(axis_order) != [0, 1, 2]:
        raise ValueError("order must be a permutation of actuator indices 0, 1, 2")
    if step_mm <= 0.0:
        raise ValueError("step_mm must be positive")
    return lengths, axis_order


def sequential_length_path(
    start_lengths_mm,
    order,
    *,
    low_limit_mm: float = 205.0,
    step_mm: float = 1.0,
):
    """Retract each actuator to low limit before starting the next one."""

    lengths, axis_order = _validated_path_inputs(
        start_lengths_mm, order, low_limit_mm, step_mm
    )
    current = list(lengths)
    rows = [lengths]
    for axis in axis_order:
        while current[axis] > low_limit_mm:
            current[axis] = max(low_limit_mm, current[axis] - step_mm)
            rows.append(tuple(current))
    return tuple(rows)


def alternating_length_path(
    start_lengths_mm,
    order,
    *,
    low_limit_mm: float = 205.0,
    step_mm: float = 1.0,
    start_phase_index: int = 0,
):
    """Retract one step per actuator in a repeated fixed cyclic order."""

    lengths, axis_order = _validated_path_inputs(
        start_lengths_mm, order, low_limit_mm, step_mm
    )
    if start_phase_index not in range(3):
        raise ValueError("start_phase_index must be 0, 1, or 2")
    current = list(lengths)
    rows = [lengths]
    phase_index = start_phase_index
    idle_checks = 0
    while any(value > low_limit_mm for value in current):
        axis = axis_order[phase_index]
        phase_index = (phase_index + 1) % len(axis_order)
        if current[axis] > low_limit_mm:
            current[axis] = max(low_limit_mm, current[axis] - step_mm)
            rows.append(tuple(current))
            idle_checks = 0
        else:
            idle_checks += 1
        if idle_checks >= len(axis_order):
            raise RuntimeError("HOME path generator made no progress")
    return tuple(rows)


def _alternating_length_path_trace(
    start_lengths_mm,
    order,
    *,
    low_limit_mm: float = 205.0,
    step_mm: float = 1.0,
    start_phase_index: int = 0,
):
    """Return each emitted length state and the phase required to resume it."""

    lengths, axis_order = _validated_path_inputs(
        start_lengths_mm, order, low_limit_mm, step_mm
    )
    if start_phase_index not in range(3):
        raise ValueError("start_phase_index must be 0, 1, or 2")
    current = list(lengths)
    phase_index = start_phase_index
    records = [
        {
            "lengths_mm": lengths,
            "next_phase_index": phase_index,
        }
    ]
    idle_checks = 0
    while any(value > low_limit_mm for value in current):
        axis = axis_order[phase_index]
        phase_index = (phase_index + 1) % len(axis_order)
        if current[axis] > low_limit_mm:
            current[axis] = max(low_limit_mm, current[axis] - step_mm)
            records.append(
                {
                    "lengths_mm": tuple(current),
                    "next_phase_index": phase_index,
                }
            )
            idle_checks = 0
        else:
            idle_checks += 1
        if idle_checks >= len(axis_order):
            raise RuntimeError("HOME path trace made no progress")
    return tuple(records)


def alternating_extension_path(
    start_lengths_mm,
    order,
    *,
    target_mm: float = 210.0,
    step_mm: float = 1.0,
    start_phase_index: int = 0,
):
    """Extend one actuator per phase until all axes reach the normal window."""

    lengths = tuple(float(value) for value in start_lengths_mm)
    axis_order = tuple(int(value) for value in order)
    if len(lengths) != 3 or any(value <= 0.0 or value > target_mm for value in lengths):
        raise ValueError("start lengths must contain three values at or below target")
    if sorted(axis_order) != [0, 1, 2]:
        raise ValueError("order must be a permutation of actuator indices 0, 1, 2")
    if step_mm <= 0.0:
        raise ValueError("step_mm must be positive")
    if start_phase_index not in range(3):
        raise ValueError("start_phase_index must be 0, 1, or 2")

    current = list(lengths)
    rows = [lengths]
    phase_index = start_phase_index
    idle_checks = 0
    while any(value < target_mm for value in current):
        axis = axis_order[phase_index]
        phase_index = (phase_index + 1) % len(axis_order)
        if current[axis] < target_mm:
            current[axis] = min(target_mm, current[axis] + step_mm)
            rows.append(tuple(current))
            idle_checks = 0
        else:
            idle_checks += 1
        if idle_checks >= len(axis_order):
            raise RuntimeError("normal-window escape generator made no progress")
    return tuple(rows)


def _dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def pose_metrics(solution):
    """Return platform tilt and retained-model PHS articulation metrics."""

    rotation = revd_data.rotation_matrix(
        solution.pitch_deg, solution.roll_deg, solution.yaw_rad
    )
    tilt_deg = degrees(acos(max(-1.0, min(1.0, rotation[2][2]))))
    articulations = []
    for _, tangent in revd_data.support_basis():
        rotated_tangent = _matvec(rotation, tangent)
        articulations.append(
            degrees(
                acos(
                    max(-1.0, min(1.0, abs(_dot(tangent, rotated_tangent))))
                )
            )
        )
    return {
        "tilt_deg": tilt_deg,
        "maximum_phs_articulation_deg": max(articulations),
    }


def audit_length_path(
    length_path,
    *,
    seed,
    tilt_limit_deg: float = 5.0,
    legacy_joint_limit_deg: float = 8.0,
    stop_on_failure: bool = True,
):
    """Forward-solve and screen one finite HOME length path."""

    maximum_tilt = -1.0
    maximum_articulation = -1.0
    worst_tilt = None
    worst_articulation = None
    failure_reasons = []
    evaluated = 0
    current_seed = seed
    final_solution = None
    for step_index, lengths in enumerate(length_path):
        solution = solve_pose_from_lengths(lengths, seed=current_seed)
        evaluated += 1
        final_solution = solution
        if not solution.converged or solution.residual_mm > 1e-6:
            failure_reasons.append("FORWARD_KINEMATICS")
            if stop_on_failure:
                break
            continue
        current_seed = solution
        metrics = pose_metrics(solution)
        if metrics["tilt_deg"] > maximum_tilt:
            maximum_tilt = metrics["tilt_deg"]
            worst_tilt = {
                "step_index": step_index,
                "lengths_mm": tuple(lengths),
                "pose": solution.__dict__,
            }
        if metrics["maximum_phs_articulation_deg"] > maximum_articulation:
            maximum_articulation = metrics["maximum_phs_articulation_deg"]
            worst_articulation = {
                "step_index": step_index,
                "lengths_mm": tuple(lengths),
                "pose": solution.__dict__,
            }
        if metrics["tilt_deg"] > tilt_limit_deg + 1e-9:
            failure_reasons.append("TILT_LIMIT")
        if metrics["maximum_phs_articulation_deg"] > legacy_joint_limit_deg + 1e-9:
            failure_reasons.append("LEGACY_JOINT_LIMIT")
        if failure_reasons and stop_on_failure:
            break

    return {
        "path_state_count": len(length_path),
        "evaluated_state_count": evaluated,
        "maximum_tilt_deg": maximum_tilt,
        "maximum_phs_articulation_deg": maximum_articulation,
        "tilt_limit_deg": tilt_limit_deg,
        "joint_limit_deg": legacy_joint_limit_deg,
        "joint_limit_status": "LEGACY_8_DEG_NOT_LDK_VERIFIED",
        "failure_reasons": sorted(set(failure_reasons)),
        "kinematic_pass": not failure_reasons,
        "cad_collision_audited": False,
        "worst_tilt": worst_tilt,
        "worst_articulation": worst_articulation,
        "terminal_pose": final_solution.__dict__ if final_solution else None,
    }


def _start_record(pose):
    lift_mm, pitch_deg, roll_deg = (float(value) for value in pose)
    platform = revd_data.solve_platform(pitch_deg, roll_deg)
    return {
        "pose": (lift_mm, pitch_deg, roll_deg),
        "lengths_mm": revd_data.pin_lengths(lift_mm, pitch_deg, roll_deg),
        "seed": (
            platform["x_mm"],
            platform["y_mm"],
            lift_mm,
            pitch_deg,
            roll_deg,
            platform["yaw_rad"],
        ),
    }


def _audit_order(start_records, order, path_generator, step_mm, low_limit_mm):
    failed = 0
    evaluated = 0
    maximum_tilt = -1.0
    maximum_articulation = -1.0
    worst_tilt = None
    worst_articulation = None
    first_failure = None
    for start_index, start in enumerate(start_records):
        path = path_generator(
            start["lengths_mm"],
            order,
            low_limit_mm=low_limit_mm,
            step_mm=step_mm,
        )
        audit = audit_length_path(path, seed=start["seed"])
        evaluated += audit["evaluated_state_count"]
        if audit["maximum_tilt_deg"] > maximum_tilt:
            maximum_tilt = audit["maximum_tilt_deg"]
            worst_tilt = {
                "start_index": start_index,
                "start_pose": start["pose"],
                "path_worst": audit["worst_tilt"],
            }
        if audit["maximum_phs_articulation_deg"] > maximum_articulation:
            maximum_articulation = audit["maximum_phs_articulation_deg"]
            worst_articulation = {
                "start_index": start_index,
                "start_pose": start["pose"],
                "path_worst": audit["worst_articulation"],
            }
        if not audit["kinematic_pass"]:
            failed += 1
            if first_failure is None:
                first_failure = {
                    "start_index": start_index,
                    "start_pose": start["pose"],
                    "failure_reasons": audit["failure_reasons"],
                    "evaluated_state_count": audit["evaluated_state_count"],
                    "worst_tilt": audit["worst_tilt"],
                    "worst_articulation": audit["worst_articulation"],
                }
    return {
        "order": tuple(axis + 1 for axis in order),
        "common_pass": failed == 0,
        "failed_start_count": failed,
        "evaluated_state_count": evaluated,
        "maximum_tilt_deg": maximum_tilt,
        "maximum_phs_articulation_deg": maximum_articulation,
        "worst_tilt": worst_tilt,
        "worst_articulation": worst_articulation,
        "first_failure": first_failure,
    }


def audit_home_sequences(
    *,
    start_poses=None,
    step_mm: float = 1.0,
    low_limit_mm: float = 205.0,
    progress_callback=None,
):
    """Screen all six common sequential orders, then alternating orders.

    The default start set is the 1,859-pose finite grid.  This preliminary
    screen uses the retained geometry and nominal 205 mm low endpoint.
    """

    using_default_start_set = start_poses is None
    poses = tuple(dense_pose_grid() if start_poses is None else start_poses)
    starts = tuple(_start_record(pose) for pose in poses)
    orders = tuple(permutations((0, 1, 2)))
    sequential_rows = []
    for index, order in enumerate(orders, start=1):
        sequential_rows.append(
            _audit_order(starts, order, sequential_length_path, step_mm, low_limit_mm)
        )
        if progress_callback:
            progress_callback("SEQUENTIAL", index, len(orders), sequential_rows[-1])

    passing_sequential = [row for row in sequential_rows if row["common_pass"]]
    alternating_rows = []
    if not passing_sequential:
        for index, order in enumerate(orders, start=1):
            alternating_rows.append(
                _audit_order(starts, order, alternating_length_path, step_mm, low_limit_mm)
            )
            if progress_callback:
                progress_callback("ALTERNATING", index, len(orders), alternating_rows[-1])

    candidates = passing_sequential or [
        row for row in alternating_rows if row["common_pass"]
    ]
    selected = (
        min(
            candidates,
            key=lambda row: (
                row["maximum_tilt_deg"],
                row["maximum_phs_articulation_deg"],
                row["order"],
            ),
        )
        if candidates
        else None
    )
    selected_method = None
    if selected is not None:
        selected_method = "SEQUENTIAL" if passing_sequential else "ALTERNATING"

    return {
        "start_pose_count": len(starts),
        "start_set_scope": (
            "DENSE_GRID_ONLY" if using_default_start_set else "CALLER_PROVIDED"
        ),
        "step_mm": step_mm,
        "low_limit_mm": low_limit_mm,
        "low_limit_status": "NOMINAL_UNVERIFIED",
        "sequential_orders": sequential_rows,
        "alternating_orders": alternating_rows,
        "selected_method": selected_method,
        "selected_order_summary": selected,
        "restart_closure_audited": False,
        "all_allowed_command_and_jog_paths_included": False,
        "full_path_cad_collision_audited": False,
        "ldk_joint_limit_verified": False,
        "release_ready": False,
        "release_blockers": [
            "Nominal 205 mm is not a verified built-in lower-limit trip point.",
            "Allowed command/JOG samples and HOME restart closure are not yet included.",
            "Full-path CAD collision audit is not yet complete.",
            "LDK PHS 6 articulation limit and actual geometry are not verified.",
        ],
    }


def audit_normal_window_escape(
    *,
    low_limit_mm: float = 205.0,
    target_mm: float = 210.0,
    step_mm: float = 1.0,
    preferred_order=(2, 1, 0),
):
    """Screen all cyclic one-axis-at-a-time paths from HOME to 210 mm."""

    start_lengths = (low_limit_mm,) * 3
    start_solution = solve_pose_from_lengths(
        start_lengths,
        seed=(0.0, 0.0, -20.0, 0.0, 0.0, 0.0),
    )
    if not start_solution.converged:
        raise RuntimeError("failed to solve equal-low HOME pose")

    rows = []
    for order in permutations((0, 1, 2)):
        path = alternating_extension_path(
            start_lengths,
            order,
            target_mm=target_mm,
            step_mm=step_mm,
        )
        audit = audit_length_path(path, seed=start_solution)
        rows.append(
            {
                "order": tuple(axis + 1 for axis in order),
                "terminal_lengths_mm": path[-1],
                **audit,
            }
        )

    passing = [row for row in rows if row["kinematic_pass"]]
    preferred_one_based = tuple(axis + 1 for axis in preferred_order)
    preferred = next(
        (row for row in passing if row["order"] == preferred_one_based),
        None,
    )
    selected = preferred or (
        min(
            passing,
            key=lambda row: (
                row["maximum_tilt_deg"],
                row["maximum_phs_articulation_deg"],
                row["order"],
            ),
        )
        if passing
        else None
    )
    return {
        "low_limit_mm": low_limit_mm,
        "low_limit_status": "NOMINAL_UNVERIFIED",
        "target_mm": target_mm,
        "step_mm": step_mm,
        "orders": rows,
        "selected_order_summary": selected,
        "selection_basis": (
            "SAME_AS_SELECTED_HOME_RETRACTION_ORDER"
            if preferred is not None
            else "LOWEST_SCREENED_TILT"
        ),
        "all_orders_pass": len(passing) == len(rows),
        "release_ready": False,
        "release_blockers": [
            "Actual L_low_switch and hard-end overtravel are not supplier-verified.",
            "Full-path CAD collision audit with final LMB/PHS/stop geometry is incomplete.",
        ],
    }


def audit_phase_preserving_resume_closure(
    *,
    start_poses=None,
    order=(2, 1, 0),
    low_limit_mm: float = 205.0,
    step_mm: float = 1.0,
):
    """Check that live-session phase resume reproduces every HOME suffix."""

    using_default_start_set = start_poses is None
    poses = tuple(dense_pose_grid() if start_poses is None else start_poses)
    starts = tuple(_start_record(pose) for pose in poses)
    failed = 0
    checked = 0
    first_failure = None
    for start_index, start in enumerate(starts):
        trace = _alternating_length_path_trace(
            start["lengths_mm"],
            order,
            low_limit_mm=low_limit_mm,
            step_mm=step_mm,
        )
        for state_index, record in enumerate(trace):
            expected = tuple(
                row["lengths_mm"] for row in trace[state_index:]
            )
            resumed = alternating_length_path(
                record["lengths_mm"],
                order,
                low_limit_mm=low_limit_mm,
                step_mm=step_mm,
                start_phase_index=record["next_phase_index"],
            )
            checked += 1
            if resumed != expected:
                failed += 1
                if first_failure is None:
                    first_failure = {
                        "start_index": start_index,
                        "start_pose": start["pose"],
                        "state_index": state_index,
                        "lengths_mm": record["lengths_mm"],
                        "next_phase_index": record["next_phase_index"],
                    }
    return {
        "start_pose_count": len(starts),
        "start_set_scope": (
            "DENSE_GRID_ONLY" if using_default_start_set else "CALLER_PROVIDED"
        ),
        "order": tuple(axis + 1 for axis in order),
        "low_limit_mm": low_limit_mm,
        "low_limit_status": "NOMINAL_UNVERIFIED",
        "step_mm": step_mm,
        "restart_state_count": checked,
        "failed_restart_state_count": failed,
        "common_pass": failed == 0,
        "first_failure": first_failure,
        "resume_scope": "SAME_POWER_SESSION_WITH_LIVE_ENCODER_COUNTS_ONLY",
        "power_loss_resume_allowed": False,
        "power_loss_action": "HOME_START_UNVERIFIED",
        "command_jog_finite_audit_recorded_separately": True,
        "continuous_workspace_proven": False,
        "release_ready": False,
        "release_blockers": [
            "The separate finite command/JOG audit does not prove continuous or arbitrary endpoint-to-endpoint paths.",
            "Power-loss or MCU-reset resume is prohibited because encoder position cannot be revalidated automatically.",
            "Actual lower-limit trip lengths and final CAD collision path remain unverified.",
        ],
    }


def write_home_escape_json(path, **audit_kwargs):
    """Write the reproducible nominal HOME-to-normal-window screen."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": "ProfileRadialRevD retained geometry",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        **audit_normal_window_escape(**audit_kwargs),
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def write_home_resume_closure_json(path, **audit_kwargs):
    """Write the reproducible live-session HOME resume closure result."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": "ProfileRadialRevD retained geometry",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        **audit_phase_preserving_resume_closure(**audit_kwargs),
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def phase_reset_restart_witness(order_summary, *, step_mm: float = 1.0):
    """Try a fresh cycle at the selected path's worst-tilt intermediate state.

    A failing witness is sufficient to reject stateless restart. It is not a
    proof that every other intermediate state fails or passes.
    """

    worst = order_summary["worst_tilt"]["path_worst"]
    pose = worst["pose"]
    seed = (
        pose["x_mm"],
        pose["y_mm"],
        pose["lift_mm"],
        pose["pitch_deg"],
        pose["roll_deg"],
        pose["yaw_rad"],
    )
    zero_based_order = tuple(int(axis) - 1 for axis in order_summary["order"])
    path = alternating_length_path(
        worst["lengths_mm"],
        zero_based_order,
        step_mm=step_mm,
    )
    audit = audit_length_path(path, seed=seed)
    return {
        "source": "SELECTED_PATH_WORST_TILT_STATE",
        "order": tuple(order_summary["order"]),
        "step_mm": step_mm,
        "start_lengths_mm": tuple(worst["lengths_mm"]),
        "phase_reset_restart_pass": audit["kinematic_pass"],
        "maximum_tilt_deg": audit["maximum_tilt_deg"],
        "maximum_phs_articulation_deg": audit["maximum_phs_articulation_deg"],
        "failure_reasons": audit["failure_reasons"],
        "evaluated_state_count": audit["evaluated_state_count"],
        "worst_tilt": audit["worst_tilt"],
        "interpretation": (
            "STATELESS_RESTART_NOT_REJECTED_BY_THIS_WITNESS"
            if audit["kinematic_pass"]
            else "STATELESS_RESTART_REJECTED; PHASE-PRESERVING RESUME OR REDESIGN REQUIRED"
        ),
    }


def annotate_existing_home_json_with_restart_witness(path):
    """Add a reproducible stateless-restart witness without rerunning all paths."""

    destination = Path(path)
    payload = json.loads(destination.read_text(encoding="utf-8"))
    selected = payload.get("selected_order_summary")
    if selected is None:
        raise ValueError("HOME audit has no selected common order")
    witness = phase_reset_restart_witness(selected, step_mm=payload["step_mm"])
    payload["phase_reset_restart_witness"] = witness
    payload["restart_closure_audited"] = False
    payload["selected_home_policy_status"] = (
        "PRELIMINARY_PHASE_PRESERVING_RESUME_REQUIRED"
        if not witness["phase_reset_restart_pass"]
        else "PRELIMINARY_RESTART_WITNESS_PASS"
    )
    blocker = (
        "Stateless restart from the selected path's worst intermediate state exceeds 5 degrees; "
        "persisted cycle phase and a complete restart-closure audit are required."
    )
    if not witness["phase_reset_restart_pass"] and blocker not in payload["release_blockers"]:
        payload["release_blockers"].append(blocker)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def annotate_home_json_with_resume_and_escape(home_path, resume_path, escape_path):
    """Attach completed dense-grid resume and nominal escape screens."""

    destination = Path(home_path)
    payload = json.loads(destination.read_text(encoding="utf-8"))
    resume = json.loads(Path(resume_path).read_text(encoding="utf-8"))
    escape = json.loads(Path(escape_path).read_text(encoding="utf-8"))
    payload["dense_grid_phase_preserving_resume_closed"] = bool(
        resume["common_pass"]
    )
    payload["phase_preserving_resume_closure"] = {
        "restart_state_count": resume["restart_state_count"],
        "failed_restart_state_count": resume["failed_restart_state_count"],
        "power_loss_resume_allowed": resume["power_loss_resume_allowed"],
        "power_loss_action": resume["power_loss_action"],
    }
    payload["normal_window_escape_summary"] = {
        "all_orders_pass": escape["all_orders_pass"],
        "selection_basis": escape["selection_basis"],
        "selected_order": escape["selected_order_summary"]["order"],
    }
    payload["power_loss_resume_allowed"] = False
    payload["restart_closure_audited"] = False
    payload["selected_home_policy_status"] = (
        "PRELIMINARY_LIVE_SESSION_RESUME_CLOSED_POWER_LOSS_BLOCKED"
    )
    obsolete_fragments = (
        "Allowed command/JOG samples and HOME restart closure",
        "Allowed command/JOG samples are not yet included",
        "LDK PHS 6 articulation limit and actual geometry are not verified",
        "persisted cycle phase and a complete restart-closure audit",
    )
    blockers = [
        blocker
        for blocker in payload.get("release_blockers", [])
        if not any(fragment in blocker for fragment in obsolete_fragments)
    ]
    for blocker in (
        "Arbitrary endpoint-to-endpoint command paths are prohibited by the preliminary HOME policy and are not audited.",
        "Power-loss, MCU-reset, and E-stop automatic HOME resume are prohibited; HOME_START_UNVERIFIED recovery is required.",
        "Final LDK PHS 6 geometry and LMB-10 geometry are not yet included in the full-path CAD collision audit.",
    ):
        if blocker not in blockers:
            blockers.append(blocker)
    payload["release_blockers"] = blockers
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def write_home_audit_json(path, **audit_kwargs):
    """Run a HOME screen and write a stable JSON verification artifact."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    audit = audit_home_sequences(**audit_kwargs)
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": "ProfileRadialRevD retained geometry",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        **audit,
    }
    selected = payload.get("selected_order_summary")
    if selected is not None:
        witness = phase_reset_restart_witness(selected, step_mm=payload["step_mm"])
        payload["phase_reset_restart_witness"] = witness
        payload["selected_home_policy_status"] = (
            "PRELIMINARY_PHASE_PRESERVING_RESUME_REQUIRED"
            if not witness["phase_reset_restart_pass"]
            else "PRELIMINARY_RESTART_WITNESS_PASS"
        )
        if not witness["phase_reset_restart_pass"]:
            payload["release_blockers"].append(
                "Stateless restart from the selected path's worst intermediate state exceeds 5 degrees; "
                "persisted cycle phase and a complete restart-closure audit are required."
            )
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def _print_progress(method, index, count, summary):
    print(
        f"{method} {index}/{count} order={summary['order']} "
        f"common_pass={summary['common_pass']} "
        f"failed_starts={summary['failed_start_count']} "
        f"max_tilt={summary['maximum_tilt_deg']:.6f}",
        flush=True,
    )


if __name__ == "__main__":
    output = ROOT / "verification" / "reve_home_path_audit_2026-09-17.json"
    result = write_home_audit_json(output, progress_callback=_print_progress)
    print(
        json.dumps(
            {
                "output": str(output),
                "start_pose_count": result["start_pose_count"],
                "selected_method": result["selected_method"],
                "selected_order": (
                    result["selected_order_summary"]["order"]
                    if result["selected_order_summary"]
                    else None
                ),
                "release_ready": result["release_ready"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
