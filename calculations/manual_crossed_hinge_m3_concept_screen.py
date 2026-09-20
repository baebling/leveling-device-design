"""Phase 1 arithmetic only; not CAD or fabrication approval.
Run with Python 3; prints concept center motion and adjustment travel.
"""
import json
import math


def screen():
    limit = math.radians(3)
    maxima = [0.0, 0.0, 0.0]
    for ip in range(-6, 7):
        for ir in range(-6, 7):
            pitch, roll = math.radians(ip / 2), math.radians(ir / 2)
            # p=a+Ry[(b-a)+Rx(p0-b)]; a=(-125,0,0), b=(0,-125,40)
            vx = 125.0
            vy = -125 + 125 * math.cos(roll) - 40 * math.sin(roll)
            vz = 40 + 125 * math.sin(roll) + 40 * math.cos(roll)
            delta = (
                -125 + math.cos(pitch) * vx + math.sin(pitch) * vz,
                vy,
                -math.sin(pitch) * vx + math.cos(pitch) * vz - 80,
            )
            maxima = [max(m, abs(v)) for m, v in zip(maxima, delta)]
    return {
        "status": "PRELIMINARY_NOT_APPROVED_FOR_FABRICATION",
        "samples": 169,
        "max_abs_center_motion_xyz_mm": maxima,
        "lever_travel": [
            {"lever_mm": d, "travel_each_side_mm": d * math.tan(limit)}
            for d in (200, 250, 300)
        ],
        "example_25kg_factored_screw_load_N": 2 * 25 * 9.80665 * 200 / 250 / math.cos(limit),
        "limitations": "Rigid kinematics and one-stage gravity screen only; no strength or interference validation.",
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2))
