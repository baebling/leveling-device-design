# Portenta·DMC-200 자동수평 제어계 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 Rev E 기구를 유지하면서 Portenta Machine Control, DMC-200 3축, 상·하부 산업용 경사계와 HMI를 적용하고 VAT 포함 380만~400만원의 증빙 가능한 구매 BOM과 검증 가능한 Arduino/C++ 제어계를 만든다.

**Architecture:** Portenta가 START/STOP, 자동수평, HMI, 기록과 오류감시를 담당하고 RS485로 세 대의 DMC-200에 축 목표를 보낸다. DMC-200은 각 액추에이터의 5 V A/B 엔코더와 DC 모터를 직접 폐루프 제어하며, 동일 모델 경사계 두 대가 하부 입력각과 상부 잔류각을 독립 측정한다.

**Tech Stack:** Python 3.12, unittest, CSV/XLSX, Arduino CLI, `arduino:mbed:envie_m7`, Arduino_PortentaMachineControl, C++17 host tests, RS485, DMC-200 MC-RS485-AG protocol, Modbus RTU/TCP, Weintek EasyBuilder Pro

**Spec:** `docs/superpowers/specs/2026-09-18-portenta-dmc200-control-upgrade-design.md`

## Global Constraints

- 적용 범위는 카트·적재물·사람이 없는 공개형 자중 자동수평 PoC다.
- 기구 자유도는 Z, pitch, roll이며 X, Y, yaw는 기구적으로 구속한다.
- `LM4075OE-1075 / DC24V / stroke 100 mm / encoder 5 V` 3대와 Rev E 기구 형상을 유지한다.
- 액추에이터 내장 종단 리미트만 사용하고 외장 리미트와 별도 기계식 스토퍼를 추가하지 않는다.
- START 명령 전에는 움직이지 않으며 STOP·E-STOP은 기존 하드웨어 전력차단계를 유지한다.
- 예비 액추에이터는 구매하지 않는다.
- 국내 재고·국내 카드결제·증빙 가능한 판매처를 우선하며 해외조달은 국내 동등품이 없다는 근거가 있을 때만 별도 표시한다.
- 확인되지 않은 가격은 0원이나 확정가로 처리하지 않는다.
- VAT 포함 기본안 총액은 3,800,000원 이상 4,000,000원 이하로 제한한다.
- 산업용 부품 사용이 사람 탑승 적합성이나 안전 인증을 의미하지 않는다.

---

### Task 1: 공급처·호환성 게이트 확정

**Files:**
- Create: `procurement/portenta_dmc200_supplier_matrix_2026-09-18.md`
- Create: `procurement/portenta_dmc200_supplier_inquiry_2026-09-18.md`
- Create: `references/vendor_downloads/portenta_dmc200/source_manifest.csv`

**Interfaces:**
- Consumes: 승인 명세와 기존 `reve_final_order_bom_2026-09-17.csv`
- Produces: BOM에서 사용할 고정 SKU, VAT 포함 가격, 납기, URL, 호환성 판정과 원문 파일 해시

- [ ] **Step 1: 판매·기술자료를 원출처에서 저장한다**

  Portenta `AKX00032`, DMC-200, DMC-200 통신 프로토콜, MKsensor `MK700 2-90-RS485-0.1`, Weintek `MT8072iP`의 상품 페이지·데이터시트·매뉴얼을 수집한다. 각 행은 `supplier,model,url,retrieved_at,local_path,sha256` 열로 기록한다.

- [ ] **Step 2: DMC-200 호환 질의를 작성한다**

  질의서에 `LM4075OE-1075`, 24 V, 부하전류 1.5 A, 5 V A/B상 6 ppr, 감속비 1/20, 리드 3.175 mm를 명시하고 전기레벨, pull-up 필요 여부, 엔코더 전원 출력, 한 바퀴 환산, 내부 리미트에서의 복귀, 위치 초기화와 RS485 3대 멀티드롭 사용을 서면 확인한다.

