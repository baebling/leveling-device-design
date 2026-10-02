import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

// Narrow Rev F workbook update. The existing Rev E source and CAD files stay untouched.
const path = './2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx';
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sheet = workbook.worksheets.getItem('Sheet1');

// Keep F09's historical identity/link for audit, but remove it from the order and sum.
sheet.getRange('B65').values = [['구매 제외']];
sheet.getRange('D65').values = [['구형 볼쪽 0.5 mm 심링 (현 검토안 불필요)']];
sheet.getRange('F65').values = [[0]];
sheet.getRange('H65').values = [['구형안 제외']];
sheet.getRange('I65').values = [[
  'F09. 현 상부 볼쪽 적층 검토안에서 CIMR6-12-0.5 심 불필요. 기존 12장/공급가 10,909원은 구매·부분합에서 제외. 신규 WSSB10-6-1.5 적합성 확인 전 HOLD.',
]];
sheet.getRange('I65').format.wrapText = true;
sheet.getRange('B65:I65').format.rowHeight = 48;

// The total formulas intentionally remain in their original cells and range.
sheet.getRange('B70').values = [['기존 숫자 가격 후보 공급가 부분합 (F09·신규 미견적 제외)']];
sheet.getRange('I72').values = [[
  'Rev E 구형 후보 VAT포함 3,143,564원 대비 F08A/B·F12·F11 제외 11,528원과 F09 제외 12,000원 감소. 신규 후보는 미견적.',
]];
sheet.getRange('I72').format.wrapText = true;
sheet.getRange('B72:I72').format.rowHeight = 42;
sheet.getRange('I73').values = [[
  'UP01A/B/C 및 신규 핀·머리쪽/볼쪽 와셔·PHS6 M6·장착 볼트/T너트 미견적. F09 12장 제외, E링은 HCDGH 동봉(별도 구매 없음). 최종 예산 적합 UNKNOWN; 구매 보류.',
]];

// Add one HOLD candidate row without moving priced rows or seller-group totals.
sheet.getRange('B82:I82').copyFrom(sheet.getRange('B81:I81'), 'all');
sheet.getRange('B79:I82').values = [
  ['머리쪽 와셔', '핀 머리와 eye 사이의 축방향 적층', '미선정 (후보 WSSB10-6-4)', '3개(축당 1개)', '한국미스미', 'https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-4', '견적 미확정', '머리쪽 T4 와셔. eye 폭·핀 릴리프·링 여유·강도 미검증 HOLD'],
  ['볼쪽 와셔', 'eye와 PHS6 볼 사이의 축방향 적층', '미선정 (후보 WSSB10-6-1.5)', '3개(축당 1개)', '한국미스미', 'https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-1.5', '표시 공급가 1,470원/개 (실결제 미확정)', 'OD10 ID6 T1.5±0.1. 2026-10-02 한국미스미 화면 VAT 1,617원/개·재고100·기준출하10/07 표시. 실제 결제·납기·CAD 적합 HOLD'],
  ['PHS6 하우징 M6 포획·이탈방지', '하우징 M6 유효물림·잠금 방식', '미선정 (후보 CBS6-12 저두볼트)', '3축 3개 필요; 최소 1개 단위', '한국미스미', 'https://kr.misumi-ec.com/vona2/detail/110100142110/?HissuCode=CBS6-12', '표시 공급가 671원/개 (실결제 미확정)', 'SCM435 10.9, M6×12·머리 Ø10×높이4. 명목 Ø11×깊이6 리세스에 머리 상면 2mm 후퇴, 3mm 웹 뒤 PHS6 공칭 물림9mm이나 공차·바닥/니플/렌치 미확인. F21 대체 금지; F17 나사고정제는 오일·나사산·토크·경화 검증 전 후보만. 2026-10-02 한국미스미 로그인 화면 재고423·참고출하10/07 표시, 결제·납기·유효물림 HOLD'],
  ['브래킷 장착 볼트·T너트', '3030 프레임에 3개 브래킷 장착', '미선정 (F02/F07 재사용 미확정)', '명목 볼트 6개·너트 6개; 길이·포장 미정', '미확정', '—', '견적 미확정', 'F02/F07 자동 전용 금지. 납품 3030 슬롯·체결력 검증 전 HOLD'],
];
sheet.getRange('B79:I82').format.wrapText = true;
sheet.getRange('B79:I82').format.rowHeight = 52;
sheet.getRange('B81:I81').format.rowHeight = 86;
sheet.getRange('B75:I82').format.borders = { preset: 'all', style: 'thin', color: '#C9D5E1' };

workbook.recalculate();
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(path);
console.log(`Saved ${path}`);
