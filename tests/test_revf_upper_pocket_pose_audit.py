import unittest
from dataclasses import replace
import cadquery as cq
import json
import gzip
import tempfile
from pathlib import Path
import numpy as np
from cad.revf_upper_pocket_inputs import load_inputs
from cad.profile_radial_reve_actual_vendor import Pose
from cad.revf_upper_pocket_pose_audit import review_poses, audit_pose, representative_poses, boolean_measure


class PoseAuditTests(unittest.TestCase):
    def test_audit_all_merges_mount_review_without_duplicate_release_keys(self):
        from unittest.mock import patch
        from contextlib import ExitStack
        from cad import revf_upper_pocket_pose_audit as module
        inputs=load_inputs();pose=Pose('merge_fixture',25,0,0)
        row=audit_pose(pose,inputs)
        # Reduce only sampling/expensive assembly boundaries; exercise the real
        # result construction and real mount subreport with its release flags.
        replacements={'representative_poses':(pose,),'review_poses':(pose,),
            'dense_pose_grid':(), '_dense_adjacent_jog_segments':(),
            'alternating_length_path':(), 'assembly_path_review':{}, 'audit_pose':row}
        with ExitStack() as stack:
            for name,value in replacements.items(): stack.enter_context(patch.object(module,name,return_value=value))
            result=module.audit_all(inputs)
        self.assertEqual(result['crossmember_centering_status'],'ALIGNED_NOMINAL')
        self.assertEqual(result['mount_attachment_status'],'UNKNOWN/HOLD')
        for key in module.RELEASES: self.assertIs(result[key],False)

    def test_grid_has_all_boundaries_without_duplicates(self):
        poses = review_poses()
        self.assertEqual(len(poses), 1859)
        self.assertEqual(len({(p.lift_mm,p.pitch_deg,p.roll_deg) for p in poses}),1859)
        self.assertEqual(len(representative_poses()),27)
        self.assertIn((50.,3.,-3.), {(p.lift_mm,p.pitch_deg,p.roll_deg) for p in poses})

    def test_unverified_slot_cannot_release_even_with_requested_release(self):
        row = audit_pose(Pose('neutral',25,0,0),replace(load_inputs(),purchase_release=True))
        self.assertEqual(row['profile_slot_status'],'UNVERIFIED')
        self.assertIn('invalid_boolean_count',row)
        self.assertFalse(row['purchase_release'])
        self.assertFalse(row['fabrication_release'])
        self.assertEqual(len(row['pin_lengths_mm']),3)
        self.assertEqual(len(row['articulation_deg']),3)
        self.assertGreater(row['pair_count'],100)
        self.assertGreater(row['unknown_pair_count'],0)
        self.assertEqual(row['status'],'HOLD')

    def test_verified_input_flag_cannot_verify_legacy_slot_geometry(self):
        row=audit_pose(Pose('neutral',25,0,0),replace(load_inputs(),profile_slot_verified=True))
        self.assertEqual(row['profile_slot_status'],'UNVERIFIED')

    def test_exact_boolean_detects_volume_and_separation(self):
        box=cq.Workplane('XY').box(2,2,2).val()
        self.assertAlmostEqual(boolean_measure(box,box.translate((1,0,0)))['volume_mm3'],4)
        self.assertEqual(boolean_measure(box,box.translate((4,0,0)))['volume_mm3'],0)

    def test_invalid_input_shape_is_unknown(self):
        row=boolean_measure(None,cq.Workplane('XY').box(1,1,1).val())
        self.assertFalse(row['valid'])
        self.assertIsNone(row['volume_mm3'])

    def test_invalid_zero_volume_common_is_not_clear(self):
        # Boundary double reproduces OCC returning an invalid empty common;
        # the prior assembly checker looked at volume alone.
        class BadCommon:
            def isValid(self): return False
            def Volume(self): return 0.
        class Input:
            def isValid(self): return True
            def intersect(self,other): return BadCommon()
        result=boolean_measure(Input(),Input())
        self.assertFalse(result['valid'])
        self.assertIsNone(result['volume_mm3'])

    def test_packaged_json_keeps_every_path_state(self):
        from scripts.export_revf_upper_pocket_review import write_audit
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            write_audit({'path_states':[{'id':i} for i in range(7)],'purchase_release':False},folder,chunk_size=3)
            index=json.loads((folder/'audit.json').read_text())
            self.assertTrue(all(name.endswith('.json.gz') for name in index['path_state_files']))
            rows=[r for name in index['path_state_files'] for r in json.loads(gzip.decompress((folder/name).read_bytes()))]
            self.assertEqual([r['id'] for r in rows],list(range(7)))
            self.assertFalse(index['purchase_release'])

    def test_transformed_bounds_enclose_actual_corner_pose_solids(self):
        from cad.revf_upper_pocket_pose_audit import _templates, _motion
        from cad.profile_radial_revf_upper_pocket_review import revf_components_for_pose
        inputs=load_inputs(); pose=Pose('corner',50,3,-3)
        parts,corners,_,_=_templates(inputs)
        actual=revf_components_for_pose(pose,inputs)
        for source,local,part in zip(parts,corners,actual):
            r,t=_motion(source,pose);world=local@r.T+t
            low=world.min(axis=0);high=world.max(axis=0)
            bb=part.shape.BoundingBox()
            self.assertTrue(np.all(low<=np.array([bb.xmin,bb.ymin,bb.zmin])+1e-5),part.name)
            self.assertTrue(np.all(high>=np.array([bb.xmax,bb.ymax,bb.zmax])-1e-5),part.name)

    def test_corrected_mount_centering_does_not_verify_actual_slot(self):
        from cad.revf_upper_pocket_pose_audit import mount_attachment_review
        result=mount_attachment_review(load_inputs())
        self.assertEqual(result['mount_attachment_status'],'UNKNOWN/HOLD')
        self.assertEqual(result['crossmember_centering_status'],'ALIGNED_NOMINAL')
        self.assertEqual(result['actual_slot_fit_status'],'UNKNOWN')
        self.assertAlmostEqual(result['legacy_slot_floor_overlap_mm'],.6)
        self.assertEqual(len(result['mount_attachment_measurements']),6)
        for row in result['mount_attachment_measurements']:
            self.assertTrue(row['nominal_crossmember_centered'])
            self.assertAlmostEqual(row['platform_center_y_mm'],0.,places=5)
            self.assertAlmostEqual(abs(row['platform_center_x_mm']),22.,places=5)
        self.assertFalse(result['purchase_release'])

    def test_three_local_bracket_exports_are_reimported_with_provenance(self):
        from scripts.export_revf_upper_pocket_review import export_bracket_parts, measurement_provenance
        provenance=measurement_provenance(load_inputs())
        with tempfile.TemporaryDirectory() as folder:
            records=export_bracket_parts(load_inputs(),Path(folder),provenance)
            self.assertEqual([r['axis'] for r in records],[1,2,3])
            for row in records:
                path=Path(folder)/row['path'];shape=cq.importers.importStep(str(path)).val()
                self.assertTrue(shape.isValid());self.assertEqual(len(shape.Solids()),1)
                self.assertLess(path.stat().st_size,10_000_000)
                self.assertAlmostEqual(shape.Volume(),row['source_volume_mm3'],places=4)
                self.assertEqual(row['measurement_fingerprint'],provenance['fingerprint'])
                self.assertEqual(row['geometry_sha256'],provenance['source_hashes']['cad/profile_radial_revf_upper_pocket_review.py'])
                self.assertIn('local',row['coordinate_system'])
                self.assertFalse(row['fabrication_release']);self.assertFalse(row['purchase_release'])
                self.assertEqual(len(row['reimport_bbox_mm']),6)

    def test_bounded_followup_executes_and_resumes_distinct_real_pairs(self):
        from cad.revf_upper_pocket_pose_audit import bounded_followup
        inputs=load_inputs()
        row=audit_pose(Pose('dense',10,1,1),inputs)
        path=audit_pose(Pose('path',11,1,1),inputs)
        home=audit_pose(Pose('home',-1,0,0),inputs)
        audit={'representatives':[],'dense':[row],'path_states':[path],'home':[home]}
        first=bounded_followup(audit,inputs,budget=3)
        self.assertEqual(len(first['completed']),3)
        self.assertEqual({r['scope'] for r in first['completed']},{'dense','command','home'})
        self.assertTrue(all('valid' in r and 'volume_mm3' in r for r in first['completed']))
        self.assertGreater(first['backlog_distinct_keys'],0)
        second=bounded_followup(audit,inputs,budget=3,previous=first)
        self.assertEqual(len(second['completed']),6)
        self.assertEqual(len({r['key'] for r in second['completed']}),6)
        self.assertEqual(second['backlog_distinct_keys'],first['backlog_distinct_keys']-3)
        self.assertEqual(second['status'],'HOLD')

    def test_repackage_rejects_changed_or_missing_measurement_provenance(self):
        from scripts.export_revf_upper_pocket_review import measurement_provenance, validate_reuse
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'shape.txt').write_text('original')
            provenance=measurement_provenance(load_inputs(),root=root,sources=('shape.txt',))
            audit={'measurement_provenance':provenance,'measurement_id':'original-run'}
            validate_reuse(audit,provenance)
            (root/'shape.txt').write_text('changed')
            changed=measurement_provenance(load_inputs(),root=root,sources=('shape.txt',))
            with self.assertRaisesRegex(ValueError,'provenance'): validate_reuse(audit,changed)
            with self.assertRaisesRegex(ValueError,'provenance'): validate_reuse({},provenance)
            self.assertEqual(audit['measurement_provenance'],provenance)
            self.assertEqual(audit['measurement_id'],'original-run')
            with self.assertRaisesRegex(ValueError,'identity'):
                validate_reuse({'measurement_provenance':provenance},provenance)

    def test_uncovered_pair_precedes_known_failed_representative_pair(self):
        from cad.revf_upper_pocket_pose_audit import bounded_followup
        inputs=load_inputs();row=audit_pose(Pose('candidate',10,1,1),inputs)
        known,uncovered=row['near_pair_indices'][:2]
        row['near_pair_indices']=[known,uncovered]
        rep={'pose':{'lift_mm':0,'pitch_deg':0,'roll_deg':0},'exact_measurements':[{'pair_indices':known,'valid':False,'volume_mm3':None}]}
        result=bounded_followup({'representatives':[rep],'dense':[row],'path_states':[],'home':[]},inputs,budget=1)
        self.assertEqual(result['completed'][0]['pair_indices'],uncovered)
        self.assertTrue(result['completed'][0]['representative_uncovered'])

    def test_followup_deduplicates_scope_overlap_and_chooses_lowest_margin(self):
        from cad.revf_upper_pocket_pose_audit import bounded_followup
        inputs=load_inputs()
        low=audit_pose(Pose('low',10,1,1),inputs)
        high=audit_pose(Pose('high',20,1,1),inputs)
        pair=low['near_pair_indices'][0]
        low['near_pair_indices']=[pair];high['near_pair_indices']=[pair]
        audit={'representatives':[],'dense':[high,low],'path_states':[low],'home':[]}
        result=bounded_followup(audit,inputs,budget=1)
        self.assertEqual(result['completed'][0]['pose'],[10,1,1])
        self.assertEqual(result['backlog_distinct_keys'],1)

    def test_provenance_detects_changed_input_values(self):
        from scripts.export_revf_upper_pocket_review import measurement_provenance, validate_reuse
        original=measurement_provenance(load_inputs(),sources=())
        changed=measurement_provenance(replace(load_inputs(),eye_offset_mm=17),sources=())
        with self.assertRaisesRegex(ValueError,'provenance'):
            validate_reuse({'measurement_id':'same','measurement_provenance':original},changed)

    def test_followup_normalizes_integer_and_float_pose_keys(self):
        from cad.revf_upper_pocket_pose_audit import bounded_followup
        row=audit_pose(Pose('integer',0,0,0),load_inputs())
        pair=row['near_pair_indices'][0];row['near_pair_indices']=[pair]
        rep={'pose':{'lift_mm':0.0,'pitch_deg':0.0,'roll_deg':0.0},'exact_measurements':[{'pair_indices':pair,'valid':True,'volume_mm3':0.0}]}
        result=bounded_followup({'representatives':[rep],'dense':[row],'path_states':[],'home':[]},load_inputs(),budget=1)
        self.assertEqual(result['attempted_this_run'],0)
        self.assertEqual(result['backlog_distinct_keys'],0)

    def test_supplemental_worst_drives_export_after_continue_and_repackage(self):
        from scripts.export_revf_upper_pocket_review import review_export_poses
        audit={'representatives':[{'pose':{'label':'representative','lift_mm':0.,'pitch_deg':0.,'roll_deg':0.},
                'exact_measurements':[{'valid':True,'volume_mm3':2.,'pair':['rep_a','rep_b'],'pair_indices':[1,2]}]}],
            'exact_followup':{'completed':[{'valid':True,'volume_mm3':10.,'pose':[30.,1.,-1.],'pair':['new_a','new_b'],'pair_indices':[3,4]},
                                         {'valid':False,'volume_mm3':1000.,'pose':[50.,3.,3.],'pair':['invalid','bad'],'pair_indices':[5,6]}]},
            'worst_articulation':None,'status':'HOLD','purchase_release':False,'fabrication_release':False,'measurement_id':'preserved'}
        poses=review_export_poses(audit)
        self.assertEqual(audit['worst_interference']['volume_mm3'],10.)
        self.assertEqual(audit['worst_interference']['pair'],['new_a','new_b'])
        self.assertEqual(next(p for p in poses if p.label=='worst_interference').lift_mm,30.)
        # A resumed batch appends a larger witness; the common export seam
        # must update the summary rather than reuse its previously saved value.
        audit['exact_followup']['completed'].append({'valid':True,'volume_mm3':20.,'pose':[40.,2.,-2.],'pair':['later_a','later_b'],'pair_indices':[7,8]})
        continued=review_export_poses(audit)
        self.assertEqual(next(p for p in continued if p.label=='worst_interference').lift_mm,40.)
        repackaged=json.loads(json.dumps(audit));repacked=review_export_poses(repackaged)
        self.assertEqual(repackaged['worst_interference']['pair'],['later_a','later_b'])
        self.assertEqual(continued,repacked)
        self.assertEqual(repackaged['measurement_id'],'preserved')
        self.assertEqual(repackaged['status'],'HOLD')
        self.assertFalse(repackaged['purchase_release'])
        self.assertFalse(repackaged['fabrication_release'])

    def test_pair_export_contains_only_requested_named_parts(self):
        from scripts.export_revf_upper_pocket_review import export_pose
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            export_pose(Pose('pair_fixture',25.,0.,0.),destination=folder,part_indices=[3,25])
            shape=cq.importers.importStep(str(folder/'pair_fixture.step')).val()
            self.assertTrue(shape.isValid())
            self.assertLess(len(shape.Solids()),118)
            self.assertGreater((folder/'pair_fixture.png').stat().st_size,1000)
            text=(folder/'pair_fixture.step').read_text()
            self.assertIn('A1_REVF_tnut_1_UNVERIFIED_SLOT',text)
            self.assertNotIn('A2_REVF_',text)

if __name__=='__main__': unittest.main()
