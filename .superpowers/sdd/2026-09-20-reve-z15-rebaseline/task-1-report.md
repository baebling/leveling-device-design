# Task 1 report — Freeze the Z+15 command-datum design basis

## Status

`DONE_WITH_CONCERNS`

## Files changed

- `design_basis/powered_reve_rebaseline_concept_2026-09-17.md`
  - Rebased the command datum to physical Z=15 mm at pitch=0°, roll=0°.
  - Defined command Z=0~50 mm as physical Z=15~65 mm, the 700×700×315 mm basic CAD envelope excluding electrical protrusions, the 221.281~289.523 mm nominal required pin-length range, and the 218~292 mm provisional software window.
  - Required recorded actual switch trip lengths before automatic operation, prohibited intentionally contacting internal limits in normal operation, and added the Z=35 mm fallback.
  - Linked the decision record and retained the existing independent-mechanical-stop release limitation.
- `requirements/current_variant_priority_2026-09-17.md`
  - Applied the same command datum, operating range, pin-length range, software window, switch-recording prerequisite, and fallback.
  - Updated HOME/commissioning wording to save both actual `L_low_switch` and `L_high_switch` before normal automatic operation.
  - Linked the decision record without changing the existing no-independent-mechanical-stop safety-deviation language.
- `verification/reve_z15_rebaseline_decision_2026-09-20.md`
  - Added the authoritative Z+15 decision table, commissioning rules, retained safety-deviation and release language, fallback, and concise not-yet-verified list.

## Verification

Command run:

```powershell
rg -n "Z=15|Z=65|221\.281|289\.523|218~292|205~305" design_basis\powered_reve_rebaseline_concept_2026-09-17.md requirements\current_variant_priority_2026-09-17.md verification\reve_z15_rebaseline_decision_2026-09-20.md
```

Output:

