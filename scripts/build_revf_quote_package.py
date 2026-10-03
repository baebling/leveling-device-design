"""Create the compact Rev F quotation package and dimensioned PDF."""

from __future__ import annotations

from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cad.revf_quote_package import (  # noqa: E402
    LOWER_PLATE_SPEC,
    LOWER_PLATE_SPECS,
    UPPER_BRACKET_SPEC,
    _mount_rotation_deg,
    export_quote_package,
)


def _font_name() -> str:
    candidates = (
        Path(r"C:\Windows\Fonts\malgun.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            name = "DrawingFont"
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(candidate)))
            return name
    return "Helvetica"


def _styles():
    font = _font_name()
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("drawing-title", parent=styles["Title"], fontName=font,
                                fontSize=19, leading=23, textColor=colors.HexColor("#19324D"),
                                alignment=TA_LEFT, spaceAfter=5 * mm),
        "h1": ParagraphStyle("drawing-h1", parent=styles["Heading1"], fontName=font,
                             fontSize=15, leading=18, textColor=colors.HexColor("#19324D"),
                             spaceAfter=3 * mm),
        "body": ParagraphStyle("drawing-body", parent=styles["BodyText"], fontName=font,
                               fontSize=9.2, leading=13, textColor=colors.HexColor("#202B33")),
        "small": ParagraphStyle("drawing-small", parent=styles["BodyText"], fontName=font,
                                fontSize=7.8, leading=10, textColor=colors.HexColor("#465866")),
        "warning": ParagraphStyle("drawing-warning", parent=styles["BodyText"], fontName=font,
                                  fontSize=9.2, leading=13, textColor=colors.HexColor("#9C2F20")),
        "center": ParagraphStyle("drawing-center", parent=styles["BodyText"], fontName=font,
                                 fontSize=9, leading=12, alignment=TA_CENTER),
    }


def _table(data, widths, font, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 8.2),
        ("LEADING", (0, 0), (-1, -1), 10.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, colors.HexColor("#CBD4DA")),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#19324D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]
    table.setStyle(TableStyle(commands))
    return table


def _header_footer(canvas, doc):
    canvas.saveState()
    font = _font_name()
    canvas.setFont(font, 7.5)
    canvas.setFillColor(colors.HexColor("#5E6D75"))
    canvas.drawString(14 * mm, 8 * mm, "Rev F quotation package - dimensions in mm")
    canvas.drawRightString(landscape(A4)[0] - 14 * mm, 8 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#19324D"))
    canvas.setLineWidth(0.6)
    canvas.line(14 * mm, landscape(A4)[1] - 11 * mm,
                landscape(A4)[0] - 14 * mm, landscape(A4)[1] - 11 * mm)
    canvas.restoreState()


def _lower_page(story, styles, part_id):
    spec = LOWER_PLATE_SPECS[part_id]
    story.append(Paragraph(f"{part_id} LOWER - LMB radial adapter", styles["h1"]))
    story.append(Paragraph(
        "A6061-T6 plate, 120 x 70 x 8. Datum is the plate centre. X is the 120 mm direction; "
        "Y is the 70 mm direction. No outline cutting beyond the ordered rectangle.", styles["body"]))
    story.append(Spacer(1, 4 * mm))
    rows = [["Hole", "X", "Y", "Machining", "Function"]]
    for i, (x, y) in enumerate(spec["profile_through"], 1):
        rows.append([f"P{i}", f"{x:.3f}", f"{y:.3f}", "D9 THRU", "profile bolt"])
    for i, (x, y) in enumerate(spec["lmb_tap_m8"], 1):
        rows.append([f"T{i}", f"{x:.3f}", f"{y:.3f}", "drill D6.8, tap M8x1.25 THRU", "LMB-10"])
    story.append(_table(rows, [24 * mm, 25 * mm, 25 * mm, 58 * mm, 48 * mm], _font_name()))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        "Machining notes: deburr all edges and holes; break sharp edges lightly. Keep the two M8 axes "
        "normal to the plate. Verify LMB-10 hole pitch against the delivered bracket before tapping. "
        "The STEP models threads as D6.8 pilot holes; this callout controls the thread.", styles["small"]))
    story.append(Spacer(1, 5 * mm))
    story.append(_table([
        ["Overall", "Material", "Profile holes", "LMB holes", "Surface"],
        ["120 x 70 x 8", "A6061-T6", "2 x D9 THRU", "2 x M8x1.25 THRU", "as-machined / deburred"],
    ], [45 * mm, 40 * mm, 45 * mm, 55 * mm, 55 * mm], _font_name()))
    story.append(PageBreak())


