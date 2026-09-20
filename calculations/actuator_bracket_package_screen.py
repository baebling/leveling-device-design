"""Preliminary HRT8E-style actuator bracket package screen.

This Phase 1 screen defines a low-load, centered double-shear bracket seed.
It intentionally does not create a fabrication drawing or freeze any supplier
hardware, tolerances, welds, or attachment pattern.
"""

from math import cos, pi, radians, sin
from pathlib import Path
import os
import sys


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calculations.joint_candidate_screen import ANGLE_MARGIN_DEG
from calculations.load_distribution import worst_case
from calculations.mobility_analysis import joint_articulation_summary


HRT8E_ALLOWABLE_ARTICULATION_DEG = 14.0
HRT8E_AXIAL_STATIC_LIMIT_N = 5290.0
HRT8E_RADIAL_STATIC_LIMIT_N = 26770.0
HRT8E_FATIGUE_LOAD_N = 5540.0
ACTIVE_ANGLE_DEG = 3.0
ACTIVE_DESIGN_FACTOR = 2.0
ACTIVE_ECCENTRICITY_MM = 100.0
STATIC_CAPACITY_SCREEN_FACTOR = 2.0
BRACKET_SEED_CODE = "JNT-BR-01-HRT8E"
PIN_DIAMETER_SEED_MM = 8.0
LUG_THICKNESS_SEED_MM = 8.0
HRT8E_BORE_MM = 8.0
HRT8E_BODY_DIAMETER_MM = 23.0
HRT8E_EYE_WIDTH_MM = 11.0
MAX_SUPPORTED_PIN_SPAN_SEED_MM = 18.0
LUG_LOAD_WIDTH_SEED_MM = 32.0
LUG_ROOT_FREE_LENGTH_SEED_MM = 30.0
PRELIM_ALLOWABLE_PIN_SHEAR_MPA = 100.0
PRELIM_ALLOWABLE_PIN_BENDING_MPA = 150.0
PRELIM_ALLOWABLE_LUG_BEARING_MPA = 100.0
PRELIM_ALLOWABLE_LUG_BENDING_MPA = 150.0


def circular_area_mm2(diameter_mm):
    return pi * diameter_mm ** 2 / 4.0


def active_bracket_load_case():
    """Use the existing active +/-3 degree, DF 2.0, 100 mm eccentricity case."""
    force = worst_case(
        angle_deg=ACTIVE_ANGLE_DEG,
        design_factor=ACTIVE_DESIGN_FACTOR,
        max_eccentricity_mm=ACTIVE_ECCENTRICITY_MM,
    )
    return {
        "basis": "active low-load user-confirmed baseline; worst_case(+/-3 deg, DF 2.0, 100 mm eccentricity)",
        "angle_deg": ACTIVE_ANGLE_DEG,
        "design_factor": ACTIVE_DESIGN_FACTOR,
        "max_eccentricity_mm": ACTIVE_ECCENTRICITY_MM,
        **force,
    }


def hrt8e_articulation_screen(angle_deg=ACTIVE_ANGLE_DEG):
    articulation = joint_articulation_summary(angle_deg)
    required_angle_deg = max(
        articulation["maximum_lower_joint_deviation_deg"],
        articulation["maximum_upper_joint_deviation_deg"],
    ) + ANGLE_MARGIN_DEG
    residual_angle_margin_deg = HRT8E_ALLOWABLE_ARTICULATION_DEG - required_angle_deg
    return {
        "component": "HRT8E-style rod-end articulation in bracket",
        "angle_case_deg": angle_deg,
        "maximum_lower_joint_deviation_deg": articulation["maximum_lower_joint_deviation_deg"],
        "maximum_upper_joint_deviation_deg": articulation["maximum_upper_joint_deviation_deg"],
        "angle_margin_deg": ANGLE_MARGIN_DEG,
        "required_articulation_deg": required_angle_deg,
        "catalog_allowable_articulation_deg": HRT8E_ALLOWABLE_ARTICULATION_DEG,
        "residual_angle_margin_deg": residual_angle_margin_deg,
        "passes_placeholder_screen": residual_angle_margin_deg >= 0.0,
        "bracket_clearance_rule": "Bracket must not contact the rod-end body through the full 14 deg catalog articulation envelope.",
        "source_ids": "SRC-JNT-006",
    }


