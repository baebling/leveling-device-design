"""Regenerate the complete NAVIMRO Rev A fabrication release."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from cad.navimro_fabrication_exports import export_all
from calculations.navimro_fabrication_budget import write_outputs as write_budget
from calculations.navimro_fabrication_verification import write_outputs as write_verification
from scripts.build_navimro_pdf_pack import main as build_pdf_pack
from scripts.build_navimro_assembly_manual import main as build_assembly_manual
from scripts.render_navimro_assembly_guide import render_all as render_assembly_guide
from scripts.render_navimro_fabrication import render_all


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_manifest():
    paths = []
    for base in (ROOT / "outputs" / "navimro_fabrication", ROOT / "output" / "pdf"):
        paths.extend(path for path in base.rglob("*") if path.is_file() and path.name != "artifact_manifest.json")
    rows = [{
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
    } for path in sorted(paths)]
    output = ROOT / "outputs" / "navimro_fabrication" / "artifact_manifest.json"
    output.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "revision": "A",
        "status": "PROTOTYPE_FABRICATION_BASELINE_VENDOR_TRANSFER_HOLES_OPEN",
        "artifact_count": len(rows),
        "artifacts": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    print("[1/6] STEP, DXF and cut lists")
    export_all(ROOT)
    print("[2/6] verification and assembly-guide renders")
    render_all(ROOT)
    render_assembly_guide(ROOT)
    print("[3/6] calculations and budget")
    write_verification(ROOT)
    write_budget(ROOT)
    print("[4/6] PDF drawing and order packs")
    build_pdf_pack()
    print("[5/6] visual assembly manual")
    build_assembly_manual()
    print("[6/6] SHA-256 manifest")
    manifest = write_manifest()
    print(manifest)


if __name__ == "__main__":
    main()
