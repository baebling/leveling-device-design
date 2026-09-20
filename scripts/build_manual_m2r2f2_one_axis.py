"""Build and verify one complete A1 axis plus exploded upper/lower joints."""
import sys, json, hashlib
from pathlib import Path
from itertools import combinations
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cadquery as cq
import vtk
from cad import manual_m2r2f2_one_axis as model
from scripts.build_manual_turnbuckle_rev_m2r1 import actor, bbox_overlap

OUT = ROOT / "outputs/manual_m2r2f2_one_axis"


def render(parts, name, camera=(1.15, -1.55, .8), subtitle=""):
    ren = vtk.vtkRenderer(); ren.SetBackground(.95, .97, .99)
    for c in parts: ren.AddActor(actor(c))
    cam = ren.GetActiveCamera(); cam.SetPosition(*camera); cam.SetFocalPoint(0, 0, 0)
    cam.SetViewUp(0, 0, 1); cam.ParallelProjectionOn(); ren.ResetCamera(); cam.SetParallelScale(cam.GetParallelScale()*1.08)
    labels = [
        ("M2R2F2 / ONE AXIS ASSEMBLY REVIEW", 950, 25, (.04,.10,.17)),
        (subtitle, 915, 18, (.12,.20,.28)),
        ("CATALOGUE INTERFACE DIMENSIONS - REVIEW ONLY - NOT FOR FABRICATION", 24, 16, (.72,.10,.07))]
    for text,y,size,color in labels:
        t=vtk.vtkTextActor();t.SetInput(text);t.SetPosition(25,y);t.GetTextProperty().SetFontFamilyToCourier();t.GetTextProperty().SetFontSize(size);t.GetTextProperty().SetColor(*color);ren.AddActor(t)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.SetSize(1600,1000);win.SetMultiSamples(8);win.AddRenderer(ren);win.Render()
    cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.SetInputBufferTypeToRGB();cap.ReadFrontBufferOff();cap.Update()
    wr=vtk.vtkPNGWriter();wr.SetFileName(str(OUT/'renders'/f'{name}.png'));wr.SetInputConnection(cap.GetOutputPort());wr.Write();win.Finalize()


def export(parts, name):
    path=OUT/'step'/f'{name}.step';a=cq.Assembly(name='M2R2F2_REVIEW_NOT_FOR_FABRICATION')
    for c in parts:a.add(c.shape,name=c.name,color=cq.Color(*c.color))
    a.export(str(path));read=cq.importers.importStep(str(path)).val();expected=cq.Compound.makeCompound([c.shape for c in parts])
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'valid':read.isValid() and all(s.isValid() for s in read.Solids()),'solids':len(read.Solids()),'volume_delta_mm3':abs(read.Volume()-expected.Volume())}


def collision_audit(parts):
    boxes={c.name:c.shape.BoundingBox() for c in parts};unexpected=[];intentional=[]
    for a,b in combinations(parts,2):
        if not bbox_overlap(boxes[a.name],boxes[b.name]):continue
        v=a.shape.intersect(b.shape).Volume()
        if v<=.01:continue
        names=a.name+' '+b.name
        if (('M5X16' in names and 'HNTT8_5' in names) or
            ('SHAT_CLAMP_HEAD' in names and 'SHAT12' in names) or
            ('HFS8_4080' in names and 'HNTT8_5' in names)):
            intentional.append({'a':a.name,'b':b.name,'volume_mm3':v,'reason':'modeled threaded/clamp engagement'})
        else:unexpected.append({'a':a.name,'b':b.name,'volume_mm3':v})
    return {'components':len(parts),'invalid':[c.name for c in parts if not c.shape.isValid()], 'unexpected':unexpected,'intentional':intentional}


def contact_distances(parts, upper):
    q={c.name:c for c in parts};prefix='U1' if upper else 'L1';member='PHS12L_INNER_RING' if upper else 'BJ761_12011N'
    rows=[]
    for side in ['L','R']:
        rows += [
            {'pair':[prefix+'_SHAT12_'+side,prefix+'_SHIM_STACK_'+side],'distance_mm':q[prefix+'_SHAT12_'+side].shape.distance(q[prefix+'_SHIM_STACK_'+side].shape)},
            {'pair':[prefix+'_SHIM_STACK_'+side,member],'distance_mm':q[prefix+'_SHIM_STACK_'+side].shape.distance(q[member].shape)},
            {'pair':[prefix+'_SHAT12_'+side,prefix+'_MCL12F_'+side],'distance_mm':q[prefix+'_SHAT12_'+side].shape.distance(q[prefix+'_MCL12F_'+side].shape)},
            {'pair':[prefix+'_SHAFT12X100',prefix+'_SHAT12_'+side],'distance_mm':q[prefix+'_SHAFT12X100'].shape.distance(q[prefix+'_SHAT12_'+side].shape)}]
    return rows


def main():
    for d in [OUT,OUT/'step',OUT/'renders']:d.mkdir(parents=True,exist_ok=True)
    sets={'A1_COMPLETE_ASSEMBLED':model.one_axis_complete(),'A1_LOWER_ASSEMBLED':model.assembled_lower(),
          'A1_UPPER_ASSEMBLED':model.assembled_upper(),'A1_LOWER_EXPLODED':model.lower_exploded(),
          'A1_UPPER_EXPLODED':model.upper_exploded()}
    report={'revision':'M2R2F2','dimension_status':model.DIMENSION_STATUS,'sets':{},'step':[],
            'purchase_release':False,'fabrication_release':False,'physical_fit_test':False}
    for name,parts in sets.items():
        report['sets'][name]=collision_audit(parts);report['step'].append(export(parts,name+'_REVIEW'))
    report['lower_contact_distances']=contact_distances(sets['A1_LOWER_ASSEMBLED'],False)
    report['upper_contact_distances']=contact_distances(sets['A1_UPPER_ASSEMBLED'],True)
    report['digital_pass']=all(not x['invalid'] and not x['unexpected'] for x in report['sets'].values()) and all(s['valid'] and s['volume_delta_mm3']<.1 for s in report['step'])
    render(sets['A1_COMPLETE_ASSEMBLED'],'A1_COMPLETE_ASSEMBLED',(1,-1.4,.65),'Actual A1 placement: lower R - STB-M12 - upper PHS12L')
    render(sets['A1_LOWER_ASSEMBLED'],'A1_LOWER_ASSEMBLED',(1.2,-1,.65),'LOWER R: SHAT12 / 5.9 shim / BJ761 W14 / 5.9 shim / SHAT12')
    render(sets['A1_UPPER_ASSEMBLED'],'A1_UPPER_ASSEMBLED',(1.2,-1,-.65),'UPPER S underside: SHAT12 / 5.0 shim / PHS12L inner W16 / 5.0 shim / SHAT12')
    render(sets['A1_LOWER_EXPLODED'],'A1_LOWER_EXPLODED',(1.1,-1.4,.55),'Exploded along shaft X; M5 fasteners separated in Z')
    render(sets['A1_UPPER_EXPLODED'],'A1_UPPER_EXPLODED',(1.1,-1.4,-.55),'Underside exploded along shaft X; PHS holder stays around supplied inner ring')
    (OUT/'M2R2F2_ONE_AXIS_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'COMPONENT_REGISTER.json').write_text(json.dumps({k:[{'name':c.name,'group':c.group,'basis':c.material} for c in v] for k,v in sets.items()},indent=2),encoding='utf-8')
    print(json.dumps({'digital_pass':report['digital_pass'],'components':{k:len(v) for k,v in sets.items()},'step':report['step']},indent=2),flush=True)


if __name__=='__main__':main()
