import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const [mode, sourcePath, outputDir] = process.argv.slice(2);
if (!mode || !sourcePath || !outputDir) throw new Error('mode, sourcePath and outputDir are required');

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sheet = workbook.worksheets.getItem('Sheet1');
await fs.mkdir(outputDir, { recursive: true });

if (mode === 'inspect') {
  console.log('import H64:H65', JSON.stringify(sheet.getRange('H64:H65').values));
  const info = await workbook.inspect({ kind: 'region', sheetId: 'Sheet1', range: 'B33:I70', maxChars: 6000 });
  console.log(info.ndjson);
  console.log(workbook.help('hyperlink', { include: 'index,examples,notes', maxChars: 3500 }).ndjson);
  const before = await workbook.render({ sheetName: 'Sheet1', range: 'B32:I41', scale: 1.4, format: 'png' });
  await fs.writeFile(path.join(outputDir, 'before.png'), new Uint8Array(await before.arrayBuffer()));
  process.exit(0);
}

if (mode === 'verify') {
  workbook.recalculate();
  const errors = await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 100 }, summary: 'formula error scan' });
  console.log(errors.ndjson);
  console.log('totals', JSON.stringify(sheet.getRange('H68:H71').values));
  for (const [name, range] of [['after', 'B33:I40'], ['totals', 'B66:I71']]) {
    const preview = await workbook.render({ sheetName: 'Sheet1', range, scale: 1.4, format: 'png' });
    await fs.writeFile(path.join(outputDir, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
  }
  process.exit(0);
}

if (mode !== 'edit') throw new Error(`Unknown mode ${mode}`);

// Move the supplier groups and totals two rows down. Bottom-up copying avoids
// reading cells that have already been replaced. Rebuild total formulas below.
const originalQuantities = sheet.getRange('F37:F65').values;
const originalAmounts = sheet.getRange('H37:H65').values;
const originalUrls = sheet.getRange('G37:G65').values.map(([url]) => String(url));
for (let row = 69; row >= 37; row--) {
  const destination = sheet.getRange(`B${row + 2}:I${row + 2}`);
  destination.clear({ applyTo: 'contents' });
  destination.copyFrom(sheet.getRange(`B${row}:I${row}`), 'all');
}
sheet.getRange('F39:F67').values = originalQuantities;
sheet.getRange('H39:H67').values = originalAmounts;

sheet.getRange('B37:I37').copyFrom(sheet.getRange('B36:I36'), 'all');
sheet.getRange('B38:I38').copyFrom(sheet.getRange('B36:I36'), 'all');
sheet.getRange('B37:I38').values = [
  [
    '재료비 구매', '나비엠알오', 'HSS 금속용 드릴 Ø6.8 mm', 'SD 6.8 / K11176399', 1,
    'https://m.navimro.com/g/171100/', 2090,
    'T01. M8×1.25 절삭탭 밑구멍용. A1~A3 직접 가공 시에만 구매. 1EA, VAT 별도 화면가 2,090원. 탭 종류·드릴 척 확인.'
  ],
  [
    '재료비 구매', '나비엠알오', 'HSS 금속용 드릴 Ø9.0 mm', 'D1101090 / K01216966', 1,
    'https://m.navimro.com/g/66938/', 21990,
    'T02. M8 클리어런스 홀용. A1~A3 직접 가공 시에만 구매. 1PK(5EA), VAT 별도 화면가 21,990원. 소량 낱개 대체는 미확인.'
  ],
];

const urls = [
  'https://m.navimro.com/g/171100/',
  'https://m.navimro.com/g/66938/',
  ...originalUrls,
];
const urlRange = sheet.getRange('G37:G67');
urlRange.clear({ applyTo: 'all' });
urlRange.formulas = urls.map((url) => {
  const safeUrl = url.replaceAll('"', '""');
  return [`=HYPERLINK("${safeUrl}","${safeUrl}")`];
});
urlRange.format.font = { name: 'Arial', size: 10, color: '#0563C1' };

// Prices are supply amounts, matching the existing quotation. The drills are
// listed as a conditional self-machining option and excluded from the base total
// while C01-C03 remain supplier-machined parts in this quotation.
sheet.getRange('B68').values = [['공급가액 소계 (업체 가공안)']];
sheet.getRange('H68').formulas = [['=SUM(H4:H36,H39:H67)']];
sheet.getRange('B69').values = [['부가세 (10%)']];
sheet.getRange('H69').formulas = [['=ROUND(H68*10%,0)']];
sheet.getRange('B70').values = [['총 액 (부가세 포함)']];
sheet.getRange('H70').formulas = [['=SUM(H68:H69)']];
sheet.getRange('B71').values = [['잔 액']];
sheet.getRange('H71').formulas = [['=$I$2-H70']];
sheet.getRange('I71').values = [['드릴 2종은 A1~A3 직접 가공 대안용이며 현재 업체 가공안 합계에서 제외. 직접 가공 결정 시 가공 견적을 교체하고 드릴비를 반영.']];

workbook.recalculate();
const check = await workbook.inspect({ kind: 'region', sheetId: 'Sheet1', range: 'B33:I71', maxChars: 8000 });
console.log(check.ndjson);
const errors = await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 100 }, summary: 'final formula error scan' });
console.log(errors.ndjson);
const after = await workbook.render({ sheetName: 'Sheet1', range: 'B33:I40', scale: 1.4, format: 'png' });
await fs.writeFile(path.join(outputDir, 'after.png'), new Uint8Array(await after.arrayBuffer()));
const totals = await workbook.render({ sheetName: 'Sheet1', range: 'B66:I71', scale: 1.4, format: 'png' });
await fs.writeFile(path.join(outputDir, 'totals.png'), new Uint8Array(await totals.arrayBuffer()));
const out = await SpreadsheetFile.exportXlsx(workbook);
await out.save(path.join(outputDir, '2026_BIZ-Lab_창업클럽_시제품_재료비관리_드릴비트_추가.xlsx'));
