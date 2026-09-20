"""Fusion-native Rev E generator with the supplied LM4075OE STEP bodies."""

import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback

import adsk.core
import adsk.fusion


PROJECT_ROOT = os.environ.get(
    "LEVELING_PROJECT_ROOT",
    r"C:\Users\gangm\OneDrive\2. 연구실\지원사업\BIZ-Lab 창업클럽\수평유지장치설계 프로젝트",
)
REVD_SCRIPT = os.path.join(
    PROJECT_ROOT, "fusion_scripts", "ProfileRadialRevD", "ProfileRadialRevD.py"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "profile_radial_revE_actual_vendor")
INPUT_DIR = os.path.join(OUTPUT_DIR, "fusion_inputs", "collapsed_actuator_parts")
F3D_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d")
STEP_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.step")
IMAGE_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_Fusion.png")
IMAGE_TOP_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_TOP.png")
IMAGE_SIDE_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_SIDE.png")
IMAGE_A1_DETAIL_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_A1_JOINT_DETAIL.png")
VALIDATION_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_Fusion_validation.json")
INTERFERENCE_PATH = os.path.join(OUTPUT_DIR, "Profile_Radial_3RPS_RevE_Fusion_interference.json")
ERROR_PATH = os.path.join(OUTPUT_DIR, "ProfileRadialRevEActualVendor_ERROR.txt")
GROUP_STEP_DIR = os.path.join(OUTPUT_DIR, "fusion_groups")
VENDOR_STEP = os.path.join(
    PROJECT_ROOT, "references", "vendor_cad", "LM4075OE-1075-100mm.stp"
)
VENDOR_NAMES = ("UP", "END", "MOTER", "WAIKE", "FENGTOU", "NEIGUAN")


