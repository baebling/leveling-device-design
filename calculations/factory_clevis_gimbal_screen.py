"""Factory-eye nested-gimbal joint screen for the static bench prototype."""

from math import pi

from cad.parameters import P
from calculations.actuator_bracket_package_screen import active_bracket_load_case
from calculations.workspace_operating_window_screen import summary as workspace_summary


JOINT_CODE = "JNT-CG-01"
FACTORY_HOLE_MM = 8.2
FACTORY_EYE_WIDTH_MOCKUP_RANGE_MM = (9.0, 11.0)
INNER_GAP_MM = 12.0
PLATE_THICKNESS_MM = 6.0
PIN_DIAMETER_MM = 8.0
TRUNNION_SUPPORTED_SPAN_MM = 22.0
SERIAL_HRT8E_ADAPTER_EXTENSION_EACH_END_MM = 32.0
PRELIM_ALLOWABLE_MPA = 100.0


def serial_adapter_workspace_screen():
    selected = workspace_summary()["recommended_candidate"]
    minimum_joint_distance = selected["worst_actuator_row"]["minimum_actuator_length_mm"]
    added_length = 2.0 * SERIAL_HRT8E_ADAPTER_EXTENSION_EACH_END_MM
    effective_actuator_pin_length = minimum_joint_distance - added_length
    return {
        "topology": "factory-eye to serial HRT8E adapter at both ends",
        "minimum_existing_joint_distance_mm": minimum_joint_distance,
        "assumed_extension_each_end_mm": SERIAL_HRT8E_ADAPTER_EXTENSION_EACH_END_MM,
        "effective_minimum_actuator_pin_length_mm": effective_actuator_pin_length,
        "catalog_retracted_length_mm": P.actuator_retracted_mm,
        "passes_catalog_endpoint": effective_actuator_pin_length >= P.actuator_retracted_mm,
        "selection_status": "reject_for_current_geometry",
        "reason": "Serial adapters consume the current lower-stroke workspace reserve.",
    }


def nested_gimbal_pin_screen():
    force_n = active_bracket_load_case()["max_axial_force_n"]
    area = pi * PIN_DIAMETER_MM ** 2 / 4.0
    pin_shear = force_n / (2.0 * area)
    pin_moment = force_n * TRUNNION_SUPPORTED_SPAN_MM / 4.0
    pin_bending = 32.0 * pin_moment / (pi * PIN_DIAMETER_MM ** 3)
    lug_bearing = force_n / (PIN_DIAMETER_MM * PLATE_THICKNESS_MM)
    return {
        "joint_code": JOINT_CODE,
        "design_force_n": force_n,
        "factory_hole_mm": FACTORY_HOLE_MM,
        "factory_eye_width_mockup_range_mm": FACTORY_EYE_WIDTH_MOCKUP_RANGE_MM,
        "factory_eye_outer_diameter_mm": 20.0,
        "inner_cradle_gap_mm": INNER_GAP_MM,
        "plate_thickness_mm": PLATE_THICKNESS_MM,
        "pin_diameter_mm": PIN_DIAMETER_MM,
        "trunnion_supported_span_mm": TRUNNION_SUPPORTED_SPAN_MM,
        "pin_double_shear_mpa": pin_shear,
        "pin_bending_mpa": pin_bending,
        "lug_bearing_mpa": lug_bearing,
        "passes_preliminary_static_screen": max(pin_shear, pin_bending, lug_bearing) < PRELIM_ALLOWABLE_MPA,
        "kinematic_center_offset_mm": 0.0,
        "allowed_rotations": "factory pin axis plus orthogonal trunnion axis",
        "selection_status": "preferred_measured_mockup_seed",
        "fabrication_note": (
            "Use an inner cradle around the factory eye and two opposed M8 shoulder-screw trunnions. "
            "Do not run a second full through-pin across the factory pin."
        ),
        "open_measurements": (
            "selected 450 lbf 8-inch front/rear eye thickness, side-face flatness, pin shoulder stack, "
            "available sweep around the actuator housing, shoulder-screw engagement and retention"
        ),
    }


def summary():
    return {
        "serial_adapter": serial_adapter_workspace_screen(),
        "nested_gimbal": nested_gimbal_pin_screen(),
        "phase_gate": "STATIC_BENCH_POC_MEASURED_MOCKUP_REQUIRED",
    }


if __name__ == "__main__":
    print(summary())
