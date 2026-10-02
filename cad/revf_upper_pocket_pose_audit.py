"""Finite Rev F review, never fabrication approval. Units mm/deg/mm^3.

Broad phase transforms enclosing source AABB corners (not meshes). A 0.25 mm
proximity margin is a screening assumption, NOT a delivered tolerance. Exact
representatives use actual supplier STEP and nominal Task 3 joint envelopes.
Uncomputed near contacts remain UNKNOWN/HOLD; finite samples are not sweeps.
"""
from dataclasses import asdict
from functools import lru_cache
from itertools import product, combinations
from math import acos, degrees
import json
import numpy as np
from cad.revf_upper_pocket_inputs import load_inputs
from cad.profile_radial_reve_actual_vendor import Pose, platform_transform, actuator_pin_lengths, upper_eye_points
from cad.profile_radial_revf_upper_pocket_review import revf_components_for_pose, joint_reference, assembly_path_review
from fusion_scripts.ProfileRadialRevD import revd_data
from calculations.reve_approved_workspace import dense_pose_grid, sample_pose_segment
from calculations.reve_command_jog_path_audit import _dense_adjacent_jog_segments
from calculations.reve_home_path_audit import alternating_length_path
from calculations.revf_forward_kinematics import solve_pose_from_lengths

MARGIN_MM = .25
RELEASES = dict(purchase_release=False, fabrication_release=False, control_power_test_release=False, motor_power_release=False)

def review_poses():
    return tuple(Pose(f'grid_{i}',*p) for i,p in enumerate(dense_pose_grid()))

def representative_poses():
    return tuple(Pose(f'representative_{i}',*p) for i,p in enumerate(product((0.,25.,50.),(-3.,0.,3.),(-3.,0.,3.))))

def boolean_measure(first, second):
    """Invalid input/common or exceptions must not become zero-volume clear."""
    try:
        if not first.isValid() or not second.isValid():
            raise ValueError('invalid source B-rep')
        common=first.intersect(second)
        volume=float(common.Volume())
        valid=common.isValid() and np.isfinite(volume) and volume >= -1e-8
        return dict(valid=bool(valid),volume_mm3=max(0.,volume) if valid else None)
    except Exception as error:
        return dict(valid=False,volume_mm3=None,error=str(error))

def mount_attachment_review(inputs):
    """Separate nominal mounting-axis alignment from unverified real slot fit."""
    pose=Pose('mount_neutral',25,0,0)
    parts=revf_components_for_pose(pose,inputs)
    frame=next(p.shape for p in parts if p.group=='upper_frame')
    measurements=[]
    for part in parts:
        if 'mount_bolt_' not in part.name: continue
        row=boolean_measure(part.shape,frame)
        row.update(part=part.name,gap_mm=float(part.shape.distance(frame)))
        axis=int(part.name[1]);centre=part.shape.Center()
        relative=np.array([centre.x,centre.y,centre.z])-np.array(joint_reference(axis,pose)['ball_center'])
        platform=np.array(platform_transform(pose)[0]).T@relative
        centered=abs(platform[1])<1e-5 and abs(abs(platform[0])-22.)<1e-5
        row.update(platform_center_x_mm=float(platform[0]),platform_center_y_mm=float(platform[1]),nominal_crossmember_centered=bool(centered))
        measurements.append(row)
    aligned=len(measurements)==6 and all(r['nominal_crossmember_centered'] for r in measurements)
    return dict(mount_attachment_status='UNKNOWN/HOLD' if aligned else 'INVALID_NOMINAL_CENTERING/HOLD',
        crossmember_centering_status='ALIGNED_NOMINAL' if aligned else 'INVALID',actual_slot_fit_status='UNKNOWN',
        legacy_slot_depth_mm=6.9,candidate_insertion_mm=7.5,legacy_slot_floor_overlap_mm=.6,
        actual_dnf3030_interference_proven=False,
        mount_attachment_measurements=measurements,
        mount_attachment_findings=[f"{r['part']}: nominal centering {'aligned' if r['nominal_crossmember_centered'] else 'invalid'}; " + ('invalid Boolean unresolved' if not r['valid'] else 'retained shallow-model intersection; actual slot unknown' if r['volume_mm3']>1e-6 else 'actual slot engagement unverified') for r in measurements],
        additional_mechanical_blockers=['Open +local Y housing insertion channel provides no independent axial capture; M6 retainer engagement/preload/locking under reversal unverified', 'Staged three-axis frame/T-nut/tool paths are finite nominal checks, not delivered assembly proof', 'Invalid head-side WSSB10-6-4 washer / supplier moving-part eye Boolean is unresolved seating, not proven physical penetration'],
        mount_attachment_blocker='Legacy slot floor 6.9 mm versus 7.5 mm insertion creates nominal 0.6 mm overlap. Historical Daeyoung DY5155 nominal floor 10.5 mm and different DYC section nominal floor 11.1 mm are not interchangeable; current NAVIMRO DNP3030 image mismatch leaves delivered DNF fit/tolerance/strength UNKNOWN.',**RELEASES)

