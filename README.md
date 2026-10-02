# 수평유지 상부모듈 — 전동 Rev E 현행 검증

> **현행 상태 (2026-10-02): 전동 LM4075OE 3축·자동수평 Rev E, 발주·제작·통전·시연 수락 모두 보류.** 대상은 카트·적재물·사람 없는 공개형 자중 시연 상부모듈이다. 목표는 Z 0~50 mm와 pitch/roll ±3°다. 기존 27자세 CAD에는 실제 상부 체결품이 빠져 있었고, 별도 후보 CAD에 볼트·너트 외피를 넣어 다시 검사했지만 하부 핀 동봉·상부 눈 접촉·프로파일 단면 불일치·스토퍼·움직이는 케이블이 열려 있어 최종 조립 합격이 아니다. 액추에이터 아이 홀도 판매도면 Ø6.4와 STEP Ø6.0이 불일치한다. 허용 금속 가공은 기존 A1~A3 판의 구멍/탭뿐이고 플라스틱 전장함/속판 타공은 가능하다. [현행 요구사항](references/수평유지장치%20요구사항.txt)과 [검증·발주 보류 사유](outputs/20261002_reve_followthrough/연속검증_중간기록.md)를 먼저 읽는다.

> **현행 검토본:** [핀축 보정 CAD/STEP](outputs/profile_radial_revE_pin_axis_corrected_2026-10-02/README_NOT_FOR_FABRICATION.md), [상부 관절 기성품 후보 CAD/STEP](outputs/20261002_reve_joint_candidates/README_REVIEW_ONLY.md), [공급처별 검수 BOM](outputs/20261002_reve_followthrough/2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx), [전장함 2D 배치 가설](outputs/20261002_reve_followthrough/5070P_2D_배치_검토전용.svg). BOM을 덮던 빈 상자는 제거했지만 VAT 포함 3,143,564원은 미확정 교체품·배송비를 제외한 **검수용 산술**이지 주문 가능 총액이 아니다. 상부 F07/F11 체결 불합격, Ø6 편심핀 강도, 추가 금속가공 없는 독립 스토퍼와 전장 실물 배치가 열려 있다. `PURCHASE_RELEASE=FALSE`, `FABRICATION_RELEASE=FALSE`, `CONTROL_POWER_TEST_RELEASE=FALSE`, `MOTOR_POWER_RELEASE=FALSE`, `POC_ACCEPTANCE=FALSE`.

> **10월 2일 독립 재검수 주의:** 포스트 스토퍼 3곳은 기존 하부 4040 프로파일과 받침 면적이 모두 0이고, 기존 보고서의 8~11 mm 여유 수치는 좌표계 재계산으로 철회했다. 새 하부 횡보 4080 후보도 기존 하부판·액추에이터와 간섭한다. 상부 슬롯 체결에 얇은 심을 더하는 후보 역시 하중 전달이 검증되지 않았다. 따라서 국내 장바구니에 보이는 기성품만 추가해 이 설계를 바로 조립할 수 있다고 판단하지 않는다. [수정 검증 기록](outputs/20261002_reve_followthrough/연속검증_중간기록.md)을 따른다.

## 아래는 과거 결정의 이력 — 현행 주문·조립 기준 아님

> **2026-09-08 현행 범위:** [상부 패널 없는 공개형 프로파일 시연](requirements/current_open_frame_demo_scope_2026-09-08.md). 카트·적재물·사람, 별도 과조절 스토퍼/전용 받침, 전용 시험대 고정품은 구매하지 않는다. 남은 구매 전 작업은 활성20행 재검산과 최종 견적이다.

> **진행상황 기록:** [2026-09-07 M2R2-S220 현재 상태](logs/current_progress_2026-09-07.md)

> **현행 실행 우선순위:** [2026-09-07 수동 M2R2-S220 1순위 및 구매 전 게이트](requirements/current_variant_priority_2026-09-07.md). 전동 Rev E는 향후 참고안이며 현재 주문 기준이 아니다.

> **현행 시연 범위:** 카트·적재물 없는 자중 전용 감독하 시연. [구매 전 점검 결과와 열린 항목](verification/m2r2s220_no_cart_pre_purchase_audit_2026-09-07.md)

> **이전 한 축 상세 M2R2F2는 조립 방법 참고용 이력이다.** [3D 조립/분해 STEP과 렌더](outputs/manual_m2r2f2_one_axis/README.md), [확인 치수와 남은 가정](design_basis/manual_m2r2f2_one_axis_assembly_2026-09-05.md). 해당 모델의 MCL-12-F 칼라는 현행 M2R2-S220에서 SCSJ12-6으로 대체됐다.

> **현재 최신은 개념 승인 후 만든 M2R2-S220 장바구니 부품 CAD다.** [CAD 패키지 설명](outputs/manual_turnbuckle_rev_m2r2s220/README.md), [설계·자유도 검토](design_basis/manual_m2r2_cart_dof_assessment_2026-09-06.md). 하부 관절만 기존 4080 슬롯 안쪽으로 옮겨 중립 높이299.2 mm와 ±3° 길이 여유5.42 mm를 확보했다. 부품 간섭과 M5/M8 공구축 및 STEP 재읽기는 통과했지만, 독립 기계식 스톱·실제 카트 래치·STB 압축 정격 때문에 구매/제작 릴리스는 아직 아니다.

> **최신 검토 CAD는 M2R2 기성 연결부형이다.** 후속 요청에 따라 프로파일 길이 절단만 허용하고 맞춤 평판·부시·추가 구멍 가공을 없애는 조립안으로 변경했다. [최신 CAD 안내](outputs/manual_turnbuckle_rev_m2r2/README.md), [부품 후보·절단표·조립 순서](design_basis/manual_revm2r2_stock_connections_2026-09-05.md). 앞1/뒤2 직교 3-RPS, 검토 외곽700×700×344 mm. 아래 M2R1 및 120° 유지 방침은 이전 이력이다. 구매·제작·실물 하중 검증은 완료되지 않았다.

> **현재 CAD: Rev M2R1 (2026-09-05).** 사용자 CAD 진행 요청에 따라 기존 Rev M2 상부 연결부를 수정했다. [CAD 패키지 안내](outputs/manual_turnbuckle_rev_m2r1/README.md), [중립 STEP](outputs/manual_turnbuckle_rev_m2r1/step/M2R1_NEUTRAL_REVIEW.step), [전체 ZIP](output/Manual_3RPS_RevM2R1_CAD_Review_2026-09-05.zip). 112개 구성요소, 9자세 부품 간 간섭 0건, 5개 STEP 재수입 통과. 부시/구면 형상/핀 적층은 공칭 가정이며 제작·구매 미승인이다.

