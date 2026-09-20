import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cad.exports import export_all
from cad.parameters import ROOT
from cad.rendering import render_all
from calculations.generate_reports import write_reports
from scripts.render_vendor_actuator_analysis import render_vendor_diagnostics
from scripts.render_factory_clevis_gimbal import render_factory_clevis_gimbal
from scripts.render_navimro_pin_lug_gimbal import render_navimro_pin_lug_gimbal


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest(paths):
    rows = []
    for path in sorted(set(Path(p).resolve() for p in paths)):
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    output = ROOT / "outputs" / "phase2" / "artifact_manifest.json"
    output.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PRELIMINARY_NOT_APPROVED_FOR_FABRICATION",
        "artifacts": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    print("[1/4] calculations and reports")
    write_reports(ROOT)
    print("[2/4] CAD exports")
    cad_paths = export_all(ROOT)
    print("[3/4] rendered verification views")
    render_paths = render_all(ROOT / "outputs" / "renders")
    render_paths += render_vendor_diagnostics()
    render_paths += render_factory_clevis_gimbal()
    render_paths += render_navimro_pin_lug_gimbal()
    report_paths = [p for p in (ROOT / "outputs" / "phase2").glob("*") if p.name != "artifact_manifest.json"]
    report_paths += list((ROOT / "outputs" / "calculations").glob("phase2_*"))
    manifest(cad_paths + render_paths + report_paths)
    print("[4/4] unittest verification")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print(f"Phase 2 complete: {len(cad_paths)} CAD files, {len(render_paths)} renders")
    return 0


if __name__ == "__main__":
    sys.exit(main())
