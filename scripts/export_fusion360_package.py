"""Export Fusion 360 compatible STEP files and the assembly-audited Rev E BOM."""

import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from cad.navimro_detailed_assembly import GROUP_OFFSETS, detailed_components, export_fusion_steps
from calculations.navimro_assembly_feasibility import audit_summary
from scripts.render_navimro_detailed import render_all


ROOT = Path(__file__).resolve().parents[1]
REVISION = "E"
OUTPUT = ROOT / "outputs" / "navimro_fusion360_revE"
STEP_DIR = OUTPUT / "step"
PACKAGE = ROOT / "output" / "NAVIMRO_Fusion360_detailed_CAD_revE.zip"


def _sha256(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_component_manifest(parts):
    path = OUTPUT / "NAVIMRO_revE_component_manifest.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("component_name", "group", "bom_key", "material", "status", "notes"))
        for part in parts:
            writer.writerow((part.name, part.group, part.bom_key, part.material, part.status, part.notes))
    return path


def write_detailed_bom(parts):
    path = OUTPUT / "NAVIMRO_revE_detailed_BOM.csv"
    groups = defaultdict(list)
    for part in parts:
        groups[part.bom_key].append(part)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("bom_key", "description_or_material", "quantity", "status", "used_in_groups", "action"))
        for key in sorted(groups):
            items = groups[key]
            provisional = any(item.status == "PROVISIONAL" for item in items)
            writer.writerow((
                key,
                items[0].material,
                len(items),
                "PROVISIONAL_VENDOR_CONFIRM" if provisional else "MODELED",
                ";".join(sorted({item.group for item in items})),
                "Replace dimensions from delivered part before fabrication" if provisional else "Use modeled position and quantity",
            ))
    return path


def write_fastener_schedule(parts):
    path = OUTPUT / "NAVIMRO_revE_fastener_schedule.csv"
    fasteners = [part for part in parts if any(token in part.bom_key for token in ("SCREW", "WASHER", "NUT", "TNUT", "BOLT", "SPACER"))]
    counts = Counter((part.bom_key, part.material, part.status, part.group) for part in fasteners)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("fastener", "description", "quantity", "status", "assembly_group"))
        for (key, material, status, group), quantity in sorted(counts.items()):
            writer.writerow((key, material, quantity, status, group))
    return path


def write_open_interfaces(parts):
    path = OUTPUT / "NAVIMRO_revE_provisional_interfaces.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("component_name", "group", "interface", "required_confirmation"))
        for part in parts:
            if part.status != "PROVISIONAL":
                continue
            writer.writerow((part.name, part.group, part.material, part.notes or "Confirm delivered dimensions and replace planning geometry"))
    return path


def write_procurement_gaps():
    path = OUTPUT / "NAVIMRO_revE_procurement_gaps.csv"
    rows = [
        ("M4 low-head socket screw", "M4x16 provisional", 16, "LMF12UU flange to transfer plate", "Confirm delivered flange counterbore and select exact NAVIMRO SKU"),
        ("M4 flat washer", "M4", 16, "LMF12UU flange", "Select exact NAVIMRO SKU after receipt check"),
        ("M4 nyloc nut", "M4", 16, "LMF12UU flange", "Use only if delivered flange has through holes"),
        ("M4 socket screw", "M4x45 provisional", 4, "Side-mounted SK12 supports", "Confirm delivered SK12 hole and exact grip stack"),
        ("M4 flat washer", "M4", 4, "SK12 supports", "Select exact NAVIMRO SKU"),
        ("M4 T-slot nut", "40-series slot compatible", 4, "SK12 supports", "Confirm profile slot compatibility and select exact NAVIMRO SKU"),
        ("M6 socket screw", "M6x20 provisional", 8, "CR-3001 mounting", "Confirm actual mounting-hole diameter"),
        ("M6 flat washer", "M6", 8, "CR-3001 mounting", "Add after vendor confirmation"),
        ("M6 T-slot nut", "40-series slot compatible", 8, "CR-3001 mounting", "Confirm profile slot compatibility"),
        ("Deck compression sleeve", "ID 8.6 / OD 18 / L15 aluminium", 16, "Acrylic deck", "Select commercial spacer or machine from tube; transfer-check deck holes"),
        ("Locator pin", "Master round plus relieved secondary", 2, "Cart coupling", "Turn locally after cart receiver dimensions are frozen"),
        ("Actuator pivot bolt", "M8 shoulder or partially threaded bolt, 36 mm grip stack", 6, "JFT-8R double-shear yokes", "Select exact shoulder length and positive retention"),
        ("JFT-8R spacer pair", "ID 8.2 / OD 12 / 4 mm each side", 12, "Rod-end spherical insert", "Measure delivered ball width before turning or ordering"),
        ("Motor-terminal bidirectional TVS", "Manufacturer example 1.5KE24CA; final part not selected", 3, "One short-lead clamp at each DMD-150 motor output", "Obtain NAVIMRO SKU and verify stand-off clamp and pulse-energy ratings by loaded-lowering test"),
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("missing_item", "planning_spec", "quantity", "use", "release_action"))
        writer.writerows(rows)
    return path


