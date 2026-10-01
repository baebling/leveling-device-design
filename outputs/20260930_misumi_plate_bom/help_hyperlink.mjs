import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const book = await SpreadsheetFile.importXlsx(await FileBlob.load('outputs/20260927_drill_quote/2026_BIZ-Lab_창업클럽_시제품_재료비관리_드릴비트_추가.xlsx'));
console.log(JSON.stringify(book.help('hyperlink', { include: 'index,examples,notes', maxChars: 3000 })));
