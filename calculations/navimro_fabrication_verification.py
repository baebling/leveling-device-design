"""Analytical checks for the NAVIMRO fabrication baseline."""

import json
from itertools import product
from math import cos, radians, sin
from pathlib import Path

from cad.navimro_fabrication_exports import flatbar_usage_mm
from cad.navimro_fabrication_parameters import N, NavimroPose, actuator_lengths, transform_local_point


G = 9.80665


def workspace_extremes():
    records = []
    for lift, pitch, roll in product((0.0, N.lift_mm), (-N.max_angle_deg, N.max_angle_deg), (-N.max_angle_deg, N.max_angle_deg)):
        pose = NavimroPose("corner", lift, pitch, roll)
        for actuator_index, length in enumerate(actuator_lengths(pose), start=1):
            records.append({
                "lift_mm": lift,
                "pitch_deg": pitch,
                "roll_deg": roll,
                "actuator": actuator_index,
                "length_mm": length,
            })
    shortest = min(records, key=lambda row: row["length_mm"])
    longest = max(records, key=lambda row: row["length_mm"])
    return shortest, longest


def minimum_vertical_direction_cosine():
    minimum = 1.0
    governing = None
    for lift, pitch, roll in product((0.0, N.lift_mm), (-N.max_angle_deg, N.max_angle_deg), (-N.max_angle_deg, N.max_angle_deg)):
        pose = NavimroPose("corner", lift, pitch, roll)
        platform_z = N.collapsed_joint_z_mm + lift
        for index, ((ux, uy), (lx, ly)) in enumerate(zip(N.upper_points_xy, N.lower_points_xy), start=1):
            tx, ty, tz = transform_local_point((ux, uy, 0.0), pose, platform_z)
            length = ((tx - lx) ** 2 + (ty - ly) ** 2 + (tz - N.base_joint_z_mm) ** 2) ** 0.5
            cosine = abs(tz - N.base_joint_z_mm) / length
            if cosine < minimum:
                minimum = cosine
                governing = (lift, pitch, roll, index)
    return minimum, governing


def verification_results():
    shortest, longest = workspace_extremes()
    min_cosine, force_pose = minimum_vertical_direction_cosine()
    service_mass = N.payload_kg + N.cart_mass_kg + N.moving_structure_mass_kg
    service_weight = service_mass * G
    design_weight = service_weight * N.design_factor
    eccentricity_mm = 100.0
    worst_vertical_reaction = design_weight * (
        1.0 / 3.0 + 2.0 * eccentricity_mm / (3.0 * N.upper_joint_radius_mm)
    )
    worst_axial_force = worst_vertical_reaction / min_cosine
    lateral_guide_force = design_weight * sin(radians(N.max_angle_deg))
    cut, kerf, flatbar_reserve = flatbar_usage_mm()
    return {
        "status": "PROTOTYPE_FABRICATION_BASELINE",
        "workspace": {
            "minimum_pin_length_mm": shortest["length_mm"],
            "minimum_case": shortest,
            "maximum_pin_length_mm": longest["length_mm"],
            "maximum_case": longest,
            "retraction_margin_mm": shortest["length_mm"] - N.actuator_min_pin_length_mm,
            "extension_margin_mm": N.actuator_max_pin_length_mm - longest["length_mm"],
        },
        "loads": {
            "service_moving_mass_kg": service_mass,
            "service_weight_n": service_weight,
            "design_factor": N.design_factor,
            "design_vertical_load_n": design_weight,
            "assumed_plan_eccentricity_mm": eccentricity_mm,
            "worst_vertical_actuator_reaction_n": worst_vertical_reaction,
            "minimum_actuator_vertical_direction_cosine": min_cosine,
            "governing_force_pose": force_pose,
            "worst_estimated_actuator_axial_force_n": worst_axial_force,
            "actuator_rating_n": N.actuator_vendor_load_n,
            "actuator_rating_utilization": worst_axial_force / N.actuator_vendor_load_n,
            "factored_3deg_lateral_guide_force_n": lateral_guide_force,
        },
        "envelope": {
            "disconnected_overall_height_mm": N.disconnected_height_mm,
            "platform_length_mm": N.platform_length_mm,
            "platform_width_mm": N.platform_width_mm,
            "moving_shaft_bottom_at_collapse_mm": N.collapsed_joint_z_mm - N.guide_shaft_length_mm,
            "module_top_at_collapse_mm": N.collapsed_joint_z_mm + 60.0,
            "cart_side_receiver_top_when_connected_mm": N.collapsed_joint_z_mm + 75.0,
        },
        "clearance": {
            "actuator_inner_envelope_radius_at_lower_joint_mm": N.lower_joint_radius_mm - 25.0,
            "central_guide_design_envelope_radius_mm": 120.0,
            "minimum_nominal_radial_gap_mm": N.lower_joint_radius_mm - 25.0 - 120.0,
        },
        "stock": {
            "flatbar_cut_length_mm": cut,
            "flatbar_kerf_allowance_mm": kerf,
            "flatbar_reserve_mm": flatbar_reserve,
        },
        "unresolved_checks": [
            "Confirm delivered DHLA2000 pin-centre minimum/maximum length and end accessory stack before drilling joint parts.",
            "Transfer-drill LMF12UU, SK12 and CR-3001 holes from delivered parts; their page tables do not publish complete mounting patterns.",
            "Measure actuator running and inrush current before final breaker and power-supply release.",
            "Perform a manual no-power sweep and a 1.25x stationary proof-load test before powered operation.",
            "No person-carrying, mobile or unattended use is evaluated.",
        ],
    }


