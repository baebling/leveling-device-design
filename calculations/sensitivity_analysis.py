from calculations.kinematics import summary as kinematic_summary


def angle_sensitivity():
    return [kinematic_summary(angle) for angle in (3.0, 5.0, 8.0)]
