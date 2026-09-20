# 전동식 수평유지장치 발주·조립·시운전 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. 각 작업은 체크박스로 진행 상태를 기록한다.

**Goal:** 현재 검증된 Rev E CAD를 기준으로 부품을 한 번에 발주하고, 무적재 공개형 시제품을 조립하여 시작 명령에 의한 자동수평 시연과 결과보고서 사진 증빙까지 완료한다.

**Architecture:** 모터뱅크의 LM4075OE 액추에이터와 LMB-10, 한국미스미의 TRUSCO PHS6 및 프로파일/체결품을 사용한다. 기존 3-RPS 프레임과 120 x 70 x 8 mm 하부 어댑터를 유지하고, 상부 PHS6에는 핀 축 방향 1.5 mm 간격을 둔다. 구조 검증, 입고검사, 무전원 조립, 축별 저속 확인, 3축 자동수평 순서로 위험을 단계적으로 제한한다.

**Tech Stack:** CadQuery/OpenCascade STEP, 24 V LM4075OE 3축, 내장 리미트, 엔코더, IMU, Arduino Mega 계열 제어기, 모터 드라이버 3채널, 알루미늄 프로파일 볼트 조립

**Spec:** `outputs/profile_radial_revE_supplier_interface_2026-09-17/README_KO.md`

## Global Constraints

- 카트·적재물·사람을 올리지 않는 공개형 자중 시연만 수행한다.
- 상부 자유도는 Z, pitch, roll이며 X, Y, yaw는 기구적으로 구속한다.
- 수직 이동은 50 mm, 자세 범위는 pitch/roll ±3도를 기준으로 한다.
- 자동수평은 사용자가 시작 명령을 내렸을 때만 동작한다.
- 액추에이터 내장 리미트만 사용하며 이번 시제품 출력에는 외부 기계식 스토퍼를 추가하지 않는다.
- 절단·용접보다 프로파일과 볼트 조립을 우선하고, 필요한 경우에만 탭가공을 허용한다.
- 액추에이터와 LMB-10은 모터뱅크, PHS6와 기구 표준품은 한국미스미를 기본 구매처로 한다.
- 디지털 CAD PASS는 사람 탑승, 적재 운반, 현장 안전 또는 인증을 의미하지 않는다.
- 결과보고서 제출 목표는 2026년 11월 말이며 각 단계의 사진을 남긴다.

---

### Task 1: 최종 발주 BOM 잠금

**Files:**
- Read: `procurement/reve_supplier_split_check_2026-09-17.md`
- Read: `outputs/20260917_powered_reve_rebaseline/powered_reve_eleparts_preliminary_bom_2026-09-17.xlsx`
- Create: `procurement/reve_final_order_bom_2026-09-17.xlsx`
- Create: `procurement/reve_final_order_bom_2026-09-17.csv`

**Interfaces:**
- Consumes: Rev E STEP, 공급처 분할 확인서, 기존 전기부품 예비 BOM
- Produces: 공급처·형번·수량·가격·납기·대체 허용 여부가 고정된 주문표

- [x] **Step 1:** 모터뱅크 주문행을 `LM4075OE-1075 24 V 100 mm` 3개와 `LMB-10` 3세트로 고정한다.
- [x] **Step 2:** 미스미 주문행을 TRUSCO `PHS6`, 발주코드 `280-7599`, 2팩(팩당 2개)으로 고정한다.
- [x] **Step 3:** 4040/3030 프로파일, 120 x 70 x 8 mm 어댑터 3개, 프로파일 브래킷, T너트와 볼트의 기존 수량을 CAD와 대조한다.
- [x] **Step 4:** 상부 조인트용 M6 x 50 및 M6 x 55 볼트 각 3개 이상, M6 나일론 너트, 0.5 mm shim washer 최소 12개를 포함한다. 실제 조립에서는 축당 총 1.5 mm를 사용한다.
- [x] **Step 5:** PHS6 고정용 3030 슬롯 대응 M6 T볼트/스터드와 잼너트 3세트 및 1세트 예비를 포함한다.
- [x] **Step 6:** 전기 BOM에서 전원공급기, 3채널 모터 드라이버, 제어기, IMU, 퓨즈, 단자대, STOP/START 조작부, 배선과 커넥터가 빠지지 않았는지 확인한다.
- [x] **Step 7:** 액추에이터, LMB-10, PHS6는 대체 금지로 표시하고 일반 볼트·와셔·T너트만 동등품 대체 허용으로 표시한다.
- [x] **Step 8:** 총액, VAT, 배송비와 납기를 공급처별로 합산하고 11월 조립 일정에 늦는 항목을 표시한다.

**Acceptance:** 수량 또는 형번이 미정인 행이 없고, 모든 품목에 구매 URL 또는 형번이 있다.

---

### Task 2: 장바구니·결제 전 최종 확인

> 2026-09-17: 결제 전 증빙 체크리스트는 작성 완료. 장바구니 입력·결제·화면 캡처는 아직 수행하지 않았다.

**Files:**
- Create: `procurement/order_evidence/`
- Create: `procurement/order_evidence/order_checklist_2026-09-17.md`

