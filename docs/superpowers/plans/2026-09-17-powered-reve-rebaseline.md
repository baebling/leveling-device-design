# Powered Rev E Rebaseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 승인된 Rev E 최소변경안을 공급자 확인, 상세 CAD·제어 갱신, 일괄구매 검토, 자중 자동수평 시험까지 추적 가능한 상태로 만든다.

**Architecture:** 기존 120° 방사형 3-RPS 기구와 실제 LM4075OE STEP 기반 모델을 유지한다. 변경 범위는 LDK PHS 6 대체, 무스토퍼 분석형과 독립 스토퍼 릴리스 요구형의 분리, HOME 전 경로, 절대 핀 길이 210~280 mm의 실측 리미트 기준 보호창, 독립 24 V 모터전원 비상차단과 엘레파츠 중심 BOM이다.

**Tech Stack:** Python 3.12, CadQuery/OpenCascade, unittest, Fusion 360, Arduino Mega2560, MPU6050, Cytron MDD10A, XLSX 구매표

**Spec:** `requirements/current_variant_priority_2026-09-17.md`

## Global Constraints

- 카트·적재물·사람 없이 상부 모듈 자중만 시연한다.
- 상부 허용 자유도는 Z/pitch/roll이고 독립 X/Y/yaw는 구속한다.
- 명령범위는 Z 0~50 mm, pitch/roll 동시 ±3°다.
- 전원인가 시 모든 PWM은 0이고 운전자 명령 전에는 움직이지 않는다.
- 사용자는 별도 기계식 스토퍼 생략을 승인했지만 프로젝트 규칙은 독립 기계식 스토퍼를 요구한다. 충돌이 해소되지 않는 동안 구매·제작 릴리스는 `FALSE`다.
- 무스토퍼안은 분석 전용이고, 구매 가능한 릴리스형의 기본/선택 예산에는 독립 스토퍼 전체가 포함된다.
- 물리 비상정지는 노트북과 독립적으로 모터 24 V를 차단한다.
- 실제 카트 치수·질량·홀 위치를 추정하지 않는다.
- 기본안과 예비 액추에이터 포함 선택안의 총 구매·가공·배송비는 각각 4,000,000원 이하다.
- 본 폴더는 Git 저장소가 아니므로 커밋 단계 대신 각 작업의 명령출력과 SHA-256을 `logs/`에 저장한다.

---

### Task 1: 공급자 인터페이스 동결

**2026-09-17 실행:** 공개자료 선별은 부분 완료했다. MotionGearOn에서 `24V/100mm/5V` 옵션 선택과 주문화면, 엘레파츠에서 `24V/100mm` 옵션·가격 및 PHS 6 주문수입 조건을 확인했다. LDK PHS 6 원본 데이터시트를 보존하고 치수·13° 편각·3.2/8.1 kN 정격을 확인했다. LMB-10 공개이미지는 일부 치수만 제공하므로 CAD 동결 불가이며, 문의 전송과 판매자 서면회신은 아직 남는다.

**Files:**
- Modify: `procurement/powered_reve_eleparts_supplier_inquiry_2026-09-17.md`
- Create: `references/vendor_docs/2026-09-17_supplier_response_index.md`
- Modify: `outputs/20260917_powered_reve_rebaseline/powered_reve_eleparts_preliminary_bom_2026-09-17.xlsx`

**Interfaces:**
- Consumes: 승인 형번과 질의목록
- Produces: 전류, 듀티, 엔코더, 리미트, 치수, 재고와 납기의 서면 입력값

- [ ] **Step 1: 액추에이터·LMB·PHS·전원·E-stop 질의를 판매자에게 전송한다.**

  `procurement/powered_reve_eleparts_supplier_inquiry_2026-09-17.md`의 문안을 사용하고 문의번호 또는 캡처 파일명을 기록한다.

- [ ] **Step 2: 답변 원본을 보존한다.**

  파일명은 `YYYY-MM-DD_supplier_topic.ext`로 통일하고 `references/vendor_docs/`에 저장한다.

