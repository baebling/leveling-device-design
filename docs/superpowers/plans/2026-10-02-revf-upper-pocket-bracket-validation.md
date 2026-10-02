# Rev F 상부 포켓 브래킷 검증 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 축당 압축·인장 750 N을 기준으로 상부 완성가공 포켓 브래킷 3개를 설계·검증하고, 실제 국내 조달 및 Rev F BOM의 발주 가능 여부를 근거별로 판정한다.

**Architecture:** 기존 Rev E의 공급자 STEP·수정 운동학은 읽기 전용 기준선으로 둔다. Rev F의 입력/하중·CAD·간섭·출력·BOM을 별도 파일로 만들며, 기구적 적합성과 구매 릴리스는 별도의 게이트로 관리한다. 조건 미충족 시 물건을 억지로 추천하지 않고 원인과 최소 설계 변경안을 남긴다.

**Tech Stack:** Python 3.12.10, CadQuery 2.8.0/OCP 7.9.3.1, `unittest`; 공급자 STEP 및 제조사 도면; 기존 Excel 양식은 `@oai/artifact-tool`로 복제·편집·렌더링한다.

**Spec:** [승인된 설계 명세](../specs/2026-10-02-upper-pocket-bracket-design.md)

## Global Constraints

- 사용자는 기존 A1~A3 알루미늄판 가공과 신규 **업체 완성가공 상부 브래킷 3개**만 금속가공으로 허용했다. 플라스틱 전장함 타공은 별도 허용. 독립 스토퍼는 이번 감독하 자중 시연에서 제외한다.
- 카트·적재물·사람 없음; 3-RPS, 명령 Z=0~50 mm, pitch/roll 동시 ±3°, 독립 X/Y/yaw 구속. 각 액추에이터 축하중 ±750 N에서 정적 안전율 목표 ≥1.5. 이는 스톨·충격·피로·인증 안전을 보증하지 않는다.
- `PURCHASE_RELEASE`, `FABRICATION_RELEASE`, `CONTROL_POWER_TEST_RELEASE`, `MOTOR_POWER_RELEASE`는 증거가 갖춰질 때까지 모두 `FALSE`. 사용자의 개념 승인과 이 구현계획은 발주나 통전을 승인하지 않는다.
- Rev E 원본 CAD/시험/엑셀을 덮어쓰지 않는다. 특히 기존 `_local_phs6_shape()`, `upper_phs_fastener_local_shapes()`, `collision_audit()`, `full_pose_audit()`는 새 관절의 검증으로 재사용하지 않는다. 기존 `group_shape("upper_frame")` 단면도 실제 DNF3030 슬롯의 최종 증거가 아니다.
- 기본 실행환경은 PowerShell에서 `$env:PYTHONPATH='C:\Users\gangm\.cache\leveling-cadquery-py312'` 후 `python -m unittest ...`. 기존 회귀시험 `python -m unittest tests.test_reve_upper_pin_alignment -v` 1개 통과를 확인했다. 다른 Python 환경에 CadQuery를 설치하거나 저장소의 `node_modules`를 건드리지 않는다.
- 각 단계는 실패하는 검증을 먼저 만들고 최소 구현으로 통과시키되, 제조사 근거가 없는 치수·정격은 `UNKNOWN/HOLD`로 둔다. 신형 기구가 기존 운동학의 S 중심을 바꾸면 HOME/JOG/조밀 경로 검증을 다시 수행한다.
- 단계별 검증 뒤 해당 파일만 커밋하고 `origin`의 현 `codex/reve-progress-backup-20261001` 브랜치에 백업한다. 기존의 무관한 untracked 파일은 stage하지 않는다. 실제 구매·결제는 하지 않는다.

---

## Task 1 — 공급자 치수와 구매 기준선 고정

