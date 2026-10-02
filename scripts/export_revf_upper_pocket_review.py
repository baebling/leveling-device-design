"""Generate review-only STEP, render, finite audit and SHA256 manifest."""
import sys
import json
import hashlib
import gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cadquery as cq
import vtk
from cad.revf_upper_pocket_inputs import load_inputs
from cad.revf_upper_pocket_pose_audit import audit_all, mount_attachment_review
from cad.profile_radial_reve_actual_vendor import Pose
from cad.profile_radial_revf_upper_pocket_review import revf_components_for_pose
from scripts.export_profile_radial_reve_actual_vendor import actor_for

OUTPUT=ROOT/'outputs/profile_radial_revF_upper_pocket_review_2026-10-02'
LABEL='REVIEW ONLY / NOT APPROVED FOR FABRICATION'

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

def export_pose(pose):
    parts=revf_components_for_pose(pose,load_inputs())
    assembly=cq.Assembly(name='REVF_REVIEW_ONLY')
    for part in parts: assembly.add(part.shape,name=part.name,color=cq.Color(*part.color))
    assembly.save(str(OUTPUT/f'{pose.label}.step'),exportType='STEP',mode='default')
    renderer=vtk.vtkRenderer();renderer.SetBackground(.94,.96,.98)
    for part in parts: renderer.AddActor(actor_for(part))
    camera=renderer.GetActiveCamera(); camera.SetPosition(1050,-1250,850);camera.SetFocalPoint(0,0,175);camera.SetViewUp(0,0,1)
    camera.ParallelProjectionOn();camera.SetParallelScale(470);renderer.ResetCameraClippingRange()
    title=vtk.vtkTextActor();title.SetInput(f'{LABEL}\nRev F {pose.label}: Z={pose.lift_mm:.2f} pitch={pose.pitch_deg:.2f} roll={pose.roll_deg:.2f}')
    title.SetPosition(20,740);title.GetTextProperty().SetFontSize(20);title.GetTextProperty().SetColor(.65,.08,.06);renderer.AddActor2D(title)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(True);window.SetSize(1300,820);window.AddRenderer(renderer);window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUTPUT/f'{pose.label}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()

def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    # Repackage only a locally generated complete monolithic audit; no geometry
    # result is changed. Useful when an older run finished during packaging edits.
    audit=json.loads((OUTPUT/'audit.json').read_text(encoding='utf-8')) if '--repackage-existing' in sys.argv else audit_all(load_inputs())
    if 'path_states' not in audit:
        audit['path_states']=[row for name in audit['path_state_files'] for row in json.loads(gzip.decompress((OUTPUT/name).read_bytes()) if name.endswith('.gz') else (OUTPUT/name).read_bytes())]
    audit.update(mount_attachment_review(load_inputs()))
    write_audit(audit,OUTPUT)
    poses=[Pose('neutral',25,0,0),Pose('raised',50,0,0)]
    for key in ('worst_interference','worst_articulation'):
        record=audit[key]
        if record:
            values=record['pose'] if key=='worst_interference' else record
            poses.append(Pose(key,values['lift_mm'],values['pitch_deg'],values['roll_deg']))
    for pose in poses: export_pose(pose)
    readme=f'''# {LABEL}

Three upper pocket candidates. All release flags FALSE. Finite sampled review only.

27 representatives use exact B-rep Booleans after conservative broad phase. 1859 grid poses and all recorded command/HOME samples use transformed enclosing AABBs. Remaining near-contact pairs are UNKNOWN/HOLD; this is an incomplete clearance audit, not a continuous workspace proof. audit.json indexes deterministic gzip-compressed path_states_*.json.gz files; decompress to UTF-8 JSON arrays.

Recorded counts: {sum(r['exact_pair_count'] for r in audit['representatives'])} exact pair checks, {sum(r['interference_count'] for r in audit['representatives'])} valid positive nominal intersections, {audit['invalid_boolean_count']} invalid Booleans, {len(audit['path_states'])} unique command states, {len(audit['command_segments'])} command segments / {sum(len(s['samples']) for s in audit['command_segments'])} sampled state occurrences, {len(audit['home'])} HOME states. Unknown near-pair occurrences: {audit['unknown_pair_count']}. All failure/unknown records are retained; no representative is released.

Mount status: {audit['mount_attachment_status']}. Measurements and per-bolt findings are in audit.json. Empty-space clearance alone is not attachment. Actual DNF3030 slot fit remains unverified. Representative invalid Boolean count: {audit['invalid_boolean_count']}; invalid pin-head/eye results leave seating unresolved (not proven physical penetration). Open housing insertion requires unverified M6 retainer engagement/preload/locking for axial capture. Task 3 profile_attachment omits installed frame/T-nut/full tool context.

Command policy: grid-to-PARK and adjacent JOG; HOME starts at PARK, retracting order 3,2,1. Arbitrary HOME starts/restart/escape remain HOLD. Manufacturer capacities, tolerances, pin transitions and complete wrench/assembly paths remain unresolved. Nominal assembly sample-clear flags do not establish valid Boolean or assembly success. No cart, payload or people validation.

Review loads +/-750 N per axis, conditional static target 1.5; see Task 2 load screen. Independent physical stops omitted by user-approved deviation; electrical limits are separate. No fabrication exports or purchase authorization.
'''
    (OUTPUT/'README.md').write_text(readme,encoding='utf-8')
    files=sorted(p for p in OUTPUT.iterdir() if p.is_file() and p.name!='manifest.json')
    manifest={'review_only':True,'purchase_release':False,'fabrication_release':False,'artifacts':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    sources=['cad/revf_upper_pocket_inputs.py','cad/profile_radial_revf_upper_pocket_review.py','cad/revf_upper_pocket_pose_audit.py','cad/profile_radial_reve_actual_vendor.py','references/vendor_cad/LM4075OE-1075-100mm.stp']
    manifest['source_artifacts']=[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in sources]
    (OUTPUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'representatives':27,'dense':1859,'path_states':len(audit['path_states']),'status':'HOLD'}))

if __name__=='__main__': main()
