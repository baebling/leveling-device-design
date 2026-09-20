"""Export preliminary Rev D custom plate DXFs and coordinate tables."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import ezdxf


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fusion_scripts" / "ProfileRadialRevD" / "revd_data.py"
OUT = ROOT / "outputs" / "profile_radial_revD_fusion_native" / "fabrication"


def load_data():
    spec = importlib.util.spec_from_file_location("profile_radial_revd_fab_data", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def new_drawing():
    doc = ezdxf.new("R2010")
    for name, color in (
        ("OUTLINE", 7),
        ("M8_CLEARANCE_D9", 1),
        ("M8_TAP_DRILL_D6_8", 2),
        ("M6_CLEARANCE_D6_8", 3),
        ("M10_CLEARANCE_D10_5", 4),
        ("CUT_OPENING_D50", 5),
        ("CENTER", 6),
        ("NOTES", 7),
    ):
        doc.layers.add(name=name, color=color)
    return doc


def outline(model, length, width):
    x = length / 2.0
    y = width / 2.0
    model.add_lwpolyline(
        [(-x, -y), (x, -y), (x, y), (-x, y)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )
    model.add_line((-5.0, 0.0), (5.0, 0.0), dxfattribs={"layer": "CENTER"})
    model.add_line((0.0, -5.0), (0.0, 5.0), dxfattribs={"layer": "CENTER"})


def note(model, title, width):
    model.add_text(title, height=3.5, dxfattribs={"layer": "NOTES"}).set_placement(
        (-width / 2.0, -48.0)
    )
    model.add_text(
        "PRELIMINARY - VERIFY FIRST ARTICLE - NOT APPROVED FOR FABRICATION",
        height=2.2,
        dxfattribs={"layer": "NOTES"},
    ).set_placement((-width / 2.0, -54.0))


def circle(model, point, diameter, layer):
    model.add_circle(point, diameter / 2.0, dxfattribs={"layer": layer})


def save_adapter_dxfs(data, rows):
    for row in data.adapter_rows():
        cx, cy = row["center_mm"]
        doc = new_drawing()
        model = doc.modelspace()
        outline(model, data.P.adapter_length_x_mm, data.P.adapter_width_y_mm)
        for hx, hy in row["profile_mount_holes_mm"]:
            circle(model, (hx - cx, hy - cy), 9.0, "M8_CLEARANCE_D9")
            rows.append((row["id"], 1, 8.0, "M8 clearance", hx - cx, hy - cy, 9.0))
        for hx, hy in row["lmb_tapped_holes_mm"]:
            circle(model, (hx - cx, hy - cy), 6.8, "M8_TAP_DRILL_D6_8")
            rows.append((row["id"], 1, 8.0, "M8x1.25 tap drill", hx - cx, hy - cy, 6.8))
        note(
            model,
            f"{row['id']} LMB RADIAL ADAPTER {data.P.adapter_length_x_mm:.0f}x{data.P.adapter_width_y_mm:.0f}x{data.P.adapter_thickness_mm:.0f} A6061",
            90.0,
        )
        doc.saveas(
            OUT
            / f"{row['id']}_LMB_RADIAL_ADAPTER_{data.P.adapter_length_x_mm:.0f}x{data.P.adapter_width_y_mm:.0f}x{data.P.adapter_thickness_mm:.0f}.dxf"
        )


def save_stop_dxfs(rows):
    variants = (("FRONT", 1.0, 1), ("REAR", -1.0, 2))
    for name, direction, qty in variants:
        doc = new_drawing()
        model = doc.modelspace()
        outline(model, 90.0, 125.0)
        opening_y = -9.5 * direction
        mount_y = 42.5 * direction
        circle(model, (0.0, opening_y), 50.0, "CUT_OPENING_D50")
        rows.append((f"STOP_CATCH_{name}", qty, 8.0, "cut opening", 0.0, opening_y, 50.0))
        for x in (-32.0, 32.0):
            circle(model, (x, mount_y), 9.0, "M8_CLEARANCE_D9")
            rows.append((f"STOP_CATCH_{name}", qty, 8.0, "M8 clearance", x, mount_y, 9.0))
        note(model, f"STOP CATCH {name} 90x125x8 A6061", 90.0)
        doc.saveas(OUT / f"STOP_CATCH_{name}_90x125x8_D50.dxf")

        doc = new_drawing()
        model = doc.modelspace()
        outline(model, 80.0, 85.0)
        rod_y = -29.5 * direction
        profile_y = 22.5 * direction
        circle(model, (0.0, rod_y), 10.5, "M10_CLEARANCE_D10_5")
        rows.append((f"STOP_ANCHOR_{name}", qty, 6.0, "M10 clearance", 0.0, rod_y, 10.5))
        for x in (-25.0, 25.0):
            circle(model, (x, profile_y), 6.8, "M6_CLEARANCE_D6_8")
            rows.append((f"STOP_ANCHOR_{name}", qty, 6.0, "M6 clearance", x, profile_y, 6.8))
        note(model, f"STOP UPPER ANCHOR {name} 80x85x6 A6061", 80.0)
        doc.saveas(OUT / f"STOP_UPPER_ANCHOR_{name}_80x85x6.dxf")

    doc = new_drawing()
    model = doc.modelspace()
    outline(model, 70.0, 20.0)
    circle(model, (0.0, 0.0), 10.5, "M10_CLEARANCE_D10_5")
    rows.append(("STOP_CONTACT_BAR", 6, 4.0, "M10 clearance", 0.0, 0.0, 10.5))
    note(model, "STOP CONTACT BAR 70x20x4 A6061", 70.0)
    doc.saveas(OUT / "STOP_CONTACT_BAR_70x20x4_D10_5.dxf")


def save_tables(data, rows):
    table = OUT / "RevD_custom_part_hole_table.csv"
    with table.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("part", "part_qty", "thickness_mm", "feature", "x_mm", "y_mm", "diameter_mm"))
        writer.writerows(rows)

    cuts = OUT / "RevD_profile_cut_list.csv"
    with cuts.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("frame", "profile", "length_mm", "qty", "cut"))
        writer.writerow(("lower", "DNF4040/M8", 700, 2, "square 90 deg"))
        writer.writerow(("lower", "DNF4040/M8", 620, 4, "square 90 deg"))
        writer.writerow(("upper", "DNF3030-6/M6", 700, 2, "square 90 deg"))
        writer.writerow(("upper", "DNF3030-6/M6", 640, 4, "square 90 deg"))


def main():
    data = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    save_adapter_dxfs(data, rows)
    save_stop_dxfs(rows)
    save_tables(data, rows)
    print(f"Exported {len(list(OUT.glob('*.dxf')))} DXFs and 2 CSV tables to {OUT}")


if __name__ == "__main__":
    main()