- [ ] **Step 3: 답변 인덱스를 작성한다.**

  각 행에 형번, 답변자, 날짜, 원본파일, 설계에 반영할 값, 미해결 질문을 기록한다.

- [ ] **Step 4: BOM의 HOLD 조건을 갱신한다.**

  옵션·SKU·VAT포함 단가·납기·반품제한을 답변 그대로 반영하고 추정값은 확정값으로 바꾸지 않는다.

- [ ] **Step 5: 체크포인트 해시를 저장한다.**

  Run: `Get-FileHash references/vendor_docs/* -Algorithm SHA256 | Out-File logs/supplier_docs_sha256_2026-09-17.txt`

  Expected: 답변 원본마다 SHA-256 한 줄.

### Task 2: 승인 운전영역 계산 모듈

**2026-09-17 실행:** 완료. 27자세와 1,859자세 조밀 격자는 210.771741~276.937115 mm로 통과했고, 수용 외란 최대 3.621431 mm/s, 양축 1°/s 스트레스 최대 5.121477 mm/s다. 공급자 리미트 미확정 때문에 릴리스는 거짓이다.

**2026-09-17 최종 회귀:** 프로젝트 지정 Python 3.12/CadQuery 2.8.0 환경에서 전체 257개 테스트가 통과했다. HOME 위상보존 재개 216,951상태, 명목 205→210 mm 탈출 6순환, HOME_PARK/인접 JOG 6,981선분도 완료했으나 공급자 실치수와 최종형상 전경로 CAD가 없어 모든 릴리스는 계속 거짓이다.

**Files:**
- Create: `calculations/reve_approved_workspace.py`
- Create: `tests/test_reve_approved_workspace.py`
- Create: `verification/reve_approved_workspace_2026-09-17.json`

**Interfaces:**
- Consumes: `fusion_scripts.ProfileRadialRevD.revd_data.pin_lengths`
- Produces: `approved_pose_grid()`, `dense_pose_grid()`, `speed_screen()`, `software_window_audit()`

- [ ] **Step 1: 실패하는 운전영역 테스트를 작성한다.**

```python
def test_approved_grid_stays_inside_physical_and_software_limits():
    result = software_window_audit()
    assert result["pose_count"] == 27
    assert result["minimum_pin_mm"] >= 210.0
    assert result["maximum_pin_mm"] <= 280.0
    assert result["passes"] is True
```

- [ ] **Step 2: 테스트 실패를 확인한다.**

  Run: `python -m unittest tests.test_reve_approved_workspace -v`

  Expected: `ModuleNotFoundError: calculations.reve_approved_workspace`.

- [ ] **Step 3: 최소 계산 모듈을 구현한다.**

  `Z=(0,25,50)`, `pitch=(-3,0,3)`, `roll=(-3,0,3)`을 생성하고 절대 핀 길이 210~280 mm를 검사한다. `L_low_switch/L_high_switch`를 파라미터로 받아 HOME 상대창 `[210−L_low_switch,280−L_low_switch]`, Z0 오프셋 `224.2075−L_low_switch`, 공급자 하드엔드 여유를 함께 검사한다.

- [ ] **Step 4: 조밀 격자·경로 스크리닝을 추가한다.**

  `Z=0:5:50 mm`, `pitch/roll=-3:0.5:+3°` 격자를 만든다. pose-space 축 인접점은 다른 두 좌표를 고정하고 Z≤1 mm 또는 한 각도≤0.1°로 선형 보간하며, 동시 명령의 시작·끝 pose도 같은 최대간격으로 표본화한다. 꼭짓점 27개와 조밀 스크리닝 결과를 분리하고 연속영역 증명으로 표현하지 않는다.

- [ ] **Step 5: 수용 외란과 스트레스 외란을 분리해 시험한다.**

