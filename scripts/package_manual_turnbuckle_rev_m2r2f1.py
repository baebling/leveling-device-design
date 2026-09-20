"""Validate and package only the final F1 artifacts, never failed draft outputs."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/manual_turnbuckle_rev_m2r2f1'
a=json.loads((OUT/'M2R2F1_AUDIT.json').read_text(encoding='utf-8'))
assert a['digital_geometry_pass'] and a['workspace']['all_locked_ranks_6']
for r in a['poses'].values():assert not r['interferences'] and not r['invalid']
for r in a['tools'].values():assert r['corridors']==84 and not r['interferences'] and len(r['installed_clamp_obstructions'])==12
for s in a['step']:
    assert s['valid'] and s['volume_delta_mm3']<.1
    assert hashlib.sha256((OUT/'step'/s['file']).read_bytes()).hexdigest()==s['sha256']
stack=json.loads((OUT/'FASTENING_STACK_AUDIT.json').read_text(encoding='utf-8'))
assert all(x['passes_nominal_geometry'] for x in stack['bolts'])
files=[OUT/n for n in ['README.md','M2R2F1_AUDIT.json','FASTENING_STACK_AUDIT.json','COMPONENT_REGISTER.json']]
files+=sorted((OUT/'step').glob('M2R2F1_*.step'))+sorted((OUT/'renders').glob('M2R2F1_*.png'))
files += [ROOT/p for p in ['cad/manual_turnbuckle_rev_m2.py','cad/manual_turnbuckle_rev_m2r1.py','cad/manual_turnbuckle_rev_m2r2f1.py','calculations/manual_turnbuckle_rev_m2_screen.py','calculations/manual_m2r2f1_fastening.py','scripts/build_manual_turnbuckle_rev_m2r1.py','scripts/build_manual_turnbuckle_rev_m2r2f1.py','scripts/package_manual_turnbuckle_rev_m2r2f1.py','design_basis/manual_m2r2f1_fastening_2026-09-05.md']]
target=ROOT/'output/Manual_3RPS_M2R2F1_Fastening_Review_2026-09-05.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for p in files:assert z.read(p.relative_to(ROOT).as_posix())==p.read_bytes()
digest=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
print(json.dumps({'artifact_checks':'PASS','files':len(files),'zip_bytes':target.stat().st_size,'sha256':digest},indent=2))