- [ ] **Step 3: HMI·경사계 구매 후보를 고정한다**

  1순위는 `MT8072iP`와 `MK700 2-90-RS485-0.1` 두 대다. 카드결제, 국내출고, VAT, 납기, 24 V 전원, 통신 프로토콜 파일 제공 여부를 확인하고 하나라도 충족하지 않으면 동등 기준으로만 대체한다.

- [ ] **Step 4: 400만원 조정용 검증 품목을 선정한다**

  전체 확정가가 380만원 미만일 때만 독립 100 mm 변위계 1대, 절연 RS485 장치, 전장함 내부 장착판 순서로 추가한다. 예비 액추에이터, 중복 제어기, 사용 목적이 없는 수량 증가는 금지한다.

- [ ] **Step 5: 게이트 판정을 기록한다**

  `PASS`, `HOLD_VENDOR_REPLY`, `REJECT` 세 상태만 사용한다. DMC-200 엔코더 호환성이 `PASS`가 아니면 Task 2 이후의 구매 릴리스는 진행하지 않는다.

### Task 2: 개정 BOM 생성기와 예산 검증

**Files:**
- Create: `scripts/build_reve_portenta_bom.py`
- Create: `tests/test_reve_portenta_bom.py`
- Create: `procurement/reve_portenta_order_bom_2026-09-18.csv`
- Create: `procurement/reve_portenta_order_bom_2026-09-18.xlsx`
- Create: `procurement/order_evidence/portenta_order_checklist_2026-09-18.md`

**Interfaces:**
- Consumes: Task 1의 고정 SKU·가격·납기와 기존 최종 BOM
- Produces: `build_rows() -> list[dict[str, object]]`, `validate_budget(rows) -> int`

- [ ] **Step 1: 실패하는 BOM 테스트를 작성한다**

```python
def test_portenta_bom_replaces_legacy_control_and_meets_budget():
    rows = build_rows()
    ids = {row["ID"] for row in rows}
    assert not {"M01S", "E01", "E02", "E03"} & ids
    assert {"PC01", "DC01", "DC02", "DC03", "IS01", "IS02", "HM01"} <= ids
    assert sum(r["확장금액"] for r in rows if r["발주구분"] == "BASE") in range(3_800_000, 4_000_001)
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

  Run: `python -m unittest tests.test_reve_portenta_bom -v`  
  Expected: FAIL because `build_reve_portenta_bom` does not exist.

- [ ] **Step 3: BOM 변환을 구현한다**

  기존 행을 보존하고 `M01S`, Mega2560, MDD10A, MPU6050을 제외한다. `PC01=AKX00032`, `DC01..03=DMC-200`, `IS01..02=MK700`, `HM01=MT8072iP` 및 검증·통신 부품을 Task 1 가격으로 추가한다. 모든 확장금액은 `주문수량 × VAT포함 단가` 공식으로 생성한다.

- [ ] **Step 4: 예산과 필수행 테스트를 통과시킨다**

  Run: `python -m unittest tests.test_reve_portenta_bom -v`  
  Expected: PASS, no optional actuator, base total 3.8M–4.0M.

- [ ] **Step 5: CSV·XLSX·체크리스트를 생성하고 검사한다**

  Run: `python scripts/build_reve_portenta_bom.py`  
  Expected: three outputs created; workbook formulas contain no `#REF!`, `#VALUE!`, `#DIV/0!`, or `#NAME?`.

### Task 3: 전기 아키텍처·배선 산출물 개정

**Files:**
- Create: `design_basis/portenta_dmc200_electrical_architecture_2026-09-18.md`
- Create: `fabrication/portenta_dmc200_io_map_2026-09-18.csv`
- Create: `fabrication/portenta_dmc200_terminal_map_2026-09-18.csv`
- Create: `fabrication/portenta_dmc200_point_to_point_2026-09-18.csv`
- Create: `tests/test_portenta_electrical_package.py`

**Interfaces:**
- Consumes: Task 2 BOM identifiers
- Produces: 장치·단자·와이어별 단일 연결 정의와 RS485 주소표

