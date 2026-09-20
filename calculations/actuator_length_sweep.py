from itertools import product

from cad.assembly import actuator_lengths
from cad.parameters import P, Pose


LIFT_SWEEP_MM = (0.0, 50.0, 75.0, 100.0)
ANGLE_SWEEP_DEG = (3.0, 5.0, 8.0)


def poses_for_angle(angle_deg):
    for lift, pitch, roll in product(LIFT_SWEEP_MM, (-angle_deg, 0.0, angle_deg), (-angle_deg, 0.0, angle_deg)):
        yield Pose(lift, pitch, roll, True, f"z{lift:g}_p{pitch:g}_r{roll:g}")


def summarize_angle(angle_deg):
    rows = []
    for pose in poses_for_angle(angle_deg):
        lengths = actuator_lengths(pose)
        rows.append((pose, lengths))
    values = [length for _, lengths in rows for length in lengths]
    min_length = min(values)
    max_length = max(values)
    return {
        "angle_deg": angle_deg,
        "lift_sweep_mm": LIFT_SWEEP_MM,
        "minimum_length_mm": min_length,
        "maximum_length_mm": max_length,
        "required_stroke_mm": max_length - min_length,
        "retracted_margin_mm": min_length - P.actuator_retracted_mm,
        "extended_margin_mm": P.actuator_extended_mm - max_length,
        "passes_current_actuator": (
            min_length >= P.actuator_retracted_mm + P.actuator_min_end_margin_mm
            and max_length <= P.actuator_extended_mm - P.actuator_min_end_margin_mm
        ),
    }


def main():
    for angle in ANGLE_SWEEP_DEG:
        print(summarize_angle(angle))


if __name__ == "__main__":
    main()
