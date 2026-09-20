from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from calculations.cart_receiver_connector_topology_screen import (
    connector_design_demand,
    shoulder_stop_screen,
)
from calculations.cart_receiver_hardpoint_screen import (
    PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
    profile_fastener_slip_screen,
)


MOCKUP_CYCLES_FOR_RECEIVER_CHECK = 30
MAX_MEASURED_SHIFT_MM_BEFORE_BACKING_PLATE = 0.2
MAX_TORQUE_RELAXATION_FRACTION_BEFORE_BACKING_PLATE = 0.2
MIN_TOOL_ACCESS_CLEARANCE_MM = 25.0
SENSOR_ENVELOPE_RESERVE_MM = (25.0, 25.0, 35.0)


def hardpoint_stack_candidates():
    """Map CR-01-H2-B into hardpoint-specific connector stack rules."""
    return [
        {
            "hardpoint": "master_locator",
            "code": "CR-01-H3-L1",
            "primary_role": "repeatable X/Y location and horizontal shear",
            "constrained_axes": ("X", "Y"),
            "released_axes": (),
            "connector_stack": "two M8-class T-slot fasteners plus shoulder/key positive stop",
            "dowel_policy": "allowed after mock-up alignment",
            "backing_plate_policy": "conditional after shift or torque-relaxation test",
            "overconstraint_risk": "low if secondary locator remains slotted",
            "selection_status": "preferred_stack_seed",
        },
        {
            "hardpoint": "slotted_secondary_locator",
            "code": "CR-01-H3-L2",
            "primary_role": "yaw reference through separated Y reaction without overconstraining X",
            "constrained_axes": ("Y",),
            "released_axes": ("X",),
            "connector_stack": "two M8-class T-slot fasteners plus one-direction shoulder/key stop",
            "dowel_policy": "do not pin both X and Y; use slotted/diamond geometry",
            "backing_plate_policy": "conditional after shift or torque-relaxation test",
            "overconstraint_risk": "high if round dowel or stop blocks both X and Y",
            "selection_status": "preferred_stack_seed",
        },
        {
            "hardpoint": "rest_pad",
            "code": "CR-01-H3-RP",
            "primary_role": "Z seating and height trimming",
            "constrained_axes": ("Z",),
            "released_axes": ("X", "Y"),
            "connector_stack": "T-slot clamp plus accessible shim stack and lock feature",
            "dowel_policy": "normally not required unless pad creep appears in test",
            "backing_plate_policy": "reserve only",
            "overconstraint_risk": "medium if rest pads are used as hidden side stops",
            "selection_status": "preferred_stack_seed",
        },
        {
            "hardpoint": "latch_keeper",
            "code": "CR-01-H3-LK",
            "primary_role": "preload/uplift retention and latch-closed sensing",
            "constrained_axes": ("Z uplift retention",),
            "released_axes": ("primary horizontal shear",),
            "connector_stack": "T-slot clamp plus local steel keeper; sensor bracket reserve",
            "dowel_policy": "not a primary locating feature",
            "backing_plate_policy": "conditional if keeper flex or latch preload relaxes",
            "overconstraint_risk": "medium if latch hook is used to pull the cart sideways",
            "selection_status": "preferred_stack_seed",
        },
    ]


def profile_wall_bearing_screen(load_factor=3.0, bearing_length_mm=40.0,
                                bearing_height_mm=8.0):
    """Conservative local screen for stop load into a profile wall or local plate."""
    demand_n = connector_design_demand()["screen_demand_n"] * load_factor
    area_mm2 = bearing_length_mm * bearing_height_mm
    bearing_mpa = demand_n / area_mm2
    return {
        "component": "CR-01-H3 profile wall / stop backing bearing screen",
        "basis": "connector demand multiplied for local uncertainty",
        "base_connector_demand_n": connector_design_demand()["screen_demand_n"],
        "load_factor": load_factor,
        "screen_load_n": demand_n,
        "bearing_length_mm": bearing_length_mm,
        "bearing_height_mm": bearing_height_mm,
        "bearing_area_mm2": area_mm2,
        "bearing_mpa": bearing_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": bearing_mpa <= PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "source_ids": "SRC-FRM-001; SRC-STD-004",
    }