- **외관·조립 개선:** [표준 표면과 축 표시, 동일 링크 키트 3개](design_basis/manual_revm2_appearance_assembly_2026-09-05.md). 형상 재설계 대신 조립 표준화와 구조 가시성을 개선하는 개념이며 제작 승인 전이다.

> **2026-09-05 최종 사용자 결정:** 설명력과 기존 검증자료 활용을 고려해 턴버클형 Rev M2를 다시 1순위로 정했다. 경첩형 M3는 비교안으로 보관한다. 구조를 새로 단순화하기보다 좌나사품·상부 부시/핀·압축 사용 확인과 조달 묶음에 집중한다. 아래 같은 날짜의 M3 우선 결정은 대체된 이력이다.

- [최신 우선순위](requirements/current_turnbuckle_priority_2026-09-05.md)
- [최소 완성 방안 및 기존 검증 재감사](design_basis/manual_revm2_minimal_completion_2026-09-05.md)
- [조달 묶음](procurement/manual_revm2_procurement_groups_2026-09-05.md) / [공급처·담당자 문의 초안](procurement/manual_revm2_supplier_inquiry_drafts_2026-09-05.md)
- 기존 상부 부시의 실제 형상/공차는 검증되지 않았다. 구매·제작 미승인, 문의 미발송.

## 아래는 같은 날 앞서 검토한 M3 이력

> **2026-09-05 최신 결정:** 빠른 마무리·낮은 작업부담·재료 중심 조달을 위해 기계식을 1순위로 변경했다. 기존 구조를 유지할 의무는 없다. 새 우선 개념은 직교 경첩 2축과 조절나사 2개의 수동 수평조절·고정 구조다. 독립 상승/자동보정은 이번 실행 가정에서 제외한다. Rev E와 Rev M2는 보관안이며 아래의 이전 우선순위/BOM은 현재 주문 기준이 아니다.

- 최신 범위: [수동 우선순위](requirements/current_manual_priority_2026-09-05.md)
- 새 구조·예비계산·미해결사항: [M3 개념설계](concepts/manual_crossed_hinge_m3_2026-09-05.md)
- 상판 중심은 기울기에 따라 종속 이동한다. 절대 X/Y 고정이 필수이면 이 개념을 다시 검토한다.
- 현재 개념검토 단계이며 상세 CAD·구매·제작·실물검증은 미완료/미승인이다. 비용분류 및 축소 성과 인정도 확인 전이다.

## 아래는 2026-09-04 이전 전동식/수동식 작업 이력

> **2026-09-04 최신 상태:** Rev E의 제작도·전장함 배치·회로/배선·Mega2560 펌웨어·후보 BOM·시험절차를 release candidate로 구현했다. 27자세 OpenCascade 3회, 기존 Fusion 간섭 3회/단면 3회, Mega2560 실제 컴파일, 전체 226개 회귀시험과 RC1 전용시험 10개가 통과했다. 공급자/실물 검증이 남아 구매·제작·통전 승인은 아직 false다.

최신 자료:

- 실행 기준: [`requirements/current_variant_priority_2026-09-04.md`](requirements/current_variant_priority_2026-09-04.md)
- 디지털 감사: [`verification/RevE_PoC_release_candidate_audit_2026-09-04.md`](verification/RevE_PoC_release_candidate_audit_2026-09-04.md)
- 제작자료: [`fabrication/profile_radial_revE_release_candidate_2026-09-04`](fabrication/profile_radial_revE_release_candidate_2026-09-04)
- 전장·공급자·후보 BOM: [`outputs/profile_radial_revE_poc_release_candidate`](outputs/profile_radial_revE_poc_release_candidate)
- 타 PC 전달 ZIP: [`output/Profile_Radial_3RPS_RevE_PoC_RC1_2026-09-04.zip`](output/Profile_Radial_3RPS_RevE_PoC_RC1_2026-09-04.zip)
- 펌웨어: [`firmware/reve_leveling_controller`](firmware/reve_leveling_controller)
- 시험절차: [`verification/RevE_PoC_test_protocol_2026-09-04.md`](verification/RevE_PoC_test_protocol_2026-09-04.md)
- 수행 및 시행착오: [`logs/reve_poc_implementation_2026-09-04.md`](logs/reve_poc_implementation_2026-09-04.md)

> **2026-09-02 최신 상태:** `LM4075OE-1075 x3 + MDD10A x2 + Mega2560 + MPU6050` 전동 자동수평 Rev E의 CAD 단계를 완료했다. 실제 액추에이터 STEP를 넣은 Fusion 단일 조립체, 27자세 해석, OpenCascade 검사와 Fusion 간섭검사 3회가 통과했다. 수동 턴버클 Rev M2는 우선순위 2 백업안이며 두 안 모두 주문·제작 승인은 아직 false다.

```text
PRIORITY_1 = POWERED_PROFILE_RADIAL_3RPS_REVE_ACTUAL_VENDOR
PRIORITY_2 = MANUAL_TURNBUCKLE_3RPS_REV_M2_BACKUP
TARGET_POWERED_Z = 0-50 mm
TARGET_PITCH_ROLL = +/-3 deg
CAD_STAGE = COMPLETE
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
COMMISSIONING_RELEASE = FALSE
```

우선순위 1에서 먼저 읽을 파일:

- 최신 우선순위: [`requirements/current_variant_priority_2026-09-02.md`](requirements/current_variant_priority_2026-09-02.md)
- 전동 제어 기준: [`design_basis/priority1_powered_control_architecture_2026-09-02.md`](design_basis/priority1_powered_control_architecture_2026-09-02.md)
- Rev E CAD·반복검증: [`design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md`](design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md)
- 60행 국내 구매형 BOM: [`procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv`](procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv), [`설명서`](procurement/profile_radial_reve_domestic_master_bom_2026-09-02.md)
- 검토용 Excel BOM: [`outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Domestic_BOM_2026-09-02.xlsx`](outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Domestic_BOM_2026-09-02.xlsx)
- Fusion 단일 조립체: [`outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`](outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d)
- STEP·렌더·검증 패키지: [`outputs/profile_radial_revE_actual_vendor`](outputs/profile_radial_revE_actual_vendor)
- 국내 제어부 조사: [`web_research/domestic_electronics_research_log_2026-09-02.md`](web_research/domestic_electronics_research_log_2026-09-02.md)
- 타 PC 전달 패키지: [`output/Profile_Radial_3RPS_RevE_CAD_Package_2026-09-02.zip`](output/Profile_Radial_3RPS_RevE_CAD_Package_2026-09-02.zip), [`SHA-256`](output/Profile_Radial_3RPS_RevE_CAD_Package_2026-09-02.zip.sha256)

우선순위 2 수동 백업안:

