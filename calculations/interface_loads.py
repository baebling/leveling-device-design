from cad.parameters import P


def latch_and_pin_screening(total_mass_kg=75.0, horizontal_accel_g=0.5):
    inertial_n = total_mass_kg * P.gravity_m_s2 * horizontal_accel_g
    design_n = inertial_n * P.preliminary_safety_factor
    latch_rating_each_n = 1601.4  # DESTACO 323-R official 360 lbf holding capacity.
    return {
        "mass_kg": total_mass_kg,
        "horizontal_accel_g": horizontal_accel_g,
        "design_shear_n": design_n,
        "four_latch_nominal_capacity_n": 4 * latch_rating_each_n,
        "latch_capacity_ratio": 4 * latch_rating_each_n / design_n,
        "rule": "Guide pins/conical seats take shear and locate X/Y/yaw; latches supply clamp/preload.",
    }


def acrylic_strip_screening(load_n=250.0, width_mm=100.0, thickness_mm=15.0, span_mm=300.0):
    inertia = width_mm * thickness_mm ** 3 / 12.0
    moment = load_n * span_mm / 4.0
    stress = moment * (thickness_mm / 2.0) / inertia
    deflection = load_n * span_mm ** 3 / (48.0 * P.acrylic_modulus_mpa * inertia)
    return {
        "load_n": load_n, "width_mm": width_mm, "thickness_mm": thickness_mm, "span_mm": span_mm,
        "second_moment_mm4": inertia, "stress_mpa": stress, "deflection_mm": deflection,
        "allowable_mpa": P.acrylic_allowable_stress_mpa,
        "passes_stress_only": stress <= P.acrylic_allowable_stress_mpa,
    }
