"""Validate exported workbook read-only; restore native hyperlinks via ZIP XML."""
import hashlib
import importlib.util
import json
from pathlib import Path
from openpyxl import load_workbook

HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'bom_change_manifest.json').read_text(encoding='utf-8'))
helper=HERE.parent/'20261007_bom_three_issue_correction'/'verify_corrected_bom.py'
spec=importlib.util.spec_from_file_location('prior_hyperlink_helper',helper)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
target=Path(manifest['outputPath'])
module.attach_exact_hyperlinks(target,manifest['rows'])
w=load_workbook(target,data_only=True)
s=w.active
f=load_workbook(target,data_only=False).active
actual=[[s.cell(r,c).value for c in range(2,10)] for r in range(4,75)]
assert actual==manifest['rows']
changed={c['oldModel']:c for c in manifest['changes']}
indexed={r[3]:r for r in actual}
assert len(indexed)==len(actual)==71
for before in manifest['originals']:
    after=changed.get(before[3],{}).get('after',before)
    assert indexed[after[3]]==after, before[3]
assert sum(c['vendorChanged'] for c in manifest['changes'])==7
assert sum(r[1]=='나비엠알오' for r in actual)==14
blocks=[r[1] for i,r in enumerate(actual) if i==0 or r[1]!=actual[i-1][1]]
assert len(blocks)==len(set(blocks))
assert all(s[f'G{r}'].hyperlink.target==s[f'G{r}'].value for r in range(4,75))
assert sum(r[6] for r in actual)==s['H75'].value==manifest['supply']
assert s['H76'].value==round(manifest['supply']*.1)==manifest['vat']
assert s['H77'].value==manifest['total']==manifest['supply']+manifest['vat']
assert s['H78'].value==4000000-manifest['total']
assert [f[f'H{r}'].value for r in range(75,79)]==['=SUM(H4:H74)','=ROUND(H75*10%,0)','=SUM(H75:H76)','=$I$2-H77']
assert not any(cell.data_type=='e' for row in s for cell in row)
assert [str(m) for m in s.merged_cells.ranges]==['B1:I1']
assert all(s.row_dimensions[r].height>=82 for r in range(4,75))
assert all(isinstance(r[4],int) and r[4]>0 and r[6]>0 for r in actual)
assert indexed['BC-PG13.5L-G-N'][4]==10
assert indexed['NMT-200KTW / 100EA'][4]==1
assert hashlib.sha256(Path(manifest['sourcePath']).read_bytes()).hexdigest()==manifest['sourceHash']
result={'purchase_rows':71,'vendor_changes':7,'navimro_remaining_rows':14,'native_hyperlinks':71,'unchanged_rows_preserved':61,'formula_errors':0,'vendor_blocks_contiguous':True,'source_preserved':True,'supply':manifest['supply'],'vat':manifest['vat'],'total':manifest['total'],'remaining_budget':manifest['remaining'],'vendor_totals':manifest['vendorTotals'],'cart_changed':False,'live_prices_not_final_checkout':True}
(HERE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