```python
def test_actuator_speed_margin_for_acceptance_vector_rate():
    result = speed_screen(pitch_rate_deg_s=2**-0.5, roll_rate_deg_s=2**-0.5)
    assert result["angular_rate_vector_deg_s"] <= 1.0 + 1e-9

def test_each_axis_one_degree_per_second_is_stress_screen_only():
    result = speed_screen(pitch_rate_deg_s=1.0, roll_rate_deg_s=1.0)
    assert result["maximum_required_mm_s"] <= 5.2
    assert result["screen_kind"] == "STRESS_ONLY"
```

- [ ] **Step 6: 테스트와 JSON 생성을 실행한다.**

  Run: `python -m unittest tests.test_reve_approved_workspace -v`

  Expected: 모든 테스트 PASS, JSON에 27자세·조밀 격자·수용 및 스트레스 최대속도 기록.

### Task 3: 공통 HOME 전진기구학과 경로검사

**2026-09-17 실행:** 부분 완료. 6변수 전진기구학과 조밀 1,859시작점×6 순차/6 교대 검사를 수행했다. 순차 6개는 모두 탈락하고 교대 `A3→A2→A1`만 기본경로를 최대 4.993699°로 통과했다. 최악 중간상태에서 위상 초기화 재시작은 5.070406°로 실패했다. 후속검사에서 선택경로 216,951개 중간상태의 같은 전원 세션 위상보존 재개는 원래 접미경로와 모두 일치했다. 전원상실·MCU reset·E-stop 후 자동 재개는 금지한다. 명목 205→210 mm 정상창 복귀는 6순환 모두 최대 약 0.233°로 통과했고 제어 단순화를 위해 같은 `A3→A2→A1`을 선택했다. HOME_PARK 1,859선분과 조밀 인접 JOG 5,122선분의 89,707표본도 통과했다. 기존 CAD 대표 4자세 교차검사는 0 mm³지만 임의 직접명령·전경로·변경 LDK/LMB 검사는 남는다.

**Files:**
- Create: `calculations/reve_forward_kinematics.py`
- Create: `calculations/reve_home_path_audit.py`
- Create: `tests/test_reve_home_path_audit.py`
- Modify: `cad/profile_radial_reve_actual_vendor.py`
- Create: `verification/reve_home_path_audit_2026-09-17.json`

**Interfaces:**
- Consumes: 세 액추에이터 핀 간 길이 `(l1,l2,l3)`
- Produces: `solve_pose_from_lengths(lengths, seed) -> PoseSolution`, `audit_home_sequences(step_mm=1.0)`

- [ ] **Step 1: 역기구학 왕복 테스트를 작성한다.**

```python
def test_forward_solution_reproduces_known_pose():
    lengths = revd_data.pin_lengths(25.0, 3.0, -3.0)
    solved = solve_pose_from_lengths(lengths, seed=(0, 0, 25, 3, -3, 0))
    assert abs(solved.lift_mm - 25.0) < 1e-4
    assert abs(solved.pitch_deg - 3.0) < 1e-4
    assert abs(solved.roll_deg + 3.0) < 1e-4
```

- [ ] **Step 2: 테스트 실패를 확인한다.**

  Run: `python -m unittest tests.test_reve_home_path_audit -v`

  Expected: 전진기구학 함수가 없어 FAIL.

- [ ] **Step 3: 6변수 Newton 해석기를 구현한다.**

  미지수는 `x,y,z,pitch,roll,yaw`이고 세 R축 접선 구속식과 세 길이식을 잔차로 사용한다. 직전 자세를 다음 스텝의 seed로 사용하고 잔차 1e-6 mm 이하만 수용한다.

- [ ] **Step 4: 모든 허용 시작점과 HOME 후보 경로를 생성한다.**

  Task 2 조밀 격자, 모든 허용 명령·JOG 경로 표본을 시작집합으로 사용한다. 각 시작점에 A1/A2/A3 모든 순열 6개 순차경로와 6개 순환순서별 1 mm 교대수축 경로를 생성한다. 생성된 HOME 중간상태도 시작집합에 넣고 동일 경로 재시작을 검사해 집합을 닫는다.

