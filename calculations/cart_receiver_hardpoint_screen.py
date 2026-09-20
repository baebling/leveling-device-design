from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calculations.cart_profile_receiver_screen import (
    locator_and_latch_screen,
    rest_pad_reaction_screen,
)


PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA = 30.0
PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA = 80.0
PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA = 120.0


def locator_insert_screen(pin_diameter_mm=12.0, insert_thickness_mm=8.0):
    """First-order bearing check for a cart locator insert plate."""
    loads = locator_and_latch_screen()
    shear_n = loads["master_locator_single_point_shear_n"]
    yaw_n = loads["yaw_couple_force_at_locator_span_n"]
    design_load_n = shear_n + yaw_n
    bearing_mpa = design_load_n / (pin_diameter_mm * insert_thickness_mm)
    return {
        "component": "CR-01 locator insert plate",
        "pin_diameter_mm": pin_diameter_mm,
        "insert_thickness_mm": insert_thickness_mm,
        "shear_load_n": shear_n,
        "yaw_couple_force_n": yaw_n,
        "combined_screen_load_n": design_load_n,
        "bearing_mpa": bearing_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "preferred_material_note": "steel or hardened bushing at repeated locator contact",
        "source_ids": "SRC-GDE-003; SRC-GDE-004",
    }


def rest_pad_insert_screen(pad_contact_length_mm=40.0, pad_contact_width_mm=30.0,
                           insert_thickness_mm=8.0):
    """Bearing/contact screen for a shim-adjustable rest pad insert."""
    pad = rest_pad_reaction_screen()
    load_n = pad["max_pad_load_n"]
    area_mm2 = pad_contact_length_mm * pad_contact_width_mm
    contact_pressure_mpa = load_n / area_mm2
    return {
        "component": "CR-01 shim-adjustable rest pad insert",
        "pad_contact_length_mm": pad_contact_length_mm,
        "pad_contact_width_mm": pad_contact_width_mm,
        "insert_thickness_mm": insert_thickness_mm,
        "max_pad_load_n": load_n,
        "contact_area_mm2": area_mm2,
        "contact_pressure_mpa": contact_pressure_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": contact_pressure_mpa <= PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "shim_adjustment_required": pad["shim_adjustment_required"],
        "source_ids": "SRC-GDE-004",
    }


def latch_keeper_screen(latch_count=4, keeper_thickness_mm=5.0, keeper_width_mm=25.0):
    """Simple bearing screen for latch keeper uplift load."""
    loads = locator_and_latch_screen(latch_count=latch_count)
    per_latch_n = loads["per_latch_uplift_n"]
    bearing_mpa = per_latch_n / (keeper_width_mm * keeper_thickness_mm)
    return {
        "component": "CR-01 latch keeper plate",
        "latch_count": latch_count,
        "per_latch_uplift_n": per_latch_n,
        "keeper_width_mm": keeper_width_mm,
        "keeper_thickness_mm": keeper_thickness_mm,
        "bearing_mpa": bearing_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "secondary_lock_required": True,
        "latch_closed_sensor_required": True,
        "latch_is_primary_shear_path": False,
        "source_ids": "SRC-LAT-001; SRC-LAT-004",
    }


def profile_fastener_slip_screen(fasteners_per_hardpoint=2,
                                 assumed_clamp_per_fastener_n=4000.0,
                                 friction_coefficient=0.15):
    """Very rough slip screen for a bolted insert-to-profile hard point.

    The final design should not rely on friction alone for locating. This
    only checks whether a modest clamp assumption is obviously too small.
    """
    loads = locator_and_latch_screen()
    demand_n = loads["master_locator_single_point_shear_n"] + loads["yaw_couple_force_at_locator_span_n"]
    slip_capacity_n = fasteners_per_hardpoint * assumed_clamp_per_fastener_n * friction_coefficient
    return {
        "component": "CR-01 insert-to-profile fastening",
        "fasteners_per_hardpoint": fasteners_per_hardpoint,
        "assumed_clamp_per_fastener_n": assumed_clamp_per_fastener_n,
        "friction_coefficient": friction_coefficient,
        "screen_demand_n": demand_n,
        "slip_capacity_n": slip_capacity_n,
        "slip_margin": slip_capacity_n / demand_n,
        "passes_placeholder_screen": slip_capacity_n >= 3.0 * demand_n,
        "anti_slip_note": "Do not use this as the final locating method; add dowel/key/positive stop after alignment.",
        "source_ids": "SRC-STD-004; SRC-FRM-001",
    }


def insert_plate_bending_screen(load_n=None, cantilever_mm=25.0, plate_width_mm=40.0,
                                plate_thickness_mm=6.0):
    """Conservative small cantilever strip check for a local keeper/stop tab."""
    if load_n is None:
        load_n = locator_and_latch_screen()["master_locator_single_point_shear_n"]
    moment_nmm = load_n * cantilever_mm
    section_modulus_mm3 = plate_width_mm * plate_thickness_mm ** 2 / 6.0
    bending_mpa = moment_nmm / section_modulus_mm3
    return {
        "component": "CR-01 local keeper/stop tab bending strip",
        "load_n": load_n,
        "cantilever_mm": cantilever_mm,
        "plate_width_mm": plate_width_mm,
        "plate_thickness_mm": plate_thickness_mm,
        "bending_mpa": bending_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
        "passes_placeholder_screen": bending_mpa <= PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
        "source_ids": "SRC-STD-004; SRC-GDE-003; SRC-GDE-004",
    }


def recommended_hardpoint_set():
    return {
        "locator_insert": "12 mm locator interface in 8 mm local steel insert or hardened bushing",
        "rest_pad_insert": "40 x 30 mm contact seed on 8 mm local aluminum/steel pad with shim stack",
        "latch_keeper": "5 mm local steel keeper seed; latch remains preload/uplift only",
        "profile_fastening": "two M8-class T-slot fasteners per critical hard point as a starting topology",
        "anti_slip": "add dowel/key/positive stop after alignment instead of relying on slot friction",
        "fabrication_status": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def summary():
    return {
        "recommended_hardpoint_set": recommended_hardpoint_set(),
        "locator_insert": locator_insert_screen(),
        "rest_pad_insert": rest_pad_insert_screen(),
        "latch_keeper_4_latch": latch_keeper_screen(latch_count=4),
        "latch_keeper_2_latch": latch_keeper_screen(latch_count=2),
        "profile_fastener_slip": profile_fastener_slip_screen(),
        "local_plate_bending": insert_plate_bending_screen(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
