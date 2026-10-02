import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load('./2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx'));
for (const [range, name] of [
  ['B62:I73', 'revf_ball_washer_priced_area.png'],
  ['B74:I82', 'revf_ball_washer_hold_area.png'],
]) {
  const preview = await workbook.render({ sheetName: 'Sheet1', range, scale: 1, format: 'png' });
  await fs.writeFile(`./${name}`, new Uint8Array(await preview.arrayBuffer()));
  console.log(`Rendered ${range} to ${name}`);
}
