import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
const sourcePath = path.resolve(here, '../20261003_revf_order_candidate/2026_BIZ-Lab_재료비관리_RevF_발주후보.xlsx');
const outputPath = path.resolve(here, '2026_BIZ-Lab_재료비관리_RevF_meviy견적반영_2026-10-04.xlsx');

const source = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sourceRows = source.worksheets.getItemAt(0).getRange('B4:I71').values;
if (sourceRows.length !== 68) throw new Error(`Expected 68 original purchase rows, found ${sourceRows.length}`);

const removedModels = new Set([
  'K14536539', // M6 nylon nut: no longer used in the retained joint stack
  'SD 6.8 / K11176399', // machining is included in meviy quotation
  'D1101090 / K01216966',
  'UP-A1 / STEP 견적', 'UP-A2 / STEP 견적', 'UP-A3 / STEP 견적',
  'A6061LNN-120-70-8', // blank plates replaced by finished tapped parts
]);
const retained = sourceRows.filter(row => !removedModels.has(row[3]));
if (retained.length !== 59) throw new Error(`Expected 59 retained purchase rows, found ${retained.length}`);

for (const row of retained) {
  if (row[3] === 'E-SPN306') row[7] = 'F07. 프레임 코너 16개 + 상부 직접체결판 6개.';
  if (row[3] === 'CB6-18') row[7] = 'F02B. 두께 9 mm 상부 직접체결판을 3030 슬롯 너트에 체결.';
  if (row[3] === 'TRUSCO PHS6 / 280-7599') {
    row[7] = 'M03. 2개입 2팩, 총 4개. 2026-10-04 미스미 장바구니 공급가 26,124원 확인.';
  }
}

const meviyRoot = 'https://meviy.misumi-ec.com/ko-kr/app/fa/3dview/';
const quotedParts = [
  ['재료비 구매', '한국미스미 meviy', '상부 PHS6 직접체결판 완성품 60×30×9', 'MVBLK-ASN-4NX-8UHCW', 3,
    `${meviyRoot}001HDRRPFT/partsview/001HEFCCUC?partIds=001HEFCCUC`, 71184,
    'UP01. AL6061, Ø6.6 관통 3개·중앙 상면 Ø11×4.5 카운터보어. 23,728원/개×3. 10/15 출하 표시. 재질 열처리상태 미표기.'],
  ['재료비 구매', '한국미스미 meviy', 'A1 하부 어댑터판 완성품 120×70×8', 'MVBLK-ASN-4NX-MBY1F', 1,
    `${meviyRoot}001HDRVE6L/partsview/001HEEXVDI?partIds=001HEEXVDI`, 35342,
    'C01. AL6061, M8×1.25 관통탭 2개·Ø9 관통 2개. 2026-10-04 장바구니 견적, 10/15 출하 표시.'],
  ['재료비 구매', '한국미스미 meviy', 'A2 하부 어댑터판 완성품 120×70×8', 'MVBLK-ASN-4NX-7TGEL', 1,
    `${meviyRoot}001HDQCIQT/partsview/001HEFESXT?partIds=001HEFESXT`, 35342,
    'C02. AL6061, M8×1.25 관통탭 2개·Ø9 관통 2개. A1과 홀 좌표가 다름. 10/15 출하 표시.'],
  ['재료비 구매', '한국미스미 meviy', 'A3 하부 어댑터판 완성품 120×70×8', 'MVBLK-ASN-4NX-1YMXR', 1,
    `${meviyRoot}001HDQBPG4/partsview/001HEEXT3O?partIds=001HEEXT3O`, 35342,
    'C03. AL6061, M8×1.25 관통탭 2개·Ø9 관통 2개. A1/A2와 홀 좌표가 다름. 10/15 출하 표시.'],
];

const phsIndex = retained.findIndex(row => row[3] === 'TRUSCO PHS6 / 280-7599');
if (phsIndex < 0) throw new Error('PHS6 insertion point is missing');
retained.splice(phsIndex + 1, 0, ...quotedParts);
const rows = retained;
if (rows.length !== 63) throw new Error(`Expected 63 current purchase rows, found ${rows.length}`);

const workbook = Workbook.create();
const sheet = workbook.worksheets.add('Sheet1');
const lastPurchaseRow = rows.length + 3;
const subtotalRow = lastPurchaseRow + 1;
const lastRow = subtotalRow + 3;

