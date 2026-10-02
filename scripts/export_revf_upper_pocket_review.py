"""Generate review-only STEP, render, finite audit and SHA256 manifest."""
import sys
import json
import hashlib
import gzip
from dataclasses import asdict
from uuid import uuid4
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cadquery as cq
import vtk
from cad.revf_upper_pocket_inputs import load_inputs
from cad.revf_upper_pocket_pose_audit import audit_all, bounded_followup, refresh_worst_interference, refresh_invalid_boolean_counts, RELEASES
from cad.profile_radial_reve_actual_vendor import Pose
from cad.profile_radial_revf_upper_pocket_review import revf_components_for_pose, local_review_geometry, _basis
from math import atan2, degrees
from calculations.revf_upper_pocket_load_screen import build_review
from scripts.export_profile_radial_reve_actual_vendor import actor_for

OUTPUT=ROOT/'outputs/profile_radial_revF_upper_pocket_review_2026-10-02'
LABEL='REVIEW ONLY / NOT APPROVED FOR FABRICATION'
MEASUREMENT_SOURCES=(
    'references/vendor_cad/LM4075OE-1075-100mm.stp',
    'cad/revf_upper_pocket_inputs.py',
    'cad/profile_radial_revf_upper_pocket_review.py',
    'cad/profile_radial_reve_actual_vendor.py',
    'cad/revf_upper_pocket_pose_audit.py',
    'fusion_scripts/ProfileRadialRevD/revd_data.py',
    'calculations/reve_forward_kinematics.py',
    'calculations/revf_forward_kinematics.py',
    'calculations/revf_upper_pocket_load_screen.py',
    'references/revf_upper_pocket_source_register_2026-10-02.md',
    'calculations/reve_approved_workspace.py',
    'calculations/reve_command_jog_path_audit.py',
    'calculations/reve_home_path_audit.py',
    'scripts/render_lm4075oe_vendor_step.py',
    'scripts/export_revf_upper_pocket_review.py',
    *(f'outputs/profile_radial_revD_fusion_native/groups/{group}.step'
      for group in ('lower_frame','lower_brackets','lower_adapters','upper_frame','upper_brackets')),
)

def measurement_provenance(inputs, *, root=ROOT, sources=MEASUREMENT_SOURCES):
    """Identity of measurement inputs, not an exporter-time replacement label."""
    record=dict(schema=1,inputs=asdict(inputs),runtime=dict(python=sys.version,cadquery=cq.__version__),
        source_hashes={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in sources})
    canonical=json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False)
    return {**json.loads(canonical),'fingerprint':hashlib.sha256(canonical.encode()).hexdigest()}

def validate_reuse(audit, current):
    """Reject stale/legacy records before rewriting any existing artifact."""
    if audit.get('measurement_provenance') != current:
        raise ValueError('measurement provenance missing or mismatched; run a fresh audit')
    if not isinstance(audit.get('measurement_id'),str) or not audit['measurement_id']:
        raise ValueError('measurement identity missing; run a fresh audit')

