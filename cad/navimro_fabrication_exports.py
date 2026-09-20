"""STEP, DXF and cut-list exports for the NAVIMRO fabrication baseline."""

import csv
from dataclasses import dataclass
from pathlib import Path

import ezdxf

from .navimro_fabrication_assembly import export_step_states
from .navimro_fabrication_parameters import N


@dataclass(frozen=True)
class FlatbarPart:
    part_no: str
    name: str
    length_mm: float
    quantity: int
    feature: str
    vendor_holes: str = "NO"


FLATBAR_PARTS = (
    FlatbarPart("NVR-P01", "universal_lower_mount_tab", 120.0, 4, "two_24x11_slots"),
    FlatbarPart("NVR-P03", "upper_joint_spreader", 100.0, 3, "two_24x9_slots"),
    FlatbarPart("NVR-P04", "lower_joint_spreader", 100.0, 3, "two_24x9_slots"),
    FlatbarPart("NVR-P16", "actuator_yoke_lug", 27.0, 12, "one_8.2_hole_15_from_end"),
    FlatbarPart("NVR-P06", "shaft_support_riser", 200.0, 2, "riser_base_and_LMF_transfer", "YES"),
    FlatbarPart("NVR-P07A", "cardan_lower_lug", 22.0, 2, "one_8.2_hole_minus_5"),
    FlatbarPart("NVR-P07B", "cardan_upper_lug", 24.0, 2, "one_8.2_hole_plus_4"),
    FlatbarPart("NVR-P08A", "cardan_lower_bridge", 100.0, 1, "cardan_lower_four_8.5_holes"),
    FlatbarPart("NVR-P08B", "cardan_upper_outer_bridge", 100.0, 2, "cardan_upper_two_8.5_holes"),
    FlatbarPart("NVR-P08C", "cardan_upper_center_bridge", 100.0, 1, "none"),
    FlatbarPart("NVR-P09", "bushing_transfer_tab", 76.0, 4, "transfer_drill_LMF12UU", "YES"),
    FlatbarPart("NVR-P10", "locator_plate", 120.0, 2, "one_11_hole_two_9_slots"),
    FlatbarPart("NVR-P11", "latch_spreader", 100.0, 4, "transfer_drill_CR3001", "YES"),
    FlatbarPart("NVR-P12", "latch_keeper", 70.0, 4, "transfer_drill_CR3001", "YES"),
    FlatbarPart("NVR-P13A", "fixed_Z_stop", 18.0, 4, "none"),
    FlatbarPart("NVR-P13B", "moving_Z_stop_inner", 32.0, 2, "two_8.5_holes_across_width"),
    FlatbarPart("NVR-P13C", "moving_Z_stop_outer", 40.0, 2, "one_13.2_hole_9_from_center"),
    FlatbarPart("NVR-P14", "cardan_cross_laminate", 50.0, 4, "line_drill_after_weld"),
    FlatbarPart("NVR-P17", "guide_riser_base_foot", 30.0, 4, "two_8.5_holes_across_width"),
)


PROFILE_CUTS = (
    ("NVR-F01", "upper_long_rail", "4040 aluminium profile", 840.0, 2, "square"),
    ("NVR-F02", "upper_end_and_cross_rail", "4040 aluminium profile", 660.0, 4, "square"),
    ("NVR-F04", "upper_center_spreader", "4040 aluminium profile", 420.0, 2, "square"),
    ("NVR-F05", "lower_long_rail", "4040 aluminium profile", 820.0, 2, "square"),
    ("NVR-F06", "lower_end_and_cross_rail", "4040 aluminium profile", 640.0, 5, "square"),
    ("NVR-F08", "vertical_guide_carriage", "4040 aluminium profile", 240.0, 1, "square"),
    ("NVR-C01", "cart_side_receiver_rail", "4040 aluminium profile", 760.0, 2, "square"),
    ("NVR-S01", "moving_vertical_guide_shaft", "12 mm linear shaft", 230.0, 2, "deburr"),
)


def flatbar_usage_mm():
    cut_length = sum(part.length_mm * part.quantity for part in FLATBAR_PARTS)
    cuts = sum(part.quantity for part in FLATBAR_PARTS)
    kerf = cuts * N.saw_kerf_mm
    stock_total = N.flatbar_stock_length_mm * N.flatbar_stock_count
    return cut_length, kerf, stock_total - cut_length - kerf


def _add_rectangle(msp, length, width):
    x, y = length / 2.0, width / 2.0
    msp.add_lwpolyline([(-x, -y), (x, -y), (x, y), (-x, y)], close=True, dxfattribs={"layer": "CUT_OUTER"})


def _add_slot(msp, center, overall_length, width):
    x, y = center
    radius = width / 2.0
    straight = overall_length - width
    x1, x2 = x - straight / 2.0, x + straight / 2.0
    msp.add_line((x1, y - radius), (x2, y - radius), dxfattribs={"layer": "CUT_HOLES"})
    msp.add_line((x2, y + radius), (x1, y + radius), dxfattribs={"layer": "CUT_HOLES"})
    msp.add_arc((x1, y), radius, 90, 270, dxfattribs={"layer": "CUT_HOLES"})
    msp.add_arc((x2, y), radius, 270, 90, dxfattribs={"layer": "CUT_HOLES"})


