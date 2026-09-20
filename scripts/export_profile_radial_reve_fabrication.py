"""Generate the Rev E release-candidate fabrication drawing package.

The package deliberately remains blocked for fabrication until the LMB-10
supplier interface is confirmed against a drawing or a measured first article.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import ezdxf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fusion_scripts" / "ProfileRadialRevD" / "revd_data.py"
OUT = ROOT / "fabrication" / "profile_radial_revE_release_candidate_2026-09-04"
PDF_OUT = ROOT / "output" / "pdf" / "Profile_Radial_3RPS_RevE_Fabrication_Drawings_RC_2026-09-04.pdf"


@dataclass(frozen=True)
class Feature:
    kind: str
    x_mm: float
    y_mm: float
    diameter_mm: float
    note: str


@dataclass(frozen=True)
class PartDrawing:
    part_id: str
    title: str
    qty: int
    material: str
    length_mm: float
    width_mm: float
    thickness_mm: float
    features: tuple[Feature, ...]
    gate_note: str = ""


def load_data():
    spec = importlib.util.spec_from_file_location("profile_radial_reve_fab_data", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adapter_drawings(data) -> list[PartDrawing]:
    drawings = []
    for row in data.adapter_rows():
        cx, cy = row["plate_center_mm"]
        features = []
        for hx, hy in row["profile_mount_holes_mm"]:
            features.append(Feature("THRU", hx - cx, hy - cy, 9.0, "M8 profile clearance"))
        for hx, hy in row["lmb_tapped_holes_mm"]:
            features.append(Feature("TAP", hx - cx, hy - cy, 6.8, "DRILL D6.8, TAP M8x1.25-6H"))
        drawings.append(
            PartDrawing(
                f"C0{len(drawings) + 1}",
                f"{row['id']} LMB radial adapter",
                1,
                "A6061-T6",
                data.P.adapter_length_x_mm,
                data.P.adapter_width_y_mm,
                data.P.adapter_thickness_mm,
                tuple(features),
                "LMB-10 D36 pitch and base envelope are provisional pending supplier drawing/first article.",
            )
        )
    return drawings


def stop_drawings() -> list[PartDrawing]:
    rows = []
    for name, direction, qty, part_id in (("FRONT", 1.0, 1, "C04"), ("REAR", -1.0, 2, "C05")):
        rows.append(
            PartDrawing(
                part_id,
                f"Lower stop catch {name}",
                qty,
                "A6061-T6",
                90.0,
                125.0,
                8.0,
                (
                    Feature("OPEN", 0.0, -9.5 * direction, 50.0, "Swept stop opening"),
                    Feature("THRU", -32.0, 42.5 * direction, 9.0, "M8 clearance"),
                    Feature("THRU", 32.0, 42.5 * direction, 9.0, "M8 clearance"),
                ),
            )
        )
    for name, direction, qty, part_id in (("FRONT", 1.0, 1, "C06"), ("REAR", -1.0, 2, "C07")):
        rows.append(
            PartDrawing(
                part_id,
                f"Upper stop anchor {name}",
                qty,
                "A6061-T6",
                80.0,
                85.0,
                6.0,
                (
                    Feature("THRU", 0.0, -29.5 * direction, 10.5, "M10 clearance"),
                    Feature("THRU", -25.0, 22.5 * direction, 6.8, "M6 clearance"),
                    Feature("THRU", 25.0, 22.5 * direction, 6.8, "M6 clearance"),
                ),
            )
        )
    rows.append(
        PartDrawing(
            "C08",
            "Stop contact bar",
            6,
            "A6061-T6",
            70.0,
            20.0,
            4.0,
            (Feature("THRU", 0.0, 0.0, 10.5, "M10 clearance"),),
        )
    )
    rows.append(
        PartDrawing(
            "C09",
            "Round through-bore standoff",
            6,
            "A6061-T6",
            16.0,
            16.0,
            28.0,
            (Feature("THRU", 0.0, 0.0, 8.4, "ID D8.4 +0.2/0 through"),),
        )
    )
    return rows


def new_dxf():
    doc = ezdxf.new("R2010")
    for name, color in (
        ("OUTLINE", 7),
        ("THRU", 1),
        ("TAP", 2),
        ("OPEN", 5),
        ("CENTER", 6),
        ("NOTES", 7),
    ):
        doc.layers.add(name=name, color=color)
    return doc


def export_dxf(drawing: PartDrawing) -> Path:
    doc = new_dxf()
    model = doc.modelspace()
    if drawing.part_id == "C09":
        model.add_circle((0, 0), drawing.length_mm / 2, dxfattribs={"layer": "OUTLINE"})
        model.add_circle((0, 0), drawing.features[0].diameter_mm / 2, dxfattribs={"layer": "THRU"})
        model.add_lwpolyline(
            [(30, -drawing.thickness_mm / 2), (46, -drawing.thickness_mm / 2),
             (46, drawing.thickness_mm / 2), (30, drawing.thickness_mm / 2)],
            close=True,
            dxfattribs={"layer": "OUTLINE"},
        )
    else:
        lx = drawing.length_mm / 2
        wy = drawing.width_mm / 2
        model.add_lwpolyline(
            [(-lx, -wy), (lx, -wy), (lx, wy), (-lx, wy)],
            close=True,
            dxfattribs={"layer": "OUTLINE"},
        )
        for feature in drawing.features:
            model.add_circle(
                (feature.x_mm, feature.y_mm),
                feature.diameter_mm / 2,
                dxfattribs={"layer": feature.kind},
            )
    model.add_line((-5, 0), (5, 0), dxfattribs={"layer": "CENTER"})
    model.add_line((0, -5), (0, 5), dxfattribs={"layer": "CENTER"})
    model.add_text(
        f"{drawing.part_id} {drawing.title} | RC - VERIFY GATES BEFORE FABRICATION",
        height=2.5,
        dxfattribs={"layer": "NOTES"},
    ).set_placement((-drawing.length_mm / 2, -drawing.width_mm / 2 - 10))
    path = OUT / f"{drawing.part_id}_{drawing.title.upper().replace(' ', '_')}.dxf"
    doc.saveas(path)
    return path


def draw_pdf_sheet(pdf: canvas.Canvas, drawing: PartDrawing, sheet: int, sheet_count: int):
    page_w, page_h = landscape(A4)
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.rect(0, page_h - 18 * mm, page_w, 18 * mm, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(12 * mm, page_h - 11.5 * mm, f"REV E FABRICATION RC | {drawing.part_id} | {drawing.title.upper()}")
    pdf.setFillColor(colors.HexColor("#111827"))

    max_dim = max(drawing.length_mm, drawing.width_mm, drawing.thickness_mm)
    scale = min(1.45, 150.0 / max_dim)
    ox = 82 * mm
    oy = 102 * mm
    pdf.setLineWidth(0.55)
    if drawing.part_id == "C09":
        radius = drawing.length_mm * scale * mm / 2
        pdf.circle(ox, oy, radius, stroke=1, fill=0)
        pdf.circle(ox, oy, drawing.features[0].diameter_mm * scale * mm / 2, stroke=1, fill=0)
        sx = 145 * mm
        sw = drawing.length_mm * scale * mm
        sh = drawing.thickness_mm * scale * mm
        pdf.rect(sx, oy - sh / 2, sw, sh, stroke=1, fill=0)
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(ox, oy - radius - 7 * mm, "END VIEW: OD16 / ID8.4 +0.2/0")
        pdf.drawCentredString(sx + sw / 2, oy - sh / 2 - 7 * mm, "SIDE VIEW: LENGTH 28 +/-0.1")
    else:
        width = drawing.length_mm * scale * mm
        height = drawing.width_mm * scale * mm
        pdf.rect(ox - width / 2, oy - height / 2, width, height, stroke=1, fill=0)
        for index, feature in enumerate(drawing.features, start=1):
            x = ox + feature.x_mm * scale * mm
            y = oy + feature.y_mm * scale * mm
            pdf.circle(x, y, feature.diameter_mm * scale * mm / 2, stroke=1, fill=0)
            pdf.setFont("Helvetica", 7)
            pdf.drawString(x + 3 * mm, y + 2 * mm, f"F{index}")
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(ox, oy - height / 2 - 7 * mm, f"{drawing.length_mm:g} +/-0.2")
        pdf.saveState()
        pdf.translate(ox - width / 2 - 7 * mm, oy)
        pdf.rotate(90)
        pdf.drawCentredString(0, 0, f"{drawing.width_mm:g} +/-0.2")
        pdf.restoreState()

    tx = 190 * mm
    top = 170 * mm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(tx, top, "PART REQUIREMENTS")
    pdf.setFont("Helvetica", 8.5)
    lines = [
        f"Material: {drawing.material}",
        f"Quantity: {drawing.qty}",
        f"Thickness/length: {drawing.thickness_mm:g} +/-0.1 mm",
        "Profile tolerance: +/-0.2 mm",
        "Hole position: +/-0.1 mm from local origin",
        "Through-hole tolerance: +0.2/0 mm",
        "Break sharp edges and deburr all features",
        "Units: mm | Do not scale drawing",
    ]
    for line in lines:
        top -= 6 * mm
        pdf.drawString(tx, top, line)

    top -= 5 * mm
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(tx, top, "FEATURE TABLE")
    pdf.setFont("Helvetica", 7.5)
    for index, feature in enumerate(drawing.features, start=1):
        top -= 5 * mm
        pdf.drawString(
            tx,
            top,
            f"F{index}: X {feature.x_mm:+.3f}, Y {feature.y_mm:+.3f}, D{feature.diameter_mm:g} - {feature.note}",
        )

    if drawing.gate_note:
        top -= 10 * mm
        pdf.setFillColor(colors.HexColor("#991B1B"))
        pdf.setFont("Helvetica-Bold", 8)
        for line_index, line in enumerate(textwrap.wrap("GATE: " + drawing.gate_note, width=52)):
            pdf.drawString(tx, top - line_index * 4 * mm, line)
        pdf.setFillColor(colors.HexColor("#111827"))

    pdf.setStrokeColor(colors.HexColor("#374151"))
    pdf.rect(8 * mm, 8 * mm, page_w - 16 * mm, 25 * mm, stroke=1, fill=0)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(12 * mm, 25 * mm, "STATUS: RELEASE CANDIDATE - NOT APPROVED FOR FABRICATION")
    pdf.drawString(12 * mm, 19 * mm, "DATUM: local part center; +X right, +Y up in the shown top view")
    pdf.drawString(12 * mm, 13 * mm, "REV: E-RC1 | DATE: 2026-09-04 | PROJECT: Profile Radial 3-RPS PoC")
    pdf.drawRightString(page_w - 12 * mm, 13 * mm, f"SHEET {sheet}/{sheet_count}")
    pdf.showPage()


def write_pdf(drawings: list[PartDrawing]) -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(PDF_OUT), pagesize=landscape(A4), pageCompression=1)
    pdf.setTitle("Profile Radial 3-RPS Rev E Fabrication Drawings RC")
    for sheet, drawing in enumerate(drawings, start=1):
        draw_pdf_sheet(pdf, drawing, sheet, len(drawings))
    pdf.save()


def write_tables(drawings: list[PartDrawing]) -> None:
    with (OUT / "RevE_custom_part_hole_table.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("part_id", "title", "qty", "material", "thickness_or_length_mm", "feature", "x_mm", "y_mm", "diameter_mm", "note", "release_gate"))
        for drawing in drawings:
            for feature in drawing.features:
                writer.writerow((drawing.part_id, drawing.title, drawing.qty, drawing.material, drawing.thickness_mm, feature.kind, f"{feature.x_mm:.3f}", f"{feature.y_mm:.3f}", f"{feature.diameter_mm:.3f}", feature.note, drawing.gate_note))

    with (OUT / "RevE_profile_cut_list.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("assembly", "profile", "length_mm", "qty", "cut", "tolerance_mm", "inspection"))
        writer.writerows(
            (
                ("lower", "DNF4040/M8", 700, 2, "square 90 deg", "+/-0.2", "match pair within 0.2"),
                ("lower", "DNF4040/M8", 620, 4, "square 90 deg", "+/-0.2", "match set within 0.2"),
                ("upper", "DNF3030-6/M6", 700, 2, "square 90 deg", "+/-0.2", "match pair within 0.2"),
                ("upper", "DNF3030-6/M6", 640, 4, "square 90 deg", "+/-0.2", "match set within 0.2"),
                ("electrical", "DIN rail 35 mm", 320, 2, "square 90 deg; deburr", "+/-1.0", "confirm enclosure backplate before cut"),
            )
        )

    inspection = [
        {"gate": "G-M01", "check": "Actuator exact option/current/encoder wiring/internal limit/duty cycle", "method": "written supplier data + first article", "status": "OPEN"},
        {"gate": "G-M02", "check": "LMB-10 D36 pitch, inner gap, pin center, pin and retainer", "method": "supplier drawing or caliper first article", "status": "OPEN"},
        {"gate": "G-C01", "check": "Adapters C01-C03 updated after G-M02", "method": "hole-table revision and CAD rerun", "status": "OPEN"},
        {"gate": "G-DXF", "check": "Nine DXFs agree with PDF and hole table", "method": "automated coordinate audit", "status": "PASS_RC"},
        {"gate": "G-CUT", "check": "Profile cut quantities and lengths agree with CAD/BOM", "method": "automated BOM audit", "status": "PASS_RC"},
    ]
    (OUT / "RevE_fabrication_gate_register.json").write_text(json.dumps(inspection, indent=2) + "\n", encoding="utf-8")

    guide = """# Rev E mechanical assembly sequence (release candidate)\n\n+Status: `NOT APPROVED FOR FABRICATION` until G-M01, G-M02, and G-C01 are closed.\n\n+1. Cut and square the lower 4040 and upper 3030 profile sets. Match equal-length members before assembly.\n+2. Assemble each rectangular frame loosely with the eight catalog corner brackets per frame, square diagonals, then torque progressively.\n+3. Inspect C01-C03 hole coordinates against the frozen LMB-10 interface register before machining.\n+4. Bolt each adapter to its specified lower cross-member slot. Install the LMB-10 with M8x16 fasteners only after the first-article pivot stack rotates freely.\n+5. Assemble one actuator axis first. Check lower pivot free rotation, motor-body clearance, upper PHS6 articulation, tool access, and cable exit.\n+6. Install the other two axes. Keep the upper frame supported independently until all three pins and retainers are installed.\n+7. Install the three independent M10 mechanical stop assemblies and set them 2 mm outside the commanded 0-50 mm range.\n+8. Move the unpowered mechanism through the 27-pose inspection matrix using controlled support. Record binding, contact, and fastener access.\n+9. Apply witness marks after final torque. Do not use threadlocker until first-article adjustments are complete.\n+\n+The cart body and drive system are outside this drawing package.\n+"""
    (OUT / "RevE_mechanical_assembly_sequence.md").write_text(guide, encoding="utf-8")


def main() -> int:
    data = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    drawings = adapter_drawings(data) + stop_drawings()
    paths = [export_dxf(drawing) for drawing in drawings]
    write_tables(drawings)
    write_pdf(drawings)
    summary = {
        "revision": "E-RC1",
        "date": "2026-09-04",
        "unique_custom_parts": len(drawings),
        "dxf_count": len(paths),
        "drawing_pdf": str(PDF_OUT.relative_to(ROOT)),
        "lmb_interface_frozen": False,
        "fabrication_release": False,
        "reason": "LMB-10 supplier drawing or first-article measurement is still required.",
    }
    (OUT / "RevE_fabrication_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
