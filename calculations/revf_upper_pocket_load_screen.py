"""Preliminary static screening only; NOT APPROVED FOR FABRICATION.

Global coordinates: lower-centre origin, +X right, +Y front, +Z up;
roll about X, pitch about Y. For each A1/A2/A3, local u points from lower
R hinge toward actuator eye; t is the fixed tangential pin axis. Define
r = e*t from PHS6 ball centre to eye. A positive F is push along u;
negative is pull. The upper joint receives F*u and r cross (F*u).
The signed scalar F*e is the moment about t cross u for perpendicular
u,t; it is NOT a global-coordinate moment component. Unknown alignment
and distributed contact are not solved by this single-pin model.

Load path on every axis: eye -> diameter-6 pin -> PHS6 inner/outer race
-> pocket and M6 -> bracket -> multiple fasteners -> 3030 slot.
At the eye the pin reaction is -F*u plus an unknown contact couple.
The lower R balances actuator force and eccentric moment through its
bearings/support. Neither end may be assumed a moment-free two-force
member while retaining the 16 mm offset. Their actual reactions require
pose, bearing spacing, stiffness, and contact distributions: unverified.
"""
from itertools import product
import json
from math import isfinite, pi, sqrt

from cad.revf_upper_pocket_inputs import PocketInputs, load_inputs


def screen_loads(inputs: PocketInputs, force_n: float) -> dict[str, object]:
    """Return magnitudes for stress, preserve signed load/moment separately.

PocketInputs supplies dimensions, not capacities. Consequently no caller
can close the strength gate with this interface's dimensional data alone.
HCDGH hardness is not converted to guaranteed yield strength. Manufacturer
guaranteed strength and contact/retaining-ring capacity remain unknown.
"""
    dimensions = (inputs.pin_dmin_mm, inputs.eye_offset_mm,
                  inputs.phs_outer_d_mm, inputs.phs_outer_width_mm,
                  inputs.phs_ball_width_mm, *inputs.eye_hole_bounds_mm)
    if (not isfinite(force_n) or len(inputs.eye_hole_bounds_mm) != 2
            or any(not isfinite(v) or v <= 0 for v in dimensions)
            or inputs.eye_hole_bounds_mm[0] > inputs.eye_hole_bounds_mm[1]):
        raise ValueError("Finite load and positive, ordered dimensions required")
    moment = force_n * inputs.eye_offset_mm
    bending = 32 * abs(moment) / (pi * inputs.pin_dmin_mm ** 3)
    shear = abs(force_n) / (pi * inputs.pin_dmin_mm ** 2 / 4)
    equivalent = sqrt(bending ** 2 + 3 * shear ** 2)
    # Separate unresolved load checks: no guessed dimensions, Kt or capacities.
    gaps = {
        "pin_transition": "HCDGH head relief and ring groove Kt, delivered yield strength, continuous contact length and E5 ring axial capacity unknown",
        "eye_reaction": "Front eye bore bearing capacity, contact distribution and moment reaction unknown",
        "lower_hinge_reaction": "Lower R bearing spacing/capacities and actuator bending/couple closure unknown",
        "phs_contact": "Exact PHS6 manufacturer static/radial/axial and reversing contact capacities unknown; dynamic rating alone is insufficient",
        "m6_reversal": "Actual engagement length, material, thread stripping, tension/shear interaction, preload and locking under reversal unknown",
        "pocket_contact": "Housing-neck/pocket contact area, pressure distribution, capture under pull and local permissible bearing unknown",
        "bracket_web": "Web section, local stress concentration, material guarantee and peak stress/deflection unknown",
        "slot_attachment": "T-nut pullout/slip, bolt spacing/preload, friction, profile lip bearing and manufacturer slot capacities unknown",
        "tolerance_stack": "Delivered hole/pin/shim/ball-width/machining limits and shoulder-thread transition positions unknown",
        "three_axis_equilibrium": "All poses and eight simultaneous force-sign combinations need global force/moment and frame reaction closure",
    }
    checks = {key: {"status": "unverified", "capacity": None, "reason": reason}
              for key, reason in gaps.items()}
    return {
        "review_only": True,
        "status": "PRELIMINARY - NOT APPROVED FOR FABRICATION",
        "force_n": force_n,
        "direction": "push" if force_n > 0 else "pull" if force_n < 0 else "zero",
        "signed_moment_nmm": moment,
        "pin_bending_mpa": bending,
        "pin_shear_mpa": shear,
        "pin_von_mises_mpa": equivalent,
        "conditional_pin_proof_mpa": None,
        "conditional_pin_ratio": None,
        "required_yield_for_bending_sf_mpa": 1.5*bending,
        "required_yield_for_von_mises_sf_mpa": 1.5*equivalent,
        "pin_candidate": "HCDGH6-35; S45C equivalent 40-45HRC, hardness is not a yield guarantee",
        "ring_load_path": "E5 is axial retention only, not an extra primary actuator-load support",
        "target_static_safety_factor": 1.5,
        "conditional_ratio_is_joint_approval": False,
        "equations": {"bending": "32*abs(F*e)/(pi*d_min^3)",
                      "single_shear": "abs(F)/(pi*d_min^2/4)",
                      "simple_von_mises": "sqrt(sigma_b^2+3*tau_avg^2)"},
        "model_limits": "N, mm, MPa=N/mm^2. Cantilever pin surrogate; average single shear combined conservatively with outer-fibre bending, not a resolved contact stress field. Kt is not silently set to 1 for approval.",
        "tolerance_screen": {
            "pin_min_diameter_mm": inputs.pin_dmin_mm,
            "eye_bore_source_bounds_mm": list(inputs.eye_hole_bounds_mm),
            "pin_diameter_limits_mm": [inputs.pin_dmin_mm, inputs.pin_dmax_mm],
            "delivered_eye_bore_tolerance_mm": None,
            "conditional_clearance_by_eye_source": [
                {"eye_source_nominal_mm": h,
                 "diametral_clearance_limits_mm": [h-inputs.pin_dmax_mm,h-inputs.pin_dmin_mm],
                 "delivered_fit_verified": False}
                for h in inputs.eye_hole_bounds_mm],
            "clearance_scope": "Each eye source is a separate fixed nominal, NOT delivered eye tolerance; conditional bounds include both pin g6 limits only",
            "source_bounds_are_delivered_tolerances": False,
            "nominal_offset_mm": inputs.eye_offset_mm,
            "worst_case_effective_offset_mm": None,
            "nominal_eye_width_mm": 20.0,
            "nominal_ball_width_mm": inputs.phs_ball_width_mm,
            "nominal_shim_mm": 1.5,
            "nominal_grip_mm": 4.0 + 20.0 + inputs.phs_ball_width_mm + 1.5,
            "nominal_head_washer_mm": 4.0,
            "nominal_eye_shim_ball_stack_mm": 20.0 + inputs.phs_ball_width_mm + 1.5,
            "nominal_groove_gap_mm": .5,
            "ball_side_washer_candidate": "WSSB10-6-1.5, one per axis",
            "known_tolerance_min_gap_mm": .20,
            "known_tolerance_max_gap_mm": .82,
            "known_gap_excludes_unknown_eye_width": True,
            "continuous_shoulder_contact_length_mm": inputs.shoulder_contact_length_mm,
            "adverse_stack_verified": False,
            "required_bounds": ["maximum eye bore", "minimum pin diameter", "maximum eye/ball/shim widths", "minimum continuous shoulder length excluding fillets/thread transition", "pocket machining and alignment tolerances", "maximum effective eccentricity/contact lever arm"],
        },
        "checks": checks,
        "unverified": list(gaps),
        "source_evidence_gaps": list(inputs.unresolved_evidence),
        "fault_screen": {"status": "unverified", "stall_force_n": None,
                         "overload_verified": False, "fatigue_verified": False,
                         "note": "750 N is a conservative static review load in both signs, not verified pull rating or maximum fault force; 2000 N self-locking is not stall thrust."},
        "strength_gate": False,
        "purchase_release": False,
        "fabrication_release": False,
        "control_power_test_release": False,
        "motor_power_release": False,
    }


