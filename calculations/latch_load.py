from cad.parameters import P


USER_CONFIRMED_COUPLED_MASS_KG = 42.0
ARCHIVED_HEAVY_COUPLED_MASS_KG = 72.0


def latch_screening(coupled_mass_kg=USER_CONFIRMED_COUPLED_MASS_KG,
                    horizontal_accel_g=0.25,
                    vertical_uplift_g=0.2,
                    design_factor=1.5,
                    latch_count=4):
    """Preliminary latch load split. Guide pins carry horizontal shear; latches carry clamp/uplift."""
    shear_design_n = coupled_mass_kg * P.gravity_m_s2 * horizontal_accel_g * design_factor
    uplift_design_n = coupled_mass_kg * P.gravity_m_s2 * vertical_uplift_g * design_factor
    destaco_323r_holding_n = 360.0 * 4.4482216152605
    return {
        "coupled_mass_kg": coupled_mass_kg,
        "horizontal_accel_g": horizontal_accel_g,
        "vertical_uplift_g": vertical_uplift_g,
        "design_factor": design_factor,
        "guide_pin_shear_design_n": shear_design_n,
        "total_latch_uplift_design_n": uplift_design_n,
        "per_latch_uplift_n": uplift_design_n / latch_count,
        "latch_count": latch_count,
        "secondary_lock_required": True,
        "latch_closed_sensor_required": True,
        "latch_preload_n": "TBD after latch geometry and receiver stiffness are defined",
        "destaco_323r_nominal_holding_n": destaco_323r_holding_n,
        "nominal_holding_to_per_latch_ratio": destaco_323r_holding_n / (uplift_design_n / latch_count),
        "note": "Do not use latch holding capacity as horizontal shear capacity.",
    }


def archived_heavy_latch_screening():
    return latch_screening(
        coupled_mass_kg=ARCHIVED_HEAVY_COUPLED_MASS_KG,
        horizontal_accel_g=0.5,
        vertical_uplift_g=0.3,
        design_factor=2.0,
        latch_count=4,
    )


if __name__ == "__main__":
    print({"basis": "active low-load user-confirmed latch case"})
    print(latch_screening())
    print({"basis": "archived heavy latch sensitivity"})
    print(archived_heavy_latch_screening())
