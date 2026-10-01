import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
import fs from 'node:fs/promises';

const target = 'outputs/20260930_misumi_plate_bom/2026_BIZ-Lab_창업클럽_시제품_재료비관리_미스미판재_반영.xlsx';
const book = await SpreadsheetFile.importXlsx(await FileBlob.load(target));
book.recalculate();
const preview = await book.render({ sheetName: 'Sheet1', range: 'B59:I71', scale: 1, format: 'png' });
await fs.writeFile('outputs/20260930_misumi_plate_bom/plate_bom_preview.png', new Uint8Array(await preview.arrayBuffer()));
const result = await SpreadsheetFile.exportXlsx(book);
await result.save(target);
