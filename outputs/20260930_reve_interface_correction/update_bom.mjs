import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20260930_misumi_plate_bom', '2026_BIZ-Lab_창업클럽_시제품_재료비관리_미스미판재_반영.xlsx');
const outDir = path.join(root, 'outputs', '20260930_reve_interface_correction');
const dest = path.join(outDir, '2026_BIZ-Lab_재료비관리_RevE_315mm_체결전장정정.xlsx');

await fs.mkdir(outDir, { recursive: true });
const book = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheet = book.worksheets.getItem('Sheet1');
const original = sheet.getRange('B4:I67').values.map(row => [...row]);
if (original.length !== 64 || original[0][1] !== '나비엠알오') {
  throw new Error('Unexpected source workbook layout');
}
const idOf = row => String(row[7] ?? '').split('.')[0];
const rows = original.filter(row => !['F11', 'E24'].includes(idOf(row)));
const byId = id => {
  const row = rows.find(item => idOf(item) === id);
  if (!row) throw new Error(`Missing ${id}`);
  return row;
};

{
  const r = byId('F05');
  r[2] = 'LMB-10 하부 M8×12 육각볼트 (한국산)';
  r[3] = 'K15696523 / M8×12';
  r[4] = 6;
  r[5] = 'https://www.navimro.com/p/K15696523/';
  r[6] = 3000;
  r[7] = 'F05. A1~A3 각 2개. 3 mm LMB 바닥+평와셔 3장+8 mm 판재 중 6 mm 나사 물림, 끝 2 mm 후퇴. 국내산 화면가 500원/개; 실물 체결 확인.';
}
byId('F04')[7] = 'F04. M8×12 볼트당 평와셔 1 mm 3장, 총 18장 필요. 포장수량·두께·체결면 확인.';
byId('F09')[7] = 'F09. 상부 액추에이터 아이 1.5 mm 외측 이동: 0.5 mm 심링 각 축 3장=9장, 12장 중 3장 여유. 실제 PHS6/아이 폭 확인.';
byId('F18')[7] = 'F18. 함체/레일 관통 체결용 후보. RSP-750-24 섀시 M4 탭에 직접 넣으면 깊이 초과하므로 사용 금지.';
byId('E06')[7] = 'E06. 400×500×155 mm. 전장 배치, 내부 판재, 전원공급기 통풍/온도 검증 후 가공·장착.';
{
  const r = byId('E14');
  r[2] = '모터 ± 공통전원 분배블럭 (각 극 1개)';
  r[3] = '14981941 / BPS100A-M6/4*M5';
  r[4] = 2;
  r[5] = 'https://www.devicemart.co.kr/goods/view?no=14981941';
  r[6] = 72000;
  r[7] = 'E14. 100 A/600 V, M6 입력 1+M5 출력 4, +/− 독립 2개. 기존 60A 4P는 각 극 내부 공통이 확인되지 않아 제외. 공급가 36,000원/개, 1주일 준비 표시.';
}
byId('E09A')[7] = 'E09A. ATO 10 A×3+제어 5 A×1. 홀더 자체 허용전류/리드선 굵기 미기재: 결제 전 확인 필요.';
byId('HP01')[7] = 'HP01. AWG8/M6 링. 분배블럭 2개 입력용 2개 사용; 실제 구매 최소수량과 압착공구 확인.';
byId('E11')[7] = 'E11. G9EA-1-B DC24: 접점 M5, 코일 M3.5/약 208 mA, 장착 M6. 접점 극성 준수. Portenta J6 출력+E-stop NC 직렬 코일 경로; 실배선 검증.';
byId('CB02')[2] = 'Portenta–ZMEC485DI Ethernet 케이블';

rows.push([
  '재료비 구매', '한국미스미', '상부 PHS6 M6×25 무두 스터드', 'E-GMSSU6-25 (후보)', 3,
  'https://kr.misumi-ec.com/vona2/detail/110310926189/?HissuCode=E-GMSSU6-25', null,
  'F11. 기존 M6×20은 315 mm 구조에서 너무 짧음. M6×25 완전나사 후보; 한국미스미 장바구니 가격·납기·PHS6 나사 유효깊이 확인 전 주문 보류.'
]);
rows.push([
  '재료비 구매', '디바이스마트', 'AWG8/M5 링 압착단자 (PSU·G9EA)', '12507001 / JOT 10-5', 4,
  'https://www.devicemart.co.kr/goods/view?no=12507001', 800,
  'HP02. 4개 사용 예상. 200원/개 공급가 기준; 웹 장바구니 최소수량은 미검증. M5 접점·PSU 단자 실측 후 주문.'
]);
rows.push([
  '재료비 구매', '디바이스마트', '14AWG/M5 링 압착단자 (축별 분기)', '12506983 / JOT 2.5-54', 12,
  'https://www.devicemart.co.kr/goods/view?no=12506983', 600,
  'HP03. 2.5 mm²/AWG14–16, M5 홀. 6개 이상 사용, 50원/개 공급가 기준; 최소수량/분기 단자 규격 확인.'
]);
rows.push([
  '재료비 구매', '디바이스마트', 'RSP-750-24 섀시 M4×6 나사', '10912091 / M4×6', 10,
  'https://www.devicemart.co.kr/goods/view?no=10912091', 300,
  'F20. 30원/개 공급가, 10개 화면 수량. PSU M4 탭 침투 길이 4–6 mm를 지지판 두께와 함께 확인; M4×25 직접 사용 금지.'
]);
rows.push([
  '재료비 구매', '디바이스마트', 'G9EA-1-B 장착 M6×12 나사', '10910853 / M6×12', 10,
  'https://www.devicemart.co.kr/goods/view?no=10910853', 1200,
  'F21. M6 장착 홀 2개에 사용, F10 M6 너트와 결합. 백판/함체 두께에 따라 관통길이 확인. 120원/개 화면가.'
]);

