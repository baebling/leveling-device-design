# RevE BOM and Assembly Release Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a corrected, traceable RevE procurement workbook and an evidence-based list of remaining mechanical and electrical release gates without claiming fabrication or purchase approval prematurely.

**Architecture:** Keep the existing one-sheet BIZ-Lab cost template and supplier grouping. Independently audit mechanical interfaces, electrical ratings, prices, hyperlink targets, and enclosure clearance; change only verified BOM entries and expose unresolved items as holds. Existing A1–A3 plate holes/taps, enclosure entry/button/mount holes, and DIN rail cutting remain allowed. A new stopper must use stock bolt-on parts with no additional fabrication.

**Tech Stack:** Existing RevE CadQuery/Python validation, `@oai/artifact-tool` for workbook import/edit/render/export, targeted OOXML hyperlink repair if the artifact API does not support hyperlink targets, independent XLSX and arithmetic checks.

**Spec:** `requirements/current_variant_priority_2026-09-17.md`; latest user clarification on 2026-10-01 overrides only the additional-machining restriction.

## Global Constraints

- Prototype has no cart, payload, or person; open-frame self-weight demonstration only.
- Keep Z command 0–50 mm and simultaneous pitch/roll ±3° unless the checked hardware cannot support it.
- Keep X/Y/yaw mechanically constrained; preserve independent electrical limits and mechanical stop requirement.
- No new machining beyond existing A1–A3 patterns, enclosure holes, and DIN rail length adjustment.
- Do not order or mark `PURCHASE_RELEASE=TRUE` while critical dimensions, stop load path, or electrical protection remain unverified.
- Budget ceiling is 4,000,000 KRW including VAT, required fabrication, and delivery.

---

### Task 1: Independent evidence and workbook audit

**Files:**
- Read: `outputs/20260930_reve_interface_correction/2026_BIZ-Lab_재료비관리_RevE_315mm_체결전장정정.xlsx`
- Read: `outputs/20260930_reve_interface_correction/RevE_잔여구매_전장함_검증_2026-09-30.md`
- Create: `outputs/20261001_reve_bom_audit/검수결과_및_남은작업.md`

**Interfaces:** Consumes the approved requirements and current workbook; produces verified defects, corrected candidates, and blocked gates for Task 2.

- [x] **Step 1: Enumerate BOM IDs, quantities, URLs, actual hyperlink targets, and cost formulas.** Compare each row to three-axis use, supplier page, and packaging unit.
- [ ] **Step 2: Check mechanical and electrical interfaces independently.** Record a source URL or exact local drawing for each conclusion; classify every row as verified, conditional, or invalid. (Critical interfaces independently checked; every sales option/stock/package is not yet verified.)
- [x] **Step 3: Record unresolved geometry and physical tests.** Explicitly keep stopper, pivot stack, fuse holder, and enclosure in HOLD if evidence is incomplete.

### Task 2: Targeted workbook correction and validation

**Files:**
- Create: `outputs/20261001_reve_bom_audit/revise_bom.mjs`
- Create: `outputs/20261001_reve_bom_audit/2026_BIZ-Lab_재료비관리_RevE_검수수정.xlsx`
- Test: source/output workbook comparison and actual hyperlink-target audit.

**Interfaces:** Consumes Task 1's row-level findings; produces the procurement review workbook and verification log.

- [x] **Step 1: Write failing checks for every populated G-column URL versus its actual hyperlink target, for subtotal/VAT/balance, and for duplicate BOM IDs.** The present RevE workbook must fail the hyperlink test.
- [x] **Step 2: Make only evidence-backed row corrections.** Preserve supplier grouping, template formatting, and existing formulas. Keep unpriced/unverified replacement choices clearly marked; do not insert invented prices.
- [x] **Step 3: Repair all link targets and re-run checks.** The output must have zero displayed/actual-link mismatches and every populated supplier URL clickable.
- [x] **Step 4: Recalculate, render changed rows and summary, inspect formula errors, export once, and reopen the saved XLSX to verify the persisted hyperlinks and totals.**

### Task 3: Mechanical and enclosure release summary

**Files:**
- Create or update: `outputs/20261001_reve_bom_audit/검수결과_및_남은작업.md`
- Read: `outputs/profile_radial_revE_frame_raise_2026-09-30/Profile_Radial_3RPS_RevE_supplier_interface_validation.json`

**Interfaces:** Consumes the audited BOM and 27-pose CAD evidence; produces a precise purchase/fabrication HOLD list and next-step order.

- [x] **Step 1: State which CAD claims are actually supported and which omit stopper, pivot fasteners, cables, enclosure, tolerances, or HOME paths.**
- [x] **Step 2: Compare bolt-on stopper options with 3 kN nominal design contact and positive bearing path.** Reject any option whose load or limit hierarchy cannot be established. (No acceptable orderable combination found.)
- [x] **Step 3: Give a provisional enclosure zone arrangement only if dimensions support it; do not publish drilling coordinates without inner-panel measurements.**
- [x] **Step 4: Report remaining tasks in priority order with the exact measurement, supplier document, or test needed to close each gate.**
