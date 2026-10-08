import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const outputDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = process.cwd();
const sourcePath = path.join(projectDir,'outputs/20261007_bom_mechanical_misumi/2026_BIZ-Lab_재료비관리_RevF_기구류미스미통합_2026-10-07.xlsx');
const outputPath = path.join(outputDir,'2026_BIZ-Lab_재료비관리_RevF_장바구니가격반영_2026-10-08.xlsx');
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sheet = workbook.worksheets.getItem('Sheet1');
if(process.argv.includes('--help-links')){
  console.log(workbook.help('hyperlink',{include:'index,examples,notes',maxChars:5000}).ndjson);
  process.exit(0);
}
if (process.argv.includes('--inspect')) {
  console.log((await workbook.inspect({kind:'table',range:'Sheet1!C68:I78',include:'values,formulas',tableMaxRows:12,tableMaxCols:7,maxChars:3500})).ndjson);
  const preview=await workbook.render({sheetName:'Sheet1',range:'C28:H35',scale:1,format:'png'});
  await fs.writeFile(path.join(outputDir,'source_preview.png'),new Uint8Array(await preview.arrayBuffer()));
  process.exit(0);
}

const evidence=JSON.parse(await fs.readFile(path.join(outputDir,'cart_evidence.json'),'utf8'));
const sourceRows=sheet.getRange('B4:I74').values;
assert.equal(sourceRows.length,71);
const originalTotal=sourceRows.reduce((sum,row)=>sum+Number(row[6]),0);
const changes=[];
const matched=new Set();
const rows=sourceRows.map((row,index)=>{
  const copy=[...row]; const originalRow=index+4;
  const vendor=String(row[1]); const model=String(row[3]); const url=String(row[5]);
  let group, sku;
  if(vendor==='나비엠알오') {group='nav';sku=model.match(/K\d{8}/)?.[0];}
  else if(vendor==='디바이스마트'){group='dm';sku=new URL(url).searchParams.get('no');if(originalRow===29)sku='16499';}
  else if(vendor==='모터뱅크'){group='mb';sku=new URL(url).searchParams.get('goodsNo');}
  else if(vendor.includes('미스미') || vendor.includes('meviy')) {group='mis';sku=model.includes('PHS6')?'PHS6':model.split(' / ')[0];}
  else if(vendor.startsWith('Digi-Key')){group='dm';sku='13113910';}
  else if(vendor.includes('G마켓')){group='gm';sku=model.includes('ZMEC485DI')?'4571273052':'3973625857';}
  assert.ok(group,`Unknown vendor ${vendor}`);
  const item=evidence[group].find(x=>x[0]===sku);
  assert.ok(item,`Missing cart match for row ${originalRow}: ${model}`);
  assert.equal(Number(row[4]),item[1],`Wrong purchase quantity ${model}`);
  const key=`${group}:${sku}`;assert.ok(!matched.has(key),`Duplicate SKU ${key}`);matched.add(key);
  copy[6]=item[2];
  if(originalRow===29){
    copy[3]='Coms C3900 / CAT6 2M / 16499';
    copy[5]='https://www.devicemart.co.kr/goods/view?no=16499';
    copy[7]='CB02. HWT905 Modbus TCP 경로. 승인된 대체: CAT6 UTP RJ45 2 m C3900. 10/8 장바구니 공급가 2,300원, 준비 3~4일.';
  }
  if(vendor.startsWith('Digi-Key')){
    copy[1]='디바이스마트'; copy[5]='https://www.devicemart.co.kr/goods/view?no=13113910';
    copy[7]='E11. 동일 Finder 22.32.0.024.4320. 2NO, 24VAC/DC 코일, 30VDC DC-1 25A. 1극 20A 모터전원·1극 자기유지. 10/8 공급가 78,070원, 구매가능 783개, 준비 4~5일. 해외구매 취소·반품 불가. 공인 안전릴레이 아님.';
  }
  if(group==='gm' && sku==='4571273052'){
    copy[3]='ZMEC485DI / 4571273052'; copy[5]='https://item.gmarket.co.kr/Item?goodsCode=4571273052';
    copy[7]=row[7]+' 10/8 장바구니 VAT 포함 90,000원. 공급가 역산·원단위 반올림.';
  }
  if(group==='gm' && sku==='3973625857')copy[7]=row[7]+' 10/8 옵션03 확인. 2개 합계 VAT 포함 355,060원(10,000원 쿠폰 적용). 공급가 역산·원단위 반올림.';
  if(model.startsWith('MVBLK-'))copy[7]=String(row[7]).replace(/10\/15 출하 표시/g,'10/19 출하 표시').replace('2026-10-04 장바구니 견적','2026-10-08 미스미 견적');
  if(copy[6]!==row[6])changes.push({originalRow,model,newModel:copy[3],oldSupply:row[6],newSupply:copy[6],delta:copy[6]-row[6]});
  return {originalRow,group,sku,values:copy};
});
assert.equal(matched.size,71);
const expectedCounts={nav:7,dm:23,mb:3,mis:36,gm:2};
for(const [group,count]of Object.entries(expectedCounts)){
  const got=rows.filter(r=>r.group===group);
  assert.equal(got.length,count);
  assert.equal(got.reduce((sum,r)=>sum+r.values[6],0),evidence.totals[group].supply);
}
// Preserve the established vendor order. Only move the contactor to the end of the existing DeviceMart block.
const contactor=rows.find(r=>r.originalRow===72);
const ordered=rows.filter(r=>r.originalRow!==72);
ordered.splice(29,0,contactor);
// Move original row objects as well as their values so styles and hyperlinks follow each part.
// The existing DeviceMart last row and contactor row have identical template styles.
for(let row=71;row>=33;row--)sheet.getRange(`B${row+1}:I${row+1}`).copyFrom(sheet.getRange(`B${row}:I${row}`),'all');
sheet.getRange('B33:I33').copyFrom(sheet.getRange('B32:I32'),'all');
sheet.getRange('B4:I74').values=ordered.map(r=>r.values);
// Native external-link destinations require the bounded OOXML compatibility repair below.
// HYPERLINK is documented but not implemented by this runtime's calculation/render engine.
sheet.freezePanes.unfreeze();sheet.freezePanes.freezeRows(39);
sheet.getRange('I75:I78').values=[
  ['2026-10-08 장바구니·미스미 견적 기준 71품목. 메비 4품목은 미스미 금액에 포함. 공급가 역산 품목은 비고 참조.'],
  ['전체 공급가의 10% 반올림. 나비엠알오 VAT는 10% 산출, G마켓 공급가·VAT는 표시 총액에서 역산. 결제·증빙 발급 시 재확인.'],
  ['미스미 712,074원, 디바이스마트 1,241,735원, 모터뱅크 675,840원, 나비엠알오 134,871원, G마켓 445,060원. 현재 배송비 0원, 센서 쿠폰 적용.'],
  ['미스미는 구형 CIMR6-12-0.5 없는 36개 견적 기준. 결제 시 쿠폰·배송비·납기 재확인. 실물 조립·통전시험 완료를 뜻하지 않음.']
];
workbook.recalculate();
assert.equal(sheet.getRange('H75').values[0][0],evidence.totals.all.supply);
assert.equal(sheet.getRange('H77').values[0][0],evidence.totals.all.gross);
assert.equal(sheet.getRange('H78').values[0][0],evidence.totals.all.remaining);
const errorScan=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'final formula error scan',maxChars:2000});
console.log(errorScan.ndjson);
console.log((await workbook.inspect({kind:'table',range:'Sheet1!H75:I78',include:'values,formulas',tableMaxRows:4,tableMaxCols:2,maxChars:3000})).ndjson);
for(const [name,range] of [['updated_items','C27:H36'],['updated_totals','H75:I78']]){
  const preview=await workbook.render({sheetName:'Sheet1',range,scale:1,format:'png'});
  await fs.writeFile(path.join(outputDir,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputPath);
const audit={asOf:evidence.asOf,sourcePath,outputPath,lineCount:71,counts:expectedCounts,oldSupplyTotal:originalTotal,newSupplyTotal:evidence.totals.all.supply,changes,rowMapping:ordered.map((r,index)=>({originalRow:r.originalRow,outputRow:index+4,group:r.group,sku:r.sku})),nativeLinkRepairs:[29,33,73].map(row=>({cell:`G${row}`,target:ordered[row-4].values[5]})),totals:evidence.totals,errorScan:errorScan.ndjson};
await fs.writeFile(path.join(outputDir,'bom_price_audit.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify({outputPath,counts:expectedCounts,changes,totals:evidence.totals.all}));
