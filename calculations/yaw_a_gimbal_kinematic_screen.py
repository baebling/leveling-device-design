"""Kinematic proof screen for the preliminary YAW-A two-axis yoke.

This is a Phase 1 concept calculation.  It fixes the yoke axis order so that
the platform has only Z, pitch, and roll motion: a lower, fixed +Y pitch axis
followed by an upper +X roll axis carried by the pitched outer yoke.  It is
not fabrication geometry or a substitute for a physical clearance mock-up.
"""

from math import acos, cos, degrees, radians, sin
from pathlib import Path
import os
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calculations.user_confirmed_baseline import central_yaw_screen
from calculations.yaw_a_architecture_screen import (
    YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
    YAW_A_GIMBAL_HARD_STOP_DEG,
)


OPERATING_AXIS_ANGLE_DEG = 3.0
STOP_AXIS_LIMIT_DEG = 7.0
ANGLE_MARGIN_DEG = 2.0
NUMERIC_TOLERANCE_DEG = 1.0e-9


def rotation_x(angle_deg):
    angle = radians(angle_deg)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, cos(angle), -sin(angle)],
        [0.0, sin(angle), cos(angle)],
    ])


def rotation_y(angle_deg):
    angle = radians(angle_deg)
    return np.array([
        [cos(angle), 0.0, sin(angle)],
        [0.0, 1.0, 0.0],
        [-sin(angle), 0.0, cos(angle)],
    ])


def platform_rotation(pitch_deg, roll_deg):
    """Return the selected lower-pitch then upper-roll gimbal orientation."""
    return rotation_y(pitch_deg) @ rotation_x(roll_deg)


def zyx_heading_yaw_deg(rotation):
    """Extract world-Z heading from the selected Rz*Ry*Rx convention."""
    return degrees(np.arctan2(rotation[1, 0], rotation[0, 0]))


def total_tilt_deg(pitch_deg, roll_deg):
    """Angle between the lower and upper local +Z axes."""
    value = cos(radians(pitch_deg)) * cos(radians(roll_deg))
    return degrees(acos(max(-1.0, min(1.0, value))))


def kinematic_axes(pitch_deg):
    """Return the two free axes and the instantaneous locked rotation axis.

    The lower pitch pin is fixed on +Y.  The upper roll pin is carried by the
    outer yoke, so its world direction is Ry(pitch) * +X.  Their normal is the
    single relative rotation that the 2R yoke blocks.  It is oriented toward
    +Z in the level pose for a readable yaw-reaction projection.
    """
    pitch_axis = np.array([0.0, 1.0, 0.0])
    roll_axis = rotation_y(pitch_deg) @ np.array([1.0, 0.0, 0.0])
    locked_axis = -np.cross(pitch_axis, roll_axis)
    locked_axis = locked_axis / np.linalg.norm(locked_axis)
    return {
        "pitch_axis_world": pitch_axis,
        "roll_axis_world": roll_axis,
        "locked_axis_world": locked_axis,
    }


def yaw_constraint_screen(pitch_deg, roll_deg, yaw_torque_nm=None):
    if yaw_torque_nm is None:
        yaw_torque_nm = central_yaw_screen()["required_design_yaw_torque_nm"]

    rotation = platform_rotation(pitch_deg, roll_deg)
    axes = kinematic_axes(pitch_deg)
    world_yaw = np.array([0.0, 0.0, 1.0])
    yaw_lock_projection = float(np.dot(world_yaw, axes["locked_axis_world"]))
    locked_reaction = abs(yaw_torque_nm * yaw_lock_projection)
    coupled_pitch_roll_moment = abs(yaw_torque_nm) * (1.0 - yaw_lock_projection ** 2) ** 0.5
    return {
        "pitch_deg": pitch_deg,
        "roll_deg": roll_deg,
        "total_tilt_deg": total_tilt_deg(pitch_deg, roll_deg),
        "heading_yaw_deg": zyx_heading_yaw_deg(rotation),
        "pitch_axis_world": axes["pitch_axis_world"].tolist(),
        "roll_axis_world": axes["roll_axis_world"].tolist(),
        "locked_axis_world": axes["locked_axis_world"].tolist(),
        "yaw_lock_projection": yaw_lock_projection,
        "yaw_torque_input_nm": yaw_torque_nm,
        "locked_axis_yaw_reaction_nm": locked_reaction,
        "coupled_pitch_roll_moment_nm": coupled_pitch_roll_moment,
        "heading_is_mechanically_constrained": abs(zyx_heading_yaw_deg(rotation)) <= NUMERIC_TOLERANCE_DEG,
        "note": (
            "The remaining moment is not a free yaw DOF. It is resolved by the "
            "two pitch/roll drive paths and must be checked by the holding/load-path review."
        ),
    }


