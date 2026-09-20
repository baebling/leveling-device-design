"""Catalogue dimensional stack checks, NOT joint strength certification."""
from pathlib import Path
import json
from math import pi
ROOT=Path(__file__).resolve().parents[1]

def main():
    rows=[]
    for name,L,grip,washer,count in [('M5x16',16,6,1,24),('M8x15',15,6,0,48)]:
        penetration=L-grip-washer
        start=5.5-3 # profile lip minus HNTT8 raised boss
        rows.append({'bolt':name,'count':count,'penetration_mm':penetration,
            'nominal_thread_overlap_mm':penetration-start,'slot_floor_clearance_mm':12.5-penetration,
            'tolerance_sensitivity_thread_overlap_min_mm':penetration-start-.2-.2-(.1 if washer else 0)-.2-.1,
            'tolerance_sensitivity_floor_clearance_min_mm':12.5-penetration-.2-.2-.2-(.1 if washer else 0),
            'passes_nominal_geometry':penetration>start and penetration<12.5})
    r={'revision':'M2R2-S220','scope':'catalogue dimensions and assumed tolerance sensitivity; no clamp force or slip capacity certification',
       'bolts':rows,'support_slot_contact':{'foot_width_mm':14,'slot_opening_mm':10,'nominal_land_each_side_mm':2,
          'rectangular_contact_area_mm2':42*(14-10),'sensitivity_land_each_side_mm':(13.8-10.2)/2-.35,
          'washer_OD_previous_mm':10,'washer_OD_selected_mm':9,'washer_outer_edge_margin_mm':21-16-9/2,
          'washer_bearing_area_over_5_5_hole_mm2':pi/4*(9**2-5.5**2),
          'load_capacity_status':'NOT VERIFIED; narrow contact strips and slot lip bending require confirmation'},
       'bracket_clearance':{'rear_crossmember_clear_gap_mm':90-2*40,'rear_rail_y_mm':-180,'front_rail_cut_length_mm':450,'rear_shat12_pair_foot_clearance_mm':18},
       'tolerance_assumptions':'Sensitivity only: bolt length +/-0.2, foot/bracket +/-0.2, washer +/-0.1, lip/floor +/-0.2, nut boss +/-0.1; foot14 +/-0.2, slot10 +/-0.2, lateral misalignment0.35. Not certified supplier tolerance bounds.',
       'limits':['Thread overlap includes unfinished thread ends; effective thread engagement and torque need supplier confirmation','No torque value invented from nominal geometry','Catalogue-matched HNTT8 and HFS8 establishes interface family; underside tapers remain schematic in CAD']}
    assert all(x['passes_nominal_geometry'] for x in rows)
    out=ROOT/'outputs/manual_turnbuckle_rev_m2r2s220/FASTENING_STACK_AUDIT.json'
    out.write_text(json.dumps(r,indent=2),encoding='utf-8')
    print('DIMENSIONAL_STACK_PASS; STRENGTH_NOT_VERIFIED')

if __name__=='__main__':main()