```text
verification\reve_z15_rebaseline_decision_2026-09-20.md:10:| 명령 원점 | pitch=0°, roll=0°에서 물리 Z=15 mm를 명령 Z=0으로 정의 |
verification\reve_z15_rebaseline_decision_2026-09-20.md:11:| 명령 매핑 | 명령 Z=0~50 mm는 물리 Z=15~65 mm에 대응 |
verification\reve_z15_rebaseline_decision_2026-09-20.md:14:| 명목 요구 핀 길이 범위 | 221.281~289.523 mm |
verification\reve_z15_rebaseline_decision_2026-09-20.md:15:| 잠정 소프트웨어 창 | 218~292 mm |
verification\reve_z15_rebaseline_decision_2026-09-20.md:16:| 기존 CAD/STEP 명목 범위 | 205~305 mm; 검증된 내장 리미트 스위치 작동점이 아님 |
verification\reve_z15_rebaseline_decision_2026-09-20.md:18:물리 Z=15 mm는 액추에이터의 물리 하한이나 내장 리미트 위치가 아니다. 물리 Z=65 mm는 명령 Z=50 mm의 수평 기준 높이이며, 현 시점에서 중앙 가이드 겹침 또는 전체 CAD로 최종 확인되지 않았다.
verification\reve_z15_rebaseline_decision_2026-09-20.md:24:- 218~292 mm 창은 잠정 소프트웨어 보호창이며, 독립 기계식 스토퍼를 대체하지 않는다.
verification\reve_z15_rebaseline_decision_2026-09-20.md:25:- 최종 중앙 가이드 겹침 또는 전체 CAD 스크리닝이 실패하면 물리 +15 mm 기준은 유지하고 명령 Z 상한만 35 mm로 제한한다. 이 경우 명령 Z=0~35 mm는 물리 Z=15~50 mm에 대응한다.
verification\reve_z15_rebaseline_decision_2026-09-20.md:34:- 물리 Z=65 mm에서 중앙 가이드 겹침
requirements\current_variant_priority_2026-09-17.md:37:| HOME | 조밀 허용 시작집합 전체에서 검증된 단일 공통순서로 세 축을 내장 하한 리미트까지 저속 원점복귀 후 물리 Z=15 mm의 명령 Z=0 운전기준점으로 상승; 실제 스위치 작동 길이 기록 전 자동운전 금지 |
requirements\current_variant_priority_2026-09-17.md:85:- 명령 Z=0: pitch=0°, roll=0°에서 물리 Z=15 mm인 운전기준점이며 액추에이터 물리 하한이 아님
requirements\current_variant_priority_2026-09-17.md:86:- 명령 Z=0~50 mm: 물리 Z=15~65 mm에 대응; pitch/roll은 동시에 ±3° 유지
requirements\current_variant_priority_2026-09-17.md:88:이 명령영역에서 명목 요구 핀 길이 범위는 221.281~289.523 mm다. `L_low_switch`와 `L_high_switch`는 각 축 내장 리미트가 실제 작동하는 핀 간 거리이며 공급자 자료와 실측으로 정한다. 205~305 mm 값은 기존 CAD/STEP의 명목 형상 범위일 뿐 검증된 내장 리미트 스위치 작동점으로 사용하지 않는다.
requirements\current_variant_priority_2026-09-17.md:90:HOME 뒤에는 물리 Z=15 mm의 명령 Z=0 기준점으로 이동한다. 축별 상승량은 실측 `L_low_switch`와 해당 기준점의 실측/검증된 핀 길이 차로 정한다. 잠정 소프트웨어 핀 길이 창은 절대길이 218~292 mm이고, HOME 상대 연장량은 축별 `[218−L_low_switch, 292−L_low_switch]`로 파생한다. 정상 운전은 내장 리미트에 의도적으로 접촉하지 않아야 하며, 자동운전 전에 시운전에서 실제 `L_low_switch`와 `L_high_switch`를 기록한다. 정확한 counts/mm, 스위치 길이, 물리 Z=15 mm의 명령 Z=0 오프셋은 실물 측정 후 저장하고 스트로크·HOME·스토퍼 검사를 다시 실행한다. 최종 가이드 겹침 또는 전체 CAD 스크리닝이 실패하면 물리 +15 mm 기준은 유지하되 명령 Z 상한을 35 mm로 제한한다. 상세 기준과 미검증 항목은 `verification/reve_z15_rebaseline_decision_2026-09-20.md`를 따른다.
requirements\current_variant_priority_2026-09-17.md:103:- HOME 시작집합은 27개 꼭짓점이 아니라 명령 `Z=0:5:50 mm`(물리 Z=15:5:65 mm), `pitch/roll=-3:0.5:+3°` 조밀 격자, 모든 허용 명령·JOG 경로 표본과 후보 HOME의 모든 중간상태다.
requirements\current_variant_priority_2026-09-17.md:117:5. 실제 `L_low_switch`, `L_high_switch`, counts/mm, 물리 Z=15 mm의 명령 Z=0 오프셋과 마지막 검증자세를 비휘발성 저장하고 이후 일반 HOME을 허용한다.
requirements\current_variant_priority_2026-09-17.md:133:- 정상 소프트웨어 창은 잠정 핀 길이 218~292 mm다. 전기 리미트 작동 길이와 공차, 그 이후 하드엔드까지의 허용 오버트래블은 공급자 서면값을 사용하며 205~305 mm 값을 리미트 작동점으로 가정하지 않는다.
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:5:승인안은 기존 `POWERED_PROFILE_RADIAL_3RPS_REVE_POC_RC1`을 최대한 재사용하는 3축 전동식 수평유지 모듈이다. 2026-09-20 Z+15 명령 기준점 결정에 따라 기본 CAD 외곽은 케이블·전장함·E-stop 및 기타 전기 돌출부를 제외하고 700×700×315 mm이며, 명령 Z 0~50 mm와 pitch/roll 동시 ±3°를 유지한다. 명령 Z=0은 pitch=0°, roll=0°에서 물리 Z=15 mm이고, 명령 Z=0~50 mm는 물리 Z=15~65 mm에 대응한다. 상세 결정과 미검증 항목은 `verification/reve_z15_rebaseline_decision_2026-09-20.md`를 기준으로 한다.
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:48:| 기존 STEP 명목 물리 핀 간 범위 | 205~305 mm, 리미트 작동점 아님 |
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:56:기존 27자세의 Z=0 기준과 현행 명령 기준을 혼동하지 않는다. 현행 명령 Z=0은 pitch=0°, roll=0°에서 물리 Z=15 mm이며, 명령 Z=0~50 mm는 물리 Z=15~65 mm에 대응한다. 이 명령영역의 명목 요구 핀 길이 범위는 221.281~289.523 mm다. 각 축의 실제 내장 하한/상한 리미트 작동 핀 길이를 `L_low_switch`, `L_high_switch`로 측정한다. 205~305 mm 값은 기존 CAD/STEP의 명목 형상 범위일 뿐이며 검증된 내장 리미트 스위치 작동점이 아니다.
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:58:잠정 소프트웨어 보호창은 절대 핀 길이 218~292 mm다. HOME 상대값은 축별 `[218−L_low_switch, 292−L_low_switch]`로 파생한다. 실제 허용 자세 명령은 명령 Z 0~50 mm(물리 Z=15~65 mm), pitch/roll ±3°의 역기구학 결과가 이 창 안에 있을 때만 실행한다. 정상 운전은 내장 리미트에 의도적으로 접촉하지 않아야 하며, 자동운전 전에 시운전에서 실제 `L_low_switch`와 `L_high_switch`를 기록해야 한다.
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:91:- 위치계층: `잠정 소프트웨어 218~292 mm → 공급자 확인 내장 리미트 작동점 → 공차 최악 최소 1 mm 후 기계 스토퍼 → 최소 2 mm 후 구조 손상/하드엔드`
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:135:상부는 3-RPS 구속을 만족하는 자세만 취할 수 있으므로, 세 길이에서 6개 플랫폼 변수 `x,y,z,pitch,roll,yaw`를 푸는 전진기구학과 각 중간 자세의 조인트 편각·간섭검사가 구매 전 필수다. HOME 시작집합은 명령 `Z=0:5:50 mm`(물리 Z=15:5:65 mm), `pitch/roll=-3:0.5:+3°` 조밀 격자, 모든 허용 명령·JOG 경로 표본과 후보 HOME 중간상태 전체다.
design_basis\powered_reve_rebaseline_concept_2026-09-17.md:141:최초 조립은 별도 `COMMISSIONING_HOME`으로 처리한다. 전원 차단·블록 지지 상태에서 세 핀 길이를 ±1 mm로 실측해 감사 시작상태임을 확인한 뒤, 모터전원 릴리스 후 한 축씩 10 mm 자유구간을 전류제한 JOG하여 `HOME_PWM`과 `I_home_run`을 교정한다. 각 축 하한 리미트·2 mm 탈출·2회 재접근을 확인한 뒤 공통 HOME을 실행하고 실제 `L_low_switch`, `L_high_switch`, counts/mm, 물리 Z=15 mm의 명령 Z=0 오프셋과 마지막 자세를 비휘발성 저장한다. 이 기록 전에는 자동운전을 허용하지 않는다.
```

`git diff --check` also completed without whitespace errors.

## Concerns

- Actual `L_low_switch` and `L_high_switch` remain unmeasured.
- Central-guide overlap at physical Z=65 mm, physical cable clearance, and all real-world commissioning results remain unverified.
- The existing no-independent-mechanical-stop safety deviation remains unresolved and continues to block purchase and fabrication release.