def build_review() -> dict[str, object]:
    """Enumerate each sign and all simultaneous combinations without claiming FEA."""
    return {
        "review_only": True,
        "scope": "3-RPS supervised indoor self-weight-only PoC; no cart, payload or person; three factory-finished new upper brackets and existing A1-A3 machining only; no separate stopper",
        "coordinate_system": "Lower centre origin; +X right, +Y front, +Z up; roll X, pitch Y",
        "axes": {axis: {"load_path": "eye -> diameter-6 pin -> PHS6 inner/outer race -> pocket/M6 -> bracket -> multiple fasteners -> 3030 slot",
                        "local_equilibrium": "r=e*t; F=F*u; M=r cross F. Eye, actuator and lower R must balance force AND eccentric couple; reactions unverified."}
                 for axis in ("A1", "A2", "A3")},
        "cases": [screen_loads(load_inputs(), f) for f in (-750.0, 750.0)],
        "simultaneous_cases": [{"forces_n": list(forces), "axis_order": ["A1", "A2", "A3"],
                                "global_equilibrium_verified": False}
                               for forces in product((-750.0, 750.0), repeat=3)],
        "strength_gate": False,
        "purchase_release": False,
        "fabrication_release": False,
        "control_power_test_release": False,
        "motor_power_release": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_review(), ensure_ascii=False, indent=2, allow_nan=False))
