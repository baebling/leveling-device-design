import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
const sourcePath = path.resolve(here,'../20261007_bom_three_issue_correction/2026_BIZ-Lab_재료비관리_RevF_3개이슈수정_2026-10-07.xlsx');
const outputPath = path.join(here,'2026_BIZ-Lab_재료비관리_RevF_구매처통합_2026-10-07.xlsx');
const hash = async p => crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
const sourceHash = await hash(sourcePath);
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const s = wb.worksheets.getItem('Sheet1');
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:1000})).ndjson);
const originals = s.getRange('B4:I74').values;
const rows = originals.map(r=>[...r]);
if(rows.length!==71 || rows.some(r=>!r[3])) throw new Error('Unexpected source BOM layout');
const changes=[];
const mi = (family,model) => `https://kr.misumi-ec.com/vona2/detail/${family}/?HissuCode=${encodeURIComponent(model)}`;
function update(oldModel, fields, reason) {
  const row=rows.find(r=>r[3]===oldModel);
  if(!row) throw new Error(`Missing source model: ${oldModel}`);
  const before=[...row];
  for(const [col,value] of Object.entries(fields)) row[Number(col)]=value;
  changes.push({oldModel,before,after:[...row],reason,vendorChanged:before[1]!==row[1]});
}
update('BC-AGP-507025 / K25262371',{1:'한국미스미',3:'BC-AGP-507025',5:mi('110400233420','BC-AGP-507025'),6:91620,
  7:'E06A. 동일 BOXCO 모델, 530×730×255mm. 플라스틱 타공만 허용. 속판 별도 E06B. 10/7 확인 91,620원/개(VAT 별도), 참고 10/15 출하·재고0. 구매처만 변경.'},'동일 모델로 구매처 통합; 기존 함체 형상 유지');
update('5070P / K25264419',{1:'한국미스미',3:'5070P',5:mi('222005921564','5070P'),6:11770,
  7:'E06B. 동일 BOXCO 플라스틱 속판, 460×660mm. E06A용. 10/7 확인 11,770원/개(VAT 별도), 참고 10/15 출하·재고0. 기존 설계품 변경 없음.'},'동일 모델로 구매처 통합');
update('K08345728',{1:'한국미스미',3:'DYP-G16B-B-3M-1.5',5:mi('222005934085','DYP-G16B-B-3M-1.5'),6:5376,
  7:'E07. 동양 KS 접지 코드, 250V/16A, IEC53 1.5SQ×3C, 흑색3m. 최소1개. 10/7 표시 할인 공급가5,376원, 재고품 1일째. 단말 피복 제거·필요 압착 후 기존 AC 입력 결선, PE→RSP FG. 할인 변동 가능.'},'정격을 유지하며 미스미 1개 주문 가능한 옵션 선정');
update('K92843703',{1:'디바이스마트',3:'CBAZY UL1007 24AWG 6색 60M / 12375531',5:'https://www.devicemart.co.kr/goods/view?no=12375531',6:24000,
  7:'E16. 6색×10m=60m 연선 제어선 키트. 공급가24,000원(VAT 포함26,400원). 평균1~2일; 품절 시4주 안내. 버튼·알림·엔코더 저전류용. 모터·AC 주전원 및 RS485 통신 케이블 대체 금지.'},'동일 전선 규격·구성의 국내 판매 키트로 변경');
update('K22571959',{1:'한국미스미',2:'PG13.5 케이블 글랜드 (낱개)',3:'BC-PG13.5L-G-N',4:10,5:mi('222302627938','BC-PG13.5L-G-N'),6:4700,
  7:'E18. BOXCO PG13.5, 케이블 외경6~11mm, 나사길이15mm, D1=20.4mm. 낱개470원×10개=4,700원. 기존10개입 수량 유지. 10/7 재고2/최대45, 참고10/12(수량10 납기는 주문 시 확인). 기존품6~12mm보다 상한1mm 작음: 실제 외경 확인 후 플라스틱 타공. 소선 여러 가닥 밀봉용 아님.'},'동일 PG13.5·10개 수량 유지; 외경 적용 범위 차이 명시');
update('K01415707',{1:'한국미스미',2:'케이블 타이 200mm (100개입)',3:'NMT-200KTW / 100EA',5:mi('222301892638','NMT-200KTW'),6:3080,
  7:'E20. NETMATE 백색 4.8×200mm, 1팩=100개. 10/7 공급가3,080원, 참고4일째. 기존 동일 치수 흑색1,000개입에서 실내 PoC용100개입으로 축소. 체결부 하중 지지용으로 사용하지 않음.'},'치수 유지, 실내 시제품용 소포장으로 과다 구매 축소');
