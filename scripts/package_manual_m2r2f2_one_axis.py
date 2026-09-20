"""Check and package the M2R2F2 one-axis review artifacts."""
from pathlib import Path
import json, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/manual_m2r2f2_one_axis'
a=json.loads((OUT/'M2R2F2_ONE_AXIS_AUDIT.json').read_text(encoding='utf-8'))
assert a['digital_pass'] and not a['fabrication_release'] and not a['physical_fit_test']
for item in a['sets'].values():assert not item['invalid'] and not item['unexpected']
for item in a['step']:
    p=OUT/'step'/item['file'];assert item['valid'] and item['volume_delta_mm3']<.1
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
lower=[r['distance_mm'] for r in a['lower_contact_distances']]
upper=[r['distance_mm'] for r in a['upper_contact_distances']]
assert sum(abs(v-.1)<1e-6 for v in lower)==2 and max(v for v in lower if abs(v-.1)>=1e-6)<=.0021
assert max(upper)<=.0021
files=[OUT/'README.md',OUT/'M2R2F2_ONE_AXIS_AUDIT.json',OUT/'COMPONENT_REGISTER.json']
files+=sorted((OUT/'step').glob('*.step'))+sorted((OUT/'renders').glob('*.png'))
files += [ROOT/p for p in ['cad/manual_m2r2f2_one_axis.py','scripts/build_manual_m2r2f2_one_axis.py','scripts/package_manual_m2r2f2_one_axis.py','design_basis/manual_m2r2f2_one_axis_assembly_2026-09-05.md']]
target=ROOT/'output/Manual_3RPS_M2R2F2_One_Axis_Assembly_2026-09-05.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for p in files:assert z.read(p.relative_to(ROOT).as_posix())==p.read_bytes()
digest=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
print(json.dumps({'artifact_checks':'PASS','files':len(files),'zip_bytes':target.stat().st_size,'sha256':digest},indent=2))
