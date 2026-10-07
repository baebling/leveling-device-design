import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const sourcePath=path.resolve(here,'../20261007_bom_vendor_consolidation/2026_BIZ-Lab_재료비관리_RevF_구매처통합_2026-10-07.xlsx');
const outputPath=path.join(here,'2026_BIZ-Lab_재료비관리_RevF_기구류미스미통합_2026-10-07.xlsx');
const hash=async p=>crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
const sourceHash=await hash(sourcePath);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const s=wb.worksheets.getItem('Sheet1');
const originals=s.getRange('B4:I74').values;
const rows=originals.map(r=>[...r]);
if(rows.length!==71||rows.some(r=>!r[3])) throw new Error('Unexpected source layout');
const changes=[];
const mi=(family,model)=>`https://kr.misumi-ec.com/vona2/detail/${family}/?HissuCode=${encodeURIComponent(model)}`;
function update(oldModel,fields,reason,evidence={}) {
  const row=rows.find(r=>r[3]===oldModel);
  if(!row||row[1]!=='나비엠알오') throw new Error(`Unexpected source item ${oldModel}`);
  const before=[...row];
  for(const [index,value] of Object.entries(fields)) row[Number(index)]=value;
  changes.push({oldModel,before,after:[...row],vendorChanged:before[1]!==row[1],reason,evidence});
}
update('K92787708',{1:'한국미스미',3:'E-DNF4040BK-700',5:mi('110311379789','E-DNF4040BK-700'),6:32340,
  7:'S01. 국내규격 40×40 경량 흑색, A6063-T5, 700mm×2개. 기존 DNF4040과 슬롯8.3/내폭20.5/깊이13/립4.5mm 동일. 끝단 탭 불필요. 10/7 표시16,170원/개, 참고10/13 출하·재고0. 추가 금속 가공 없음.'},
  '기존 국내규격 흑색 DNF4040 단면·길이·재질 유지',
  {unitSupply:16170,quantity:2,minimumOrder:1,stock:0,referenceShipDate:'2026-10-13',sectionMm:{outer:40,slot:8.3,cavity:20.5,depth:13,lip:4.5},drawing:'https://kr.misumi-ec.com/linked/item/10311379789/img/E-DNF4040_%EC%B9%98%EC%88%98%EB%8F%84.jpg'});
update('K92787705',{1:'한국미스미',3:'E-DNF4040BK-620',5:mi('110311379789','E-DNF4040BK-620'),6:57288,
  7:'S02. S01과 같은 국내규격 흑색 DNF4040, 620mm×4개. 절단공차0.3mm. 기존 외형·슬롯 체결 유지, 끝단 탭 불필요. 10/7 표시14,322원/개, 참고10/13 출하·재고0. 추가 금속 가공 없음.'},
  'S01과 같은 호환 단면 및 기존 620mm 길이 유지',
  {unitSupply:14322,quantity:4,minimumOrder:1,stock:0,referenceShipDate:'2026-10-13'});
update('K92782553',{1:'한국미스미',3:'E-DCBK4035',5:mi('110311380419','E-DCBK4035'),6:5360,
  7:'S05. 국내규격 직각 다이캐스팅 브래킷, 40×35×40mm/t6, 각면9×18 장공. 기존4035 체결·공구 경로 유지. 브래킷8개, 볼트/너트 별도 F01/F06. 10/7 표시670원/개(1~9개), 참고10/14 출하·재고0.'},
  '외형·두께·장공 및 국내규격 계열 일치',
  {unitSupply:670,quantity:8,minimumOrder:1,stock:0,referenceShipDate:'2026-10-14',dimensionsMm:{length:40,width:35,height:40,thickness:6,slot:[9,18]}});
update('K53536280',{1:'한국미스미',3:'CB8-16',4:100,5:mi('110100141750','CB8-16'),6:9800,
  7:'F01. M8×1.25/L16 육각렌치, 크롬몰리브덴강12.9급(기존10.9 이상), 머리Ø13×8/렌치6. 기존36개입→낱개100개. 100개 구간98원/개=9,800원; 36개×522원보다 저렴. 10/7 재고208, 참고10/12. 과도한 조임 금지·체결 토크 상향하지 않음.'},
  '나사·길이·머리 동일, 강도 상향; 기존 수량 이상 주문 중 100개 할인 구간이 더 저렴',
  {unitSupply:98,quantity:100,minimumOrder:1,stock:208,referenceShipDate:'2026-10-12',previousPhysicalQuantity:36,sourceGrade:10.9,targetGrade:12.9,priceForOriginalQuantity:36*522,catalog:'https://kr.misumi-ec.com/pdf/press/2018_pr_997.pdf'});