def _motion(part, pose):
    axis=int(part.name[1]) if part.name.startswith(('A1_','A2_','A3_')) else None
    rotation,translation,_=platform_transform(pose)
    if part.group=='actuators':
        lower=np.array(revd_data.lower_eye_points()[axis-1]); eye=np.array(upper_eye_points(pose)[axis-1])
        u=(eye-lower)/np.linalg.norm(eye-lower); t=np.array(revd_data.support_basis()[axis-1][1])
        return np.column_stack((-u,t,-np.cross(u,t))), eye if 'NEIGUAN' in part.name else lower
    if part.group in ('upper_frame','upper_brackets'):
        return np.array(rotation),np.array(translation)
    if part.group in ('upper_pockets','upper_joints','upper_fasteners'):
        follows=part.group!='upper_joints' or part.name.endswith(('housing','m6_retainer_envelope','grease_nipple_unknown_envelope'))
        return np.array(rotation) if follows else np.eye(3),np.array(joint_reference(axis,pose)['ball_center'])
    return np.eye(3),np.zeros(3)

def _exemption(a,b):
    # Explicit nominal contact interfaces only; exemptions remain unverified.
    if a.group.startswith('lower') and b.group.startswith('lower'): return 'retained lower fixed assembly'
    if a.group in ('upper_frame','upper_brackets') and b.group in ('upper_frame','upper_brackets'): return 'retained upper fixed assembly'
    same=a.name[:3]==b.name[:3] and a.name.startswith(('A1_','A2_','A3_'))
    if same and a.group==b.group=='actuators': return 'supplier internal assembly'
    names=(a.name,b.name)
    if same:
        keys=tuple(n.split('_REVF_')[-1] for n in names)
        contact={frozenset(p) for p in [('housing','ball'),('housing','m6_retainer_envelope'),('pin_shoulder','ball'),('pin_shoulder','shim'),('pin_shoulder','spacer'),('pin_shoulder','e5_ring_envelope')]}
        if frozenset(keys) in contact: return 'nominal bearing/retention/stack interface'
        if any('POCKET_REVIEW' in n for n in names) and any(n.endswith('housing') for n in names): return 'housing saddle interface'
    return None

@lru_cache(maxsize=4)
def _templates(inputs):
    neutral=Pose('template',25,0,0)
    parts=revf_components_for_pose(neutral,inputs)
    corners=[]
    for p in parts:
        bb=p.shape.BoundingBox()
        world=np.array(list(product((bb.xmin,bb.xmax),(bb.ymin,bb.ymax),(bb.zmin,bb.zmax))))
        r,t=_motion(p,neutral)
        corners.append((world-t)@r)
    pairs=[]; exemptions=[]
    for i,j in combinations(range(len(parts)),2):
        why=_exemption(parts[i],parts[j])
        if why: exemptions.append(dict(pair=[parts[i].name,parts[j].name],reason=why,status='INTERFACE_UNVERIFIED'))
        else: pairs.append((i,j))
    return parts,corners,np.array(pairs),exemptions

