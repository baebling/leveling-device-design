"""LS-01 twin-rod external stop and electrical-limit CAD seed."""

import cadquery as cq

from calculations.actuator_limit_package_screen import package_positions

from .common import COLORS, Component, compound, cylinder_between
from .parameters import P


def _ring(center, axis, outer_radius, inner_radius, width):
    start = center - axis.multiply(width / 2.0)
    end = center + axis.multiply(width / 2.0)
    return cylinder_between(start, end, outer_radius).cut(
        cylinder_between(
            start - axis.multiply(1.0),
            end + axis.multiply(1.0),
            inner_radius,
        )
    )


def _oriented_box(center, axis, tangent, tangent_width, normal_depth, axial_length):
    return cq.Workplane(cq.Plane(
        origin=center,
        xDir=tangent,
        normal=axis,
    )).box(tangent_width, normal_depth, axial_length)


def components(base, top, name):
    base = cq.Vector(*base) if not isinstance(base, cq.Vector) else base
    top = cq.Vector(*top) if not isinstance(top, cq.Vector) else top
    axis = (top - base).normalized()
    tangent = cq.Vector(-axis.y, axis.x, 0.0)
    if tangent.Length <= 1e-9:
        tangent = cq.Vector(0.0, 1.0, 0.0)
    tangent = tangent.normalized()
    normal = axis.cross(tangent).normalized()
    length = (top - base).Length
    positions = package_positions()

    guide_center = base + axis.multiply(P.limit_fixed_guide_station_mm)
    crosshead_center = top - axis.multiply(P.limit_crosshead_offset_from_top_mm)
    adapter_center = crosshead_center - axis.multiply(P.limit_moving_adapter_setback_mm)
    half_spacing = P.limit_guide_rod_spacing_mm / 2.0
    rod_centers = (
        crosshead_center + tangent.multiply(half_spacing),
        crosshead_center - tangent.multiply(half_spacing),
    )

    moving_rods = []
    for center in rod_centers:
        moving_rods.append(cylinder_between(
            center - axis.multiply(P.limit_guide_rod_length_mm),
            center,
            P.limit_guide_rod_diameter_mm / 2.0,
        ))

    crosshead_bridge = _oriented_box(
        adapter_center,
        axis,
        tangent,
        P.limit_guide_rod_spacing_mm + 24.0,
        16.0,
        14.0,
    ).cut(cylinder_between(
        adapter_center - axis.multiply(8.0),
        adapter_center + axis.multiply(8.0),
        P.actuator_rod_radius_mm + 3.0,
    ))
    # The two axial keys show the intended clevis-adapter capture load path.
    # Their final pin and shoulder details require the purchased actuator.
    capture_keys = []
    for sign in (1.0, -1.0):
        key_center = (
            crosshead_center
            - axis.multiply(P.limit_moving_adapter_setback_mm / 2.0)
            + tangent.multiply(sign * (P.actuator_rod_radius_mm + 14.0))
        )
        capture_keys.append(_oriented_box(
            key_center,
            axis,
            tangent,
            6.0,
            10.0,
            P.limit_moving_adapter_setback_mm,
        ))

    # Assembly-oriented envelope derived from the official MB21 STEP. The
    # source shape is retained separately because its imported topology is not
    # suitable for repeated parametric transforms in the main assembly.
    clamp_offset = P.limit_mb21_envelope_axial_mm / 2.0 - 12.0
    carrier = _ring(
        guide_center - axis.multiply(clamp_offset),
        axis,
        P.actuator_body_radius_mm + 7.0,
        P.actuator_body_radius_mm + 0.8,
        10.0,
    ).union(_ring(
        guide_center + axis.multiply(clamp_offset),
        axis,
        P.actuator_body_radius_mm + 7.0,
        P.actuator_body_radius_mm + 0.8,
        10.0,
    ))
    for sign in (1.0, -1.0):
        carrier = carrier.union(_oriented_box(
            guide_center + normal.multiply(sign * 35.0),
            axis,
            tangent,
            P.limit_mb21_envelope_tangent_mm,
            8.0,
            P.limit_mb21_envelope_axial_mm,
        ))
    carrier = carrier.union(_oriented_box(
        guide_center,
        axis,
        tangent,
        P.limit_fixed_carrier_width_mm,
        24.0,
        P.limit_fixed_carrier_thickness_mm,
    )).cut(cylinder_between(
        guide_center - axis.multiply(P.limit_fixed_carrier_thickness_mm),
        guide_center + axis.multiply(P.limit_fixed_carrier_thickness_mm),
        P.actuator_body_radius_mm + 0.6,
    ))
    for sign in (1.0, -1.0):
        carrier = carrier.union(_oriented_box(
            guide_center + tangent.multiply(sign * 42.0),
            axis,
            tangent,
            12.0,
            72.0,
            P.limit_fixed_carrier_thickness_mm,
        ))

    bushing_shapes = []
    for sign in (1.0, -1.0):
        rod_guide_center = guide_center + tangent.multiply(sign * half_spacing)
        bore = cylinder_between(
            rod_guide_center - axis.multiply(P.limit_fixed_carrier_thickness_mm),
            rod_guide_center + axis.multiply(P.limit_fixed_carrier_thickness_mm),
            P.limit_bushing_bore_mm / 2.0,
        )
        carrier = carrier.cut(bore)
        bushing_shapes.append(_ring(
            rod_guide_center,
            axis,
            P.limit_bushing_outer_diameter_mm / 2.0,
            P.limit_bushing_bore_mm / 2.0,
            P.limit_fixed_carrier_thickness_mm,
        ))

    mechanical_shapes = []
    for offset_key in (
        "lower_mechanical_collar_offset_from_crosshead_mm",
        "upper_mechanical_collar_offset_from_crosshead_mm",
    ):
        offset = positions[offset_key]
        for rod_center in rod_centers:
            mechanical_shapes.append(_ring(
                rod_center - axis.multiply(offset),
                axis,
                P.limit_collar_outer_diameter_mm / 2.0,
                P.limit_guide_rod_diameter_mm / 2.0 + 0.15,
                P.limit_collar_width_mm,
            ))

    lower_cam_center = rod_centers[0] - axis.multiply(
        positions["lower_electrical_cam_offset_from_crosshead_mm"]
    )
    upper_cam_center = rod_centers[1] - axis.multiply(
        positions["upper_electrical_cam_offset_from_crosshead_mm"]
    )
    cam_shapes = [
        _ring(
            center,
            axis,
            P.limit_trip_cam_outer_diameter_mm / 2.0,
            P.limit_guide_rod_diameter_mm / 2.0 + 0.15,
            P.limit_trip_cam_width_mm,
        )
        for center in (lower_cam_center, upper_cam_center)
    ]

    switch_shapes = []
    bracket_shapes = []
    for sign in (1.0, -1.0):
        rod_guide_center = guide_center + tangent.multiply(sign * half_spacing)
        switch_center = rod_guide_center + normal.multiply(35.0)
        switch_shapes.append(_oriented_box(
            switch_center,
            axis,
            tangent,
            P.limit_switch_body_width_mm,
            P.limit_switch_body_depth_mm,
            P.limit_switch_body_length_mm,
        ))
        roller_start = rod_guide_center + normal.multiply(20.0)
        roller_end = rod_guide_center + normal.multiply(10.0)
        switch_shapes.append(cylinder_between(
            roller_start,
            roller_end,
            P.limit_switch_roller_diameter_mm / 2.0,
        ))
        bracket_center = rod_guide_center + normal.multiply(53.0)
        bracket = _oriented_box(
            bracket_center,
            axis,
            tangent,
            42.0,
            6.0,
            P.limit_switch_body_length_mm + 18.0,
        )
        for axial_offset in (-22.0, 22.0):
            slot_center = bracket_center + axis.multiply(axial_offset)
            slot = _oriented_box(
                slot_center,
                axis,
                tangent,
                6.5,
                10.0,
                2.0 * P.limit_switch_adjustment_mm + 6.5,
            )
            bracket = bracket.cut(slot)
        bracket_shapes.append(bracket)
        bracket_shapes.append(_oriented_box(
            guide_center + tangent.multiply(sign * half_spacing) + normal.multiply(28.0),
            axis,
            tangent,
            24.0,
            44.0,
            8.0,
        ))

    result = [
        Component(
            f"{name}_limit_fixed_carrier",
            carrier.val(),
            COLORS["darkgray"],
            "MB21-derived fixed body carrier envelope",
            notes="Official MB21 geometry establishes the datum; external stop-reaction acceptance remains open",
        ),
        Component(
            f"{name}_limit_guide_bushings",
            compound(bushing_shapes),
            COLORS["teal"],
            "2x replaceable 12.4 mm bore guide bushings",
            category="purchased_or_fabricated",
            notes="Low-friction guidance only; stop faces react through the fixed carrier",
        ),
        Component(
            f"{name}_limit_moving_striker",
            compound(moving_rods + [crosshead_bridge] + capture_keys),
            COLORS["yellow"],
            "Twin 12 mm rods and keyed clevis-adapter capture crosshead",
            notes="Front pin is the motion datum; final JNT-CG-01 eye and pin-stack measurements remain open",
        ),
        Component(
            f"{name}_external_mechanical_stops",
            compound(mechanical_shapes),
            COLORS["red"],
            "4x 12 mm two-piece steel stop collars, 28 mm OD x 11 mm",
            category="purchased",
            notes="Two collars per direction; verify push-off and impact before fabrication approval",
        ),
    ]
    if P.external_electrical_limit_package_enabled:
        result.extend([
            Component(
                f"{name}_electrical_trip_cams",
                compound(cam_shapes),
                COLORS["cyan"],
                "Separate adjustable electrical trip cams",
                notes="Cams are non-load-bearing and nominally trigger 5 mm before mechanical contact",
            ),
            Component(
                f"{name}_electrical_limit_brackets",
                compound(bracket_shapes),
                COLORS["gray"],
                "Slotted D4N mounting brackets",
                notes="+/-8 mm axial adjustment seed; final fasteners and guarding remain open",
            ),
            Component(
                f"{name}_electrical_limits",
                compound(switch_shapes),
                COLORS["green"],
                "2x Omron D4N roller-plunger envelope",
                category="purchased",
                notes="D4N-4D32 envelope reference; exact contact form, connector and wiring remain open",
            ),
        ])
    return result