**Files:** `references/revf_upper_pocket_source_register_2026-10-02.md` 생성; `cad/revf_upper_pocket_inputs.py` 및 `tests/test_revf_upper_pocket_inputs.py` 생성. 기준 자료는 `references/vendor_cad/LM4075OE-1075-100mm.stp`, [PHS6 제조사 도면](https://image.trusco-sterra2.com/pdf/zumen/PHS6_4500__ZM.pdf), [MSB6 공식 도면](https://kr.misumi-ec.com/pdf/press/2018_pr_1011.pdf), 실제 DNF3030 단면과 선택 T너트 제조사 도면이다.

**Interfaces:** `PocketInputs`는 `bracket_count:int`, `eye_hole_bounds_mm:tuple[float,float]`, `pin_dmin_mm:float`, `eye_offset_mm:float`, `phs_outer_d_mm:float`, `phs_outer_width_mm:float`, `phs_ball_width_mm:float`, `shoulder_contact_length_mm:float|None`, `profile_slot_width_mm:float|None`, `profile_slot_verified:bool`, `purchase_release:bool` 필드를 갖는다. `load_inputs() -> PocketInputs`, `source_complete(inputs: PocketInputs) -> bool`을 제공한다. 다음 태스크는 이 객체와 `source_complete()`만 소비한다.

- [ ] 현 상품·도면을 다시 열어 정확한 형번, 치수, 공차, 링크와 확인일을 표에 기록한다. 액추에이터 전면 eye 홀은 공급 STEP Ø6.0과 판매도면 Ø6.4를 **서로 다른 경계**로 기록한다. `TRUSCO PHS6` 제조사 자료와 현 BOM의 `THK PHS6` 표기가 동일 주문품인지 확인하고 조용히 동치로 취급하지 않는다. MSB6 연속 평활 어깨 길이·필릿, T너트/프로파일 슬롯 치수가 없다면 빈칸 대신 `UNKNOWN`과 그 영향을 적는다.
- [ ] 입력 검증 테스트를 먼저 작성한다. 아래 검사처럼 어깨 접촉 길이를 `None`으로 만든 보수적 사례가 `source_complete=False`이고 구매 릴리스도 false인지 확인한다. `python -m unittest tests.test_revf_upper_pocket_inputs -v`가 신규 모듈 부재로 실패하는 것을 확인한다.
- [ ] 테스트의 핵심은 아래와 같이 작성한다. `None`은 추측값이 아니라 실제 제조사 근거가 아직 없는 상태다.

```python
from dataclasses import replace
from cad.revf_upper_pocket_inputs import load_inputs, source_complete
inputs = load_inputs()
assert inputs.bracket_count == 3
assert inputs.eye_hole_bounds_mm == (6.0, 6.4)
assert source_complete(replace(inputs, shoulder_contact_length_mm=None)) is False
assert inputs.purchase_release is False
```

- [ ] `revf_upper_pocket_inputs.py`를 구현한다. 형상 값과 근거 URL/로컬 경로를 한 곳에 두고, 불명값을 임의 숫자로 메우지 않는다. `source_complete`는 필수 도면·공차가 모두 채워져야만 참이다. 같은 명령으로 테스트를 통과시킨다.
- [ ] 소스 불일치가 포켓 가공치수나 핀 접촉위치를 바꾼다면 다음 태스크는 **범위 양쪽 스크리닝**까지만 진행하고 제작치 확정은 멈춘다. 소스 등록표와 테스트 결과를 독립 검토 후 커밋한다.
- [ ] `git add references/revf_upper_pocket_source_register_2026-10-02.md cad/revf_upper_pocket_inputs.py tests/test_revf_upper_pocket_inputs.py`와 `git commit -m "Document Rev F pocket source dimensions"`를 실행한 뒤 원격에 푸시한다.

## Task 2 — 핀·포켓·프로파일의 하중 및 공차 스크리닝

**Files:** `calculations/revf_upper_pocket_load_screen.py`, `tests/test_revf_upper_pocket_load_screen.py`, `outputs/profile_radial_revF_upper_pocket_review_2026-10-02/load_screen.json`.

**Interfaces:** `screen_loads(inputs: PocketInputs, force_n: float) -> dict[str, object]`는 `pin_bending_mpa`, `pin_shear_mpa`, `unverified`, `strength_gate`, `purchase_release`를 돌려준다. 양의 힘과 음의 힘을 모두 입력한다.

- [ ] 먼저 실패 테스트를 만든다. `M=750*16=12000 N·mm`, `d_min=5.95 mm`에서 핀 단독 굽힘 약 580 MPa를 재현하고, `F=−750/+750 N` 두 부호가 모두 포함되며, `Kt`, 제조사 허용 면압, 실제 나사물림 또는 슬롯 허용하중이 미상일 때 `strength_gate=False`인지 확인한다. 실행: `python -m unittest tests.test_revf_upper_pocket_load_screen -v`.
- [ ] 첫 테스트는 다음 수치 검산으로 시작한다. 신규 모듈 부재에 따른 실패를 확인한 뒤 구현한다.

```python
from dataclasses import replace
from cad.revf_upper_pocket_inputs import load_inputs
from calculations.revf_upper_pocket_load_screen import screen_loads
for force_n in (-750.0, 750.0):
    result = screen_loads(load_inputs(), force_n)
    assert abs(result["pin_bending_mpa"] - 580.0) < 2.0
    assert result["strength_gate"] is False
    assert result["purchase_release"] is False
```

- [ ] 자유물체도와 세 축별 하중경로를 코드·보고서에 명시한다: eye → Ø6 핀 → PHS6 내륜/외륜 → 포켓·M6 → 브래킷 → 다점 체결 → 3030 슬롯. 핀 굽힘 `32Fe/(πd³)`, 단전단 `F/(πd²/4)`, 합성응력과 1.5 목표를 계산하되, 단순 핀값 `~1.6`을 관절 전체의 합격값으로 사용하지 않는다. 전면 eye와 하부 힌지의 반력, M6 체결 반전, 브래킷 웹·포켓 국부접촉, T너트 인발·미끄럼·프로파일 립 면압을 별도 항목으로 둔다.
- [ ] 불리한 hole·pin·shim·볼 폭·가공 공차와 pin shoulder-thread 전환부를 포함한다. 데이터가 없으면 해당 하중항목에 `unverified` 및 `strength_gate=False`를 반환하도록 구현하고 테스트를 통과시킨다. 750 N은 최대 고장하중이 아니므로 스톨·과부하 검증을 결과에서 분리한다.
- [ ] 독립 검토에서 계산식, 단위, 하중 부호 및 미확정값 처리 확인. `load_screen.json`은 `review_only=true`와 모든 릴리스 `false`로 저장하고 커밋한다.
- [ ] `python -m unittest tests.test_revf_upper_pocket_load_screen -v` 통과 후 `git add calculations/revf_upper_pocket_load_screen.py tests/test_revf_upper_pocket_load_screen.py outputs/profile_radial_revF_upper_pocket_review_2026-10-02/load_screen.json`과 `git commit -m "Screen Rev F upper joint load paths"`를 실행하고 푸시한다.

## Task 3 — 새 관절·브래킷 CAD와 1축 조립 경로

**Files:** `cad/profile_radial_revf_upper_pocket_review.py`, `tests/test_revf_upper_pocket_review.py`. 기존 `cad/profile_radial_reve_actual_vendor.py`는 수정 없이 `Pose`, `solve_reve_platform`, `platform_transform`, `upper_eye_points`, `actuator_parts`, 실제 공급자 STEP 로더만 활용한다.

**Interfaces:** `pocket_brackets(inputs: PocketInputs) -> tuple[Part, Part, Part]`, `phs_components(axis_index: int, pose: Pose) -> dict[str, cq.Shape]`, `revf_components_for_pose(pose: Pose, inputs: PocketInputs) -> list[Part]`를 제공한다. `Part`와 `Pose`는 기존 `cad.profile_radial_reve_actual_vendor`의 자료형이다. 축 번호는 1, 2, 3이다.

- [ ] 먼저 실패하는 형상 테스트를 쓴다: `len(pocket_brackets(load_inputs())) == 3`; PHS6 외륜과 내륜/볼이 별개 솔리드; 포켓이 외륜을 지지하되 볼·내륜의 편각창을 침범하지 않음; 액추에이터 eye를 브래킷에 추가 고정하는 귀가 없음; Ø6 핀축이 세 eye/볼 중심과 일치. 실행: `python -m unittest tests.test_revf_upper_pocket_review -v`.
- [ ] 첫 형상 테스트는 `len(pocket_brackets(load_inputs())) == 3`과 각 `Part.name`의 유일성, `phs_components(1, Pose("neutral",25,0,0))`에 `housing`, `ball`이 별도 키로 존재하는지부터 검사한다. 같은 테스트에서 `revf_components_for_pose(...)`에 구형 `UPPER_PHS_FASTENER_STACK` 구성품이 없는지도 검사한다. 신규 모듈 부재 실패를 먼저 확인한다.
- [ ] 한 축의 S45C/SM45C 포켓과 다점 프로파일 체결을 파라메트릭 형상으로 만든 뒤 120° 방향별 3개에 적용한다. 실제 방향별로 같지 않으면 같은 제품 3개라고 표시하지 않는다. PHS6 바깥 하우징 포획, M6 이탈방지, eye20 + 볼9 + shim1.5 명목 그립 30.5 mm, 핀 머리·M5 너트·스페이서, 장착 공구 접근 공간을 모두 모델에 넣는다.
- [ ] 삽입·체결 순서의 모든 단계에서 부품을 통과시켜야 하는 경로를 검사한다. 의도된 접촉과 관통 간섭을 분리한다. 공급자 도면의 미확정 필릿/어깨 길이는 단순 원통으로 대체해 `조립 가능`이라고 하지 않는다.
- [ ] 한 축 테스트와 기존 `python -m unittest tests.test_reve_upper_pin_alignment tests.test_reve_supplier_interface_cad tests.test_reve_upper_joint_candidate_screen_20261002 -v`를 통과시킨다. 구형 후보의 탈락 판정은 바꾸지 않는다. 검토 후 커밋한다.
- [ ] 위 명령 통과 후 `git add cad/profile_radial_revf_upper_pocket_review.py tests/test_revf_upper_pocket_review.py`와 `git commit -m "Model Rev F upper pocket joints"`를 실행하고 푸시한다.

## Task 4 — 3축 자세·명령·HOME 간섭과 리뷰용 3D 출력

**Files:** `cad/revf_upper_pocket_pose_audit.py`, `tests/test_revf_upper_pocket_pose_audit.py`, `scripts/export_revf_upper_pocket_review.py`, `outputs/profile_radial_revF_upper_pocket_review_2026-10-02/`.

**Interfaces:** `review_poses() -> tuple[Pose, ...]`는 조밀 격자 1859개를 준다. `audit_pose(pose: Pose, inputs: PocketInputs) -> dict[str, object]`, `audit_all(inputs: PocketInputs) -> dict[str, object]`가 각각 단일·전체 자세 결과를 준다. 두 결과는 `invalid_boolean_count`, `purchase_release`, `fabrication_release`를 반드시 포함한다.

- [ ] 실패 테스트를 먼저 작성한다. 27 대표자세와 `Z=0:5:50 mm`, pitch/roll `−3:0.5:+3°` 조밀 격자(11×13×13=1859 자세), 허용 명령선분·HOME 경로가 각각 집계되고, 모든 축의 eye/핀·볼 편각·완전한 체결 적층 및 다른 축 액추에이터·프레임의 **비의도적** 관통이 검사 대상에 있어야 한다. 기존 옛 슬롯 단면만 사용한 결과는 `profile_slot_status=UNVERIFIED`와 릴리스 false를 강제한다.
- [ ] 첫 단위시험은 아래처럼 검사 격자와 보수적 판정을 고정한다. `python -m unittest tests.test_revf_upper_pocket_pose_audit -v`의 신규 모듈 부재 실패를 확인한다.

```python
from dataclasses import replace
from cad.revf_upper_pocket_inputs import load_inputs
from cad.revf_upper_pocket_pose_audit import review_poses, audit_pose
from cad.profile_radial_reve_actual_vendor import Pose
assert len(review_poses()) == 1859
screen = audit_pose(Pose("neutral", 25.0, 0.0, 0.0), replace(load_inputs(), profile_slot_verified=False))
assert screen["profile_slot_status"] == "UNVERIFIED"
assert "invalid_boolean_count" in screen
assert screen["purchase_release"] is False
```

- [ ] 실제 STEP 기반 Rev F 조립으로 위 검사를 구현한다. **27 대표자세는 정확 B-rep 검사를 실행**하고, 1859 조밀 격자와 명령/HOME 경로는 모든 자세에서 길이·편각·보수적 bounding-volume broad phase를 검사한다. broad phase의 간섭 가능/근접 자세에만 정확 Boolean을 추가한다. 잘못된 Boolean 또는 계산 미완료인 자세는 `UNKNOWN/HOLD`로 남기며, `assembly_path_review().nominal_sample_clear`만으로 `clear` 판정하지 않는다. 이는 기존 27자세 검사에 약 394초가 걸린 실행환경의 계산량을 고려한 보수적 순서다.
- [ ] 합격 자세와 최악 간섭/편각 자세, 위치·부품쌍·체적·invalid Boolean 수를 JSON에 남긴다. 본체 간섭 외에 포켓 조립 경로, 핀 삽입·너트 및 렌치 접근, 상·하한 여유를 별도 기록한다. S 중심이 변하면 `tests.test_reve_approved_workspace`, `tests.test_reve_home_path_audit`, `tests.test_reve_command_jog_path_audit` 및 신규 모델 경로를 재계산한다. 조밀 격자를 연속영역의 수학적 증명으로 표현하지 않는다.
- [ ] `python -m unittest tests.test_revf_upper_pocket_pose_audit -v`를 통과시키고 `python scripts/export_revf_upper_pocket_review.py`로 리뷰용 STEP·렌더·감사 JSON·SHA256 manifest를 생성한다. 렌더와 README에 `REVIEW ONLY / NOT APPROVED FOR FABRICATION`을 넣는다. 제작 DXF/CNC 도면은 만들지 않는다.
- [ ] 출력 JSON에서 모든 릴리스 flag false, 3개 브래킷, 모든 검사자세·실패자세가 누락 없이 기록됐는지 독립 검토한다. 실제 DNF3030 슬롯 단면 또는 제조사 허용치 부재는 합격으로 바꾸지 않고 blocker로 남긴다. 검증된 출력만 커밋한다.
- [ ] `git add cad/revf_upper_pocket_pose_audit.py tests/test_revf_upper_pocket_pose_audit.py scripts/export_revf_upper_pocket_review.py outputs/profile_radial_revF_upper_pocket_review_2026-10-02`와 `git commit -m "Audit and export Rev F pocket review geometry"`를 실행하고 푸시한다.

## Task 5 — 3축 상부 브래킷 체결부 방향 수정과 조립 경로 재검증

**왜 추가됐나:** Task 4의 독립 검수에서 기존 동일형 브래킷 3개의 구멍이 실제 상부 3030 가로바의 X방향 슬롯과 맞지 않는 것이 확인됐다. A1 볼트는 가로바를 빗나가고 A2/A3 볼트는 모델의 벽을 관통한다. 잘못된 리뷰 STEP로 견적을 요청하지 않는다. 이는 새 사용자 요구가 아니라 기존 승인안의 필수 결함 수정이다.

**Files:** `cad/profile_radial_revf_upper_pocket_review.py`, `tests/test_revf_upper_pocket_review.py`, 필요하면 `references/revf_upper_pocket_source_register_2026-10-02.md`. Rev E 원본 프레임/운동학 코드는 읽기 전용으로 유지한다.

**Interfaces:** 축별 완성 브래킷 형상과 장착품을 반환한다. 기존 `pocket_brackets(inputs)`, `phs_components(axis_index,pose)`, `revf_components_for_pose(pose,inputs)` 공개 인터페이스는 유지한다. `assembly_path_review(inputs)`는 A1/A2/A3의 단계별 결과를 구별하여 반환하고, 예전 A1 단독 결과를 전체 조립 확인으로 사용하지 않는다.

- [ ] 먼저 실패하는 회귀 테스트를 작성한다. 상부 프레임 기준 S=(0,250), (−216.506351,−125), (+216.506351,−125) mm에서 각 축의 두 장착 구멍은 `(Sx−22,Sy)`와 `(Sx+22,Sy)`여야 한다. 모든 구멍은 해당 640 mm 가로바의 중심선 위에 있어야 하며, 같은 자세로 변환된 상부 프레임과 브래킷의 정확 Boolean은 유효하고 양의 관통이 없어야 한다. `group_shape('upper_frame')`의 변환 전 Rev D 좌표를 변환 후 브래킷과 섞어 검사하지 않는다.
- [ ] PHS 포켓·볼·핀 중심/접선축, e=16 mm, 브래킷 장착면의 높이는 그대로 둔다. 축별 일체형 베이스 장변·두 구멍의 **배열 방향**·T너트 장변만 상부 **프레임 X 방향**으로 배치한다. 구멍·볼트·드라이버의 **중심축은 프레임 Z 방향**으로 유지하고 위치·방향 모두 플랫폼 자세를 따라 변환한다. 이 두 방향을 각각 테스트한다. 전체 브래킷을 회전해 PHS 핀축을 틀지 않는다. A1/A2/A3는 하나의 동일 SKU라고 가정하지 않는다.
- [ ] 세 브래킷이 각각 유효한 단일 연결 솔리드인지, 기존 상부 코너 연결부와 양의 관통이 없는지, 베이스–레일 연결 및 구멍 주변 재료가 단절되지 않았는지 확인한다. 단일 솔리드는 ±750 N의 강도 합격 근거가 아니므로 기존 하중 `strength_gate`를 true로 바꾸지 않는다.
- [ ] 축별로 하우징 삽입, M6 이탈방지 체결, 실제 공급 STEP eye 접근, 핀/심/스페이서/너트, 브래킷 체결볼트·T너트 및 공구 접근을 재검사한다. PHS·중앙 M6의 **프로파일 장착 전** 단계와 T너트·볼트의 **장착 후** 단계를 나누어 실제 장애물만 넣는다. T너트의 끝단 삽입 또는 검증된 회전 삽입을 명시한다. 각 단계의 어떤 Boolean이라도 invalid이면 체적이 0으로 보이더라도 `UNKNOWN`으로 둔다. 표본 경로만 검사한 경우도 `UNKNOWN`이다. M6 잠금·반전하중 포획, 핀 머리의 invalid Boolean, 연속 평활 어깨 길이와 하부 R 설치는 이번 형상 수정으로 자동 해결되지 않는다.
- [ ] 기존 단순 프레임 코드의 3030 슬롯 깊이 6.9 mm와 후보 볼트·T너트 삽입 7.5 mm의 **0.6 mm 모델 바닥 간섭**을 별도 기록한다. 이는 실제 DNF3030 간섭의 증거가 아니다. 제조사 단면/납품 형상이 확인되지 않으면 슬롯·체결력 판정은 `UNKNOWN/HOLD`; 볼트 길이를 임의로 줄이거나 프레임 원본 모델을 조용히 바꾸지 않는다.
- [ ] `python -m unittest tests.test_revf_upper_pocket_review tests.test_revf_upper_pocket_inputs tests.test_revf_upper_pocket_load_screen -v`를 통과시킨다. 독립 검수에서 각 축의 중심선, 실제 변환 좌표, 장착·조립경로, 불명값을 확인한 뒤 해당 파일만 커밋하고 푸시한다. 모든 release flag는 false다.

## Task 6 — 수정된 3축 전 자세 재감사와 단품 견적용 리뷰 STEP

**Files:** `cad/revf_upper_pocket_pose_audit.py`, `tests/test_revf_upper_pocket_pose_audit.py`, `scripts/export_revf_upper_pocket_review.py`, `outputs/profile_radial_revF_upper_pocket_review_2026-10-02/`.

**Interfaces:** Task 4의 `audit_pose`, `audit_all` 및 증거/출처 fingerprint 계약을 유지한다. 새 출력에 A1/A2/A3 **각각의 단품 브래킷 STEP**과 SHA256/단일 솔리드/파일 크기/REVIEW ONLY 메타데이터를 추가한다. 조립 STEP와 단품 견적 후보를 혼동하지 않는다.

- [ ] 수정된 장착축에 대한 실패 테스트를 먼저 작성한다. 27 대표자세의 정확 B-rep, 1859 조밀 자세와 명령/HOME 경로의 보수적 broad phase, 결정론적 bounded exact follow-up을 새 CAD 출처 해시로 재실행해야 한다. 새 형상에 예전 측정 ledger를 붙이는 재포장은 거절해야 한다.
- [ ] 실제 eye/핀/볼, 세 브래킷·프레임·장착품 및 다른 축의 부품쌍을 다시 검사한다. 브래킷 자체 관통과 잘못된 장착 중심선은 해결돼야 하며, 구형 간략 슬롯의 바닥 간섭 및 실물 공차·강도는 별도 `UNKNOWN/HOLD`로 남긴다. 샘플·broad phase를 연속 운동영역의 무간섭 증명으로 부르지 않는다.
- [ ] `python -m unittest tests.test_revf_upper_pocket_pose_audit tests.test_revf_upper_pocket_review -v`와 exporter를 실행한다. 27/1859/명령/HOME 카운트, 모든 invalid Boolean 및 전체 결과 중 유효 최악 간섭을 JSON·그림·STEP에서 일치시킨다. 네 release flag는 전부 false다.
- [ ] 세 단품 브래킷 STEP를 각각 1개 유효 솔리드, 10 MB 미만으로 내보내고 다시 불러 체적·경계상자를 비교한다. 조립용 11 MB급 STEP는 meviy 업로드 후보가 아니다. README·manifest에 단품마다 형상 방향, 출처 해시, `REVIEW ONLY / NOT APPROVED FOR FABRICATION`을 명시한다. 제작 DXF/CNC 도면은 여전히 만들지 않는다.
- [ ] 독립 검수 후 수정 CAD 결과만 커밋·푸시한다. 명목 조립이 불가능하거나 실제 상부 슬롯 증거와 모순되는 부분이 남으면 다음 견적 업로드는 보류한다. 강도·공차 미확정은 숨기지 않고 조건부 견적과 구매 릴리스를 구별한다.

## Task 7 — 국내 완성가공·기성품 조달 확인 및 Rev F BOM

**Files:** 신규 `procurement/revf_upper_pocket_purchase_evidence_2026-10-02.md`, `tests/check_revf_bom_xlsx.py`, `outputs/20261002_reve_upper_pocket_bom/2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx`. 원본 `outputs/20261002_reve_followthrough/2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx`는 보존한다.

**Interfaces:** 읽기 전용 `read_rows(path: Path) -> list[dict[str, object]]`가 새 XLSX 데이터행을 ID 기준으로 찾아 `id`, `seller`, `quantity_pieces`, `link_text`, `hyperlink_target`, `price_krw`를 반환하고, `check(path: Path) -> None`이 검사한다. 새 브래킷 행 ID는 `UP01A`, `UP01B`, `UP01C`로 각 1개이며 형상이 같다는 근거가 생기면 동일 SKU를 세 행에 재사용할 수 있다. 구매 증거 문서는 SKU마다 `판매처/정확 형번/수량/가격/납기/카드결제 확인/출처/확인일/상태`를 기록한다. 미정 견적은 숫자 가격이 아니라 문자 `견적 미확정`으로 남긴다.

- [ ] Task 6의 **단품 브래킷 STEP**가 모델 내부 자체검사에서 성립할 때만 한국미스미 meviy에 해당 축별 형상 3개로 견적을 시도한다. 자동견적 수락, 재질, 실제 수량별 단가·VAT·배송·납기·카드 장바구니 가능 여부를 증거와 함께 기록한다. 실패하면 수동견적 또는 다른 국내 완성가공업체를 확인하되 주문하지 않는다. 어떤 견적도 없으면 가격을 지어내지 않고 BOM에 `견적 미확정/발주 보류`로 표기한다.
- [ ] MSB6-35 / MSB6-LC31 중 실제 전 길이 평활 어깨·필릿·너트 적층이 성립하는 형번만 남긴다. M6 체결품, 스페이서, 정확한 T너트·볼트와 3축 총수량의 국내 카드결제·재고·납기를 확인한다. 구형 F07/F08A/B/F11/F12를 무증거로 `구매 적합`으로 승격하지 않는다. F10 M6 너트는 F21/G9EA 장착에도 쓰이므로 관절 변경만으로 전량 삭제하지 않는다.
- [ ] 신규 BOM 검증을 먼저 작성해 기존 67행 고정 검사에 묶이지 않도록 한다. 품목 ID 중복 없음, 정확한 하이퍼링크, 판매처별 연속 묶음, 포장단위↔실수량, 신규 완성 브래킷 정확히 3개, 미확정 가격은 숫자 0이 아님, 공급가·VAT·총액·400만 원 잔액이 독립 계산과 일치하는지 검증한다. 새 파일 부재일 때 실패를 확인한다.

```powershell
python tests/check_revf_bom_xlsx.py 'outputs/20261002_reve_upper_pocket_bom/2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx'
```

- [ ] 신규 검사기는 실제 BOM 행을 ID 열로 찾아야 하며 고정 `range(4,71)`로 숨겨진 신규 행을 놓쳐서는 안 된다. 필수 불변식은 다음과 같다.

```python
rows = read_rows(path)
ids = [row["id"] for row in rows]
bracket_rows = [row for row in rows if row["id"] in {"UP01A", "UP01B", "UP01C"}]
purchasable_rows = [row for row in rows if row["price_krw"] != "견적 미확정"]
unquoted_rows = [row for row in rows if row["price_krw"] == "견적 미확정"]
seller_names = [row["seller"] for row in rows]
assert len(ids) == len(set(ids))
assert sum(row["quantity_pieces"] for row in bracket_rows) == 3
assert all(row["link_text"] == row["hyperlink_target"] for row in purchasable_rows)
assert all(row["price_krw"] != 0 for row in unquoted_rows)
supplier_groups = [name for index, name in enumerate(seller_names)
                   if index == 0 or name != seller_names[index - 1]]
assert len(supplier_groups) == len(set(supplier_groups))
```

- [ ] 스프레드시트 스킬의 `workflows/edit_workflows.md`, `artifact_tool_docs/API_QUICK_START.md`, `style_guidelines.md`를 읽는다. 첫 편집 명령 직전에 해당 스킬의 `mark_artifact_operation_started.mjs --operation-kind edit --expected-output-count 1 --output-format xlsx`를 1회 실행한다. `load_workspace_dependencies` 경로의 `@oai/artifact-tool`만으로 Rev E 파일을 복제·필요 셀만 편집하고, 재계산·핵심 범위 검사·오류 스캔·변경영역 렌더 후 저장한다.
- [ ] 신규 검사와 원본 회귀검사를 모두 실행한다. 견적 미확정이면 현 3,143,564원은 **구형 후보합계**라고 밝히고 Rev F 총액은 `확정 금액+미정`으로 표시하며 최종 예산 적합을 주장하지 않는다.

```powershell
python tests/check_revf_bom_xlsx.py 'outputs/20261002_reve_upper_pocket_bom/2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx'
python tests/check_reve_bom_xlsx.py 'outputs/20261002_reve_followthrough/2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx'
```

- [ ] 가격·발주 상태와 기구 검증 결과를 교차 검토한다. `git add procurement/revf_upper_pocket_purchase_evidence_2026-10-02.md tests/check_revf_bom_xlsx.py outputs/20261002_reve_upper_pocket_bom/2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx`와 `git commit -m "Review Rev F pocket procurement and BOM"` 후 푸시한다. 실제 주문은 별도 사용자 지시가 있어도 모든 릴리스 게이트 충족 후에만 수행한다.

## Task 8 — 최신 요구사항·조립 지침·릴리스 판정 정합화

**Files:** `references/수평유지장치 요구사항.txt`의 맨 위 최신 결정 단락, `requirements/current_variant_priority_2026-10-02.md`, `requirements/hard_constraints.md`, `fabrication/profile_radial_revE_release_candidate_2026-09-04/README_CURRENT_SCOPE_2026-10-02.md`, `verification/revf_upper_pocket_release_review_2026-10-02.md`, `assembly/revf_upper_pocket_assembly_review_2026-10-02.md`.

**Interfaces:** 새 요구사항 문서는 `CURRENT_VARIANT=POWERED_3RPS_REVF_UPPER_POCKET_REVIEW`, `BRACKET_FACTORY_FINISHED_COUNT=3`, `MECHANICAL_STOP=EXCLUDED_FOR_SUPERVISED_SELF_WEIGHT_POC`와 네 릴리스 flag를 명시한다. 검증 문서는 기구·조달·전장 증거의 항목별 판정표를 제공하고, 조립 문서는 통전 전/후 절차를 구분한다.

- [ ] 이전 2026-09-17의 `스토퍼 없으면 구매 릴리스 불가` 조항과 최신 사용자 결정의 충돌을 **최신 날짜의 감독하 자중 PoC 편차**로 명시적으로 해소한다. `requirements/hard_constraints.md`와 현 제작범위 README의 오래된 절대 문구도 새 예외와 우선순위가 분명하도록 정정하되 역사 기록은 삭제하지 않는다. 무스토퍼 위험과 소프트웨어 운전창·내장 리미트·E-stop의 한계를 분리해 적고, 사람/적재/현장 안전 인증은 제외한다.
- [ ] 부품 순서와 공구 접근, 브래킷 포획, 핀/심/너트 적층, 3축 조립 확인, 배전함 플라스틱 타공 허용 범위를 설명한다. 자잠금 액추에이터를 무전원 손 스윕하라고 쓰지 않는다. 자세 이동은 별도 `MOTOR_POWER_RELEASE` 뒤 저속 단계로 둔다.
- [ ] 릴리스 매트릭스에서 `소스/하중/간섭/견적·BOM/전장·내장리미트` 각각의 관측 증거, 통과 조건, 실제 상태를 분리한다. 불명 치수·스톨하중·E-stop 차단정격·전장 검증 미완료 중 하나라도 남으면 구매·제작·통전 release는 false다. `rg -n 'PURCHASE_RELEASE|FABRICATION_RELEASE|MOTOR_POWER_RELEASE|스토퍼'`로 새 문서와 역사 문서의 우선순위가 모호하지 않은지 검토한다.
- [ ] 독립 검수자 두 명이 CAD/하중 및 BOM/전장 경계를 따로 검토하고 지적사항을 반영한다. 모든 신구 회귀시험과 출력 검사 결과를 보고서에 기록한다. 검증된 문서만 커밋·푸시한다.
- [ ] 새 문서에 다음 릴리스 블록을 정확히 보존한 뒤, 실제 증거가 모두 닫히기 전에는 어떤 이전 스크립트도 이를 `TRUE`로 쓰지 않는지 확인한다.

```text
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
CONTROL_POWER_TEST_RELEASE = FALSE
MOTOR_POWER_RELEASE = FALSE
```

- [ ] `git diff --check`와 신규·기존 회귀시험을 다시 수행한다. `git add references/수평유지장치 요구사항.txt requirements/current_variant_priority_2026-10-02.md requirements/hard_constraints.md fabrication/profile_radial_revE_release_candidate_2026-09-04/README_CURRENT_SCOPE_2026-10-02.md verification/revf_upper_pocket_release_review_2026-10-02.md assembly/revf_upper_pocket_assembly_review_2026-10-02.md` 후 `git commit -m "Record Rev F pocket review and scope gates"`와 `git push origin codex/reve-progress-backup-20261001`로 백업한다.

## Final decision rule

모든 형상·강도·조립·조달 증거가 실제로 충족되면 별도 구매 승인 제안을 할 수 있다. 어느 하나라도 실패·미확정이면 `발주 보류`와 구체적 수정 옵션을 보고한다. 실측 전 3D 모델과 자동견적만으로 `최종 조립/간섭 확인 완료` 또는 `제작 가능`이라고 표시하지 않는다.