update('K53536553',{1:'한국미스미',3:'CB8-20',4:100,5:mi('110100141750','CB8-20'),6:9700,
  7:'F03. M8×1.25/L20 육각렌치、12.9급(기존10.9 이상), 머리Ø13×8/렌치6. 기존34개입→낱개100개. 100개 구간97원/개=9,700원; 34개×518원보다 저렴. 10/7 재고795, 참고10/12. 기존 하부판·홀더 체결 적층 유지, 토크 상향 없음.'},
  '나사·길이·머리 동일, 강도 상향; 기존 수량 이상 주문 중 100개 할인 구간이 더 저렴',
  {unitSupply:97,quantity:100,minimumOrder:1,stock:795,referenceShipDate:'2026-10-12',previousPhysicalQuantity:34,sourceGrade:10.9,targetGrade:12.9,priceForOriginalQuantity:34*518,catalog:'https://kr.misumi-ec.com/pdf/press/2018_pr_997.pdf'});
update('K15696523 / M8×12',{1:'한국미스미',3:'HXN-ST-M8-12',5:mi('221000550533','HXN-ST-M8-12'),6:1740,
  7:'F05. SUNCO 스틸4.8급, M8×1.25/L12 전체나사 육각머리(대변13/높이5.5). 축당2개, 총6개. 기존8mm 판 M8 탭·1mm 와셔 유지. 10/7 표시290원/개, 최소1개, 참고10/14·재고0. 렌치볼트로 바꾸지 않고 육각머리 유지.'},
  'LMB-10용 M8×12 전체나사 육각머리 및 기존 적층 유지',
  {unitSupply:290,quantity:6,minimumOrder:1,stock:0,referenceShipDate:'2026-10-14',threadPitchMm:1.25,headAcrossFlatsMm:13,headHeightMm:5.5,targetGrade:4.8,loadScreen:{axialLoadN:750,boltsPerAxis:2,tensileAreaMm2:36.6,nominalStressMpa:750/2/36.6,scope:'Nominal direct load check only; not joint certification or a new strength release'}});
update('K14671419',{1:'한국미스미',3:'E-SPN408',4:100,5:mi('110311380239','E-SPN408'),6:19000,
  7:'F06. 국내규격40용 M8×1.25 스프링너트, 23.5×12×6mm, SAE1018 니켈. 기존100개입→낱개100개 유지. 100개 구간190원/개=19,000원, 최소10개, 참고10/13·재고0. 하부센서2개 포함 배정. 3030용 E-SPN306과 혼용 금지.'},
  '너트 폭·두께·나사 및 국내규격 유지; 길이+0.5mm는 슬롯 내 이동 체결에 영향 없음',
  {unitSupply:190,quantity:100,minimumOrder:10,stock:0,referenceShipDate:'2026-10-13',previousPhysicalQuantity:100,dimensionsMm:{length:23.5,width:12,thickness:6},sectionChecksMm:{cavityWidthMargin:20.5-12,nutSpaceDepthMargin:13-4.5-6}});
update('K06130485',{7:'F04. 나비엠알오 유지: SUS304 M8 평와셔100개입, ID8.5/OD17/t1mm. LMB-10 높이 보정·하부판 체결용. 일반 미스미 M8 와셔 t1.6mm는 기존 적층을 바꾸므로 제외. 같은1mm 치수의 합리적 가격 판매품 미확정.'},
  '높이 보정용1mm 와셔 치수를 보존; 일반1.6mm 후보 제외',
  {previousPhysicalQuantity:100,requiredDimensionsMm:{inside:8.5,outside:17,thickness:1},replacementStatus:'Not confirmed; do not interpret as unavailable from every supplier'});
update('K64647607',{7:'F17. 나비엠알오 유지: LOCTITE243 청색 중강도10mL 1병, 기존8,990원. CBS6-12/PHS6 암나사 등에 소량 사용. 미스미 동급10mL의 현재 주문 가능한 SKU·가격을 확인하지 못해 변경 보류. 강력 영구고정제·다른243 품목으로 대체 금지.'},
  '동급 중강도 소포장 판매 확인 미완료; 원래 제품 유지',
  {quantity:1,volumeMl:10,replacementStatus:'Orderable matching small bottle not confirmed'});
