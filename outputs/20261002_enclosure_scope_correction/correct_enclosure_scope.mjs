import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root = process.cwd();
const source = path.join(root, 'outputs', '20261001_reve_bom_audit',
  '2026_BIZ-Lab_재료비관리_RevE_검수수정.xlsx');
const outputDir = path.join(root, 'outputs', '20261002_enclosure_scope_correction');
const dest = path.join(outputDir, '2026_BIZ-Lab_재료비관리_RevE_가공범위정정.xlsx');

const book = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheet = book.worksheets.getItem('Sheet1');
const get = address => sheet.getRange(address).values[0][0];
if (!String(get('I24')).startsWith('E06. SL902') ||
    !String(get('I45')).startsWith('E22.') ||
    get('E45') !== '12538843 / JTRN-4-1M') {
  throw new Error('BOM row identity changed; refusing to edit.');
}

for (const [name, range] of [
  ['before_enclosure.png', 'B22:I25'],
  ['before_din.png', 'B43:I46'],
]) {
  const blob = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outputDir, name), new Uint8Array(await blob.arrayBuffer()));
}

sheet.getRange('I24').values = [[
  'E06. SL902 ABS 함체·플라스틱 속판의 버튼/케이블/장착 타공 가능. 400×500×155 mm는 외형. 속판 유효치수·문 간섭·PSU 통풍 확인 전 홀 좌표와 발주 보류. 철제 ES 후보의 현장 타공은 금지.',
]];
sheet.getRange('D45').values = [['35 mm DIN 레일 (1 m 절단 필요·사용 보류)']];
sheet.getRange('I45').values = [[
  'E22. JTRN-4-1M 금속 레일은 함체에 맞추려면 현장 절단이 필요해 사용 보류. 미스미 MRB 길이지정 완제품 등으로 대체하되 국내 주문옵션·가격·장착홀 확인 전 확정하지 않는다.',
]];

book.recalculate();
const result = await book.inspect({kind: 'region', sheetId: 'Sheet1', range: 'B43:I46',
  maxChars: 2500, tableMaxRows: 4, tableMaxCols: 8});
await fs.writeFile(path.join(outputDir, 'changed_region.ndjson'), result.ndjson);
const errors = await book.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: {useRegex: true, maxResults: 100},
  summary: 'enclosure scope correction formula error scan',
});
await fs.writeFile(path.join(outputDir, 'formula_errors.ndjson'), errors.ndjson);
for (const [name, range] of [
  ['after_enclosure.png', 'B22:I25'],
  ['after_din.png', 'B43:I46'],
]) {
  const blob = await book.render({sheetName: 'Sheet1', range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outputDir, name), new Uint8Array(await blob.arrayBuffer()));
}

const exported = await SpreadsheetFile.exportXlsx(book);
await exported.save(dest);
console.log(JSON.stringify({dest, editedCells: ['I24', 'D45', 'I45'],
  total: get('H73'), errorScan: errors.ndjson.slice(0, 500)}));