def operating_envelope_screen():
    rows = []
    for pitch_deg in (-OPERATING_AXIS_ANGLE_DEG, 0.0, OPERATING_AXIS_ANGLE_DEG):
        for roll_deg in (-OPERATING_AXIS_ANGLE_DEG, 0.0, OPERATING_AXIS_ANGLE_DEG):
            rows.append(yaw_constraint_screen(pitch_deg, roll_deg))
    return rows


def stop_envelope_screen():
    required_total_tilt = total_tilt_deg(OPERATING_AXIS_ANGLE_DEG, OPERATING_AXIS_ANGLE_DEG)
    required_total_tilt_with_margin = required_total_tilt + ANGLE_MARGIN_DEG
    diagonal_stop_tilt = total_tilt_deg(STOP_AXIS_LIMIT_DEG, STOP_AXIS_LIMIT_DEG)
    return {
        "operating_pitch_roll_deg": OPERATING_AXIS_ANGLE_DEG,
        "operating_diagonal_total_tilt_deg": required_total_tilt,
        "required_total_tilt_with_margin_deg": required_total_tilt_with_margin,
        "legacy_gimbal_design_envelope_deg": YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
        "legacy_total_tilt_hard_stop_deg": YAW_A_GIMBAL_HARD_STOP_DEG,
        "selected_independent_pin_stop_deg": STOP_AXIS_LIMIT_DEG,
        "maximum_diagonal_total_tilt_at_pin_stops_deg": diagonal_stop_tilt,
        "operating_clearance_passes": required_total_tilt_with_margin <= YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
        "stop_envelope_passes": diagonal_stop_tilt <= YAW_A_GIMBAL_HARD_STOP_DEG,
        "implementation_rule": (
            "Use four independent, adjustable, non-load-bearing stop contacts: "
            "pitch +/-7 deg and roll +/-7 deg. This simple square stop envelope "
            "keeps the worst diagonal total tilt below the existing 10 deg limit."
        ),
        "warning": (
            "Do not interpret the legacy 10 deg total-tilt stop as 10 deg on each "
            "pin axis. Two independent 10 deg pin stops would permit about 14.1 deg "
            "diagonal total tilt."
        ),
    }


def physical_architecture_definition():
    return {
        "coordinate_origin": "O at the intersection of the two yoke pin axes and the keyed-slide centerline",
        "axes": {
            "+X": "upper platform roll axis at level",
            "+Y": "fixed lower yoke pitch-pin axis",
            "+Z": "keyed-slide translation axis and world vertical at level",
        },
        "motion_order": "lower pitch pin about +Y, then upper roll pin about the pitched carrier local +X",
        "relative_orientation": "R = Ry(pitch) @ Rx(roll)",
        "yaw_path": (
            "lower housing -> keyed square guide -> guide inner head -> lower yoke -> "
            "outer yoke -> upper yoke -> upper platform; no third revolute or azimuth bearing is permitted"
        ),
        "translation_path": "keyed guide provides Z translation while constraining X and Y",
        "required_build_features": (
            "double-shear pins, replaceable pin bushings/washers, four adjustable angular "
            "stops, separate electrical limit switches, and a debris cover for guide wear pads"
        ),
        "fabrication_status": "Phase 1 preliminary concept; not approved for fabrication",
    }


def mockup_acceptance_rules():
    return {
        "fixture": "non-load-bearing wood/plate or laser-cut gauge with the real planned pin diameters and spacers",
        "check_1": "At all nine pitch/roll combinations from -3 to +3 deg, the guide translates freely and the yoke has no contact or binding.",
        "check_2": "At the four +/-7 deg pin-stop positions and four diagonal corners, the mechanical stops contact before tube, pin-retention, or actuator interference.",
        "check_3": "With the guide clamped and an upper-platform lever arm, no perceptible independent yaw spin is possible; measure backlash against the <=0.5 deg candidate limit.",
        "check_4": "Apply the representative yaw couple only after a separate safe bench-fixture plan is approved; inspect wear-pad marking, pin contact, and stop contact.",
        "reject_if": "any third yaw joint exists, heading changes independently of pitch/roll, the +/-3 deg grid binds, or a hard stop relies on an electrical limit switch",
    }


def summary():
    return {
        "physical_architecture": physical_architecture_definition(),
        "operating_envelope": operating_envelope_screen(),
        "stop_envelope": stop_envelope_screen(),
        "mockup_acceptance": mockup_acceptance_rules(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def main():
    result = summary()
    print({"physical_architecture": result["physical_architecture"]})
    print({"stop_envelope": result["stop_envelope"]})
    for row in result["operating_envelope"]:
        print({"operating_row": row})


if __name__ == "__main__":
    main()
