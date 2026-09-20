import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const workDir = path.join(root, ".superpowers", "sdd", "2026-09-20-reve-z15-rebaseline", "task4_workbook");
const payload = JSON.parse(await fs.readFile(path.join(workDir, "bom_data.json"), "utf8"));
const outputPath = path.join(root, "procurement", "reve_portenta_order_bom_2026-09-18.xlsx");
const verificationDir = path.join(workDir, "verification");
const { rows, known_price_subtotal: knownSubtotal, planning_allowance: allowance } = payload;

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("BOM");
sheet.showGridLines = false;
sheet.freezePanes.freezeRows(8);

sheet.mergeCells("A1:N1");
sheet.mergeCells("A2:N2");
sheet.mergeCells("A4:N4");
sheet.mergeCells("A5:N5");
sheet.mergeCells("A6:N6");
sheet.getRange("A1").values = [["Rev E | Portenta / DMC-200 HMI-less 발주 검토 BOM"]];
sheet.getRange("A2").values = [["공개형 자중 PoC · 명령 Z 0–50 mm (물리 Z 15–65 mm) · laptop START 후 작동 · 내장 리미트만 사용 · 구매 승인 문서 아님"]];
sheet.getRange("A3").values = [["알려진 표시가 소계 (AL01 충당 및 비가격 hold 제외)", null, null, null, knownSubtotal, null, null, "판정 보류", null, null, "표시가 기반 참고값이며 공급처 견적·장바구니 합계가 아님", null, null, null]];
sheet.getRange("A4").values = [["구매 릴리스: HOLD_VENDOR_REPLY | 모든 checkout은 차단됨. HMI, HMI 배송, HMI USB, KC522 리피터는 HMI-less 구성에서 제거."]];
sheet.getRange("A5").values = [["비가격 hold: SG01(ICP DAS tGW-715i-T)은 국내 견적·재고·카드결제 미확인. E04 24 V 30 A급 PSU는 SKU·정격 자료 미확정."]];
sheet.getRange("A6").values = [[`AL01 PC01 수입·운임 충당 ${allowance.toLocaleString("ko-KR")}원은 계획 가정이며 주문품·공급처 견적이 아님. MV01/MV02는 독립 Z 검증용이며 제어 피드백이 아님.`]];

const headers = [["구분", "ID", "품목", "규격 / 상품번호", "공급처", "사용", "주문", "단위", "표시가 / 충당", "계획금액", "품목 상태 / 납기", "조립·검증 / 출하 주의", "", "구매 URL / 증빙"]];
sheet.getRange("A8:N8").values = headers;
const values = rows.map((r) => [
  r["발주구분"], r.ID, r["품목"], r["규격"], r["공급처"], r["사용수량"], r["주문수량"], r["주문단위"],
  r["단가(VAT포함)"], r["확장금액"], `${r["주문상태"]}\n${r["납기"]}`,
  `${r["CAD/조립확인"]}\n[출하] ${r["출하구분"]}`, "", `${r["구매URL"]}\n${r["증빙"]}`,
]);
const firstDataRow = 9;
const lastDataRow = firstDataRow + values.length - 1;
sheet.getRange(`A${firstDataRow}:N${lastDataRow}`).values = values;
const totalRow = lastDataRow + 2;
sheet.mergeCells(`A${totalRow}:D${totalRow}`);
sheet.getRange(`A${totalRow}`).values = [["알려진 표시가 소계 | 수량 × 표시 단가 · AL01 및 비가격 hold 제외"]];
sheet.getRange(`J${totalRow}`).values = [[knownSubtotal]];
sheet.mergeCells(`A${totalRow + 1}:N${totalRow + 1}`);
sheet.getRange(`A${totalRow + 1}`).values = [[`AL01 계획 충당 ${allowance.toLocaleString("ko-KR")}원은 확정 도착원가가 아님. SG01/E04/E09C는 0원 비가격 hold이며 실제 구매 총액에 포함할 수 없음.`]];
sheet.mergeCells(`A${totalRow + 2}:N${totalRow + 2}`);
sheet.getRange(`A${totalRow + 2}`).values = [["해제 전제: ACTUATOR_SWITCH_POINTS · PEAK_STALL_CURVE · DMC_ENCODER_MULTIDROP_COMPATIBILITY · DMC_STOP_BEHAVIOR · SG01 · SMPS_30A · ESTOP_DC_INTERRUPTION · BENCH_VERIFY · PHYSICAL_CABLE_GUIDE · NO_INDEPENDENT_MECHANICAL_STOPS."]];
sheet.mergeCells(`A${totalRow + 3}:N${totalRow + 3}`);
sheet.getRange(`A${totalRow + 3}`).values = [["주문·결제·문의 전송 없음. 시제품 검토이며 안전 인증·현장 안전·사람 탑승 적합성을 주장하지 않습니다."]];