sheet.getRange('B1:I1').merge();
sheet.getRange('B1').values = [['Rev F 수평유지장치 구매 BOM (meviy 견적 반영, 2026-10-04)']];
sheet.getRange('B2:I2').values = [[
  '2026 BIZ-Lab 창업클럽 시제품지원 프로그램 지출계획', null, null, null, null,
  'meviy 가공품·PHS6 장바구니 확인 / 기타 종전 BOM 가격', '지원금', 4000000,
]];
sheet.getRange('B3:I3').values = [['지출방법', '업체명', '제품명', '모델명', '수량', '링크', '총 가격 (공급가액)', '비고']];
sheet.getRange(`B4:I${lastPurchaseRow}`).values = rows;
sheet.getRange(`B${subtotalRow}:I${lastRow}`).values = [
  ['공급가 부분합', null, null, null, null, null, null,
    '2026-10-04 확인: meviy 완성품 4종 177,210원, 미스미 PHS6 26,124원. 기타 품목은 종전 BOM 가격으로 결제 전 갱신.'],
  ['부가세 10% 추정', null, null, null, null, null, null,
    'meviy 가공품 4종의 장바구니 VAT는 17,720원. 전체 행은 간편 10% 추정이며 사이트별 반올림·배송비가 다를 수 있음.'],
  ['VAT 포함 추정 합계', null, null, null, null, null, null,
    'meviy 가공품 4종은 자동견적 발주 준비완료. 미스미 장바구니 표시 총액 194,930원(공급가 177,210원) 확인.'],
  ['지원금 잔여 추정액', null, null, null, null, null, null,
    '다른 구매처의 가격·옵션·재고·배송비를 재확인한 뒤 확정.'],
];
sheet.getRange(`H${subtotalRow}:H${lastRow}`).formulas = [
  [`=SUM(H4:H${lastPurchaseRow})`],
  [`=ROUND(H${subtotalRow}*10%,0)`],
  [`=SUM(H${subtotalRow}:H${subtotalRow + 1})`],
  [`=$I$2-H${subtotalRow + 2}`],
];

sheet.getRange(`B1:I${lastRow}`).format.font = { name: 'Malgun Gothic', size: 10 };
sheet.getRange('B1:I1').format = {
  fill: '#17365D', font: { name: 'Malgun Gothic', size: 15, bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center', verticalAlignment: 'center', rowHeight: 30,
};
sheet.getRange('B2:I2').format = { fill: '#D9EAF7', font: { name: 'Malgun Gothic', size: 10, bold: true }, rowHeight: 24 };
sheet.getRange('B3:I3').format = {
  fill: '#2F75B5', font: { name: 'Malgun Gothic', size: 10, bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center', verticalAlignment: 'center', wrapText: true, rowHeight: 32,
};
sheet.getRange(`B4:I${lastPurchaseRow}`).format.wrapText = true;
sheet.getRange(`B4:I${lastPurchaseRow}`).format.verticalAlignment = 'top';
sheet.getRange(`B4:I${lastPurchaseRow}`).format.rowHeight = 42;
sheet.getRange(`B${subtotalRow}:I${lastRow}`).format = {
  fill: '#E2F0D9', font: { name: 'Malgun Gothic', size: 10, bold: true }, wrapText: true, rowHeight: 44,
};
sheet.getRange(`B3:I${lastRow}`).format.borders = { preset: 'all', style: 'thin', color: '#A6A6A6' };

let start = 4;
let currentVendor = rows[0][1];
let block = 0;
for (let i = 1; i <= rows.length; i += 1) {
  const nextVendor = i < rows.length ? rows[i][1] : null;
  if (nextVendor !== currentVendor) {
    if (block % 2 === 1) sheet.getRange(`B${start}:I${i + 3}`).format.fill = '#F5F9FC';
    start = i + 4;
    currentVendor = nextVendor;
    block += 1;
  }
}
const quoteStart = phsIndex + 5;
sheet.getRange(`B${quoteStart}:I${quoteStart + 3}`).format.fill = '#FFF2CC';
sheet.getRange(`H${quoteStart}:H${quoteStart + 3}`).format.font = {
  name: 'Malgun Gothic', size: 10, bold: true, color: '#7F6000',
};
sheet.getRange(`H4:H${lastRow}`).format.numberFormat = '#,##0"원"';
sheet.getRange('I2').format.numberFormat = '#,##0"원"';
sheet.getRange(`F4:F${lastPurchaseRow}`).format.horizontalAlignment = 'center';
sheet.getRange(`H4:H${lastRow}`).format.horizontalAlignment = 'right';
const widths = { B: 14, C: 22, D: 31, E: 31, F: 8, G: 48, H: 18, I: 68 };
for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
sheet.freezePanes.freezeRows(3);

workbook.recalculate();
const sumExpected = 2897525;
const subtotalActual = sheet.getRange(`H${subtotalRow}`).values[0][0];
if (subtotalActual !== sumExpected) throw new Error(`Supply subtotal ${subtotalActual} != ${sumExpected}`);
const quoteRange = `B${quoteStart}:I${quoteStart + 3}`;
const details = await workbook.inspect({ kind: 'table', range: `Sheet1!${quoteRange}`, include: 'values,formulas', tableMaxRows: 4, tableMaxCols: 8 });
console.log(details.ndjson);
const errorScan = await workbook.inspect({
  kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',
  options: { useRegex: true, maxResults: 50 }, summary: 'formula error scan',
});
console.log(errorScan.ndjson);
await fs.mkdir(here, { recursive: true });
for (const [name, range] of [['quote_rows', `B${quoteStart}:I${quoteStart + 6}`], ['totals', `B${subtotalRow - 1}:I${lastRow}`]]) {
  const preview = await workbook.render({ sheetName: 'Sheet1', range, scale: 1.15, format: 'png' });
  await fs.writeFile(path.resolve(here, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(outputPath);
console.log(JSON.stringify({ outputPath, purchaseRows: rows.length, quoteRows: quoteRange, subtotalActual,
  vat: sheet.getRange(`H${subtotalRow + 1}`).values[0][0],
  total: sheet.getRange(`H${subtotalRow + 2}`).values[0][0],
  remaining: sheet.getRange(`H${lastRow}`).values[0][0] }));
