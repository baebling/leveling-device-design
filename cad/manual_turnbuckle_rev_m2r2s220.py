"""M2R2-S220 cart-BOM CAD for the approved manual 3-RPS concept.

The lower SHAT12 centres are moved in the existing 4080 slots to gain
turnbuckle margin and reduce height.  All interfaces use purchased parts or
length-configured extrusions; no user-machined plate, bush, hole, tapped end,
or pin is introduced.  Catalogue fillets and thread helices remain simplified.
"""
from functools import lru_cache
from math import sin, cos, radians, sqrt
import numpy as np
import cadquery as cq
from cad import manual_turnbuckle_rev_m2 as b
from cad import manual_turnbuckle_rev_m2r1 as previous
from calculations import manual_turnbuckle_rev_m2_screen as old

C = b.Component
SILVER, BLACK, BLUE = previous.SILVER, previous.STEEL, previous.BLUE
LOWER = np.array([[0,30,63],[-30,-180,63],[30,-180,63]],float)
UPPER = np.array([[0,250,0],[-250,-180,0],[250,-180,0]],float)
AXES = np.array([[1,0,0],[0,1,0],[0,1,0]],float)
UPPER_PIN_Z = 63.0 + sqrt(280.0**2 - 220.0**2)

def pose(pitch=0, roll=0):
    R = np.array(old.rotation_matrix(pitch,roll))
    t = np.array([-250*R[0,1],-180*(1-R[1,1]),UPPER_PIN_Z])
    return R,t,UPPER@R.T+t

def transform(shape,pitch,roll):
    _,t,_=pose(pitch,roll)
    return b._transform_shape(shape,pitch,roll,0,tuple(t))

def part(name,group,shape,color=SILVER,material='catalogue component envelope'):
    return C(name,group,shape,color,material)

@lru_cache(None)
def profile(length,width):
    # Longitudinal X. Real slot pitch/opening; internal cavities only schematic.
    s=b._box(length,width,40,(0,0,20))
    for yy in ([0] if width==40 else [-20,20]):
        for z,h,w in [(37.25,5.52,10),(31,7,20),(2.75,5.52,10),(9,7,20)]:
            s=s.cut(b._box(length+2,w,h,(0,yy,z)))
    for sign in [-1,1]:
        s=s.cut(b._box(length+2,5.52,10,(0,sign*(width/2-2.75),20)))
        s=s.cut(b._box(length+2,7,20,(0,sign*(width/2-9),20)))
    return s.clean()

@lru_cache(None)
def angle_bracket():
    # HBLSSB8 catalogue: legs40, width30, thickness6; hole distances30 and20.
    s=b._box(40,6,30,(20,3,0)).fuse(b._box(6,40,30,(3,20,0)))
    s=s.cut(b._cylinder_between((30,-1,0),(30,7,0),4.5))
    return s.cut(b._cylinder_between((-1,20,0),(7,20,0),4.5)).clean()

def tnut(m):
    # Z=profile mounting face; HNTT8 boss3, total9, shoulder at depth5.5.
    # Underside taper/fillets remain conservative rectangular envelopes.
    s=b._box(17,17,6,(0,0,-8.5)).fuse(b._box(17,9.8,3,(0,0,-4)))
    return s.cut(b._cylinder_between((0,0,-12),(0,0,-2),m/2+.03)).clean()

def frame_hardware():
    out=[]
    for n,pos,axis,rot in [('X',(30,0,0),(0,1,0),-90),('Y',(0,20,0),(1,0,0),90)]:
        if n=='X':
            place=lambda s:s.rotate((0,0,0),(1,0,0),-90).translate(pos)
        else:
            place=lambda s:s.rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(0,1,0),90).translate(pos)
        bolt=b._cylinder_between((0,0,-9),(0,0,6),3.98).fuse(b._cylinder_between((0,0,6),(0,0,14),6.5))
        out.extend([part(n+'_M8X15','frame_fasteners',place(bolt),BLACK,'HCBMT8-15 stock bracket set'),part(n+'_HNTT8_8','frame_fasteners',place(tnut(8)),BLACK,'HNTT8-8, boss3/total9; underside taper schematic')])
    return out