def copy_supporting_documents():
    sources = {
        ROOT / "procurement" / "navimro_single_order_bom.csv": OUTPUT / "NAVIMRO_single_order_BOM_revE.csv",
        ROOT / "procurement" / "navimro_single_order_bom.md": OUTPUT / "NAVIMRO_single_order_BOM_revE.md",
        ROOT / "procurement" / "navimro_preorder_inquiry_2026-08-27.md": OUTPUT / "NAVIMRO_vendor_inquiry_revE.md",
        ROOT / "procurement" / "electrical_control_completeness_2026-08-28.md": OUTPUT / "ELECTRICAL_CONTROL_COMPLETENESS_REVE.md",
        ROOT / "design_basis" / "dmd150_official_manual_review_2026-08-28.md": OUTPUT / "DMD150_OFFICIAL_MANUAL_REVIEW_REVE.md",
        ROOT / "design_basis" / "fusion360_actuator_joint_rebuild_revD_2026-08-28.md": OUTPUT / "ACTUATOR_JOINT_REBUILD_REVD.md",
        ROOT / "design_basis" / "fusion360_assembly_validation_revE_2026-08-28.md": OUTPUT / "ASSEMBLY_VALIDATION_REVE.md",
    }
    for source, destination in sources.items():
        shutil.copy2(source, destination)
    return list(sources.values())


def write_readme(parts):
    provisional = sum(part.status == "PROVISIONAL" for part in parts)
    text = f"""# Fusion 360 import - NAVIMRO detailed CAD Rev E

## Recommended file

Import `step/NAVIMRO_detailed_neutral_revE.step` into Fusion 360 with **Upload** or **File > Open**. The STEP assembly contains named groups and components. Use `ACT1_complete_mounting_cassette_neutral_revE.step` for the clearest actuator mounting inspection, `NAVIMRO_detailed_exploded_revE.step` for assembly order, and the `SUB_*.step` files for smaller editable subassemblies.

## Model scope

- {len(parts)} positioned mechanical components at the neutral pose.
- 4040 profiles include visible T-slots.
- Profile joint plates, screws, washers, T-nuts, nyloc nuts, guide fasteners, pivot pins, deck spacers and latch fasteners are modeled.
- Aluminium profile, SS400 plate, acrylic, purchased parts and fasteners use separate colors.
- Six catalog-modeled JMC JFT-8R rod ends replace the invalid rigid U/H stacks from Rev C.
- Each actuator end now contains a separate spherical rod end, two bored steel lugs, two spacers, one bored M8 pin stack and an explicit M8/A2 adapter.
- {provisional} components remain yellow/provisional because the delivered A2 actuator interfaces and several other supplier interfaces remain unverified.
- The package is a mechanical digital mock-up. Electrical panel internal parts are documented in the procurement BOM but are not mounted on the moving mechanical module.
- The cart-side group is a static provisional reference displayed 56 mm below the module. It is excluded from the digital assembly pass and must not be fabricated before the real cart interface is frozen.

## Fusion 360 notes

1. STEP is used because a native `.f3d` file requires Fusion 360 itself and its API. Fusion 360 imports these STEP files directly.
2. After import, save the document as F3D if a native editable archive is required.
3. Do not combine or rename yellow components until vendor measurements are entered.
4. Replace `LA2000_A2_PROVISIONAL_*` and `ACT*_M8_A2_ADAPTER_PROVISIONAL` from the delivered actuator or supplier STEP. JFT-8R geometry is catalog-modeled but still requires receipt inspection.
5. The assembly-audited guide uses one 240 mm carriage, two 230 mm shafts, four LMF12UU bushings and two side-mounted SK12 supports.
6. `NAVIMRO_module_only_collapsed_revE.step` excludes the loose cart-side coupling parts and is the correct file for checking the 300 mm disconnected module height.
7. Full detailed states include collapsed, neutral, raised, max pitch, max roll and max pitch+roll.
8. Read `NAVIMRO_revE_assembly_audit.json` and `ASSEMBLY_VALIDATION_REVE.md` before fabrication; a digital pass does not close vendor-dependent transfer holes.

## Color key

- Grey: 4040 aluminium profile
- Dark blue: fabricated SS400 plate
- Transparent cyan: acrylic deck
- Black/silver: fasteners
- Yellow: purchased or vendor-dependent provisional interface
- Red: mechanical stop

## Release restriction

Do not release the A2 adapter/thread detail, spacer thickness, pivot hardware, guide transfer holes, latch keepers or locator pins for fabrication until the provisional-interface CSV is closed with measured values. The six P03/P04/P16 yokes require local cutting, drilling, jig alignment and welding.
"""
    path = OUTPUT / "FUSION360_IMPORT_README.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_assembly_audit():
    path = OUTPUT / "NAVIMRO_revE_assembly_audit.json"
    path.write_text(json.dumps(audit_summary(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_manifest():
    files = [path for path in OUTPUT.rglob("*") if path.is_file() and path.name != "artifact_manifest.json"]
    rows = [{
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    } for path in sorted(files)]
    path = OUTPUT / "artifact_manifest.json"
    path.write_text(json.dumps({
        "revision": REVISION,
        "status": "DIGITAL_ASSEMBLY_PASS_VENDOR_INTERFACES_OPEN",
        "artifact_count": len(rows),
        "artifacts": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def package_zip():
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    if PACKAGE.exists():
        PACKAGE.unlink()
    shutil.make_archive(str(PACKAGE.with_suffix("")), "zip", OUTPUT)
    return PACKAGE


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = detailed_components("neutral")
    print(f"[1/5] exporting {len(parts)}-component Fusion STEP set")
    export_fusion_steps(STEP_DIR, REVISION)
    print("[2/5] rendering detailed assembly")
    render_all(ROOT)
    print("[3/5] writing BOM, fastener and provisional-interface tables")
    write_component_manifest(parts)
    write_detailed_bom(parts)
    write_fastener_schedule(parts)
    write_open_interfaces(parts)
    write_procurement_gaps()
    write_assembly_audit()
    write_readme(parts)
    copy_supporting_documents()
    print("[4/5] writing SHA-256 manifest")
    write_manifest()
    print("[5/5] building Fusion 360 zip package")
    package_zip()
    print(PACKAGE)


if __name__ == "__main__":
    main()