def write_audit(audit, destination, chunk_size=5000):
    """Keep lossless JSON in deterministic gzip chunks with a plain-JSON index."""
    index=dict(audit);states=index.pop('path_states')
    index['path_state_files']=[];index['path_state_count']=len(states)
    for start in range(0,len(states),chunk_size):
        name=f'path_states_{start:06d}.json.gz'
        raw=(json.dumps(states[start:start+chunk_size],separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
        compressed=gzip.compress(raw,mtime=0)
        assert gzip.decompress(compressed)==raw
        (destination/name).write_bytes(compressed)
        # Only replace this writer's exact previous uncompressed chunk after
        # verifying lossless compression; no broad cleanup or unrelated files.
        old=destination/name.removesuffix('.gz')
        if old.exists(): old.unlink()
        index['path_state_files'].append(name)
    (destination/'audit.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')

def write_load_screen(destination):
    """Regenerate the saved screen from the same fingerprinted calculation."""
    (destination/'load_screen.json').write_text(json.dumps(build_review(),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def review_export_poses(audit):
    """Refresh derived global witness for fresh, continued and repackaged runs."""
    refresh_invalid_boolean_counts(audit)
    refresh_worst_interference(audit)
    poses=[Pose('neutral',25,0,0),Pose('raised',50,0,0)]
    for key in ('worst_interference','worst_articulation'):
        record=audit[key]
        if record:
            values=record['pose'] if key=='worst_interference' else record
            poses.append(Pose(key,values['lift_mm'],values['pitch_deg'],values['roll_deg']))
    return poses

def export_pose(pose, *, destination=OUTPUT, part_indices=None):
    parts=revf_components_for_pose(pose,load_inputs())
    if part_indices is not None: parts=[parts[i] for i in part_indices]
    assembly=cq.Assembly(name='REVF_REVIEW_ONLY')
    for part in parts: assembly.add(part.shape,name=part.name,color=cq.Color(*part.color))
    assembly.save(str(destination/f'{pose.label}.step'),exportType='STEP',mode='default')
    renderer=vtk.vtkRenderer();renderer.SetBackground(.94,.96,.98)
    focus=min(parts,key=lambda part:part.shape.Volume()) if part_indices is not None else None
    for part in parts:
        actor=actor_for(part)
        if focus is not None:
            actor.GetProperty().SetOpacity(1.0 if part is focus else .3)
            if part is focus: actor.GetProperty().SetColor(.85,.16,.05)
        renderer.AddActor(actor)
    camera=renderer.GetActiveCamera(); camera.SetPosition(1050,-1250,850);camera.SetFocalPoint(0,0,175);camera.SetViewUp(0,0,1)
    camera.ParallelProjectionOn();camera.SetParallelScale(470);renderer.ResetCameraClippingRange()
    if focus is not None:
        centre=focus.shape.Center();camera.SetFocalPoint(centre.x,centre.y,centre.z)
        camera.SetPosition(centre.x+140,centre.y-170,centre.z+110);camera.SetParallelScale(60);renderer.ResetCameraClippingRange()
    title=vtk.vtkTextActor();title.SetInput(f'{LABEL}\nRev F {pose.label}: Z={pose.lift_mm:.2f} pitch={pose.pitch_deg:.2f} roll={pose.roll_deg:.2f}')
    title.SetPosition(20,740);title.GetTextProperty().SetFontSize(20);title.GetTextProperty().SetColor(.65,.08,.06);renderer.AddActor2D(title)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(True);window.SetSize(1300,820);window.AddRenderer(renderer);window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(destination/f'{pose.label}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()

def export_bracket_parts(inputs, destination, provenance):
    """Local single-part quotation review candidates; verify STEP round trip."""
    def bounds(shape):
        b=shape.BoundingBox()
        return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]
    records=[]
    for axis in (1,2,3):
        shape=local_review_geometry(inputs,axis)['bracket']
        path=destination/f'A{axis}_bracket_local_REVIEW_ONLY.stp'
        assert shape.isValid() and len(shape.Solids())==1
        cq.exporters.export(shape,str(path),exportType='STEP')
        restored=cq.importers.importStep(str(path)).val()
        assert restored.isValid() and len(restored.Solids())==1
        assert path.stat().st_size<10_000_000
        assert abs(restored.Volume()-shape.Volume())<1e-4
        assert all(abs(a-b)<1e-5 for a,b in zip(bounds(shape),bounds(restored)))
        records.append(dict(axis=axis,path=path.name,label=LABEL,review_only=True,solid_count=1,
            bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            coordinate_system='local PHS ball origin; X radial, Y tangent/pin, Z platform up; mm',
            mount_pad_rotation_about_local_z_deg=degrees(atan2(_basis(axis)[0][1],_basis(axis)[0][0])),
            source_volume_mm3=shape.Volume(),reimport_volume_mm3=restored.Volume(),
            source_bbox_mm=bounds(shape),reimport_bbox_mm=bounds(restored),
            geometry_sha256=provenance['source_hashes']['cad/profile_radial_revf_upper_pocket_review.py'],
            measurement_fingerprint=provenance['fingerprint'],**RELEASES))
    return records


def main():
    inputs=load_inputs();provenance=measurement_provenance(inputs)
    if '--repackage-existing' in sys.argv or '--continue-followup' in sys.argv:
        audit=json.loads((OUTPUT/'audit.json').read_text(encoding='utf-8'))
        validate_reuse(audit,provenance)
    else:
        audit=audit_all(inputs)
        audit['measurement_provenance']=provenance
        audit['measurement_id']=str(uuid4())
    # Also detect geometry/input changes while a long audit was running.
    validate_reuse(audit,measurement_provenance(inputs))
    OUTPUT.mkdir(parents=True,exist_ok=True)
    if 'path_states' not in audit:
        audit['path_states']=[row for name in audit['path_state_files'] for row in json.loads(gzip.decompress((OUTPUT/name).read_bytes()) if name.endswith('.gz') else (OUTPUT/name).read_bytes())]
    if '--continue-followup' in sys.argv:
        audit['exact_followup']=bounded_followup(audit,inputs,previous=audit['exact_followup'])
        validate_reuse(audit,measurement_provenance(inputs))
    poses=review_export_poses(audit)
    bracket_parts=export_bracket_parts(inputs,OUTPUT,provenance)
    write_load_screen(OUTPUT)
    audit['bracket_part_exports']=bracket_parts
    write_audit(audit,OUTPUT)
    for pose in poses: export_pose(pose)
    witness=audit['worst_interference']
    if witness:
        p=witness['pose']
        export_pose(Pose('worst_interference_pair',p['lift_mm'],p['pitch_deg'],p['roll_deg']),part_indices=witness['pair_indices'])
    readme=f'''# {LABEL}

Three upper pocket candidates. All release flags FALSE. Finite sampled review only.

Pin/eye clearance is reported per separate nominal eye source, not as delivered-eye tolerance: HCDGH diameter5.988–5.996 gives conditional0.004–0.012 for STEP eye6.0 and0.404–0.412 for sales eye6.4. Delivered eye tolerance and fit remain UNKNOWN. The former dmin-only clearance-bounds key is replaced by per-source lower/upper records in load_screen.json.

Task 9/10 hardware baseline: TRUSCO PHS6 OD20 x 6.75, ball width9, conservative neck diameter11 and foot diameter13 x5, blind M6 depth12. The opened +localY channel preserves ball freedom. The all-azimuth nipple keepout (radius9, local Z10..25) is an assumed screening envelope, NOT a supplier-verified bound; a clear sample cannot establish actual nipple clearance. Candidate M6x12 socket head diameter10 x6 gives nominal9 engagement, length-only8.65..9.35, nominal3 bottom clearance and ZERO nominal head/recess flush margin. Exact SKU, tolerances, preload, locking and strength remain UNKNOWN/HOLD; install the retainer before mounting to the profile, which blocks later head access.

Pin candidate HCDGH6-35 uses the head-under stack WSSB10-6-4 washer4 -> eye20 -> one WSSB10-6-1.5 washer1.5 -> ball9 =34.5, then nominal0.5 groove gap and E5 ring. The ball-side OD10 washer replaces three OD12 CIMR shims while preserving e16 and centres; legacy geometry key shim now denotes this one stock washer. Known tolerance gap0.20–0.82 excludes unknown eye width and relief; no assembly fit approval. HCDGH head diameter9 x1.5, groove diameter5(+0.075/0), width0.7(+0.1/0), end allowance2. Simplified ring C-contour and radial tool envelope are NOT verified E5 installation geometry. Pin/ring intended interface is separated from unintended interference checks but remains unverified. Ring capacity, groove/relief stress, supplier eye tolerance and delivered strength remain UNKNOWN/HOLD. S45C hardness is not converted to guaranteed yield. The regenerated load_screen.json uses minimum pin5.988, not historical MSB5.95 or a class10.9 proof assumption.

Coverage exclusion: pin_transition_unknown_keepout is diagnostic local geometry only, NOT exported or included in pose/assembly collision lists. Its status is explicitly EXCLUDED/UNKNOWN in assembly hardware_review, not geometrically cleared. Actual head relief, groove transition contact and strength need supplier evidence. Assumed nipple-envelope intersections are potential obstructions, not confirmed actual nipple penetration. Conservative nominal neck/washer interference is distinct from retained shallow-slot-model mismatch; it is never blanket-exempted as intentional contact.

27 representatives use exact B-rep Booleans after conservative broad phase. 1859 grid poses and all recorded command/HOME samples use transformed enclosing AABBs. Remaining near-contact pairs are UNKNOWN/HOLD; this is an incomplete clearance audit, not a continuous workspace proof. audit.json indexes deterministic gzip-compressed path_states_*.json.gz files; decompress to UTF-8 JSON arrays.

Recorded counts: {sum(r['exact_pair_count'] for r in audit['representatives'])} representative exact pair checks, {sum(r['interference_count'] for r in audit['representatives'])} representative valid positive nominal intersections. Invalid Boolean counts: pose {audit['pose_invalid_boolean_count']} (including supplemental exact), assembly {audit['assembly_invalid_boolean_count']}, combined {audit['combined_invalid_boolean_count']}. These count attempts across scopes, not unique physical contacts. Assembly stages already aggregate child paths and are counted once. Legacy invalid_boolean_count remains a pose-only alias, not the combined total. {len(audit['path_states'])} unique command states, {len(audit['command_segments'])} command segments / {sum(len(s['samples']) for s in audit['command_segments'])} sampled state occurrences, {len(audit['home'])} HOME states. Unknown near-pair occurrences: {audit['unknown_pair_count']}. All failure/unknown records are retained; no representative is released.

Supplemental bounded exact follow-up: {len(audit['exact_followup']['completed'])} distinct state/pair checks completed; {audit['exact_followup']['backlog_distinct_keys']} distinct keys remain uncomputed. Invalid completed results remain unresolved separately. The original broad occurrence count above is retained for traceability; exact_followup is the authoritative supplemental ledger. Scope queues prioritize representative-uncovered pairs and worst articulation/switch-margin states. All remainder stays UNKNOWN/HOLD.

worst_interference is recomputed from all valid representative and supplemental exact measurements after every batch and before packaging. Its full-pose STEP/render and separate worst_interference_pair STEP/render follow that same witness; the pair view shows the smaller part in orange and the larger part translucent for inspection. Invalid Booleans never select a worst-volume witness.

Measurement ID: {audit['measurement_id']}. Source fingerprint: {audit['measurement_provenance']['fingerprint']}. Cached reuse requires identical measured inputs, STEP/frame sources, geometry, closure/policy/audit source hashes and runtime; missing or changed provenance is rejected before output writes. Repackaging preserves this original identity.

Run the exporter with --continue-followup to execute the next bounded 24 distinct near-pair keys under the same validated measurement identity. --repackage-existing only repackages; it never silently substitutes fresh source hashes for old measurements.

Mount status: {audit['mount_attachment_status']}; centering {audit['crossmember_centering_status']}. Measurements and per-bolt findings are in audit.json. Empty-space clearance alone is not attachment. Corrected pads follow platform X. Retained shallow slot depth 6.9 mm versus 7.5 mm insertion creates 0.6 mm nominal floor overlap, not proof of delivered DNF3030 interference. Historical Daeyoung DY5155 nominal floor 10.5 mm differs from the DYC section nominal floor 11.1 mm (2.5+8.6); neither establishes current NAVIMRO delivery, whose page image says DNP3030. See the source register for separate identities. Actual section, tolerance and strength remain UNKNOWN/HOLD. Current BOM PHS6 is TRUSCO 280-7599, not historical THK; delivered capacity/tolerances remain unverified. Combined pose-plus-assembly invalid Boolean count: {audit['combined_invalid_boolean_count']}; invalid pin-head/eye results leave seating unresolved (not proven physical penetration). Open housing insertion requires unverified M6 retainer engagement/preload/locking for axial capture. Staged three-axis frame/T-nut/tool context is now included; finite nominal checks do not prove complete assembly.

Three local bracket-only quotation-review candidates (not purchase/fabrication authorization) are listed below. Each reimport is one valid solid, under 10 MB, with volume/bounds checked. Local origin is PHS ball, X radial, Y tangent/pin, Z platform up, units mm. Full assembly STEP files (~11 MB) are NOT meviy upload candidates. No upload has been performed.

{chr(10).join(f"- {r['path']}: {r['bytes']} bytes; local pad Z rotation {r['mount_pad_rotation_about_local_z_deg']:.6f} deg; geometry SHA256 {r['geometry_sha256']}; STEP SHA256 {r['sha256']}; {LABEL}." for r in bracket_parts)}

Command policy: grid-to-PARK and adjacent JOG are pose interpolations whose IK lengths use the corrected CAD world-fixed tangent eye offset, not legacy FK. HOME uses the Rev F six-equation length/hinge solver and rechecks every solution against CAD lengths (1e-7 mm) and hinge closure. It starts at PARK, retracting order 3,2,1. Normal length window is 210-280 mm; intentional HOME may go to nominal 205 mm STEP collapsed length, NOT a verified physical switch trip. Per-row normal-window and HOME-window results are separate. Nonconvergence or FK/CAD disagreement stays UNKNOWN/HOLD without geometry clearance. Arbitrary HOME starts/restart/escape remain HOLD. Manufacturer capacities, tolerances, pin transitions and complete wrench/assembly paths remain unresolved. Nominal assembly sample-clear flags do not establish valid Boolean or assembly success. No cart, payload or people validation.

Review loads +/-750 N per axis, conditional static target 1.5; see Task 2 load screen. Independent physical stops omitted by user-approved deviation; electrical limits are separate. No fabrication exports or purchase authorization.

Production HOME additionally reconstructs the CAD X/Y/yaw branch: X/Y residuals are mm; wrapped yaw radians are multiplied by support radius250 mm, then all three length-equivalent residuals must be finite and <=1e-7 mm. Each HOME row records residuals, radius and threshold; divergence remains UNKNOWN/HOLD and cannot advance the continuation seed. Provenance now includes the load calculation (20 source files); all 30 artifact hashes include the regenerated load screen.
'''
    (OUTPUT/'README.md').write_text(readme,encoding='utf-8')
    files=sorted(p for p in OUTPUT.iterdir() if p.is_file() and p.name!='manifest.json')
    manifest={'review_only':True,**RELEASES,'bracket_part_exports':bracket_parts,'artifacts':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    manifest['measurement_id']=audit['measurement_id']
    manifest['measurement_provenance']=audit['measurement_provenance']
    manifest['source_artifacts']=[{'path':name,'sha256':digest} for name,digest in audit['measurement_provenance']['source_hashes'].items()]
    (OUTPUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'representatives':27,'dense':1859,'path_states':len(audit['path_states']),'status':'HOLD'}))

if __name__=='__main__': main()
