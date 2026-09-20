from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cad.parameters import P
from calculations.interface_moments import interface_loads, worst_case
from calculations.latch_load import latch_screening
from calculations.user_confirmed_baseline import central_yaw_screen


HFS8_4040_MASS_KG_PER_M = 1.73
GFS8_4040_MASS_KG_PER_M = 2.17
ALUMINUM_DENSITY_KG_M3 = 2700.0
STEEL_DENSITY_KG_M3 = 7850.0

TARGET_EMPTY_CART_MASS_KG = 10.0
PREFERRED_RECEIVER_MASS_BUDGET_KG = 5.5
MAX_RECEIVER_MASS_BUDGET_KG = 7.0


def rectangular_plate_mass_kg(length_mm, width_mm, thickness_mm, density_kg_m3):
    volume_m3 = (length_mm / 1000.0) * (width_mm / 1000.0) * (thickness_mm / 1000.0)
    return volume_m3 * density_kg_m3


def mixed_hardpoint_mass_kg():
    """Placeholder hard-point allowance for Phase 1 mass screening, not a BOM."""
    rest_pad_blocks = 4 * rectangular_plate_mass_kg(60.0, 50.0, 8.0, ALUMINUM_DENSITY_KG_M3)
    locator_plates = 2 * rectangular_plate_mass_kg(60.0, 60.0, 8.0, STEEL_DENSITY_KG_M3)
    latch_keepers = 4 * rectangular_plate_mass_kg(50.0, 30.0, 5.0, STEEL_DENSITY_KG_M3)
    stop_tabs = 2 * rectangular_plate_mass_kg(60.0, 30.0, 6.0, STEEL_DENSITY_KG_M3)
    fastener_allowance = 0.75
    return rest_pad_blocks + locator_plates + latch_keepers + stop_tabs + fastener_allowance