def hrt8e_axial_capacity_screen(static_screen_factor=STATIC_CAPACITY_SCREEN_FACTOR):
    load = active_bracket_load_case()
    required_static_capacity_n = load["max_axial_force_n"] * static_screen_factor
    return {
        "component": "HRT8E-style rod-end axial capacity",
        **load,
        "static_capacity_screen_factor": static_screen_factor,
        "required_static_capacity_n": required_static_capacity_n,
        "catalog_axial_static_limit_n": HRT8E_AXIAL_STATIC_LIMIT_N,
        "catalog_radial_static_limit_n": HRT8E_RADIAL_STATIC_LIMIT_N,
        "catalog_fatigue_load_n": HRT8E_FATIGUE_LOAD_N,
        "axial_static_margin": HRT8E_AXIAL_STATIC_LIMIT_N / required_static_capacity_n,
        "passes_placeholder_screen": HRT8E_AXIAL_STATIC_LIMIT_N >= required_static_capacity_n,
        "capacity_basis_rule": "Use the catalog axial static limit for actuator-axis screening; do not substitute the higher radial limit.",
        "source_ids": "SRC-JNT-006",
    }


def centered_double_shear_screen(pin_diameter_mm=PIN_DIAMETER_SEED_MM,
                                 lug_thickness_mm=LUG_THICKNESS_SEED_MM,
                                 supported_pin_span_mm=MAX_SUPPORTED_PIN_SPAN_SEED_MM,
                                 lug_load_width_mm=LUG_LOAD_WIDTH_SEED_MM,
                                 lug_root_free_length_mm=LUG_ROOT_FREE_LENGTH_SEED_MM):
    """Screen pin/lug stresses for a centered two-lug yoke.

    The pin-bending model is a simply supported pin with the resultant centered
    between lug inner faces. The 18 mm span is a revised CAD seed based on the
    official 23 mm body diameter, 11 mm eye width and 14 degree envelope.
    """
    load = active_bracket_load_case()
    force_n = load["max_axial_force_n"]
    pin_area_mm2 = circular_area_mm2(pin_diameter_mm)
    pin_shear_mpa = force_n / (2.0 * pin_area_mm2)
    pin_moment_nmm = force_n * supported_pin_span_mm / 4.0
    pin_bending_mpa = 32.0 * pin_moment_nmm / (pi * pin_diameter_mm ** 3)
    lug_bearing_mpa = force_n / (pin_diameter_mm * lug_thickness_mm)
    force_per_lug_n = force_n / 2.0
    lug_root_moment_nmm = force_per_lug_n * lug_root_free_length_mm
    lug_section_modulus_mm3 = lug_load_width_mm * lug_thickness_mm ** 2 / 6.0
    lug_root_bending_mpa = lug_root_moment_nmm / lug_section_modulus_mm3
    supported_span_ok = supported_pin_span_mm <= MAX_SUPPORTED_PIN_SPAN_SEED_MM
    return {
        "component": "JNT-BR-01 centered double-shear yoke local screen",
        **load,
        "pin_diameter_mm": pin_diameter_mm,
        "lug_thickness_mm": lug_thickness_mm,
        "supported_pin_span_mm": supported_pin_span_mm,
        "lug_load_width_mm": lug_load_width_mm,
        "lug_root_free_length_mm": lug_root_free_length_mm,
        "pin_double_shear_mpa": pin_shear_mpa,
        "pin_bending_mpa": pin_bending_mpa,
        "lug_bearing_mpa": lug_bearing_mpa,
        "lug_root_bending_mpa": lug_root_bending_mpa,
        "allowable_pin_shear_mpa": PRELIM_ALLOWABLE_PIN_SHEAR_MPA,
        "allowable_pin_bending_mpa": PRELIM_ALLOWABLE_PIN_BENDING_MPA,
        "allowable_lug_bearing_mpa": PRELIM_ALLOWABLE_LUG_BEARING_MPA,
        "allowable_lug_bending_mpa": PRELIM_ALLOWABLE_LUG_BENDING_MPA,
        "supported_pin_span_ok": supported_span_ok,
        "passes_placeholder_screen": (
            supported_span_ok
            and pin_shear_mpa <= PRELIM_ALLOWABLE_PIN_SHEAR_MPA
            and pin_bending_mpa <= PRELIM_ALLOWABLE_PIN_BENDING_MPA
            and lug_bearing_mpa <= PRELIM_ALLOWABLE_LUG_BEARING_MPA
            and lug_root_bending_mpa <= PRELIM_ALLOWABLE_LUG_BENDING_MPA
        ),
        "span_rule": "Keep the loaded inner-lug support span at or below the revised 18 mm CAD seed; recalculate if actual spacers require a wider stack.",
        "source_ids": "SRC-JNT-006; SRC-STD-004",
    }


