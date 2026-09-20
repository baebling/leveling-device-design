from pathlib import Path
import math
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calculations.cart_receiver_hardpoint_screen import (
    PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
    PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
    insert_plate_bending_screen,
    profile_fastener_slip_screen,
)


PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA = 80.0
POSITIVE_STOP_REQUIRED_FOR_FINAL_LOCATING = True


def connector_design_demand():
    """Return the CR-01-H1 demand that drives insert-to-profile connector choice."""
    slip = profile_fastener_slip_screen()
    return {
        "basis": "CR-01-H1 locator shear plus low-load yaw couple force",
        "screen_demand_n": slip["screen_demand_n"],
        "friction_only_slip_margin": slip["slip_margin"],
        "friction_only_passes_strength_screen": slip["passes_placeholder_screen"],
        "positive_stop_required_for_final_locating": POSITIVE_STOP_REQUIRED_FOR_FINAL_LOCATING,
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def shoulder_stop_screen(stop_width_mm=40.0, stop_contact_height_mm=8.0,
                         stop_tab_thickness_mm=6.0, stop_cantilever_mm=25.0):
    """Screen a local shoulder/key/positive stop that carries final shear."""
    demand = connector_design_demand()["screen_demand_n"]
    contact_area_mm2 = stop_width_mm * stop_contact_height_mm
    bearing_mpa = demand / contact_area_mm2
    bending = insert_plate_bending_screen(
        load_n=demand,
        cantilever_mm=stop_cantilever_mm,
        plate_width_mm=stop_width_mm,
        plate_thickness_mm=stop_tab_thickness_mm,
    )
    return {
        "component": "CR-01-H2 shoulder/key positive stop",
        "screen_demand_n": demand,
        "stop_width_mm": stop_width_mm,
        "stop_contact_height_mm": stop_contact_height_mm,
        "contact_area_mm2": contact_area_mm2,
        "bearing_mpa": bearing_mpa,
        "bearing_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "stop_tab_thickness_mm": stop_tab_thickness_mm,
        "stop_cantilever_mm": stop_cantilever_mm,
        "bending_mpa": bending["bending_mpa"],
        "bending_allowable_mpa": PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
        "passes_placeholder_screen": (
            bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA
            and bending["bending_mpa"] <= PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA
        ),
        "final_shear_path": True,
        "source_ids": "SRC-STD-004; SRC-FRM-001; SRC-GDE-003; SRC-GDE-004",
    }


def dowel_backup_screen(dowel_count=1, dowel_diameter_mm=6.0,
                        plate_thickness_mm=8.0):
    """Optional post-alignment dowel screen for repeatable anti-slip locating."""
    demand = connector_design_demand()["screen_demand_n"]
    shear_area_mm2 = dowel_count * math.pi * dowel_diameter_mm ** 2 / 4.0
    shear_mpa = demand / shear_area_mm2
    bearing_mpa = demand / (dowel_count * dowel_diameter_mm * plate_thickness_mm)
    return {
        "component": "CR-01-H2 optional alignment dowel",
        "screen_demand_n": demand,
        "dowel_count": dowel_count,
        "dowel_diameter_mm": dowel_diameter_mm,
        "plate_thickness_mm": plate_thickness_mm,
        "shear_area_mm2": shear_area_mm2,
        "shear_mpa": shear_mpa,
        "shear_allowable_mpa": PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA,
        "bearing_mpa": bearing_mpa,
        "bearing_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": (
            shear_mpa <= PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA
            and bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA
        ),
        "use_note": "Use after mock-up alignment when repeatability is more important than slot adjustability.",
        "source_ids": "SRC-STD-004; SRC-GDE-004",
    }


def connector_topology_candidates():
    demand = connector_design_demand()
    stop = shoulder_stop_screen()
    dowel = dowel_backup_screen()
    return [
        {
            "code": "CR-01-H2-A",
            "topology": "slot_friction_only",
            "selection_status": "reject_for_final_locating",
            "strength_screen": "numeric slip margin passes the placeholder check",
            "slip_margin": demand["friction_only_slip_margin"],
            "passes_phase_policy": False,
            "reason": "Profile slot friction is useful for mock-up adjustment but must not be the final locating or yaw shear path.",
        },
        {
            "code": "CR-01-H2-B",
            "topology": "slot_fasteners_plus_shoulder_stop",
            "selection_status": "preferred",
            "strength_screen": "positive stop bearing and tab bending pass placeholder checks",
            "positive_stop_bearing_mpa": stop["bearing_mpa"],
            "positive_stop_bending_mpa": stop["bending_mpa"],
            "optional_dowel_shear_mpa": dowel["shear_mpa"],
            "passes_phase_policy": True,
            "reason": "Keeps slot-nut adjustment during mock-up, then gives the aligned hard point a mechanical stop/key load path.",
        },
        {
            "code": "CR-01-H2-C",
            "topology": "slot_fasteners_plus_backing_clamp_plate",
            "selection_status": "reserve",
            "strength_screen": "likely adequate at current low loads but heavier and less compact",
            "passes_phase_policy": True,
            "reason": "Use if T-slot stiffness, local profile wall bearing, or repeated service adjustment is poor in bench tests.",
        },
        {
            "code": "CR-01-H2-D",
            "topology": "through_bolted_crossmember_or_cart_member",
            "selection_status": "conditional_reserve",
            "strength_screen": "robust when a real accessible cart member exists",
            "passes_phase_policy": True,
            "reason": "Do not assume cart-body holes or member geometry; keep only if the later cart frame deliberately provides access.",
        },
    ]


def recommended_connector_set():
    return {
        "code": "CR-01-H2-B",
        "profile_fasteners": "two M8-class T-slot fasteners per critical hard point for clamp and adjustment",
        "final_shear_path": "replaceable shoulder/key/positive stop face after mock-up alignment",
        "repeatability_option": "one 6 mm or larger dowel may be added after alignment if repeatability requires it",
        "backing_plate_reserve": "add backing clamp plate only if slot stiffness or service tests demand it",
        "reject": "slot friction alone is not an approved final locating method",
        "fabrication_status": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def summary():
    return {
        "demand": connector_design_demand(),
        "shoulder_stop": shoulder_stop_screen(),
        "optional_dowel": dowel_backup_screen(),
        "candidates": connector_topology_candidates(),
        "recommended_connector_set": recommended_connector_set(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
