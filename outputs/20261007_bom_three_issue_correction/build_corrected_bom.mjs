import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
const sourcePath = path.resolve(here, '../20261004_meviy_quote_bom/2026_BIZ-Lab_재료비관리_RevF_meviy견적반영_2026-10-04.xlsx');
const outputPath = path.join(here, '2026_BIZ-Lab_재료비관리_RevF_3개이슈수정_2026-10-07.xlsx');
const source = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const originals = source.worksheets.getItemAt(0).getRange('B4:I66').values;
const rows = originals.map(r => [...r]);
const changes = [];
function change(model, fields) {
  const row = rows.find(r => r[3] === model);
  if (!row) throw new Error(`Missing ${model}`);
  const before = [...row];
  for (const [i, value] of Object.entries(fields)) row[Number(i)] = value;
  changes.push({oldModel:model, before, after:[...row]});
}
const dm = n => `https://www.devicemart.co.kr/goods/view?no=${n}`;
const misumi = (family, model) => `https://kr.misumi-ec.com/vona2/detail/${family}/?HissuCode=${model}`;
change('3.5~5.5SQ', {1:'디바이스마트', 2:'주전원 리드 접속 레버 커넥터', 3:'WAGO 221-615 / 14954324', 4:5,
  5:dm(14954324), 6:10500, 7:'E24. 2개 사용+최소주문 잔여 3개. 0.5~6SQ 연선, 14AWG↔4SQ 각 구멍에 한 가닥. 20A 퓨즈 유지. 2,100원/개, 평균 1주. 공구 불필요.'});
change('K92839991', {1:'디바이스마트', 2:'페룰 단자 세트 (압착공구 없음)', 3:'PVMC PV2 / 16055797',
  5:dm(16055797), 6:8000, 7:'E19. E2508(14AWG), E4009(4SQ) 포함 1,200개. 공구 미포함: 0.25~6SQ용 전용 압착기 차용. WAGO는 페룰·납땜 없이 연선 직접 삽입. 평균 1주.'});
// The former generic red/black set is now two orderable metre-length items.
change('KIV 4SQ, 각 2 m', {1:'디바이스마트', 2:'주전원 KIV 4SQ 적색 2 m', 3:'KIV 4.0SQ 빨강 / 7182', 4:2,
  5:dm(7182), 6:8400, 7:'E15A-R. 1m 단위 2개, 2m 한 줄 절단 옵션 선택. 4,200원/m, 평균 1~2일. 20A 주전원 경로. 절단품 반품 불가.'});
change('WAGO 221-415, 10개입', {2:'저전류 제어선 레버 커넥터 (25개입)', 3:'WAGO 221-415 / 14954315 / 25EA',
  5:dm(14954315), 6:34000, 7:'E25. 0.14~4SQ 연선. 24AWG 제어선은 이 제품 사용(221-615 최소 0.5SQ 미달). 1팩=25개, 평균 1주.'});
change('AUTO-FUSE 32V 20A', {3:'11512 / AUTO-FUSE 32V 20A', 5:dm(11512),
  7:'E09M. 최소주문 10개, 100원/개. 1개 사용+9개 잔여. 32V ATO, 20A 홀더의 정격을 초과하는 퓨즈로 올리지 않음. 평균 1~2일.'});
change('E-DNF3030-6-700', {3:'E-DNF3030-700', 5:misumi('110311379609','E-DNF3030-700'), 6:15260,
  7:'S03. 30/60 국내규격, 공장 절단 700mm. 기존 -6-는 주문 형번 오류로 삭제. 7,630원/개, 참고 10/13 출하. 단면/길이 변경 없음.'});
change('E-DNF3030-6-640', {3:'E-DNF3030-640', 5:misumi('110311379609','E-DNF3030-640'), 6:27904,
  7:'S04. 30/60 국내규격, 공장 절단 640mm. 6,976원/개, 참고 10/13 출하. 단면/길이 변경 없음.'});