**Interfaces:**
- Consumes: Task 1 최종 BOM
- Produces: 결제 직전 장바구니 캡처와 납기 증빙

- [ ] **Step 1:** 모터뱅크 장바구니에 액추에이터 3개와 LMB-10 3세트를 넣고 옵션, 전압, 스트로크, 수량을 화면에서 다시 확인한다.
- [ ] **Step 2:** 한국미스미 장바구니에 PHS6 2팩과 기구 표준품을 넣고 발주코드 `280-7599`를 확인한다.
- [ ] **Step 3:** 전기전자 부품이 미스미에서 모두 충족되지 않으면 나비엠알오 장바구니만 별도로 사용한다.
- [ ] **Step 4:** 각 장바구니의 품목, 수량, 가격, 예상 출하일이 보이도록 전체 화면을 저장한다.
- [ ] **Step 5:** 품절·장기납기 항목은 결제 전에만 대응하고, 액추에이터나 조인트 형번을 임의 대체하지 않는다.

**Acceptance:** 핵심 기구품은 모터뱅크+미스미 두 주문 안에 들어가며 카드결제가 가능하다.

---

### Task 3: 입고검사와 치수 기록

**Files:**
- Create: `verification/reve_prototype/incoming_inspection.csv`
- Create: `verification/photos/incoming/`

**Interfaces:**
- Consumes: 입고 부품, A1 상세 STEP
- Produces: 조립 전 치수 적합 판정과 사진

- [ ] **Step 1:** 박스 라벨, 형번, 수량, 외관을 개봉 전후로 촬영한다.
- [ ] **Step 2:** LMB-10 내폭, 장착홀 피치 36 mm, 피벗홀 Ø6.2를 측정한다.
- [ ] **Step 3:** 액추에이터 전·후단 아이 폭과 구멍 지름, 최소/최대 핀 중심거리를 측정한다.
- [ ] **Step 4:** PHS6 축방향 폭, Ø6 보어, M6 암나사와 전체 높이를 측정한다.
- [ ] **Step 5:** LMB 내폭이 액추에이터 후단 아이보다 넓고, PHS6+액추에이터 전단 아이+1.5 mm shim stack이 선택한 M6 볼트의 유효 길이 안에 들어오는지 확인한다.
- [ ] **Step 6:** 불일치가 있으면 프레임이나 플레이트를 즉시 가공하지 말고 shim 수량 또는 M6 볼트 길이만 먼저 조정한다.

**Acceptance:** 세 축 모두 핀 삽입이 가능하고 조인트가 손으로 자유롭게 회전하며, 조립을 막는 치수 불일치가 없다.

---

### Task 4: 무전원 기계 조립

**Files:**
- Read: `outputs/profile_radial_revE_supplier_interface_2026-09-17/README_KO.md`
- Create: `verification/photos/mechanical_assembly/`
- Create: `verification/reve_prototype/mechanical_assembly_log.md`

**Interfaces:**
- Consumes: 검사 완료 부품, 조립 STEP
- Produces: 전원을 연결하지 않은 3축 완성 기구

- [ ] **Step 1:** 하부 프레임을 평면에 놓고 대각 치수를 비교하여 직각을 맞춘다.
- [ ] **Step 2:** 하부 어댑터 3개와 LMB-10을 느슨하게 체결한다.
- [ ] **Step 3:** 액추에이터 세 개의 핀 중심거리를 약 242.9 mm로 맞춘다.
- [ ] **Step 4:** 하부 아이를 LMB-10에 연결하고 핀과 클립을 체결한다.
- [ ] **Step 5:** 상부 프레임은 사람 또는 받침 블록으로 지지하고 액추에이터에 하중을 걸지 않는다.
- [ ] **Step 6:** PHS6를 3030 슬롯에 체결하고 각 축에 1.5 mm shim 간격을 적용한 뒤 M6 피벗 볼트를 넣는다.
- [ ] **Step 7:** 세 액추에이터를 모두 연결한 뒤 어댑터와 슬롯 체결을 최종 조인다.
- [ ] **Step 8:** 손으로 상부를 천천히 ±3도 움직여 간섭, 걸림, 볼트 풀림과 케이블 예상 경로를 확인한다.
- [ ] **Step 9:** 전체, 하부, 상부, 각 축 조인트, 체결부 근접 사진을 촬영한다.

**Acceptance:** 무전원 상태에서 세 조인트가 걸리지 않고, 상부 프레임이 X/Y/yaw 방향으로 눈에 띄게 유격 이동하지 않는다.

---

### Task 5: 전기 결선과 저속 축별 확인

**Files:**
- Read: `outputs/profile_radial_revE_poc_release_candidate/electrical/`
- Read: `firmware/reve_leveling_controller/reve_leveling_controller.ino`
- Create: `verification/photos/electrical_assembly/`
- Create: `verification/reve_prototype/axis_commissioning.csv`

**Interfaces:**
- Consumes: 기계 조립체, 전기 BOM, 제어 펌웨어
- Produces: 방향·엔코더·내장 리미트가 확인된 세 축

