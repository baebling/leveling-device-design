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

from calculations.cart_profile_receiver_screen import rest_pad_reaction_screen
from calculations.cart_receiver_connector_topology_screen import (
    PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA,
    connector_design_demand,
)
from calculations.cart_receiver_hardpoint_screen import (
    PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
    PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
    PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
    insert_plate_bending_screen,
)


HARDWARE_SEED_CODE = "CR-01-H4-S1"
LOCAL_UNCERTAINTY_FACTOR = 3.0
MASTER_LOCATOR_DIAMETER_MM = 12.0
LOCATOR_BUSHING_THICKNESS_MM = 8.0
SECONDARY_X_SLOT_LENGTH_SEED_MM = 20.0
REPLACEABLE_STOP_WIDTH_MM = 40.0
REPLACEABLE_STOP_CONTACT_HEIGHT_MM = 8.0
REPLACEABLE_STOP_THICKNESS_MM = 8.0
REPLACEABLE_STOP_CANTILEVER_MM = 25.0
OPTIONAL_DOWEL_DIAMETER_MM = 6.0
REST_PAD_CONTACT_MM = (40.0, 30.0)
BACKING_PLATE_SEED_MM = (60.0, 40.0, 6.0)
MIN_TOOL_ACCESS_CLEARANCE_MM = 25.0
SENSOR_ENVELOPE_RESERVE_MM = (25.0, 25.0, 35.0)


def local_connector_load(load_factor=LOCAL_UNCERTAINTY_FACTOR):
    """Apply the H3 local uncertainty factor to the H2 connector demand."""
    base_demand_n = connector_design_demand()["screen_demand_n"]
    return {
        "base_connector_demand_n": base_demand_n,
        "local_uncertainty_factor": load_factor,
        "local_screen_load_n": base_demand_n * load_factor,
        "basis": "CR-01-H2 connector demand with CR-01-H3 local uncertainty factor",
    }


def locator_bushing_screen(pin_diameter_mm=MASTER_LOCATOR_DIAMETER_MM,
                           bushing_thickness_mm=LOCATOR_BUSHING_THICKNESS_MM):
    """Screen a replaceable master-locator bushing at the local load level."""
    load = local_connector_load()
    bearing_area_mm2 = pin_diameter_mm * bushing_thickness_mm
    bearing_mpa = load["local_screen_load_n"] / bearing_area_mm2
    return {
        "component": "CR-01-H4 removable master locator bushing",
        "pin_diameter_mm": pin_diameter_mm,
        "bushing_thickness_mm": bushing_thickness_mm,
        "bearing_area_mm2": bearing_area_mm2,
        **load,
        "bearing_mpa": bearing_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "replacement_policy": "Use a removable bushing or insert, not a wear surface directly in the aluminum profile.",
        "source_ids": "SRC-GDE-003; SRC-GDE-004; SRC-STD-004",
    }


def replaceable_stop_block_screen(stop_width_mm=REPLACEABLE_STOP_WIDTH_MM,
                                  contact_height_mm=REPLACEABLE_STOP_CONTACT_HEIGHT_MM,
                                  thickness_mm=REPLACEABLE_STOP_THICKNESS_MM,
                                  cantilever_mm=REPLACEABLE_STOP_CANTILEVER_MM):
    """Screen a locally replaceable steel shoulder stop at 3x connector demand."""
    load = local_connector_load()
    contact_area_mm2 = stop_width_mm * contact_height_mm
    bearing_mpa = load["local_screen_load_n"] / contact_area_mm2
    bending = insert_plate_bending_screen(
        load_n=load["local_screen_load_n"],
        cantilever_mm=cantilever_mm,
        plate_width_mm=stop_width_mm,
        plate_thickness_mm=thickness_mm,
    )
    return {
        "component": "CR-01-H4 replaceable shoulder stop block",
        "stop_width_mm": stop_width_mm,
        "stop_contact_height_mm": contact_height_mm,
        "stop_thickness_mm": thickness_mm,
        "stop_cantilever_mm": cantilever_mm,
        "contact_area_mm2": contact_area_mm2,
        **load,
        "bearing_mpa": bearing_mpa,
        "bearing_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "bending_mpa": bending["bending_mpa"],
        "bending_allowable_mpa": PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA,
        "passes_placeholder_screen": (
            bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA
            and bending["bending_mpa"] <= PLACEHOLDER_STEEL_BENDING_ALLOWABLE_MPA
        ),
        "replacement_policy": "Make the stop a bolted wear item; final screw pattern and edge distances remain open.",
        "source_ids": "SRC-STD-004; SRC-FRM-001; SRC-GDE-003; SRC-GDE-004",
    }


def optional_alignment_dowel_screen(dowel_diameter_mm=OPTIONAL_DOWEL_DIAMETER_MM,
                                    plate_thickness_mm=LOCATOR_BUSHING_THICKNESS_MM):
    """Screen one post-alignment dowel; it remains optional during adjustment."""
    load = local_connector_load()
    shear_area_mm2 = math.pi * dowel_diameter_mm ** 2 / 4.0
    shear_mpa = load["local_screen_load_n"] / shear_area_mm2
    bearing_mpa = load["local_screen_load_n"] / (dowel_diameter_mm * plate_thickness_mm)
    return {
        "component": "CR-01-H4 optional post-alignment dowel",
        "dowel_diameter_mm": dowel_diameter_mm,
        "plate_thickness_mm": plate_thickness_mm,
        "shear_area_mm2": shear_area_mm2,
        **load,
        "shear_mpa": shear_mpa,
        "shear_allowable_mpa": PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA,
        "bearing_mpa": bearing_mpa,
        "bearing_allowable_mpa": PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": (
            shear_mpa <= PLACEHOLDER_STEEL_SHEAR_ALLOWABLE_MPA
            and bearing_mpa <= PLACEHOLDER_STEEL_BEARING_ALLOWABLE_MPA
        ),
        "use_policy": "Install only after the mock-up location is frozen; do not add a second round X/Y locator.",
        "source_ids": "SRC-STD-004; SRC-GDE-004",
    }