change('E-SPN306', {4:24, 5:misumi('110311380239','E-SPN306'), 6:5040,
  7:'F07. 코너 16+상부판 6+상부센서 2=24개。하부 4040 센서는 기존 K14671419의 M8 너트 2개 사용. 최소주문 10, 210원/개.'});
change('E-DCBK3025', {5:misumi('110311380419','E-DCBK3025')});
change('CB6-12', {5:misumi('110100141750','CB6-12')});
change('CB6-18', {5:misumi('110100141750','CB6-18'), 7:'F02B. 9mm 판+3030 슬롯립 2.5mm 기준 공칭 나사 진입 6.5mm. 최종 체결 시 슬롯 바닥에 닿지 않는지 확인.'});
change('HCDGH6-35', {3:'HCDGH6-40', 5:misumi('110300095750','HCDGH6-40'), 6:6306,
  7:'F08. 40mm 유효길이, E링 동봉. 4+아이20+1.5+볼9+4+얇은심 명목1=39.5mm. 실측 축방향 유격 0.2~0.5mm로 심 조절. 2,102원/개. 강도 향상 의미 아님.'});
change('WSSB10-6-4', {2:'핀 머리·E링쪽 스페이서 와셔', 4:6, 6:8820,
  7:'F08A. 축당 머리쪽 1+E링쪽 1=2개, 총 6개. OD10/ID6/T4. 아이–볼 중심 편심 16mm 유지. 1,470원/개.'});
change('WSSB10-6-1.5', {4:5, 6:7350,
  7:'F08B. 관절 볼쪽 3개+상부센서 M6 볼트 머리 밑 2개. 하부센서는 기존 M8 평와셔 사용. OD10/ID6/T1.5, 1,470원/개.'});
change('CBS6-12', {7:'F12. 중앙 Ø11×4.5 카운터보어의 잔여 판두께 4.5mm. PHS6 공칭 물림 12−4.5=7.5mm(기존 약9mm 표기 정정), 나사고정제 소량.'});
change('MRB-300', {5:misumi('110500152560','MRB-300'), 6:49095, 7:'E22. 300mm 완제품×3, 금속 절단 없음. 기존 5,000원/개 추정 정정→16,365원/개. 10/7 참고 10/14 출하, 최대주문50/재고0/판매종료예정 경고. 결제 시 공급 가능 여부 확인.'});
change('K14671419', {7:'F06. 기존 포장 유지. 하부 프레임·A1~A3 외 하부센서 장착 M8 슬롯너트 2개 배정. 3030용 E-SPN306과 혼용하지 않음.'});
change('Finder 22.32.0.024.4320', {5:'https://www.digikey.kr/ko/products/detail/finder-relays-inc/22-32-0-024-4320/10055786', 6:65302,
  7:'E11. 2NO, 24VAC/DC 코일, 30VDC DC-1 25A. 1극 20A 모터전원·1극 자기유지. 10/7 표시 65,302원, 재고 783개. 공인 안전릴레이 아님.'});
