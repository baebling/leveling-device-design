"""Fabrication baseline for the NAVIMRO single-order proof-of-concept.

Dimensions are millimetres. Vendor-interface dimensions that are not visible in
an authoritative drawing remain explicitly provisional and are excluded from
pre-drilled fabrication features.
"""

from dataclasses import dataclass
from math import cos, radians, sin, sqrt


@dataclass(frozen=True)
class NavimroPose:
    label: str
    lift_mm: float
    pitch_deg: float = 0.0
    roll_deg: float = 0.0


@dataclass(frozen=True)
class NavimroFabricationParameters:
    platform_length_mm: float = 900.0
    platform_width_mm: float = 800.0
    acrylic_thickness_mm: float = 15.0
    profile_size_mm: float = 40.0

    collapsed_joint_z_mm: float = 235.0
    # Rev E retains both actuator yokes below their supporting 4040 members.
    # Keeping the same offset at both ends preserves the screened actuator
    # length window while clearing the frame and the upper work surface.
    base_joint_z_mm: float = -10.0
    upper_joint_offset_mm: float = -38.0
    lift_mm: float = 100.0
    max_angle_deg: float = 3.0
    upper_joint_radius_mm: float = 400.0
    lower_joint_radius_mm: float = 195.0

    actuator_min_pin_length_mm: float = 265.0
    actuator_max_pin_length_mm: float = 415.0
    actuator_vendor_stroke_mm: float = 150.0
    actuator_vendor_load_n: float = 2000.0

    # NAVIMRO K02020097 / JMC JFT-8R catalog geometry.
    rod_end_model: str = "JFT-8R"
    rod_end_bore_mm: float = 8.0
    rod_end_outer_diameter_mm: float = 24.0
    rod_end_housing_width_mm: float = 9.0
    rod_end_ball_width_mm: float = 12.0
    rod_end_center_to_end_mm: float = 36.0
    rod_end_thread_depth_mm: float = 17.0
    rod_end_thread: str = "M8x1.25 RH female"
    rod_end_allowable_angle_deg: float = 13.0
    rod_end_catalog_breaking_load_n: float = 760.0 * 9.80665
    actuator_yoke_inner_gap_mm: float = 20.0
    actuator_yoke_lug_thickness_mm: float = 6.0
    actuator_yoke_pin_diameter_mm: float = 8.0
    actuator_yoke_pin_hole_mm: float = 8.2
    actuator_yoke_pin_drop_mm: float = 15.0

    lower_long_length_mm: float = 820.0
    lower_end_length_mm: float = 640.0
    upper_long_length_mm: float = 840.0
    upper_end_length_mm: float = 660.0
    lower_crossmember_length_mm: float = 640.0
    upper_crossmember_length_mm: float = 660.0
    # Legacy Rev A exports retain the old 560 mm placeholder until their
    # separate drawing package is regenerated. Rev E detailed CAD uses the
    # physically connected lower/upper values above.
    crossmember_length_mm: float = 560.0
    upper_center_length_mm: float = 420.0
    carriage_length_mm: float = 240.0
    cart_receiver_length_mm: float = 760.0

    # Compatibility only for the archived Rev A fabrication exporter. Rev E
    # detailed CAD uses the single carriage_center_offset_mm value below.
    carriage_lower_offset_mm: float = -145.0
    carriage_upper_offset_mm: float = -105.0

    guide_shaft_diameter_mm: float = 12.0
    guide_shaft_x_mm: float = 60.0
    guide_shaft_y_mm: float = 43.0
    guide_shaft_length_mm: float = 230.0
    guide_shaft_top_offset_mm: float = -29.0
    fixed_bushing_lower_z_mm: float = 94.0
    fixed_bushing_upper_z_mm: float = 124.0
    carriage_center_offset_mm: float = -78.0
    guide_riser_length_mm: float = 200.0
    guide_riser_offset_from_shaft_mm: float = 40.0

    # Rev E uses two vertically offset pivots in one compact serial gimbal.
    # The offset prevents the M8 X/Y pins from occupying the same material.
    cardan_upper_axis_offset_mm: float = -34.0
    cardan_lower_axis_offset_mm: float = -46.0
    cardan_upper_bridge_offset_mm: float = -23.0
    cardan_lower_bridge_offset_mm: float = -55.0
    cardan_yoke_offset_mm: float = 28.5
    cardan_cross_size_mm: float = 50.0
    cardan_cross_height_mm: float = 24.0

    lower_frame_center_z_mm: float = 28.0
    cart_rail_y_mm: float = 260.0
    locator_x_mm: float = 260.0
    latch_x_mm: float = 330.0
    latch_y_mm: float = 260.0

    flatbar_width_mm: float = 50.0
    flatbar_thickness_mm: float = 6.0
    flatbar_stock_length_mm: float = 6000.0
    flatbar_stock_count: int = 2
    saw_kerf_mm: float = 2.0

    payload_kg: float = 10.0
    cart_mass_kg: float = 10.0
    moving_structure_mass_kg: float = 18.0
    design_factor: float = 2.0

    @property
    def upper_points_xy(self):
        return radial_points(self.upper_joint_radius_mm)

    @property
    def lower_points_xy(self):
        return radial_points(self.lower_joint_radius_mm)

    @property
    def guide_shaft_points_xy(self):
        return (
            (-self.guide_shaft_x_mm, -self.guide_shaft_y_mm),
            (self.guide_shaft_x_mm, self.guide_shaft_y_mm),
        )

    @property
    def disconnected_height_mm(self):
        top = self.collapsed_joint_z_mm + 41.0
        bottom = min(
            self.base_joint_z_mm - 14.0,
            self.collapsed_joint_z_mm + self.guide_shaft_top_offset_mm - self.guide_shaft_length_mm,
        )
        return top - bottom