- [ ] **Step 1: 실패하는 연결 완전성 테스트를 작성한다**

```python
def test_three_axes_have_unique_addresses_and_power_cutoff():
    rows = load_point_to_point()
    assert dmc_addresses(rows) == {1, 2, 3}
    for axis in ("A1", "A2", "A3"):
        assert has_encoder_ab(rows, axis)
        assert has_motor_pair(rows, axis)
        assert motor_power_passes_estop_relay(rows, axis)
```

- [ ] **Step 2: 실패를 확인한다**

  Run: `python -m unittest tests.test_portenta_electrical_package -v`  
  Expected: FAIL because the new maps do not exist.

- [ ] **Step 3: I/O와 통신 토폴로지를 기록한다**

  DMC 주소는 1/2/3, 경사계 주소는 11/12, HMI는 Modbus TCP 우선으로 고정해 DMC RS485와 버스를 분리한다. 종단저항은 각 RS485 버스의 양 끝 한 곳씩만 두고 실드는 제어함 한쪽에서만 접지한다.

- [ ] **Step 4: 점대점 배선표를 완성한다**

  24 V motor, 24 V control, encoder 5 V, logic ground, PE를 서로 다른 net으로 표기하고 E-stop 릴레이가 세 DMC 모터전원을 차단하지만 Portenta 로그전원은 유지하도록 작성한다.

- [ ] **Step 5: 연결 테스트를 통과시킨다**

  Run: `python -m unittest tests.test_portenta_electrical_package -v`  
  Expected: PASS with unique addresses, no dangling mandatory terminals, and no PE used as signal return.

### Task 4: DMC-200 프로토콜 라이브러리

**Files:**
- Create: `firmware/reve_portenta_controller/lib/reve_dmc200/reve_dmc200.h`
- Create: `firmware/reve_portenta_controller/lib/reve_dmc200/reve_dmc200.cpp`
- Create: `firmware/reve_portenta_controller/test/test_dmc200.cpp`

**Interfaces:**
- Produces: `uint8_t dmcChecksum(const uint8_t*, size_t)`, `DmcFrame makePing(uint8_t)`, `DmcFrame makePositionMove(uint8_t, const PositionMove&)`, `bool parsePositionFeedback(const uint8_t*, size_t, PositionFeedback&)`

- [ ] **Step 1: 공식 예제 기반 실패 테스트를 작성한다**

```cpp
TEST(Dmc200, BuildsPingForIdZero) {
  EXPECT_EQ(makePing(0).bytes(), Bytes({0xFF,0xFE,0x00,0x02,0x2D,0xD0}));
}

TEST(Dmc200, Parses180DegreeFeedback) {
  const uint8_t p[] = {0xFF,0xFE,0x00,0x08,0x90,0xD1,0x00,0x46,0x50,0x00,0x00,0x00};
  PositionFeedback out{};
  ASSERT_TRUE(parsePositionFeedback(p, sizeof p, out));
  EXPECT_FLOAT_EQ(out.position_deg, 180.00f);
}
```

- [ ] **Step 2: 실패를 확인한다**

  Run: host C++ test build command documented in `firmware/reve_portenta_controller/README.md`  
  Expected: compile failure because protocol symbols do not exist.

- [ ] **Step 3: 체크섬·프레임 코덱을 최소 구현한다**

  헤더와 checksum 바이트를 제외한 합의 하위 8비트를 NOT하는 공식 규칙을 구현한다. 수신 길이, header, ID, checksum, mode를 모두 검사하고 잘못된 프레임은 `false`로 반환한다.

- [ ] **Step 4: 공식 명령 1·2·3·15·17~20만 구현한다**

  위치/속도 이동, 가감속 이동, 위치 초기화, 위치·속도 피드백만 포함한다. PID 자동튜닝이나 사용하지 않는 30개 전체 명령은 구현하지 않는다.

- [ ] **Step 5: 프로토콜 테스트를 통과시킨다**

  Expected: all codec tests PASS, malformed length/checksum/direction tests also PASS.