- 설계 기준: [`design_basis/manual_turnbuckle_rev_m2_2026-09-02.md`](design_basis/manual_turnbuckle_rev_m2_2026-09-02.md)
- BOM: [`procurement/manual_turnbuckle_rev_m2_bom_2026-09-02.md`](procurement/manual_turnbuckle_rev_m2_bom_2026-09-02.md)
- CAD/검증 결과: [`outputs/manual_turnbuckle_rev_m2`](outputs/manual_turnbuckle_rev_m2)
- 자립성 감사: [`outputs/manual_turnbuckle_rev_m2/Manual_3RPS_RevM2_self_standing_verification.json`](outputs/manual_turnbuckle_rev_m2/Manual_3RPS_RevM2_self_standing_verification.json)
- 최신 타 PC 전달 패키지: [`output/Manual_3RPS_RevM2_CadQuery_Package_v2_2026-09-02.zip`](output/Manual_3RPS_RevM2_CadQuery_Package_v2_2026-09-02.zip)
- 재생성: `powershell -ExecutionPolicy Bypass -File scripts/run_manual_turnbuckle_rev_m2.ps1`

> **2026-09-01 과거 결정:** 전동 액추에이터·IMU·모터제어·전원장치를 제외하고 수동식으로 전환했으나, 이 결정은 2026-09-02의 우선순위 변경으로 대체됐다. 아래 내용은 수동 백업안의 이력이다.

현재 상태:

```text
BACKUP_VARIANT = MANUAL_ADJUSTABLE_3RPS_HISTORY
POWERED_VARIANT = PRIORITY_1_REACTIVATED
TARGET_MANUAL_Z = 0-50 mm provisional
TARGET_PITCH_ROLL = +/-3 deg
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
```

현재 먼저 읽을 파일:

- 수동 요구사항: [`requirements/current_manual_scope_2026-09-01.md`](requirements/current_manual_scope_2026-09-01.md)
- 수동 설계 기준: [`design_basis/manual_adjustable_3rps_baseline_2026-09-01.md`](design_basis/manual_adjustable_3rps_baseline_2026-09-01.md)
- 전동안 보관 기록: [`design_basis/archived_powered_control_architecture_2026-09-01.md`](design_basis/archived_powered_control_architecture_2026-09-01.md)
- BOM 변경표: [`procurement/manual_3rps_bom_delta_2026-09-01.csv`](procurement/manual_3rps_bom_delta_2026-09-01.csv)
- 인수인계: [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md)

수동안은 기존 Rev D의 700 x 700 mm 프로파일 프레임, 250 mm 지지 반경과 90/210/330 deg 지지점은 재사용 후보로 유지한다. 27자세 이상모델의 요구 핀 중심 길이는 212.137-297.864 mm이며, 새 수동 지지대의 예비 설계 포락체는 205-305 mm다. 정확한 스크루·너트·조인트·잠금장치를 선정하고 Fusion 조립체를 다시 검사하기 전에는 주문하거나 제작하지 않는다.

## 보관된 전동안 - 프로파일 방사형 3-RPS Rev D

> **보관 시점 최종 갱신:** Rev D 기술 BOM을 62개 고유 행으로 평탄화했다. 가격 확인분은 VAT 포함 화면가 1,589,208원이고, 이 중 나비엠알오 45행 소계는 1,085,370원이다. 별도 견적이 필요한 A6061 가공품은 9행이며 Fusion 조립체는 루트 전체 간섭 0건과 회귀검사 18개를 유지한다.

> **전동안 보관 판정:** 아래 기술 BOM은 현재 `ARCHIVED_DO_NOT_ORDER`다. 당시에도 액추에이터 정확 옵션/배선자료, LMB-10 핀 포함품, 가공 견적과 최종 결제총액이 닫히지 않아 `purchase_release=false`, `fabrication_release=false`였다.

전동안 보관 파일:

- Fusion 원본: [`outputs/profile_radial_revD_fusion_native/Profile_Radial_3RPS_RevD_NATIVE.f3d`](outputs/profile_radial_revD_fusion_native/Profile_Radial_3RPS_RevD_NATIVE.f3d)
- 최종 통합 BOM: [`outputs/bom/Profile_Radial_3RPS_RevD_Final_BOM_2026-09-01.xlsx`](outputs/bom/Profile_Radial_3RPS_RevD_Final_BOM_2026-09-01.xlsx), [`CSV`](procurement/profile_radial_revd_final_master_bom_2026-09-01.csv), [`설명서`](procurement/profile_radial_revd_final_master_bom_2026-09-01.md)
- Rev D 설계·조립 기준: [`design_basis/profile_radial_revD_fusion_native_2026-08-31.md`](design_basis/profile_radial_revD_fusion_native_2026-08-31.md)
- Rev D 구조·체결 BOM: [`procurement/profile_radial_revD_structural_bom_2026-08-31.md`](procurement/profile_radial_revD_structural_bom_2026-08-31.md)
- Rev D 최신 분할 구매안: [`procurement/profile_radial_revd_split_source_purchase_plan_2026-09-01.md`](procurement/profile_radial_revd_split_source_purchase_plan_2026-09-01.md), [`주문 그룹 CSV`](procurement/profile_radial_revd_split_source_order_groups_2026-09-01.csv)
- Rev D 발주표 재감사: [`procurement/profile_radial_revd_order_readiness_audit_2026-09-01.md`](procurement/profile_radial_revd_order_readiness_audit_2026-09-01.md)
- Rev D 나비엠알오 실상품 후보 BOM: [`procurement/profile_radial_revd_navimro_candidate_bom_2026-09-01.md`](procurement/profile_radial_revd_navimro_candidate_bom_2026-09-01.md), [`CSV`](procurement/profile_radial_revd_navimro_candidate_bom_2026-09-01.csv)
- 과거 일괄 발주 준비도: [`procurement/profile_radial_revd_single_order_readiness_2026-09-01.md`](procurement/profile_radial_revd_single_order_readiness_2026-09-01.md)
- ISO 검토 이미지: [`outputs/profile_radial_revD_fusion_native/Profile_Radial_3RPS_RevD_Fusion.png`](outputs/profile_radial_revD_fusion_native/Profile_Radial_3RPS_RevD_Fusion.png)
- 가공 DXF/좌표표: [`outputs/profile_radial_revD_fusion_native/fabrication`](outputs/profile_radial_revD_fusion_native/fabrication)
- 기존 Rev C와 그 이전 자료는 비교·시행착오 기록이며 현재 주문 기준이 아니다.

> **2026-08-31 이전 상태(Rev C):** Rev B 기각 후 실제 120 deg 방사형 3-RPS를 복구했던 단계다. 수동 전환 직전 전동안에서는 이 구조의 중앙 허브판까지 제거한 Rev D가 마지막 기준이었다.

이 저장소는 기존 자재운반 카트와 하부 이동체 사이에 설치하는 독립형 수평유지·리프팅 상부모듈 및 기계식 카트 결합 인터페이스의 PoC 개념설계 자료이다.