def _upper_page(story, styles, axis):
    d = UPPER_BRACKET_SPEC
    angle = _mount_rotation_deg(axis)
    story.append(Paragraph(f"UP-A{axis} - PHS6 supplier-finished pocket bracket", styles["h1"]))
    story.append(Paragraph(
        f"S45C untreated, one finished part. Local origin is the PHS6 ball centre. The mounting pad is "
        f"rotated {angle:.3f} degrees about local Z in the supplied STEP. Quote and machine from STEP; "
        "the DXF is mounting-face reference only.", styles["body"]))
    story.append(Spacer(1, 3 * mm))
    rows = [
        ["Feature", "Nominal dimension", "Manufacturing note"],
        ["Base", "60 x 30 x 9", "two D6.6 mount holes, pitch 44"],
        ["PHS6 saddle", "D20.2 x 6.75 wide", "STEP controls 3D pocket; remove burrs"],
        ["Saddle outside", "D28", "support ring joined to two 4 mm rails"],
        ["Centre fastener", "D6.6 THRU", "D11 counterbore x 6 deep from top"],
        ["Side insertion channel", "18.5 wide", "keep open for PHS6 housing installation"],
        ["Height", "ball centre to mount face: 39", "do not change without assembly re-check"],
    ]
    story.append(_table(rows, [50 * mm, 55 * mm, 125 * mm], _font_name()))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Suggested quote notes: general dimensional tolerance +/-0.2 unless the supplier proposes a "
        "different DFM tolerance; saddle D20.2 is a clearance feature, not a press fit; no heat treatment "
        "or plating; deburr C0.2 max. The supplier may propose tool-radius relief only if the PHS6 contact "
        "surface and the D20.2 clearance remain unchanged.", styles["small"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Critical assembly note: fit the PHS6 housing and its central M6x12 low-head retainer before the "
        "bracket is bolted to the upper profile. The bearing ball, actuator eye, pin and E-ring are separate "
        "parts and must not be clamped by the pocket.", styles["warning"]))
    story.append(PageBreak())


def build_drawing_pdf(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "RevF_custom_parts_dimensioned_drawings.pdf"
    styles = _styles()
    doc = SimpleDocTemplate(
        str(path), pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm,
        topMargin=17 * mm, bottomMargin=14 * mm, title="Rev F custom parts dimensioned drawings",
        author="BIZ-Lab leveling device project",
    )
    story = []
    story.append(Paragraph("Rev F custom metal parts - quotation package", styles["title"]))
    story.append(Paragraph(
        "Six custom parts only: three lower A6061 adapter plates and three supplier-finished S45C upper "
        "PHS6 pocket brackets. No cart, payload, or person. Supervised indoor self-weight PoC only.",
        styles["body"]))
    story.append(Spacer(1, 5 * mm))
    story.append(_table([
        ["Part", "Qty", "Material", "Required process", "Authoritative file"],
        ["A1/A2/A3 LOWER", "1 each", "A6061-T6", "rectangle stock + drilling + M8 tapping", "DXF + hole table"],
        ["UP-A1/A2/A3", "1 each", "S45C untreated", "supplier-finished 3D milling/drilling", "STEP; PDF notes"],
    ], [45 * mm, 22 * mm, 38 * mm, 85 * mm, 55 * mm], _font_name()))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "File priority: upper bracket STEP controls the 3D pocket; upper DXF only documents the mounting "
        "face. Lower plate DXF and the CSV hole table control hole locations. Ask the supplier to flag any "
        "unmachinable corner or inaccessible tool path instead of silently changing geometry.", styles["warning"]))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        "Status: quotation/fabrication candidate. Vendor DFM review and delivered-part fit checks remain. "
        "This document does not claim certification, payload use, human carrying, or field safety.", styles["small"]))
    story.append(PageBreak())
    for part_id in ("A1", "A2", "A3"):
        _lower_page(story, styles, part_id)
    for axis in (1, 2, 3):
        _upper_page(story, styles, axis)
    story.append(Paragraph("Assembly interface summary", styles["h1"]))
    assembly_rows = [
        ["Interface", "Selected stack", "Practical installation order"],
        ["Lower", "LMB-10 -> A1/A2/A3 M8 taps -> profile D9 holes", "fit plate to profile, then bolt LMB-10"],
        ["Upper housing", "PHS6 -> CBS6-12 -> UP-Ax pocket", "install PHS6 and M6 retainer on bench"],
        ["Upper pin", "HCDGH6-35 + WSSB10-6-4 + actuator eye + WSSB10-6-1.5 + PHS6 ball + supplied E-ring", "assemble after bracket is on profile"],
        ["Upper profile", "E-DNF3030 + E-SPN306 + E-DCBK3025", "preload slot nuts before frame ends close"],
    ]
    assembly_rows = [assembly_rows[0]] + [
        [Paragraph(cell, styles["small"]) for cell in row] for row in assembly_rows[1:]
    ]
    story.append(_table(assembly_rows, [38 * mm, 112 * mm, 95 * mm], _font_name()))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        "Representative digital checks are limited to neutral, Z=50 mm, and simultaneous +/-3 degree "
        "pitch/roll combinations. They are interference screens, not proof of continuous motion, strength, "
        "tolerance stack, or supplier acceptance.", styles["warning"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Before motor power: measure the delivered eye width and bore, dry-fit each pin stack, confirm the "
        "PHS6 housing seats without clamping the ball, and verify that all three actuators can be moved one "
        "axis at a time within the software travel window.", styles["body"]))
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return path


def main() -> None:
    output = ROOT / "outputs" / "20261003_revf_quote_package"
    manifest = export_quote_package(output, include_pdf=True)
    print(manifest["drawing_pdf"])


if __name__ == "__main__":
    main()
