// Restore cached summary values after native-hyperlink repair while retaining
// exact hyperlink relationships in the existing workbook.
import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const path = './2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx';
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
workbook.recalculate();
const view = await workbook.render({ sheetName: 'Sheet1', range: 'B70:I81', scale: 1.2, format: 'png' });
await fs.writeFile('./revf_hold_rows_final.png', new Uint8Array(await view.arrayBuffer()));
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(path);
console.log('Recalculated Rev F summary and retained existing hyperlink relationships');