## 2026-09-01 보관된 전동안의 마지막 방향

수동 전환 직전까지 과거 중앙 카단, 잘못 조립된 Rev B, 중앙 허브판을 사용한 Rev C는 **역사/비교 자료**로 보관했고, 전동안의 마지막 기준은 허브판 없는 프로파일 방사형 Rev D였다.

- 목표 구조: 하부 회전힌지(R) + 엔코더 액추에이터(P) + 상부 구면 로드엔드(S) × 3
- 허용 자유도: Z, pitch, roll
- 기구 구속: 세 하부 R축 평면 구속으로 X, Y, yaw가 종속되며, 27자세 해석에서 최대 보정량은 X 0.342 mm, Y 0.171 mm, yaw 0.079 deg다.
- 현재 Fusion 360 검토 패키지: [`output/Profile_Radial_3RPS_RevD_Fusion360_Native.zip`](output/Profile_Radial_3RPS_RevD_Fusion360_Native.zip)
- Rev D 설계 기준: [`design_basis/profile_radial_revD_fusion_native_2026-08-31.md`](design_basis/profile_radial_revD_fusion_native_2026-08-31.md)
- Rev D 구조 BOM: [`procurement/profile_radial_revD_structural_bom_2026-08-31.md`](procurement/profile_radial_revD_structural_bom_2026-08-31.md)
- 로컬 어댑터·스톱 가공자료: [`outputs/profile_radial_revD_fusion_native/fabrication`](outputs/profile_radial_revD_fusion_native/fabrication)
- Rev B 기각 재감사: [`design_basis/revB_assembly_reaudit_2026-08-31.md`](design_basis/revB_assembly_reaudit_2026-08-31.md)
- 유지 검토 후보: LM4075OE-1075 24 V/100 mm/5 V encoder, DMD-150 ×3, Arduino Mega 2560, WT901C
- 목표 운동: Z 0~50 mm, pitch/roll 각각 ±3°; Rev D 요구 핀 길이 218.958~279.846 mm
- Rev D 포락체: 접힘 상태 700×700×300 mm, Fusion 네이티브 컴포넌트 138개
- Rev D 절단표: 하부 4040 700×2/620×4, 상부 3030 700×2/640×4
- 디지털 검증: 방위각 90/210/330 deg, PHS 최대 굴절 4.096 deg, STEP 289 solids, Fusion 전체 간섭 0건, 독립 감사 교차 0 mm3
- 제작 게이트: LM4075OE 아이 폭·공급 STEP, LMB 핀/리테이너, 상부 심·숄더볼트, 스톱 정확 SKU, A1 어댑터+스톱 1차품과 한 축 실조립

아래의 과거 Phase 2, 중앙 카단, Firgelli/DIHOOL, NAVIMRO Rev D/E와 프로파일 Rev A/B/C 자료는 최신 구매지시가 아니다. Rev D의 노란 LM4075OE 외피, 파란 로컬 어댑터와 빨간 스톱도 공급자 자료·실물시험 전까지 제작 승인값은 아니다.

2026-08-24부터 기존 예비 CAD를 Phase 0 웹 조사 기반 파라미터 선정 단계로 되돌려 외부 피드백과 사용자 요구를 다시 반영했다. 2026-08-25에는 **10 kg 가반하중, 약 10 kg 빈 카트, 연결 전 장치 높이 250~300 mm, Pitch/Roll ±3°, 쉬운 가공·제작·조립 우선, 알루미늄 프로파일 카트 리시버**를 기준으로 확정했고, 2026-08-26 사용자가 정확히 **`APPROVE CONCEPT`**를 입력해 Phase 2 상세 CAD 진행을 승인했다. 이후 첫 중앙 짐벌/스톱 카트리지안이 지나치게 복잡하다는 사용자 피드백을 받아 당시 CAD를 세 액추에이터가 120° 방사형 주 구조를 이루는 `RADIAL_3_CLEAN`으로 바꿨다. 2026-08-27에는 움직이지 않는 감독하 저속 시험대 조건에 맞춰 외부 D4N/캠 패키지를 보관안으로 내리고 `LS-01M_STATIC_BENCH_MINIMAL`과 공장 아이 중심의 `JNT-CG-01` 목업 시드를 추가했다.

> 모든 Phase 2 산출물은 `PRELIMINARY — NOT APPROVED FOR FABRICATION` 상태이며 사람 운송용이 아니다.

## 이어받기 문서

다른 컴퓨터에서 이어서 작업할 때는 먼저 아래 파일을 읽는다.

