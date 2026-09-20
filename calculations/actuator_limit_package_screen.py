"""Preliminary LS-01 actuator-axis stop and switch package screen.

The package converts the existing actuator pin-to-pin limit hierarchy into
positions along two moving guide rods. It is a layout and static screen, not
an impact-capacity or safety-certification calculation.
"""

from math import pi

from cad.parameters import P
from calculations.travel_limit_hierarchy_screen import (
    ACTIVE_TOTAL_LIFTED_MASS_KG,
    PRELIMINARY_STATIC_STOP_FACTOR,
    length_hierarchy,
)


PACKAGE_CODE = "LS-01"
STOP_ROD_COUNT = 2
MIN_COLLAR_HOLDING_REQUIREMENT_FACTOR = 2.0

# Measurements extracted from the archived official vendor STEP coordinate
# system. They establish a traceable layout datum but are not a toleranced
# manufacturing drawing.
VENDOR_STEP_REAR_PIN_Y_MM = 38.5
VENDOR_STEP_FRONT_PIN_Y_MM = -279.517
VENDOR_STEP_BODY_Y_RANGE_MM = (-250.23, -6.67)


def vendor_mount_datum_screen():
    body_near_from_rear = VENDOR_STEP_REAR_PIN_Y_MM - VENDOR_STEP_BODY_Y_RANGE_MM[1]
    body_far_from_rear = VENDOR_STEP_REAR_PIN_Y_MM - VENDOR_STEP_BODY_Y_RANGE_MM[0]
    bracket_near = P.limit_fixed_guide_station_mm - P.limit_mb21_envelope_axial_mm / 2.0
    bracket_far = P.limit_fixed_guide_station_mm + P.limit_mb21_envelope_axial_mm / 2.0
    return {
        "source_step_pin_span_mm": VENDOR_STEP_REAR_PIN_Y_MM - VENDOR_STEP_FRONT_PIN_Y_MM,
        "official_nominal_retracted_pin_span_mm": P.actuator_retracted_mm,
        "source_step_fixed_body_zone_from_rear_pin_mm": (body_near_from_rear, body_far_from_rear),
        "mb21_envelope_mm": (
            P.limit_mb21_envelope_tangent_mm,
            P.limit_mb21_envelope_normal_mm,
            P.limit_mb21_envelope_axial_mm,
        ),
        "mb21_axial_range_from_rear_pin_mm": (bracket_near, bracket_far),
        "mb21_inside_source_step_body_zone": (
            bracket_near >= body_near_from_rear and bracket_far <= body_far_from_rear
        ),
        "near_end_reserve_mm": bracket_near - body_near_from_rear,
        "far_end_reserve_mm": body_far_from_rear - bracket_far,
        "moving_datum": "official front clevis pin centre",
        "moving_adapter_rule": (
            "Capture the clevis adapter or clevis shoulder with keyed faces; "
            "do not clamp or side-load the chrome rod."
        ),
        "limitation": (
            "STEP-derived body limits and MB21 envelope are layout evidence only. "
            "Firgelli has not yet accepted external stop reaction through MB21."
        ),
    }


def package_positions():
    hierarchy = length_hierarchy()
    hard_lower, hard_upper = hierarchy["hard_stop_guarded_range_mm"]
    electrical_lower, electrical_upper = hierarchy["electrical_limit_target_range_mm"]
    datum = P.limit_fixed_guide_station_mm + P.limit_crosshead_offset_from_top_mm

    def offset(length_mm):
        return length_mm - datum

    return {
        "package_code": PACKAGE_CODE,
        "active_variant": "LS-01M_STATIC_BENCH_MINIMAL",
        "external_electrical_limit_package_enabled": P.external_electrical_limit_package_enabled,
        "electrical_limit_path": "actuator internal non-adjustable limit switches",
        "mechanical_limit_path": "independent external twin-rod stop collars",
        "fixed_guide_station_from_base_pin_mm": P.limit_fixed_guide_station_mm,
        "moving_crosshead_offset_from_top_pin_mm": P.limit_crosshead_offset_from_top_mm,
        "lower_mechanical_collar_offset_from_crosshead_mm": offset(hard_lower),
        "lower_electrical_cam_offset_from_crosshead_mm": offset(electrical_lower),
        "upper_electrical_cam_offset_from_crosshead_mm": offset(electrical_upper),
        "upper_mechanical_collar_offset_from_crosshead_mm": offset(hard_upper),
        "electrical_to_mechanical_allowance_lower_mm": electrical_lower - hard_lower,
        "electrical_to_mechanical_allowance_upper_mm": hard_upper - electrical_upper,
        "rod_length_mm": P.limit_guide_rod_length_mm,
        "upper_collar_fits_on_rod": offset(hard_upper) + P.limit_collar_width_mm / 2.0 < P.limit_guide_rod_length_mm,
        "sequence": (
            "lower command -> lower electrical cam -> lower mechanical collars -> actuator retracted endpoint; "
            "upper command -> upper electrical cam -> upper mechanical collars -> actuator extended endpoint"
        ),
    }


def static_package_screen():
    design_load_n = (
        ACTIVE_TOTAL_LIFTED_MASS_KG
        * P.gravity_m_s2
        * PRELIMINARY_STATIC_STOP_FACTOR
    )
    load_per_rod_n = design_load_n / STOP_ROD_COUNT
    rod_area_mm2 = pi * P.limit_guide_rod_diameter_mm ** 2 / 4.0
    collar_face_area_mm2 = pi * (
        P.limit_collar_outer_diameter_mm ** 2
        - P.limit_guide_rod_diameter_mm ** 2
    ) / 4.0
    return {
        "design_package_static_load_n": design_load_n,
        "stop_rod_count": STOP_ROD_COUNT,
        "equal_share_load_per_rod_n": load_per_rod_n,
        "guide_rod_axial_stress_mpa": load_per_rod_n / rod_area_mm2,
        "collar_face_contact_pressure_mpa": load_per_rod_n / collar_face_area_mm2,
        "minimum_verified_axial_holding_per_collar_n": (
            load_per_rod_n * MIN_COLLAR_HOLDING_REQUIREMENT_FACTOR
        ),
        "warning": (
            "Static axial stress and face pressure are only geometry screens. Purchased collar push-off, "
            "fixed-carrier attachment, one-rod load concentration, impact energy, fatigue, and actuator-housing "
            "load acceptance remain unverified."
        ),
    }


def switch_candidate():
    return {
        "family": "Omron D4N",
        "active_in_current_variant": P.external_electrical_limit_package_enabled,
        "layout_seed": "roller-plunger, slow-action direct-opening contact candidate",
        "envelope_mm": (
            P.limit_switch_body_width_mm,
            P.limit_switch_body_depth_mm,
            P.limit_switch_body_length_mm,
        ),
        "roller_diameter_mm": P.limit_switch_roller_diameter_mm,
        "catalogue_pretravel_max_mm": 2.0,
        "catalogue_overtravel_min_mm": 4.0,
        "bracket_adjustment_each_direction_mm": P.limit_switch_adjustment_mm,
        "selection_note": (
            "D4N-4D32 is archived from the active static-bench prototype. Retain this reference only if "
            "the module later becomes mobile, unattended, higher-speed, or safety-reviewed."
        ),
    }


def summary():
    return {
        "positions": package_positions(),
        "vendor_mount_datum": vendor_mount_datum_screen(),
        "static_screen": static_package_screen(),
        "switch_candidate": switch_candidate(),
        "phase_gate": "PHASE_2_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    print(summary())