- [ ] **Step 5: 각 경로 자세의 조인트·간섭 검사를 연결한다.**

  `cad.profile_radial_reve_actual_vendor.collision_audit()`가 임의 해석자세를 받도록 확장하고 PHS 편각, 공급자 하드엔드/리미트 범위, 5° 초과 기울기를 함께 검사한다.

- [ ] **Step 6: 안전한 HOME 방식을 선택한다.**

  Run: `python calculations/reve_home_path_audit.py`

  Expected: 모든 시작점·경로의 최대 기울기·편각·간섭을 JSON으로 출력. 전체 시작집합에서 통과하는 단일 공통 순차순서 중 최대 기울기와 편각이 가장 작은 하나를 채택하고, 없으면 전체에 공통으로 통과하는 단일 교대 순환순서를 같은 방식으로 선택한다.

- [ ] **Step 7: 회귀시험을 실행한다.**

  Run: `python -m unittest tests.test_profile_radial_revd tests.test_profile_radial_reve_poc_release tests.test_reve_approved_workspace tests.test_reve_home_path_audit -v`

  Expected: 전체 PASS.

### Task 4: 변경 조인트와 스토퍼 요구 분리 CAD

**Files:**
- Modify: `fusion_scripts/ProfileRadialRevD/revd_data.py`
- Modify: `cad/profile_radial_reve_actual_vendor.py`
- Create: `cad/profile_radial_reve_approved.py`
- Create: `tests/test_profile_radial_reve_approved.py`
- Create: `outputs/profile_radial_reve_approved_2026-09-17/README.md`
- Create: `verification/reve_changed_geometry_full_audit_2026-09-17.json`

**Interfaces:**
- Consumes: 공급자 LMB-10·LDK PHS 6 도면값과 Task 3 HOME 방식
- Produces: 사용자 요청 무스토퍼 분석형, 독립 스토퍼 릴리스형, 변경형 조밀 격자·명령선분·HOME 전체경로 결과

- [ ] **Step 1: 공급도면 치수에 대한 실패 테스트를 작성한다.**

```python
def test_vendor_joint_dimensions_are_not_assumptions():
    assert P.lmb_drawing_verified is True
    assert P.phs6_drawing_verified is True
```

- [ ] **Step 2: 도면값을 별도 승인 파라미터에 입력한다.**

  기존 Rev D 역사값을 덮어쓰지 않고 `profile_radial_reve_approved.py`에서 변경값을 명시한다.

- [ ] **Step 3: C04~C09 제외 분석형과 독립 스토퍼 릴리스형을 분리한다.**

  기존 RC 패키지는 보존한다. 무스토퍼 분석형은 `purchase_release=false`와 `fabrication_release=false`를 강제한다. 릴리스형에는 C04~C09, M10 로드/너트, 장착 체결품을 복원한다. 하한/상한 모두 `SW 210~280 mm → 공급자 확인 전기리미트 → 공차 최악 최소 1 mm 후 스토퍼 → 최소 2 mm 후 하드엔드` 계층을 요구한다. 한 스토퍼 선접촉+나머지 1축/2축 스톨, 상·하한 비대칭, 접촉위치·구동방향 순열을 3-RPS 정역학/Jacobian 전치로 해석한다. 서비스하중은 `max(750 N, 스톨추력, 2,000 N, 계산 접촉반력)`, 설계하중은 1.5배로 하고 항복 SF≥2, 파단 SF≥3, 변형≤0.5 mm, 슬롯마찰 단독지지 금지를 시험한다.

- [ ] **Step 4: 변경형 전체 검사를 세 번 반복한다.**

  Run: `python -m unittest tests.test_profile_radial_reve_approved -v`

  Expected: 변경 LMB/PHS와 독립 스토퍼 릴리스형으로 27자세, 조밀 격자, 명령선분, 조밀 시작집합×6 순차순서, 필요 시 ×6 교대순환을 모두 재실행한다. 예상 밖 충돌 0, 핀 길이 범위, 조인트 편각, 스토퍼 비접촉 운전여유와 기계 종단 접촉조건을 JSON에 기록한다.