def write_outputs(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    output_dir = root / "outputs" / "navimro_fabrication" / "verification"
    output_dir.mkdir(parents=True, exist_ok=True)
    results = verification_results()
    json_path = output_dir / "navimro_fabrication_verification.json"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    w = results["workspace"]
    loads = results["loads"]
    env = results["envelope"]
    clearance = results["clearance"]
    lines = [
        "# NAVIMRO Fabrication Verification",
        "",
        "Status: prototype fabrication baseline for supervised stationary testing only.",
        "",
        "## Workspace",
        "",
        f"- Full +/-3 degree, 0/100 mm corner sweep: {w['minimum_pin_length_mm']:.3f} to {w['maximum_pin_length_mm']:.3f} mm.",
        f"- Provisional actuator envelope: {N.actuator_min_pin_length_mm:.0f} to {N.actuator_max_pin_length_mm:.0f} mm.",
        f"- Retraction/extension margin: {w['retraction_margin_mm']:.3f} / {w['extension_margin_mm']:.3f} mm.",
        "",
        "## Factored load screen",
        "",
        f"- Moving mass assumption: {loads['service_moving_mass_kg']:.1f} kg (10 kg payload + 10 kg cart/interface + 18 kg moving structure).",
        f"- Factored vertical load: {loads['design_vertical_load_n']:.1f} N at design factor {loads['design_factor']:.1f}.",
        f"- With 100 mm plan eccentricity, worst estimated actuator force: {loads['worst_estimated_actuator_axial_force_n']:.1f} N.",
        f"- Utilization against the advertised 2000 N actuator rating: {loads['actuator_rating_utilization'] * 100.0:.1f}%.",
        f"- Factored 3 degree lateral guide load: {loads['factored_3deg_lateral_guide_force_n']:.1f} N.",
        "",
        "## Envelope and clearance",
        "",
        f"- Disconnected overall height including 5 mm shaft projection: {env['disconnected_overall_height_mm']:.1f} mm.",
        f"- Platform envelope: {env['platform_length_mm']:.0f} x {env['platform_width_mm']:.0f} mm.",
        f"- Nominal actuator-to-guide radial gap at the lower joint plane: {clearance['minimum_nominal_radial_gap_mm']:.1f} mm.",
        "- X, Y and yaw are constrained by the twin-shaft fixed-bushing tower; pitch and roll pass through the Cardan; Z passes through both guide shafts.",
        "- Actuator internal electrical limits, split-collar Z hard stops and M8 Cardan angle stops are independent elements.",
        "",
        "## Release blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in results["unresolved_checks"])
    md_path = output_dir / "navimro_fabrication_verification.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [json_path, md_path]


if __name__ == "__main__":
    for path in write_outputs():
        print(path)