def audit_pose(pose, inputs, *, exact=False):
    parts,corners,pairs,_=_templates(inputs)
    low=[];high=[]
    for part,local in zip(parts,corners):
        r,t=_motion(part,pose); world=local@r.T+t
        low.append(world.min(axis=0)); high.append(world.max(axis=0))
    low=np.array(low);high=np.array(high)
    near=np.all((low[pairs[:,0]]<=high[pairs[:,1]]+MARGIN_MM)&(low[pairs[:,1]]<=high[pairs[:,0]]+MARGIN_MM),axis=1)
    candidates=pairs[near]; measurements=[]; invalid=0
    if exact:
        actual=revf_components_for_pose(pose,inputs)
        for i,j in candidates:
            row=boolean_measure(actual[i].shape,actual[j].shape)
            row.update(pair=[parts[i].name,parts[j].name],pair_indices=[int(i),int(j)],location_mm=((low[i]+high[i])/2).tolist())
            measurements.append(row); invalid+=not row['valid']
    lengths=actuator_pin_lengths(pose)
    hinges=max(abs(float(np.dot(np.array(eye)-lower,tangent))) for eye,lower,(_,tangent) in zip(upper_eye_points(pose),revd_data.lower_eye_points(),revd_data.support_basis()))
    r,_,_=platform_transform(pose)
    angles=[degrees(acos(np.clip(abs(np.dot(t,np.array(r)@t)),-1,1))) for _,t in revd_data.support_basis()]
    collision=[m for m in measurements if m['valid'] and m['volume_mm3']>1e-6]
    return dict(pose=asdict(pose),status='HOLD',geometry_status='INTERFERENCE' if collision else 'UNKNOWN' if invalid or not exact else 'NOMINAL_SAMPLE_CLEAR',
        pin_lengths_mm=list(lengths),articulation_deg=angles,hinge_constraint_residual_mm=hinges,
        length_window_policy='NORMAL_210_TO_280',normal_window_pass=min(lengths)>=210 and max(lengths)<=280,
        kinematic_sample_pass=min(lengths)>=210 and max(lengths)<=280 and max(angles)<=13 and hinges<=1e-7,
        nominal_lower_switch_margin_mm=min(lengths)-205,nominal_upper_switch_margin_mm=305-max(lengths),limits_status='NOMINAL_UNVERIFIED',
        pair_count=len(pairs),broad_clear_pair_count=int((~near).sum()),near_pair_indices=candidates.tolist(),exact_pair_count=len(measurements),
        unknown_pair_count=len(candidates)-len(measurements)+invalid,invalid_boolean_count=int(invalid),exact_measurements=measurements,
        interference_count=len(collision),profile_slot_status='UNVERIFIED',**RELEASES)