- `PROJECT_HANDOFF.md`: 현재 상태, Phase 게이트, 기존 진행 흐름, 시행착오, 다음 작업
- `design_basis/minimal_radial_revC_2026-08-31.md`: 현재 120 deg 방사형 구조, 운동학, 체결축, 검증과 남은 불확실성
- `outputs/minimal_radial_revC/FUSION360_IMPORT_AND_ASSEMBLY_GUIDE.md`: Rev C Fusion 360 파일 선택과 실제 조립 순서
- `procurement/minimal_radial_revC_structural_bom_2026-08-31.md`: 현재 프로파일·허브판·브래킷·체결품 수량과 발주 게이트
- `design_basis/phase2_cad_baseline_2026-08-26.md`: 첫 상세 CAD의 보관 기록; 대형 중앙안은 현재 비선호
- `design_basis/radial_3_clean_baseline_2026-08-26.md`: 사용자 디자인 피드백 후 채택한 활성 방사형 3액추에이터 기준
- `outputs/reports/phase2_cad_update_summary.md`: 이번 CAD 갱신 결과 요약
- `outputs/reports/phase2_review_render_pack.md`: 상판 제거 내부도, 정·측·평면도, 분해도 및 번호 조립도 안내
- `design_basis/static_bench_minimal_variant_2026-08-27.md`: 정지형 저속 시험대 최소 구성과 삭제/유지 범위
- `design_basis/actuator_limit_package_cad_2026-08-27.md`: LS-01M 쌍봉식 기계 스톱 상세 CAD 기준
- `design_basis/factory_clevis_gimbal_seed_2026-08-27.md`: JNT-CG-01 공장 아이 중첩 짐벌 목업 시드
- `outputs/phase2/actuator_limit_package_summary.md`: LS-01 위치·정적 스크리닝·미해결 검증 요약
- `design_basis/user_confirmed_scope_2026-08-25.md`: 10 kg 적재/10 kg 카트/250~300 mm/±3°/쉬운 제작 우선 사용자 확인 기준
- `design_basis/cart_profile_receiver_concept_2026-08-25.md`: 알루미늄 프로파일 기반 카트 리시버 예비 개념
- `design_basis/cart_profile_receiver_layout_screen.md`: CR-01 알루미늄 프로파일 리시버 배치/질량/하중 스크리닝
- `design_basis/cart_receiver_hardpoint_screen.md`: CR-01-H1 locator/rest pad/latch keeper 하드포인트 스크리닝
- `design_basis/cart_receiver_connector_topology_screen.md`: CR-01-H2 슬롯너트/백킹플레이트/포지티브 스토퍼 토폴로지 스크리닝
- `design_basis/cart_receiver_connector_detail_screen.md`: CR-01-H3 하드포인트별 연결 스택/서비스 접근성 스크리닝
- `design_basis/cart_receiver_hardware_selection_screen.md`: CR-01-H4 조립·목업용 하드웨어 시드 스크리닝
- `outputs/reports/phase0_summary.md`: Phase 0 웹 조사 기반 파라미터 선정 요약
- `outputs/reports/final_candidate_parameter_pack.md`: 승인된 개념과 남은 증거를 정리한 파라미터 팩 v1.2
- `outputs/reports/cart_profile_receiver_summary.md`: 카트 리시버 CR-01 요약
- `outputs/reports/cart_receiver_hardpoint_summary.md`: 카트 리시버 CR-01-H1 하드포인트 요약
- `outputs/reports/cart_receiver_connector_summary.md`: 카트 리시버 CR-01-H2 연결/스토퍼 요약
- `outputs/reports/cart_receiver_connector_detail_summary.md`: 카트 리시버 CR-01-H3 연결 스택/접근성 요약
- `outputs/reports/cart_receiver_hardware_selection_summary.md`: 카트 리시버 CR-01-H4 하드웨어 시드 요약
- `design_basis/design_basis_report.md`: 설계 변수 선정 근거 보고서
- `design_basis/guide_mobility_review.md`: 중앙 가이드/조인트 자유도 검토
- `design_basis/joint_candidate_screen.md`: 액추에이터 조인트/중앙 카단 후보 스크리닝
- `design_basis/joint_detail_screen.md`: 조인트 브래킷 하중경로 및 중앙 yaw 토크 스크리닝
- `design_basis/actuator_bracket_package_screen.md`: JNT-BR-01 HRT8E형 이중전단 브래킷 시드 스크리닝
- `design_basis/actuator_joint_detail_cad_2026-08-27.md`: 공식 HRT8E 외형을 반영한 18 mm 요크/부싱/핀 유지장치 상세 CAD 기준
- `design_basis/central_yaw_path_comparison.md`: 중앙 yaw 토크 경로 후보 비교
- `design_basis/yaw_a_architecture_definition.md`: YAW-A 선호 구조의 후보 파라미터 정의
- `design_basis/yaw_a_gimbal_kinematic_definition.md`: YAW-A 두 축 요크의 축 순서, yaw 구속, 각도 스토퍼 정의
- `design_basis/combined_workspace_operating_window.md`: WS-01-H20 통합 작업영역/가이드 후보
- `design_basis/travel_limit_and_stop_strategy.md`: 전기 리미트와 기계식 스토퍼의 분리 전략
- `design_basis/pre_cad_verification_plan.md`: CAD 전 물리 목업/측정 통과 기준
- `outputs/reports/guide_mobility_summary.md`: 중앙 가이드 모빌리티 분석 요약
- `outputs/reports/joint_candidate_summary.md`: 조인트 후보 스크리닝 요약
- `outputs/reports/joint_detail_summary.md`: 조인트 상세 스크리닝 요약
- `outputs/reports/actuator_bracket_package_summary.md`: JNT-BR-01 액추에이터 브래킷 요약
- `outputs/reports/central_yaw_path_summary.md`: 중앙 yaw 경로 비교 요약
- `outputs/reports/yaw_a_architecture_summary.md`: YAW-A 후보 파라미터 요약
- `outputs/reports/yaw_a_gimbal_kinematic_summary.md`: YAW-A 축 순서/스토퍼 요약
- `outputs/reports/combined_workspace_operating_window_summary.md`: WS-01-H20 작업영역 요약
- `outputs/reports/travel_limit_and_stop_summary.md`: 리미트/스토퍼 요약
- `web_research/joint_sources.md`: 조인트/카단 후보 출처 메모
- `logs/feedback_recheck_2026-08-24.md`: 외부 피드백 반영 및 재점검 기록
- `logs/work_history.md`: 작업 이력과 시행착오 로그
- `logs/environment_setup.md`: 이 PC에서 수행한 환경 설정 기록

현재 승인 상태:

```text
APPROVE CONCEPT RECEIVED 2026-08-26
REV B REJECTED AFTER ASSEMBLY AXIS REAUDIT
REV C TRUE 120-DEG RADIAL DIGITAL CORE CHECKS PASSED
DIGITAL_CORE_ASSEMBLY_PASS_EYE_WIDTH_AND_STOP_MOUNT_OPEN
FABRICATION_RELEASE FALSE
PURCHASE_RELEASE FALSE
NOT APPROVED FOR FABRICATION
```

상세 CAD 진행은 승인됐지만 제작 릴리스는 승인되지 않았다. 첫 제작은 실측값을 반영한 조인트 1개와 액추에이터 카세트 1개 목업으로 제한한다. 무간섭·기계 스톱·질량·전원 기능을 확인하기 전에는 나머지 5개 조인트와 2개 카세트를 복제하지 않는다.

## 권장 개념

