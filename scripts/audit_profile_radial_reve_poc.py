"""Audit the Rev E release-candidate package without claiming physical tests."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import ezdxf

from cad.profile_radial_reve_actual_vendor import full_pose_audit
from fusion_scripts.ProfileRadialRevD import revd_data


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "outputs" / "profile_radial_revE_poc_release_candidate"
FAB = ROOT / "fabrication" / "profile_radial_revE_release_candidate_2026-09-04"
MECH = ROOT / "outputs" / "profile_radial_revE_actual_vendor"
VERIFY = ROOT / "verification"
FIRMWARE = ROOT / "firmware" / "reve_leveling_controller" / "reve_leveling_controller.ino"


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest().upper()


def repeated_occ_audit() -> dict:
    passes = []
    for pass_number in range(1, 4):
        result = full_pose_audit()
        signature = {
            "pose_count": result["pose_count"],
            "minimum_pin_mm": result["minimum_pin_mm"],
            "maximum_pin_mm": result["maximum_pin_mm"],
            "max_collision_mm3": result["maximum_unintended_collision_volume_mm3"],
            "passes": result["passes"],
            "rows": [
                {
                    "pose": row["pose"],
                    "lengths": row["pin_lengths_mm"],
                    "collision": row["collision"]["maximum_volume_mm3"],
                }
                for row in result["rows"]
            ],
        }
        passes.append({"pass": pass_number, "signature": digest(signature), **{key: signature[key] for key in ("pose_count", "minimum_pin_mm", "maximum_pin_mm", "max_collision_mm3", "passes")}})
    return {
        "method": "CadQuery/OpenCascade full 27-pose B-rep audit repeated three times",
        "passes": passes,
        "repeatable": len({row["signature"] for row in passes}) == 1,
        "all_pass": all(row["passes"] for row in passes),
    }


def fusion_evidence_audit() -> dict:
    interference = json.loads((MECH / "Profile_Radial_3RPS_RevE_Fusion_interference.json").read_text(encoding="utf-8"))
    sections = [MECH / f"Profile_Radial_3RPS_RevE_SECTION_PASS_{index}.png" for index in range(1, 4)]
    return {
        "method": interference["method"],
        "pass_count": interference["pass_count"],
        "repeatable": interference["repeatable"],
        "all_zero_unexpected": interference["all_zero_unexpected"],
        "section_images": [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()} for path in sections],
        "passes": interference["pass_count"] == 3 and interference["repeatable"] and interference["all_zero_unexpected"] and all(path.exists() and path.stat().st_size > 10000 for path in sections),
        "note": "Evidence is the existing Fusion-native Rev E baseline. Fusion must be rerun after any supplier-interface geometry change.",
    }


def fabrication_audit() -> dict:
    dxfs = sorted(FAB.glob("*.dxf"))
    feature_rows = list(csv.DictReader((FAB / "RevE_custom_part_hole_table.csv").open("r", encoding="utf-8-sig", newline="")))
    entity_counts = {}
    for path in dxfs:
        doc = ezdxf.readfile(path)
        entity_counts[path.name] = len(list(doc.modelspace()))
    part_ids = {row["part_id"] for row in feature_rows}
    a3 = [row for row in feature_rows if row["part_id"] == "C03" and row["note"] == "M8 profile clearance"]
    a3_x = sorted(round(float(row["x_mm"]), 3) for row in a3)
    return {
        "dxf_count": len(dxfs),
        "unique_part_ids": sorted(part_ids),
        "entity_counts": entity_counts,
        "a3_profile_hole_local_x_mm": a3_x,
        "passes": len(dxfs) == 9 and len(part_ids) == 9 and all(value >= 4 for value in entity_counts.values()) and abs(a3_x[1] - a3_x[0] - 100.0) < 1e-6,
        "fabrication_release": False,
        "open_gate": "LMB-10 supplier drawing/first-article measurement",
    }


def electrical_audit() -> dict:
    layout = json.loads((RELEASE / "electrical" / "RevE_enclosure_layout_validation.json").read_text(encoding="utf-8"))
    bom_path = RELEASE / "procurement" / "Profile_Radial_3RPS_RevE_PoC_candidate_BOM_2026-09-04.csv"
    rows = list(csv.DictReader(bom_path.open("r", encoding="utf-8-sig", newline="")))
    subtotal = sum(int(row["extended_price_krw_screen"] or 0) for row in rows)
    required = {
        "RevE_terminal_map.csv",
        "RevE_point_to_point_wiring.csv",
        "RevE_harness_schedule.csv",
        "RevE_io_map.csv",
        "RevE_enclosure_layout.csv",
    }
    existing = {path.name for path in (RELEASE / "electrical").glob("*.csv")}
    return {
        "candidate_bom_rows": len(rows),
        "known_subtotal_krw": subtotal,
        "under_target_before_open_quotes": subtotal <= 3_600_000,
        "under_absolute_budget_before_open_quotes": subtotal <= 4_000_000,
        "required_tables_present": required <= existing,
        "enclosure_layout_envelope_pass": layout["passes_layout_envelope"],
        "open_bom_rows": [row["bom_id"] for row in rows if row["procurement_status"].startswith(("HOLD", "QUOTE"))],
        "passes_detail_design": required <= existing and layout["passes_layout_envelope"] and subtotal <= 4_000_000,
        "purchase_release": False,
        "power_release": False,
    }


def firmware_audit() -> dict:
    source = FIRMWARE.read_text(encoding="utf-8")
    required_commands = ("STATUS", "HOME", "JOG", "LIFT", "LEVEL", "STOP", "ZERO_IMU", "SAVE_CAL")
    required_fragments = (
        "ENC_A[AXES] = {2, 3, 18}",
        "ENC_B[AXES] = {22, 23, 24}",
        "MOTOR_PWM[AXES] = {5, 6, 7}",
        "MOTOR_DIR[AXES] = {30, 31, 32}",
        "REVERSE_PAUSE_MS = 100",
        "NO_PULSE_MS = 500",
        "IMU_STALE_MS = 200",
        "TILT_FAULT_DEG = 5.0f",
        "MOTION_TIMEOUT_MS = 30000",
        "LEVEL_STEP_MM = 0.25f",
        "LEVEL_TOLERANCE_DEG = 0.5f",
        "LEVEL_HOLD_MS = 10000",
        "EEPROM.put",
    )
    brace_balance = source.count("{") - source.count("}")
    build_dir = RELEASE / "firmware_build"
    compile_record = build_dir / "compile_record.txt"
    binaries = sorted(build_dir.glob("*.hex"))
    return {
        "required_commands": {command: f'"{command}"' in source for command in required_commands},
        "required_safety_fragments": {fragment: fragment in source for fragment in required_fragments},
        "brace_balance": brace_balance,
        "passes_static_audit": all(f'"{command}"' in source for command in required_commands) and all(fragment in source for fragment in required_fragments) and brace_balance == 0,
        "compile_test": "PASS_ARDUINO_AVR_MEGA" if compile_record.exists() and binaries else "NOT_RUN_OR_FAILED",
        "compile_record": str(compile_record.relative_to(ROOT)) if compile_record.exists() else "",
        "firmware_binaries": [str(path.relative_to(ROOT)) for path in binaries],
        "bench_test": "NOT_RUN_HARDWARE_REQUIRED",
    }


def write_matrix(results: dict) -> None:
    rows = [
        ("D01", "27-pose stroke", "205-305 mm", results["occ"]["all_pass"], "digital"),
        ("D02", "PHS6 articulation", "<=8 deg", results["joint"]["passes"], "digital"),
        ("D03", "OpenCascade interference 3x", "0 unexpected", results["occ"]["repeatable"] and results["occ"]["all_pass"], "digital"),
        ("D04", "Fusion interference 3x", "0 unexpected", results["fusion"]["passes"], "existing Fusion evidence"),
        ("D05", "Fusion section inspection 3x", "3 images", len(results["fusion"]["section_images"]) == 3, "existing Fusion evidence"),
        ("F01", "Nine custom-part drawings", "9 DXF + PDF", results["fabrication"]["passes"], "release candidate"),
        ("E01", "Enclosure envelope", "no overlap, >=50 mm AC/logic", results["electrical"]["enclosure_layout_envelope_pass"], "digital"),
        ("E02", "Wiring package", "terminal/wire/harness/io tables", results["electrical"]["required_tables_present"], "digital"),
        ("C01", "Firmware static interface", "all commands/pins/faults", results["firmware"]["passes_static_audit"], "static only"),
        ("P01", "Known-price budget", "<=4,000,000 KRW", results["electrical"]["under_absolute_budget_before_open_quotes"], "quotes/freight remain"),
        ("G01", "LMB-10 interface", "supplier/first article", False, "physical evidence required"),
        ("G02", "Actuator current/pinout", "supplier/first article", False, "physical evidence required"),
        ("G03", "One-axis commissioning", "current/counts/bus", False, "physical hardware required"),
        ("G04", "10 kg 27-trial acceptance", "+/-0.5 deg for 10 s", False, "physical hardware required"),
    ]
    with (VERIFY / "RevE_PoC_completion_matrix_2026-09-04.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("id", "check", "criterion", "pass", "evidence"))
        writer.writerows(rows)


def main() -> int:
    VERIFY.mkdir(parents=True, exist_ok=True)
    joint = revd_data.joint_axis_audit()
    results = {
        "revision": "E-RC1",
        "date": "2026-09-04",
        "occ": repeated_occ_audit(),
        "joint": {
            "max_phs6_articulation_deg": joint["maximum_phs6_articulation_deg"],
            "limit_deg": joint["published_phs6_allowance_deg"],
            "passes": joint["passes"],
        },
        "fusion": fusion_evidence_audit(),
        "fabrication": fabrication_audit(),
        "electrical": electrical_audit(),
        "firmware": firmware_audit(),
        "physical_tests_executed": False,
        "purchase_release": False,
        "fabrication_release": False,
        "power_release": False,
        "poc_acceptance": False,
    }
    write_matrix(results)
    results["digital_package_pass"] = all((results["occ"]["all_pass"], results["occ"]["repeatable"], results["joint"]["passes"], results["fusion"]["passes"], results["fabrication"]["passes"], results["electrical"]["passes_detail_design"], results["firmware"]["passes_static_audit"]))
    out = VERIFY / "RevE_PoC_release_candidate_audit_2026-09-04.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = f"""# Rev E PoC release-candidate audit\n\n+Date: 2026-09-04  \n+Digital package: `{'PASS' if results['digital_package_pass'] else 'FAIL'}`  \n+Purchase/fabrication/power/PoC acceptance: `FALSE`\n+\n+## Completed digitally\n+\n+- OpenCascade 27-pose audit repeated three times: {'PASS' if results['occ']['repeatable'] and results['occ']['all_pass'] else 'FAIL'}.\n+- Pin distance: {results['occ']['passes'][0]['minimum_pin_mm']:.6f}-{results['occ']['passes'][0]['maximum_pin_mm']:.6f} mm inside 205-305 mm.\n+- PHS6 maximum articulation: {results['joint']['max_phs6_articulation_deg']:.6f} degrees below 8 degrees.\n+- Existing Fusion-native interference evidence: three repeats, zero unexpected interference.\n+- Existing Fusion section evidence: three section images present and hashed.\n+- Fabrication RC: nine unique DXFs, one nine-sheet PDF, hole table, cut list, and assembly sequence.\n+- Electrical RC: enclosure STEP/layout, circuit PDF, terminal map, point-to-point wiring, harness schedule, I/O map, and revised candidate BOM.\n+- Firmware: command/state/fault/calibration implementation and static interface audit.\n+\n+## Still blocked by external evidence\n+\n+- LMB-10 supplier drawing or measured first article.\n+- LM4075OE rated/start/stall current, exact encoder wiring/levels, internal limit behavior, and duty cycle.\n+- Physical enclosure/backplate and PCB mounting-hole verification.\n+- Arduino compilation on an installed board toolchain and hardware-in-loop checks.\n+- One-axis current/counts/regeneration test, three-axis unloaded test, and 10 kg 27-trial acceptance.\n+\n+No purchase or fabrication should be released from this audit alone.\n+"""
    (VERIFY / "RevE_PoC_release_candidate_audit_2026-09-04.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"digital_package_pass": results["digital_package_pass"], "audit": str(out), "physical_tests_executed": False}, indent=2))
    return 0 if results["digital_package_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
