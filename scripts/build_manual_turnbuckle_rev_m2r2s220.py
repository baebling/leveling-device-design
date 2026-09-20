"""Build and verify the approved M2R2-S220 cart-BOM CAD."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cadquery as cq
import vtk
from itertools import combinations
from cad import manual_turnbuckle_rev_m2r2s220 as m
from scripts.build_manual_turnbuckle_rev_m2r1 import actor,bbox_overlap
OUT=ROOT/'outputs/manual_turnbuckle_rev_m2r2s220'

def render(parts,name,direction=(1,-1.4,.85),subtitle=''):
    ren=vtk.vtkRenderer();ren.SetBackground(.94,.96,.98)
    for c in parts:ren.AddActor(actor(c))
    camera=ren.GetActiveCamera();camera.SetPosition(*direction);camera.SetFocalPoint(0,0,0);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();ren.ResetCamera()
    for text,y,size,col in [('MANUAL 3-RPS / M2R2-S220 CART-BOM CAD',850,25,(.06,.12,.18)),(subtitle,817,17,(.15,.22,.3)),('PRELIMINARY PoC - NOT APPROVED FOR FABRICATION',22,17,(.7,.13,.08))]:
        label=vtk.vtkTextActor();label.SetInput(text);label.SetPosition(25,y);label.GetTextProperty().SetFontSize(size);label.GetTextProperty().SetFontFamilyToCourier();label.GetTextProperty().SetColor(*col);ren.AddViewProp(label)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.SetSize(1500,900);win.AddRenderer(ren);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'renders'/f'{name}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();win.Finalize()

def audit(parts):
    boxes={c.name:c.shape.BoundingBox() for c in parts};hits=[];count=0
    for a,b in combinations(parts,2):
        if not bbox_overlap(boxes[a.name],boxes[b.name]):continue
        count+=1;vol=a.shape.intersect(b.shape).Volume()
        if vol>.01:hits.append({'a':a.name,'b':b.name,'volume_mm3':vol})
    return {'components':len(parts),'tested_pairs':count,'invalid':[c.name for c in parts if not c.shape.isValid()],'interferences':hits}

def export(parts,name):
    target=OUT/'step'/f'{name}.step';assembly=cq.Assembly(name='M2R2S220_PRELIMINARY_POC')
    for c in parts:assembly.add(c.shape,name=c.name,color=cq.Color(*c.color))
    assembly.export(str(target));read=cq.importers.importStep(str(target)).val()
    expected=cq.Compound.makeCompound([c.shape for c in parts])
    return {'file':target.name,'valid':read.isValid() and all(s.isValid() for s in read.Solids()),'volume_delta_mm3':abs(read.Volume()-expected.Volume()),'solids':len(read.Solids()),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}

def tools_audit(parts,p,r):
    paths=m.tool_paths(p,r);boxes={c.name:c.shape.BoundingBox() for c in parts};hits=[];sequence=[]
    for tool in paths:
        box=tool.shape.BoundingBox()
        for c in parts:
            if not bbox_overlap(box,boxes[c.name]):continue
            v=tool.shape.intersect(c.shape).Volume()
            if v>.01:
                row={'tool':tool.name,'obstacle':c.name,'volume_mm3':v}
                tokens=tool.name.split('_')
                own_clamp=(tokens[0]+'_SHAT_CLAMP_HEAD_'+('L' if tokens[1]=='-1' else 'R')) if len(tokens)>2 and tokens[2]=='M5' else None
                if c.name==own_clamp:sequence.append(row)
                else:hits.append(row)
    return {'corridors':len(paths),'interferences':hits,'installed_clamp_obstructions':sequence,'required_sequence':'Remove each supplied M4 clamp screw before tightening M5 mounting bolts; reinstall and torque M4 afterward, unloaded/supported only','scope':'60mm straight insertion M5/M8 mounting screws, 50mm SHAT M4; collar screw and wrench handle sweep excluded'}

def main():
    for folder in [OUT,OUT/'renders',OUT/'step']:folder.mkdir(parents=True,exist_ok=True)
    report={'revision':'M2R2-S220','concept_approved':True,'fabrication_release':False,'purchase_release':False,'catalogue_interfaces':m.catalogue_interfaces(),'workspace':m.workspace(),'poses':{},'tools':{},'step':[],'limitations':['profile taper and tnut underside simplified; stock matched-series compatibility checked from catalogue','SCSJ12-6 clamp screw and wrench handle sweep not modeled','thread helices/envelopes simplified inside each compound link','independent mechanical stops, actual cart receiver and base fixture remain unresolved','STB-M12 compression and SHAT12/SCSJ12 holding ratings not established']}
    for p,r in [(0,0),(-3,-3),(-3,3),(3,-3),(3,3),(3,0),(-3,0),(0,3),(0,-3)]:
        name=f'P{p:+}_R{r:+}';parts=m.components_for_pose(p,r);a=audit(parts);report['poses'][name]=a
        print(name,'interferences',len(a['interferences']),'invalid',a['invalid'],flush=True)
        if a['interferences']:print(json.dumps(a['interferences']),flush=True)
        if (p,r) in [(0,0),(3,3),(-3,-3)]:
            ta=tools_audit(parts,p,r);report['tools'][name]=ta;print('TOOL_CORRIDORS',len(ta['interferences']),flush=True)
            if ta['interferences']:print(json.dumps(ta['interferences']),flush=True)
        if (p,r) in [(0,0),(3,3)]:
            tag='M2R2S220_NEUTRAL' if p==0 else 'M2R2S220_P3_R3';report['step'].append(export(parts,tag));render(parts,tag,subtitle=f'700 x 700 mm | neutral height 299.2 mm | pitch {p:+} / roll {r:+} deg')
        if p==r==0:
            render([c for c in parts if not c.group.startswith('UPPER_')],'M2R2S220_EXPOSED',subtitle='Upper frame hidden to show three stock-component links')
            view=[c for c in parts if c.name.startswith(('L1_','U1_','A1_'))]
            render(view,'M2R2S220_LINK_DETAIL',(1,-.3,.5),'One link: SHAT12 / SFU12 / MISUMI shims / SCSJ12-6 / turnbuckle')
            report['step'].append(export(view,'M2R2S220_SINGLE_LINK'))
            (OUT/'COMPONENT_REGISTER.json').write_text(json.dumps([{'name':c.name,'group':c.group,'basis':c.material} for c in parts],indent=2),encoding='utf-8')
    report['digital_geometry_pass']=report['workspace']['passes'] and all(not a['invalid'] and not a['interferences'] for a in report['poses'].values()) and all(x['valid'] and x['volume_delta_mm3']<.1 for x in report['step']) and all(not a['interferences'] for a in report['tools'].values())
    (OUT/'M2R2S220_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('GEOMETRY_PASS',report['digital_geometry_pass'],flush=True)

if __name__=='__main__':main()