def frame(prefix,z):
    specs=[('SIDE_L',700,40,90,(-330,0,z)),('SIDE_R',700,40,90,(330,0,z)),
           ('FRONT',620,40,0,(0,330,z)),('BACK',620,40,0,(0,-330,z)),
           ('REAR_RAIL',620,80,0,(0,-180,z)),('FRONT_RAIL',450,80,90,(0,85,z))]
    parts=[part(prefix+'_'+n,prefix+'_frame',profile(l,w).rotate((0,0,0),(0,0,1),a).translate(pos),
           SILVER,f'HFS8-40{w:02d}-{l}; cut only; slot section simplified') for n,l,w,a,pos in specs]
    # Convex open quadrant directions, angle stock face contacts both profile side slots.
    corners=[(-310,-310,0),(310,-310,90),(310,310,180),(-310,310,270),
             (-310,-220,270),(-310,-140,0),(310,-220,180),(310,-140,90),
             (-40,-140,90),(40,-140,0),(-40,310,180),(40,310,270)]
    for i,(x,y,a) in enumerate(corners,1):
        parts.append(part(f'{prefix}_BRACKET_{i}',prefix+'_brackets',angle_bracket().rotate((0,0,0),(0,0,1),a).translate((x,y,z+20)),BLACK,'HBLSSB8-SET; catalogue mounting dimensions, corner radii omitted'))
        for c in frame_hardware():
            parts.append(part(f'{prefix}_BRACKET_{i}_'+c.name,c.group,c.shape.rotate((0,0,0),(0,0,1),a).translate((x,y,z+20)),c.color,c.material))
    return parts

@lru_cache(None)
def shaft_support():
    # Local shaft Y, feet +/-X, foot bottom Z=-23; SHAT12 nominal dimensions.
    s=b._box(42,14,6,(0,0,-20)).fuse(b._box(20,14,31.5,(0,0,-1.25)))
    s=s.cut(b._cylinder_between((0,-8,0),(0,8,0),6.0))
    s=s.cut(b._box(1,16,15,(0,0,7.5)))
    for x in [-16,16]:
        s=s.cut(b._cylinder_between((x,0,-24),(x,0,-16),2.75))
    return s.clean()

def joint(prefix,upper=False):
    # Assemble around local Y shaft. Stock shims selected on receipt, never ground.
    parts=[]
    for sign in [-1,1]:
        suffix='L' if sign<0 else 'R'
        parts.append(part(prefix+'_SHAT12_'+suffix,'supports',shaft_support().translate((0,sign*20,0)),BLACK,'MISUMI SHAT12; bore12, H23, thickness14, mounting pitch32'))
        for n,x in enumerate([-16,16],1):
            bolt=b._cylinder_between((x,sign*20,-32),(x,sign*20,-16),2.45).fuse(b._cylinder_between((x,sign*20,-16),(x,sign*20,-11),4.25))
            washer=b._ring((x,sign*20,-16.5),(0,0,1),9,5.5,1,(1,0,0))
            nut=tnut(5).translate((x,sign*20,-23))
            parts += [part(f'{prefix}_{suffix}_CB5_16_{n}','fasteners',bolt,BLACK,'MISUMI CB5-16; nominal engagement6.5 and floor clearance3.5'),part(f'{prefix}_{suffix}_FWSSB_D9_V5p5_T1_{n}','fasteners',washer,SILVER,'MISUMI FWSSB-D9-V5.5-T1'),part(f'{prefix}_{suffix}_HNTT8_5_{n}','fasteners',nut,BLACK,'MISUMI HNTT8-5 boss3/total9, taper schematic')]
        clamp=b._cylinder_between((10,sign*20,9.5),(14,sign*20,9.5),3.5)
        parts.append(part(prefix+'_SHAT_CLAMP_HEAD_'+suffix,'clamp_heads',clamp,BLACK,'Supplied M4 head envelope; tool corridor +X'))
        # 26 gap = 16 + 2*5 upper; lower 14 + 2*6. Leave nominal 0.2 axial clearance lower.
        total=5.0 if upper else 5.9
        inner=8 if upper else 7
        parts.append(part(prefix+'_SHIM_STACK_'+suffix,'shims',b._ring((0,sign*(inner+total/2),0),(0,1,0),18,12.1,total,(1,0,0)),SILVER,'MISUMI PCIMR/CIMR 12x18 stock shim stack; measured fit required'))
        # SCSJ12-6 touches the outer SHAT face at |Y|=27 and extends to |Y|=33.
        parts.append(part(prefix+'_SCSJ12_6_'+suffix,'collars',b._ring((0,sign*30,0),(0,1,0),25,12.01,6,(1,0,0)),BLACK,'MISUMI SCSJ12-6; OD25 W6, clamp screw envelope omitted'))
    parts.append(part(prefix+'_SHAFT12X100','shafts',b._cylinder_between((0,-50,0),(0,50,0),5.998),SILVER,'MISUMI SFU12-100 h5 catalogue configured shaft; no end machining'))
    if upper:
        return [part(c.name,c.group,c.shape.rotate((0,0,0),(1,0,0),180),c.color,c.material) for c in parts]
    return parts