change('K14364804', {7:'F18. 기존 포장 유지. 플라스틱 속판 외에 HWT905 고정 6개 사용(M4×25, 센서 귀4+PVC5 관통), 볼트 머리는 판 아래. 공구 차용, 금속 볼트 절단 금지.'});
change('K06130054', {7:'F19. 기존 포장 유지. HWT905 2대에 M4 너트 6개 추가 사용. 포장 수량에서 속판용과 함께 배정.'});
const added = [
  ['재료비 구매','디바이스마트','주전원 KIV 4SQ 검정 2 m','KIV 4.0SQ 검정 / 7181',2,dm(7181),8400,'E15A-B. 1m 단위 2개, 2m 한 줄 절단 옵션. 4,200원/m, 평균 1~2일. 공통 0V.'],
  ['재료비 구매','한국미스미','상부 핀 미세조정 심 0.1mm','CIMR6-10-0.1',9,misumi('110302677870','CIMR6-10-0.1'),6300,'F08C. 축당 최대 3개(0.3mm), 필요한 만큼만 삽입. 700원/개, 참고 10/13 출하.'],
  ['재료비 구매','한국미스미','상부 핀 미세조정 심 0.5mm','CIMR6-10-0.5',12,misumi('110302677870','CIMR6-10-0.5'),8400,'F08D. 축당 최대 4개(2mm). 명목은 2개 사용. 700원/개, 실측 0.2~0.5mm 유격 우선.'],
  ['재료비 구매','한국미스미','상·하부 센서 장착용 PVC 판','ENBT-100-100-5',2,misumi('110302063110','ENBT-100-100-5'),32140,'IS03. 100×100×5, 상하 각1장. 플라스틱 타공만 수행. 16,070원/개, 참고 10/14 출하. 센서 Ø4.2×3+프레임 관통홀×2.'],
  ['재료비 구매','한국미스미','상부센서 M6×25 볼트','CB6-25',2,misumi('110100141750','CB6-25'),650,'IS04. 상부 3030용 2개. PVC5+간격재10+와셔1.5+립2.5, 공칭 나사진입6mm. 325원/개.'],
  ['재료비 구매','한국미스미','상부센서 5mm 기성 간격재','WSSB10-6-5',4,misumi('110302677010','WSSB10-6-5'),5840,'IS05. 상부 2곳×각2개=4개, 높이10mm. 1,460원/개. 하부 4040은 M8 별도 간격재 사용.'],
  ['재료비 구매','한국미스미','하부센서 M8×25 볼트','CB8-25',2,misumi('110100141750','CB8-25'),1040,'IS06. 하부 4040용 2개. PVC5+간격재10+기존 M8 와셔. 기존 M8 슬롯너트 사용。520원/개, 참고 10/8 출하. 나사 바닥 접촉·판 휨 없이 체결.'],
  ['재료비 구매','한국미스미','하부센서 5mm 기성 간격재','WSSB12-8-5',4,misumi('110302677010','WSSB12-8-5'),5840,'IS07. 하부 2곳×각2개=4개, 높이10mm. OD12/ID8. 1,460원/개.'],
];
rows.push(...added);
const vendorOrder = ['나비엠알오','디바이스마트','모터뱅크','한국미스미','한국미스미 meviy','Digi-Key Korea','액티웍스','G마켓 케이일레븐홀딩스'];
rows.sort((a,b) => vendorOrder.indexOf(a[1]) - vendorOrder.indexOf(b[1]));
const wb = Workbook.create(), s = wb.worksheets.add('Sheet1');
const end = rows.length + 3, subtotal = end + 1, final = subtotal + 3;
s.getRange('B1:I1').merge();
s.getRange('B1').values = [['Rev F 수평유지장치 BOM — 3개 이슈 수정 (2026-10-07)']];
s.getRange('B2:I2').values = [['2026 BIZ-Lab 시제품 재료비',null,null,null,null,'추가 금속가공 없음 / 변경품 가격 갱신 / 기타 기존 가격','지원금',4000000]];
s.getRange('B3:I3').values = [['지출방법','업체명','제품명','모델명','수량','링크','총 가격 (공급가액)','비고']];
s.getRange(`B4:I${end}`).values = rows;
s.getRange(`B${subtotal}:I${final}`).values = [
 ['공급가 부분합',null,null,null,null,null,null,'10/7 변경품 가격+10/4 meviy 견적+기타 기존 BOM 가격. 확정 결제액 아님.'],
 ['부가세 10% 추정',null,null,null,null,null,null,'사이트별 반올림·배송비 차이 있음.'],
 ['VAT 포함 추정 합계',null,null,null,null,null,null,'배송비 제외. 추가 금속 가공품 구매 없음.'],
 ['지원금 잔여 추정액',null,null,null,null,null,null,'전용 페룰 압착기·드릴비트 등 공구는 차용(미구매).'],
];
s.getRange(`H${subtotal}:H${final}`).formulas = [[`=SUM(H4:H${end})`],[`=ROUND(H${subtotal}*10%,0)`],[`=SUM(H${subtotal}:H${subtotal+1})`],[`=$I$2-H${subtotal+2}`]];
s.getRange(`B1:I${final}`).format.font = {name:'Malgun Gothic',size:10};
s.getRange('B1:I1').format = {fill:'#17365D',font:{name:'Malgun Gothic',size:15,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:30};
s.getRange('B2:I2').format = {fill:'#D9EAF7',font:{name:'Malgun Gothic',size:10,bold:true},rowHeight:36,wrapText:true};
s.getRange('B3:I3').format = {fill:'#2F75B5',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:32,wrapText:true};
s.getRange(`B4:I${end}`).format = {wrapText:true,verticalAlignment:'top',rowHeight:72};
s.getRange(`B${subtotal}:I${final}`).format = {fill:'#E2F0D9',font:{name:'Malgun Gothic',size:10,bold:true},rowHeight:44,wrapText:true};
s.getRange(`B3:I${final}`).format.borders = {preset:'all',style:'thin',color:'#A6A6A6'};
let block=-1, vendor=null;
rows.forEach((r,i)=>{if(r[1]!==vendor){vendor=r[1];block++;} if(block%2) s.getRange(`B${i+4}:I${i+4}`).format.fill='#F5F9FC';
 if(changes.some(c=>c.after[3]===r[3])||added.includes(r)) s.getRange(`D${i+4}:I${i+4}`).format.fill='#FFF2CC';});
s.getRange(`G4:G${end}`).format.font = {name:'Malgun Gothic',size:9,color:'#0563C1'};
s.getRange(`H4:H${final}`).format.numberFormat = '#,##0"원"';
s.getRange('I2').format.numberFormat = '#,##0"원"';
s.getRange(`F4:F${end}`).format.horizontalAlignment='center';
s.getRange(`H4:H${final}`).format.horizontalAlignment='right';
for(const [c,w] of Object.entries({B:14,C:22,D:31,E:31,F:8,G:48,H:18,I:68})) s.getRange(`${c}:${c}`).format.columnWidth=w;
s.freezePanes.freezeRows(3);
wb.recalculate();
const expected=rows.reduce((n,r)=>n+r[6],0), actual=s.getRange(`H${subtotal}`).values[0][0];
if(expected!==actual) throw new Error('Subtotal mismatch');
for (const [name, keyword] of [['main','WAGO 221-615'],['joint','HCDGH6-40'],['sensor','ENBT-100']]) {
 const idx=rows.findIndex(r=>r[3].includes(keyword));
 const preview=await wb.render({sheetName:'Sheet1',range:`B${Math.max(4,idx+3)}:I${Math.min(end,idx+7)}`,scale:1.05,format:'png'});
 await fs.writeFile(path.join(here,`bom_${name}_preview.png`),new Uint8Array(await preview.arrayBuffer()));
}
const preview=await wb.render({sheetName:'Sheet1',range:`B${subtotal}:I${final}`,scale:1.1,format:'png'});
await fs.writeFile(path.join(here,'bom_total_preview.png'),new Uint8Array(await preview.arrayBuffer()));
const errorScan=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'formula errors'});
console.log(errorScan.ndjson);
const exported=await SpreadsheetFile.exportXlsx(wb); await exported.save(outputPath);
const result={sourcePath,outputPath,rows,changes,added,subtotalRow:subtotal,lastRow:final,supply:actual,vat:s.getRange(`H${subtotal+1}`).values[0][0],total:s.getRange(`H${subtotal+2}`).values[0][0],remaining:s.getRange(`H${final}`).values[0][0]};
await fs.writeFile(path.join(here,'bom_change_manifest.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({...result,rows:rows.length,changes:changes.length,added:added.length}));