def slot_nut_clamp_bearing_screen(slot_nut_contact_length_mm=18.0,
                                  slot_nut_contact_width_mm=12.0):
    """Rough clamp contact pressure screen; exact slot nut geometry remains open."""
    slip = profile_fastener_slip_screen()
    clamp_n = slip["assumed_clamp_per_fastener_n"]
    area_mm2 = slot_nut_contact_length_mm * slot_nut_contact_width_mm
    pressure_mpa = clamp_n / area_mm2
    return {
        "component": "CR-01-H3 slot nut local clamp screen",
        "assumed_clamp_per_fastener_n": clamp_n,
        "slot_nut_contact_length_mm": slot_nut_contact_length_mm,
        "slot_nut_contact_width_mm": slot_nut_contact_width_mm,
        "contact_area_mm2": area_mm2,
        "clamp_contact_pressure_mpa": pressure_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": pressure_mpa <= PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "backing_plate_still_conditional": True,
        "source_ids": "SRC-FRM-001; SRC-STD-004",
    }


def mockup_acceptance_rules():
    return {
        "cycles": MOCKUP_CYCLES_FOR_RECEIVER_CHECK,
        "max_measured_hardpoint_shift_mm": MAX_MEASURED_SHIFT_MM_BEFORE_BACKING_PLATE,
        "max_fastener_torque_relaxation_fraction": MAX_TORQUE_RELAXATION_FRACTION_BEFORE_BACKING_PLATE,
        "add_backing_plate_if": (
            "hardpoint shift exceeds limit, fastener torque relaxes beyond limit, "
            "profile wall marks/indents, or latch preload changes after cycling"
        ),
        "add_dowel_if": (
            "alignment is finalized and repeatability is needed beyond slot adjustment"
        ),
        "reject_if": (
            "secondary locator blocks both X and Y, latch hook carries primary shear, "
            "or electrical sensor is used as a mechanical stop"
        ),
    }


def service_access_screen(tool_access_clearance_mm=MIN_TOOL_ACCESS_CLEARANCE_MM,
                          sensor_envelope_mm=SENSOR_ENVELOPE_RESERVE_MM):
    sensor_l, sensor_w, sensor_h = sensor_envelope_mm
    return {
        "component": "CR-01-H3 service and sensor access reserve",
        "minimum_tool_access_clearance_mm": tool_access_clearance_mm,
        "sensor_envelope_reserve_mm": sensor_envelope_mm,
        "sensor_envelope_volume_mm3": sensor_l * sensor_w * sensor_h,
        "latch_closed_sensor_required": True,
        "cart_present_sensor_required": True,
        "keep_sensor_separate_from_mechanical_stop": True,
        "passes_placeholder_screen": (
            tool_access_clearance_mm >= MIN_TOOL_ACCESS_CLEARANCE_MM
            and min(sensor_envelope_mm) >= 20.0
        ),
        "source_ids": "SRC-SAF-002; SRC-LAT-004",
    }


def recommended_detail_set():
    return {
        "code": "CR-01-H3",
        "master_locator": "fixed X/Y locator with H2-B stop and optional dowel after alignment",
        "secondary_locator": "slotted/diamond locator constraining Y only; avoid an X hard stop",
        "rest_pad": "shim-adjustable Z seating pad, not a hidden horizontal stop",
        "latch_keeper": "retention/preload keeper with secondary lock and sensor reserve",
        "backing_plate_rule": "reserve unless mock-up shift, torque relaxation, wall marking, or preload drift appears",
        "service_access": "keep at least 25 mm tool clearance and reserve a small latch/cart sensor envelope",
        "fabrication_status": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def summary():
    return {
        "recommended_detail_set": recommended_detail_set(),
        "hardpoint_stack_candidates": hardpoint_stack_candidates(),
        "profile_wall_bearing": profile_wall_bearing_screen(),
        "slot_nut_clamp_bearing": slot_nut_clamp_bearing_screen(),
        "h2_positive_stop_reference": shoulder_stop_screen(),
        "mockup_acceptance_rules": mockup_acceptance_rules(),
        "service_access": service_access_screen(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