def load_revd():
    name = "profile_radial_revd_runtime_for_reve"
    spec = importlib.util.spec_from_file_location(name, REVD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load Rev D generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVD = load_revd()


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def import_vendor_actuator(actuator_group, index, lower, upper, tangent):
    del lower, tangent
    pin_length = sum((upper[axis] - REVD.lower_eye_points()[index - 1][axis]) ** 2 for axis in range(3)) ** 0.5
    occurrence = actuator_group.occurrences.addNewComponent(REVD.identity())
    component = occurrence.component
    component.name = f"A{index}_LM4075OE_VENDOR_ASSEMBLY_PIN_{pin_length:.3f}mm"
    REVD.COMPONENT_NAMES.append(component.name)
    manager = REVD.APP.importManager
    for part_name in VENDOR_NAMES:
        path = os.path.join(INPUT_DIR, f"A{index}_{part_name}.step")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        options = manager.createSTEPImportOptions(path)
        imported = manager.importToTarget2(options, component)
        if imported is None or imported.count == 0:
            raise RuntimeError("Fusion STEP import failed: " + path)
        imported_occurrences = []
        for imported_index in range(imported.count):
            imported_occurrence = adsk.fusion.Occurrence.cast(imported.item(imported_index))
            if imported_occurrence:
                imported_occurrences.append(imported_occurrence)
        if not imported_occurrences:
            raise RuntimeError("No occurrence imported from: " + path)
        for imported_occurrence in imported_occurrences:
            imported_occurrence.component.name = f"A{index}_LM4075OE_{part_name}"
            REVD.COMPONENT_NAMES.append(imported_occurrence.component.name)
            key = "ROD" if part_name == "NEIGUAN" else "ACTUATOR"
            appearance = REVD.APPEARANCES.get(key)
            for body in imported_occurrence.component.bRepBodies:
                body.name = f"A{index}_LM4075OE_{part_name}_BODY"
                if appearance:
                    try:
                        body.appearance = appearance
                    except Exception:
                        pass


def interference_entity_name(entity):
    try:
        if entity.component:
            return entity.component.name
    except Exception:
        pass
    try:
        return entity.name
    except Exception:
        return str(entity)


def run_fusion_interference_checks(pass_count=3):
    entities = adsk.core.ObjectCollection.create()
    for occurrence in REVD.ROOT.allOccurrences:
        if occurrence.component.bRepBodies.count > 0:
            entities.add(occurrence)
    passes = []
    for pass_index in range(1, pass_count + 1):
        interference_input = REVD.DESIGN.createInterferenceInput(entities)
        interference_input.areCoincidentFacesIncluded = False
        results = REVD.DESIGN.analyzeInterference(interference_input)
        rows = []
        for result_index in range(results.count):
            result = results.item(result_index)
            volume_mm3 = None
            try:
                volume_mm3 = result.interferenceBody.volume * 1000.0
            except Exception:
                pass
            rows.append(
                {
                    "entity_one": interference_entity_name(result.entityOne),
                    "entity_two": interference_entity_name(result.entityTwo),
                    "volume_mm3": volume_mm3,
                }
            )
        for row in rows:
            first = row["entity_one"]
            second = row["entity_two"]
            numerical_contact = (
                row["volume_mm3"] is not None and row["volume_mm3"] <= 0.01
            )
            same_actuator = any(
                first.startswith(f"A{index}_LM4075OE_")
                and second.startswith(f"A{index}_LM4075OE_")
                for index in range(1, 4)
            )
            suffixes = {first.rsplit("_", 1)[-1], second.rsplit("_", 1)[-1]}
            row["classification"] = (
                "NUMERICAL_TOLERANCE_CONTACT"
                if numerical_contact
                else "EXPECTED_VENDOR_SOURCE_OVERLAP"
                if same_actuator and suffixes in ({"UP", "END"}, {"UP", "MOTER"})
                else "UNEXPECTED_ASSEMBLY_INTERFERENCE"
            )
        signature = tuple(
            sorted(
                (
                    row["entity_one"],
                    row["entity_two"],
                    None if row["volume_mm3"] is None else round(row["volume_mm3"], 6),
                )
                for row in rows
            )
        )
        passes.append(
            {
                "pass": pass_index,
                "checked_leaf_occurrences": entities.count,
                "interference_count": results.count,
                "signature": signature,
                "rows": rows,
                "unexpected_count": sum(
                    row["classification"] == "UNEXPECTED_ASSEMBLY_INTERFERENCE"
                    for row in rows
                ),
                "passes": all(
                    row["classification"] != "UNEXPECTED_ASSEMBLY_INTERFERENCE"
                    for row in rows
                ),
            }
        )
    report = {
        "method": "Fusion Design.analyzeInterference; coincident faces excluded",
        "pass_count": pass_count,
        "repeatable": all(row["signature"] == passes[0]["signature"] for row in passes),
        "all_zero_unexpected": all(row["passes"] for row in passes),
        "passes": passes,
    }
    with open(INTERFERENCE_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return report


def save_section_checks():
    paths = []
    analyses = REVD.DESIGN.analyses.sectionAnalyses
    for pass_index, offset_mm in enumerate((0.0, 3.0, -3.0), start=1):
        section_input = analyses.createInput(REVD.ROOT.yZConstructionPlane, REVD.mm(offset_mm))
        analysis = analyses.add(section_input)
        analysis.name = f"REV_E_A1_SECTION_PASS_{pass_index}_X_{offset_mm:+.1f}mm"
        analysis.isHatchShown = True
        analysis.isLightBulbOn = True
        path = os.path.join(OUTPUT_DIR, f"Profile_Radial_3RPS_RevE_SECTION_PASS_{pass_index}.png")
        REVD.save_camera_image(
            path,
            (500.0, 165.0, 190.0),
            (0.0, 165.0, 165.0),
            (0.0, 0.0, 1.0),
        )
        paths.append({"pass": pass_index, "x_offset_mm": offset_mm, "image": path})
        analysis.isLightBulbOn = False
        analysis.deleteMe()
    return paths


def configure_revd(app, design):
    REVD.APP = app
    REVD.DESIGN = design
    REVD.ROOT = design.rootComponent
    REVD.TBM = adsk.fusion.TemporaryBRepManager.get()
    REVD.OUTPUT_DIR = OUTPUT_DIR
    REVD.F3D_PATH = F3D_PATH
    REVD.STEP_PATH = STEP_PATH
    REVD.IMAGE_PATH = IMAGE_PATH
    REVD.IMAGE_TOP_PATH = IMAGE_TOP_PATH
    REVD.IMAGE_SIDE_PATH = IMAGE_SIDE_PATH
    REVD.IMAGE_A1_DETAIL_PATH = IMAGE_A1_DETAIL_PATH
    REVD.VALIDATION_PATH = VALIDATION_PATH
    REVD.ERROR_PATH = ERROR_PATH
    REVD.GROUP_STEP_DIR = GROUP_STEP_DIR
    REVD.COMPONENT_NAMES.clear()
    REVD.GROUP_COMPONENTS = {}
    REVD.add_actuator = import_vendor_actuator


def amend_validation(interference, sections):
    with open(VALIDATION_PATH, "r", encoding="utf-8") as stream:
        audit = json.load(stream)
    audit["revision"] = "E_ACTUAL_VENDOR_STEP"
    audit["status"] = "FUSION_NATIVE_CAD_REVIEW_NOT_FOR_ORDER"
    audit["vendor_step"] = VENDOR_STEP
    audit["vendor_step_sha256"] = sha256(VENDOR_STEP)
    audit["vendor_named_bodies_per_actuator"] = VENDOR_NAMES
    audit["actuator_envelope_basis"] = (
        "Actual supplier STEP; six named bodies imported per actuator. "
        "Rear/front pin centers are 205.0 mm apart in the downloaded file."
    )
    audit["fusion_interference"] = interference
    audit["section_checks"] = sections
    audit["purchase_release"] = False
    audit["fabrication_release"] = False
    with open(VALIDATION_PATH, "w", encoding="utf-8") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return audit


def run(context):
    del context
    ui = None
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        app = adsk.core.Application.get()
        ui = app.userInterface
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        document.name = "Profile_Radial_3RPS_RevE_ACTUAL_VENDOR"
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        configure_revd(app, design)
        REVD.add_parameters()
        REVD.setup_appearances()
        REVD.ROOT.attributes.add("REV_E", "STATUS", "CAD_REVIEW_NOT_FOR_ORDER")
        REVD.ROOT.attributes.add("REV_E", "ACTUATOR_GEOMETRY", "ACTUAL_VENDOR_STEP")
        REVD.ROOT.attributes.add("REV_E", "VENDOR_STEP_SHA256", sha256(VENDOR_STEP))
        REVD.create_assembly()
        REVD.export_results()
        interference = run_fusion_interference_checks(3)
        sections = save_section_checks()
        audit = amend_validation(interference, sections)
        if os.path.exists(ERROR_PATH):
            os.remove(ERROR_PATH)
        ui.messageBox(
            "Rev E actual-vendor assembly created.\n\n"
            f"Vendor bodies: 3 x {len(VENDOR_NAMES)}\n"
            f"Fusion interference passes: {interference['pass_count']}\n"
            f"All-zero unexpected interference: {interference['all_zero_unexpected']}\n"
            f"Digital layout pass: {audit['digital_layout_passes']}\n\n"
            f"F3D: {F3D_PATH}\n\n"
            "Status: CAD review only; not released for ordering."
        )
    except Exception:
        message = "ProfileRadialRevEActualVendor failed:\n" + traceback.format_exc()
        if ui:
            ui.messageBox(message)
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(ERROR_PATH, "w", encoding="utf-8") as stream:
                stream.write(message)
        except Exception:
            pass
