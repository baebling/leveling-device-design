import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const path = './2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx';
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sheet = workbook.worksheets.getItem('Sheet1');

const urls = {
  pin: 'https://kr.misumi-ec.com/vona2/detail/110300095750/?HissuCode=HCDGH6-35',
  washer: 'https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-4',
  screw: 'https://kr.misumi-ec.com/vona2/detail/110300239250/?HissuCode=PACK-SCB6-12-YBM',
};

// Only the already-unpriced HOLD section changes. Candidates are not order lines.
sheet.getRange('B77:F81').values = [
  ['신규 상부 피벗 핀', '3축 포켓-아이 연결', '미선정 (후보 HCDGH6-35)', '3개(축당 1개), E링 각 1개 동봉', '한국미스미'],
  ['핀 리테이너', '피벗 축방향 이탈 방지', 'HCDGH6-35 동봉 E형 No.5 고정링', '동봉 3개; 별도 발주 없음', '한국미스미'],
  ['조립 스페이서/와셔', '축별 유격·간섭 제어', '미선정 (후보 WSSB10-6-4; F09 CIMR6-12-0.5)', '와셔 3개; 심 명목 9장(기존 F09 12장 후보)', '한국미스미'],
  ['PHS6 하우징 M6 포획·이탈방지', '하우징 M6 유효물림·잠금 방식', '미선정 (후보 PACK-SCB6-12-YBM)', '3축 3개 필요; 후보 10개입 1팩', '한국미스미'],
  ['브래킷 장착 볼트·T너트', '3030 프레임에 3개 브래킷 장착', '미선정 (F02/F07 재사용 미확정)', '명목 볼트 6개·너트 6개; 길이·포장 미정', '미확정'],
];
for (const [row, url] of [[77, urls.pin], [78, urls.pin], [79, urls.washer], [80, urls.screw]]) {
  // The renderer does not implement HYPERLINK() and poisons its cached text.
  // Export plain exact URLs, then repair only native hyperlink relationships.
  sheet.getRange(`G${row}`).values = [[url]];
}
sheet.getRange('G81').values = [['—']];
sheet.getRange('H77:H81').values = [
  ['견적 미확정'],
  ['동봉 (별도 발주 없음)'],
  ['신규 와셔 견적 미확정; F09 기포함'],
  ['견적 미확정'],
  ['견적 미확정'],
];
sheet.getRange('I77:I81').values = [
  ['핀 보증 항복·홈 강도·eye 공차·링 축하중 미검증 HOLD'],
  ['HCDGH에 동봉; 별도 구매 0. 실제 링 유지력 미검증 HOLD'],
  ['eye 폭·링 장착 여유 미확정. F09 심 12장과 중복 구매 금지 HOLD'],
  ['F21/G9EA용 볼트와 구별. M6 유효물림·잠금·머리 여유·카드결제 HOLD'],
  ['F02/F07 자동 전용 금지. 납품 3030 슬롯·체결력 검증 전 HOLD'],
];
sheet.getRange('I73').values = [[
  'UP01A/B/C 및 신규 핀·와셔·PHS6 M6·장착 볼트/T너트 미견적. E링은 HCDGH 동봉(별도 구매 없음). 최종 예산 적합 UNKNOWN; 구매 보류.'
]];
sheet.getRange('I75').values = [['유료 구매행 미반영·HOLD']];
sheet.getRange('I73').format.wrapText = true;
sheet.getRange('B73:I73').format.rowHeight = 54;
sheet.getRange('B77:I81').format.rowHeight = 52;

workbook.recalculate();
const scan = await workbook.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 30 },
  summary: 'Rev F HOLD update formula-error scan',
});
console.log('formula_error_scan', scan.ndjson);
const view = await workbook.render({ sheetName: 'Sheet1', range: 'B74:I81', scale: 1.5, format: 'png' });
await fs.writeFile('./revf_hold_rows_updated.png', new Uint8Array(await view.arrayBuffer()));
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(path);
console.log('Updated HOLD candidate rows 77–81; paid rows unchanged');