- [ ] **Step 5: 렌더와 STEP을 생성한다.**

  collapsed, Z50, pitch/roll 복합 극값, HOME 최대기울기 자세를 각각 렌더하고 모델에 `NOT APPROVED FOR PEOPLE OR PAYLOAD`를 기록한다. 무스토퍼 분석형에는 `NOT FOR PURCHASE OR FABRICATION RELEASE`도 기록한다.

### Task 5: 전장과 펌웨어 갱신

**Files:**
- Modify: `firmware/reve_leveling_controller/reve_leveling_controller.ino`
- Modify: `firmware/reve_leveling_controller/README.md`
- Create: `tests/test_reve_approved_firmware.py`
- Modify: `outputs/profile_radial_revE_poc_release_candidate/electrical/RevE_point_to_point_wiring.csv`
- Create: `outputs/profile_radial_reve_approved_2026-09-17/electrical/e_stop_motor_power_cutoff.md`

**Interfaces:**
- Consumes: 공급자 counts/mm, 전류, 리미트/오버트래블과 컨택터 정격; Task 3 HOME 방식
- Produces: 실측 `L_low_switch`에서 파생한 210~280 mm 보호창, 축별 전류판정 HOME, E-stop 상태입력과 오류로그

- [ ] **Step 1: 실패하는 정적 인터페이스 테스트를 작성한다.**

```python
def test_firmware_uses_approved_limits_and_safe_boot():
    source = SOURCE.read_text(encoding="utf-8")
    assert "PIN_LENGTH_MIN_MM = 210.0" in source
    assert "PIN_LENGTH_MAX_MM = 280.0" in source
    assert "L_low_switch" in source
    assert "digitalWrite(MOTOR_PWM[axis], LOW)" in source
    assert "FAULT_ESTOP" in source
```

- [ ] **Step 2: 기존 테스트가 실패하는지 확인한다.**

  Run: `python -m unittest tests.test_reve_approved_firmware -v`

  Expected: 새 상수와 오류가 없어 FAIL.

- [ ] **Step 3: 보호창과 HOME 상태기를 구현한다.**

  HOME 중단, 반대방향 탈출, no-pulse endpoint 판정, 운전기준점 상승과 HOME 미완료 명령거부를 각각 명시한다. 일반 운전 no-pulse는 즉시 FAULT다. HOME 접근은 `1.0±0.2 mm/s`, `NO_PULSE_TIMEOUT_MS=clamp(max(500 ms,3×expected_pulse_period),≤2000 ms)`로 고정한다. 리미트 상태신호가 없으면 축별 전류센서로 `no-pulse AND I_axis<0.1×I_home_run`을 개방리미트 후보, `I_axis>1.5×I_home_run`을 걸림으로 구분한다. 2.0 mm 탈출≥기대카운트 90%와 재접근 2회 종단차 `max(1 count,0.25 mm×counts/mm)` 이내를 모두 요구한다. 구분신호가 없으면 자동 HOME을 금지한다.

- [ ] **Step 4: HOME 시작상태 검증을 구현한다.**

  저장된 마지막 자세가 없거나 전원차단 중 수동이동 가능성이 있거나 Task 3 시작집합 포함 근거가 없으면 `HOME_START_UNVERIFIED`로 자동 HOME을 거부한다. 감독하 블록 지지 복구절차만 허용한다.

- [ ] **Step 5: 최초 `COMMISSIONING_HOME` 상태기를 구현한다.**

  전원차단·블록지지 상태의 세 핀 길이 ±1 mm 실측과 감사 시작상태 확인을 요구한다. 모터전원 릴리스 후 한 축만 연결해 자유구간 10 mm 전류제한 JOG로 `HOME_PWM`과 `I_home_run`을 교정하고, 하한 리미트·2 mm 탈출·2회 재접근을 축별 확인한다. 이후 공통 HOME을 실행해 `L_low_switch`, counts/mm, `224.2075−L_low_switch` Z0 오프셋과 마지막 자세를 비휘발성 저장한다.

