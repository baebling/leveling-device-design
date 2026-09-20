"""JNT-CG-01 factory-eye nested-gimbal measured-mockup CAD seed."""

import cadquery as cq

from .common import COLORS, Component, centered_box, compound, cylinder_between


def components():
    factory_eye = cylinder_between((0.0, -5.5, 0.0), (0.0, 5.5, 0.0), 10.0).cut(
        cylinder_between((0.0, -7.0, 0.0), (0.0, 7.0, 0.0), 4.1)
    )

    inner_parts = []
    for y in (-9.0, 9.0):
        plate = centered_box(40.0, 6.0, 32.0, (0.0, y, 0.0)).cut(
            cylinder_between((0.0, y - 4.0, 0.0), (0.0, y + 4.0, 0.0), 4.15)
        )
        inner_parts.append(plate)
    for x in (-17.0, 17.0):
        inner_parts.append(centered_box(6.0, 24.0, 32.0, (x, 0.0, 0.0)))
    inner_cradle = compound(inner_parts)

    outer_parts = []
    for z in (-20.0, 20.0):
        lug = centered_box(52.0, 42.0, 6.0, (4.0, 0.0, z)).cut(
            cylinder_between((0.0, 0.0, z - 4.0), (0.0, 0.0, z + 4.0), 4.15)
        )
        outer_parts.append(lug)
    outer_parts.append(centered_box(8.0, 42.0, 52.0, (34.0, 0.0, 0.0)))
    outer_yoke = compound(outer_parts)

    factory_pin = cylinder_between((0.0, -17.0, 0.0), (0.0, 17.0, 0.0), 4.0)
    trunnions = compound([
        cylinder_between((0.0, 0.0, 16.0), (0.0, 0.0, 25.0), 4.0),
        cylinder_between((0.0, 0.0, -16.0), (0.0, 0.0, -25.0), 4.0),
    ])

    return [
        Component(
            "jnt_cg01_factory_eye_reference",
            factory_eye.val(),
            COLORS["orange"],
            "Firgelli factory mounting-eye envelope",
            category="purchased_reference",
            notes="11 mm eye-width reference; replace with purchased-part measurement",
        ),
        Component(
            "jnt_cg01_inner_cradle",
            inner_cradle,
            COLORS["yellow"],
            "6 mm plate nested-gimbal inner cradle",
            notes="12 mm eye gap; cut/weld or machined mock-up topology remains open",
        ),
        Component(
            "jnt_cg01_outer_yoke",
            outer_yoke,
            COLORS["navy"],
            "6 mm plate outer trunnion yoke",
            notes="Root attachment pattern is intentionally not released",
        ),
        Component(
            "jnt_cg01_factory_pin",
            factory_pin.val(),
            COLORS["darkgray"],
            "M8 factory-eye pin envelope",
            category="purchased",
        ),
        Component(
            "jnt_cg01_opposed_trunnions",
            trunnions,
            COLORS["cyan"],
            "Opposed M8 shoulder-screw trunnion envelopes",
            category="purchased",
            notes="Use opposed stubs, not a second full through-pin across the factory pin",
        ),
    ]


def assembly():
    result = cq.Assembly(name="jnt_cg01_factory_eye_nested_gimbal_seed")
    for component in components():
        r, g, b, a = component.color
        result.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
    return result