def stock_link(i,lower,upper,axis,ut):
    # THK PHS12L catalogue ball diameter22.225, inner16, housing12, neck22.
    unit=cq.Vector(*(upper-lower)).normalized(); av=cq.Vector(*axis)
    originals=b._link_shape(tuple(lower),tuple(upper),tuple(axis),tuple(ut)).Solids()
    rad,half=22.225/2,6
    edge=sqrt((rad+.025)**2-half**2)
    shell=(cq.Workplane('XY').moveTo(15,-half).lineTo(15,half).lineTo(edge,half)
       .threePointArc((rad+.025,0),(edge,-half)).close().revolve(360,(0,0,0),(0,1,0)).val())
    neck=b._cylinder_between((-50,0,0),(-13,0,0),11)
    housing=shell.fuse(neck).clean().located(cq.Location(cq.Plane(origin=tuple(upper),xDir=unit.toTuple(),normal=unit.cross(av).toTuple())))
    half=8;edge=sqrt(rad*rad-half*half)
    ball=(cq.Workplane('XY').moveTo(6,-half).lineTo(edge,-half).threePointArc((rad,0),(edge,half)).lineTo(6,half).close().revolve(360,(0,0,0),(0,1,0)).val())
    utv=cq.Vector(*ut); xx=utv.cross(unit).cross(utv).normalized()
    ball=ball.located(cq.Location(cq.Plane(origin=tuple(upper),xDir=xx.toTuple(),normal=xx.cross(utv).toTuple())))
    return [part(f'A{i}_TURNBUCKLE','links',cq.Compound.makeCompound(list(originals[:-2])+[housing]),BLACK,'NBK STB-M12 + IMAO BJ761-12011N + MISUMI NTFL12-36 + IKO PHS12L; threaded envelopes'),part(f'A{i}_PHS12L_INNER','bearings',ball,SILVER,'IKO PHS12L inner-ring catalogue envelope')]

def components_for_pose(pitch=0,roll=0):
    R,t,points=pose(pitch,roll)
    result=frame('LOWER',0)
    result += [part(c.name,c.group,transform(c.shape,pitch,roll),c.color,c.material) for c in frame('UPPER',23)]
    for i,(lo,up,local,axis) in enumerate(zip(LOWER,points,UPPER,AXES),1):
        for isupper,center in [(False,lo),(True,local)]:
            # Rear A2 lower supports face outward so the SHAT12 M4 tool axis
            # does not cross the adjacent A3 support.  Reversing a revolute
            # axis is kinematically identical and needs no different part.
            a=-90 if i==1 else (180 if i==2 and not isupper else 0)
            for c in joint(('U' if isupper else 'L')+str(i),isupper):
                s=c.shape.rotate((0,0,0),(0,0,1),a).translate(tuple(center))
                if isupper:s=transform(s,pitch,roll)
                result.append(part(c.name,c.group,s,c.color,c.material))
        result+=stock_link(i,lo,up,axis,R@axis)
    return result

