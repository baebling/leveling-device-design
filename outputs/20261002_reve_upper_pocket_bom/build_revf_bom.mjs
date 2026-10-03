import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const outputPath = '../20261003_revf_order_candidate/2026_BIZ-Lab_재료비관리_RevF_발주후보.xlsx';

const rows = [
  // NAVIMRO: frame, enclosure, wiring consumables and hand-machining tools.
  ['재료비 구매','나비엠알오','하부 4040 프로파일 700 mm','K92787708',2,'https://www.navimro.com/p/K92787708/',39980,'S01. 하부 프레임 장변. 공장 절단품.'],
  ['재료비 구매','나비엠알오','하부 4040 프로파일 620 mm','K92787705',4,'https://www.navimro.com/p/K92787705/',71960,'S02. 하부 프레임 단변·가로대. 공장 절단품.'],
  ['재료비 구매','나비엠알오','40시리즈 직각 브래킷','K92782553',8,'https://www.navimro.com/p/K92782553/',6640,'S05. 하부 프레임 코너 체결.'],
  ['재료비 구매','나비엠알오','M8×16 육각렌치볼트','K53536280',1,'https://www.navimro.com/p/K53536280/',6890,'F01. 하부 프레임 브래킷 체결용 포장.'],
  ['재료비 구매','나비엠알오','M8×20 육각렌치볼트','K53536553',1,'https://www.navimro.com/p/K53536553/',6690,'F03. 하부 어댑터판의 Ø9 홀을 통해 프로파일 너트에 체결.'],
  ['재료비 구매','나비엠알오','M8 평와셔','K06130485',1,'https://www.navimro.com/p/K06130485/',4590,'F04. LMB-10 높이 보정 및 하부 판 체결용.'],
  ['재료비 구매','나비엠알오','LMB-10 하부 M8×12 육각볼트','K15696523 / M8×12',6,'https://www.navimro.com/p/K15696523/',3000,'F05. 축당 2개. 8 mm 판의 M8 탭에 체결.'],
  ['재료비 구매','나비엠알오','40시리즈 M8 스프링너트','K14671419',1,'https://www.navimro.com/p/K14671419/',22990,'F06. 하부 프로파일 및 A1~A3 판 체결용 포장.'],
  ['재료비 구매','나비엠알오','M6 나일론 인서트 너트','K14536539',1,'https://www.navimro.com/p/K14536539/',7990,'F10. 일반 보조 체결용; 상부 PHS6 포획에는 사용하지 않음.'],
  ['재료비 구매','나비엠알오','중강도 나사고정제','K64647607',1,'https://www.navimro.com/p/K64647607/',8990,'F17. CBS6-12와 PHS6 암나사 체결부에 소량 사용.'],
  ['재료비 구매','나비엠알오','M4×25 더블샘스볼트','K14364804',1,'https://www.navimro.com/p/K14364804/',16490,'F18. 플라스틱 속판 관통 고정용. RSP 본체 탭에는 사용하지 않음.'],
  ['재료비 구매','나비엠알오','M4 육각너트','K06130054',1,'https://www.navimro.com/p/K06130054/',1390,'F19. 속판 관통 고정용.'],
  ['재료비 구매','나비엠알오','ABS 전장함','BC-AGP-507025 / K25262371',1,'https://www.navimro.com/p/K25262371/',109990,'E06A. 530×730×255 mm급. 플라스틱 타공만 현장 수행.'],
  ['재료비 구매','나비엠알오','전장함 플라스틱 속판','5070P / K25264419',1,'https://www.navimro.com/p/K25264419/',18139,'E06B. 전장부품·DIN 레일 장착판.'],
  ['재료비 구매','나비엠알오','접지 전원코드','K08345728',1,'https://www.navimro.com/p/K08345728/',3990,'E07. AC 입력용. PE는 RSP FG에 연결.'],
  ['재료비 구매','나비엠알오','24AWG 제어전선 세트','K92843703',1,'https://www.navimro.com/p/K92843703/',30990,'E16. 버튼·접촉기 코일·저전류 제어배선.'],
  ['재료비 구매','나비엠알오','열수축튜브 키트','K52569152',1,'https://www.navimro.com/p/K52569152/',10990,'E17. 절연 및 표식 보강.'],
  ['재료비 구매','나비엠알오','케이블 글랜드 세트','K22571959',1,'https://www.navimro.com/p/K22571959/',6290,'E18. 전장함 하부 케이블 인입.'],
  ['재료비 구매','나비엠알오','페룰 및 압착 키트','K92839991',1,'https://www.navimro.com/p/K92839991/',39990,'E19. 14AWG 이하 연선 종단.'],
  ['재료비 구매','나비엠알오','케이블 타이','K01415707',1,'https://www.navimro.com/p/K01415707/',15490,'E20. 배선 고정.'],
  ['재료비 구매','나비엠알오','PVC 절연테이프','K40799280',3,'https://www.navimro.com/p/K40799280/',1500,'E21. 색상 구분 및 임시 보강.'],
  ['재료비 구매','나비엠알오','녹/황 보호접지선','K55027039',3,'https://www.navimro.com/p/K55027039/',3870,'E23. RSP FG 및 도전성 장착부 접지.'],
  ['재료비 구매','나비엠알오','DMC-200 축별 분기 케이블','14 AWG 실리콘 전선 세트 / K92854706',1,'https://www.navimro.com/p/K92854706/',74990,'E15B. 6 A 전류제한 축 3개와 24 V 분기 배선.'],
  ['재료비 구매','나비엠알오','주전원 케이블 적/흑','KIV 4SQ, 각 2 m',1,'https://www.navimro.com/s/?q=KIV%204SQ',14000,'E15A. 20 A 주퓨즈 전후 및 공통 0 V. 실제 색상·미터단위 확인.'],
  ['재료비 구매','나비엠알오','열수축 압착 슬리브','3.5~5.5SQ',1,'https://www.navimro.com/s/?q=열수축%20압착%20슬리브%205.5',9000,'E24. 01550300Z 리드와 4SQ 케이블 연결용. 실제 리드 굵기에 맞춤.'],
  ['재료비 구매','나비엠알오','HSS 금속용 드릴 Ø6.8 mm','SD 6.8 / K11176399',1,'https://m.navimro.com/p/K11176399/',2090,'T01. A1~A3 M8×1.25 탭 밑구멍.'],
  ['재료비 구매','나비엠알오','HSS 금속용 드릴 Ø9.0 mm','D1101090 / K01216966',1,'https://m.navimro.com/p/K01216966/',21990,'T02. A1~A3 프로파일 체결 클리어런스 홀.'],

  // DeviceMart: power and controls. 20 A main fuse caps the downstream DC chain.
  ['재료비 구매','디바이스마트','24 V 주 전원공급기','RSP-750-24 / 13232167',1,'https://www.devicemart.co.kr/goods/view?no=13232167',272300,'E04. 24 V, 31.3 A. 출력 전체가 아니라 20 A 주퓨즈 이후만 모터계통에 사용.'],
  ['재료비 구매','디바이스마트','밀폐형 ATO 인라인 퓨즈홀더','Littelfuse 01550300Z / 8994457',5,'https://www.devicemart.co.kr/goods/view?no=8994457',54900,'E09A. 32 VDC, 20 A. 주 1개·축 3개·제어 1개.'],
  ['재료비 구매','디바이스마트','주전원 ATO 퓨즈 20 A','AUTO-FUSE 32V 20A',10,'https://www.devicemart.co.kr/s-1/c-3/?q=AUTO-FUSE%2020A',1000,'E09M. 실제 사용 1개, 나머지 예비.'],
  ['재료비 구매','디바이스마트','액추에이터 분기 ATO 퓨즈 10 A','11510 / AUTO-FUSE 32V 10A',10,'https://www.devicemart.co.kr/goods/view?no=11510',1000,'E09B. 축당 1개. DMC-200 전류제한은 6.0 A로 시작.'],
  ['재료비 구매','디바이스마트','제어전원 ATO 퓨즈 5 A','11509 / AUTO-FUSE 32V 5A',10,'https://www.devicemart.co.kr/goods/view?no=11509',1000,'E09C. Portenta·DDR·접촉기 코일 제어분기.'],
  ['재료비 구매','디바이스마트','비상정지 스위치','KGE-C4R2R / 10895022',1,'https://www.devicemart.co.kr/goods/view?no=10895022',6600,'E10. NC 접점으로 Finder 코일만 차단. 모터전류 직접 차단 금지.'],
  ['재료비 구매','디바이스마트','START 순간버튼 녹색','KGF-CM1G / 10894246',1,'https://www.devicemart.co.kr/goods/view?no=10894246',4000,'E13. NO 접점. Finder 두 번째 NO와 병렬로 자기유지.'],
  ['재료비 구매','디바이스마트','DIN 전원분배블록','DKD35-P001 / 16043939',2,'https://www.devicemart.co.kr/goods/view?no=16043939',30400,'E14. 1개는 접촉기 이후 +24 V 모터분배, 1개는 공통 0 V.'],
  ['재료비 구매','디바이스마트','DIN DC-DC 전원','DDR-15G-12 / 11269545',1,'https://www.devicemart.co.kr/goods/view?no=11269545',31500,'E12. 24 V→12 V/1.25 A. ZMEC485DI와 HWT905 2대 전원.'],
  ['재료비 구매','디바이스마트','2P 누전차단기','LS EBE32FB 2P 10A 30mA / 15085668',1,'https://www.devicemart.co.kr/goods/view?no=15085668',30000,'E08. RSP AC 입력 전단. 실제 판매가·재고는 결제 화면에서 갱신.'],
  ['재료비 구매','디바이스마트','Portenta Machine Control','AKX00032 / 13963538',1,'https://www.devicemart.co.kr/goods/view?no=13963538',496970,'PC01. J5 RS-485는 DMC-200 3대 전용. J7은 온도센서 단자.'],
  ['재료비 구매','디바이스마트','5선 레버 커넥터','WAGO 221-415, 10개입',1,'https://www.devicemart.co.kr/s-1/c-3/?q=WAGO%20221-415',18000,'E25. 저전류 +24 V/+12 V 분기용. 모터 주전류 분배에는 사용하지 않음.'],
  ['재료비 구매','디바이스마트','차폐 3쌍 통신 케이블','광일전선 UL2919 / 3P×24AWG / 13352',6,'https://www.devicemart.co.kr/goods/view?no=13352',21000,'CB01. DMC 버스·HWT 버스를 물리적으로 분리.'],
  ['재료비 구매','디바이스마트','RS-485 종단저항','120Ω 1/4W 1% / 1997',10,'https://www.devicemart.co.kr/goods/view?no=1997',400,'RT01. 각 RS-485 버스의 물리적 양 끝에만 적용.'],
  ['재료비 구매','디바이스마트','Portenta–ZMEC Ethernet 케이블','Anyport AP-6UTP-2M(G) / 10932540',1,'https://www.devicemart.co.kr/goods/view?no=10932540',1200,'CB02. HWT905 Modbus TCP 경로.'],
  ['재료비 구매','디바이스마트','Portenta 프로그래밍 USB 케이블','USB-A to Micro-B C3886 / 1061716',1,'https://www.devicemart.co.kr/goods/view?no=1061716',2500,'CB03. 펌웨어 업로드용.'],
  ['재료비 구매','디바이스마트','RSP-750-24 섀시 고정나사','M4×6 / 10912091',10,'https://www.devicemart.co.kr/goods/view?no=10912091',300,'F20. RSP 지정 탭 깊이 이내에서만 사용.'],

  // Motorbank: actuator and closed-loop drive.
  ['재료비 구매','모터뱅크','광학엔코더 리니어 액추에이터','LM4075OE-1075 / 24 V / 100 mm / 5 V / 6 ppr',3,'https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000035578',345000,'M01. 24 V·100 mm·5 V 엔코더 옵션. 기준점 +15 mm, 명령 최대 50 mm; CAD 간섭 시 35 mm로 제한.'],
  ['재료비 구매','모터뱅크','하부 피벗 브래킷','LMB-10 / 1000007655',3,'https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000007655',12000,'M02. 동봉 핀/R클립 수량을 수령 즉시 확인.'],
  ['재료비 구매','모터뱅크','엔코더 위치제어 드라이버','DMC-200 / 1000008040',3,'https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000008040',257400,'DC01. 축별 1대, ID 1/2/3. 위치·속도 제어 전류제한 6.0 A 초기값.'],

  // MISUMI: factory-cut upper frame, joints and six custom/blank parts.
  ['재료비 구매','한국미스미','상부 로드엔드 (2개입/포장)','TRUSCO PHS6 / 280-7599',2,'https://kr.misumi-ec.com/vona2/detail/221005504380/?HissuCode=PHS6',26124,'M03. 4개 확보: 3축 사용+1개 예비.'],
  ['재료비 구매','한국미스미','축 A 상부 포켓 브래킷 — 업체 완성품','UP-A1 / STEP 견적',1,'../20261003_revf_quote_package/step/UP_A1_PHS6_POCKET_BRACKET.step','사용자 견적','UP01A. S45C 무처리 완성품. 사용자 meviy 업로드·견적.'],
  ['재료비 구매','한국미스미','축 B 상부 포켓 브래킷 — 업체 완성품','UP-A2 / STEP 견적',1,'../20261003_revf_quote_package/step/UP_A2_PHS6_POCKET_BRACKET.step','사용자 견적','UP01B. S45C 무처리 완성품. 사용자 meviy 업로드·견적.'],
  ['재료비 구매','한국미스미','축 C 상부 포켓 브래킷 — 업체 완성품','UP-A3 / STEP 견적',1,'../20261003_revf_quote_package/step/UP_A3_PHS6_POCKET_BRACKET.step','사용자 견적','UP01C. S45C 무처리 완성품. 사용자 meviy 업로드·견적.'],
  ['재료비 구매','한국미스미','A1 하부 어댑터판 120×70×8','A6061LNN-120-70-8',1,'https://kr.misumi-ec.com/vona2/detail/110302243870/?ProductCode=A6061LNN-120-70-8',21310,'C01. 공급 판재에 사용자 Ø9 타공·Ø6.8 후 M8×1.25 탭.'],
  ['재료비 구매','한국미스미','A2 하부 어댑터판 120×70×8','A6061LNN-120-70-8',1,'https://kr.misumi-ec.com/vona2/detail/110302243870/?ProductCode=A6061LNN-120-70-8',21310,'C02. 도면 좌표가 A1과 다름.'],
  ['재료비 구매','한국미스미','A3 하부 어댑터판 120×70×8','A6061LNN-120-70-8',1,'https://kr.misumi-ec.com/vona2/detail/110302243870/?ProductCode=A6061LNN-120-70-8',21310,'C03. 도면 좌표가 A1/A2와 다름.'],
  ['재료비 구매','한국미스미','상부 3030 프로파일 700 mm','E-DNF3030-6-700',2,'https://kr.misumi-ec.com/vona2/result/?Keyword=E-DNF3030-6-700',15900,'S03. 공장 절단품.'],
  ['재료비 구매','한국미스미','상부 3030 프로파일 640 mm','E-DNF3030-6-640',4,'https://kr.misumi-ec.com/vona2/result/?Keyword=E-DNF3030-6-640',27265,'S04. 공장 절단품.'],
  ['재료비 구매','한국미스미','3030용 M6 스프링너트','E-SPN306',22,'https://kr.misumi-ec.com/vona2/result/?Keyword=E-SPN306',4620,'F07. 프레임 코너 16개+상부 포켓 브래킷 6개.'],
  ['재료비 구매','한국미스미','3030 직각 브래킷','E-DCBK3025',8,'https://kr.misumi-ec.com/vona2/result/?Keyword=E-DCBK3025',3200,'S06. 상부 프레임 코너 체결.'],
  ['재료비 구매','한국미스미','M6×12 육각렌치볼트','CB6-12',16,'https://kr.misumi-ec.com/vona2/result/?Keyword=CB6-12',3840,'F02A. E-DCBK3025 체결.'],
  ['재료비 구매','한국미스미','M6×18 육각렌치볼트','CB6-18',6,'https://kr.misumi-ec.com/vona2/result/?Keyword=CB6-18',1560,'F02B. 9 mm 상부 브래킷 베이스→E-SPN306 체결.'],
  ['재료비 구매','한국미스미','상부 피벗 핀 (E링 동봉)','HCDGH6-35',3,'https://kr.misumi-ec.com/vona2/detail/110300095750/?HissuCode=HCDGH6-35',12000,'F08. 축당 1개. 별도 리테이너 구매 없음.'],
  ['재료비 구매','한국미스미','핀 머리쪽 스페이서 와셔','WSSB10-6-4',3,'https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-4',7500,'F08A. OD10×ID6×T4, 축당 1개.'],
  ['재료비 구매','한국미스미','볼쪽 스페이서 와셔','WSSB10-6-1.5',3,'https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-1.5',4410,'F08B. OD10×ID6×T1.5, 축당 1개.'],
  ['재료비 구매','한국미스미','PHS6 포획 저두볼트','CBS6-12',3,'https://kr.misumi-ec.com/vona2/detail/110100142110/?HissuCode=CBS6-12',2013,'F12. 브래킷 카운터보어에서 PHS6 암나사로 약 9 mm 물림.'],
  ['재료비 구매','한국미스미','DIN 레일 300 mm 완제품','MRB-300',3,'https://kr.misumi-ec.com/vona2/result/?Keyword=MRB-300',15000,'E22. 금속 절단 없이 3열 배치.'],

  // One-line vendors retained because they solve a specific compatibility gap.
  ['재료비 구매','Digi-Key Korea','24 VDC 모터전원 접촉기','Finder 22.32.0.024.4320',1,'https://www.digikey.kr/en/products/filter/contactors-electromechanical/969',72339,'E11. 2NO, 24 VAC/DC 코일, 30 VDC DC-1 25 A. 1극 주전원·1극 자기유지.'],
  ['재료비 구매','액티웍스','절연 Ethernet–RS485 게이트웨이','ZMEC485DI / 1000028596',1,'https://actiworks.co.kr/goods/goods_view.php?goodsNo=1000028596',76364,'SG01. HWT905 두 대 전용 Modbus TCP↔RTU. DMC 프로토콜에는 사용하지 않음.'],
  ['재료비 구매','G마켓 케이일레븐홀딩스','상·하부 절대 경사센서','HWT905-RS485 / 3973625857 / 옵션03',2,'https://item.gmarket.co.kr/Item?goodsCode=3973625857',331871,'IS01/02. 12 V 공급, Modbus ID를 한 대씩 0x50/0x51로 설정한 뒤 병렬 연결.'],
];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add('Sheet1');