def hrt8e_bracket_clearance_screen(inner_gap_mm=MAX_SUPPORTED_PIN_SPAN_SEED_MM,
                                    articulation_deg=HRT8E_ALLOWABLE_ARTICULATION_DEG):
    """Conservative projected-width check for the eye body between flat lugs."""
    angle = radians(articulation_deg)
    projected_width_mm = (
        HRT8E_EYE_WIDTH_MM * cos(angle)
        + HRT8E_BODY_DIAMETER_MM * sin(angle)
    )
    clearance_mm = inner_gap_mm - projected_width_mm
    return {
        "component": "HRT8E eye-body projected bracket clearance",
        "body_diameter_mm": HRT8E_BODY_DIAMETER_MM,
        "eye_width_mm": HRT8E_EYE_WIDTH_MM,
        "bore_mm": HRT8E_BORE_MM,
        "articulation_deg": articulation_deg,
        "inner_gap_mm": inner_gap_mm,
        "projected_width_mm": projected_width_mm,
        "total_clearance_mm": clearance_mm,
        "clearance_per_side_mm": clearance_mm / 2.0,
        "passes_placeholder_screen": clearance_mm > 1.0,
        "interpretation": "Numerical envelope only; V-01 physical diagonal sweep remains mandatory.",
        "source_ids": "SRC-JNT-006",
    }


def bracket_topology_candidates():
    return [
        {
            "code": "JNT-BR-01-A",
            "topology": "single_lug_or_single_shear_pin",
            "selection_status": "reject",
            "reason": "Does not provide the preferred centered double-shear pin support or boxed lug stiffness.",
        },
        {
            "code": "JNT-BR-01-B",
            "topology": "offset_threaded_shank_standoff",
            "selection_status": "reject",
            "reason": "Turns the M8 threaded shank into a cantilever; previous screen identified this as the load-path blocker.",
        },
        {
            "code": BRACKET_SEED_CODE,
            "topology": "centered_boxed_double_shear_yoke",
            "selection_status": "preferred_hardware_seed",
            "reason": "Uses two symmetric lugs and a centered pin to route force through the spherical-center load path without a threaded-shank spacer.",
        },
        {
            "code": "JNT-BR-01-R",
            "topology": "high_angle_link_ball_package",
            "selection_status": "reserve",
            "reason": "Keep only if HRT8E drawing or mock-up cannot preserve the full 14 deg articulation in the required envelope.",
        },
    ]


def recommended_bracket_seed():
    return {
        "code": BRACKET_SEED_CODE,
        "coordinate_system": (
            "J is the spherical-bearing center; +X follows the neutral actuator force line "
            "toward the actuator, +Y is the pin axis, and +Z completes the right-hand frame."
        ),
        "load_path": "Actuator resultant and pin axis intersect at J; no intentional threaded-shank standoff or spacer carries bending.",
        "bracket_form": "Two symmetric 8 mm steel lug plates tied into a boxed/base yoke; exact weld or bolt attachment to the module is open.",
        "pin_seed": "8 mm nominal through-pin in double shear; retain it with a positive mechanical feature after exact pin hardware is selected.",
        "pin_span_rule": "Loaded inner-lug support span <=18 mm revised CAD seed based on the official HRT8E envelope.",
        "lug_seed": "8 mm lug thickness, >=32 mm load width, <=30 mm free root length seed; actual edge distances and attachment remain open.",
        "articulation_rule": "Demonstrate no bracket contact through the full 14 deg catalog articulation envelope before freezing geometry.",
        "fallback": "Use the high-angle link-ball reserve if the actual HRT8E package cannot retain the required articulation without a standoff.",
        "fabrication_status": "PHASE_2_DETAILED_CAD_APPROVED_NOT_FOR_FABRICATION",
    }


def mockup_acceptance_rules():
    return {
        "go_no_go_articulation_deg": HRT8E_ALLOWABLE_ARTICULATION_DEG,
        "required_calculated_articulation_deg": hrt8e_articulation_screen()["required_articulation_deg"],
        "confirm_on_manufacturer_drawing": (
            "eye bore, eye width, ball/body envelope, threaded shank engagement, "
            "and permitted load direction"
        ),
        "reject_if": (
            "bracket contacts before required articulation, threaded shank acts as a bending spacer, "
            "pin support span exceeds the screened value without recalculation, or a single-shear lug carries the primary pin load"
        ),
        "keep_open": (
            "pin material/retention, lug material and joining method, exact bracket attachment, "
            "edge distances, fatigue/shock test, and purchased HRT8E drawing"
        ),
    }


def summary():
    return {
        "recommended_bracket_seed": recommended_bracket_seed(),
        "topology_candidates": bracket_topology_candidates(),
        "articulation": hrt8e_articulation_screen(),
        "axial_capacity": hrt8e_axial_capacity_screen(),
        "double_shear_local_screen": centered_double_shear_screen(),
        "hrt8e_bracket_clearance_screen": hrt8e_bracket_clearance_screen(),
        "mockup_acceptance_rules": mockup_acceptance_rules(),
        "phase_gate": "PHASE_2_DETAILED_CAD_APPROVED_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
