from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Pose:
    lift_mm: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    cart_coupled: bool = True
    label: str = "collapsed"


@dataclass(frozen=True)
class Parameters:
    concept_approval_date: str = "2026-08-26"
    phase_status: str = "PHASE_2_DETAILED_CAD_APPROVED"
    design_variant: str = "RADIAL_3_CLEAN"
    prototype_operating_mode: str = "STATIC_BENCH_LOW_SPEED"
    external_electrical_limit_package_enabled: bool = False
    external_mechanical_stops_enabled: bool = True

    # Overall nominal envelope. Cart-body dimensions remain unknown.
    platform_length_mm: float = 900.0
    platform_width_mm: float = 800.0
    # Approved WS-01-H20 PoC envelope. The disconnected level/collapsed
    # device height remains inside the user-confirmed 250 to 300 mm range.
    target_collapsed_height_mm: float = 270.0
    target_disconnected_height_min_mm: float = 250.0
    target_disconnected_height_max_mm: float = 300.0
    target_lift_mm: float = 100.0
    recommended_angle_deg: float = 3.0

    # Selected web-purchasable actuator: Firgelli F-SD-H-450-12V-8.
    actuator_model: str = "Firgelli F-SD-H-450-12V-8in Hall"
    actuator_retracted_mm: float = 319.0
    actuator_extended_mm: float = 523.0
    actuator_stroke_mm: float = 203.2
    actuator_dynamic_force_n: float = 2001.7
    actuator_static_force_n: float = 2001.7
    actuator_no_load_speed_mm_s: float = 6.0
    actuator_max_current_a: float = 5.5
    actuator_duty_cycle: float = 0.25
    actuator_feedback_pulses_per_mm: float = 41.1
    actuator_clevis_hole_mm: float = 8.2
    actuator_yoke_pin_diameter_mm: float = 8.0
    actuator_yoke_lug_thickness_mm: float = 8.0
    # HRT8E official envelope: 8 mm bore, 23 mm body diameter, 11 mm eye
    # width and 14 deg allowable articulation. An 18 mm inner gap clears the
    # projected 14 deg body envelope with a small preliminary reserve; the
    # earlier 16 mm maximum-span seed was too tight once official dimensions
    # were applied.
    actuator_yoke_inner_gap_mm: float = 18.0
    actuator_rod_end_bore_mm: float = 8.0
    actuator_rod_end_eye_width_mm: float = 11.0
    actuator_rod_end_outer_diameter_mm: float = 23.0
    actuator_rod_end_thread: str = "M8x1.25"
    actuator_rod_end_allowable_angle_deg: float = 14.0
    actuator_misalignment_spacer_width_mm: float = 3.5
    actuator_misalignment_spacer_outer_diameter_mm: float = 10.8
    actuator_lug_bushing_outer_diameter_mm: float = 12.0
    actuator_lug_bushing_bore_mm: float = 8.2
    actuator_pin_head_diameter_mm: float = 14.0
    actuator_pin_head_thickness_mm: float = 5.0
    actuator_pin_retainer_diameter_mm: float = 14.0
    actuator_pin_retainer_thickness_mm: float = 6.5
    actuator_bracket_mount_plate_thickness_mm: float = 8.0
    actuator_bracket_mount_hole_mm: float = 8.5
    actuator_min_end_margin_mm: float = 5.0
    # Radially inclined tripod. WS-01-H20 preserves the screened horizontal
    # offset while raising the collapsed joint plane by 20 mm.
    # level/collapsed, eliminating the disallowed vertical-stick arrangement.
    actuator_level_length_at_lift0_mm: float = 359.87286886991865
    actuator_vertical_separation_collapsed_mm: float = 185.0
    base_joint_z_mm: float = 50.0
    actuator_body_length_mm: float = 250.0
    actuator_body_radius_mm: float = 29.0
    actuator_rod_radius_mm: float = 16.0
    actuator_motor_box_x_mm: float = 115.0
    actuator_motor_box_y_mm: float = 70.0
    actuator_motor_box_z_mm: float = 45.0

    # Equilateral upper joint triangle (radius 400 mm) and concentric lower
    # joint triangle. Radial inclination cancels lateral force resultants for
    # a centered load and is simpler to fabricate than a twisted tripod.
    support_radius_mm: float = 400.0
    support_a1_x_mm: float = 400.0
    support_a1_y_mm: float = 0.0
    support_a2_x_mm: float = -200.0
    support_a2_y_mm: float = 346.4101615137755
    support_a3_x_mm: float = -200.0
    support_a3_y_mm: float = -346.4101615137755

    # Hybrid structural architecture.
    material_variant: str = "hybrid_acrylic"
    lower_plate_thickness_mm: float = 8.0
    upper_panel_thickness_mm: float = 15.0
    frame_size_mm: float = 40.0
    lower_frame_center_z_mm: float = 28.0
    upper_frame_half_height_mm: float = 20.0
    adapter_rail_height_mm: float = 30.0
    adapter_rail_width_mm: float = 60.0
    module_top_above_joint_mm: float = 35.0

    # Central keyed square-tube slide and two-axis gimbal head.
    guide_outer_size_mm: float = 50.0
    guide_outer_wall_mm: float = 3.0
    guide_outer_z0_mm: float = 8.0
    guide_outer_length_mm: float = 195.0
    guide_inner_size_mm: float = 42.0
    guide_inner_wall_mm: float = 3.0
    guide_inner_length_mm: float = 220.0
    guide_min_overlap_mm: float = 80.0
    guide_yaw_clearance_target_mm: float = 0.2
    cardan_design_angle_deg: float = 8.0
    gimbal_pin_stop_angle_deg: float = 7.0
    cardan_hard_stop_angle_deg: float = 10.0
    gimbal_pin_diameter_mm: float = 12.0
    gimbal_lug_thickness_mm: float = 8.0
    gimbal_yoke_span_mm: float = 100.0

    # Independent external Z-travel stop seed. The stop bars remain outside
    # the keyed tube bore; electrical switches are separate components.
    lift_stop_post_spacing_mm: float = 130.0
    lift_stop_post_x_offset_mm: float = 35.0
    lift_stop_post_diameter_mm: float = 10.0
    lift_stop_nut_diameter_mm: float = 24.0
    lift_stop_bar_offset_below_joint_mm: float = 25.0
    lift_stop_bar_thickness_mm: float = 8.0
    lift_stop_contact_clearance_mm: float = 2.0
    lift_limit_switch_inset_mm: float = 3.0
    upper_service_opening_x_mm: float = 0.0
    upper_service_opening_y_mm: float = 0.0

    # LS-01 actuator-axis travel limiter cassette. The fixed station is placed
    # on the official MB21 body-bracket zone. The moving datum is the front
    # clevis pin centre; the crosshead must capture a clevis adapter and may
    # not clamp the chrome rod. Values remain adjustable mock-up seeds.
    limit_fixed_guide_station_mm: float = 220.0
    limit_crosshead_offset_from_top_mm: float = 0.0
    limit_guide_rod_diameter_mm: float = 12.0
    limit_guide_rod_spacing_mm: float = 104.0
    limit_guide_rod_length_mm: float = 320.0
    limit_collar_outer_diameter_mm: float = 28.0
    limit_collar_width_mm: float = 11.0
    limit_fixed_carrier_width_mm: float = 132.0
    limit_fixed_carrier_thickness_mm: float = 14.0
    limit_mb21_envelope_tangent_mm: float = 50.0
    limit_mb21_envelope_normal_mm: float = 82.854
    limit_mb21_envelope_axial_mm: float = 100.0
    limit_moving_adapter_setback_mm: float = 32.0
    limit_bushing_outer_diameter_mm: float = 16.0
    limit_bushing_bore_mm: float = 12.4
    limit_trip_cam_outer_diameter_mm: float = 20.0
    limit_trip_cam_width_mm: float = 8.0
    limit_switch_body_length_mm: float = 65.0
    limit_switch_body_width_mm: float = 31.0
    limit_switch_body_depth_mm: float = 30.0
    limit_switch_roller_diameter_mm: float = 9.5
    limit_switch_adjustment_mm: float = 8.0

    # Factory-clevis joint adapter inputs. The archived STEP establishes the
    # pin axis and 8.2 mm hole, but not a trustworthy manufacturing stack.
    # These remain measured-input placeholders and are not fabrication values.
    actuator_factory_clevis_width_mm: float = 20.0
    actuator_factory_clevis_pin_stack_mm: float = 32.0
    actuator_joint_adapter_plate_thickness_mm: float = 6.0
    actuator_joint_adapter_pin_edge_mm: float = 12.0

    # Dummy cart interface. These are parameters, not measurements from images.
    cart_interface_length_mm: float = 650.0
    cart_interface_width_mm: float = 500.0
    cart_frame_member_width_mm: float = 60.0
    guide_pin_spacing_x_mm: float = 600.0
    guide_pin_spacing_y_mm: float = 540.0
    latch_spacing_mm: float = 700.0
    cart_disengaged_gap_mm: float = 120.0

    # Load and material assumptions.
    payload_cases_kg: tuple = (5.0, 10.0)
    cart_mass_cases_kg: tuple = (10.0, 20.0, 30.0)
    moving_structure_mass_range_kg: tuple = (15.0, 22.0)
    total_module_mass_range_kg: tuple = (55.0, 75.0)
    preliminary_safety_factor: float = 2.0
    gravity_m_s2: float = 9.80665
    eccentricity_x_mm: float = 0.0
    eccentricity_y_mm: float = 0.0
    eccentricity_sensitivity_mm: tuple = (0.0, 50.0, 100.0)
    acrylic_density_kg_m3: float = 1190.0
    acrylic_modulus_mpa: float = 3300.0
    acrylic_allowable_stress_mpa: float = 5.0
    acrylic_demo_max_payload_kg: float = 5.0

    # Electrical placeholders from official product specifications.
    supply_voltage_v: float = 12.0
    supply_current_a: float = 29.0
    motor_driver_continuous_a: float = 13.0

    @property
    def support_points_xy(self):
        return (
            (self.support_a1_x_mm, self.support_a1_y_mm),
            (self.support_a2_x_mm, self.support_a2_y_mm),
            (self.support_a3_x_mm, self.support_a3_y_mm),
        )

    @property
    def actuator_horizontal_offset_mm(self):
        return sqrt(
            self.actuator_level_length_at_lift0_mm ** 2
            - self.actuator_vertical_separation_collapsed_mm ** 2
        )

    @property
    def base_support_radius_mm(self):
        return self.support_radius_mm - self.actuator_horizontal_offset_mm

    @property
    def actuator_incline_from_horizontal_deg(self):
        return degrees(atan2(
            self.actuator_vertical_separation_collapsed_mm,
            self.actuator_horizontal_offset_mm,
        ))

    @property
    def base_points_xy(self):
        radius = self.base_support_radius_mm
        return tuple(
            (radius * cos(radians(angle)), radius * sin(radians(angle)))
            for angle in (0.0, 120.0, 240.0)
        )

    @property
    def platform_joint_z_collapsed_mm(self):
        return self.base_joint_z_mm + self.actuator_vertical_separation_collapsed_mm

    @property
    def commercial_collapsed_height_mm(self):
        return self.platform_joint_z_collapsed_mm + self.module_top_above_joint_mm

    @property
    def commercial_neutral_height_mm(self):
        return self.commercial_collapsed_height_mm + 50.0

    @property
    def commercial_raised_height_mm(self):
        return self.commercial_collapsed_height_mm + 100.0


P = Parameters()


POSES = {
    "collapsed": Pose(0.0, 0.0, 0.0, True, "collapsed"),
    "neutral": Pose(50.0, 0.0, 0.0, True, "neutral"),
    "raised": Pose(100.0, 0.0, 0.0, True, "raised"),
    "max_pitch": Pose(50.0, 3.0, 0.0, True, "max_pitch"),
    "max_roll": Pose(50.0, 0.0, 3.0, True, "max_roll"),
    "max_pitch_roll": Pose(100.0, 3.0, 3.0, True, "max_pitch_roll"),
    "cart_disengaged": Pose(0.0, 0.0, 0.0, False, "cart_disengaged"),
}
