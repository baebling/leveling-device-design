"""HWT905 stock PVC mount: only plastic drilling; no new metal machining."""
from itertools import product
import json
from pathlib import Path
import cadquery as cq
from cad.profile_radial_reve_actual_vendor import Pose, actuator_parts, group_shape, transform_upper_frame_shape
from cad.revf_direct_phs6_mount import _intersection, placed_direct_mount_plate

SENSOR_HOLES = [(-23.95, 0), (23.95, -14.35), (23.95, 14.35)]
FRAME_HOLES = [(-40, -35), (40, -35)]
CENTER = (0, -295)


def mount(frame_top, frame_bolt_diameter=6):
    plate_bottom = frame_top + 10
    plate = cq.Workplane('XY').box(100, 100, 5).val().translate((*CENTER, plate_bottom + 2.5))
    for (x, y), radius in [(h, 2.1) for h in SENSOR_HOLES] + [(h, 3.3 if frame_bolt_diameter == 6 else 4.5) for h in FRAME_HOLES]:
        plate = plate.cut(cq.Solid.makeCylinder(radius, 5, cq.Vector(x, CENTER[1] + y, plate_bottom)))
    sensor = cq.Workplane('XY').box(55, 36.8, 24).val().translate((*CENTER, plate_bottom + 5 + 12))
    spacers = []
    for x, y in FRAME_HOLES:
        for dz in (0, 5):
            spacer = cq.Solid.makeCylinder(5 if frame_bolt_diameter == 6 else 6, 5, cq.Vector(x, CENTER[1] + y, frame_top + dz))
            spacer = spacer.cut(cq.Solid.makeCylinder(frame_bolt_diameter / 2 + .1, 5, cq.Vector(x, CENTER[1] + y, frame_top + dz)))
            spacers.append(spacer)
    return plate, sensor, spacers


def export_review():
    out = Path(__file__).resolve().parents[1] / 'outputs' / '20261007_bom_three_issue_correction'
    upper = cq.Compound.makeCompound([*mount(300)[:2], *mount(300)[2]])
    lower = cq.Compound.makeCompound([*mount(40, 8)[:2], *mount(40, 8)[2]])
    rows = []
    for z, pitch, roll in product((0., 25., 50.), (-3., 0., 3.), (-3., 0., 3.)):
        pose = Pose('sensor_mount', z, pitch, roll)
        upper_now = transform_upper_frame_shape(upper, pose)
        actuators = cq.Compound.makeCompound([p.shape for a in (1, 2, 3) for p in actuator_parts(a, pose)])
        upper_obstacles = cq.Compound.makeCompound([
            group_shape('lower_frame'), group_shape('lower_brackets'), group_shape('lower_adapters'),
            transform_upper_frame_shape(group_shape('upper_frame'), pose),
            *[placed_direct_mount_plate(a, pose) for a in (1, 2, 3)], actuators])
        lower_obstacles = cq.Compound.makeCompound([
            group_shape('lower_frame'), group_shape('lower_brackets'), group_shape('lower_adapters'),
            transform_upper_frame_shape(group_shape('upper_frame'), pose), actuators])
        for label, shape, obstacle in [('upper', upper_now, upper_obstacles), ('lower', lower, lower_obstacles), ('between', upper_now, lower)]:
            measurement = _intersection(shape, obstacle)
            rows.append(dict(pose=[z, pitch, roll], mount=label, **measurement))
    report = {
        'pose_count': 27, 'invalid_boolean_count': sum(not m['valid'] for m in rows),
        'unexpected_interference_count': sum(m['volume_mm3'] is not None and m['volume_mm3'] > 1e-6 for m in rows),
        'plate_quantity': 2, 'plate_size_mm': [100, 100, 5], 'plate_holes_per_plate': 5,
        'sensor_holes_mm': SENSOR_HOLES, 'frame_holes_mm': FRAME_HOLES,
        'm4_sensor_fasteners': 6, 'm6_profile_fasteners': 2, 'm8_profile_fasteners': 2, 'spacer_5mm_quantity': 8,
        'new_metal_machining_operations': 0, 'plastic_drilling_operations': 10,
        'm6_nominal_thread_entry_mm': 25 - 5 - 10 - 1.5 - 2.5,
        'sensor_shape_is_datasheet_envelope': True, 'moving_cable_sweep_verified': False,
        'measurements': rows,
    }
    (out / 'sensor_mount_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    p, s, spacers = mount(0)
    cq.exporters.export(p, str(out / 'HWT905_UPPER_PVC_100x100x5_PLASTIC_DRILL_ONLY.step'))
    cq.exporters.export(mount(0, 8)[0], str(out / 'HWT905_LOWER_PVC_100x100x5_PLASTIC_DRILL_ONLY.step'))
    cq.exporters.export(cq.Compound.makeCompound([p, s, *spacers]), str(out / 'HWT905_MOUNT_REVIEW.step'))
    from scripts.build_revf_direct_mount_review import _render, RenderPart
    _render([RenderPart('PVC plate', p, (.6, .8, .85)), RenderPart('HWT905 envelope', s, (.20, .3, .38)),
             *[RenderPart('2 x 5mm stock spacers', part, (.55, .55, .55)) for part in spacers]],
            out / 'sensor_mount_review.png', 'HWT905 bolt-on PVC mount (x2)',
            '100 x 100 x 5 PVC / M4 x 25 (x3) / M6 x 25 (x2) / 10mm spacers',
            (160, -465, 170), (0, -295, 15), 100)
    print(json.dumps({k: v for k, v in report.items() if k != 'measurements'}, ensure_ascii=False))


if __name__ == '__main__':
    export_review()