- 중심 반경 91 mm에서 상부 반경 400 mm로 펼쳐지는 3점 방사형 사선 액추에이터 개념
- 세 사선 액추에이터는 120° 방사형으로 동일 배치하며 승강과 Pitch/Roll을 직접 만든다.
- 중앙 키드 텔레스코픽 슬라이드 + 컴팩트 카단은 X/Y/Yaw 구속만 담당하며, 상판 중앙 개구나 대형 브리지를 사용하지 않는다.
- 직렬 HRT8E 어댑터는 양단 길이 증가 때문에 현재 319 mm 수축 길이를 만족하지 못해 활성안에서 제외하고 보관 후보로 둔다.
- 활성 조인트 시드는 `JNT-CG-01`: 액추에이터 공장 M8 핀을 한 축으로 쓰고, 내부 크래들의 대향 M8 트러니언으로 직교축을 만드는 영점 오프셋 중첩 짐벌이다.
- JNT-BR-01 상세 시드: 공식 HRT8E 8/23/11 mm 외형, 5.29 kN 축방향 정적값, ball center를 지나는 8 mm 이중전단 핀/러그, 18 mm 지지간격, 교체형 부싱과 핀 유지장치 포락체; 실제 14° 무간섭 목업 통과가 유지 조건
- 조인트 브래킷은 하중선을 볼 중심에 맞춰야 하며, 나사부 외팔보 지지는 현재 스크리닝에서 설계 차단점
- 작은 카탈로그 U-joint는 여전히 주 yaw 구속 경로로 쓰기보다 YAW-A keyed guide 구조 안에서 보조/형상 참고로만 검토
- 중앙 yaw 토크 경로의 원리는 유지하되, 활성 형상은 120 mm 이내 컴팩트 카단으로 축소하고 세 액추에이터를 설계의 주 구조로 둔다.
- YAW-A 후보값: 8° 설계 포락선, 10° 총 기울기 포락선, 하부 +Y pitch/상부 local +X roll 축 순서, 각 축 +/-7° 물리 스토퍼, yaw clearance 0.2 mm target/0.3 mm max
- WS-01-H20 후보: 270 mm 접힘, 100 mm 리프트, 195/220 mm guide, +/-3° 전 구간에서 11.13 mm 이상 actuator soft reserve 및 88 mm 이상 guide overlap
- 승인된 개념과 남은 검증 항목은 최종 후보 파라미터 팩 v1.2 `outputs/reports/final_candidate_parameter_pack.md`에 정리됨
- 허용 자유도: Z, Pitch, Roll
- 구속 자유도: X, Y, Yaw
- 사용자 확인 1차 PoC 목표: 적재물 10 kg, 빈 카트 약 10 kg, 연결 전 장치 높이 250~300 mm, Pitch/Roll 각각 ±3°, 쉬운 제작/조립 우선
- 목표 리프트: WS-01-H20 기준 100 mm와 ±3° 조합은 계산상 통과했지만, 실제 actuator/guide/stop 목업 증거 전에는 보장으로 주장하지 않음
- 상부 하이브리드 구조 후보: HFS8-4040 알루미늄 프레임 + 15 mm 주조 아크릴 상판 + 금속 하중분산판
- 카트 리시버 방향: CR-01 2-레일 알루미늄 프로파일 키트 + CR-01-H1 위치결정핀/받침/래치용 국부 금속 하드포인트 + CR-01-H2 슬롯 체결/포지티브 스토퍼 토폴로지
- CR-01-H2 선호안: 슬롯너트와 M8급 체결은 mock-up 조정/클램프용으로 쓰고, 최종 반복 위치와 X/Y/Yaw 전단은 숄더/키/도웰/포지티브 스토퍼가 담당
- CR-01-H3 스택 규칙: master locator는 X/Y 고정, secondary locator는 Y만 잡고 X는 풀기, rest pad는 Z seating만, latch keeper는 preload/uplift만 담당
- CR-01-H4 하드웨어 시드: master는 12 mm removable round bushing + replaceable stop, secondary는 X-slot/diamond Y-only locator, rest pad는 40 x 30 mm shim seat, latch keeper는 별도 기계식 secondary lock을 유지
- 카트 결합 원칙: 원뿔형 기계식 위치결정핀 + 래치, 단 래치 형번/수량/예압은 미확정
- 시험대 최소 보호: Firgelli 내장 비조정식 종단 리미트와 별개의 LS-01M 기계식 칼라를 유지한다. 외부 D4N, 전기 캠, 슬롯 브래킷과 전용 산업용 비상정지품은 활성 CAD/BOM에서 제외했다.
- LS-01M datum: 공식 Firgelli MB21 STEP 포락체를 220 mm 고정 station에 적용하고 이동 datum은 전방 clevis pin centre다. 12 x 320 mm twin rod와 104/298 mm 기계 칼라 offset을 사용하며 chrome rod clamp는 폐기했다.
- Firgelli 원본 STEP 4종(actuator/MB21/MB20/MB17), 분리 진단 렌더 2종과 SHA-256 기록은 `references/vendor/firgelli/` 및 `design_basis/firgelli_mount_datum_review_2026-08-27.md`에 보존
- 현재 핵심 open item은 선택한 450 lbf/8-inch 액추에이터의 실제 아이 두께, 공급 핀 스택과 MB21 외부 스톱 하중 허용 여부다. `JNT-CG-01`은 이 실측값을 넣은 1개 목업을 통과하기 전에는 6개분 제작치로 동결하지 않는다.

## Phase 2 주요 산출물

- `outputs/phase2/phase2_engineering_report.md`: 운동학, 하중, 민감도, 위험
- `outputs/phase2/diagonal_design_decision.md`: 사선 배치 대안 비교와 선정 근거
- `outputs/phase2/acrylic_feasibility.md`: 전체 아크릴/하이브리드 비교
- `outputs/phase2/purchase_research.md`: 공식 판매처 기반 부품 조사
- `outputs/phase2/phase2_bom.csv`: 구매·가공 BOM과 확인 가격
- `outputs/phase2/actuator_limit_package_summary.md`: LS-01 스톱·리미트 계산/선정 요약
- `outputs/cad/step/`: 7개 동작상태 조립 STEP + 2개 중앙 가이드/짐벌 상세 STEP + 방사형 액추에이터 조인트 및 LS-01 상세 STEP
- `outputs/cad/glb/`: 중립상태 GLB
- `outputs/cad/stl/`: IMU 브래킷·케이블 가이드
- `outputs/cad/dxf/`: 하부판·아크릴 상판 예비 2D 프로파일
- `outputs/renders/`: Phase 2 상태/중앙/방사형/조인트/LS-01M/JNT-CG-01 상세, 도면성 검토 및 vendor STEP 진단 렌더
- `outputs/phase2/artifact_manifest.json`: 산출물 크기와 SHA-256

## 재생성 및 검증

Windows PowerShell에서 `scripts/run_phase2.ps1`을 실행하면 계산 보고서, CAD, 렌더, 체크섬을 재생성하고 테스트를 수행한다. CadQuery 런타임은 `vendor/python`에 포함되어 있다.

```powershell
& .\scripts\run_phase2.ps1
```

2026-08-27 최신 검증: 단위 테스트 109개 통과, CAD 산출물 17개, pipeline 렌더 24개. 활성 BOM은 15행이며 HRT8E 구형 joint-package와 D4N/A22E 품목은 모두 0건, source ID 누락도 없다.

## 상태

`REV C TRUE 120-DEG RADIAL - DIGITAL CORE PASS - EYE WIDTH AND STOP MOUNT OPEN - NOT APPROVED FOR FABRICATION`

## NAVIMRO 단일 주문 패키지

2026-08-28 Rev D 기준으로 필요한 구매 자재와 부속을 나비엠알오 CSV 50개 감사행, 47개 활성 주문행으로 정리했다. 알려진 가격 합계는 VAT 포함 2,767,127원이며 팬/필터 로그인 가격, 착불비와 가공비는 제외된다.

- `procurement/navimro_single_order_bom.csv`: 주문용 원본 목록
- `procurement/navimro_single_order_bom.md`: 사람이 읽는 구매 요약
- `procurement/navimro_preorder_inquiry_2026-08-27.md`: 판매처 통합문의 문안
- `design_basis/navimro_single_order_redesign_basis_2026-08-27.md`: 나비엠알오 부품 기반 재설계 기준
- `design_basis/navimro_pin_lug_interface_assumption_2026-08-27.md`: 평판 미포함 M8-to-eye 핀/러그 인터페이스 가정과 발주 확인 게이트

