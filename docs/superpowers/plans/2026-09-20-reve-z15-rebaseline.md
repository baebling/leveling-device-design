# Rev E Z+15 mm Rebaseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebaseline the self-weight PoC at a physical Z=15 mm datum, verify its Z=15~65 mm operating envelope, and update the electrical and procurement baseline without claiming purchase release.

**Architecture:** The existing LM4075OE-1075 100 mm actuator and three-axis Rev E mechanism remain unchanged. The new command datum maps Z=0~50 mm to existing physical Z=15~65 mm; the software pin-length window is provisional until actual actuator limit switch lengths are measured. The HMI-less laptop/Portenta/DMC-200 architecture remains the electrical direction.

**Tech Stack:** Python 3.12, CadQuery 2.8 local runtime, Markdown, CSV/XLSX procurement workbook.

**Spec:** `docs/superpowers/specs/2026-09-20-portenta-laptop-dual-rs485-design.md`; `requirements/current_variant_priority_2026-09-17.md`; `design_basis/powered_reve_rebaseline_concept_2026-09-17.md`

## Global Constraints

- Demo scope is no cart, no payload, no person, supervised indoor self-weight open-frame PoC only.
- Permitted upper motion is Z, pitch, and roll; X, Y, and yaw remain mechanically constrained.
- Retain `LM4075OE-1075 / DC24V / 100 mm / 750 N / encoder 5 V / 6 ppr` x3.
- New command datum is physical Z=15 mm; command Z=0~50 mm maps to physical Z=15~65 mm.
- The nominal 205~305 mm pin range is not proof of actual internal switch trip points.
- Do not add an HMI or a spare actuator. Select a 24 V 30 A-class PSU candidate; do not claim a purchase release.
- No external mechanical stops is an explicit safety deviation limited to this PoC; do not represent it as a safe production release.
- Record assumptions and unresolved supplier questions; preserve existing user work.

---

### Task 1: Freeze the Z+15 command-datum design basis

**Files:**
- Modify: `design_basis/powered_reve_rebaseline_concept_2026-09-17.md`
- Modify: `requirements/current_variant_priority_2026-09-17.md`
- Create: `verification/reve_z15_rebaseline_decision_2026-09-20.md`

**Interfaces:**
- Consumes: existing physical coordinate convention and `LM4075OE-1075` selection.
- Produces: exact rebaseline mapping, external dimensions, provisional pin-length window, and clear release limitations for Tasks 2–4.

- [ ] Write the decision record using these exact values: physical Z=15~65 mm, command Z=0~50 mm, pitch/roll ±3°, basic envelope 700×700×315 mm, nominal pin range 221.281~289.523 mm, provisional soft window 218~292 mm.
- [ ] State that the 205~305 mm values are nominal CAD/STEP geometry, not verified internal limit trip points.
- [ ] State the fallback: retain the Z+15 datum but cap command Z at 35 mm if guide overlap or full CAD screening fails.
- [ ] Cross-link the decision record from the concept and current-requirement documents without changing the PoC safety-deviation status.
- [ ] Verify all three files contain the same datum, bounds, and release language.

### Task 2: Verify the full Z+15 CAD operating envelope

**Files:**
- Create: `calculations/reve_z15_workspace_audit.py`
- Create: `tests/test_reve_z15_workspace_audit.py`
- Create: `verification/reve_z15_workspace_audit_2026-09-20.json`
- Create: `verification/reve_z15_workspace_audit_2026-09-20.md`

**Interfaces:**
- Consumes: Task 1 physical range and `fusion_scripts/ProfileRadialRevD/revd_data.py` / `cad/profile_radial_reve_actual_vendor.py`.
- Produces: reproducible dense-grid pin-length results and a maximum-Z CAD collision screen used by Task 4.

- [ ] Write a failing test that asserts the sampled physical range is Z=15~65 mm, the minimum pin length is at least 221.0 mm, and the maximum is at most 290.0 mm.
- [ ] Implement a dense kinematic grid using physical Z=15:5:65 mm and pitch/roll=-3:0.5:3°; serialize minimum/maximum pin lengths and worst poses to JSON.
- [ ] Implement a CAD collision screen at physical Z=65 mm for all nine pitch/roll combinations, using the existing supplier STEP and joint-envelope collision function.
- [ ] Run with `PYTHONPATH=$env:USERPROFILE\\.cache\\leveling-cadquery-py312` and record the executed result; label this finite screening only, not fabrication approval.
- [ ] Write the Markdown report with the result, unverified guide-overlap limitation, and the 35 mm command-Z fallback.

### Task 3: Update the HMI-less electrical selection basis

**Files:**
- Modify: `docs/superpowers/specs/2026-09-20-portenta-laptop-dual-rs485-design.md`
- Create: `design_basis/reve_z15_electrical_basis_2026-09-20.md`
- Create: `verification/reve_z15_electrical_gate_2026-09-20.md`

**Interfaces:**
- Consumes: Task 1 bounds, DMC-200 manual/protocol, actuator data supplied by the user, and SG01 procurement research.
- Produces: a no-HMI topology, provisional power requirements, exact communication contracts, and unresolved hardware gates for Task 4.

- [ ] Specify the 24 V 30 A-class PSU basis: 3×1.5 A nominal load, 7.5 A provisional per-axis peak, 22.5 A aggregate provisional peak, and 28.125 A with 25% margin.
- [ ] Select ICP DAS `tGW-715i-T` as provisional SG01 only if domestic price/card/lead evidence is marked unresolved; otherwise do not substitute an unisolated gateway silently.
- [ ] Define the sensor contract: Portenta Modbus TCP client → SG01 TCP server port 502 → SG01 RTU master → HWT905 IDs 11 and 12, configured one at a time.
- [ ] Define the DMC path as a direct short RS-485 daisy chain and remove IF01 from the new topology; retain PC command-session timeout, STOP/fault behavior, and independent E-stop motor-power cut.
- [ ] Explicitly prohibit routine hard-limit HOME. Require supervised commissioning at the Z+15 datum and recording actual limit positions before enabling automatic operation.

### Task 4: Create a revised preliminary order BOM and checkout gate

**Files:**
- Modify: `scripts/build_reve_portenta_bom.py`
- Modify: `tests/test_reve_portenta_bom.py`
- Modify: `procurement/reve_portenta_order_bom_2026-09-18.csv`
- Modify: `procurement/reve_portenta_order_bom_2026-09-18.xlsx`
- Create: `procurement/order_evidence/reve_z15_hmiless_checkout_gate_2026-09-20.md`

**Interfaces:**
- Consumes: Task 1 datum, Task 2 CAD outcome, and Task 3 electrical parts/hold conditions.
- Produces: one HMI-less preliminary BOM and an explicit checkout hold list; it never sets purchase release true.

- [ ] Write failing tests that reject HM01, SH01, LG01, and IF01 as active order rows; require a 24 V 30 A-class PSU line and provisional SG01 line; retain `PURCHASE_RELEASE=FALSE`.
- [ ] Update the BOM generator and CSV/XLSX using the project spreadsheet workflow; reuse CB02 as the SG01 Ethernet cable where suitable and do not add a redundant cable.
- [ ] Record every unavailable price, card-payment status, stock, delivery lead, and actual actuator-limit evidence as `HOLD_*`, not as invented pricing.
- [ ] Recalculate the workbook and run its tests; confirm the workbook contains no formula errors and that the final total is clearly labelled preliminary/conditional.
- [ ] Write the checkout gate listing the exact conditions required before a human presses order.