def _add_features(msp, part):
    feature = part.feature
    if feature == "two_24x11_slots":
        _add_slot(msp, (-35.0, 0.0), 24.0, 11.0)
        _add_slot(msp, (35.0, 0.0), 24.0, 11.0)
    elif feature == "one_8.2_hole_minus_5":
        msp.add_circle((-5.0, 0.0), 4.1, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "one_8.2_hole_plus_4":
        msp.add_circle((4.0, 0.0), 4.1, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "two_24x9_slots":
        _add_slot(msp, (-30.0, 0.0), 24.0, 9.0)
        _add_slot(msp, (30.0, 0.0), 24.0, 9.0)
    elif feature == "cardan_lower_four_8.5_holes":
        for x in (-30.0, 30.0):
            for y in (-14.0, 14.0):
                msp.add_circle((x, y), 4.25, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "cardan_upper_two_8.5_holes":
        for x in (-30.0, 30.0):
            msp.add_circle((x, 0.0), 4.25, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "one_8.2_hole_15_from_end":
        msp.add_circle((1.5, 0.0), 4.1, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "two_8.5_holes_across_width":
        for y in (-15.0, 15.0):
            msp.add_circle((0.0, y), 4.25, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "one_13.2_hole_9_from_center":
        msp.add_circle((-9.0, 0.0), 6.6, dxfattribs={"layer": "CUT_HOLES"})
    elif feature == "one_11_hole_two_9_slots":
        msp.add_circle((0.0, 0.0), 5.5, dxfattribs={"layer": "CUT_HOLES"})
        _add_slot(msp, (-38.0, 0.0), 18.0, 9.0)
        _add_slot(msp, (38.0, 0.0), 18.0, 9.0)


def export_flatbar_dxfs(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for part in FLATBAR_PARTS:
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4
        for layer in ("CUT_OUTER", "CUT_HOLES", "REFERENCE", "NOTES"):
            doc.layers.add(layer)
        msp = doc.modelspace()
        _add_rectangle(msp, part.length_mm, N.flatbar_width_mm)
        _add_features(msp, part)
        msp.add_line((-part.length_mm / 2.0, 0.0), (part.length_mm / 2.0, 0.0), dxfattribs={"layer": "REFERENCE"})
        note = f"{part.part_no} {part.name} QTY {part.quantity} | 50x6 SS400"
        msp.add_text(note, height=3.0, dxfattribs={"layer": "NOTES"}).set_placement((-part.length_mm / 2.0, -32.0))
        if part.vendor_holes == "YES":
            msp.add_text("NO VENDOR HOLES: CLAMP AND TRANSFER-DRILL AFTER RECEIPT", height=2.5, dxfattribs={"layer": "NOTES"}).set_placement((-part.length_mm / 2.0, 29.0))
        path = output_dir / f"{part.part_no}_{part.name}.dxf"
        doc.saveas(path)
        outputs.append(path)
    return outputs


def export_acrylic_dxf(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for layer in ("CUT_OUTER", "CUT_HOLES", "REFERENCE", "NOTES"):
        doc.layers.add(layer)
    msp = doc.modelspace()
    _add_rectangle(msp, N.platform_length_mm, N.platform_width_mm)
    holes = set()
    for x in (-400.0, -200.0, 0.0, 200.0, 400.0):
        holes.add((x, -350.0))
        holes.add((x, 350.0))
    for y in (-175.0, 0.0, 175.0):
        holes.add((-400.0, y))
        holes.add((400.0, y))
    for x, y in sorted(holes):
        msp.add_circle((x, y), 9.1, dxfattribs={"layer": "CUT_HOLES"})
    msp.add_circle((-N.locator_x_mm, 0.0), 5.5, dxfattribs={"layer": "CUT_HOLES"})
    _add_slot(msp, (N.locator_x_mm, 0.0), 24.0, 11.0)
    msp.add_text("NVR-U02 900x800x15 CLEAR ACRYLIC | NON-STRUCTURAL COVER", height=7.0, dxfattribs={"layer": "NOTES"}).set_placement((-430.0, -385.0))
    msp.add_text("CR-3001 HOLES OMITTED: TRANSFER-DRILL FROM DELIVERED CLAMPS", height=5.0, dxfattribs={"layer": "NOTES"}).set_placement((-300.0, 370.0))
    path = output_dir / "NVR-U02_upper_acrylic_deck.dxf"
    doc.saveas(path)
    return path


def export_cut_lists(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    profile_path = output_dir / "navimro_profile_and_shaft_cut_list.csv"
    with profile_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("part_no", "name", "material", "finished_length_mm", "quantity", "end_finish"))
        writer.writerows(PROFILE_CUTS)

    flatbar_path = output_dir / "navimro_flatbar_cut_list.csv"
    with flatbar_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("part_no", "name", "stock", "length_mm", "quantity", "feature", "vendor_transfer_drill"))
        for part in FLATBAR_PARTS:
            writer.writerow((part.part_no, part.name, "SS400 50x6", part.length_mm, part.quantity, part.feature, part.vendor_holes))
        cut, kerf, reserve = flatbar_usage_mm()
        writer.writerow(("SUMMARY", "cut_total", "2 x 6000 mm stock", cut, "", "", ""))
        writer.writerow(("SUMMARY", "kerf_allowance", "2 mm/cut", kerf, "", "", ""))
        writer.writerow(("SUMMARY", "remaining_reserve", "", reserve, "", "", ""))
    return [profile_path, flatbar_path]


def export_all(root):
    root = Path(root)
    step_dir = root / "outputs" / "navimro_fabrication" / "step"
    dxf_dir = root / "outputs" / "navimro_fabrication" / "dxf"
    table_dir = root / "outputs" / "navimro_fabrication" / "tables"
    outputs = export_step_states(step_dir)
    outputs.extend(export_flatbar_dxfs(dxf_dir))
    outputs.append(export_acrylic_dxf(dxf_dir))
    outputs.extend(export_cut_lists(table_dir))
    return outputs