def rest_pad_hardware_screen(contact_length_mm=REST_PAD_CONTACT_MM[0],
                             contact_width_mm=REST_PAD_CONTACT_MM[1],
                             z_load_factor=LOCAL_UNCERTAINTY_FACTOR):
    """Screen the serviceable rest-pad contact without assigning it horizontal load."""
    pad = rest_pad_reaction_screen()
    screen_load_n = pad["max_pad_load_n"] * z_load_factor
    contact_area_mm2 = contact_length_mm * contact_width_mm
    contact_pressure_mpa = screen_load_n / contact_area_mm2
    return {
        "component": "CR-01-H4 shim-adjustable rest pad hardware",
        "contact_length_mm": contact_length_mm,
        "contact_width_mm": contact_width_mm,
        "contact_area_mm2": contact_area_mm2,
        "base_pad_load_n": pad["max_pad_load_n"],
        "z_load_factor": z_load_factor,
        "screen_load_n": screen_load_n,
        "contact_pressure_mpa": contact_pressure_mpa,
        "placeholder_allowable_mpa": PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "passes_placeholder_screen": contact_pressure_mpa <= PLACEHOLDER_ALUMINUM_BEARING_ALLOWABLE_MPA,
        "load_path_rule": "Pad transfers Z seating only; clamp screws retain the pad and shim pack, not primary X/Y shear.",
        "source_ids": "SRC-GDE-004; SRC-STD-004",
    }


def backing_plate_policy(mockup_shift_mm=0.0, torque_relaxation_fraction=0.0,
                         profile_wall_marked=False, latch_preload_changed=False):
    """Keep the first build adjustable, then add a backing bridge only on evidence."""
    add_backing_plate = (
        mockup_shift_mm > 0.2
        or torque_relaxation_fraction > 0.2
        or profile_wall_marked
        or latch_preload_changed
    )
    return {
        "default_stack": "two M8-class T-slot fasteners per critical hard point with accessible adjustment",
        "conditional_upgrade": "6 mm steel backing bridge seed, nominal 60 x 40 mm, if the mock-up trigger occurs",
        "backing_plate_seed_mm": BACKING_PLATE_SEED_MM,
        "mockup_shift_mm": mockup_shift_mm,
        "torque_relaxation_fraction": torque_relaxation_fraction,
        "profile_wall_marked": profile_wall_marked,
        "latch_preload_changed": latch_preload_changed,
        "add_backing_plate": add_backing_plate,
        "reason": "Preserve simple slot adjustment until measured shift, torque loss, marking, or preload drift warrants a stiffer local stack.",
        "source_ids": "SRC-FRM-001; SRC-STD-004",
    }


def recommended_hardware_seed():
    """Return a hardware-level seed while preserving H3's DOF role separation."""
    return {
        "code": HARDWARE_SEED_CODE,
        "master_locator": {
            "constraint": "fixed X/Y",
            "hardware": "12 mm removable round locator pin/bushing plus 40 x 8 mm replaceable shoulder stop face",
            "clamp": "two M8-class T-slot fasteners for adjustment and clamp",
            "repeatability": "one optional 6 mm dowel only after mock-up alignment is frozen",
        },
        "secondary_locator": {
            "constraint": "fixed Y; released X",
            "hardware": "12 mm nominal locator contact in a 20 mm X-slotted or diamond-style receiver seed",
            "clamp": "two M8-class T-slot fasteners for adjustment and clamp",
            "prohibition": "Do not use a second round X/Y pin or a second X shoulder stop.",
        },
        "rest_pad": {
            "constraint": "Z seating only",
            "hardware": "40 x 30 mm replaceable contact pad with accessible shim pack and two pad-retention screws",
            "service_rule": "Keep a 25 mm minimum tool corridor; do not make the pad a side stop.",
        },
        "latch_keeper": {
            "constraint": "preload and uplift retention only",
            "hardware": "5 mm local steel keeper with a separate mechanical secondary lock",
            "sensor_rule": "Reserve a 25 x 25 x 35 mm adjustable bracket envelope for separate latch-closed and cart-present sensors.",
            "prohibition": "Do not use the latch hook or either sensor as a horizontal shear path or mechanical stop.",
        },
        "backing_plate": "Start without a full backing bridge; add the 60 x 40 x 6 mm steel seed only if mock-up evidence triggers it.",
        "fabrication_status": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def implementation_open_items():
    return [
        "Exact T-slot nut family, fastener grade, torque, and profile compatibility.",
        "Final bushing material, fit, retention method, and supplier part number.",
        "Final shoulder-stop screw pattern, edge distances, and access direction.",
        "Whether the post-alignment dowel is needed after the 30-cycle mock-up.",
        "Latch model, secondary-lock form, and final sensor model/bracket placement.",
    ]


def summary():
    return {
        "recommended_hardware_seed": recommended_hardware_seed(),
        "master_locator_bushing": locator_bushing_screen(),
        "replaceable_stop_block": replaceable_stop_block_screen(),
        "optional_alignment_dowel": optional_alignment_dowel_screen(),
        "rest_pad_hardware": rest_pad_hardware_screen(),
        "backing_plate_default": backing_plate_policy(),
        "implementation_open_items": implementation_open_items(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