### Task 5: 하드웨어 독립 자동수평 코어

**Files:**
- Create: `firmware/reve_portenta_controller/lib/reve_core/reve_core.h`
- Create: `firmware/reve_portenta_controller/lib/reve_core/reve_core.cpp`
- Create: `firmware/reve_portenta_controller/test/test_reve_core.cpp`

**Interfaces:**
- Consumes: `TiltSample`, `AxisFeedback[3]`, `Command`
- Produces: `ControlOutput step(const ControlInput&)` containing three axis targets, state and fault

- [ ] **Step 1: 상태기계 실패 테스트를 작성한다**

```cpp
TEST(Core, NeverMovesBeforeStart) {
  Controller c;
  auto out = c.step(nominalInput(Command::None));
  EXPECT_EQ(out.state, State::Idle);
  EXPECT_TRUE(allTargetsHold(out));
}

TEST(Core, StaleUpperTiltFaultsAndHolds) {
  Controller c;
  auto in = nominalInput(Command::StartLevel);
  in.upper_tilt.age_ms = 201;
  auto out = c.step(in);
  EXPECT_EQ(out.fault, Fault::TiltStale);
  EXPECT_TRUE(allTargetsHold(out));
}
```

- [ ] **Step 2: 실패를 확인한다**

  Expected: compile failure because `Controller` does not exist.

- [ ] **Step 3: 기존 Mega 로직을 순수 C++ 코어로 옮긴다**

  START 전 무동작, HOME/JOG/LIFT/LEVEL/HOLD/FAULT, 0.25 mm 보정, ±5° fault, timeout, 축간 위치차와 sensor stale를 옮기되 Arduino API를 호출하지 않는다.

- [ ] **Step 4: 하부 경사 로그와 상부 제어 기준을 분리한다**

  상부 센서만 제어 오차에 사용하고 하부 센서는 입력기울기·보고서 기록에만 사용한다. 센서 둘을 빼서 상부 목표를 계산하지 않는다.

- [ ] **Step 5: 코어 테스트를 통과시킨다**

  Expected: startup, home gate, ±pitch/roll correction sign, timeout, stale, tilt fault and STOP tests all PASS.

### Task 6: Portenta 하드웨어 통합과 컴파일

**Files:**
- Create: `firmware/reve_portenta_controller/reve_portenta_controller.ino`
- Create: `firmware/reve_portenta_controller/README.md`
- Create: `scripts/setup_and_compile_portenta_firmware.ps1`
- Create: `tests/test_portenta_firmware_contract.py`

**Interfaces:**
- Consumes: Tasks 3–5 maps and libraries
- Produces: Portenta M7 firmware binary for `arduino:mbed:envie_m7`

- [ ] **Step 1: 정적 계약 테스트를 작성한다**

```python
def test_portenta_firmware_has_zero_motion_startup_and_watchdog():
    src = SKETCH.read_text(encoding="utf-8")
    assert "holdAllAxes" in src
    assert "watchdog" in src.lower()
    assert "Command::StartLevel" in src
    assert "DMC_ADDRESS" in src
```

- [ ] **Step 2: 실패를 확인한다**

  Run: `python -m unittest tests.test_portenta_firmware_contract -v`  
  Expected: FAIL because the sketch does not exist.

- [ ] **Step 3: Portenta 어댑터를 구현한다**

  공식 `Arduino_PortentaMachineControl` 라이브러리만 사용하고 deprecated `Arduino_MachineControl`은 사용하지 않는다. RS485 송수신, 24 V START/STOP, HMI Modbus map, 저장 로그를 `reve_core`와 연결한다.

- [ ] **Step 4: 재현 가능한 컴파일 스크립트를 작성한다**

  Arduino CLI와 core/library 버전, 다운로드 SHA256, FQBN `arduino:mbed:envie_m7`, compile timestamp를 `outputs/portenta_firmware_build/compile_record.txt`에 남긴다.

