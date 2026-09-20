"""Validate delivered STEP files and package only review outputs and sources."""
from pathlib import Path
import sys, json, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cadquery as cq
from cad.manual_turnbuckle_rev_m2r1 import components_for_pose
OUT=ROOT/'outputs/manual_turnbuckle_rev_m2r1'
records=[]
for path in sorted((OUT/'step').glob('*.step')):
    imported=cq.importers.importStep(str(path)).val()
    valid=imported.isValid() and all(s.isValid() for s in imported.Solids())
    record={'file':path.name,'valid':valid,'solids':len(imported.Solids()),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    pose={'M2R1_NEUTRAL_REVIEW.step':(0,0),'M2R1_P3_R3_REVIEW.step':(3,3),
          'M2R1_PM3_RM3_REVIEW.step':(-3,-3)}.get(path.name)
    if pose is not None:
        expected=cq.Compound.makeCompound([c.shape for c in components_for_pose(*pose)])
        record['volume_delta_mm3']=abs(imported.Volume()-expected.Volume())
        record['bounds_max_delta_mm']=max(abs(getattr(imported.BoundingBox(),v)-getattr(expected.BoundingBox(),v))
             for v in ('xmin','xmax','ymin','ymax','zmin','zmax'))
        valid=valid and record['volume_delta_mm3']<0.1 and record['bounds_max_delta_mm']<1e-5
    record['pass']=valid
    records.append(record)
    print(path.name, valid, flush=True)
if not all(r['pass'] for r in records):
    raise SystemExit('STEP verification failed; do not package')
(OUT/'STEP_MANIFEST.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
audit=json.loads((OUT/'M2R1_CAD_AUDIT.json').read_text())
if not audit['digital_pass']:
    raise SystemExit('Pose audit failed; do not package')
package=ROOT/'output/Manual_3RPS_RevM2R1_CAD_Review_2026-09-05.zip'
paths=list((OUT/'step').glob('*.step'))+list((OUT/'renders').glob('*.png'))
paths+=list(OUT.glob('*.json'))+[OUT/'README.md']
for rel in ('cad/manual_turnbuckle_rev_m2r1.py','cad/manual_turnbuckle_rev_m2.py',
            'calculations/manual_turnbuckle_rev_m2_screen.py','scripts/build_manual_turnbuckle_rev_m2r1.py',
            'scripts/package_manual_turnbuckle_rev_m2r1.py',
            'requirements/current_turnbuckle_priority_2026-09-05.md'):
    paths.append(ROOT/rel)
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in paths:
        archive.write(path,path.relative_to(ROOT))
with zipfile.ZipFile(package) as archive:
    if archive.testzip() is not None:
        raise SystemExit('ZIP CRC failed')
digest=hashlib.sha256(package.read_bytes()).hexdigest()
package.with_suffix('.zip.sha256').write_text(digest+'  '+package.name+'\n',encoding='ascii')
print('PACKAGE',package.name,'FILES',len(paths),'BYTES',package.stat().st_size,'SHA256',digest)
