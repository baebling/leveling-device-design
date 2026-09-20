"""Kinematic screen for the active manually adjustable 3-RPS concept.

The geometry intentionally reuses the last powered 3-RPS datum so the
manual struts can later be exchanged for actuators. This calculation does
not select a screw, nut, tube, joint, or fabrication tolerance.
"""

from itertools import product

from calculations.minimal_3rps_100mm_screen import actuator_lengths_mm


MANUAL_STRUT_MIN_PIN_LENGTH_MM = 205.0
MANUAL_STRUT_MAX_PIN_LENGTH_MM = 305.0
NOMINAL_PIN_LENGTH_MM = 230.0
LIFT_TARGET_MM = 50.0
ANGLE_TARGET_DEG = 3.0


def _screen(lift_values_mm):
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        lift_values_mm,
        (-ANGLE_TARGET_DEG, 0.0, ANGLE_TARGET_DEG),
        (-ANGLE_TARGET_DEG, 0.0, ANGLE_TARGET_DEG),
    ):
        lengths = actuator_lengths_mm(lift_mm, pitch_deg, roll_deg)
        rows.append(
            {
                "lift_mm": lift_mm,
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                "strut_pin_lengths_mm": lengths,
            }
        )

    lengths = [length for row in rows for length in row["strut_pin_lengths_mm"]]
    minimum = min(lengths)
    maximum = max(lengths)
    return {
        "pose_count": len(rows),
        "required_min_pin_length_mm": minimum,
        "required_max_pin_length_mm": maximum,
        "required_adjustment_mm": maximum - minimum,
        "minimum_end_margin_mm": minimum - MANUAL_STRUT_MIN_PIN_LENGTH_MM,
        "maximum_end_margin_mm": MANUAL_STRUT_MAX_PIN_LENGTH_MM - maximum,
        "fits_preliminary_strut_envelope": (
            minimum >= MANUAL_STRUT_MIN_PIN_LENGTH_MM
            and maximum <= MANUAL_STRUT_MAX_PIN_LENGTH_MM
        ),
        "rows": rows,
    }


def manual_workspace_screen():
    """Screen manual Z 0/25/50 mm and pitch/roll -3/0/+3 degrees."""
    return _screen((0.0, LIFT_TARGET_MM / 2.0, LIFT_TARGET_MM))


def tilt_only_screen():
    """Screen a no-lift display variant over pitch/roll -3/0/+3 degrees."""
    return _screen((0.0,))


def main():
    for name, result in (
        ("manual_full_workspace", manual_workspace_screen()),
        ("manual_tilt_only", tilt_only_screen()),
    ):
        print(name)
        for key, value in result.items():
            if key != "rows":
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
