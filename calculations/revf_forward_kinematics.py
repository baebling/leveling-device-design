"""Rev F six-equation FK: eye offset follows the world-fixed hinge tangent.

Legacy Rev E FK/results are intentionally unchanged. Units mm/degrees/radians.
"""
import numpy as np
from calculations.reve_forward_kinematics import PoseSolution
from fusion_scripts.ProfileRadialRevD import revd_data


def residual(values, target_lengths_mm):
    x,y,lift,pitch,roll,yaw=values
    rotation=np.array(revd_data.rotation_matrix(pitch,roll,yaw))
    lengths=[];hinges=[]
    for lower,support,(_,tangent),target in zip(revd_data.lower_eye_points(),
            revd_data.upper_support_points(),revd_data.support_basis(),target_lengths_mm):
        eye=rotation@np.array([support[0],support[1],0.])+np.array([x,y,revd_data.P.upper_ring_z_collapsed_mm+lift])-revd_data.P.upper_joint_side_offset_mm*np.array(tangent)
        actuator=eye-np.array(lower)
        lengths.append(float(np.linalg.norm(actuator))-target)
        hinges.append(float(np.dot(actuator,tangent)))
    return np.array(lengths+hinges)


def solve_pose_from_lengths(lengths_mm,seed=(0.,0.,25.,0.,0.,0.),*,tolerance_mm=1e-8,max_iterations=30):
    """Newton solve lengths + hinge constraints; failure stays nonconverged."""
    target=tuple(float(v) for v in lengths_mm)
    values=np.array(seed.as_seed() if isinstance(seed,PoseSolution) else seed,dtype=float)
    if len(target)!=3 or not all(np.isfinite(v) and v>0 for v in target):
        raise ValueError('three finite positive target lengths required')
    if values.shape!=(6,) or not np.all(np.isfinite(values)):
        raise ValueError('six finite seed coordinates required')
    if tolerance_mm<=0 or max_iterations<0: raise ValueError('invalid solver bounds')
    steps=(1e-4,1e-4,1e-4,1e-5,1e-5,1e-7)
    converged=False
    for iteration in range(max_iterations+1):
        current=residual(values,target)
        if not np.all(np.isfinite(current)): break
        if max(abs(current))<=tolerance_mm: converged=True;break
        if iteration==max_iterations: break
        columns=[]
        for axis,step in enumerate(steps):
            shifted=values.copy();shifted[axis]+=step
            columns.append((residual(shifted,target)-current)/step)
        try: delta=np.linalg.solve(np.array(columns).T,-current)
        except np.linalg.LinAlgError: break
        if not np.all(np.isfinite(delta)): break
        values+=delta
    error=float(max(abs(residual(values,target))))
    return PoseSolution(*map(float,values),residual_mm=error,iterations=iteration,
        converged=bool(converged and np.isfinite(error)),target_lengths_mm=target)