def bounded_followup(audit, inputs, *, budget=24, previous=None):
    """Execute a bounded, resumable exact queue, never declare backlog clear.

    Distinct key = pose coordinates + part indices. Per scope/pair, take its
    worst pending state; prioritize pair classes absent from representatives,
    then known invalid/interfering classes, articulation and switch proximity.
    Round-robin dense/command/HOME ensures all three scopes get follow-up.
    Remaining keys are losslessly defined by the near arrays minus the exact
    key ledgers, avoiding millions of duplicated backlog JSON strings.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError('nonnegative integer exact-pair budget required')
    def coordinates(row):
        return tuple(round(float(row['pose'][k]),9)+0.0 for k in ('lift_mm','pitch_deg','roll_deg'))
    def key(pose, pair):
        return json.dumps([*pose,*pair],separators=(',',':'))
    completed=list((previous or {}).get('completed',[]))
    done={r['key'] for r in completed}; representative_keys=set();covered=set();risk_pairs=set()
    for row in audit['representatives']:
        for measured in row['exact_measurements']:
            pair=tuple(measured['pair_indices']);covered.add(pair)
            representative_keys.add(key(coordinates(row),pair))
            if not measured['valid'] or measured['volume_mm3']>1e-6: risk_pairs.add(pair)
    done.update(representative_keys)
    unique={}
    for scope,rows in (('dense',audit['dense']),('command',audit['path_states']),('home',audit['home'])):
        for row in rows:
            if 'pose' not in row: continue
            pose=coordinates(row)
            if pose not in unique: unique[pose]=(row,set())
            unique[pose][1].add(scope)
    best={};backlog=0
    # All duplicate occurrences share one physical key, not repeated Booleans.
    for pose,(row,scopes) in unique.items():
        state_risk=(-max(row['articulation_deg']),min(row['nominal_lower_switch_margin_mm'],row['nominal_upper_switch_margin_mm']))
        for indices in row['near_pair_indices']:
            pair=tuple(indices);identifier=key(pose,pair)
            if identifier in done: continue
            backlog+=1
            priority=(pair in covered,pair not in risk_pairs,*state_risk,pose,pair)
            for scope in scopes:
                slot=(scope,pair)
                if slot not in best or priority<best[slot][0]: best[slot]=(priority,identifier,pose,pair)
    queues={scope:sorted((v for (s,_),v in best.items() if s==scope)) for scope in ('dense','command','home')}
    positions={s:0 for s in queues};selected=[];selected_keys=set()
    while len(selected)<budget:
        progress=False
        for scope,queue in queues.items():
            while positions[scope]<len(queue):
                candidate=queue[positions[scope]];positions[scope]+=1
                if candidate[1] in selected_keys: continue
                selected.append((scope,candidate));selected_keys.add(candidate[1]);progress=True;break
            if len(selected)>=budget: break
        if not progress: break
    geometries={}
    for scope,(priority,identifier,coords,pair) in selected:
        if coords not in geometries:
            geometries[coords]=revf_components_for_pose(Pose('bounded_exact',*coords),inputs)
        parts=geometries[coords];i,j=pair
        measurement=boolean_measure(parts[i].shape,parts[j].shape)
        completed.append(dict(key=identifier,scope=scope,pose=list(coords),pair_indices=list(pair),
            pair=[parts[i].name,parts[j].name],representative_uncovered=not priority[0],
            **measurement))
    return dict(status='HOLD',budget_per_run=budget,attempted_this_run=len(selected),completed=completed,
        backlog_distinct_keys=backlog-len(selected),invalid_completed_count=sum(not r['valid'] for r in completed),
        positive_completed_count=sum(r['valid'] and r['volume_mm3']>1e-6 for r in completed),
        backlog_definition='Unique pose-coordinate/part-index keys in dense, command and HOME near_pair_indices minus representative exact keys and completed keys; invalid completed keys remain unresolved separately',
        priority_policy='Per-scope/per-pair worst pending state; representative-uncovered first, known invalid/interfering pair next, maximum articulation then minimum switch margin; deterministic dense/command/HOME round-robin',
        full_near_contact_clearance=False,**RELEASES)

def refresh_invalid_boolean_counts(audit):
    """Separate scope counts; assembly stages already aggregate child paths.

    Counts are Boolean attempts, not unique physical contacts across scopes.
    Preserve the historical invalid_boolean_count as a pose-only alias.
    """
    pose=sum(row.get('invalid_boolean_count',0) for scope in ('representatives','dense','path_states','home')
        for row in audit.get(scope,()))
    pose+=sum(not row['valid'] for row in audit.get('exact_followup',{}).get('completed',()))
    stages=audit.get('assembly_path',{}).get('stages')
    assembly=sum(row['invalid_boolean_count'] for row in stages) if stages is not None else None
    audit.update(invalid_boolean_count=pose,pose_invalid_boolean_count=pose,
        assembly_invalid_boolean_count=assembly,
        combined_invalid_boolean_count=pose+assembly if assembly is not None else None,
        invalid_boolean_count_scope='Legacy alias: pose checks including supplemental exact only; combined count adds top-level assembly stages once, not their duplicated child summaries')


def refresh_worst_interference(audit):
    """Derived global witness over every valid measured intersection, not backlog."""
    candidates=[]
    for row in audit['representatives']:
        for measured in row['exact_measurements']:
            candidates.append({**measured,'pose':row['pose'],'measurement_scope':'representative'})
    for measured in audit.get('exact_followup',{}).get('completed',[]):
        pose=measured['pose']
        if not isinstance(pose,dict): pose=asdict(Pose('supplemental_exact',*pose))
        candidates.append({**measured,'pose':pose,'measurement_scope':'supplemental'})
    valid=[row for row in candidates if row['valid'] and isinstance(row.get('volume_mm3'),(int,float))
           and np.isfinite(row['volume_mm3']) and row['volume_mm3']>1e-6]
    audit['worst_interference']=max(valid,key=lambda row:row['volume_mm3'],default=None)
    return audit['worst_interference']

def audit_home(inputs):
    """Finite intentional 205-to-PARK length path; 205 is not a verified switch."""
    home=[];seed=(0.,0.,0.,0.,0.,0.)
    park=actuator_pin_lengths(Pose('park',0,0,0))
    for index,lengths in enumerate(alternating_length_path(park,(2,1,0))):
        unknown=dict(index=index,commanded_lengths_mm=list(lengths),status='UNKNOWN/HOLD',
            length_window_policy='INTENTIONAL_HOME_205_TO_PARK',**RELEASES)
        try: solution=solve_pose_from_lengths(lengths,seed=seed)
        except (ValueError,ArithmeticError,np.linalg.LinAlgError) as error:
            home.append(dict(unknown,reason='forward closure exception: '+str(error)));continue
        if not solution.converged or not np.isfinite(solution.residual_mm) or solution.residual_mm>1e-7:
            home.append(dict(unknown,reason='forward closure failed'));continue
        pose=Pose(f'home_{index}',solution.lift_mm,solution.pitch_deg,solution.roll_deg)
        _,_,branch=platform_transform(pose)
        residuals={k:abs(getattr(solution,k)-branch[k]) for k in ('x_mm','y_mm','yaw_rad')}
        residuals['yaw_rad']=abs((solution.yaw_rad-branch['yaw_rad']+np.pi)%(2*np.pi)-np.pi)
        radius=max(float(np.linalg.norm(s)) for s in revd_data.upper_support_points())
        residuals['yaw_arc_mm']=residuals['yaw_rad']*radius
        branch_record=dict(cad_branch_residual=residuals,cad_branch_tolerance_mm=1e-7,cad_branch_yaw_radius_mm=radius)
        if any(not np.isfinite(v) for v in residuals.values()) or max(residuals['x_mm'],residuals['y_mm'],residuals['yaw_arc_mm'])>1e-7:
            home.append(dict(unknown,reason='FK solution disagrees with CAD X/Y/yaw branch',**branch_record));continue
        actual=actuator_pin_lengths(pose)
        error=max(abs(a-b) for a,b in zip(actual,lengths))
        if not np.isfinite(error) or error>1e-7:
            home.append(dict(unknown,reason='FK solution disagrees with CAD branch',command_length_residual_mm=error));continue
        row=audit_pose(pose,inputs)
        if row['hinge_constraint_residual_mm']>1e-7:
            home.append(dict(unknown,reason='CAD hinge closure failed'));continue
        seed=solution
        row.update(commanded_lengths_mm=list(lengths),command_length_residual_mm=error,
            **branch_record,
            forward_residual_mm=solution.residual_mm,forward_solution=asdict(solution),
            length_window_policy='INTENTIONAL_HOME_205_TO_PARK',
            home_length_window_pass=all(205.-1e-7<=v<=start+1e-7 for v,start in zip(actual,park)))
        row['kinematic_sample_pass']=row['home_length_window_pass'] and max(row['articulation_deg'])<=13
        home.append(row)
    return home


def audit_all(inputs):
    representatives=[]
    for pose in representative_poses():
        representatives.append(audit_pose(pose,inputs,exact=True))
        print(f'Exact representative {len(representatives)}/27',flush=True)
    dense=[audit_pose(p,inputs) for p in review_poses()]
    # Shared records retain every sampled state and segment membership without
    # repeating geometry for endpoints shared by several command segments.
    states={};segments=[]
    def record(p):
        key=tuple(round(float(v),9) for v in p)
        if key not in states: states[key]=audit_pose(Pose(f'path_{len(states)}',*key),inputs)
        return states[key]['pose']['label']
    for kind,paths in [('PARK',((p,(0.,0.,0.)) for p in dense_pose_grid())),('JOG',_dense_adjacent_jog_segments())]:
        for start,end in paths:
            segments.append(dict(kind=kind,start=start,end=end,samples=[record(p) for p in sample_pose_segment(start,end)]))
        print(f'{kind} paths recorded; unique states {len(states)}',flush=True)
    # Selected finite HOME policy starts from commanded PARK, not arbitrary
    # direct endpoint retraction; interrupted or power-loss starts are HOLD.
    home=audit_home(inputs)
    parts,_,pairs,exemptions=_templates(inputs)
    all_rows=representatives+dense+list(states.values())+home
    result=dict(review_only=True,status='HOLD',bracket_count=3,coordinate_system='lower centre; +X right,+Y front,+Z up; pitch Y,roll X; dependent X/Y/yaw closure',
        unchanged_S_centers=True,continuous_workspace_proven=False,profile_slot_status='UNVERIFIED',
        representative_count=len(representatives),dense_count=len(dense),representatives=representatives,dense=dense,
        path_states=list(states.values()),command_segments=segments,park_segment_count=1859,jog_segment_count=5122,home=home,
        home_scope='PARK then alternating retract order 3,2,1 at <=1 mm samples; arbitrary starts, escape and restart collision audit HOLD',
        pair_catalog=[[parts[i].name,parts[j].name] for i,j in pairs],intentional_interfaces=exemptions,
        broad_phase_margin_mm=MARGIN_MM,exact_followup_policy='27 representatives exact plus deterministic bounded distinct-key follow-up; remaining near pairs UNKNOWN/HOLD',
        invalid_boolean_count=sum(r.get('invalid_boolean_count',0) for r in all_rows),unknown_pair_count=sum(r.get('unknown_pair_count',0) for r in all_rows),
        nominal_clear_representatives=[r['pose'] for r in representatives if r['geometry_status']=='NOMINAL_SAMPLE_CLEAR'],
        worst_articulation=max((r for r in all_rows if 'articulation_deg' in r),key=lambda r:max(r['articulation_deg']))['pose'],
        assembly_path=assembly_path_review(inputs),assembly_status='HOLD; nominal_sample_clear never proves valid Boolean or assembly',
        blockers=list(inputs.unresolved_evidence)+['Near contacts outside representatives await exact Boolean; no full-path clearance claim','Retained lower and intentional interfaces unverified','Manufacturer capacities and delivered tolerances missing','Independent mechanical stops omitted by approved deviation; electrical limits not physical stops','Pin transitions, wrench handle sweep and full assembly access unresolved'],**RELEASES)
    result.update(mount_attachment_review(inputs))
    result['exact_followup']=bounded_followup(result,inputs)
    refresh_invalid_boolean_counts(result)
    result['unknown_pair_count_note']='Baseline broad-phase occurrence count retained for traceability; consult exact_followup distinct-key ledger/backlog for supplemental resolved measurements'
    refresh_worst_interference(result)
    return result
