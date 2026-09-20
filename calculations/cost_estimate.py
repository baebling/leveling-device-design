def cost_estimate_krw():
    rows = [
        ("structure_frame", 350000, 550000, 850000),
        ("plates_and_brackets", 450000, 750000, 1200000),
        ("actuators_3ea", 750000, 1100000, 2100000),
        ("guide_joint_bearing", 300000, 600000, 1300000),
        ("cart_coupling_latches_pins", 250000, 500000, 1000000),
        ("sensors_and_control", 250000, 450000, 850000),
        ("drivers_power_safety", 350000, 650000, 1200000),
        ("wiring_enclosure_misc", 200000, 350000, 700000),
        ("outsourced_processing", 450000, 750000, 1400000),
        ("contingency_rework", 250000, 450000, 800000),
    ]
    totals = {
        "low": sum(row[1] for row in rows),
        "target": sum(row[2] for row in rows),
        "high": sum(row[3] for row in rows),
    }
    return {"rows": rows, "totals": totals, "budget_limit_krw": 4000000}


if __name__ == "__main__":
    print(cost_estimate_krw())
