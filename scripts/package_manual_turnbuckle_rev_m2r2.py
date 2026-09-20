"""Package and independently check written artifacts without loading CAD runtime."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/manual_turnbuckle_rev_m2r2'
a=json.loads((OUT/'M2R2_AUDIT.json').read_text(encoding='utf-8'))
assert a['digital_geometry_pass'] and a['workspace']['all_locked_ranks_6']
for entry in a['step']:
    p=OUT/'step'/entry['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
    assert entry['valid'] and entry['volume_delta_mm3']<.1
for report in a['poses'].values():
    assert not report['interferences'] and not report['invalid']
files=sorted(p for p in OUT.rglob('*') if p.is_file())
files += [ROOT/p for p in ['cad/manual_turnbuckle_rev_m2.py','cad/manual_turnbuckle_rev_m2r1.py','cad/manual_turnbuckle_rev_m2r2.py','calculations/manual_turnbuckle_rev_m2_screen.py','scripts/build_manual_turnbuckle_rev_m2r1.py','scripts/build_manual_turnbuckle_rev_m2r2.py','scripts/package_manual_turnbuckle_rev_m2r2.py','design_basis/manual_revm2r2_stock_connections_2026-09-05.md']]
target=ROOT/'output/Manual_3RPS_M2R2_Stock_Connections_2026-09-05.zip'
target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for p in files:assert z.read(p.relative_to(ROOT).as_posix())==p.read_bytes()
digest=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
print(json.dumps({'written_artifact_checks':'PASS','files':len(files),'zip_bytes':target.stat().st_size,'sha256':digest},indent=2))
