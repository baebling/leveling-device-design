"""M2R2 stock-connection review CAD, not fabrication geometry.

Catalogue mounting dimensions; simplified extrusion cavities and bracket bodies.
No user-machined plates, bushes, holes, tapped ends, or pins.
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
LOWER = np.array([[0,75,63],[-75,-200,63],[75,-200,63]],float)
UPPER = np.array([[0,250,0],[-250,-200,0],[250,-200,0]],float)
AXES = np.array([[1,0,0],[0,1,0],[0,1,0]],float)
UPPER_PIN_Z = 281.0

def pose(pitch=0, roll=0):
    R = np.array(old.rotation_matrix(pitch,roll))
    t = np.array([-250*R[0,1],-200*(1-R[1,1]),UPPER_PIN_Z])
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
        for z,h,w in [(38,4.02,10),(31.75,8.5,16),(2,4.02,10),(8.25,8.5,16)]:
            s=s.cut(b._box(length+2,w,h,(0,yy,z)))
    for sign in [-1,1]:
        s=s.cut(b._box(length+2,4.02,10,(0,sign*(width/2-2),20)))
        s=s.cut(b._box(length+2,8.5,16,(0,sign*(width/2-8.25),20)))
    return s.clean()

@lru_cache(None)
def angle_bracket():
    # HBLSS8 envelope, catalogue bolt kit; fillets/exact hole offsets pending vendor CAD.
    s=b._box(35,4,32,(17.5,2,0)).fuse(b._box(4,35,32,(2,17.5,0)))
    s=s.cut(b._cylinder_between((20,-1,0),(20,5,0),4.5))
    return s.cut(b._cylinder_between((-1,20,0),(5,20,0),4.5)).clean()

def frame(prefix,z):
    specs=[('SIDE_L',700,40,90,(-330,0,z)),('SIDE_R',700,40,90,(330,0,z)),
           ('FRONT',620,40,0,(0,330,z)),('BACK',620,40,0,(0,-330,z)),
           ('REAR_RAIL',620,80,0,(0,-200,z)),('FRONT_RAIL',470,80,90,(0,75,z))]
    parts=[part(prefix+'_'+n,prefix+'_frame',profile(l,w).rotate((0,0,0),(0,0,1),a).translate(pos),
           SILVER,f'HFS8-40{w:02d}-{l}; cut only; slot section simplified') for n,l,w,a,pos in specs]
    # Convex open quadrant directions, angle stock face contacts both profile side slots.
    corners=[(-310,-310,0),(310,-310,90),(310,310,180),(-310,310,270),
             (-310,-240,270),(-310,-160,0),(310,-240,180),(310,-160,90),
             (-40,-160,90),(40,-160,0),(-40,310,180),(40,310,270)]
    for i,(x,y,a) in enumerate(corners,1):
        parts.append(part(f'{prefix}_BRACKET_{i}',prefix+'_brackets',angle_bracket().rotate((0,0,0),(0,0,1),a).translate((x,y,z+20)),BLACK,'HBLSSB8-SET; exact bracket geometry/fasteners not modeled'))
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
            washer=b._ring((x,sign*20,-16.5),(0,0,1),10,5.3,1,(1,0,0))
            nut=b._box(12,15.5,6,(x,sign*20,-30)).cut(b._cylinder_between((x,sign*20,-34),(x,sign*20,-26),2.5))
            parts += [part(f'{prefix}_{suffix}_M5X16_{n}','fasteners',bolt,BLACK,'M5x16; final engagement check required'),part(f'{prefix}_{suffix}_W5_{n}','fasteners',washer),part(f'{prefix}_{suffix}_HNTT8_5_{n}','fasteners',nut,BLACK,'HNTT8-5 envelope')]
        # 26 gap = 16 + 2*5 upper; lower 14 + 2*6. Leave nominal 0.2 axial clearance lower.
        total=5.0 if upper else 5.9
        inner=8 if upper else 7
        parts.append(part(prefix+'_SHIM_STACK_'+suffix,'shims',b._ring((0,sign*(inner+total/2),0),(0,1,0),18,12.1,total,(1,0,0)),SILVER,'K1151.1218100 plus .5/.2 shims; stack envelope, measured fit required'))
        parts.append(part(prefix+'_MCL12F_'+suffix,'collars',b._ring((0,sign*32.5,0),(0,1,0),28,12.01,11,(1,0,0)),BLACK,'Ruland MCL-12-F; clamp screw envelope omitted'))
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
    return [part(f'A{i}_TURNBUCKLE','links',cq.Compound.makeCompound(list(originals[:-2])+[housing]),BLACK,'NBK STB-M12 + BJ761-12011N + DIN6334 M12x36 + THK PHS12L; threaded envelopes'),part(f'A{i}_PHS12L_INNER','bearings',ball)]

def components_for_pose(pitch=0,roll=0):
    R,t,points=pose(pitch,roll)
    result=frame('LOWER',0)
    result += [part(c.name,c.group,transform(c.shape,pitch,roll),c.color,c.material) for c in frame('UPPER',23)]
    for i,(lo,up,local,axis) in enumerate(zip(LOWER,points,UPPER,AXES),1):
        a=-90 if i==1 else 0
        for isupper,center in [(False,lo),(True,local)]:
            for c in joint(('U' if isupper else 'L')+str(i),isupper):
                s=c.shape.rotate((0,0,0),(0,0,1),a).translate(tuple(center))
                if isupper:s=transform(s,pitch,roll)
                result.append(part(c.name,c.group,s,c.color,c.material))
        result+=stock_link(i,lo,up,axis,R@axis)
    return result

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
