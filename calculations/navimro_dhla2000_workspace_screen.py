from itertools import product
from math import cos, dist, radians, sin


# Candidate-only screen. These values do not modify the active CAD baseline.
UPPER_RADIUS_MM = 400.0
LOWER_RADIUS_MM = 175.0
# User-selected planning assumption: no flat plates are supplied. The compact
# pin/lug-end geometry balances the provisional A1-style endpoint reserves.
COLLAPSED_VERTICAL_JOINT_SEPARATION_MM = 185.0
BASE_JOINT_Z_MM = 50.0
TOP_ABOVE_JOINT_MM = 35.0

ACTUATOR_VARIANTS_MM = {
    # Official DIHOOL drawings for stroke S < 500 mm.
    "PIN_LUG_END_ASSUMPTION": (255.0, 405.0),
    "A1_PIN_END": (255.0, 405.0),  # Lmin = S + 105; Lmax = Lmin + S
    "A2_PLATE_END": (265.0, 415.0),  # Lmin = S + 115; Lmax = Lmin + S
}
PLANNING_END_MARGIN_MM = 5.0
TARGET_LIFT_MM = 100.0
TARGET_ANGLE_DEG = 3.0


def actuator_lengths(lift_mm, pitch_deg, roll_deg):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)
    lengths = []

    for angle_deg in (0.0, 120.0, 240.0):
        angle = radians(angle_deg)
        upper_x = UPPER_RADIUS_MM * cos(angle)
        upper_y = UPPER_RADIUS_MM * sin(angle)

        rolled_y = upper_y * cos(roll)
        rolled_z = upper_y * sin(roll)
        pitched_x = upper_x * cos(pitch) + rolled_z * sin(pitch)
        pitched_z = -upper_x * sin(pitch) + rolled_z * cos(pitch)

        lower_x = LOWER_RADIUS_MM * cos(angle)
        lower_y = LOWER_RADIUS_MM * sin(angle)
        top = (
            pitched_x,
            rolled_y,
            pitched_z + COLLAPSED_VERTICAL_JOINT_SEPARATION_MM + lift_mm,
        )
        bottom = (lower_x, lower_y, 0.0)
        lengths.append(dist(bottom, top))

    return tuple(lengths)


def screen(variant="PIN_LUG_END_ASSUMPTION"):
    actuator_retracted_mm, actuator_extended_mm = ACTUATOR_VARIANTS_MM[variant]
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        tuple(float(value) for value in range(0, 101, 5)),
        (-TARGET_ANGLE_DEG, 0.0, TARGET_ANGLE_DEG),
        (-TARGET_ANGLE_DEG, 0.0, TARGET_ANGLE_DEG),
    ):
        lengths = actuator_lengths(lift_mm, pitch_deg, roll_deg)
        rows.append((lift_mm, pitch_deg, roll_deg, lengths))

    values = [length for *_, lengths in rows for length in lengths]
    minimum = min(values)
    maximum = max(values)
    return {
        "candidate": "NAVIMRO DIHOOL LA2000-125150 / K92931811",
        "mounting_variant": variant,
        "upper_radius_mm": UPPER_RADIUS_MM,
        "lower_radius_mm": LOWER_RADIUS_MM,
        "collapsed_vertical_joint_separation_mm": COLLAPSED_VERTICAL_JOINT_SEPARATION_MM,
        "disconnected_collapsed_height_mm": (
            BASE_JOINT_Z_MM
            + COLLAPSED_VERTICAL_JOINT_SEPARATION_MM
            + TOP_ABOVE_JOINT_MM
        ),
        "level_collapsed_actuator_length_mm": actuator_lengths(0.0, 0.0, 0.0)[0],
        "minimum_workspace_length_mm": minimum,
        "maximum_workspace_length_mm": maximum,
        "required_workspace_span_mm": maximum - minimum,
        "actuator_retracted_mm": actuator_retracted_mm,
        "actuator_extended_mm": actuator_extended_mm,
        "physical_retraction_margin_mm": minimum - actuator_retracted_mm,
        "physical_extension_margin_mm": actuator_extended_mm - maximum,
        "passes_5_mm_planning_window": (
            minimum >= actuator_retracted_mm + PLANNING_END_MARGIN_MM
            and maximum <= actuator_extended_mm - PLANNING_END_MARGIN_MM
        ),
        "selected_procurement_variant": "PIN_LUG_END_ASSUMPTION",
        "end_interface_assumption": (
            "No flat panels supplied; M8 threaded rod-end accessory adapts to a pin/lug joint"
        ),
        "seller_variant_confirmation_required": True,
    }


if __name__ == "__main__":
    for mounting_variant in ACTUATOR_VARIANTS_MM:
        print(screen(mounting_variant))
