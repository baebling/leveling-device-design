from cad.parameters import P


def simply_supported_profile_deflection(load_n=250.0, span_mm=700.0, elastic_modulus_mpa=69000.0, inertia_mm4=10.4e4):
    """Single-beam conservative screen for HFS8-4040; final frame is a grillage, not one beam."""
    deflection_mm = load_n * span_mm ** 3 / (48.0 * elastic_modulus_mpa * inertia_mm4)
    bending_moment_nmm = load_n * span_mm / 4.0
    section_modulus_mm3 = inertia_mm4 / 20.0
    bending_stress_mpa = bending_moment_nmm / section_modulus_mm3
    return {
        "load_n": load_n,
        "span_mm": span_mm,
        "elastic_modulus_mpa": elastic_modulus_mpa,
        "inertia_mm4": inertia_mm4,
        "deflection_mm": deflection_mm,
        "bending_stress_mpa": bending_stress_mpa,
        "allowable_platform_deflection_mm": 2.0,
        "passes_deflection_screen": deflection_mm <= 2.0,
        "source": "SRC-FRM-001",
    }


def acrylic_panel_screen(load_n=250.0, span_mm=240.0):
    width_mm = 100.0
    thickness_mm = P.upper_panel_thickness_mm
    inertia = width_mm * thickness_mm ** 3 / 12.0
    stress = (load_n * span_mm / 4.0) * (thickness_mm / 2.0) / inertia
    deflection = load_n * span_mm ** 3 / (48.0 * P.acrylic_modulus_mpa * inertia)
    return {
        "load_n": load_n,
        "span_mm": span_mm,
        "stress_mpa": stress,
        "deflection_mm": deflection,
        "allowable_stress_mpa": P.acrylic_allowable_stress_mpa,
        "passes_stress_screen": stress <= P.acrylic_allowable_stress_mpa,
    }


if __name__ == "__main__":
    print(simply_supported_profile_deflection())
    print(acrylic_panel_screen())