const body = sheet.getRange(`A1:N${totalRow + 3}`);
body.format.font = { name: "Arial", size: 9, color: "#1F2937" };
sheet.getRange("A1:N1").format = { font: { name: "Arial", size: 14, bold: true, color: "#17365D" } };
sheet.getRange("A2:N2").format = { font: { name: "Arial", size: 9, color: "#5B6770", italic: true } };
sheet.getRange("A3:N3").format = { fill: "#FFF2CC", font: { name: "Arial", size: 10, bold: true, color: "#7F6000" } };
sheet.getRange("A4:N4").format = { fill: "#FCE4D6", font: { name: "Arial", size: 9, bold: true, color: "#C00000" } };
sheet.getRange("A5:N6").format = { font: { name: "Arial", size: 9, color: "#7F6000" } };
sheet.getRange("A8:N8").format = { fill: "#1F4E78", font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
sheet.getRange(`A${firstDataRow}:N${lastDataRow}`).format = { verticalAlignment: "top", wrapText: true };
sheet.getRange(`F${firstDataRow}:J${lastDataRow}`).format.horizontalAlignment = "right";
sheet.getRange(`A${totalRow}:N${totalRow}`).format = { fill: "#D9EAF7", font: { name: "Arial", size: 10, bold: true, color: "#17365D" } };
sheet.getRange(`A${totalRow + 1}:N${totalRow + 3}`).format = { font: { name: "Arial", size: 9, color: "#5B6770", italic: true } };
sheet.getRange(`A8:N${lastDataRow}`).format.borders = { preset: "insideHorizontal", style: "thin", color: "#D9E2F3" };
sheet.getRange(`A8:N${lastDataRow}`).format.borders = { preset: "outside", style: "thin", color: "#9EADBA" };
sheet.getRange(`I${firstDataRow}:J${totalRow}`).format.numberFormat = "#,##0";
sheet.getRange("A:A").format.columnWidth = 10;
sheet.getRange("B:B").format.columnWidth = 11;
sheet.getRange("C:C").format.columnWidth = 26;
sheet.getRange("D:D").format.columnWidth = 36;
sheet.getRange("E:E").format.columnWidth = 20;
sheet.getRange("F:G").format.columnWidth = 7;
sheet.getRange("H:H").format.columnWidth = 10;
sheet.getRange("I:J").format.columnWidth = 14;
sheet.getRange("K:K").format.columnWidth = 24;
sheet.getRange("L:L").format.columnWidth = 44;
sheet.getRange("M:M").format.columnWidth = 3;
sheet.getRange("N:N").format.columnWidth = 48;
sheet.getRange("A1:N1").format.rowHeight = 24;
sheet.getRange("A8:N8").format.rowHeight = 34;
sheet.getRange(`A${firstDataRow}:N${lastDataRow}`).format.rowHeight = 56;
sheet.getRange(`A${totalRow}:N${totalRow + 3}`).format.rowHeight = 24;

workbook.recalculate();
await fs.mkdir(verificationDir, { recursive: true });
const inspection = await workbook.inspect({
  kind: "table",
  range: `BOM!A1:N${totalRow + 3}`,
  include: "values,formulas",
  tableMaxRows: 100,
  tableMaxCols: 14,
  tableMaxCellChars: 300,
  maxChars: 60000,
});
await fs.writeFile(path.join(verificationDir, "bom-final-inspect.ndjson"), inspection.ndjson, "utf8");
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(verificationDir, "bom-formula-errors.ndjson"), errors.ndjson, "utf8");
const preview = await workbook.render({ sheetName: "BOM", range: `A1:N${totalRow + 3}`, scale: 1, format: "png" });
await fs.writeFile(path.join(verificationDir, "bom-final.png"), new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, knownSubtotal, allowance, rowCount: rows.length, totalRow }));
