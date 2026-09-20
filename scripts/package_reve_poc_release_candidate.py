from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "RevE_PoC_RC1"
STAMP = date(2026, 9, 4).isoformat()
OUTPUT_DIR = ROOT / "output"
ZIP_PATH = OUTPUT_DIR / f"Profile_Radial_3RPS_{REVISION}_{STAMP}.zip"
SHA_PATH = ZIP_PATH.with_suffix(ZIP_PATH.suffix + ".sha256")
MANIFEST_PATH = (
    ROOT
    / "outputs"
    / "profile_radial_revE_poc_release_candidate"
    / "RevE_PoC_package_manifest.json"
)


INCLUDE_PATHS = (
    "README.md",
    "PROJECT_HANDOFF.md",
    "AGENTS.md",
    "requirements/current_variant_priority_2026-09-04.md",
    "references/수평유지장치 요구사항.txt",
    "references/vendor_cad/LM4075OE-1075-100mm.stp",
    "logs/reve_poc_implementation_2026-09-04.md",
    "logs/work_history.md",
    "design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md",
    "design_basis/priority1_powered_control_architecture_2026-09-02.md",
    "procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv",
    "fabrication/profile_radial_revE_release_candidate_2026-09-04",
    "firmware/reve_leveling_controller",
    "tools/reve_commissioning_logger.py",
    "verification/RevE_PoC_completion_matrix_2026-09-04.csv",
    "verification/RevE_PoC_release_candidate_audit_2026-09-04.json",
    "verification/RevE_PoC_release_candidate_audit_2026-09-04.md",
    "verification/RevE_PoC_test_log_template.csv",
    "verification/RevE_PoC_test_protocol_2026-09-04.md",
    "outputs/profile_radial_revE_poc_release_candidate",
    "outputs/profile_radial_revE_actual_vendor",
    "output/pdf/Profile_Radial_3RPS_RevE_Electrical_Drawings_RC_2026-09-04.pdf",
    "output/pdf/Profile_Radial_3RPS_RevE_Fabrication_Drawings_RC_2026-09-04.pdf",
    "cad/profile_radial_reve_actual_vendor.py",
    "fusion_scripts/ProfileRadialRevEActualVendor",
    "scripts/audit_profile_radial_reve_poc.py",
    "scripts/build_reve_electrical_package.py",
    "scripts/export_profile_radial_reve_actual_vendor.py",
    "scripts/export_profile_radial_reve_fabrication.py",
    "scripts/package_reve_poc_release_candidate.py",
    "scripts/setup_and_compile_reve_firmware.ps1",
    "tests/test_profile_radial_reve_poc_release.py",
)


REQUIRED_ARCHIVE_PATHS = (
    "PROJECT_HANDOFF.md",
    "outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d",
    "outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.step",
    "outputs/profile_radial_revE_poc_release_candidate/procurement/Profile_Radial_3RPS_RevE_PoC_candidate_BOM_2026-09-04.csv",
    "outputs/profile_radial_revE_poc_release_candidate/firmware_build/reve_leveling_controller.ino.hex",
    "firmware/reve_leveling_controller/reve_leveling_controller.ino",
    "verification/RevE_PoC_release_candidate_audit_2026-09-04.json",
    "output/pdf/Profile_Radial_3RPS_RevE_Electrical_Drawings_RC_2026-09-04.pdf",
    "output/pdf/Profile_Radial_3RPS_RevE_Fabrication_Drawings_RC_2026-09-04.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def collect_files() -> list[Path]:
    files: set[Path] = set()
    for relative in INCLUDE_PATHS:
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(f"Required package input is missing: {relative}")
        if path.is_dir():
            files.update(candidate for candidate in path.rglob("*") if candidate.is_file())
        else:
            files.add(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix().lower())


def build_manifest(files: list[Path]) -> dict[str, object]:
    entries = []
    for path in files:
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return {
        "revision": REVISION,
        "date": STAMP,
        "purpose": "Cross-PC powered Rev E PoC release-candidate handoff",
        "file_count_excluding_manifest": len(entries),
        "total_bytes_excluding_manifest": sum(entry["bytes"] for entry in entries),
        "release_state": {
            "digital_package_pass": True,
            "purchase_release": False,
            "fabrication_release": False,
            "power_release": False,
            "poc_acceptance": False,
        },
        "files": entries,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    files = collect_files()
    manifest = build_manifest(files)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    files = collect_files()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            raise RuntimeError(f"ZIP CRC validation failed at {corrupt}")
        archive_paths = set(archive.namelist())
        missing = [path for path in REQUIRED_ARCHIVE_PATHS if path not in archive_paths]
        if missing:
            raise RuntimeError(f"ZIP is missing required paths: {missing}")
        zip_file_count = len(archive_paths)

    digest = sha256(ZIP_PATH)
    SHA_PATH.write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="ascii")
    print(
        json.dumps(
            {
                "zip": str(ZIP_PATH),
                "sha256_sidecar": str(SHA_PATH),
                "sha256": digest,
                "archive_file_count": zip_file_count,
                "archive_bytes": ZIP_PATH.stat().st_size,
                "crc_pass": True,
                "required_paths_pass": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
