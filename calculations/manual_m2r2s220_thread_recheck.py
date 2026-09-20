"""Independent nominal thread/length audit; no fabrication or load release.

2026-09-09 correction: NBK SHS outer E thread is RH on BOTH studs.
Only the long inner thread changes RH/LH. PHS12L is incompatible.
Uses standard-library math, independently of the historic plotting modules.
"""
from math import sin, cos, radians, sqrt, asin, degrees
import json

LOWER = ((0., 30., 63.), (-30., -180., 63.), (30., -180., 63.))
UPPER = ((0., 250., 0.), (-250., -180., 0.), (250., -180., 0.))
AXES = ((1., 0., 0.), (0., 1., 0.), (0., 1., 0.))
PITCH = 1.75


def pose(pitch, roll):
    p, r = radians(pitch), radians(roll)
    R = ((cos(p), sin(p)*sin(r), sin(p)*cos(r)),
         (0., cos(r), -sin(r)),
         (-sin(p), cos(p)*sin(r), cos(p)*cos(r)))
    t = (-250*R[0][1], -180*(1-R[1][1]), 63+sqrt(280**2-220**2))
    def rotate(v):
        return tuple(sum(R[i][j]*v[j] for j in range(3)) for i in range(3))
    lengths, angles = [], []
    for low, up, axis in zip(LOWER, UPPER, AXES):
        q = rotate(up)
        delta = tuple(q[i]+t[i]-low[i] for i in range(3))
        length = sqrt(sum(v*v for v in delta))
        a = rotate(axis)
        angle = degrees(asin(min(1., abs(sum(delta[i]*a[i] for i in range(3))/length))))
        lengths.append(length)
        angles.append(angle)
    return {"pitch_deg": pitch, "roll_deg": roll, "lengths_mm": lengths,
            "turns_from_280mm": [(x-280)/(2*PITCH) for x in lengths],
            "rod_end_angles_deg": angles}


def sweep(step):
    n = round(6/step)
    minimum, maximum, max_angle = float('inf'), 0., 0.
    min_at = max_at = None
    for i in range(n+1):
        for j in range(n+1):
            row = pose(-3+i*step, -3+j*step)
            for k, length in enumerate(row['lengths_mm']):
                if length < minimum:
                    minimum, min_at = length, [row['pitch_deg'], row['roll_deg'], k+1]
                if length > maximum:
                    maximum, max_at = length, [row['pitch_deg'], row['roll_deg'], k+1]
            max_angle = max(max_angle, *row['rod_end_angles_deg'])
    return {"step_deg": step, "pose_count": (n+1)**2,
            "minimum_mm": minimum, "minimum_pose_leg": min_at,
            "maximum_mm": maximum, "maximum_pose_leg": max_at,
            "max_rod_end_angle_deg": max_angle}


def audit():
    # Nominal lengths, including incomplete thread ends; NOT effective overlap.
    eye_insert, lower_stud_insert, upper_stud_insert = 22., 12., 16.
    thin, thick, external_stud_thread = 7., 10., 24.
    coupling_gap = 36-eye_insert-lower_stud_insert
    fixed_allowance = (50+36-eye_insert-lower_stud_insert)+(50-upper_stud_insert)
    min_length = 171+fixed_allowance
    max_length = min_length+2*(38-18)
    coarse, fine = sweep(.25), sweep(.05)
    for key in ('minimum_mm', 'maximum_mm'):
        assert abs(coarse[key]-fine[key]) < 1e-8
    worst_internal = 38-(fine['maximum_mm']-min_length)/2
    result = {
        "status": "PRELIMINARY_NOMINAL_GEOMETRY_ONLY_NOT_APPROVED_FOR_FABRICATION",
        "thread_correction": "Both STB external E threads are M12x1.75 RH; current MISUMI order code is IKO PHS12A (same audited boundary dimensions), not PHS12L",
        "nut_counts": {"HNT1-ST-M12": 3, "HNT3-ST-M12": 6},
        "external_stack_mm": {
            "BJ761_insert": eye_insert, "BJ761_nut": thin,
            "BJ761_shoulder_clearance": 30-eye_insert-thin,
            "lower_STB_insert": lower_stud_insert, "lower_STB_nut": thick,
            "lower_STB_shoulder_clearance": external_stud_thread-lower_stud_insert-thick,
            "coupling_tip_gap": coupling_gap,
            "upper_STB_insert": upper_stud_insert, "upper_STB_nut": thin,
            "upper_STB_shoulder_clearance": external_stud_thread-upper_stud_insert-thin,
            "IKO_recommended_min_insert": 1.25*12,
            "IKO_insert_margin": upper_stud_insert-1.25*12,
            "PHS12_catalogue_thread_depth": 24.,
            "PHS12_nominal_depth_margin": 24-upper_stud_insert},
        "length_mm": {"fixed_allowance": fixed_allowance, "nominal_available_min": min_length,
            "nominal_available_max_at_18mm_internal": max_length,
            "required_min": fine['minimum_mm'], "required_max": fine['maximum_mm'],
            "short_end_margin": fine['minimum_mm']-min_length,
            "long_end_margin": max_length-fine['maximum_mm'],
            "neutral_pin_distance": 280., "neutral_STB_tip_span": 280-fixed_allowance,
            "neutral_internal_engagement_each_end": 38-(280-min_length)/2,
            "minimum_internal_engagement_each_end": worst_internal,
            "minimum_internal_margin_over_project_18mm": worst_internal-18},
        "turns": {"one_turn_length_change_mm": 2*PITCH,
            "neutral_from_171mm_STB_min": (280-min_length)/(2*PITCH),
            "required_min_from_neutral": (fine['minimum_mm']-280)/(2*PITCH),
            "required_max_from_neutral": (fine['maximum_mm']-280)/(2*PITCH)},
        "sweeps": [coarse, fine],
        "standard_poses": [pose(p,r) for p,r in ((0,0),(3,0),(-3,0),(0,3),(0,-3),(3,3),(3,-3),(-3,3),(-3,-3))],
        "conditional_nominal_length_pass": min_length <= fine['minimum_mm'] and fine['maximum_mm'] <= max_length and worst_internal >= 18,
        "uncertainty": "No certified stack tolerances; 1mm shoulder and insertion margins can be consumed by runout, chamfers, phase alignment and setting error. 18mm internal engagement is a project screen, not NBK compression approval.",
        "load_case": "NO_CART_NO_PAYLOAD; actual upper assembly self-weight unknown; no strength/safety factor established here",
        "coordinate_system": "X right, Y front, Z up; R=Ry(pitch)Rx(roll), yaw=0; dependent X/Y translations follow passive hinge constraints; no independent common Z lift",
        "lubrication": "Not purchased per user; manufacturer lubrication requirement remains. No dry-use approval.",
    }
    assert min_length == 257 and max_length == 297 and fixed_allowance == 86
    assert min(result['external_stack_mm'][k] for k in ('BJ761_shoulder_clearance','lower_STB_shoulder_clearance','upper_STB_shoulder_clearance','coupling_tip_gap','IKO_insert_margin')) > 0
    assert result['conditional_nominal_length_pass']
    return result


if __name__ == '__main__':
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