def tool_paths(pitch=0,roll=0):
    """Straight hex-key insertion envelopes; independent sequential operations."""
    tools=[]
    corners=[(-310,-310,0),(310,-310,90),(310,310,180),(-310,310,270),
             (-310,-220,270),(-310,-140,0),(310,-220,180),(310,-140,90),
             (-40,-140,90),(40,-140,0),(-40,310,180),(40,310,270)]
    for upper,z in [(False,0),(True,23)]:
        for i,(x,y,a) in enumerate(corners,1):
            for tag,start,end in [('X',(30,14.1,0),(30,74.1,0)),('Y',(14.1,20,0),(74.1,20,0))]:
                s=b._cylinder_between(start,end,3.6).rotate((0,0,0),(0,0,1),a).translate((x,y,z+20))
                if upper:s=transform(s,pitch,roll)
                tools.append(part(f'{"UPPER" if upper else "LOWER"}_B{i}_{tag}_6MM_HEX','tool',s,BLUE))
    for i,(lo,up) in enumerate(zip(LOWER,UPPER),1):
        for upper,center in [(False,lo),(True,up)]:
            a=-90 if i==1 else (180 if i==2 and not upper else 0)
            for sign in [-1,1]:
                items=[(f'M5_{x}',(x,sign*20,-10.9),(x,sign*20,49.1),2.5) for x in [-16,16]]
                items.append(('M4_CLAMP',(14.1,sign*20,9.5),(64.1,sign*20,9.5),2))
                for tag,start,end,r in items:
                    s=b._cylinder_between(start,end,r)
                    if upper:s=s.rotate((0,0,0),(1,0,0),180)
                    s=s.rotate((0,0,0),(0,0,1),a).translate(tuple(center))
                    if upper:s=transform(s,pitch,roll)
                    tools.append(part(f'{"U" if upper else "L"}{i}_{sign}_{tag}','tool',s,BLUE))
    return tools

def workspace():
    rows=[]
    for p in np.linspace(-3,3,13):
        for r in np.linspace(-3,3,13):
            R,t,u=pose(float(p),float(r));delta=u-LOWER
            lengths=np.linalg.norm(delta,axis=1)
            constraint=np.einsum('ij,ij->i',AXES,delta)
            # Independent R constraints on rigid-body twist [vx,vy,vz,wx,wy,wz].
            A=np.hstack([AXES,np.cross(u-t,AXES)])
            unit=delta/lengths[:,None]
            locked=np.vstack([A,np.hstack([unit,np.cross(u-t,unit)])])
            rows.append({'pitch':float(p),'roll':float(r),'lengths_mm':lengths.tolist(),'constraint_residual_mm':float(max(abs(constraint))),'constraint_rank':int(np.linalg.matrix_rank(A)), 'locked_rank':int(np.linalg.matrix_rank(locked)), 'tx_mm':float(t[0]),'ty_mm':float(t[1])})
    lens=[v for r in rows for v in r['lengths_mm']]
    return {'samples':len(rows),'min_length_mm':min(lens),'max_length_mm':max(lens),'minimum_thread_engagement_mm':38-(max(lens)-260)/2,'max_constraint_residual_mm':max(r['constraint_residual_mm'] for r in rows),'all_constraint_ranks_3':all(r['constraint_rank']==3 for r in rows),'all_locked_ranks_6':all(r['locked_rank']==6 for r in rows),'max_abs_tx_mm':max(abs(r['tx_mm']) for r in rows),'max_abs_ty_mm':max(abs(r['ty_mm']) for r in rows),'passes':min(lens)>=260 and max(lens)<=300 and all(r['constraint_rank']==3 and r['locked_rank']==6 for r in rows),'rows':rows}


def catalogue_interfaces():
    return {
        'revision':'M2R2-S220',
        'lower_joint_centres_mm':LOWER.tolist(),
        'upper_joint_local_centres_mm':UPPER.tolist(),
        'upper_pin_z_mm':UPPER_PIN_Z,
        'estimated_overall_height_mm':UPPER_PIN_Z+63.0,
        'neutral_pin_distance_mm':280.0,
        'rear_shat12_foot_clearance_mm':18.0,
        'user_machining_required':False,
        'cart_bom_substitutions':{
            'shaft_collar':'SCSJ12-6, bore12 OD25 W6',
            'coupling_nut':'NTFL12-36, M12x1.75 L36',
            'support_washer':'FWSSB-D9-V5.5-T1',
            'support_bolt':'CB5-16',
            'shims':'PCIMR12-18-1.0 / CIMR12-18-0.5 / CIMR12-18-0.2',
            'upper_rod_end':'IKO PHS12L',
        },
    }
