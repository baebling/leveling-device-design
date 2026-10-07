"""Read generated STEP solids independently of the producing functions."""
import json
from math import pi
from pathlib import Path
import xml.etree.ElementTree as ET
import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def validate():
    records = []
    for name, frame_hole_radius in [
        ('HWT905_UPPER_PVC_100x100x5_PLASTIC_DRILL_ONLY.step', 3.3),
        ('HWT905_LOWER_PVC_100x100x5_PLASTIC_DRILL_ONLY.step', 4.5),
    ]:
        shape = cq.importers.importStep(str(HERE / name)).val()
        assert shape.isValid() and len(shape.Solids()) == 1
        box = shape.BoundingBox()
        assert all(abs(a-b)<1e-6 for a,b in zip((box.xlen,box.ylen,box.zlen),(100,100,5)))
        expected = 100*100*5 - pi*5*(3*2.1**2+2*frame_hole_radius**2)
        assert abs(shape.Volume()-expected)<1e-3, f'Wrong hole volumes: {name}'
        records.append({'file':name,'valid':True,'solids':1,'dimensions_mm':[box.xlen,box.ylen,box.zlen], 'volume_mm3':shape.Volume()})
    for name in ('UPPER_JOINT_HCDGH6_40_REVIEW.step','HWT905_MOUNT_REVIEW.step'):
        shape = cq.importers.importStep(str(HERE / name)).val()
        assert shape.isValid()
        records.append({'file':name,'valid':True,'solids':len(shape.Solids())})
    for file in (HERE/'HWT905_플라스틱판_타공조립.svg',ROOT/'electrical/RevF_wiring_overview.svg'):
        ET.parse(file)
    report = {'step_reimport_count':len(records), 'failed':0,'steps':records,'svg_xml_valid':True,
              'plastic_plate_analytic_volume_check':True,'manufacturing_strength_verification':False}
    (HERE/'exported_parts_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    validate()