액추에이터의 실제 M8 양단 형상과 핀 중심 길이, Hall/배선/전류, 래치/칼라 정격이 확인되기 전에는 반품불가 품목을 발주하지 않는다. active 상세 CAD는 DIHOOL A2 보수 포락체와 JFT-8R 카탈로그 형상을 사용한다.

단일 주문 패키지 추가 후 전체 단위 테스트 110개와 BOM 소계/CSV 무결성 검사가 통과했다.

웹 도면 재검토 후 평판 미포함 M8-to-eye 핀/러그 구성을 계획 기준으로 선택하고 수직 관절간격을 185 mm로 복원했다. `K92931811`의 실제 축단 부속, 핀 중심 길이와 Hall/배선 옵션은 판매처 확인이 남아 있다.

최신 결정: 공식 도면상 U/H 브래킷은 서로 쌓는 2축 세트가 아니라 단일축 장착 대안이므로 주문 수량을 0으로 내렸다. 대신 `K02020097 / JFT-8R` 구면 로드엔드 6개와 `NVR-P03/P04/P16` 이중 전단 용접 요크를 사용한다. 접힘 모듈 높이는 300 mm, 전 작동영역 핀 중심 길이는 269.040~394.209 mm, 여유 포함 최대 관절각은 10.852°다. 실제 A2 M8 양단 형상, 핀 중심 Lmin/Lmax, Hall/배선/전류와 STEP 확인은 발주 전 필수다.

2026-08-28 DIHOOL `DHLA6000-A2 24V` 공식 페이지에서 A2가 `평판 + M8 나사 설치형`이고 중앙 튜브 장착 헤드가 탈착식이라는 설명을 확인했다. 다만 현재 BOM의 `K92931811 / LA2000-125150`과 동일 모델이라는 증거는 없으며, 표시된 A2 STEP 링크도 403으로 내려받지 못했다. 따라서 Rev D의 M8 어댑터는 계속 provisional로 두고 판매처에 정확한 납품 모델·포함품·STEP를 요청한다.

사용자가 2026-08-28 나비엠알오 납품 사양을 `DC 12 V / 2000 N / 150 mm stroke / 5 mm/s`로 확인했다. 이 네 항목과 12 V 버스는 Rev D 확정 입력으로 승격했고, DHLA6000의 24 V·6000 N·72 W 값은 적용하지 않는다. A1/A2 설치형, M8 암/수와 물림 길이, pin-center Lmin/Lmax, Hall/배선/전류와 실제 STEP는 계속 발주 gate다.

추가 비교에서 DIHOOL `DHLA6000-A2` 12 V와 24 V 페이지가 동일 외형도와 동일 A2 STEP 이름을 공유함을 확인했다. 따라서 DHLA6000 제품군 안에서 전압형 간 기계 하드웨어 공용 가능성은 높다. 그러나 현재 주문품은 `LA2000-125150`, 2000 N/5 mm/s이고 DHLA6000 표는 2000 N을 15 mm/s와 짝지으므로 두 제품군의 기계부가 같다고 확대 해석하지 않는다.

전원·제어 구매품은 AC 입력, 12 V/29 A PSU, DMD-150 3채널, Mega2560 PRO, BNO055, 5 V DC-DC, AC/DC 차단기, 배선·단자·접지·함체·냉각까지 포함한다. 배터리/BMS/충전기는 정지 시험대라 제외했다. 제조사 매뉴얼로 DMD-150의 IN1/IN2/PWM, brake/coast 논리와 12 V 180 W, 무냉각 연속 12 A/냉각 시 15 A를 확인했다. 남은 전기 gate는 실제 액추에이터 Hall/배선/정격·기동·스톨전류, 회생전압용 양방향 TVS 선정·시험, 최종 배선도와 펌웨어다. 전기부는 계속 `하드웨어 대부분 포함, 최종 배선/통전 미승인` 상태이며 상세는 `procurement/electrical_control_completeness_2026-08-28.md`와 `design_basis/dmd150_official_manual_review_2026-08-28.md`를 따른다.

평판 미포함 핀/러그 관절의 독립 예비 STEP과 검토 렌더를 생성했으며, 전체 단위 테스트 112개가 통과했다.

## NAVIMRO 제작 CAD Rev A - 현재 기준

사용자의 400만원 상한과 제작 CAD/가공도면 요청을 반영해 기존 Firgelli CAD와 별도로 NAVIMRO 제작본을 완성했다. 이제 active NAVIMRO 산출물은 `outputs/navimro_fabrication/`과 `output/pdf/`에 있으며, 이전의 "active CAD는 아직 Firgelli" 문장은 역사 기록으로만 남는다.

- 조립 STEP 6상태: 접힘, 중립, 상승, 최대 pitch, 최대 roll, 최대 pitch+roll.
- 평철 DXF `NVR-P01`~`P14`, 900x800x15 아크릴 DXF, 4040/축/평철 절단표.
- moving Ø12 shafts + fixed LMF12UU 4개 + moving SK12 4개 중앙가이드.
- 50x50x6 6장 적층 Cardan cross와 네 M8 opposed trunnion.
- 접힘 전체 높이 300 mm, 전체 +/-3도와 Z 0/100 mm corner sweep 길이 273.196~385.349 mm.
- Rev A 당시 나비엠알오 49행 확정가 2,799,522원, 전체 계획 3,799,522원, 예산 여유 200,478원. 현재 Rev D 금액은 아래 최신 절을 따른다.
- 제작도면 PDF 11쪽과 조립·발주 PDF 11쪽은 전 페이지 렌더 검수 완료.
- 전체 단위 테스트 123개 통과.

핵심 문서:

- `design_basis/navimro_fabrication_release_revA_2026-08-27.md`
- `output/pdf/NAVIMRO_leveling_module_fabrication_drawings_revA.pdf`
- `output/pdf/NAVIMRO_leveling_module_assembly_and_order_pack_revA.pdf`
- `outputs/navimro_fabrication/artifact_manifest.json`

재생성:

```powershell
& .\scripts\run_navimro_fabrication.ps1
```

주문제작 액추에이터는 아직 즉시 결제하면 안 된다. 실제 pin-center 길이, 양단 M8 암/수 형상과 물림 길이, Hall/배선/전류/STEP, JFT-8R 적합성, CR-3001 및 collar 정격을 서면 확인한 뒤 transfer-drill 치수와 전원 정격을 최종 반영한다.

## 그림 중심 조립 매뉴얼 Rev B

2026-08-27 사용자 검토에서 기존 조립·발주 PDF의 조립 순서가 글 위주라 실제 연결 관계를 파악하기 어렵다는 문제가 확인되었다. 이를 보완해 `output/pdf/NAVIMRO_visual_assembly_manual_revB.pdf`를 추가했다.

