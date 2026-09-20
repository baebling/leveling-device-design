"""Workspace screen for the user-selected 100 mm LM4075OE concept.

This is a Phase 1 kinematic check only. It does not include joint stack
dimensions, compliance, collision geometry, or fabrication tolerances.
"""

from itertools import product
from math import cos, radians, sin, sqrt


SUPPORT_RADIUS_MM = 250.0
SUPPORT_POINTS_MM = (
    (0.0, SUPPORT_RADIUS_MM, 0.0),
    (-216.5, -125.0, 0.0),
    (216.5, -125.0, 0.0),
)
ACTUATOR_STROKE_MM = 100.0
ACTUATOR_MIN_PIN_LENGTH_MM = 205.0
ACTUATOR_MAX_PIN_LENGTH_MM = 305.0
COLLAPSED_NEUTRAL_PIN_LENGTH_MM = 230.0
LIFT_TARGET_MM = 50.0
ANGLE_TARGET_DEG = 3.0


def _rotation_yx(pitch_deg, roll_deg):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)
    cp, sp = cos(pitch), sin(pitch)
    cr, sr = cos(roll), sin(roll)
    return (
        (cp, sp * sr, sp * cr),
        (0.0, cr, -sr),
        (-sp, cp * sr, cp * cr),
    )


def actuator_lengths_mm(lift_mm, pitch_deg, roll_deg):
    """Return the three base-to-platform joint distances for one pose."""
    rotation = _rotation_yx(pitch_deg, roll_deg)
    lengths = []
    for base_x, base_y, _ in SUPPORT_POINTS_MM:
        top_x = rotation[0][0] * base_x + rotation[0][1] * base_y
        top_y = rotation[1][0] * base_x + rotation[1][1] * base_y
        top_z = (
            COLLAPSED_NEUTRAL_PIN_LENGTH_MM
            + lift_mm
            + rotation[2][0] * base_x
            + rotation[2][1] * base_y
        )
        lengths.append(
            sqrt(
                (top_x - base_x) ** 2
                + (top_y - base_y) ** 2
                + top_z ** 2
            )
        )
    return tuple(lengths)


def workspace_screen():
    """Screen the 0/25/50 mm and -3/0/+3 degree pose grid."""
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        (0.0, LIFT_TARGET_MM / 2.0, LIFT_TARGET_MM),
        (-ANGLE_TARGET_DEG, 0.0, ANGLE_TARGET_DEG),
        (-ANGLE_TARGET_DEG, 0.0, ANGLE_TARGET_DEG),
    ):
        lengths = actuator_lengths_mm(lift_mm, pitch_deg, roll_deg)
        rows.append(
            {
                "lift_mm": lift_mm,
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                "lengths_mm": lengths,
            }
        )

    all_lengths = [length for row in rows for length in row["lengths_mm"]]
    minimum = min(all_lengths)
    maximum = max(all_lengths)
    return {
        "pose_count": len(rows),
        "actuator_min_pin_length_mm": ACTUATOR_MIN_PIN_LENGTH_MM,
        "actuator_max_pin_length_mm": ACTUATOR_MAX_PIN_LENGTH_MM,
        "required_min_length_mm": minimum,
        "required_max_length_mm": maximum,
        "required_span_mm": maximum - minimum,
        "retract_margin_mm": minimum - ACTUATOR_MIN_PIN_LENGTH_MM,
        "extend_margin_mm": ACTUATOR_MAX_PIN_LENGTH_MM - maximum,
        "passes_stroke": (
            minimum >= ACTUATOR_MIN_PIN_LENGTH_MM
            and maximum <= ACTUATOR_MAX_PIN_LENGTH_MM
        ),
        "rows": rows,
        "status": "Phase 1 preliminary; not approved for fabrication",
    }


def main():
    result = workspace_screen()
    for key, value in result.items():
        if key != "rows":
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