- [ ] **Step 6: E-stop 입력을 래치형 고장으로 추가한다.**

  모터전원 차단은 외부 하드웨어가 수행하고 펌웨어는 상태기록만 담당한다.

- [ ] **Step 7: Arduino 컴파일과 정적시험을 수행한다.**

  Run: `arduino-cli compile --fqbn arduino:avr:mega firmware/reve_leveling_controller`

  Expected: 컴파일 성공, PWM·방향·엔코더 핀 충돌 없음.

### Task 6: 최종 구매 릴리스 검토

**Files:**
- Modify: `outputs/20260917_powered_reve_rebaseline/powered_reve_eleparts_preliminary_bom_2026-09-17.xlsx`
- Create: `procurement/powered_reve_order_release_audit_2026-09-17.md`
- Modify: `verification/powered_reve_verification_matrix_2026-09-17.md`

**Interfaces:**
- Consumes: Tasks 1~5의 공급자·CAD·전장 결과
- Produces: 기본안, 선택 예비품, 두 번째 구매처 예외와 주문 가능/보류 판정

- [ ] **Step 1: 장바구니의 SKU·옵션·수량을 BOM과 행별 대조한다.**

  액추에이터는 24 V/100 mm/5 V 엔코더를 화면과 판매자 답변에서 이중확인한다.

- [ ] **Step 2: VAT·배송·가공비를 포함한 총액을 갱신한다.**

  기본안과 예비 액추에이터 선택안을 분리하고 두 안 모두 4,000,000원 이하인지 계산한다.

- [ ] **Step 3: 구매 게이트 G0~G9를 재검토한다.**

  하나라도 OPEN이면 `PURCHASE_RELEASE=FALSE`를 유지하고 결제하지 않는다.

- [ ] **Step 4: 네 릴리스를 분리해 판정한다.**

  구매 릴리스는 G0~G9, 제작 릴리스는 LMB/PHS 실치수·어댑터/스토퍼 도면·변경형 조밀 스크리닝·HOME 경로를 요구한다. `CONTROL_POWER_TEST_RELEASE`는 모터·드라이버 출력 분리와 무전원 도통/단락·PE·퓨즈 후 허용한다. 컨택터 전력입력에 1 A 제한 24 V 시험전압을 인가하여 E-stop 해제 출력은 입력±5%, 작동 1초 후 출력은 1.0 V 이하인지 측정한다. `MOTOR_POWER_RELEASE`는 이 시험과 PWM/드라이버 출력 0, 극성·퓨즈·전류제한 확인 뒤에만 허용한다.

- [ ] **Step 5: 사용자에게 최종 장바구니 검토를 요청한다.**

  주문수입품의 취소·반품 제한과 최장 납기를 함께 제시한다.

### Task 7: 조립·통전·자동수평 인수시험

**Files:**
- Create: `verification/powered_reve_physical_test_log_2026-09-17.xlsx`
- Modify: `verification/powered_reve_verification_matrix_2026-09-17.md`
- Create: `outputs/profile_radial_reve_approved_2026-09-17/physical_test_report.md`

**Interfaces:**
- Consumes: 조립 완료 하드웨어와 승인 펌웨어
- Produces: 입고·조립·E-stop·HOME·Z·자동수평의 사진, 계측값과 최종 PoC 판정

- [ ] **Step 1: 입고와 실측을 기록한다.**

  액추에이터 최소/최대 핀 거리, LMB 홀과 핀, PHS 외형을 측정하고 CAD값과 차이를 기록한다.

- [ ] **Step 2: 전원 미인가 기구검사를 수행한다.**

  프레임 대각선, 체결, 핀 이탈방지, 케이블 여유와 손 끼임 영역을 사진으로 남긴다.

