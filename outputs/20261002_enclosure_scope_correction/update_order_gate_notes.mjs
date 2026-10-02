import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root = process.cwd();
const outdir = path.join(root, 'outputs', '20261002_reve_followthrough');
const workbookPath = path.join(outdir, '2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx');
const book = await SpreadsheetFile.importXlsx(await FileBlob.load(workbookPath));
const sheet = book.worksheets.getItem('Sheet1');
const get = address => sheet.getRange(address).values[0][0];
const guards = {I26: 'E08.', I41: 'E10.', I57: 'M02.'};
for (const [address, prefix] of Object.entries(guards)) {
  if (!String(get(address)).startsWith(prefix)) {
    throw new Error(`${address} row identity changed; refusing to edit`);
  }
}

async function renderRegions(stage) {
  for (const [key, range] of [
    ['e08', 'C25:I27'],
    ['e10', 'C40:I43'],
    ['m02', 'C55:I58'],
  ]) {
    const blob = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
    await fs.writeFile(path.join(outdir, `bom_${stage}_${key}.png`),
      new Uint8Array(await blob.arrayBuffer()));
  }
}

await renderRegions('before_gate');
if (process.argv.includes('--before-only')) {
  console.log(JSON.stringify({workbookPath, beforeRendered: true,
    rows: Object.fromEntries(Object.keys(guards).map(address => [address, get(address)]))}));
  process.exit(0);
}

const before = sheet.getRange('A1:I74').values;
const formulasBefore = sheet.getRange('H71:H74').formulas;
const totalsBefore = ['H71', 'H72', 'H73', 'H74'].map(get);
const drawingBefore = await book.inspect({kind: 'drawing', sheetId: 'Sheet1'});
const drawingRecords = drawingBefore.ndjson.split('\n').filter(Boolean).map(line => JSON.parse(line))
  .filter(record => record.kind === 'drawing');
if (drawingRecords.length > 1 || (drawingRecords.length === 1 &&
    (drawingRecords[0].name !== 'Text Box 2' ||
     drawingRecords[0].drawingType !== 'shape' || drawingRecords[0].anchor?.from?.row !== 0 ||
     drawingRecords[0].anchor?.to?.row !== 26))) {
  throw new Error(`Unexpected drawing set; refusing deletion: ${drawingBefore.ndjson}`);
}
const notes = {
  I26: 'E08. 출하표시 10/06과 배송까지 3개월 이상 가능 경고가 상충. 11월 말 일정용 확정 납기 아님. 실제 납기·보호곡선 확인 전 발주 보류.',
  I41: 'E10. 현재 STOP 스위치의 직접개리·DC-13 정격 미확인. 24 V 접촉기 코일 차단용 승인 전까지 주문·통전 보류.',
  I57: 'M02. 사진에는 핀·R클립이 보이나 단일옵션 동봉 수량 미명시. 3세트 각 1조 확보, 눈홀 판매도면 Ø6.4/STEP Ø6.0 불일치·측면 유격 확인 전 조립 보류.',
};
const expectedChanges = Object.entries(notes).filter(([address, value]) => get(address) !== value)
  .map(([address]) => address).sort();
for (const [address, value] of Object.entries(notes)) {
  sheet.getRange(address).values = [[value]];
}
// The only drawing is an empty white textbox from A1 through row 27; it obscures BOM rows.
if (drawingRecords.length === 1) sheet.deleteAllDrawings();
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
if (JSON.stringify(changed.sort()) !== JSON.stringify(expectedChanges)) {
  throw new Error(`Unexpected workbook changes: ${changed.join(', ')}`);
}
const totalsAfter = ['H71', 'H72', 'H73', 'H74'].map(get);
if (JSON.stringify(totalsAfter) !== JSON.stringify(totalsBefore)) {
  throw new Error('Totals changed in note-only edit');
}
if (JSON.stringify(sheet.getRange('H71:H74').formulas) !== JSON.stringify(formulasBefore)) {
  throw new Error('Total formulas changed in note-only edit');
}
const errors = await book.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: {useRegex: true, maxResults: 100},
  summary: 'order gate note formula error scan',
});
if (!errors.ndjson.includes('matched 0 entries')) {
  throw new Error(`Formula error scan failed: ${errors.ndjson}`);
}
await renderRegions('after_gate');
const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(workbookPath);
const saved = await SpreadsheetFile.importXlsx(await FileBlob.load(workbookPath));
const savedSheet = saved.worksheets.getItem('Sheet1');
if (JSON.stringify(savedSheet.getRange('A1:I74').values) !== JSON.stringify(after) ||
    JSON.stringify(savedSheet.getRange('H71:H74').formulas) !== JSON.stringify(formulasBefore)) {
  throw new Error('Saved workbook reimport differs from expected values or formulas');
}
const drawingAfter = await saved.inspect({kind: 'drawing', sheetId: 'Sheet1'});
const drawingAfterRecords = drawingAfter.ndjson.split('\n').filter(Boolean).map(line => JSON.parse(line))
  .filter(record => record.kind === 'drawing');
if (drawingAfterRecords.length !== 0) {
  throw new Error(`Obscuring drawing survived export: ${drawingAfter.ndjson}`);
}
const validation = {workbookPath, changed, totalsBefore, totalsAfter,
  drawingRemoved: drawingRecords.length === 1 ? drawingRecords[0].name : 'already absent',
  formulaErrors: 0, savedWorkbookReimported: true};
await fs.writeFile(path.join(outdir, 'bom_order_gate_note_validation.json'),
  JSON.stringify(validation, null, 2));
console.log(JSON.stringify(validation));
