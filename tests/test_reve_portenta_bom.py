import unittest
import copy
import csv

from scripts.build_reve_portenta_bom import build_rows, known_price_subtotal, validate_budget, DELETIONS, SOURCE


class PortentaBomTests(unittest.TestCase):
    def test_landed_cost_uncertainty_and_commercial_holds_block_checkout(self):
        rows = {r["ID"]: r for r in build_rows()}
        self.assertIn("AL01", rows)
        self.assertIn("SG01", rows)
        self.assertNotIn("IF01", rows)
        self.assertNotIn("HM01", rows)
        self.assertNotIn("SH01", rows)
        self.assertNotIn("LG01", rows)
        self.assertEqual(rows["AL01"]["확장금액"], 109333)
        self.assertEqual(rows["AL01"]["주문상태"], "PLANNING_ALLOWANCE_NOT_QUOTE")
        self.assertIn("확정 세액 아님", rows["AL01"]["주문/조립 메모"])
        self.assertIn("4~5", rows["PC01"]["납기"])
        self.assertIn("10~15", rows["PC01"]["납기"])
        self.assertEqual(rows["SG01"]["단가(VAT포함)"], 0)
        self.assertEqual(rows["SG01"]["주문상태"], "HOLD_SG01_QUOTE_CARD_STOCK")
        self.assertEqual(rows["E04"]["단가(VAT포함)"], 0)
        self.assertEqual(rows["E04"]["주문상태"], "HOLD_SMPS_30A_SKU")
        self.assertTrue(all(r["예산판정"] == "판정 보류" for r in rows.values()))
        self.assertEqual(validate_budget(list(rows.values())), known_price_subtotal(list(rows.values())))

    def test_portenta_bom_replaces_legacy_control_without_padding(self):
        rows = build_rows()
        ids = {row["ID"] for row in rows}
        self.assertFalse({"M01S", "E01", "E02", "E03"} & ids)
        self.assertTrue({"PC01", "DC01", "DC02", "DC03", "IS01", "IS02", "SG01", "E04"} <= ids)
        self.assertFalse({"HM01", "SH01", "LG01", "IF01"} & ids)
        total = validate_budget(rows)
        self.assertLess(total, 3_800_000)
        actuators = [row for row in rows if "액추에이터" in row["품목"]]
        self.assertEqual([(row["ID"], row["주문수량"]) for row in actuators], [("M01", 3)])

    def test_known_subtotal_and_shipping(self):
        rows = build_rows()
        self.assertEqual(validate_budget(rows), 3_350_915)
        self.assertEqual(sum(r["확장금액"] for r in rows if r["분류"] == "배송"), 3000)
        self.assertEqual(sum(r["확장금액"] for r in rows if r["ID"] == "AL01"), 109333)

    def test_retained_baseline_and_prices_are_not_padded(self):
        with SOURCE.open(encoding="utf-8-sig", newline="") as f:
            old = {r["ID"]: r for r in csv.DictReader(f) if r["ID"] not in DELETIONS}
        affected = {"E04", "E09C"}
        rows = [r for r in build_rows() if r["ID"] in old and r["ID"] not in affected]
        expected = {id_ for id_ in old if id_ not in affected}
        self.assertEqual({r["ID"] for r in rows}, expected)
        self.assertEqual(sum(r["확장금액"] for r in rows), 1_300_779)
        for r in rows:
            self.assertEqual(r["주문수량"], int(old[r["ID"]]["주문수량"]))
            self.assertEqual(r["단가(VAT포함)"], int(old[r["ID"]]["단가(VAT포함)"]))

    def test_hold_and_verified_gauge_interfaces(self):
        rows = {r["ID"]: r for r in build_rows()}
        self.assertTrue(all(r["구매릴리스"] == "HOLD_VENDOR_REPLY" for r in rows.values()))
        self.assertEqual(rows["E09C"]["주문상태"], "HOLD_CONTROL_FUSE_RATING")
        self.assertIn("해외조달", rows["PC01"]["출하구분"])
        self.assertIn("폐루프 제어 아님", rows["MV01"]["주문/조립 메모"])
        self.assertIn("DG60103", rows["MV02"]["규격"])
        self.assertIn("Ø8 호환", rows["MV02"]["주문/조립 메모"])
        self.assertIn("Portenta-SG01", rows["CB02"]["품목"])

    def test_programming_cable_matches_machine_control_micro_b(self):
        rows = {r["ID"]: r for r in build_rows()}
        self.assertIn("Micro-B", rows["CB03"]["규격"])

    def test_invalid_totals_ids_and_quantities_are_rejected(self):
        for mutation in ("duplicate", "missing", "mismatch", "overbudget", "zero_quantity", "false_release"):
            with self.subTest(mutation=mutation):
                rows = copy.deepcopy(build_rows())
                if mutation == "duplicate": rows.append(copy.deepcopy(rows[0]))
                if mutation == "missing": rows = [r for r in rows if r["ID"] != "PC01"]
                if mutation == "mismatch": rows[0]["확장금액"] += 1
                if mutation == "overbudget":
                    smps = next(row for row in rows if row["ID"] == "E04")
                    smps["단가(VAT포함)"] = 100000
                    smps["확장금액"] = smps["단가(VAT포함)"] * smps["주문수량"]
                if mutation == "zero_quantity": rows[0]["주문수량"] = 0
                if mutation == "false_release": rows[0]["구매릴리스"] = "APPROVED"
                with self.assertRaises(ValueError): validate_budget(rows)


if __name__ == "__main__":
    unittest.main()
