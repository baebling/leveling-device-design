"""Two-piece PHS6 upper-bracket DFM concept for the Rev F PoC.

The model deliberately separates the profile mounting pad from a flat
keyhole-shaped backup support.  It is a visual/DFM concept only: the actual
PHS6 grease-nipple orientation and delivered housing transitions are still
unmeasured, so this geometry is NOT APPROVED FOR FABRICATION.

Local coordinates: PHS6 ball centre at (0, 0, 0), pin axis along Y, PHS6
stem along +Z.  The upper-profile mounting face is z=40 mm.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq


SPLIT_KEYHOLE_SPEC = {
    "status": "CONCEPT / NOT APPROVED FOR FABRICATION",
    "approved_for_fabrication": False,
    "design_load_per_axis_n": 750.0,
    "mount_plate_material": "S45C or SS400, untreated",
    "mount_plate_length_mm": 60.0,
    "mount_plate_width_mm": 30.0,
    "mount_plate_thickness_mm": 10.0,
    "mount_pitch_mm": 44.0,
    "mount_hole_diameter_mm": 6.6,
    "centre_clearance_diameter_mm": 6.6,
    "centre_counterbore_diameter_mm": 11.0,
    "centre_counterbore_depth_mm": 6.0,
    "keyhole_plate_material": "S45C flat plate, 8T",
    "keyhole_plate_width_mm": 48.0,
    "keyhole_plate_height_mm": 48.0,
    "keyhole_plate_thickness_mm": 8.0,
    "phs6_nominal_housing_diameter_mm": 20.0,
    "housing_clearance_diameter_mm": 20.4,
    "stem_slot_width_mm": 14.0,
    "mount_plate_groove_width_mm": 8.2,
    "mount_plate_groove_depth_mm": 4.0,
    "edge_screw_count": 2,
    "edge_screw": "M5 low-head, two places",
    "edge_tap_pilot_diameter_mm": 4.2,
    "edge_screw_clearance_diameter_mm": 5.5,
    "edge_screw_pitch_mm": 26.0,
    "unresolved": [
        "Delivered PHS6 grease-nipple direction/envelope must clear the 14 mm open slot.",
        "Delivered PHS6 housing/neck/foot transitions must be measured before machining.",
        "M5 edge-thread detail and 750 N reversing-load path require supplier DFM review.",
        "This concept has not been checked in the full three-axis moving assembly.",
    ],
}


def _box(x: float, y: float, z: float, centre) -> cq.Shape:
    return cq.Workplane("XY").box(x, y, z).val().translate(centre)


def _cylinder(radius: float, length: float, start, direction=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def build_mount_plate() -> cq.Shape:
    """Return the simple drilled/grooved upper profile mounting plate."""
    d = SPLIT_KEYHOLE_SPEC
    plate = _box(60, 30, 10, (0, 0, 35))

    # Existing 3030-profile fastening pattern.
    for x in (-22.0, 22.0):
        plate = plate.cut(_cylinder(d["mount_hole_diameter_mm"] / 2, 12, (x, 0, 29)))

    # M6 low-head retainer enters from the top and engages the female PHS6 foot.
    plate = plate.cut(_cylinder(d["centre_clearance_diameter_mm"] / 2, 12, (0, 0, 29)))
    plate = plate.cut(
        _cylinder(
            d["centre_counterbore_diameter_mm"] / 2,
            d["centre_counterbore_depth_mm"],
            (0, 0, 34),
        )
    )

    # A straight underside groove locates the 8T backup plate without a deep
    # three-dimensional pocket.  Two screws load the plate edge symmetrically.
    plate = plate.cut(_box(48, d["mount_plate_groove_width_mm"], 4, (0, 0, 32)))
    for x in (-13.0, 13.0):
        plate = plate.cut(_cylinder(d["edge_screw_clearance_diameter_mm"] / 2, 12, (x, 0, 29)))
        plate = plate.cut(_cylinder(4.5, 5, (x, 0, 35)))
    return plate.clean()


def build_keyhole_support() -> cq.Shape:
    """Return the flat 8T keyhole plate that backs up the PHS6 housing.

    The D20.4 circular opening is clearance, not a clamp.  The upper slot is
    intentionally open so the assembled PHS6 can be lowered into the plate.
    """
    d = SPLIT_KEYHOLE_SPEC
    support = _box(48, 8, 48, (0, 0, 10))  # z=-14 ... +34
    support = support.cut(
        _cylinder(d["housing_clearance_diameter_mm"] / 2, 10, (0, -5, 0), (0, 1, 0))
    )
    support = support.cut(_box(d["stem_slot_width_mm"], 10, 35, (0, 0, 17.5)))

    # M5 pilot representation in the top edge.  The fabrication decision
    # remains open: rolled insert or supplier-approved edge tap may replace it.
    for x in (-13.0, 13.0):
        support = support.cut(
            _cylinder(d["edge_tap_pilot_diameter_mm"] / 2, 16, (x, 0, 18), (0, 0, 1))
        )
    return support.clean()


def build_phs6_proxy() -> dict[str, cq.Shape]:
    """Return a nominal PHS6 envelope for visual fit review only."""
    ring = _cylinder(10.0, 6.75, (0, -3.375, 0), (0, 1, 0))
    neck = _cylinder(5.5, 19.0, (0, 0, 6.0))
    foot = _cylinder(6.5, 5.0, (0, 0, 25.0))
    race = cq.Solid.makeSphere(6.35)
    housing = ring.fuse(neck).fuse(foot).cut(race)
    # Visual-only female-thread clearance; not a modeled M6 thread.
    housing = housing.cut(_cylinder(3.0, 12.0, (0, 0, 18.0)))
    ball = cq.Solid.makeSphere(6.30).intersect(_box(16, 9, 16, (0, 0, 0)))
    ball = ball.cut(_cylinder(3.0, 20.0, (0, -10, 0), (0, 1, 0)))

    # The real nipple direction is unknown.  This translucent-review envelope
    # is deliberately kept as a separate part and is not used to claim fit.
    nipple_unknown = _cylinder(3.0, 25.0, (8.0, 0, 0), (1, 0, 0))
    return {
        "housing": housing.clean(),
        "ball": ball.clean(),
        "grease_nipple_unknown": nipple_unknown,
    }


def build_fastener_proxies() -> dict[str, cq.Shape]:
    """Visual envelopes for the central M6 and two edge M5 screws."""
    m6 = _cylinder(3.0, 16.0, (0, 0, 24.0)).fuse(_cylinder(5.2, 4.0, (0, 0, 36.0)))
    m5_left = _cylinder(2.5, 20.0, (-13, 0, 20.0)).fuse(
        _cylinder(4.3, 3.0, (-13, 0, 37.0))
    )
    m5_right = _cylinder(2.5, 20.0, (13, 0, 20.0)).fuse(
        _cylinder(4.3, 3.0, (13, 0, 37.0))
    )
    return {"m6_retainer": m6, "m5_left": m5_left, "m5_right": m5_right}


def assembled_components(*, exploded: bool = False) -> dict[str, cq.Shape]:
    """Return named components for rendering or STEP export."""
    dz = 18.0 if exploded else 0.0
    components = {
        "mount_plate": build_mount_plate().translate((0, 0, dz)),
        "keyhole_support": build_keyhole_support(),
    }
    components.update(build_phs6_proxy())
    for name, shape in build_fastener_proxies().items():
        components[name] = shape.translate((0, 0, dz if exploded else 0.0))
    return components


def build_assembly_compound(*, exploded: bool = False) -> cq.Shape:
    return cq.Compound.makeCompound(list(assembled_components(exploded=exploded).values()))


def export_split_keyhole_concept(output_dir: Path) -> dict:
    """Export the two custom parts and a visual assembly STEP."""
    output_dir.mkdir(parents=True, exist_ok=True)
    step_dir = output_dir / "step"
    step_dir.mkdir(exist_ok=True)
    paths = [
        step_dir / "UPPER_PHS6_SPLIT_01_MOUNT_PLATE_CONCEPT.step",
        step_dir / "UPPER_PHS6_SPLIT_02_KEYHOLE_SUPPORT_CONCEPT.step",
        step_dir / "UPPER_PHS6_SPLIT_ASSEMBLY_CONCEPT.step",
    ]
    cq.exporters.export(build_mount_plate(), str(paths[0]))
    cq.exporters.export(build_keyhole_support(), str(paths[1]))
    cq.exporters.export(build_assembly_compound(), str(paths[2]))

    readme = output_dir / "README_NOT_FOR_FABRICATION.md"
    readme.write_text(
        "# Rev F split-keyhole upper bracket concept\n\n"
        "**CONCEPT / NOT APPROVED FOR FABRICATION OR PURCHASE.**\n\n"
        "This one-axis model replaces the tall one-piece pocket with two simple custom parts: "
        "a 60×30×10 mounting plate and an 8T flat keyhole support. The centre M6 follows the normal "
        "female-rod-end load path; the flat plate provides lateral/compressive backup. The review load "
        "is 750 N per actuator for the supervised indoor self-weight PoC only.\n\n"
        "The PHS6 grease-nipple orientation and housing transitions are not dimensionally verified. "
        "The unknown-nipple proxy intentionally intersects the flat plate in one possible orientation; "
        "that is a HOLD marker, not an interference-free claim. Before any fabrication quote, measure "
        "one delivered PHS6 or obtain a complete supplier model, then rotate/relieve the open slot and "
        "re-run the full three-axis motion check.\n\n"
        "U-bolts are not used because direct clamping can distort the bearing housing and makes clamp "
        "force, grease access, and articulation dependent on assembly torque.\n",
        encoding="utf-8",
    )
    comparison = output_dir / "manufacturing_comparison.json"
    comparison.write_text(
        json.dumps(
            {
                "status": SPLIT_KEYHOLE_SPEC["status"],
                "previous_one_piece": {
                    "custom_parts_per_axis": 1,
                    "processes": ["3D annular pocket milling", "tall rail milling", "side channel", "drilling"],
                    "dfm_risk": "high for a small one-off part",
                },
                "split_concept": {
                    "custom_parts_per_axis": 2,
                    "processes": ["plate cutting", "straight groove", "through drilling", "two edge pilots/taps"],
                    "dfm_risk": "lower, but PHS6 nipple evidence still open",
                },
                "spec": SPLIT_KEYHOLE_SPEC,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "step_files": paths,
        "readme": readme,
        "comparison": comparison,
    }

