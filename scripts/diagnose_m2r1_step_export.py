from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq
from cad.manual_turnbuckle_rev_m2r1 import components_for_pose
out = Path('outputs/manual_turnbuckle_rev_m2r1/export_diagnostics')
out.mkdir(exist_ok=True)
s = next(c for c in components_for_pose() if c.name == 'LEG_1_STB_M12_LINK').shape.Solids()[-1]
print('source', s.Volume(), s.isValid(), flush=True)
for mode in [0, 1, 2]:
    q = s if mode != 2 else s.toNURBS()
    p = out / f'check_{mode}.step'
    q.exportStep(str(p), write_pcurves=(mode != 1))
    z = cq.importers.importStep(str(p)).val()
    print(mode, q.Volume(), z.Volume(), z.isValid(), flush=True)
