"""Six-variable forward kinematics for the retained radial 3-RPS geometry."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fusion_scripts.ProfileRadialRevD import revd_data


@dataclass(frozen=True)
class PoseSolution:
    x_mm: float
    y_mm: float
    lift_mm: float
    pitch_deg: float
    roll_deg: float
    yaw_rad: float
    residual_mm: float
    iterations: int
    converged: bool
    target_lengths_mm: tuple[float, float, float]

    def as_seed(self):
        return (
            self.x_mm,
            self.y_mm,
            self.lift_mm,
            self.pitch_deg,
            self.roll_deg,
            self.yaw_rad,
        )


def _dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def _residual(values, target_lengths_mm):
    x_mm, y_mm, lift_mm, pitch_deg, roll_deg, yaw_rad = values
    rotation = revd_data.rotation_matrix(pitch_deg, roll_deg, yaw_rad)
    z_mm = revd_data.P.upper_ring_z_collapsed_mm + lift_mm
    length_rows = []
    constraint_rows = []
    for lower, upper_local, (_, tangent), target in zip(
        revd_data.lower_eye_points(),
        revd_data.upper_eye_local_points(),
        revd_data.support_basis(),
        target_lengths_mm,
    ):
        rotated = _matvec(rotation, upper_local)
        upper = (
            rotated[0] + x_mm,
            rotated[1] + y_mm,
            rotated[2] + z_mm,
        )
        actuator = tuple(upper[axis] - lower[axis] for axis in range(3))
        length_rows.append(sqrt(_dot(actuator, actuator)) - target)
        constraint_rows.append(_dot(actuator, tangent))
    return tuple(length_rows + constraint_rows)


def _solve_linear(matrix, vector):
    size = len(vector)
    rows = [list(matrix[row]) + [vector[row]] for row in range(size)]
    for pivot in range(size):
        selected = max(range(pivot, size), key=lambda row: abs(rows[row][pivot]))
        if abs(rows[selected][pivot]) < 1e-12:
            raise ValueError("Singular 3-RPS forward-kinematics Jacobian")
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for row in range(pivot + 1, size):
            scale = rows[row][pivot] / rows[pivot][pivot]
            for column in range(pivot, size + 1):
                rows[row][column] -= scale * rows[pivot][column]
    result = [0.0] * size
    for row in range(size - 1, -1, -1):
        result[row] = (
            rows[row][size]
            - sum(rows[row][column] * result[column] for column in range(row + 1, size))
        ) / rows[row][row]
    return tuple(result)


def solve_pose_from_lengths(
    lengths_mm,
    seed=(0.0, 0.0, 25.0, 0.0, 0.0, 0.0),
    *,
    tolerance_mm: float = 1e-8,
    max_iterations: int = 30,
):
    """Solve x/y/lift/pitch/roll/yaw from three actuator pin lengths.

    Three length equations and the three revolute-axis tangent constraints are
    solved together. Pitch and roll variables use degrees; yaw uses radians.
    """

    target = tuple(float(value) for value in lengths_mm)
    if len(target) != 3 or any(value <= 0.0 for value in target):
        raise ValueError("exactly three positive pin lengths are required")
    if isinstance(seed, PoseSolution):
        values = list(seed.as_seed())
    else:
        values = [float(value) for value in seed]
    if len(values) != 6:
        raise ValueError("seed must contain x, y, lift, pitch, roll, yaw")

    steps = (1e-4, 1e-4, 1e-4, 1e-5, 1e-5, 1e-7)
    iterations = 0
    converged = False
    for iterations in range(max_iterations + 1):
        residual = _residual(values, target)
        if max(abs(value) for value in residual) <= tolerance_mm:
            converged = True
            break
        if iterations == max_iterations:
            break
        columns = []
        for axis, step in enumerate(steps):
            shifted = list(values)
            shifted[axis] += step
            moved = _residual(shifted, target)
            columns.append(
                tuple(
                    (moved[row] - residual[row]) / step
                    for row in range(6)
                )
            )
        jacobian = tuple(
            tuple(columns[column][row] for column in range(6))
            for row in range(6)
        )
        delta = _solve_linear(jacobian, tuple(-value for value in residual))
        values = [values[index] + delta[index] for index in range(6)]

    final_residual = _residual(values, target)
    return PoseSolution(
        x_mm=values[0],
        y_mm=values[1],
        lift_mm=values[2],
        pitch_deg=values[3],
        roll_deg=values[4],
        yaw_rad=values[5],
        residual_mm=max(abs(value) for value in final_residual),
        iterations=iterations,
        converged=converged,
        target_lengths_mm=target,
    )