- [ ] **Step 3: 제어전원 시험 릴리스를 수행한다.**

  액추에이터 모터와 드라이버 모터출력을 분리하고 무전원 도통·단락, 보호접지, 분기퓨즈를 확인한다. 5 V 제어부와 24 V 컨택터 코일을 통전하고 컨택터 전력입력에는 1 A 제한 24 V 시험전압만 인가한다. E-stop 해제 출력이 입력±5%, 작동 1초 후 1.0 V 이하이며 제어기가 오류를 기록하는지 확인한다. 통과 전에는 모터를 연결하지 않는다.

- [ ] **Step 4: 모터전원 릴리스 후 축별 시운전을 수행한다.**

  PWM/드라이버 출력 0, 극성, 퓨즈와 전류제한을 확인해 `MOTOR_POWER_RELEASE=TRUE`로 한 뒤 A1, A2, A3를 각각 짧게 저속 JOG해 극성·엔코더·리미트·전류를 확인하고 3축으로 확대한다.

- [ ] **Step 5: HOME과 Z 시험을 수행한다.**

  최초에는 `COMMISSIONING_HOME`으로 HOME_PWM, I_home_run, `L_low_switch`, counts/mm와 Z0 오프셋을 저장한다. 이후 일반 HOME 3회, Z 0/25/50 mm 왕복 3회를 수행하고 백래시, 수평오차와 최대전류를 기록한다.

- [ ] **Step 6: 정적 각도와 자동수평 시험을 수행한다.**

  상부 제어 IMU와 하부 IMU는 동일 Mega2560 `micros()`로, 독립 상부 기준계는 TTL 또는 공통 동기 이벤트로 정렬해 시험 전후 timestamp skew≤25 ms를 확인한다. 기준계는 ±5° 정확도≤±0.2°, 분해능≤0.05°이고 -3/0/+3°에서 축·부호·영점 잔차≤0.2°를 확인한다. 모두 20 Hz 이상 기록한다. 정적 합격은 독립 상부 기준계 1초 평균이 하부 정지 후 5초 이내 `|pitch|≤1° AND |roll|≤1°`에 진입해 10초 유지하는 것이다. 동적 시험은 하부 합성 각속도≤1°/s에서 운동개시(0.1°/s 초과) 2초 후부터 두 축 동시충족 표본≥90%, 기준계 원시값 어느 축도 2° 초과 금지로 판정한다. 독립 상부 기준계가 없으면 `POC_ACCEPTANCE=PROVISIONAL`이다.

- [ ] **Step 7: 오류시험과 최종판정을 수행한다.**

  E-stop, IMU stale, 엔코더 무펄스 모의, 범위초과 명령을 확인한다. 모든 필수항목과 사진이 있으면 `POC_ACCEPTANCE` 판정을 갱신한다.

## Self-review

- 승인 요구사항 Z 0~50 mm, ±3°, 자동수평, 자중 시연, 단일구매처, 일괄구매와 사진기록이 각각 Task 1~7에 연결됐다.
- 기계식 스토퍼 생략은 안전 완료가 아니라 프로젝트 규칙과 충돌하는 릴리스 차단 편차로 유지됐다.
- 조밀 시작집합의 공통 HOME 순차/교대 경로는 Task 3에서 구매 전 게이트로 처리됐다.
- 전류·리미트·조인트 치수와 E-stop DC 정격은 공급자 자료 없이는 확정되지 않는다.
- 미정 내용을 숨기는 자리표시자 없이 각 미결사항의 증거와 종료조건을 명시했다.
- 인터페이스 이름은 Task 2와 Task 3 안에서 일관되게 정의했다.

## Execution Handoff

계획 실행은 두 방법 중 하나로 진행한다.

1. Subagent-Driven: 작업별 별도 에이전트와 단계별 검토
2. Inline Execution: 현재 세션에서 `executing-plans` 절차로 순차 실행

이 프로젝트는 사용자 요청 없이 하위 에이전트를 시작하지 않는다.
