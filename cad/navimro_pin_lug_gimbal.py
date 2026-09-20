"""Preliminary NAVIMRO M8-to-eye pin/lug nested-gimbal CAD seed."""

import cadquery as cq

from .common import COLORS, Component, centered_box, compound, cylinder_between


ASSUMED_EYE_OUTER_DIAMETER_MM = 10.0
ASSUMED_EYE_WIDTH_MM = 10.0
ASSUMED_PIN_DIAMETER_MM = 6.0
ASSUMED_THREAD_DIAMETER_MM = 8.0
U_BRACKET_OUTSIDE_WIDTH_MM = 26.5
U_BRACKET_SIDE_THICKNESS_MM = 3.0
FABRICATED_YOKE_THICKNESS_MM = 6.0


def components():
    half_eye = ASSUMED_EYE_WIDTH_MM / 2.0
    eye = cylinder_between(
        (0.0, -half_eye, 0.0),
        (0.0, half_eye, 0.0),
        ASSUMED_EYE_OUTER_DIAMETER_MM / 2.0,
    ).cut(
        cylinder_between(
            (0.0, -half_eye - 2.0, 0.0),
            (0.0, half_eye + 2.0, 0.0),
            3.05,
        )
    )
    threaded_stud = cylinder_between(
        (0.0, 0.0, -20.0),
        (0.0, 0.0, -5.0),
        ASSUMED_THREAD_DIAMETER_MM / 2.0,
    )
    adapter_reference = compound([eye, threaded_stud])

    side_center_y = (
        U_BRACKET_OUTSIDE_WIDTH_MM - U_BRACKET_SIDE_THICKNESS_MM
    ) / 2.0
    u_parts = []
    for y in (-side_center_y, side_center_y):
        side = centered_box(45.0, U_BRACKET_SIDE_THICKNESS_MM, 30.0, (22.5, y, 0.0)).cut(
            cylinder_between((0.0, y - 3.0, 0.0), (0.0, y + 3.0, 0.0), 3.05)
        )
        u_parts.append(side)
    u_parts.append(centered_box(6.0, U_BRACKET_OUTSIDE_WIDTH_MM, 30.0, (42.0, 0.0, 0.0)))
    inner_u_bracket = compound(u_parts)

    outer_parts = []
    for z in (-18.0, 18.0):
        plate = centered_box(64.0, 38.0, FABRICATED_YOKE_THICKNESS_MM, (10.0, 0.0, z)).cut(
            cylinder_between((0.0, 0.0, z - 4.0), (0.0, 0.0, z + 4.0), 4.15)
        )
        outer_parts.append(plate)
    outer_parts.append(centered_box(6.0, 38.0, 42.0, (42.0, 0.0, 0.0)))
    outer_yoke = compound(outer_parts)

    eye_pin = cylinder_between((0.0, -15.5, 0.0), (0.0, 15.5, 0.0), 3.0)
    trunnions = compound([
        cylinder_between((0.0, 0.0, 15.0), (0.0, 0.0, 24.0), 4.0),
        cylinder_between((0.0, 0.0, -15.0), (0.0, 0.0, -24.0), 4.0),
    ])

    return [
        Component(
            "navimro_m8_eye_adapter_assumption",
            adapter_reference,
            COLORS["orange"],
            "Assumed diameter-10/M8 rod-end accessory envelope",
            category="purchased_reference",
            notes="Eye hole, width, thread engagement and supplied quantity are not vendor-confirmed",
        ),
        Component(
            "navimro_6mm_u_bracket_assumption",
            inner_u_bracket,
            (0.91, 0.77, 0.42, 0.58),
            "Approximate IPS-B1-6MM-U envelope",
            category="purchased_reference",
            notes="Uses web-image outside width and base length; final hole stack remains open",
        ),
        Component(
            "navimro_shared_center_outer_yoke",
            outer_yoke,
            COLORS["navy"],
            "6 mm steel shared-centre orthogonal outer yoke",
            notes="Preliminary local fabrication seed; root attachment is not released",
        ),
        Component(
            "navimro_assumed_6mm_eye_pin",
            eye_pin.val(),
            COLORS["darkgray"],
            "6 mm pivot-pin envelope",
            category="purchased_reference",
            notes="Pin material, shoulder stack and retention require seller confirmation",
        ),
        Component(
            "navimro_opposed_m8_trunnions",
            trunnions,
            COLORS["cyan"],
            "Opposed M8 trunnion envelopes",
            category="purchased",
        ),
    ]


def assembly():
    result = cq.Assembly(name="navimro_pin_lug_nested_gimbal_assumption")
    for component in components():
        r, g, b, a = component.color
        result.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
    return result
