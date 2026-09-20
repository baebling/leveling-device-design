from math import cos, radians, sin, sqrt
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "requirements/system_requirements.md",
    "requirements/assumptions.md",
    "requirements/exclusions.md",
    "concepts/mechanism_A_three_point.md",
    "concepts/mechanism_B_four_point.md",
    "concepts/mechanism_C_gimbal.md",
    "concepts/decision_matrix.md",
    "outputs/renders/concept_isometric.png",
    "outputs/renders/concept_front.png",
    "outputs/renders/concept_side.png",
    "outputs/renders/concept_top.png",
    "outputs/renders/concept_exploded.png",
    "outputs/renders/cart_latch_concept.png",
    "outputs/calculations/preliminary_geometry_report.md",
    "outputs/calculations/unresolved_issues.md",
]


def matmul(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(3)) for i in range(3)]


def rotation(pitch_deg, roll_deg):
    pitch, roll = radians(pitch_deg), radians(roll_deg)
    cp, sp = cos(pitch), sin(pitch)
    cr, sr = cos(roll), sin(roll)
    return [
        [cp, sp * sr, sp * cr],
        [0.0, cr, -sr],
        [-sp, cp * sr, cp * cr],
    ]


def lengths(lift, pitch, roll):
    supports = [(300.0, 0.0), (-280.0, 250.0), (-280.0, -250.0)]
    transform = rotation(pitch, roll)
    result = []
    for x, y in supports:
        rotated = matmul(transform, [x, y, 0.0])
        vector = [rotated[0] - x, rotated[1] - y, rotated[2] + 160.0 + lift]
        result.append(sqrt(sum(component * component for component in vector)))
    return result


def verify_files():
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    if missing:
        raise AssertionError(f"Missing Phase 1 outputs: {missing}")


def verify_images():
    for relative in REQUIRED:
        if not relative.endswith(".png"):
            continue
        with Image.open(ROOT / relative) as image:
            if image.size != (1600, 1000):
                raise AssertionError(f"Unexpected image size for {relative}: {image.size}")
            if image.mode != "RGB":
                raise AssertionError(f"Unexpected image mode for {relative}: {image.mode}")


def verify_kinematics():
    values = [[] for _ in range(3)]
    for lift in (0.0, 50.0, 100.0):
        for pitch in (-3.0, 0.0, 3.0):
            for roll in (-3.0, 0.0, 3.0):
                for index, value in enumerate(lengths(lift, pitch, roll)):
                    values[index].append(value)
    strokes = [max(axis) - min(axis) for axis in values]
    expected = [131.4, 155.4, 155.4]
    for actual, target in zip(strokes, expected):
        if abs(actual - target) > 0.15:
            raise AssertionError(f"Kinematic regression: {strokes}")
    neutral = lengths(50.0, 0.0, 0.0)
    if any(abs(value - 210.0) > 1e-6 for value in neutral):
        raise AssertionError(f"Neutral-length regression: {neutral}")


if __name__ == "__main__":
    verify_files()
    verify_images()
    verify_kinematics()
    print("PASS: 15 Phase 1 deliverables present")
    print("PASS: 6 concept images are 1600 x 1000 RGB")
    print("PASS: three-point kinematic reference values match the report")
