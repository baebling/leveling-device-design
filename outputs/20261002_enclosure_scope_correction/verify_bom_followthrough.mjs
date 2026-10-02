import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20261002_enclosure_scope_correction',
  '2026_BIZ-Lab_재료비관리_RevE_가공범위정정.xlsx');
const dest = path.join(root, 'outputs', '20261002_reve_followthrough',
  '2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx');
const [aBook, bBook] = await Promise.all([
  SpreadsheetFile.importXlsx(await FileBlob.load(source)),
  SpreadsheetFile.importXlsx(await FileBlob.load(dest)),
]);
const a = aBook.worksheets.getItem('Sheet1');
const b = bBook.worksheets.getItem('Sheet1');
const aValues = a.getRange('A1:I74').values;
const bValues = b.getRange('A1:I74').values;
const changed = [];
for (let row = 0; row < aValues.length; row++) {
  for (let col = 0; col < 9; col++) {
    if (JSON.stringify(aValues[row][col]) !== JSON.stringify(bValues[row][col])) {
      changed.push(`${String.fromCharCode(65 + col)}${row + 1}`);
    }
  }
}
const expected = ['I17', 'I24', 'I38', 'I42', 'I45', 'I54', 'I66'];
if (JSON.stringify(changed) !== JSON.stringify(expected)) {
  throw new Error(`Saved workbook has unexpected changed cells: ${changed.join(', ')}`);
}
const formulasA = a.getRange('H71:H74').formulas;
const formulasB = b.getRange('H71:H74').formulas;
if (JSON.stringify(formulasA) !== JSON.stringify(formulasB)) {
  throw new Error('Saved workbook total formulas changed');
}
const total = b.getRange('H73').values[0][0];
const balance = b.getRange('H74').values[0][0];
if (total !== 3143564 || balance !== 856436) {
  throw new Error(`Unexpected calculated totals: ${total}, ${balance}`);
}
const errors = await bBook.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: {useRegex: true, maxResults: 100},
  summary: 'saved followthrough workbook formula error scan',
});
if (!errors.ndjson.includes('matched 0 entries')) {
  throw new Error(`Saved workbook formula error scan: ${errors.ndjson}`);
}
console.log(JSON.stringify({changed, total, balance, formulasIntact: true,
  formulaErrors: 0, savedWorkbookReimported: true}));