update('K40799280',{1:'한국미스미',3:'KS-ELETAPE-016MM-19MM-10M-BLACK',5:mi('223006497889','KS-ELETAPE-016MM-19MM-10M-BLACK'),6:1170,
  7:'E21. 태영 KS PVC 전기절연테이프 흑색, 0.16×19mm×10m. 최소1롤, 390원×3롤=1,170원(VAT 별도). 재고품1일째. 보조 절연·표시용; 주전원 접속은 지정 단자 사용.'},'미스미 낱개 구매 가능한 동급 보조 절연재');
update('K52569152',{7:'E17. 기존 열수축 튜브 키트 유지(공급가10,990원). 미스미 EA944BH-21은55,670원으로 약5배여서 이번 통합에서 제외. 절연 보조·표시 마감용.'},'대체품 가격 급증을 피하여 나비엠알오 유지');
update('K55027039',{7:'E23. 기존 녹/황 TFR-GV 2.5SQ, 1m 단위3개 유지. RSP FG 등 보호접지 경로. 디바이스마트 후보는 제목2.5SQ/설명2.0SQ 불일치로 제외. 본 행 금액은 기존 BOM 가격이며 결제 시 갱신.'},'전선 규격 불일치 후보를 제외하여 나비엠알오 유지');
update('14 AWG 실리콘 전선 세트 / K92854706',{7:'E15B. 기존14AWG 실리콘 세트 유지. DMC-200 6A 제한×3축 24V 분기용; 공통 주전원4SQ 대체 아님. 디바이스마트 FIT0583은 적/흑 각1m·해외배송으로 구성/납기 불리. 본 행은 기존 가격.'},'국내 공급·기존 구성 유지, 해외 소포장 후보 제외');
const vendorOrder=['나비엠알오','디바이스마트','모터뱅크','한국미스미','한국미스미 meviy','Digi-Key Korea','액티웍스','G마켓 케이일레븐홀딩스'];
if(rows.some(r=>!vendorOrder.includes(r[1]))) throw new Error('Unknown source vendor');
rows.sort((a,b)=>vendorOrder.indexOf(a[1])-vendorOrder.indexOf(b[1]));
s.getRange('B1').values=[['Rev F 수평유지장치 BOM — 구매처 통합 (2026-10-07)']];
s.getRange('G2').values=[['7개 품목 구매처 변경 / 나비엠알오 14개 유지 / 장바구니 미변경']];
s.getRange('B4:I74').values=rows;
s.getRange('I75:I78').values=[['10/7 대체품 표시 가격+기타 기존 BOM 가격. 확정 결제액 아님.'],['사이트별 반올림·배송비 차이 있음.'],['배송비 제외. 구매처 변경7건, 추가 금속 가공 없음.'],['타이100개입 축소 반영. 공구는 기존 차용 방침 유지.']];
s.getRange('B4:I74').format.fill='#FFFFFF';
let previous=null,block=-1;
rows.forEach((row,i)=>{
  if(previous!==row[1]) {previous=row[1];block++;}
  const range=s.getRange(`B${i+4}:I${i+4}`);
  range.format.rowHeight=82;
  range.format.wrapText=true;
  range.format.verticalAlignment='top';
  if(block%2) range.format.fill='#F5F9FC';
  if(changes.some(c=>c.after[3]===row[3])) s.getRange(`D${i+4}:I${i+4}`).format.fill='#FFF2CC';
});
s.getRange('G4:G74').format.font={name:'Malgun Gothic',size:9,color:'#0563C1'};
s.getRange('B75:I78').format.rowHeight=44;
s.getRange('B75:I78').format.wrapText=true;
s.getRange('H4:H78').format.numberFormat='#,##0"원"';
s.getRange('G:G').format.columnWidth=48;
s.getRange('I:I').format.columnWidth=68;
wb.recalculate();
const supply=rows.reduce((n,r)=>n+r[6],0);
if(s.getRange('H75').values[0][0]!==supply) throw new Error('Supply total mismatch');
for(const [name,range] of [['remaining','B4:I17'],['replacements','B43:I48'],['total','B75:I78']]){
  const preview=await wb.render({sheetName:'Sheet1',range,scale:1,format:'png'});
  await fs.writeFile(path.join(here,`${name}_preview.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'formula errors',maxChars:2000})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(outputPath);
if(await hash(sourcePath)!==sourceHash) throw new Error('Source workbook changed');
const vendorTotals=Object.fromEntries(vendorOrder.map(v=>[v,{rows:rows.filter(r=>r[1]===v).length,supply:rows.filter(r=>r[1]===v).reduce((n,r)=>n+r[6],0)}]));
const result={sourcePath,sourceHash,outputPath,rows,originals,changes,supply,vat:s.getRange('H76').values[0][0],total:s.getRange('H77').values[0][0],remaining:s.getRange('H78').values[0][0],vendorTotals,previousSupply:originals.reduce((n,r)=>n+r[6],0),cartChanged:false,scope:'Procurement consolidation only; no powered test or new mechanical release'};
await fs.writeFile(path.join(here,'bom_change_manifest.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({...result,rows:rows.length,originals:originals.length,changes:changes.length}));