- 전체 구조 분해도 1장과 하부에서 상부로 이어지는 8단계 누적 CAD 그림을 포함한다.
- 각 단계에서 새로 장착할 부품은 주황색, 이미 조립된 부품은 회색으로 표시한다.
- 각 단계마다 사용 부품, 조립 방법, 완료 판정을 같은 페이지에 배치한다.
- 중앙 가이드와 Cardan 관절은 확대 그림으로 별도 설명한다.
- 마지막 페이지는 현장에서 인쇄해 사용할 수 있는 한 장 조립 순서표다.
- CAD에 남아 있던 `DHLA2000_A1` 명칭은 확정 형식으로 오해되지 않도록 `LA2000 pin/lug planning envelope`로 변경했다.
- 조립 단계 그룹 검사 3개를 추가한 뒤 전체 단위 테스트 126개가 통과했다.

## Fusion 360 상세 CAD Rev C

사용자 요청에 따라 모든 프로파일, 철판, 접합판, 볼트, 와셔, T너트, nyloc 너트, pivot bolt, 상판 spacer가 보이는 상세 조립체를 추가했다.

- 전달 패키지: `output/NAVIMRO_Fusion360_detailed_CAD_revC.zip`
- Fusion 360 권장 파일: `outputs/navimro_fusion360_revC/step/NAVIMRO_detailed_neutral_revC.step`
- 분해 검토: `NAVIMRO_detailed_exploded_revC.step`
- 접힘 높이 검토: `NAVIMRO_module_only_collapsed_revC.step`
- 중립 자세 기준 556개 이름 있는 컴포넌트, 공급자 치수에 의존하는 187개는 노란색 provisional 상태다.
- 전체/접힘/중립/상승/분해 STEP와 8개 하위 조립체 STEP를 포함한다.
- 역수입 검증에서 neutral STEP는 722 solids, module-only collapsed STEP는 664 solids로 정상 복구됐다.
- module-only 접힘 외형은 900 x 800 x 292 mm다.
- 전체 테스트 132개 통과.

상세 근거와 수정 이력은 `design_basis/fusion360_detailed_cad_revC_2026-08-27.md`에 있다. Fusion 360에서 STEP를 연 뒤 필요하면 F3D로 저장한다. 노란색 부품은 공급자 STEP 또는 입고 실측값으로 교체하기 전까지 가공 승인하지 않는다.

2026-08-28 Fusion 실물 검토에서 액추에이터 조립부는 표시만 불명확한 것이 아니라 실제로 미완성임을 확인했다. 6 mm U/H 브래킷에 M8 피벗이 들어가고, U/H가 한 덩어리이며, 핀 구멍이 없는 솔리드와 프레임/액추에이터 간 큰 교차가 존재한다. 상세 판정과 수정 게이트는 `design_basis/fusion360_actuator_joint_review_2026-08-28.md`를 따른다. 현재 Rev C 액추에이터부로 발주·가공하지 않는다.

## Fusion 360 상세 CAD Rev D

Rev D는 Rev C의 액추에이터 체결 오류를 수정한 이전 검토 기준이다. 전체 조립성 수정은 아래 Rev E를 따른다.

- U/H 가상 스택을 제거하고 JFT-8R 6개, 실제 Ø8/Ø8.2 관통부, 스페이서, M8 피벗과 잠금너트를 개별 부품으로 모델링했다.
- 각 끝단은 `NVR-P03/P04` 받침판에 `NVR-P16` 러그 2장을 지그 정렬 후 용접하는 이중 전단 요크다.
- 하부 액추에이터 지지 프로파일은 640 mm, 상부 엔드/크로스 프로파일은 660 mm로 연결면까지 닿게 수정했다.
- 접힘, 중립, 상승, 최대 pitch, 최대 roll, 최대 pitch+roll 6개 자세에서 액추에이터와 상·하부 프레임의 솔리드 교차가 없다.
- 액추에이터 1번만 분리한 `ACT1_complete_mounting_cassette_neutral_revD.step`을 함께 제공해 핀과 요크 조립을 확인할 수 있다.
- 제작 해제 전 확인 항목은 A2 양단 M8 암/수 형상, 실제 핀 중심 길이, JFT-8R 입고 치수, M8 어깨부 길이와 공급자 STEP다.

상세 근거는 `design_basis/fusion360_actuator_joint_rebuild_revD_2026-08-28.md`에 기록한다. Rev D 패키지는 `output/NAVIMRO_Fusion360_detailed_CAD_revD.zip`, Fusion 권장 파일은 `outputs/navimro_fusion360_revD/step/NAVIMRO_detailed_neutral_revD.step`이다.

## Fusion 360 상세 CAD Rev E

Rev E는 Rev D 전체 조립체를 B-rep 교차시험과 조립 순서 관점에서 다시 검증한 현재 기준이다.

- Z 0~100 mm를 10 mm 간격으로 검사하고 중간 높이의 pitch/roll 최대 자세를 더한 14개 자세에서 가이드와 중앙부의 의도하지 않은 솔리드 교차가 없다.
- 상부 중앙 프로파일 관통, 교차 카단 핀, 잘못 놓인 SK12, 무가공 LMF/SK/상판 구멍, 부싱을 통과해야 했던 축 칼라와 제작 불가능한 50 x 64 스토퍼를 수정했다.
- 현재 가이드는 230 mm 축 2개, 고정 LMF12UU 4개, 이동 SK12 2개, 단일 240 mm 캐리지와 50 mm 평철 절단품으로 만든 독립 기계식 스토퍼를 사용한다.
- 직렬 카단 두 축은 Z 방향으로 12 mm 떨어져 있고 솔리드 간격은 4 mm다. 상/하 브리지는 각각 캐리지와 상부 중앙 레일에 0 mm 접촉한다.
- 명령 끝점의 스토퍼 여유는 접힘/상승 모두 2 mm이고 연결 전 모듈 포락체는 900 x 800 x 300 mm다.
- 카트 결합 그룹은 실제 카트 치수가 없으므로 모듈 아래에 분리된 provisional 참조로만 표시하며 조립 통과 판정에서 제외한다.
- 현재 가격이 있는 나비엠알오 소계는 VAT 포함 2,687,993원이다. 정확한 M4 LMF/SK 체결품, 상판 압축 슬리브와 모터 TVS가 주문행으로 확정되기 전에는 일괄 발주하지 않는다.

검증 근거와 조립 순서는 `design_basis/fusion360_assembly_validation_revE_2026-08-28.md`에 있다. 전달 패키지는 `output/NAVIMRO_Fusion360_detailed_CAD_revE.zip`, Fusion 권장 파일은 `outputs/navimro_fusion360_revE/step/NAVIMRO_detailed_neutral_revE.step`이다.