sheet.getRange('B1:I1').merge();
sheet.getRange('B1').values = [['Rev F 수평유지장치 발주 후보 BOM (2026-10-03)']];
sheet.getRange('B2:I2').values = [['2026 BIZ-Lab 창업클럽 시제품지원 프로그램 지출계획',null,null,null,null,null,'지원금',4000000]];
sheet.getRange('B3:I3').values = [['지출방법','업체명','제품명','모델명','수량','링크','총 가격 (공급가액)','비고']];
sheet.getRange(`B4:I${rows.length + 3}`).values = rows;

const subtotalRow = rows.length + 4;
const vatRow = subtotalRow + 1;
const totalRow = subtotalRow + 2;
const remainingRow = subtotalRow + 3;
sheet.getRange(`B${subtotalRow}:I${remainingRow}`).values = [
  ['공급가 부분합 (상부 브래킷 견적 제외)',null,null,null,null,null,null,'UP-A1/A2/A3 사용자 견적 3건은 합계에서 제외.'],
  ['부가세 10% (상부 브래킷 견적 제외)',null,null,null,null,null,null,'실제 사이트별 VAT·배송비는 결제 화면에서 확인.'],
  ['VAT 포함 합계 (상부 브래킷 견적 제외)',null,null,null,null,null,null,'맞춤 상부 브래킷 3개 가격을 더해야 최종 총액이 됨.'],
  ['지원금 잔여액 (상부 브래킷 견적 제외)',null,null,null,null,null,null,'견적 3건과 배송비를 반영한 뒤 최종 예산 확인.'],
];
sheet.getRange(`H${subtotalRow}:H${remainingRow}`).formulas = [
  [`=SUM(H4:H${rows.length + 3})`],
  [`=ROUND(H${subtotalRow}*10%,0)`],
  [`=SUM(H${subtotalRow}:H${vatRow})`],
  [`=$I$2-H${totalRow}`],
];