const supplierOrder = ['나비엠알오','디바이스마트','모터뱅크','한국미스미','아이씨뱅큐','액티웍스','G마켓 케이일레븐홀딩스'];
rows.sort((a,b) => supplierOrder.indexOf(a[1]) - supplierOrder.indexOf(b[1]));
if (rows.length !== 67) throw new Error(`Expected 67 BOM lines, got ${rows.length}`);
const last = 3 + rows.length;
const subtotalRow = last + 1;
const vatRow = last + 2;
const totalRow = last + 3;
const balanceRow = last + 4;

// Copy the old summary formats before writing new line items over their cells.
sheet.getRange(`B${subtotalRow}:I${balanceRow}`).copyFrom(sheet.getRange('B68:I71'), 'all');
sheet.getRange('B68:I70').copyFrom(sheet.getRange('B67:I67'), 'all');
sheet.getRange(`B4:I${last}`).clear({ applyTo: 'contents' });
sheet.getRange(`B4:I${last}`).values = rows;
// Imported total rows retain stale cached formula values in artifact-tool's
// table layer after a block rewrite.  Force these three cells explicitly.
for (const row of [68, 69, 70]) {
  sheet.getRange(`H${row}`).values = [[rows[row - 4][6]]];
}
sheet.getRange('B68:I70').format.font.bold = false;
sheet.getRange('B68:I70').format.font.size = 9;
sheet.getRange('G68:G70').format.font.color = '#0563C1';
sheet.getRange(`B${subtotalRow}`).values = [['확인 가격 소계 (F11·배송비 제외)']];
sheet.getRange(`H${subtotalRow}`).formulas = [[`=SUM(H4:H${last})`]];
sheet.getRange(`B${vatRow}`).values = [['부가세 (10%)']];
sheet.getRange(`H${vatRow}`).formulas = [[`=ROUND(H${subtotalRow}*10%,0)`]];
sheet.getRange(`B${totalRow}`).values = [['확인 가격 총액 (부가세 포함)']];
sheet.getRange(`H${totalRow}`).formulas = [[`=SUM(H${subtotalRow}:H${vatRow})`]];
sheet.getRange(`B${balanceRow}`).values = [['잔액 (미견적품 제외)']];
sheet.getRange(`H${balanceRow}`).formulas = [[`=$I$2-H${totalRow}`]];
sheet.getRange(`I${balanceRow}`).values = [['주문승인 전 F11·단자 최소수량·배송비·재고/납기·퓨즈홀더/함체 열검증 확인. CAD 통과는 실물 조립 승인 아님.']];

book.recalculate();
const expected = rows.reduce((sum,row) => sum + (Number(row[6]) || 0), 0);
const actual = sheet.getRange(`H${subtotalRow}`).values[0][0];
if (actual !== expected) {
  const suspicious = sheet.getRange(`H4:H${last}`).values.map((item,index) => [index+4,item[0]]).filter(([index,value]) => value !== rows[index-4][6]);
  console.log(JSON.stringify({suspicious,formulas:sheet.getRange('H68:H74').formulas}));
  throw new Error(`Subtotal mismatch: expected ${expected}, got ${actual}`);
}
const inspection = await book.inspect({ kind: 'region', sheetId: 'Sheet1', range: `B${last-3}:I${balanceRow}`, maxChars: 7000, tableMaxRows: 8, tableMaxCols: 8 });
await fs.writeFile(path.join(outDir, 'bom_check.json'), JSON.stringify({lineCount:rows.length,expected,actual,summaryRows:[subtotalRow,vatRow,totalRow,balanceRow],inspection}, null, 2));
const preview = await book.render({ sheetName:'Sheet1', range:`B${last-8}:I${balanceRow}`, scale:1, format:'png' });
await fs.writeFile(path.join(outDir, 'bom_last_rows_preview.png'), new Uint8Array(await preview.arrayBuffer()));
const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(dest);
console.log(JSON.stringify({dest,lineCount:rows.length,subtotal:actual,summaryRows:[subtotalRow,vatRow,totalRow,balanceRow]}));