def radial_points(radius_mm):
    return tuple(
        (radius_mm * cos(radians(angle)), radius_mm * sin(radians(angle)))
        for angle in (0.0, 120.0, 240.0)
    )


def transform_local_point(point, pose, platform_z_mm):
    """Map an upper-platform point through the Rev E serial Cardan axes."""
    x, y, z = point
    upper_axis_z = -34.0
    lower_axis_z = -46.0
    z -= upper_axis_z
    cr, sr = cos(radians(pose.roll_deg)), sin(radians(pose.roll_deg))
    cp, sp = cos(radians(pose.pitch_deg)), sin(radians(pose.pitch_deg))
    y1, z1 = y * cr - z * sr, y * sr + z * cr
    z1 += upper_axis_z - lower_axis_z
    x2, z2 = x * cp + z1 * sp, -x * sp + z1 * cp
    return x2, y1, z2 + platform_z_mm + lower_axis_z


def actuator_lengths(pose, parameters=None):
    p = parameters or N
    platform_z = p.collapsed_joint_z_mm + pose.lift_mm
    lengths = []
    for (tx, ty), (bx, by) in zip(p.upper_points_xy, p.lower_points_xy):
        x, y, z = transform_local_point(
            (tx, ty, p.upper_joint_offset_mm), pose, platform_z
        )
        lengths.append(sqrt((x - bx) ** 2 + (y - by) ** 2 + (z - p.base_joint_z_mm) ** 2))
    return tuple(lengths)


N = NavimroFabricationParameters()

NAVIMRO_POSES = {
    "collapsed": NavimroPose("collapsed", 0.0),
    "neutral": NavimroPose("neutral", 50.0),
    "raised": NavimroPose("raised", 100.0),
    "max_pitch": NavimroPose("max_pitch", 50.0, pitch_deg=3.0),
    "max_roll": NavimroPose("max_roll", 50.0, roll_deg=3.0),
    "max_pitch_roll": NavimroPose("max_pitch_roll", 50.0, pitch_deg=3.0, roll_deg=3.0),
}
