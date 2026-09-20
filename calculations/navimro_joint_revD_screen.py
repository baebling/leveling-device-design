"""Kinematic and local-strength screen for the NAVIMRO Rev D actuator joint."""

from itertools import product
from math import acos, cos, degrees, pi, radians, sin, sqrt

from cad.navimro_fabrication_parameters import (
    N,
    NavimroPose,
    actuator_lengths,
    transform_local_point,
)
from calculations.load_distribution import worst_case


ANGLE_MARGIN_DEG = 1.0
STATIC_CAPACITY_FACTOR = 2.0


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _unit(vector):
    length = sqrt(_dot(vector, vector))
    return tuple(value / length for value in vector)


def _angle_deg(a, b):
    return degrees(acos(max(-1.0, min(1.0, _dot(_unit(a), _unit(b))))))


def _rotation_matrix(pose):
    cr, sr = cos(radians(pose.roll_deg)), sin(radians(pose.roll_deg))
    cp, sp = cos(radians(pose.pitch_deg)), sin(radians(pose.pitch_deg))
    return (
        (cp, sp * sr, sp * cr),
        (0.0, cr, -sr),
        (-sp, cp * sr, cp * cr),
    )


def _transpose_multiply(matrix, vector):
    return tuple(
        sum(matrix[row][column] * vector[row] for row in range(3))
        for column in range(3)
    )


def actuator_axes(pose):
    platform_z = N.collapsed_joint_z_mm + pose.lift_mm
    rotation = _rotation_matrix(pose)
    rows = []
    for (ux, uy), (lx, ly) in zip(N.upper_points_xy, N.lower_points_xy):
        top = transform_local_point(
            (ux, uy, N.upper_joint_offset_mm), pose, platform_z
        )
        base = (lx, ly, N.base_joint_z_mm)
        lower = _unit(tuple(t - b for t, b in zip(top, base)))
        upper_world = tuple(b - t for b, t in zip(base, top))
        upper_local = _unit(_transpose_multiply(rotation, upper_world))
        rows.append((lower, upper_local))
    return tuple(rows)


def kinematic_screen(angle_deg=N.max_angle_deg):
    reference = actuator_axes(NavimroPose("reference", 50.0))
    lower_rows = []
    upper_rows = []
    lengths = []
    for lift in range(0, int(N.lift_mm) + 1, 5):
        for pitch, roll in product((-angle_deg, 0.0, angle_deg), repeat=2):
            pose = NavimroPose("sweep", float(lift), pitch, roll)
            lengths.extend(actuator_lengths(pose))
            for index, (current, neutral) in enumerate(
                zip(actuator_axes(pose), reference), start=1
            ):
                lower_rows.append((
                    _angle_deg(current[0], neutral[0]),
                    lift,
                    pitch,
                    roll,
                    index,
                ))
                upper_rows.append((
                    _angle_deg(current[1], neutral[1]),
                    lift,
                    pitch,
                    roll,
                    index,
                ))
    worst_lower = max(lower_rows)
    worst_upper = max(upper_rows)
    required = max(worst_lower[0], worst_upper[0]) + ANGLE_MARGIN_DEG
    return {
        "minimum_pin_center_length_mm": min(lengths),
        "maximum_pin_center_length_mm": max(lengths),
        "worst_lower_joint_deviation_deg": worst_lower[0],
        "worst_lower_pose": worst_lower[1:],
        "worst_upper_joint_deviation_deg": worst_upper[0],
        "worst_upper_pose": worst_upper[1:],
        "required_articulation_with_margin_deg": required,
        "catalog_articulation_deg": N.rod_end_allowable_angle_deg,
        "length_window_pass": (
            min(lengths) >= N.actuator_min_pin_length_mm
            and max(lengths) <= N.actuator_max_pin_length_mm
        ),
        "articulation_pass": required <= N.rod_end_allowable_angle_deg,
    }


def local_strength_screen():
    load = worst_case(
        angle_deg=N.max_angle_deg,
        design_factor=N.design_factor,
        max_eccentricity_mm=100.0,
    )
    force = load["max_axial_force_n"]
    pin_d = N.actuator_yoke_pin_diameter_mm
    lug_t = N.actuator_yoke_lug_thickness_mm
    span = N.actuator_yoke_inner_gap_mm
    pin_area = pi * pin_d ** 2 / 4.0
    pin_shear = force / (2.0 * pin_area)
    pin_moment = force * span / 4.0
    pin_bending = 32.0 * pin_moment / (pi * pin_d ** 3)
    lug_bearing = force / (pin_d * lug_t)
    lug_root_moment = (force / 2.0) * 25.0
    lug_section_modulus = 32.0 * lug_t ** 2 / 6.0
    lug_bending = lug_root_moment / lug_section_modulus
    projected_housing_width = (
        N.rod_end_housing_width_mm
        * cos(radians(N.rod_end_allowable_angle_deg))
        + N.rod_end_outer_diameter_mm
        * sin(radians(N.rod_end_allowable_angle_deg))
    )
    required_capacity = force * STATIC_CAPACITY_FACTOR
    return {
        **load,
        "pin_double_shear_mpa": pin_shear,
        "pin_bending_mpa": pin_bending,
        "lug_bearing_mpa": lug_bearing,
        "lug_root_bending_mpa": lug_bending,
        "projected_housing_width_mm": projected_housing_width,
        "yoke_clearance_mm": N.actuator_yoke_inner_gap_mm
        - projected_housing_width,
        "required_breaking_load_n": required_capacity,
        "catalog_breaking_load_n": N.rod_end_catalog_breaking_load_n,
        "catalog_breaking_load_margin": (
            N.rod_end_catalog_breaking_load_n / required_capacity
        ),
        "preliminary_pass": (
            pin_shear < 100.0
            and pin_bending < 150.0
            and lug_bearing < 100.0
            and lug_bending < 150.0
            and N.actuator_yoke_inner_gap_mm - projected_housing_width > 2.0
            and N.rod_end_catalog_breaking_load_n >= required_capacity
        ),
    }


def summary():
    return {
        "joint": "NAVIMRO K02020097 / JMC JFT-8R in NVR-P03/P04/P16 double-shear yoke",
        "kinematics": kinematic_screen(),
        "local_strength": local_strength_screen(),
        "release_status": "PRELIMINARY_POC_NOT_APPROVED_FOR_FABRICATION",
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(summary())