def receiver_layout_screen(profile_mass_kg_per_m=HFS8_4040_MASS_KG_PER_M,
                           longitudinal_rails=2,
                           longitudinal_rail_length_mm=760.0,
                           cross_members=0,
                           cross_member_length_mm=560.0,
                           label="two_rail_hfs8_receiver_kit",
                           source_id="SRC-FRM-001"):
    profile_length_m = (
        longitudinal_rails * longitudinal_rail_length_mm
        + cross_members * cross_member_length_mm
    ) / 1000.0
    profile_mass_kg = profile_length_m * profile_mass_kg_per_m
    hardpoint_mass_kg = mixed_hardpoint_mass_kg()
    total_receiver_mass_kg = profile_mass_kg + hardpoint_mass_kg
    return {
        "layout": label,
        "source_id": source_id,
        "longitudinal_rails": longitudinal_rails,
        "longitudinal_rail_length_mm": longitudinal_rail_length_mm,
        "cross_members": cross_members,
        "cross_member_length_mm": cross_member_length_mm,
        "profile_length_m": profile_length_m,
        "profile_mass_kg_per_m": profile_mass_kg_per_m,
        "profile_mass_kg": profile_mass_kg,
        "hardpoint_mass_kg": hardpoint_mass_kg,
        "total_receiver_mass_kg": total_receiver_mass_kg,
        "fraction_of_10kg_cart": total_receiver_mass_kg / TARGET_EMPTY_CART_MASS_KG,
        "passes_preferred_mass_budget": total_receiver_mass_kg <= PREFERRED_RECEIVER_MASS_BUDGET_KG,
        "passes_max_mass_budget": total_receiver_mass_kg <= MAX_RECEIVER_MASS_BUDGET_KG,
        "fabrication_status": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def candidate_layouts():
    return [
        receiver_layout_screen(),
        receiver_layout_screen(
            cross_members=2,
            label="self_contained_hfs8_rectangular_receiver",
        ),
        receiver_layout_screen(
            profile_mass_kg_per_m=GFS8_4040_MASS_KG_PER_M,
            label="two_rail_gfs8_stiff_reserve",
            source_id="SRC-FRM-002",
        ),
        receiver_layout_screen(
            profile_mass_kg_per_m=GFS8_4040_MASS_KG_PER_M,
            cross_members=2,
            label="self_contained_gfs8_rectangular_reserve",
            source_id="SRC-FRM-002",
        ),
    ]


def preferred_receiver_zone():
    profile_size_mm = 40.0
    receiver_outer_length_mm = 760.0
    receiver_outer_width_mm = 560.0
    rail_center_y_mm = (receiver_outer_width_mm - profile_size_mm) / 2.0
    return {
        "coordinate_origin": "device center, X length direction, Y width direction",
        "receiver_outer_length_mm": receiver_outer_length_mm,
        "receiver_outer_width_mm": receiver_outer_width_mm,
        "rail_centerline_y_mm": (-rail_center_y_mm, rail_center_y_mm),
        "rest_pad_x_span_mm": 620.0,
        "rest_pad_y_span_mm": 520.0,
        "locator_x_span_mm": 520.0,
        "master_locator_candidate_xy_mm": (-260.0, 0.0),
        "slotted_secondary_locator_candidate_xy_mm": (260.0, 0.0),
        "latch_placeholder_count": 4,
        "latch_candidate_xy_mm": (
            (-330.0, -260.0),
            (-330.0, 260.0),
            (330.0, -260.0),
            (330.0, 260.0),
        ),
        "profile_note": "Two longitudinal aluminum-profile receiver rails; cart frame cross support is outside this module scope.",
        "hardpoint_note": "Use local metal inserts for locators, rest pads, latch keepers, and stop faces.",
    }


def rest_pad_reaction_screen(rest_pad_x_span_mm=620.0, rest_pad_y_span_mm=520.0):
    case = worst_case()
    vertical_n = case["maximum_vertical_interface_load_n"]
    pitch_moment_nm = abs(case["maximum_pitch_interface_moment_nm"])
    roll_moment_nm = abs(case["maximum_roll_interface_moment_nm"])
    base_per_pad_n = vertical_n / 4.0
    pitch_delta_per_pad_n = pitch_moment_nm / (2.0 * (rest_pad_x_span_mm / 1000.0))
    roll_delta_per_pad_n = roll_moment_nm / (2.0 * (rest_pad_y_span_mm / 1000.0))
    max_pad_load_n = base_per_pad_n + pitch_delta_per_pad_n + roll_delta_per_pad_n
    min_pad_load_n = base_per_pad_n - pitch_delta_per_pad_n - roll_delta_per_pad_n
    return {
        "basis": "active low-load worst interface moment",
        "vertical_design_load_n": vertical_n,
        "pitch_moment_nm": pitch_moment_nm,
        "roll_moment_nm": roll_moment_nm,
        "rest_pad_x_span_mm": rest_pad_x_span_mm,
        "rest_pad_y_span_mm": rest_pad_y_span_mm,
        "base_per_pad_n": base_per_pad_n,
        "pitch_delta_per_pad_n": pitch_delta_per_pad_n,
        "roll_delta_per_pad_n": roll_delta_per_pad_n,
        "max_pad_load_n": max_pad_load_n,
        "min_pad_load_n": min_pad_load_n,
        "all_pads_remain_compressive_in_screen": min_pad_load_n >= 0.0,
        "shim_adjustment_required": True,
    }


def locator_and_latch_screen(locator_x_span_mm=520.0, latch_count=4):
    latch = latch_screening(latch_count=latch_count)
    yaw = central_yaw_screen()
    yaw_couple_force_n = yaw["required_design_yaw_torque_nm"] / (locator_x_span_mm / 1000.0)
    return {
        "basis": "active low-load user-confirmed receiver screen",
        "locator_x_span_mm": locator_x_span_mm,
        "guide_pin_shear_design_n": latch["guide_pin_shear_design_n"],
        "master_locator_single_point_shear_n": latch["guide_pin_shear_design_n"],
        "two_locator_shared_shear_n": latch["guide_pin_shear_design_n"] / 2.0,
        "yaw_design_torque_nm": yaw["required_design_yaw_torque_nm"],
        "yaw_couple_force_at_locator_span_n": yaw_couple_force_n,
        "total_latch_uplift_design_n": latch["total_latch_uplift_design_n"],
        "latch_count": latch_count,
        "per_latch_uplift_n": latch["per_latch_uplift_n"],
        "latches_are_primary_shear_path": False,
    }


def summary():
    layouts = candidate_layouts()
    return {
        "preferred_zone": preferred_receiver_zone(),
        "preferred_layout": layouts[0],
        "candidate_layouts": layouts,
        "rest_pad_reactions": rest_pad_reaction_screen(),
        "locator_and_latch": locator_and_latch_screen(),
        "active_interface_case": interface_loads(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
