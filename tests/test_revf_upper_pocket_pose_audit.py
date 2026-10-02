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

    def test_mounts_require_material_engagement_not_merely_no_collision(self):
        from cad.revf_upper_pocket_pose_audit import mount_attachment_review
        result=mount_attachment_review(load_inputs())
        self.assertEqual(result['mount_attachment_status'],'INVALID_NOMINAL_PLACEMENT_ACTUAL_SLOT_UNVERIFIED')
        self.assertEqual(len(result['mount_attachment_measurements']),6)
        self.assertGreater(result['mount_attachment_measurements'][0]['gap_mm'],3.9)
        self.assertGreater(result['mount_attachment_measurements'][2]['volume_mm3'],200)

if __name__=='__main__': unittest.main()
