"""Validate and package the approved-concept M2R2-S220 CAD review."""

from pathlib import Path
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "manual_turnbuckle_rev_m2r2s220"


def main():
    audit = json.loads((OUT / "M2R2S220_AUDIT.json").read_text(encoding="utf-8"))
    assert audit["concept_approved"]
    assert audit["digital_geometry_pass"] and audit["workspace"]["all_locked_ranks_6"]
    assert len(audit["poses"]) == 9
    for row in audit["poses"].values():
        assert not row["interferences"] and not row["invalid"]
    for row in audit["tools"].values():
        assert row["corridors"] == 84 and not row["interferences"]
        assert len(row["installed_clamp_obstructions"]) == 12
    for step in audit["step"]:
        path = OUT / "step" / step["file"]
        assert step["valid"] and step["volume_delta_mm3"] < 0.1
        assert hashlib.sha256(path.read_bytes()).hexdigest() == step["sha256"]
    fastening = json.loads((OUT / "FASTENING_STACK_AUDIT.json").read_text(encoding="utf-8"))
    assert all(row["passes_nominal_geometry"] for row in fastening["bolts"])

    files = [OUT / name for name in (
        "README.md", "ASSEMBLY.md", "BOM.csv", "M2R2S220_AUDIT.json",
        "FASTENING_STACK_AUDIT.json", "COMPONENT_REGISTER.json",
    )]
    files += sorted((OUT / "step").glob("M2R2S220_*.step"))
    files += sorted((OUT / "renders").glob("M2R2S220_*.png"))
    files += [ROOT / name for name in (
        "cad/manual_turnbuckle_rev_m2r2s220.py",
        "calculations/manual_m2r2_cart_dof_simulation.py",
        "calculations/manual_m2r2_slot_layout_optimization.py",
        "calculations/manual_m2r2s220_fastening.py",
        "scripts/build_manual_turnbuckle_rev_m2r2s220.py",
        "scripts/package_manual_turnbuckle_rev_m2r2s220.py",
        "design_basis/manual_m2r2_cart_dof_assessment_2026-09-06.md",
        "procurement/manual_m2r2_misumi_joint_sourcing_2026-09-06.md",
    )]
    target = ROOT / "output" / "Manual_3RPS_M2R2S220_Cart_BOM_CAD_2026-09-06.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for path in files:
            assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    print(json.dumps({"artifact_checks": "PASS", "files": len(files), "zip_bytes": target.stat().st_size, "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
