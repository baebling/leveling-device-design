def power_budget(actuator_voltage_v=12.0, actuator_full_load_current_a=5.5, actuator_count=3,
                 controller_current_a=1.0, margin=1.3, driver_channels=3):
    continuous_current_a = actuator_full_load_current_a * actuator_count + controller_current_a
    recommended_supply_current_a = continuous_current_a * margin
    return {
        "actuator_voltage_v": actuator_voltage_v,
        "actuator_count": actuator_count,
        "independent_driver_channels_required": driver_channels,
        "assumed_full_load_current_per_actuator_a": actuator_full_load_current_a,
        "controller_current_a": controller_current_a,
        "continuous_current_a": continuous_current_a,
        "margin": margin,
        "recommended_supply_current_a": recommended_supply_current_a,
        "recommended_supply_power_w": actuator_voltage_v * recommended_supply_current_a,
        "candidate_supply": "For 12 V Firgelli baseline, use a 12 V supply around this current class; 24 V bus requires a 24 V actuator variant or a large DC-DC converter.",
    }


def power_architecture_options():
    return {
        "option_a_12v_firgelli_baseline": power_budget(),
        "option_b_24v_actuator_reselection": power_budget(
            actuator_voltage_v=24.0,
            actuator_full_load_current_a=6.0,
            controller_current_a=1.0,
            margin=1.25,
        ),
        "note": "Do not approve a 24 V bus while the baseline actuator remains the 12 V SKU.",
    }


if __name__ == "__main__":
    print(power_architecture_options())