- [ ] **Step 1:** 전원을 끈 상태에서 축별 퓨즈, 드라이버, 모터, 엔코더와 공통 접지를 결선한다.
- [ ] **Step 2:** START 입력 없이 전원만 인가했을 때 액추에이터가 움직이지 않는지 확인한다.
- [ ] **Step 3:** `STATUS`로 세 축 엔코더와 IMU 값이 갱신되는지 확인한다.
- [ ] **Step 4:** A1만 저속으로 5 mm 이내 JOG하고 명령 방향과 엔코더 증가 방향을 기록한다.
- [ ] **Step 5:** A2와 A3에도 같은 확인을 반복한다.
- [ ] **Step 6:** 각 축을 저속으로 내장 리미트 근처까지 이동시키되, 고정 구조물에 힘이 걸리기 전에 STOP이 가능한 상태를 유지한다.
- [ ] **Step 7:** `STOP` 명령과 물리 조작부가 세 축을 즉시 정지시키는지 확인한다.
- [ ] **Step 8:** 결선 전경, 축별 라벨, 퓨즈, 드라이버와 조작부 사진을 촬영한다.

**Acceptance:** 무명령 자발 동작이 없고, 세 축 방향과 엔코더가 일치하며, 내장 리미트와 STOP이 모두 동작한다.

---

### Task 6: 자동수평 무부하 시운전

**Files:**
- Create: `verification/reve_prototype/auto_level_trials.csv`
- Create: `verification/photos/auto_level_demo/`

**Interfaces:**
- Consumes: 축별 확인 완료 조립체
- Produces: 시작 명령 기반 자동수평 시연 데이터

- [ ] **Step 1:** 받침 블록으로 하부 프레임을 수평에 놓고 `ZERO_IMU`를 수행한다.
- [ ] **Step 2:** `HOME` 후 세 축 길이와 초기 pitch/roll을 기록한다.
- [ ] **Step 3:** 하부 프레임 한쪽을 천천히 들어 약 2도 기울이고, 상부가 움직이지 않은 상태의 초기값을 기록한다.
- [ ] **Step 4:** 사용자가 `LEVEL` 시작 명령을 내리고 상부 pitch/roll이 감소하는 과정을 영상으로 촬영한다.
- [ ] **Step 5:** 전·후·좌·우 네 방향과 한 번의 대각 방향에서 같은 시험을 수행한다.
- [ ] **Step 6:** 한 시험이라도 진동, 역방향 발산, 리미트 반복 충돌 또는 구조 걸림이 나타나면 즉시 STOP하고 제어 이득만 낮춘 뒤 반복한다.
- [ ] **Step 7:** Z=0, 25, 50 mm 대표 높이에서 상부 수평 유지 여부를 확인한다.

**Acceptance:** 모든 시험은 무적재로 수행하며, 시작 명령 전에는 정지하고 시작 명령 후에는 초기 pitch/roll 오차가 지속적으로 감소한다. 시제품이므로 절대 정확도를 임의로 PASS 처리하지 않고 실제 수치를 보고서에 기록한다.

---

### Task 7: 결과보고서 증빙 정리

**Files:**
- Create: `reports/reve_prototype_evidence_index.md`
- Create: `reports/reve_prototype_result_draft.docx`

**Interfaces:**
- Consumes: 주문 캡처, 입고검사, 조립사진, 결선사진, 자동수평 로그·영상
- Produces: 11월 말 제출용 결과보고서 초안

- [ ] **Step 1:** 요구사항, 설계 선택, 공급품 선정 이유와 구매처 분할 사유를 정리한다.
- [ ] **Step 2:** CAD 27자세 PASS와 실물시험을 별도 표로 구분한다.
- [ ] **Step 3:** 부품 입고부터 프레임, 조인트, 전기결선, 시운전까지 시간순 사진을 배치한다.
- [ ] **Step 4:** 자동수평 시험별 초기/최종 pitch·roll, 동작시간, 이상 유무를 표로 작성한다.
- [ ] **Step 5:** 외부 기계식 스토퍼를 사용하지 않고 액추에이터 내장 리미트를 사용했다는 범위를 명시한다.
- [ ] **Step 6:** 무적재 실내 시제품이며 사람 탑승·운반·현장 안전을 입증하지 않았다고 명시한다.

**Acceptance:** 모든 주장에 사진, 로그 또는 CAD 검증 파일이 연결되고 미실시 항목이 완료된 것처럼 표현되지 않는다.

---

## Self-Review

- 요구사항 커버리지: 자동수평, 50 mm Z, ±3도, 무적재, 시작 명령, 내장 리미트, 볼트 조립, 2개 공급처, 사진 중심 보고서를 모두 작업에 연결했다.
- 범위 제외: 카트 본체, 구동 휠, AMR/AGV, 사람 탑승과 적재 운반은 포함하지 않았다.
- 핵심 잔여 위험: PHS6 축방향 폭과 M6 유효길이는 입고검사로 닫고, 저비용 M6 볼트 두 길이와 shim washer를 함께 주문해 재가공을 피한다.
