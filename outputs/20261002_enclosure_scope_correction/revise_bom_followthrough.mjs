import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20261002_enclosure_scope_correction',
  '2026_BIZ-Lab_재료비관리_RevE_가공범위정정.xlsx');
const outdir = path.join(root, 'outputs', '20261002_reve_followthrough');
const dest = path.join(outdir, '2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx');

const book = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheet = book.worksheets.getItem('Sheet1');
const get = address => sheet.getRange(address).values[0][0];
const guards = {
  I17: 'F08A.', I24: 'E06.', I38: 'E09A.', I42: 'E13.',
  I45: 'E22.', I54: 'F20.', I66: 'F11.',
};
for (const [address, prefix] of Object.entries(guards)) {
  if (!String(get(address)).startsWith(prefix)) {
    throw new Error(`${address} row identity changed; refusing to edit`);
  }
}
const before = sheet.getRange('A1:I74').values;
const totalsBefore = ['H71', 'H72', 'H73', 'H74'].map(get);
for (const [name, range] of [
  ['bom_before_joint.png', 'B63:I67'],
  ['bom_before_enclosure.png', 'B22:I25'],
]) {
  const blob = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outdir, name), new Uint8Array(await blob.arrayBuffer()));
}

const notes = {
  I17: 'F08A. 해외직수입·강도등급 미확인. Ø6 편심핀 하중경로 미승인. 주문 보류.',
  I24: 'E06. 현 SL902 내부치수 미상. BOXCO 507025+5070 P 검토 후보, 발주 보류.',
  I38: 'E09A. 현 홀더 DC 정격 미상·주문 금지. 01550300Z(32V/20A) 검토 후보.',
  I42: 'E13. 현 START DC 정격 미상. KGF-CM1G(10894246) 후보, 발주 보류.',
  I45: 'E22. 1m 금속 레일 절단 불가. 미스미 MRB-300 완제품 후보, 발주 보류.',
  I54: 'F20. RSP 바닥 M4 침투≤4mm, 측면≤6mm. 적층 치수 확인 전 사용 보류.',
  I66: 'F11. M6×25 너트 물림≤3.5mm·외면 4mm 공극. 체결 불가, 주문 금지.',
};
for (const [address, value] of Object.entries(notes)) {
  sheet.getRange(address).values = [[value]];
}
book.recalculate();
const after = sheet.getRange('A1:I74').values;
const changed = [];
for (let row = 0; row < before.length; row++) {
  for (let col = 0; col < 9; col++) {
    if (JSON.stringify(before[row][col]) !== JSON.stringify(after[row][col])) {
      changed.push(`${String.fromCharCode(65 + col)}${row + 1}`);
    }
  }
}
const expected = Object.keys(notes).sort();
if (JSON.stringify(changed.sort()) !== JSON.stringify(expected)) {
  throw new Error(`Unexpected workbook changes: ${changed.join(', ')}`);
}
const totalsAfter = ['H71', 'H72', 'H73', 'H74'].map(get);
if (JSON.stringify(totalsBefore) !== JSON.stringify(totalsAfter)) {
  throw new Error('BOM totals changed when only review notes were edited');
}
const errors = await book.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: {useRegex: true, maxResults: 100},
  summary: 'followthrough formula error scan',
});
await fs.writeFile(path.join(outdir, 'bom_formula_errors.ndjson'), errors.ndjson);
for (const [name, range] of [
  ['bom_after_joint.png', 'B63:I67'],
  ['bom_after_enclosure.png', 'B22:I25'],
  ['bom_after_electrical.png', 'B36:I45'],
  ['bom_after_f20.png', 'B52:I55'],
]) {
  const blob = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outdir, name), new Uint8Array(await blob.arrayBuffer()));
}
const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(dest);
await fs.writeFile(path.join(outdir, 'bom_note_change_validation.json'),
  JSON.stringify({source, dest, changed, totalsBefore, totalsAfter}, null, 2));
console.log(JSON.stringify({dest, changed, totalsAfter, errorScan: errors.ndjson.slice(0, 200)}));
