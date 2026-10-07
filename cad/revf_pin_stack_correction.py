"""Stock-only 40 mm upper pin correction; historical CAD remains untouched.

Only extra pin length and ring-side packing change. Spherical bearing and
actuator-eye centres are retained. Shape envelopes are not strength proof.
"""
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import cadquery as cq
from cad.profile_radial_revf_upper_pocket_review import local_review_geometry, _place
from cad.revf_upper_pocket_inputs import load_inputs
from cad.revf_direct_phs6_mount import placed_direct_mount_plate, _intersection
from cad.profile_radial_reve_actual_vendor import (
    Pose, actuator_parts, group_shape, transform_upper_frame_shape,
)

PIN_LENGTH = 40.0
HEAD_WASHER = 4.0
EYE_WIDTH = 20.0  # supplier nominal; delivered tolerance unknown
BALL_SIDE_WASHER = 1.5
BALL_WIDTH = 9.0
RING_SIDE_WASHER = 4.0
NOMINAL_SHIM = 1.0


def cylinder(radius, length, y):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(0, y, 0), cq.Vector(0, 1, 0))


def washer(y, thickness):
    return cylinder(5, thickness, y).cut(cylinder(3.1, thickness, y))


def corrected_local_hardware():
    original = local_review_geometry(load_inputs(), 1)
    start = -(HEAD_WASHER + EYE_WIDTH + BALL_SIDE_WASHER + BALL_WIDTH / 2)
    groove = start + PIN_LENGTH
    pin = cylinder(3, PIN_LENGTH, start).fuse(cylinder(2.5, .7, groove)).fuse(cylinder(3, 1.3, groove + .7))
    ring = cylinder(5.5, .6, groove).cut(cylinder(2.5, .6, groove))
    ring = ring.cut(cq.Workplane('XY').box(8, 1, 5.2).val().translate((4, groove + .3, 0)))
    return {
        'housing': original['housing'], 'ball': original['ball'],
        'pin': pin, 'pin_head': original['pin_head'],
        'head_washer': original['spacer'], 'ball_side_washer': original['shim'],
        'ring_side_washer': washer(BALL_WIDTH / 2, RING_SIDE_WASHER),
        'adjustment_shims': washer(BALL_WIDTH / 2 + RING_SIDE_WASHER, NOMINAL_SHIM),
        'e5_ring_envelope': ring,
    }


def stack_dimensions():
    fixed = HEAD_WASHER + EYE_WIDTH + BALL_SIDE_WASHER + BALL_WIDTH + RING_SIDE_WASHER
    return {
        'pin_length_mm': PIN_LENGTH, 'fixed_stack_mm': fixed,
        'eye_to_ball_offset_mm': EYE_WIDTH / 2 + BALL_SIDE_WASHER + BALL_WIDTH / 2,
        'unshimmed_gap_mm': PIN_LENGTH - fixed,
        'nominal_shim_mm': NOMINAL_SHIM,
        'nominal_final_gap_mm': PIN_LENGTH - fixed - NOMINAL_SHIM,
        'shim_adjustment_per_axis_mm': 4 * .5 + 3 * .1,
        'target_measured_gap_mm': [.2, .5],
        'eye_width_tolerance_verified': False, 'axial_ring_capacity_verified': False,
        'strength_improved_by_longer_pin': False,
    }


@lru_cache(maxsize=1)
def audit_corrected_pin():
    local = corrected_local_hardware()
    changed = ('pin', 'ring_side_washer', 'adjustment_shims', 'e5_ring_envelope')
    lower = cq.Compound.makeCompound([group_shape(n) for n in ('lower_frame', 'lower_brackets', 'lower_adapters')])
    rows = []
    for lift, pitch, roll in product((0., 25., 50.), (-3., 0., 3.), (-3., 0., 3.)):
        pose = Pose('corrected_pin', lift, pitch, roll)
        frame = transform_upper_frame_shape(group_shape('upper_frame'), pose)
        brackets = transform_upper_frame_shape(group_shape('upper_brackets'), pose)
        # Pin/eye contacts are intentional. Compare packing to actuator eye;
        # compare shaft only to frame/plates/housing (not its intended bore).
        measurements = []
        axes_actuators = {axis: cq.Compound.makeCompound([p.shape for p in actuator_parts(axis, pose)]) for axis in (1, 2, 3)}
        for axis in (1, 2, 3):
            housing = _place(local['housing'], axis, pose, True)
            plates = cq.Compound.makeCompound([placed_direct_mount_plate(a, pose) for a in (1, 2, 3)])
            for key in changed:
                shape = _place(local[key], axis, pose, False)
                obstacles = [('frame', frame), ('frame_brackets', brackets), ('plates', plates), ('lower', lower), ('housing', housing)]
                obstacles += [(f'actuator_{a}', axes_actuators[a]) for a in (1, 2, 3) if a != axis or key != 'pin']
                for label, obstacle in obstacles:
                    row = _intersection(shape, obstacle)
                    row.update(axis=axis, hardware=key, obstacle=label)
                    measurements.append(row)
        rows.append({'pose': [lift, pitch, roll], 'measurements': measurements})
    invalid = [m for r in rows for m in r['measurements'] if not m['valid']]
    overlaps = [dict(pose=r['pose'], **m) for r in rows for m in r['measurements'] if m['volume_mm3'] is not None and m['volume_mm3'] > 1e-6]
    return {'pose_count': len(rows), 'invalid_boolean_count': len(invalid),
            'unexpected_interference_count': len(overlaps), 'overlaps': overlaps,
            'stack': stack_dimensions(), 'continuous_sweep_verified': False,
            'pin_transition_and_ring_are_envelopes': True, 'poses': rows}


def export_review(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = audit_corrected_pin()
    (output_dir / 'pin_stack_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    local = corrected_local_hardware()
    cq.exporters.export(cq.Compound.makeCompound(list(local.values())), str(output_dir / 'UPPER_JOINT_HCDGH6_40_REVIEW.step'))
    from scripts.build_revf_direct_mount_review import _render, RenderPart, COLORS
    _render([RenderPart(k, v, COLORS['housing'] if k == 'housing' else (0.15, .40, .65) if 'washer' in k else (.3, .3, .3)) for k, v in local.items()],
            output_dir / 'pin_stack_review.png', '40 mm stock pin + ring-side packing',
            'Head / 4 / eye20 / 1.5 / ball9 / 4 / shims1 / gap0.5 / E-ring',
            (65, 75, 48), (0, -8, 8), 45)
    print(json.dumps({k: v for k, v in report.items() if k != 'poses'}, ensure_ascii=False))


if __name__ == '__main__':
    export_review(Path(__file__).resolve().parents[1] / 'outputs' / '20261007_bom_three_issue_correction')