- [ ] **Step 5: 정적시험과 컴파일을 통과시킨다**

  Run: `python -m unittest tests.test_portenta_firmware_contract -v`  
  Run: `powershell -ExecutionPolicy Bypass -File scripts/setup_and_compile_portenta_firmware.ps1`  
  Expected: tests PASS and Arduino CLI compile exit 0.

### Task 7: HMI·로그 인터페이스

**Files:**
- Create: `firmware/reve_portenta_controller/hmi/modbus_register_map.csv`
- Create: `firmware/reve_portenta_controller/hmi/mt8072ip_screen_spec.md`
- Create: `verification/portenta_log_schema_2026-09-18.csv`
- Create: `tests/test_portenta_hmi_contract.py`

**Interfaces:**
- Produces: 고정 Modbus register map and CSV telemetry schema

- [ ] **Step 1: 레지스터 중복 실패 테스트를 작성한다**

```python
def test_hmi_registers_are_unique_and_commands_are_writable_only():
    rows = load_registers()
    assert len({r.address for r in rows}) == len(rows)
    assert all(r.access == "RW" for r in rows if r.name in {"CMD_START", "CMD_STOP", "CMD_HOME"})
    assert all(r.access == "RO" for r in rows if r.name.startswith(("UPPER_", "LOWER_", "AXIS_", "FAULT_")))
```

- [ ] **Step 2: 화면·로그 계약을 작성한다**

  단일 메인 화면에 IDLE/HOMING/LEVELING/HOLD/STOP/FAULT, 상·하부 pitch/roll, A1/A2/A3 current/target, START/STOP/HOME를 배치한다. 로그 열은 `timestamp_ms,state,upper_pitch_deg,upper_roll_deg,lower_pitch_deg,lower_roll_deg,a1_mm,a2_mm,a3_mm,a1_target_mm,a2_target_mm,a3_target_mm,fault`로 고정한다.

- [ ] **Step 3: 계약 테스트를 통과시킨다**

  Run: `python -m unittest tests.test_portenta_hmi_contract -v`  
  Expected: PASS with no duplicate address, command/status access separation and exact log columns.

### Task 8: 구매·조립 릴리스 감사

**Files:**
- Create: `verification/portenta_dmc200_release_audit_2026-09-18.md`
- Modify: `verification/powered_reve_verification_matrix_2026-09-17.md`
- Modify: `PROJECT_HANDOFF.md`

**Interfaces:**
- Consumes: Tasks 1–7 outputs
- Produces: `PURCHASE_RELEASE`, `CONTROL_POWER_TEST_RELEASE`, `MOTOR_POWER_RELEASE` 판정

- [ ] **Step 1: 전체 자동시험을 실행한다**

  Run: `python -m unittest discover -s tests -v`  
  Expected: all tests PASS.

- [ ] **Step 2: 구매 릴리스 조건을 확인한다**

  DMC 호환 서면답변, 정확한 SKU·VAT·납기·배송비, 3.8M–4.0M 합계, 예비 액추에이터 없음, HMI/센서 국내 출고 증빙이 모두 있을 때만 `PURCHASE_RELEASE=TRUE`로 한다.

- [ ] **Step 3: 통전 릴리스 조건을 분리한다**

  구매완료가 통전승인을 의미하지 않도록 한다. 무전원 도통·단락·PE·퓨즈 확인과 START 전 hold, E-stop 전력차단 시험을 통과해야 `CONTROL_POWER_TEST_RELEASE=TRUE`로 한다.

- [ ] **Step 4: 모터 시험 순서를 기록한다**

  A1 단축 무부하 JOG → A2 → A3 → 세 축 HOME → 0/25/50 mm Z → 저속 pitch/roll → 하부 기울임 자동수평 순서로 고정한다. 각 단계의 HMI 화면과 전체 배선·기구 사진을 촬영한다.

- [ ] **Step 5: 최종 증빙을 검토한다**

  BOM, 견적, 회로·배선표, firmware compile record, 시험 로그와 사진목록을 서로 교차 확인하고 열린 항목은 `PASS`로 추정하지 않고 명시적으로 남긴다.