// Compact, readable form without the old merged overlay cells.
sheet.getRange(`B1:I${remainingRow}`).format.font = { name: 'Malgun Gothic', size: 10 };
sheet.getRange('B1:I1').format = {
  fill: '#17365D', font: { name: 'Malgun Gothic', size: 15, bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center', verticalAlignment: 'center', rowHeight: 30,
};
sheet.getRange('B2:I2').format = { fill: '#D9EAF7', font: { name: 'Malgun Gothic', size: 10, bold: true }, rowHeight: 24 };
sheet.getRange('B3:I3').format = {
  fill: '#2F75B5', font: { name: 'Malgun Gothic', size: 10, bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center', verticalAlignment: 'center', wrapText: true, rowHeight: 32,
};
sheet.getRange(`B4:I${rows.length + 3}`).format.wrapText = true;
sheet.getRange(`B4:I${rows.length + 3}`).format.verticalAlignment = 'top';
sheet.getRange(`B4:I${rows.length + 3}`).format.rowHeight = 42;
sheet.getRange(`B${subtotalRow}:I${remainingRow}`).format = {
  fill: '#E2F0D9', font: { name: 'Malgun Gothic', size: 10, bold: true }, wrapText: true, rowHeight: 28,
};
sheet.getRange(`B3:I${remainingRow}`).format.borders = { preset: 'all', style: 'thin', color: '#A6A6A6' };

// Vendor blocks alternate subtle fills so contiguous grouping is obvious.
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

// Emphasize the three user-quoted custom parts only.
for (let i = 0; i < rows.length; i += 1) {
  if (rows[i][6] === '사용자 견적') {
    const rowNumber = i + 4;
    sheet.getRange(`B${rowNumber}:I${rowNumber}`).format.fill = '#FFF2CC';
    sheet.getRange(`H${rowNumber}`).format.font = { name: 'Malgun Gothic', size: 10, bold: true, color: '#9C6500' };
  }
}

sheet.getRange(`H4:H${rows.length + 3}`).format.numberFormat = '#,##0"원"';
sheet.getRange(`H${subtotalRow}:H${remainingRow}`).format.numberFormat = '#,##0"원"';
sheet.getRange('I2').format.numberFormat = '#,##0"원"';
sheet.getRange(`F4:F${rows.length + 3}`).format.horizontalAlignment = 'center';
sheet.getRange(`H4:H${remainingRow}`).format.horizontalAlignment = 'right';

const widths = { B: 14, C: 22, D: 31, E: 31, F: 8, G: 48, H: 18, I: 68 };
for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
sheet.freezePanes.freezeRows(3);

workbook.recalculate();
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(outputPath);
console.log(`Saved ${outputPath} with ${rows.length} purchase rows.`);
