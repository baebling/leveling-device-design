import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20260927_drill_quote', '2026_BIZ-Lab_창업클럽_시제품_재료비관리_드릴비트_추가.xlsx');
const outDir = path.join(root, 'outputs', '20260930_misumi_plate_bom');
const destination = path.join(outDir, '2026_BIZ-Lab_창업클럽_시제품_재료비관리_미스미판재_반영.xlsx');
const link = 'https://kr.misumi-ec.com/vona2/detail/110302243870/?ProductCode=A6061LNN-120-70-8';

await fs.mkdir(outDir, { recursive: true });
const book = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheet = book.worksheets.getItem('Sheet1');

// Preserve the grant template and its seller ordering; only replace C01-C03.
for (const [row, plate] of [[60, 'A1'], [61, 'A2'], [62, 'A3']]) {
  if (sheet.getRange(`H${row}`).values[0][0] !== 45455) {
    throw new Error(`Unexpected prior plate price in H${row}`);
  }
  sheet.getRange(`D${row}`).values = [[`${plate} 하부 어댑터용 알루미늄 판재 120×70×8 mm`]];
  sheet.getRange(`E${row}`).values = [['A6061LNN-120-70-8']];
  sheet.getRange(`G${row}`).values = [[link]];
  sheet.getRange(`H${row}`).values = [[21310]];
  sheet.getRange(`I${row}`).values = [[`C0${row - 59}. 9/30 미스미 장바구니가. ${plate} 홀·탭 직접 가공. 소재·배송비 확인.`]];
}

// The drill rows were already in this version, but excluded as an alternative to outsourcing.
// They are now part of the selected self-machining route.
sheet.getRange('B68').values = [['공급가액 소계 (판재 직접 가공안)']];
sheet.getRange('H68').formulas = [['=SUM(H4:H67)']];
sheet.getRange('I71').values = [['판재 3장·드릴 2종 반영. 미결제·배송비 미확인.']];

book.recalculate();
const check = await book.inspect({ kind: 'region', sheetId: 'Sheet1', range: 'B59:I71', maxChars: 5000, tableMaxRows: 15, tableMaxCols: 8 });
console.log(JSON.stringify(check));

try {
  const preview = await book.render({ sheetName: 'Sheet1', range: 'B59:I71', scale: 1, format: 'png' });
  await fs.writeFile(path.join(outDir, 'plate_bom_preview.png'), new Uint8Array(await preview.arrayBuffer()));
} catch (error) {
  console.warn(`Preview unavailable: ${error.message}`);
}

const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(destination);
console.log(`Saved ${destination}`);