update('K14364804',{7:'F18. 나비엠알오 유지: M4×0.7/L25 합금강 니켈 더블셈스100개입. HWT905에6개 배정, 머리 아래 스프링+평와셔. 미스미 CBST4-25는 현재 검색 정확일치 없음(4-20 이하 후보만 확인). 길이/와셔 구성을 임의 변경하지 않음. 플라스틱 속판·PVC5 관통, 금속 절단 금지.'},
  'M4×25 더블셈스 현재 판매 후보 미확정; 짧은4-20으로 임의 변경하지 않음',
  {previousPhysicalQuantity:100,allocatedSensorQuantity:6,searchUrl:'https://kr.misumi-ec.com/vona2/result/?Keyword=CBST4-25',replacementStatus:'Exact L25 double-SEMS not confirmed'});
update('K06130054',{7:'F19. 나비엠알오 유지: SUS304 M4×0.7, 대변7/높이3.2,50개입1,390원. HWT9056개·기존 속판용 함께 배정. 미스미 HNT1-SUS-M4 동규격350원/개×50=17,500원으로 가격 급증하여 제외. 볼트 사용 수량 부족 없이 기존 포장 유지.'},
  '동규격 미스미 판매는 가능하나 기존50개입 대비 약12.6배 가격이어서 제외',
  {previousPhysicalQuantity:50,candidateUrl:mi('221000544334','HNT1-SUS-M4'),candidateUnitSupply:350,candidateQuantity:50,candidateSupply:17500,replacementStatus:'Compatible but rejected on cost'});

const vendorOrder=['나비엠알오','디바이스마트','모터뱅크','한국미스미','한국미스미 meviy','Digi-Key Korea','액티웍스','G마켓 케이일레븐홀딩스'];
rows.sort((a,b)=>vendorOrder.indexOf(a[1])-vendorOrder.indexOf(b[1]));
s.getRange('B1').values=[['Rev F 수평유지장치 BOM — 기구류 미스미 통합 (2026-10-07)']];
s.getRange('G2').values=[['기구류11개 검토:7개 미스미 변경 / 나비엠알오7개 유지 / 장바구니 미변경']];
s.getRange('B4:I74').values=rows;
s.getRange('I75:I78').values=[['10/7 미스미7개 표시가격+기타 기존 가격. 확정 결제액 아님.'],['전체 공급가의10% 반올림 추정. 사이트별 계산·배송비 차이 있음.'],['추가 금속 가공 없음. 구매처 변경7건; 미교체 기구4건 사유는 비고 참조.'],['M8 볼트는 각100개 할인 적용. 실제 조립·통전시험 완료를 뜻하지 않음.']];
let previous=null,block=-1;
rows.forEach((row,i)=>{
  if(previous!==row[1]) {previous=row[1];block++;}
  const range=s.getRange(`B${i+4}:I${i+4}`);
  range.format.rowHeight=92;
  range.format.wrapText=true;
  range.format.verticalAlignment='top';
  range.format.fill=block%2?'#F5F9FC':'#FFFFFF';
  if(changes.some(c=>c.after[3]===row[3])) s.getRange(`D${i+4}:I${i+4}`).format.fill='#FFF2CC';
});
s.getRange('G4:G74').format.font={name:'Malgun Gothic',size:9,color:'#0563C1'};
s.getRange('B75:I78').format.rowHeight=44;
s.getRange('B75:I78').format.wrapText=true;
s.getRange('H4:H78').format.numberFormat='#,##0"원"';
wb.recalculate();
const supply=rows.reduce((n,r)=>n+r[6],0);
if(s.getRange('H75').values[0][0]!==supply) throw new Error('Supply sum mismatch');
const firstChanged=rows.findIndex(r=>r[3]==='E-DNF4040BK-700')+4;
for(const [name,range] of [['remaining','B4:I10'],['mechanical',`B${firstChanged}:I${firstChanged+6}`],['total','B75:I78']]){
  const preview=await wb.render({sheetName:'Sheet1',range,scale:1,format:'png'});
  await fs.writeFile(path.join(here,`${name}_preview.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(outputPath);
if(await hash(sourcePath)!==sourceHash) throw new Error('Source changed');
const vendorTotals=Object.fromEntries(vendorOrder.map(v=>[v,{rows:rows.filter(r=>r[1]===v).length,supply:rows.filter(r=>r[1]===v).reduce((n,r)=>n+r[6],0)}]));
const result={sourcePath,sourceHash,outputPath,originals,rows,changes,supply,vat:s.getRange('H76').values[0][0],total:s.getRange('H77').values[0][0],remaining:s.getRange('H78').values[0][0],vendorTotals,previousSupply:originals.reduce((n,r)=>n+r[6],0),cartChanged:false,scope:'Mechanical procurement substitutions only; no CAD, fabrication release, powered-test or safety status changed'};
await fs.writeFile(path.join(here,'bom_change_manifest.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({...result,originals:originals.length,rows:rows.length,changes:changes.length}));
