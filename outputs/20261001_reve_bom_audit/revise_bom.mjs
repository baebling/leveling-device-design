import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20260930_reve_interface_correction',
  '2026_BIZ-Lab_재료비관리_RevE_315mm_체결전장정정.xlsx');
const outputDir = path.join(root, 'outputs', '20261001_reve_bom_audit');
const dest = path.join(outputDir, '2026_BIZ-Lab_재료비관리_RevE_검수수정.xlsx');

const book = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheet = book.worksheets.getItem('Sheet1');
const ids = sheet.getRange('I4:I70').values.map(row => String(row[0] ?? '').split('.')[0]);
if (ids.length !== 67 || new Set(ids).size !== 67 || ids[62] !== 'F11') {
  throw new Error('Unexpected input BOM row layout');
}

await fs.mkdir(outputDir, {recursive: true});
const before = await book.render({sheetName: 'Sheet1', range: 'B61:I74', scale: 1, format: 'png'});
await fs.writeFile(path.join(outputDir, 'before_edit.png'), new Uint8Array(await before.arrayBuffer()));

sheet.getRange('B1').values = [['검수용 · 발주 보류 (2026-10-01)']];
sheet.getRange('B1').format.font.color = '#B91C1C';
sheet.getRange('B1').format.font.bold = true;

// Confirmed product identity and later verified price. Fit/option selection remain open.
sheet.getRange('D56').values = [['LM4075OE-1075 광학엔코더 액추에이터']];
sheet.getRange('E56').values = [['LM4075OE-1075 / 24 V / 100 mm / 5 V / 6 ppr']];
sheet.getRange('I56').values = [['M01. 모터뱅크 1000035578은 LM4075OE-1075. 결제 전 24 V·100 mm·5 V 옵션 3개 재확인. 내장 리미트 위치 미검증.']];
sheet.getRange('D61').values = [['상부 로드엔드 (PHS6 2개입/포장)']];
sheet.getRange('I61').values = [['M03. 수량 2포장×2개입=4개, 3축에 3개 사용·1개 잔여. 한국미스미 결제 화면에서 실제 포장 단위·재고·납기 재확인.']];
sheet.getRange('H66').values = [[600]];
sheet.getRange('I66').values = [['F11. 미스미 M6×25 3개×200원(공급가). 명목 적층 25 mm가 정확히 소진되어 PHS 암나사 깊이·물림·공차 검증 전 사용 보류.']];

// Do not make incompatible lines appear purchase-ready merely because they have prices.
sheet.getRange('D18').values = [['M6×55 전나사 피벗 볼트 (사용 보류)']];
sheet.getRange('I17').values = [['F08A. M6×50 반나사 민무늬부 32 mm. 눈폭·PHS폭·와셔/심 적층과 너트 체결 여유 실측 전 사용 보류.']];
sheet.getRange('I18').values = [['F08B. 완전나사여서 피벗 지지면에 나사산 접촉. 현 설계에는 사용 보류; 대체 피벗 규격 미확정.']];
sheet.getRange('D38').values = [['ATO 퓨즈홀더 (DC 정격 미확인)']];
sheet.getRange('I38').values = [['E09A. SZH-FU005의 DC 허용전압·전류·리드선 굵기 미입증. 퓨즈 10 A 선택만으로 홀더 승인 불가. 교체 필요.']];
sheet.getRange('D43').values = [['BPS100A 전원분배블럭 (배선 부적합)']];
sheet.getRange('I43').values = [['E14. M5 출력 허용 4–16 mm², 현 AWG14 분기선 약 2.08 mm² 불가. XK2 대체안은 입력 10 mm² 이상과 상류 분기 재설계 필요.']];
sheet.getRange('D44').values = [['AWG8 공통선 (대체안과 부적합)']];
sheet.getRange('I44').values = [['E15. AWG8 약 8.37 mm²는 XK2 입력 최소 10 mm² 미달. G9EA 제조사 주접점 권장선 14–22 mm²에도 미달.']];
sheet.getRange('I47').values = [['HP01. 현 링크 판매 최소수량 100개 단위, 기재수량·가격은 주문 불가. 공통선 규격 재결정 후 링 규격/압착 방법 재선정.']];
sheet.getRange('I52').values = [['HP02. 현 링크 판매 최소수량 100개 단위, 기재수량·가격은 주문 불가. PSU/G9EA 단자와 전선 규격 확정 후 교체.']];
sheet.getRange('I53').values = [['HP03. 현 링크 판매 최소수량 100개 단위. BPS 출력 최소 4 mm²와 현 14AWG 단자는 불일치하므로 단순 증량 금지.']];
sheet.getRange('I24').values = [['E06. SL902 400×500×155 mm는 외형치수. 기존 함체 타공은 허용되지만 속판 유효치수·문 간섭·PSU 통풍 검증 전 배치/홀 좌표 미승인.']];
for (const row of [58, 59, 60]) {
  const id = ids[row - 4];
  sheet.getRange(`I${row}`).values = [[`${id}. DMC-200 1대/축. 판매자 추천은 확인했으나 실제 5 V·6 ppr 배선/주소/전류 제한은 통전 전 검증. 발주 릴리스 보류.`]];
}

sheet.getRange('B71').values = [['기존 후보 공급가 합계 (발주 불가)']];
sheet.getRange('B73').values = [['기존 후보 VAT 포함 합계 (발주 불가)']];
sheet.getRange('B74').values = [['잔액 참고 (누락 비용 있음)']];
sheet.getRange('I74').values = [['미확정 비용 제외. 결제 금지.']];

book.recalculate();
const expected = sheet.getRange('H4:H70').values.reduce((sum, row) => sum + (Number(row[0]) || 0), 0);
const actual = sheet.getRange('H71').values[0][0];
if (expected !== actual || expected !== 2846985) {
  throw new Error(`Unexpected subtotal: ${expected} / ${actual}`);
}
const errors = await book.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: {useRegex: true, maxResults: 100},
  summary: 'RevE correction formula error scan',
});
await fs.writeFile(path.join(outputDir, 'formula_errors.ndjson'), errors.ndjson);
const inspection = await book.inspect({kind: 'region', sheetId: 'Sheet1', range: 'B62:I74',
  maxChars: 7000, tableMaxRows: 13, tableMaxCols: 8});
await fs.writeFile(path.join(outputDir, 'summary_inspection.ndjson'), inspection.ndjson);
const after = await book.render({sheetName: 'Sheet1', range: 'B61:I74', scale: 1, format: 'png'});
await fs.writeFile(path.join(outputDir, 'after_edit.png'), new Uint8Array(await after.arrayBuffer()));
for (const [name, range] of [
  ['after_header.png', 'B1:I12'],
  ['after_electrical.png', 'B36:I55'],
]) {
  const preview = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outputDir, name), new Uint8Array(await preview.arrayBuffer()));
}
const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(dest);
console.log(JSON.stringify({dest, lineCount: ids.length, subtotal: actual}));
