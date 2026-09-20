# 프로젝트 인수인계 기록

## 2026-09-16 최신 상태 — 액추에이터형으로 재전환

산단 요청으로 수동 `M2R2-S220` 구매안을 보류하고, 기존 전동 3-RPS Rev E를 출발점으로 액추에이터형 요구조건과 BOM을 다시 확정한다. 수동 MISUMI 견적/장바구니/엑셀은 삭제하지 않고 `HOLD_DO_NOT_SUBMIT_OR_ORDER`로 보관한다. 현재 구매·제작·배선·통전·PoC 합격은 모두 미승인이다.

산단이 변경했다고 확인되지 않은 범위는 유지한다. 카트·적재물·사람 없음, 상판 없는 공개형, 자중 전용 시연을 기본값으로 두며, 전동안에서는 독립 기계식 스토퍼와 전기식 리미트를 별도로 검토한다. 자동수평 여부, 동작범위, 시험하중, 카트 결합 범위, 납기와 제출물을 먼저 확인한다.

- 최신 실행 기준: `requirements/current_variant_priority_2026-09-16.md`
- 다른 채팅용 전체 인수인계와 시작 프롬프트: `PROJECT_HANDOFF_ACTUATOR_2026-09-16.md`
- 기존 전동안 디지털 감사: `verification/RevE_PoC_release_candidate_audit_2026-09-04.md`
- 기존 수동 우선순위와 구매 기록은 이력이며 현행 발주 지시가 아니다.

## 2026-09-08 최신 범위 — 상부 패널 없는 공개형 시연

- 수동 `M2R2-S220`의 상부 패널은 사용하지 않으며 프로파일과 링크를 그대로 노출한다. 현행 CAD/BOM에는 원래 상부 패널이 없었다.
- 카트·적재물·사람, 별도 과조절 스토퍼/전용 받침, 전용 시험대 고정품과 카트 래치는 구매하지 않는다.
- 조절 범위와 최소 나사 물림을 측정하고 잠금너트5개/축을 체결하는 절차로 제한한다. 이는 독립 기계식 스토퍼와 동등하지 않다.
- 전용 고정품은 없지만 조절 중 하부가 움직이면 보유 중인 임시 클램프 또는 미끄럼 방지 패드를 사용한다.
- 남은 구매 전 작업은 활성20행 재검산과 한국미스미 최종 견적·납기 확인이다.
- 현행 기준은 `requirements/current_open_frame_demo_scope_2026-09-08.md`다.

## 2026-09-07 후속 범위 — 카트·적재물 없는 수동 시연

- 현행 `M2R2-S220`에는 카트, 적재물 또는 사람을 올리지 않는다.
- 하부 프레임을 시험대에 고정하고 조절 중 상판 받침을 사용하는 자중 전용 수동 시연으로 제한한다.
- 카트 로케이터/래치는 현행 구매에서 제외했다.
- 상부 확인 질량 소계는 9.069 kg이며 미확인 체결품을 포함한 구매 전 임시 자중은 10 kg이다.
- 구매 전 미결은 독립 과조절 방지/상판 받침, 시험대 고정품, 최종 BOM과 로그인 견적이다.
- 상세 판정은 `verification/m2r2s220_no_cart_pre_purchase_audit_2026-09-07.md`를 따른다.

## 2026-09-07 최신 상태 — M2R2-S220 Phase 2 CAD 완료

현재 활성안은 수동 턴버클 3-RPS `M2R2-S220`이다. 사용자가 `APPROVE CONCEPT`를 입력해 Phase 2로 진입했고, 장바구니 미스미 부품을 반영한 상세 CAD·자유도 계산·대표 자세 간섭·공구 접근·STEP 재수입 검증을 완료했다.

2026-09-07 사용자가 수동안을 우선순위 1로 다시 확인했다. 현행 실행 기준과 전체 구매 전 게이트는 `requirements/current_variant_priority_2026-09-07.md`다. 전동 Rev E는 향후 참고안으로 보관한다.

- 전체 크기 700×700×299.205 mm, pitch/roll 각각 ±3°.
- 하부 관절 중심 `[0,30,63]`, `[-30,-180,63]`, `[30,-180,63]` mm. 중립 링크280 mm.
- ±3° 링크265.420~293.310 mm, 최소 나사 물림21.345 mm, 최대 조절4.17회전.
- 조절 상태 랭크3/잠금 상태 랭크6. 대표9자세 간섭0, 3자세×84 공구축 예상 밖 방해0, STEP3개 재수입 통과, 전용검사6개 통과.
- 첫 CAD에서 A2 하부 SHAT12 공구축이 A3와 겹쳐 A2 하부 지지대를180° 돌린 뒤 해결했다.
- IKO PHS12L 필요 편각1.95°는 공식 보수 허용8° 이내다.
- NBK STB-M12 압축 정격, SCSJ/SHAT 유지력, 독립 기계식 스톱, 실제 카트 래치가 남아 `purchase_release=false`, `fabrication_release=false`, `poc_acceptance=false`다.

먼저 읽을 기록은 `logs/current_progress_2026-09-07.md`다. CAD 패키지는 `outputs/manual_turnbuckle_rev_m2r2s220`, 전달 ZIP은 `output/Manual_3RPS_M2R2S220_Cart_BOM_CAD_2026-09-06.zip`이며 SHA-256은 `8e8cb60aa3a78524401dc2db9d24f0e343b8fb75dc3a173965e1a9b50ac72ba7`이다.

아래 M2R2F2, M2R2F1과 이전 Rev 기록은 이력이며 현행 설계가 아니다.

## 최신 한 축 상세 M2R2F2

사용자 요청으로 A1 하부 R-STB-M12-상부 PHS12L 한 축을 조립/분해 모델링. `outputs/manual_m2r2f2_one_axis/README.md`와 `design_basis/manual_m2r2f2_one_axis_assembly_2026-09-05.md`가 최신 접합부 상세다. 조립에 직접 필요한 SHAT12/HFS8/HNTT8/BJ761/PHS12L/MCL12F/STB 치수를 제조사 PDF와 대조. 하부5.9+14+5.9 및 총0.2유격, 상부5+16+5, 지지대 안쪽26, 축12×100. 5모델 예상 밖 교차0, STEP5 재수입 통과. 상세 주물/나사산/내부부시/칼라슬릿 및 실제 공차·강도는 미확정.

## 최신 M2R2F1 체결 검토 / 볼트 통일

`outputs/manual_turnbuckle_rev_m2r2f1/README.md`, `design_basis/manual_m2r2f1_fastening_2026-09-05.md`가 최신. 제조사 PDF 도면 실독으로 HBLSSB8 다리40/두께6, HNTT8 높이9/돌출3, 프로파일 턱5.5를 반영. 뒤 가로재Y−180, 앞 세로450 두 개. M8×15 48개/M5×16 24개로 통일, M5 DIN433 OD9 와셔24개. M4 클램프는 M5 체결 전 제거/후 재조립해야 공구 경로가 확보됨. 264개 구성요소,9자세 교차0,3자세×84공구 경로 순서 적용 후0. 지지대의 슬롯 양옆2 mm 받침 강도는 미검증, 하중 승인을 주장하지 말 것. CAD 런타임 종료코드1은 유지, stdlib 패키지 검사는 정상.

## 2026-09-05 최신 CAD — 기성 연결부 Rev M2R2

후속 요청: 프로파일 절단은 허용, 접합부는 무가공 기성품 조립. `cad/manual_turnbuckle_rev_m2r2.py`, `scripts/build_manual_turnbuckle_rev_m2r2.py`, `design_basis/manual_revm2r2_stock_connections_2026-09-05.md`, `outputs/manual_turnbuckle_rev_m2r2/README.md`가 최신이다. 120° 방사형을 앞1/뒤2 직교 3-RPS로 변경하고 SHAT12 쌍+표준 축+기성 심+칼라를 슬롯에 직접 장착한다. M2R1 맞춤 부시/평판은 주문하지 않는다. 카트·스톱·제조사 정격 미완료, 검토만 완료. 아래는 이전 M2R1 기록이다.

## 2026-09-05 최신 CAD — 수동 Rev M2R1

사용자가 CAD 진행을 요청해 기존 Rev M2의 별도 수정본을 만들었다. 원본과 생성형 이미지는 변경하지 않았다.
- 소스: `cad/manual_turnbuckle_rev_m2r1.py`; 실행: `scripts/build_manual_turnbuckle_rev_m2r1.py`.
- 상부 포크의 Ø20급 보어, 플랜지 부시 6개, 내륜 스페이서 6개, 구면 내/외륜, 핀 머리·와셔·너트를 분리했다. A1/A2/A3 표시는 비구조 라벨이다.
- 원래 3-RPS 좌표/운동학 유지. 112개 구성요소/169 솔리드, 9자세에서 모든 서로 다른 부품 쌍의 교차 검사 통과(판정 임계 0.01 mm³). 링크 내부 나사 중첩은 검사 범위 밖이다.
- 초기 구면 포켓의 STEP 재수입 실패를 발견해 회전 단면으로 재작성했다. 후속 9자세 검사와 STEP 5개 개별 유효성/전체 조립체 3개 부피·경계 재대조를 통과했다.
- 중립 STEP 부피차 0.000000445 mm³. CAD 렌더 전체/내부/상부 단면·분해도를 육안 확인했다.
- 결과: `outputs/manual_turnbuckle_rev_m2r1/README.md`, `M2R1_CAD_AUDIT.json`, `STEP_MANIFEST.json`. ZIP: `output/Manual_3RPS_RevM2R1_CAD_Review_2026-09-05.zip`.
- 부시 공차/재질, 구면 내부 치수, 스페이서 3.2 mm, 임시 M12x80의 평활부50 mm는 공급품 확인 전 가정이다. 원래 M12x65와 신규 스페이서 추가를 기존 26행 BOM에 자동 주문 반영하지 않았다.
- STB 압축 사용, 정확 좌나사품, 하부 핀 유지장치, 프레임 체결 상세, 기계 스톱, 실측 카트/하부 장착과 총질량은 미확정이다. 구매/제작/실물 성능 승인은 false.

## 2026-09-05 후속 — 외관과 조립 편의 개선

사용자가 '쉽게 만들되 복잡해 보이게' 개선하도록 요청했다. 실제 기능이 있는 세 링크/관절을 노출하고 표준 은색 프레임·검은 조인트·청색 축 라벨로 정리한다. 동일 키트 3개, 기존 어댑터 2종, 운용 잠금/조립 고정 구분을 채택했다. 상세 사양은 `design_basis/manual_revm2_appearance_assembly_2026-09-05.md`다. CAD 형상은 변경하지 않았다. 생성형 외관 이미지는 시각 참고이며 부품 수량·조립 검증 근거가 아니다.

## 2026-09-05 최종 결정 — 턴버클 Rev M2 재활성화

사용자가 턴버클 구조의 설명력과 이동체 상부모듈 개발 단계로서의 의미를 유지하는 방향에 동의했다. M3는 보관하고 Rev M2를 1순위로 되돌렸다. 최신 기준은 `requirements/current_turnbuckle_priority_2026-09-05.md`다.

- 이번 작업은 우선순위 갱신, 기존 코드/자료 재감사, 제조사 공개자료 재확인, 조달 묶음과 미발송 문의 초안 작성이다.
- 상부 BJ762-20001의 CAD는 부시를 독립 모델링하지 않고 12.2 mm 구멍으로 단순화했고 끼움 검사도 상수 비교였다. 기존 통과기록은 실제 부시/핀 적층 검증을 의미하지 않는다.
- SJN은 중앙 joint nut다. 'SJN 잠금너트 2개'라는 과거 명칭을 공급 문의에서 정정했다. 기존 잠금 위치를 삭제하지 않았다.
- 형상/검증 코드/기존 BOM 원본은 수정하지 않았다. 상세 CAD, 구매/제작, 물리시험, 공급처 문의 발송은 미수행이다.
- 다음 우선 대상은 STB 압축 사용, 정확 LH 로드엔드/너트, 상부 부시/핀 적층이다. 전체 기구 재설계 대신 국소 확인을 우선한다.
- 관련 파일: `design_basis/manual_revm2_minimal_completion_2026-09-05.md`, `procurement/manual_revm2_procurement_groups_2026-09-05.md`, `procurement/manual_revm2_supplier_inquiry_drafts_2026-09-05.md`.

아래 M3 결정은 같은 날짜의 이전 이력이며 현재 우선순위가 아니다.

## 2026-09-05 최신 상태 — 최소 수동식 M3 개념 우선

사용자가 연구과제 미선정과 시간 제약, 기자재 구매 제한 때문에 기계식 우선 및 기존 구조에 구애받지 않는 최소 설계를 요청했다. 1순위는 `MANUAL_CROSSED_HINGE_M3_CONCEPT`다. Rev E 및 Rev M2는 보관한다.

- 새 구조는 하부/중간/상부 구조 3단, 직교 경첩 2축, 조절나사 2개, 나사 잠금 및 별도 포획 클램프다.
- 독립 Z 상승과 자동보정 제외는 앞선 대화에 따른 실행 가정이다. 수동 ±3° 조절 후 10 kg 하중에서 수평 유지 시연을 목표로 한다.
- 간단한 링크 산술과 169자세 중심 이동 계산만 수행했다. CAD/제작도/실물 시험을 새로 만들거나 수행하지 않았다.
- 예시 250 mm 레버암에서 각 축 나사 조절량은 ±13.10 mm. 예시 기구의 중심 종속 이동은 X 4.70/Y 2.26/Z 13.24 mm까지다. 절대 횡이동 금지와 동일하지 않다.
- 경첩 정격/유격, 나사 및 포획클램프, 실측 카트 인터페이스, 예산비목과 축소 성과 인정은 미확정. 구매/제작 승인은 false.
- 시작 파일: `requirements/current_manual_priority_2026-09-05.md`, `concepts/manual_crossed_hinge_m3_2026-09-05.md`.
- 이번 요청은 우선순위 변경/개념설계를 허용한다. AGENTS.md의 새 개념 상세설계 게이트는 유지한다.
- 이전 문서의 컴파일 미완료 표기는 실제 Rev E 컴파일 기록과 불일치하는 과거 상태이며 M3 업무로 이어받지 않는다.

아래의 과거 ‘최신 상태’ 제목은 해당 날짜의 이력이다.

## 2026-09-04 최신 상태 - Rev E 작동 PoC 디지털 실행 패키지 완료

- 우선순위 1은 `POWERED_PROFILE_RADIAL_3RPS_REVE_POC_RC1`, 우선순위 2는 수동 턴버클 Rev M2 백업안이다.
- 공급자 인터페이스 레지스터, MotionGearOn/Motorbank 문의서, Rev E 맞춤품 9종 DXF와 9쪽 제작도, 홀표·절단표·조립순서를 작성했다.
- 400x500x155 mm 전장함 STEP/배치, 회로 PDF, 단자표, 57행 점대점 배선표, 하네스표와 I/O표를 작성했다. 디지털 외형 검사에서 부품 겹침 0건, AC-로직 이격 60 mm다.
- MDD10A의 2채널 공용 전원구조를 반영해 보드입력 10 A 퓨즈 2개+예비 1개를 추가하고 퓨즈홀더 수량을 6개로 수정했다. 새 후보 BOM은 61행, 화면가 확인분 1,278,437원이다.
- Mega2560 펌웨어와 USB 로거를 구현했다. Arduino CLI 1.5.1/AVR 1.8.8로 Mega2560 컴파일이 통과했고 flash 15,296 bytes, SRAM 901 bytes다.
- OpenCascade 27자세 검사를 3회 재실행해 동일 서명을 얻었다. 핀 거리 210.771741-276.937115 mm, PHS6 최대 4.096369 deg, 예상하지 않은 교차 0건이다. 기존 Fusion 간섭검사 3회·단면검사 3회 증거도 재대조했다.
- 전체 회귀시험 226개와 신규 전용시험 10개가 모두 통과했다.
- 핵심 작업 폴더는 `outputs/profile_radial_revE_poc_release_candidate`, 제작자료는 `fabrication/profile_radial_revE_release_candidate_2026-09-04`, 감사결과는 `verification/RevE_PoC_release_candidate_audit_2026-09-04.md`다.
- 아직 열려 있는 외부 게이트는 LMB-10 도면/실측, 액추에이터 전류·엔코더·리미트·듀티 정보, 실물 전장 장착홀, 가공·배송 견적, 단축 통전과 10 kg 27회 시험이다.
- 따라서 현재 `digital_package_pass=true`이지만 `purchase_release=false`, `fabrication_release=false`, `power_release=false`, `poc_acceptance=false`다.
- 타 PC 전달 파일은 `output/Profile_Radial_3RPS_RevE_PoC_RC1_2026-09-04.zip`이며 145개 파일의 CRC·필수경로 검사를 통과했다. 무결성은 같은 이름의 `.zip.sha256` 파일로 확인한다.
- 상세 수행·시행착오는 `logs/reve_poc_implementation_2026-09-04.md`, 최신 요구 기준은 `requirements/current_variant_priority_2026-09-04.md`를 먼저 읽는다.

## 2026-09-02 23:15 최신 상태 - 전동식 Rev E CAD 단계 완료

- 우선순위 1 전동식은 `POWERED_PROFILE_RADIAL_3RPS_REVE_ACTUAL_VENDOR`로 갱신했다. 우선순위 2 수동 턴버클 Rev M2는 백업안으로 유지한다.
- 실제 공급자 STEP `LM4075OE-1075-100mm.stp`의 여섯 바디를 축마다 넣은 Fusion 단일 조립체를 생성했다. 파일은 `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`다.
- 27자세 요구 핀 길이는 210.771741-276.937115 mm이고 205-305 mm 액추에이터 포락체 안에 들어간다. PHS6 최대 굴절은 4.096369 deg로 게시 허용 8 deg 이내다.
- Fusion `Design.analyzeInterference`를 150개 구성요소에 3회 반복했다. 매번 예상하지 않은 간섭은 0건이고, 공통 3건은 Ø6.4 액추에이터 보어와 M6 축의 0.000116-0.001377 mm3 수치 허용오차 접촉이다.
- X=0/+3/-3 mm 단면검사 3회, OpenCascade 교차검사, BOM 역대조 후 전체 검증을 한 차례 더 반복했고 같은 결과를 얻었다.
- 하부 횡재는 Y=330/95/-47.5/-330 mm, 어댑터는 120x70x8 mm다. A1/A2 프로파일 홀은 96 mm 대칭 피치, A3는 local X=-70/+30 mm의 비대칭 100 mm 피치다.
- 제어부는 국내 구매 비용을 줄이기 위해 `MDD10A x2 + Mega2560 호환 x1 + MPU6050 x1 + LRS-350-24 x1 + 24->5 V buck x1`로 변경했다. DMC-200 3대, DMD-150 3대, WT901C, 검증되지 않은 모터단 TVS와 중복 USB 케이블은 제외했다.
- 최신 BOM은 `procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv`의 60행이다. 확인 화면가 합계는 1,268,724원, 400만원 대비 가공·배송 전 잔액은 2,731,276원이다.
- 필터와 수식 요약이 있는 Excel 검토본은 `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Domestic_BOM_2026-09-02.xlsx`다.
- 상세 검증은 `design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md`, 국내 제어부 조사는 `web_research/domestic_electronics_research_log_2026-09-02.md`를 따른다.
- 다른 PC 전달용 핵심 묶음은 `output/Profile_Radial_3RPS_RevE_CAD_Package_2026-09-02.zip`이며 같은 이름의 `.sha256` 파일로 무결성을 확인한다. 공급자 STEP 원본도 `references/vendor_cad`에 복사해 OneDrive 밖의 Downloads 경로 의존성을 제거했다.
- CAD 단계는 완료했지만 LMB-10 공급도면, 액추에이터 전류/핀맵, Rev E 제작용 DXF·공차도, 전장함 내부 배치와 단축 통전시험이 남았다. 현재 `purchase_release=false`, `fabrication_release=false`, `commissioning_release=false`다.

## 2026-09-02 최신 우선순위 변경 - 전동식 1순위, 수동식 2순위

- 사용자 결정에 따라 기계식 전환 직전의 `POWERED_PROFILE_RADIAL_3RPS_REVD`를 우선순위 1로 재활성화했다.
- 우선순위 1은 `LM4075OE-1075` 24 V/100 mm/엔코더 액추에이터 3개, `DMD-150` 3개, `Mega2560 PRO`, `WT901C/UART`, `NES-350-24`를 사용하는 전동 자동수평안이다.
- 우선순위 2는 현재 검증한 `STB-M12` 수동 턴버클 Rev M2다. 폐기하지 않고 구매·제어 위험에 대한 백업안으로 보존한다.
- 전동식 기술 BOM은 `procurement/profile_radial_revd_final_master_bom_2026-09-01.csv`의 62행이다. 가격 확인분은 1,589,208원이고 A6061 가공품 15개, 스탠드오프 6개, 배송·세금은 미포함이다.
- 우선순위 변경은 주문 승인이 아니다. 액추에이터 정확 옵션/STEP/배선/정격·기동·스톨전류, LMB-10 동봉 핀, 가공견적, 최종 회로·배선·펌웨어와 단축 통전시험이 남아 있다.
- 현재 상태는 `PRIORITY_1=POWERED_REVD`, `PRIORITY_2=MANUAL_REVM2`, `purchase_release=false`, `fabrication_release=false`, `commissioning_release=false`다.
- 최신 우선순위 기준은 `requirements/current_variant_priority_2026-09-02.md`다.

## 2026-09-02 우선순위 2 백업안 - 시판 턴버클 Manual 3-RPS Rev M2

- 사용자가 CadQuery/OpenCascade로 무인 생성·반복검사를 수행하고 최종 조립체만 Fusion에서 F3D로 확정하는 절차를 승인했다.
- Rev M1의 Ø32/Ø25 텔레스코픽 관, 21개 조절홀, POM 가이드와 맞춤 플러그/클레비스가 제작성이 나빠 새 Rev M2로 분기했다. Rev M1 파일은 시행착오 기록으로 보존한다.
- Rev M2는 공통 Z를 제외한 pitch/roll +/-3 deg 전용이다. `STB-M12`, `BJ761-12011N`, `BJ762-12001`, `BJ762-20001`, `PHS12L`과 단순 평판 6장으로 구성한다.
- 상부 `BJ762-16001`은 링 폭만 보고 선택했으나 PHS12L 목 폭 19 mm가 포크 간격 17 mm를 통과하지 못해 B-rep 검사에서 기각했다. 포크 간격 22 mm의 `BJ762-20001`과 12→20 부시로 수정했다.
- 최종 운동학은 하부/상부 반경 75/315 mm, 핀 z=81/213 mm, 요구 길이 262.723-284.444 mm, STB 내부 최소 물림 25.778 mm다.
- 9자세를 두 사이클 반복해 운동학/강도, OpenCascade 간섭, 단면/끼움과 BOM 역검산을 수행했다. 두 사이클 모두 동일하고 간섭 0건이다.
- 추가 자립성 감사에서 169자세 구속 Jacobian이 모두 rank 6, 최소 특이값 0.4018, 최대 조건수 4.3105로 통과했다. 20 kg/CG 편심 150 mm의 12,168 중력조건도 모든 반력이 양수이고 최대 등가 축력 306.660 N으로 통과했다.
- 따라서 세 링크와 STB 공급 잠금너트를 모두 체결한 정지 상태에서는 중앙 기둥 없이 상판이 자립한다. 링크가 하나라도 빠진 조립 중 상태와 하중을 둔 조정에는 임시 받침이 필요하다.
- 잠금 스택 재감사에서 외부 나사 경계가 축당 3곳임을 확인했다. STB 공급 SJN 잠금너트 2개/축 외에 F09 RH, F11 RH, F12 LH를 각 1개/축 추가해 BOM은 26행이 됐다. 특히 F12 좌나사 너트는 정확 SKU 확인 전이다.
- 실제 하부 접촉/카트 체결 형상과 완성 질량중심이 없으므로 비고정 전체 장치의 횡외력 전도저항은 미검증이다. 이 항목은 구매/제작 gate로 유지한다.
- 결과는 `outputs/manual_turnbuckle_rev_m2`, 기준은 `design_basis/manual_turnbuckle_rev_m2_2026-09-02.md`, BOM은 `procurement/manual_turnbuckle_rev_m2_bom_2026-09-02.md`다.
- 다음 작업은 정확한 PHS12L/F12 좌나사 잠금너트/ID12-OD20-L11 부시 국내 SKU 확정, STB-M12 압축 사용 확인 또는 1축 proof test, 완성 CG·하부 접촉형상 측정, 그 뒤 Fusion F3D 최종 조립체 작성이다.
- 현재 `purchase_release=false`, `fabrication_release=false`다.
- 기존 v1 전달 ZIP `output/Manual_3RPS_RevM2_CadQuery_Package_2026-09-02.zip`은 자립성 추가 감사 전 이력으로 보존한다.
- 최신 전달물은 `output/Manual_3RPS_RevM2_CadQuery_Package_v2_2026-09-02.zip`이다. 자립성 계산/감사, 잠금너트 5개/축 CAD, 26행 BOM과 최신 문서를 포함하며 무결성 값은 같은 이름의 `.sha256` 사이드카를 따른다. 전체 회귀시험은 217개가 408.839초에 통과했다.

## 2026-09-01 현재 활성 상태 - 수동 조절식 3-RPS로 전환

사용자의 최신 지시에 따라 전동 액추에이터와 자동수평 전자제어를 현재 PoC 범위에서 제외했다. 기존 전동안은 삭제하지 않고 `design_basis/archived_powered_control_architecture_2026-09-01.md`에 보존했다.

현재 활성 기준은 다음과 같다.

- `requirements/current_manual_scope_2026-09-01.md`
- `design_basis/manual_adjustable_3rps_baseline_2026-09-01.md`
- `procurement/manual_3rps_bom_delta_2026-09-01.csv`
- `calculations/manual_adjustable_strut_screen.py`

현재 목표 구조:

- 120 deg 방사형 수동 길이조절 지지대 3개
- 기존 700 x 700 mm 프로파일 프레임과 250 mm 지지 반경은 재사용 후보
- 수동 Z 0-50 mm와 pitch/roll 각각 +/-3 deg를 보존 목표로 설정
- 중립 핀 중심 길이 약 230 mm
- 27자세 요구 길이 212.137-297.864 mm
- 수동 지지대 예비 포락체 205-305 mm
- 전동·센서·전원·배선 품목은 모두 `ARCHIVED_DO_NOT_ORDER`

현재 상태:

```text
ACTIVE_VARIANT = MANUAL_ADJUSTABLE_3RPS
POWERED_VARIANT = ARCHIVED_DO_NOT_ORDER
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
```

다음 작업은 수동 사다리꼴 나사 스트럿, 턴버클, 텔레스코픽 잠금식 후보를 실제 국내 구매품 도면으로 비교하고, 나사 좌굴·조절 토크·잠금·조인트 적층을 계산하는 것이다. 제품 선정 뒤 기존 Fusion Rev D를 별도 `Manual 3RPS Rev M1`로 복제·수정하고 전 자세 간섭과 공구 접근을 다시 검사한다.

## 아래 내용의 상태

아래의 Rev D 전동 BOM, DMD-150, LM4075OE, IMU와 전원 관련 기록은 방향 전환 전의 이력이다. 시행착오와 향후 전동화 참고를 위해 보존하지만 현행 구매 지시로 사용하지 않는다.

## 2026-09-01 Rev D 최종 통합 BOM 작성 - 전동안 보관 기록

- Rev D Fusion 네이티브 조립체, 구조 BOM, 나비엠알오 45개 세부행, 분할 조달품, 24 V 제어·보호·배선 및 가공품을 `procurement/profile_radial_revd_final_master_bom_2026-09-01.csv`의 62개 고유 행으로 통합했다.
- 검토용 설명서는 `procurement/profile_radial_revd_final_master_bom_2026-09-01.md`, 필터·수식·주문 제외표·주문 게이트를 포함한 엑셀본은 `outputs/bom/Profile_Radial_3RPS_RevD_Final_BOM_2026-09-01.xlsx`다.
- 공급처별 가격 확인분은 NAVIMRO 1,085,370원, MotionGearOn 390,000원, Motorbank 13,200원, SpeedMall 52,448원, DigiKey 48,190원으로 합계 1,589,208원이다. 400만원 상한 대비 가공·배송·세금 전 잔액은 2,410,792원이다.
- 가공 견적 대상은 A6061-T6 판재 15개를 만드는 8개 DXF 행과 OD16/ID8.4/L28 스탠드오프 6개를 포함한 9행이다. 견적과 배송비는 현재 합계에 포함하지 않았다.
- `1.5KE24CA`, JFT-6R, LM4075-F, DHLA6000-A2, 구형 피벗 길이 키트, 2 m DIN 레일과 5 V 벽면 어댑터는 주문 제외표로 분리했다. 최종 24 V 모터단 보호는 `SMCJ24CA` 양방향 TVS 3개 사용+3개 예비를 기준으로 잡았다.
- 결제 전 필수 게이트는 (1) LM4075OE-1075 세 대 모두 24 V/100 mm/5 V encoder/6 ppr 옵션 확인, (2) 공급자 아이 폭·핀 중심거리·배선·전류 자료 확인, (3) LMB-10 세트별 Ø6 핀과 리테이너 포함 확인, (4) 가공 견적과 배송·세금 포함 총액 400만원 이하 확인이다.
- 기술 BOM은 완성됐지만 위 게이트가 열려 있으므로 `purchase_release=false`, `fabrication_release=false`를 유지한다. 향후 전동안을 재활성화할 때는 최종 CSV/엑셀의 `procurement_status`와 `Order Gates` 시트부터 다시 확인한다.

## 2026-09-01 발주 요약표 재감사 - 구매 승인 철회

사용자가 주문 그룹 표가 전체 리스트인지, TVS 다이오드가 왜 포함됐는지 문제를 제기했다. 확인 결과 지적이 맞았다. `profile_radial_revd_split_source_order_groups_2026-09-01.csv`는 전체 BOM이 아니라 9개 공급처 요약행이며, G04 한 행이 `profile_radial_revd_navimro_candidate_bom_2026-09-01.csv`의 45개 행을 숨기고 있었다. 그 45개 중 12개는 `HOLD_*`, `FIT_KIT_HOLD_*`, `READY_AFTER_*` 조건이 남아 있으므로 과거 `READY_TO_CART`와 `split_purchase_release=true` 판정은 잘못됐다.

DMD-150 매뉴얼은 모터단 양방향 TVS와 `1.5KE24CA`를 참고 예로 제시하지만 실제 스탠드오프 조건을 검토하라고 명시한다. 해당 부품은 `VRWM 20.5 V`, `VBR(min) 22.8 V`여서 24 V PWM 모터 출력의 무검증 확정품으로 쓸 수 없다. 주문수량을 0으로 바꾸고 `DO_NOT_ORDER_UNVALIDATED_24V`로 내렸다. 24 V 승인 회생보호 회로와 실제 파형을 확보한 뒤 다시 선정한다.

최신 판정은 `procurement/profile_radial_revd_order_readiness_audit_2026-09-01.md`에 기록했다. 공급처 분할 방향은 유지하지만 전체 세부행 평탄화, 액추에이터 전류, 피벗 길이, LMB 핀, PHS6/JFT-6R 선택, 함체/DIN 배치와 보호회로가 닫히기 전에는 주문하지 않는다. 현재 `purchase_release=false`, `fabrication_release=false`다.

## 2026-09-01 일괄 발주 준비도 감사 — 현재 NO-GO

사용자가 필요한 품목을 나비엠알오에서 한 번에 주문해야 한다고 재확인했다. 최신 Rev D 구조·전장 BOM과 나비엠알오의 2026-09-01 판매 페이지를 대조한 결과, **현재는 주문 가능한 상태가 아니다.** Fusion 전체 간섭 0건은 유지되지만 구매 기준의 핵심 액추에이터 `LM4075OE-1075 24 V/100 mm/5 V encoder`와 같은 활성 나비엠알오 SKU가 확인되지 않았고, 나비엠알오의 엔코더형 `LM4075E / 24V` 10종은 단종으로 표시된다. 주문 가능한 `K92931811 / DIHOOL 12 V 150 mm`는 최신 CAD와 전압·행정·피드백·외형이 달라 임의 대체할 수 없다.

`LMB-10`은 나비엠알오 페이지의 단종 표시와 `K47449076 1SET(2EA)` 출하 옵션이 서로 모순되어 통합 견적 확인이 필요하다. `PHS6`는 `K02020042 / JMC JFT-6R`로 나비엠알오 치환 가능성이 있지만 공급도면 확인, Fusion 컴포넌트 교체와 간섭 재검사가 먼저다. A6061 원소재 SKU/네스팅, F05/F07/F13~F15 정확 SKU, 24 V 전원·배선·보호품의 통합 BOM과 VAT·가공·배송 포함 400만원 견적도 아직 없다.

이 판정으로 과거 `한 축분 선행 구매 후 나머지 주문` 절차는 폐기한다. 한 번 주문 조건에서는 공급 도면과 STEP를 먼저 받아 CAD를 확정하고, 심·피벗 길이 조정용 여유 키트까지 같은 장바구니에 넣어야 한다. 개별로 주문 가능한 프로파일, DMD-150, WT901C도 전체 게이트가 닫히기 전에는 결제하지 않는다. 상세 판정과 기계 판독용 차단 목록은 `procurement/profile_radial_revd_single_order_readiness_2026-09-01.md`와 `procurement/profile_radial_revd_single_order_gap_list_2026-09-01.csv`에 기록했다. 현재 `purchase_release=false`, `fabrication_release=false`다.

## 2026-09-01 최신 상태 — Fusion 전체 간섭 검사 통과

사용자가 Fusion 화면에서 4035/DCB3025 L 브래킷이 프로파일 가운데에 박혀 있다고 지적했다. 재검사 결과 지적이 맞았으며, 기존 독립 STEP 감사가 프레임-브래킷 쌍을 검사하지 않아 잘못 통과한 것이 원인이었다. Fusion `검사 > 간섭`에서 하부 브래킷-횡재 교차 `7009.664/3767.350 mm3`를 확인한 뒤 브래킷 코너 기준을 횡재 중심이 아니라 횡재 외측면으로 옮겼다.

후속 전체 조립 검사에서 드러난 체결 문제도 함께 수정했다. L 브래킷 두 다리는 한 솔리드로 합치고 X/Y 체결 보어를 넣었으며, 프로파일 T-slot 언더컷, T너트 방향과 체결 깊이를 반영했다. 로컬 LMB 어댑터는 M8 볼트 머리와 LMB 베이스가 겹치던 `90x70x8/60 mm pitch`를 폐기하고 `120x70x8/96 mm pitch`로 바꿨다. M8 소켓 외경을 포함한 A2/A3 최소 작업 여유는 `3.569 mm`, 홀 중심 최소 가장자리 여유는 `12.0 mm`다. LMB 베이스 보어, PHS6 암나사 코어, TB306 머리 위치, 스토퍼 스탠드오프/너트 보어를 추가했고 전면 스토퍼 앵커는 PHS6를 피하도록 `80x85x6`으로 줄였다.

최종 검증 결과:

- Fusion 루트 컴포넌트 전체 `검사 > 간섭`: **간섭이 탐지되지 않았습니다**.
- Fusion 네이티브 컴포넌트 `138개`, 전체 STEP `289 solids`, 포락체 `700x700x300 mm`.
- 독립 STEP 감사 14개 부품군 쌍 모두 교차체적 `0 mm3`. 여기에는 프레임-브래킷, 어댑터-LMB, LMB-액추에이터, 액추에이터-PHS, PHS-스토퍼가 포함된다.
- Rev D 회귀검사 `18개` 통과. 최신 가공자료는 DXF `8개`와 CSV `2개`다.
- Fusion 원본, STEP, 렌더, 감사 JSON은 `outputs/profile_radial_revD_fusion_native/`에 있다.
- 타 PC 전달 ZIP은 `output/Profile_Radial_3RPS_RevD_Fusion360_Native.zip`이며 42개 항목이고 CRC read를 통과했다. 최신 SHA-256은 같은 위치의 `.zip.sha256` 파일에 기록한다.

이번 결과는 현재의 단순화 CAD 형상에 대한 디지털 조립성 통과다. 실제 LM4075OE 아이 폭/공급자 STEP, LMB 핀과 리테이너, 상부 심/숄더볼트, 스토퍼 정확 SKU, A1 한 축 실조립이 남았으므로 `fabrication_release=false`, `purchase_release=false`를 유지한다.

## 2026-08-31 이전 상태 — 허브 없는 프로파일 Rev D Fusion 네이티브 조립체

사용자가 상세설계 완료 전 주문하지 않고, 중앙 허브판 없이 프로파일과 브래킷의 실제 조립을 Fusion 360에서 확인하겠다고 결정했다. 이에 Rev C의 `280x220x10 mm` 허브판을 삭제하고 하부 4040 횡재별 `90x70x8 mm` A6061 로컬 어댑터 3개로 LMB-10을 고정하는 Rev D를 만들었다. 상·하 프레임은 각각 4035/DCB3025 8개와 수평 X/Y 체결축으로 조립한다.

Fusion 360에서 스크립트를 직접 실행해 `Profile_Radial_3RPS_RevD_NATIVE.f3d`를 생성했다. 상위 10개 조립 그룹, 141개 네이티브 컴포넌트, 프로파일/브래킷/조인트/액추에이터/스톱/볼트·너트·와셔·임시 심이 포함된다. 전체 STEP은 314 solids, 포락체는 `700x700x300 mm`다.

검증 결과:

- 27자세 핀 거리 `218.958~279.846 mm`; LM4075OE 이론 205~305 mm 대비 여유 `13.958/25.154 mm`.
- 하부 핀축 직각오차 `2.23e-14 deg`, PHS6 최대 굴절 `4.096 deg`.
- 액추에이터 대 상하 프레임/브래킷/스톱, 스톱 대 상하 프레임의 비의도 교차체적 모두 `0 mm3`.
- 독립 M10 스톱은 명령범위 밖 `-2/+52 mm` 접촉, 최대 횡이동 `13.320 mm`, 최소 개구 여유 `6.680 mm`.
- 단위검사 16개 통과, DXF 8개와 CSV 좌표표 2개 생성 및 재로딩 확인.

이번 세부 재검토에서 스톱 컴포넌트 이름에 남아 있던 과거 `90x80/80x50` 표기를 실제 `90x125/80x100`으로 고쳤다. 상부 PHS 피벗 와셔를 실제 접촉면으로 옮기고 1 mm 임시 심 3개를 추가했으며, 스톱 접촉바를 로드에 고정하는 M10 잼너트 12개도 추가했다. 마지막으로 A1 조인트 상세도에서 액추에이터 OD20 로드가 상부 아이 외형에 닿기 전 끝나는 표시 오류를 찾아, 로드가 아이 외형과 2 mm 겹치도록 보정하고 전용 회귀검사를 추가했다. 수정 후 Fusion과 STEP 검사를 다시 통과했다.

현재 기준은 `design_basis/profile_radial_revD_fusion_native_2026-08-31.md`, `procurement/profile_radial_revD_structural_bom_2026-08-31.md`, `outputs/profile_radial_revD_fusion_native/`다. `output/Profile_Radial_3RPS_RevD_Fusion360_Native.zip`을 다른 PC 전달용으로 사용한다.

전달 ZIP은 43개 항목으로 구성했으며 Fusion F3D, 전체 및 그룹 STEP 11개, 검토 이미지, DXF 8개, CSV 2개, BOM·설계 기준·작업 이력과 재생성·검증 스크립트를 포함한다. ZIP CRC와 필수 파일 포함 여부를 확인했으며 SHA-256은 같은 위치의 `.zip.sha256` 파일에 기록한다.

남은 게이트는 실제 LM4075OE 아이 폭/STEP, LMB 핀 포함품, 상부 피벗 심과 숄더볼트 길이, 스톱 스탠드오프 정확 SKU, A1+스톱 1차품과 한 축 실조립이다. 따라서 `fabrication_release=false`, `purchase_release=false`를 유지한다.

## 2026-08-31 최신 상태 — 실제 120 deg 방사형 Rev C 디지털 코어 통과

Rev B의 잘못된 체결축과 90/90/180 deg 지지배치를 버리고, 방위각 90/210/330 deg의 3-RPS Rev C를 새로 만들었다. 하부는 DNF4040 직교 프레임과 `280×220×10 mm` A6061-T6 소형 허브판, 상부는 DNF3030 직교 프레임으로 구성한다. 큰 구조판과 용접은 없으며, 하부 LMB-10 세 개는 허브판에 고정하고 상부 PHS6 세 개는 3030 슬롯 아래에 직접 둔다.

브라켓은 4035/DCB3025의 두 다리를 모두 같은 평면 프레임 코너 안쪽에 세우고, 실제 체결축을 수평 X/Y 두 방향으로 모델링했다. PHS6 단측 연결의 14.5 mm 접선 오프셋은 하부와 상부 아이에 동일하게 적용했다. 요청한 Z/pitch/roll마다 세 하부 R축 평면조건을 풀어 플랫폼 X/Y/yaw 보정량도 CAD에 반영했다.

핵심 검증 결과:

- 27자세 최대 구속 잔차 `6.54e-13 mm`; 최대 종속 보정 X `0.342 mm`, Y `0.171 mm`, yaw `0.079 deg`.
- LM4075OE 요구 핀 길이 `217.933~278.080 mm`; 205~305 mm 이론범위 대비 수축/신장 여유 `12.933/26.920 mm`.
- 액추에이터축-핀축 최대 직각오차 `1.56e-13 deg`; PHS6 최대 굴절 `4.096 deg`.
- 대표 6자세 액추에이터 몸체/아이 대 고정구조 교차체적 `0 mm3`.
- 접힘 포락체 `700×700×300 mm`; 독립 스토퍼 횡이동 최대 `14.544 mm`, 계산 여유 `5.456 mm`.
- 85개 위치 부품, STEP 14개, DXF 1개, 렌더 9개. 접힘 STEP 역수입 `224 solids`, 유효 체적 양수.
- Rev C 및 Rev B 기각 회귀시험 합계 15개 통과.

현재 전달물은 `output/Minimal_3RPS_Radial_RevC_Fusion360.zip`이다. 설계 기준은 `design_basis/minimal_radial_revC_2026-08-31.md`, 구조 BOM은 `procurement/minimal_radial_revC_structural_bom_2026-08-31.md`, Fusion 조립 순서는 `outputs/minimal_radial_revC/FUSION360_IMPORT_AND_ASSEMBLY_GUIDE.md`에 있다. 하부 허브 가공파일은 `outputs/minimal_radial_revC/fabrication/LOWER_HUB_280x220x10_revC.dxf`와 홀표 CSV다.

최종 Rev C ZIP은 42 entries, 5,786,238 bytes, CRC 통과, SHA-256 `CBC470619C80B170F4E4173C9BBDD392768A2A5A8770A2B45118C1395F936E9C`다.

상태는 `DIGITAL_CORE_ASSEMBLY_PASS_EYE_WIDTH_AND_STOP_MOUNT_OPEN`, `fabrication_release=false`, `purchase_release=false`다. 다음 다섯 항목을 닫기 전에는 전량 발주나 제작 릴리스로 해석하지 않는다.

1. LM4075OE 납품품 아이 축방향 폭과 공급자 STEP.
2. LMB-10 핀과 포지티브 리테이너의 포함 여부/실치수.
3. M6×50 상부 조인트의 실제 와셔·심 적층과 공구 접근.
4. 독립 스토퍼 포획판의 프로파일 장착 스탠드오프와 정확 SKU.
5. 하부 허브 1차품의 홀/탭 위치, 렌치 접근과 LMB 한 축 실조립.

이번 시행착오도 보존했다. 첫 Rev C 렌더에서 TB306 머리가 전역 원점을 기준으로 회전해 공중에 떠 보였고, 로컬 원점 회전 후 위치 이동 순서로 수정했다. 브라켓 체결홀도 솔리드에 추가했다. 분해도 제목이 `NEUTRAL`로 출력되던 문제와 조립도 제목 가림은 출력 라벨과 카메라 스케일을 수정했다. 이 수정 후 시각 QA와 자동 검사를 다시 수행했다.

## 2026-08-31 이전 상태 — Rev B 조립성 재감사 기각

사용자가 3D 조립이 이상해 보인다고 지적한 뒤 브라켓 체결축과 액추에이터 핀축을 다시 감사했다. 기존 `DIGITAL_ASSEMBLY_PASS` 판정은 철회했으며, 현재 상태는 `REJECTED_ASSEMBLY_GEOMETRY_REDESIGN_REQUIRED`, `fabrication_release=false`, `purchase_release=false`다.

차단 오류는 세 가지다. (1) 동일 평면 프레임 코너에서 4035/DCB3025의 두 다리는 세로로 서고 체결축은 수평 X/Y 두 방향이어야 하지만 CAD의 두 볼트가 모두 수직이다. (2) 상부 PHS6 단측 오프셋 14.5 mm를 상부에만 적용해 0 deg 자세의 액추에이터축-핀축 직각오차가 3.549 deg, 검토자세 최대가 5.447 deg다. (3) 지지점은 0/90/180 deg, 간격 90/90/180 deg여서 요청한 120 deg 방사형이 아니다.

자동 재감사는 `calculations/revb_assembly_reaudit.py`, 결과는 `outputs/minimal_profile_only_revB/verification/revB_assembly_reaudit_2026-08-31.json`, 상세 판단은 `design_basis/revB_assembly_reaudit_2026-08-31.md`에 있다. Rev B STEP/ZIP/BOM은 실패 재현용으로만 남기며 발주·제작에 사용하지 않는다. 후속 Rev C는 위 최신 절과 같이 실제 체결축과 작은 하부 허브판을 사용해 이 세 오류를 수정했다.

기각 안내로 다시 만든 Rev B ZIP은 34 entries, CRC 통과, SHA-256 `5986A3EEF958F624DF3E94DE1B76CFDB847E62FFE8A973BCBB30494DF1CFEC48`이다.

## 2026-08-31 이전 판정 — 프로파일 전용 3-RPS Rev B (철회됨)

Rev A 공급자 치수 감사에서 실패한 LMB-10 측면장착, A2/A3 사선 4035 접합, PHS6 높이 15 mm 누락과 297 mm 비표준 절단을 모두 수정했다. Rev B는 하부 직교 4040 격자와 상부 직교 3030 격자를 쓰며, 모든 구조 연결은 90도 카탈로그 브래킷이다. LMB-10은 프로파일 상면 한 슬롯에 두 M8 고정부를 36 mm 간격으로 놓고, PHS6 링 중심은 상부 프로파일 하부면에서 35 mm 떨어진다.

당시 Fusion 360 전달물은 `output/Minimal_3RPS_ProfileOnly_Fusion360_revB.zip`이었다. 6개 자세 STEP, 폭발 STEP, 4개 서브어셈블리 STEP, A1 조인트 상세 STEP, 렌더 6개, 절단표, 기계 BOM, 체결표, 검증 JSON과 설계·구매 지원문서가 포함됐다. 이후 같은 ZIP은 기각 안내를 포함하도록 재패키징했다.

핵심 수치는 700×700×296 mm 접힘 포락체, Z 0~50 mm, pitch/roll 각각 +/-3 deg, 요구 액추에이터 핀 길이 225.002~280.344 mm다. LM4075OE 이론 205~305 mm에 수축/신장 여유 20.002/24.656 mm가 있다. 대표 6자세에서 액추에이터 몸체/아이와 프레임·브래킷·LMB 교차체적은 0 mm3다. 독립 스토퍼 계산 여유는 7.818 mm, actuation Jacobian은 full rank, 전용 시험 10개와 205-solid STEP 역수입이 통과했다.

당시 절단표는 4040 700×2, 620×3, 300×1과 3030 700×2, 640×4였다. 이 수량과 당시 나비엠알오 SKU는 모두 기각된 Rev B에만 해당한다.

당시 상태 문자열은 `DIGITAL_ASSEMBLY_PASS_EYE_WIDTH_AND_STOP_CATALOG_OPEN`이었으나 후속 재감사로 철회됐다.

## 2026-08-30 이전 최소안 배경 — 위 Rev B 다음으로 참고

사용자는 기존 제품화 수준 설계가 과도하다고 판단하고, 중앙 카단 없이 수직 액추에이터 3개와 조인트·판·알루미늄 프로파일을 조립하는 최소 PoC로 방향을 재정의했다. 따라서 아래의 `RADIAL_3_CLEAN`, 중앙 키드 가이드/카단, Firgelli/DIHOOL 및 NAVIMRO 제작 CAD 기록은 역사 자료이며 현재 구매·조립 기준이 아니다.

현재 활성 기준은 `procurement/detailed_purchase_bom_2026-08-30.md`와 `procurement/minimal_3actuator_poc_purchase_plan_2026-08-30.md`이다. 구조는 3-RPS, 액추에이터는 2026-08-31 사용자가 선택한 LM4075OE-1075 24 V/100 mm/5 V encoder, 제어는 DMD-150 3개 + Arduino Mega 2560 + WT901C/UART다. 상단 `LMB-10 → PF30/BA01K13` 직렬안은 폐기하고, PHS6 구면 로드엔드를 액추에이터 아이에 직접 연결하는 1축 선행 목업으로 변경했다.

판매 상세 이미지와 제공 STEP에서 LM4075OE 베이스 아이 두께 약 18.00 mm, LMB-10 내부 폭 20 mm, 내장 종단 리미트, 엔코더 배선, 24 V 부하전류 1.5 A를 확인했다. WT901C MCU 케이블 포함과 24 V/5 A 어댑터의 5.5/2.5 mm center-positive 및 AC 코드 옵션도 확인했다. 현재 남은 발주 게이트는 **PHS6 단측 M6 연결의 1축 실물조립**과 **기동·stall 전류 및 24 V/5 A 어댑터 적합성 실측**이다. 새 최소형 개념은 Phase 1 예비 상태이며 제작 승인 전이다. 전체 변경·검증 이력은 `logs/minimal_3actuator_poc_progress_2026-08-30.md`를 먼저 참조한다.

100 mm stroke안은 공통 Z 승강을 50 mm로 조정한다. 반경 250 mm, 기준 핀 간격 230 mm, pitch/roll 각각 +/-3 deg의 27개 자세 스크린에서 요구 길이는 212.137~297.864 mm이고, 이론 205~305 mm 범위에 수축/신장 여유 7.137/7.136 mm로 들어온다. 계산은 `calculations/minimal_3rps_100mm_screen.py`에서 재현한다. 합판은 외관 선호로 구매 보류이며, 프로파일 구조와 알루미늄 패널/선택적 아크릴 커버 구성 확정 후 구조 BOM을 교체한다.

## 이전 방향의 인수인계 기록 — 현재 구매 기준으로 사용하지 않음

작성일: 2026-08-24 / 최종 갱신: 2026-08-30  
작업 위치: `C:\Users\Kangmin\OneDrive\2. 연구실\지원사업\BIZ-Lab 창업클럽\수평유지장치설계 프로젝트`

### 1. 2026-08-27 당시 한 줄 상태

Phase 0 재검토와 파라미터 스크리닝을 마친 뒤 2026-08-26 사용자가 정확히 `APPROVE CONCEPT`를 입력했다. 첫 상세안의 대형 중앙 짐벌/스톱 카트리지 형상은 사용자 디자인 피드백으로 비선호 보관안이 됐다. 현재 활성 CAD는 `RADIAL_3_CLEAN`: 세 액추에이터가 120° 방사형 주 구조를 이루고, 작은 중앙 키드 가이드/카단은 X/Y/Yaw 구속만 담당한다. 상세 CAD 진행은 승인됐지만 제작 릴리스는 아직 아니다.

현재 결론은 다음과 같다.

```text
PHASE 0 DIRECTION REVIEWED
PARAMETER TABLE REVISED AFTER FEEDBACK
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
ALUMINUM PROFILE CART RECEIVER DIRECTION RECORDED
CR-01-H2 CONNECTOR TOPOLOGY SCREENED
CR-01-H3 CONNECTOR STACK RULES SCREENED
CR-01-H4 HARDWARE SEED SCREENED
JNT-BR-01 HRT8E BRACKET SEED SCREENED
YAW-A AXIS ORDER AND STOP ENVELOPE SCREENED
WS-01-H20 270 MM WORKSPACE CANDIDATE SCREENED
APPROVE CONCEPT RECEIVED 2026-08-26
PHASE 2 DETAILED CAD BASELINE GENERATED
RADIAL_3_CLEAN ACTIVE DESIGN
HRT8E 18 MM ACTUATOR JOINT DETAIL SEED GENERATED
PHASE 2 REVIEW RENDER PACK GENERATED
LS-01M STATIC-BENCH TWIN-ROD MECHANICAL STOP PACKAGE GENERATED
FIRGELLI MB21 FIXED DATUM AND FRONT-CLEVIS MOVING DATUM APPLIED
EXTERNAL D4N/CAM PACKAGE ARCHIVED
JNT-CG-01 FACTORY-EYE NESTED-GIMBAL MOCK-UP SEED GENERATED
LARGE CENTRAL GIMBAL/CARTRIDGE VARIANT ARCHIVED
BENCH EVIDENCE PENDING BEFORE DESIGN FREEZE
NOT APPROVED FOR FABRICATION
```

상세 CAD는 계속 진행할 수 있다. 다만 실제 중앙 가이드/요크/브래킷/리시버 접촉 증거, 질량 분리, 12 V PoC 전원 차단·전류보호, JNT-CG-01 실측 목업이 남아 있으므로 전체 6개 조인트의 치수공차 제작도로 올리면 안 된다.

## 2. 반드시 지켜야 할 프로젝트 게이트

- 작업 범위는 수평유지/리프팅 상부모듈, 범용 하부 장착 인터페이스, 기계식 카트 결합 인터페이스로 제한한다.
- AMR, AGV, 바퀴, 캐스터, 구동부, 내비게이션, 로봇팔, 카트 본체는 설계하지 않는다.
- 상부 플랫폼의 허용 자유도는 Z, Pitch, Roll이다.
- X, Y, Yaw는 기계적으로 구속해야 한다.
- 전기식 리미트와 독립 기계식 스토퍼는 분리해야 한다.
- 카트 고정은 기계식 위치결정/래칭이 기본이며, 전자석은 1차 고정수단으로 쓰지 않는다.
- 이미지에서 실제 카트 치수, 질량, 재질, 홀 위치를 추정하지 않는다.
- 사람 운송용 적합성, 인증, 현장 안전성을 주장하지 않는다.
- 모든 기존 Phase 2 CAD/렌더/도면성 산출물은 `PRELIMINARY - NOT APPROVED FOR FABRICATION`이다.
- `APPROVE CONCEPT`는 Phase 2 상세 CAD 진입 승인이다. 실물 검증이나 제작 적합성 승인으로 해석하지 않는다.

## 3. 폴더별 역할

| 폴더/파일 | 역할 |
|---|---|
| `AGENTS.md` | Codex 작업 규칙과 범위/Phase 게이트 |
| `references/` | 요구사항 원문, PDF, 참고 이미지 |
| `requirements/` | 최신 요구사항, 하드 제약, 목표, 미확정 입력 |
| `concepts/` | Phase 1 기구 대안 비교 |
| `cad/` | Phase 2 예비 파라메트릭 CAD 코드 |
| `calculations/` | 운동학, 하중, 스윕, 전원, 비용 계산 |
| `web_research/` | 웹 조사 출처 레지스터와 부품/표준 조사 기록 |
| `design_basis/` | Phase 0 파라미터 선정 근거와 결정표 |
| `design_basis/user_confirmed_scope_2026-08-25.md` | 10 kg 적재/10 kg 카트/250~300 mm/+/-3 deg/쉬운 제작 우선 사용자 확인 기준 |
| `design_basis/cart_profile_receiver_concept_2026-08-25.md` | 알루미늄 프로파일 기반 카트 리시버 예비 개념 |
| `design_basis/cart_profile_receiver_layout_screen.md` | CR-01 알루미늄 프로파일 리시버 배치/질량/하중 스크리닝 |
| `design_basis/cart_receiver_hardpoint_screen.md` | CR-01-H1 locator/rest pad/latch keeper 하드포인트 스크리닝 |
| `design_basis/cart_receiver_connector_topology_screen.md` | CR-01-H2 슬롯너트/백킹플레이트/포지티브 스토퍼 토폴로지 스크리닝 |
| `design_basis/cart_receiver_connector_detail_screen.md` | CR-01-H3 하드포인트별 연결 스택/서비스 접근성 스크리닝 |
| `design_basis/cart_receiver_hardware_selection_screen.md` | CR-01-H4 조립·목업용 하드웨어 시드 스크리닝 |
| `design_basis/guide_mobility_review.md` | 중앙 가이드/조인트 자유도 재검토 |
| `design_basis/joint_candidate_screen.md` | 액추에이터 조인트/중앙 카단 후보 스크리닝 |
| `design_basis/joint_detail_screen.md` | 조인트 브래킷 하중경로 및 중앙 yaw 토크 스크리닝 |
| `design_basis/actuator_bracket_package_screen.md` | JNT-BR-01 HRT8E형 이중전단 브래킷 시드 스크리닝 |
| `design_basis/actuator_joint_detail_cad_2026-08-27.md` | 공식 HRT8E 외형을 반영한 18 mm 요크/부싱/핀 유지장치 상세 CAD 기준 |
| `design_basis/static_bench_minimal_variant_2026-08-27.md` | 정지형 저속 시험대 최소 구성과 삭제/유지 범위 |
| `design_basis/actuator_limit_package_cad_2026-08-27.md` | LS-01M 쌍봉식 기계 스톱 상세 CAD 기준 |
| `design_basis/factory_clevis_gimbal_seed_2026-08-27.md` | JNT-CG-01 공장 아이 중첩 짐벌 목업 시드 |
| `design_basis/firgelli_mount_datum_review_2026-08-27.md` | 공식 actuator/MB21/MB20/MB17 STEP 해시, 고정·이동 datum 결정, clevis adapter 미해결점 |
| `design_basis/central_yaw_path_comparison.md` | 중앙 yaw 토크 경로 후보 비교 |
| `design_basis/yaw_a_architecture_definition.md` | YAW-A 선호 구조의 후보 파라미터 정의 |
| `design_basis/yaw_a_gimbal_kinematic_definition.md` | YAW-A 축 순서, yaw 구속, +/-7 deg 스토퍼 정의 |
| `design_basis/combined_workspace_operating_window.md` | WS-01-H20 통합 작업영역/가이드 후보 |
| `design_basis/travel_limit_and_stop_strategy.md` | 전기 리미트/기계식 스토퍼 분리 전략 |
| `design_basis/pre_cad_verification_plan.md` | CAD 전 V-01~V-06 물리 검증 기준 |
| `outputs/phase2/` | 기존 Phase 2 예비 엔지니어링 리포트/BOM |
| `outputs/phase2/actuator_limit_package_summary.md` | LS-01 위치·정적 스크리닝·미해결 검증 요약 |
| `outputs/cad/` | 기존 예비 STEP/GLB/STL/DXF 산출물 |
| `outputs/renders/` | 기존 예비 렌더 이미지 |
| `outputs/reports/phase0_summary.md` | Phase 0 요약 |
| `outputs/reports/phase2_review_render_pack.md` | 상판 제거 내부도, 정·측·평면도, 분해도 및 번호 조립도 안내 |
| `outputs/reports/final_candidate_parameter_pack.md` | 사용자가 판단할 최종 후보 파라미터 팩 v1.1 |
| `outputs/reports/cart_profile_receiver_summary.md` | 카트 리시버 CR-01 요약 |
| `outputs/reports/cart_receiver_hardpoint_summary.md` | 카트 리시버 CR-01-H1 하드포인트 요약 |
| `outputs/reports/cart_receiver_connector_summary.md` | 카트 리시버 CR-01-H2 연결/스토퍼 요약 |
| `outputs/reports/cart_receiver_connector_detail_summary.md` | 카트 리시버 CR-01-H3 연결 스택/접근성 요약 |
| `outputs/reports/cart_receiver_hardware_selection_summary.md` | 카트 리시버 CR-01-H4 하드웨어 시드 요약 |
| `outputs/reports/actuator_bracket_package_summary.md` | JNT-BR-01 액추에이터 브래킷 요약 |
| `outputs/reports/joint_candidate_summary.md` | 조인트 후보 스크리닝 요약 |
| `outputs/reports/joint_detail_summary.md` | 조인트 상세 스크리닝 요약 |
| `outputs/reports/central_yaw_path_summary.md` | 중앙 yaw 경로 비교 요약 |
| `outputs/reports/yaw_a_architecture_summary.md` | YAW-A 후보 파라미터 요약 |
| `outputs/reports/yaw_a_gimbal_kinematic_summary.md` | YAW-A 축 순서/스토퍼 요약 |
| `outputs/reports/combined_workspace_operating_window_summary.md` | WS-01-H20 작업영역 요약 |
| `outputs/reports/travel_limit_and_stop_summary.md` | 리미트/스토퍼 요약 |
| `logs/feedback_recheck_2026-08-24.md` | 외부 피드백 반영 및 승인 보류 기록 |
| `logs/` | 작업 이력, 환경 설정, 시행착오 기록 |
| `wheelhouse/` | 오프라인 Python wheel 패키지 |
| `vendor/python/` | 로컬 Python 의존성 설치 위치 |

## 4. 기존 작업 진행 흐름

### Phase 1: 개념 비교

세 가지 기구 대안을 비교했다.

- A: 3점 독립 리프팅 + 중앙 키드 텔레스코픽/Cardan 가이드
- B: 4점 액추에이터 방식
- C: Z축 리프트와 Pitch/Roll 분리형 구조

결론은 대안 A를 개념 방향으로 유지하는 것이다. 이유는 3점이 상부 평면을 유일하게 결정해 4점 과구속을 피하고, 낮은 적층 높이와 부품 수를 기대할 수 있기 때문이다. 단, 중앙 가이드가 X/Y/Yaw를 구속하면서 Pitch/Roll을 허용하는 실제 기구는 아직 해결되지 않아 `critical_open` 상태다.

관련 파일:

- `concepts/decision_matrix.md`
- `concepts/mechanism_A_three_point.md`
- `concepts/mechanism_B_four_point.md`
- `concepts/mechanism_C_gimbal.md`

### Phase 2: 예비 CAD 및 산출물 생성

다른 컴퓨터에서 이미 Phase 2 예비 CAD가 진행되어 있었다. 주요 구성은 다음과 같다.

- 3개 방사형 사선 Firgelli Hall 액추에이터
- 중앙 키드 텔레스코픽 슬라이드 + Cardan 조인트
- HFS8-4040 알루미늄 프레임 + 15 mm 아크릴 상판 + 금속 하중분산판
- 원뿔형 기계식 위치결정핀 + pull-action 래치 4개
- 전기 리미트와 별도의 기계식 스토퍼 개념

생성된 산출물:

- `outputs/cad/step/`: 예비 STEP 조립체
- `outputs/cad/glb/`: 중립 상태 GLB
- `outputs/cad/stl/`: IMU 브래킷, 케이블 가이드
- `outputs/cad/dxf/`: 예비 2D 프로파일
- `outputs/renders/`: 예비 렌더
- `outputs/phase2/phase2_engineering_report.md`
- `outputs/phase2/phase2_bom.csv`

단, 최신 지침상 이 산출물들은 제작 승인용이 아니며, Phase 0 파라미터 승인 전에는 상세 CAD로 발전시키면 안 된다.

### Phase 0 재정렬: 웹 조사 기반 파라미터 선정

사용자가 추가한 지침에 따라 임의값 입력을 중단하고, 공식 표준/제조사 데이터/공식 판매처 기반으로 파라미터를 다시 정리했다.

주요 산출물:

- `web_research/source_register.csv`
- `web_research/standards_review.md`
- `web_research/actuator_sources.md`
- `web_research/latch_sources.md`
- `web_research/frame_sources.md`
- `web_research/sensor_sources.md`
- `web_research/procurement_sources.md`
- `design_basis/design_basis_report.md`
- `design_basis/parameter_decision_table.csv`
- `design_basis/component_candidate_table.csv`
- `design_basis/source_to_parameter_matrix.md`
- `design_basis/user_confirmed_scope_2026-08-25.md`
- `design_basis/cart_profile_receiver_concept_2026-08-25.md`
- `design_basis/cart_profile_receiver_layout_screen.md`
- `design_basis/cart_receiver_hardpoint_screen.md`
- `design_basis/cart_receiver_connector_topology_screen.md`
- `design_basis/cart_receiver_connector_detail_screen.md`
- `design_basis/cart_receiver_hardware_selection_screen.md`
- `outputs/reports/phase0_summary.md`
- `outputs/reports/final_candidate_parameter_pack.md`
- `outputs/reports/cart_profile_receiver_summary.md`
- `outputs/reports/cart_receiver_hardpoint_summary.md`
- `outputs/reports/cart_receiver_connector_summary.md`
- `outputs/reports/cart_receiver_connector_detail_summary.md`
- `outputs/reports/cart_receiver_hardware_selection_summary.md`

## 5. Phase 0 재점검 후 파라미터 요약

| 항목 | 현재 제안값 | 상태 |
|---|---:|---|
| PoC 정격 적재 | 10 kg 추가 자재 적재 | 사용자 확인 |
| 적재 스윕 | 5, 10 kg 중심; 20 kg은 보관 민감도 | 분석 기준 |
| 카트 질량 | 10 kg 1차 기준; 20/30 kg은 보관 민감도 | 사용자 확인, 새 카트 설계 후 재확인 |
| 연결 전 장치 높이 | 250~300 mm | 사용자 확인, 카트는 이 높이에 맞춰 설계 가능 |
| 상부 모듈 이동 질량 | 15, 22 kg | 단순 PoC 스윕 기준, 실제 BOM 필요 |
| 설계계수 기준 | 1.5 | 내부 PoC 스크리닝 가정, ISO 근거 아님 |
| 설계계수 민감도 | 2.0 | 민감도 검토용 |
| 수직 리프트 | 100 mm | 목표값, 전 영역 보장 아님 |
| Pitch/Roll 기준 | +/-3 deg | 사용자 확인, 복합 작업공간/가이드 검증 필요 |
| Pitch/Roll 확장 | +/-5 deg | 현 요구 아님, 미래 확장 옵션 |
| Pitch/Roll 스트레스 케이스 | +/-8 deg | 보관 민감도 |
| 액추에이터 | Firgelli F-SD-H-450-12V-8in Hall | 저하중 PoC 선호 후보, 구매 확정 아님 |
| 액추에이터 업그레이드 | 단순 10 kg/+/-3 deg 패키지가 실패할 때만 | 4000 N 고정 기준 삭제 |
| 프레임 | MISUMI HFS8-4040 | 후보, 접합부 강성 미검증 |
| 카트 리시버 제작방향 | CR-01 2-레일 알루미늄 프로파일 키트 + CR-01-H1 하드포인트 + CR-01-H2 연결/스토퍼 토폴로지 + CR-01-H3 연결 스택 + CR-01-H4-S1 목업 하드웨어 시드 | 후보, 정확한 슬롯너트/백킹플레이트/인서트/fit/체결/래치/센서 상세 미확정 |
| 카트 결합 | 테이퍼 위치결정핀/받침 + 기계식 래치 | 원칙 유지, 래치 형번/예압 미확정 |
| 센서 | BNO085 PoC, WT901C 옵션 | 후보 |
| 전원 | Firgelli 유지 시 12 V PoC 기준 | 24 V는 액추에이터 재선정 시에만 |

## 6. 주요 계산 결론

- 현재 Firgelli 450 lbf 액추에이터의 정격은 약 2002 N이다.
- 사용자 확인 1차 기준인 10 kg 자재, 10 kg 카트, 22 kg 이동 구조, DF 1.5, 50 mm 편심, +/-3 deg 조건에서는 최대 액추에이터 축력이 약 618 N으로 450 lbf 후보 정격 대비 약 3.24배 여유가 있다.
- DF 2.0/50 mm 편심 민감도는 약 824 N, DF 1.5/100 mm 편심 민감도는 약 729 N으로 둘 다 Firgelli 450 lbf 후보 정격을 통과한다.
- 30 kg 카트 보관 민감도에서는 최대 액추에이터 축력이 약 912 N이며, 이 경우도 약 2.19배 여유가 있다.
- 15 mm 액추에이터 끝단 여유를 요구하면, 현재 CAD 형상에서 0-100 mm 리프트 전 구간의 최소 대칭 Pitch/Roll 허용각은 약 3.5 deg다.
- 최저 높이에서 +/-3 deg, 15 mm 여유 조건은 실효 여유가 약 2.5 mm밖에 없어 승인값으로 보기에는 빡빡하다.
- 최저 높이에서 +/-5 deg, 15 mm 여유 조건은 실패하지만, 이는 현 요구사항이 아니라 미래 확장 옵션이다.
- 액추에이터 하부 조인트 편차가 가장 크다. 2 deg 여유를 더하면 +/-3 deg 기준에는 약 13 deg 이상의 조인트 허용각이 필요하다.
- PHSOSM8은 현재 1차 액추에이터 조인트 스크리닝에서 각도/정하중 여유가 모두 부족하다.
- HRT8E-style M8 rod end는 +/-3 deg 기준 조건부 후보로 둔다. 공식 8/23/11 mm 외형을 반영한 JNT-BR-01 상세 시드는 5.29 kN axial static 기준, ball center를 지나는 8 mm double-shear pin/lug, 18 mm supported span, 교체형 부싱과 유지 핀 포락체를 사용한다. 실제 14 deg articulation 무간섭은 여전히 V-01로 증명해야 한다.
- MISUMI RBLD8 계열 고각도 링크볼은 예비안으로 유지한다.
- 중앙 카단은 yaw를 전달하는 U-joint/gimbal 계열이 필요하다. Ruland 스타일 U-joint는 각도 기준 참고군일 뿐, 토크/백래시/축하중 검토 전에는 선정품이 아니다.
- 조인트 상세 스크리닝 결과, 핀 전단과 러그 베어링보다 나사부 외팔보 굽힘이 먼저 문제가 된다. 액추에이터 하중선은 볼 중심을 지나야 하고, 나사부를 스페이서처럼 쓰면 안 된다.
- 이전 보수적 중앙 yaw 토크 스크린은 약 125 Nm 운전 토크와 약 250 Nm 피크/설계 토크였지만, 새 사용자 확인 PoC 1차 기준에서는 설계 yaw 토크가 약 16 Nm로 내려간다. 30 kg 카트 보관 민감도에서는 약 24 Nm다.
- 50 x 3 mm 중앙 사각 가이드 튜브 자체의 1차 비틀림 응력은 낮게 나오지만, Cardan/gimbal/키/체결부/백래시 경로는 여전히 미해결이다.
- 중앙 yaw 경로 비교 결과, 현재 선호 방향은 YAW-A다. 즉 keyed square telescoping guide가 yaw 토크를 전달하고, 2축 gimbal은 pitch/roll을 허용하되 yaw 토크 경로를 끊지 않아야 한다.
- Ruland US32급 대형 U-joint는 저하중 PoC 기준에서 과한 예비안이다. 16 mm ball spline은 저하중에서는 토크만으로 탈락하지 않지만, 패키징/조달/피치롤 절연 복잡도가 있어 예비안으로만 둔다.
- YAW-A 후보 파라미터는 gimbal 8 deg 설계각/10 deg 하드스톱, yaw total clearance 0.2 mm target/0.3 mm max, anti-yaw contact 10 mm 폭과 80 mm 최소 겹침, yoke couple arm 50 mm, pin 10 mm, lug 8 mm이다. 1차 기준 접촉력은 약 328 N, 접촉압은 약 0.41 MPa다.
- 새 저하중 인터페이스 스크린에서 기준 수직 설계하중은 약 618 N, 최악 인터페이스 모멘트는 약 108 Nm, 가이드핀 전단 설계하중은 약 154 N, 4개 래치 기준 래치당 uplift는 약 31 N이다.
- 카트 리시버 CR-01 스크린에서는 760 mm x 560 mm 리시버 존에 760 mm HFS8-4040 2개를 쓰는 2-레일 키트를 우선 후보로 둔다. placeholder 하드포인트 포함 질량은 약 4.50 kg이다.
- HFS8 사각 서브프레임 예비안은 약 6.43 kg으로, 10 kg 빈 카트 목표에서는 무거운 예비안이다.
- CR-01의 4개 받침 패드 스크린에서는 active worst 조건에서 최대 패드하중 약 331 N, 최소 패드하중 약 81 N으로 모두 압축 상태를 유지한다. 520 mm locator span 기준 yaw couple force는 약 32 N이다.
- CR-01-H1 하드포인트 스크린에서는 12 mm locator/8 mm local insert 베어링 약 1.94 MPa, 40 x 30 mm rest pad 접촉압 약 0.28 MPa, 5 mm latch keeper bearing 약 0.25 MPa(4 latch) 또는 0.49 MPa(2 latch), 6 mm local tab bending 약 16 MPa로 bulk strength는 낮게 나온다.
- 단, 프로파일 슬롯 마찰은 최종 위치결정 기준으로 쓰면 안 된다. mock-up 후 dowel/keyed plate/shoulder block/positive stop 중 하나를 넣어야 한다.
- CR-01-H2 연결/스토퍼 스크린에서는 slot friction only를 최종 위치결정 방식에서 탈락시켰고, 선호안은 두 M8급 T-slot fastener로 조정/클램프한 뒤 shoulder/key/positive stop으로 최종 전단·yaw 기준을 잡는 방식이다. 현재 demand 약 186 N에서 positive stop bearing은 약 0.58 MPa, 6 mm tab/25 mm cantilever bending은 약 19 MPa, optional 6 mm dowel shear는 약 6.6 MPa로 낮다.
- CR-01-H3 연결 스택 스크린에서는 master locator는 X/Y 고정, slotted secondary locator는 Y만 고정하고 X를 풀며, rest pad는 Z seating만, latch keeper는 preload/uplift만 담당하도록 역할을 분리했다. Profile wall/stop bearing은 3배 local factor에서 약 1.74 MPa, slot nut clamp contact screen은 약 18.5 MPa다. 30 cycle mock-up 후 shift >0.2 mm 또는 torque relaxation >20%면 backing plate/stiffer stack을 추가한다.
- CR-01-H4-S1은 H3 역할을 조립 가능한 목업 하드웨어로 좁혔다. Master는 12 mm removable bushing과 40 x 8 mm replaceable stop, secondary는 X를 release하는 20 mm seed slot/diamond locator, rest pad는 40 x 30 mm shim seat, latch keeper는 5 mm steel + 별도 mechanical secondary lock이다. 3배 local screen에서 bushing bearing 약 5.8 MPa, stop bearing 약 1.7 MPa / bending 약 32.7 MPa, optional 6 mm dowel shear 약 19.7 MPa, rest pad contact 약 0.8 MPa다.
- JNT-BR-01 HRT8E bracket screen은 actuator-axis capacity를 catalog 5.29 kN axial static limit으로 정정했다. Active +/-3 deg/DF 2.0/100 mm eccentricity force 약 972 N에서 2x static screen demand는 약 1.94 kN, axial margin은 약 2.72x다. Required articulation은 약 12.94 deg라 14 deg catalog value까지 약 1.06 deg만 남으므로, 14 deg full-envelope physical no-contact check가 유지 조건이다.
- 래치 검토상 래치는 좌굴/수평 전단을 담당하면 안 되며, 위치결정핀/받침/가이드가 전단과 X/Y/Yaw 구속을 담당해야 한다.
- 전원 예비 검토상 현재 Firgelli 12 V 후보를 유지하면 12 V 약 23 A / 273 W 이상급이 1차 기준이며, 24 V는 액추에이터 재선정 시에만 검토한다.
- 비용 예비 스크린은 저가 케이스가 약 360만 원, 목표 케이스가 약 615만 원으로 나왔다. 400만 원 제한 내에서는 부품 등급/가공 범위/동시구동 요구를 조정해야 한다.

## 7. 이 컴퓨터에서 완료한 환경 설정

이 PC에서는 `vendor/python` 의존성이 불완전했다. `wheelhouse/`의 로컬 wheel을 사용해 CadQuery, ezdxf, matplotlib, pillow, vtk 등을 `vendor/python`에 재설치했다.

실행한 핵심 명령:

```powershell
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install --no-index --find-links wheelhouse --target vendor\python --upgrade cadquery ezdxf matplotlib pillow vtk
```

또한 `scripts/run_phase2.ps1`에 다른 컴퓨터 사용자 경로가 하드코딩되어 있어, 현재 PC에서도 동작하도록 Python 경로 자동 탐색 방식으로 수정했다.

현재 재생성 명령:

```powershell
& .\scripts\run_phase2.ps1
```

검증 결과:

- Phase 2 재생성 성공: CAD 파일 12개, 렌더 9개 생성 확인
- 기존 단위 테스트와 새 조인트/중앙 yaw 경로/YAW-A 구조/사용자 확인 기준 스크리닝 테스트 포함 36개 통과
- Phase 0 계산 스크립트 실행 성공

## 8. 시행착오와 수정 이력

1. `vendor/python` 의존성 누락
   - 증상: CadQuery/ezdxf 관련 import가 정상 동작하지 않았다.
   - 조치: `wheelhouse/` 로컬 패키지로 `vendor/python`을 재설치했다.

2. `scripts/run_phase2.ps1`의 사용자 경로 하드코딩
   - 증상: 다른 컴퓨터의 `C:\Users\Kangmin\...` 경로를 참조해 현재 PC에서 바로 실행할 수 없었다.
   - 조치: `CODEX_PYTHON`, Codex bundled Python, 로컬 Python, 시스템 `python` 순서로 자동 탐색하도록 수정했다.

3. 캐시/폰트 경로 권한 경고
   - 증상: ezdxf/matplotlib 실행 중 사용자 홈 캐시나 Windows Fonts 접근 경고가 있었다.
   - 조치: 작업 폴더 안에 `.cache`, `.mplcache`를 만들고 실행 시 해당 경로를 사용하도록 했다.

4. 참고 이미지와 최신 요구사항의 충돌
   - 과거 참고 이미지에는 100 kg 적재, Yaw, 특정 외형 수치처럼 보이는 내용이 있었지만, 최신 요구사항은 이미지에서 실제 치수/질량/홀 위치를 추정하지 말라고 한다.
   - 조치: 100 kg은 채택하지 않고 `unresolved`로 남겼다. 최신 파라미터 지침의 5/10/20 kg 스윕을 우선했다.

5. 기존 Phase 2 산출물과 Phase 게이트의 충돌 가능성
   - 이미 상세 CAD 형태의 산출물이 존재하지만, 최신 지침은 파라미터 승인 전 상세 CAD 진행을 막는다.
   - 조치: 기존 산출물은 모두 예비/비제작용으로 표기했다. 이후 외부 피드백 반영으로, 새로운 상세 CAD 수정은 중앙 가이드/복합 작업공간/질량/전원/제어안전 재검토와 새 승인 패키지 이후로 미뤘다.

6. `calculations/interface_moments.py`의 오래된 질량 가정
   - 증상: Phase 0 실행 중 기존 125 kg 기준 출력이 남아 최신 5/10/20 kg 스윕과 맞지 않았다.
   - 조치: payload/cart/상부질량 스윕 기반으로 수정했다.

7. `calculations/power_budget.py`의 전원 문구 불일치
   - 증상: 계산상 권장 전류는 23.75 A, 570 W인데 문구가 20 A급 권장처럼 읽혔다.
   - 조치: 3축 동시 구동 시 24 V 25 A / 600 W급, 20 A급은 제한 조건 필요로 수정했다.

8. `rg --files` 출력 과다
   - 증상: `vendor/python`과 wheel 파일이 많아 전체 파일 목록이 매우 길었다.
   - 조치: 이후 확인은 필요한 폴더로 범위를 좁혀 수행했다.

9. 외부 피드백 반영 후 승인 보류
   - 증상: 기존 Phase 0 표가 문서 구조는 좋았지만, 부품/치수 선정이 너무 일찍 `SELECTED`로 표시되어 있었다.
   - 조치: `parameter_decision_table.csv`, `component_candidate_table.csv`, `design_basis_report.md`, `phase0_summary.md`를 수정했다. 중앙 가이드를 `critical_open`으로 바꾸고, 복합 작업공간/질량분리/전원아키텍처/제어안전 항목을 추가했다.

10. 중앙 가이드 모빌리티 분석
   - 증상: `central keyed telescoping guide plus Cardan` 문구만으로는 실제 기구가 걸리지 않는지 알 수 없었다.
   - 조치: `calculations/mobility_analysis.py`, `design_basis/guide_mobility_review.md`, `outputs/reports/guide_mobility_summary.md`를 추가했다.
   - 결론: yaw를 전달하는 2축 Cardan을 쓰면 이론상 Z/Pitch/Roll 3자유도가 남지만, rigid keyed slide를 상부판에 직접 고정하면 Pitch/Roll이 막힌다. 현재도 실제 조인트 형번, Cardan 축, side-load, guide overlap 여유가 미해결이므로 `critical_open` 유지.

11. 조인트 후보 스크리닝
   - 증상: 중앙 가이드 모빌리티 분석만으로는 실제 구매 가능한 조인트가 각도와 하중을 만족하는지 알 수 없었다.
   - 조치: 공식/제조사 근거를 추가하고 `calculations/joint_candidate_screen.py`, `design_basis/joint_candidate_screen.md`, `outputs/reports/joint_candidate_summary.md`를 작성했다.
   - 결론: PHSOSM8은 1차 액추에이터 조인트에서 제외, HRT8E는 +/-3 deg 기준 후보, 고각도 링크볼 계열은 +/-5 deg 확장 후보로 유지한다. 중앙 카단은 Ruland 스타일 U-joint 계열을 참고하되 정확한 SKU/토크/백래시/장착 검토 전까지 `critical_open`이다.

12. 조인트 상세 패키징/토크 스크리닝
   - 증상: 고각도 링크볼이 각도/카탈로그 하중은 만족해도, 브래킷 패키징에서 나사부 굽힘이 생기면 실제 설계가 성립하지 않을 수 있었다.
   - 조치: `calculations/joint_detail_screen.py`, `design_basis/joint_detail_screen.md`, `outputs/reports/joint_detail_summary.md`를 추가했다. Ruland 단품 토크 출처 `SRC-JNT-007`, `SRC-JNT-008`도 추가했다.
   - 결론: 액추에이터 조인트는 볼 중심 하중선/이중전단 박스형 브래킷 조건이 필요하다. 작은 U-joint 단품은 중앙 yaw 토크 단독 경로로 탈락한다. 중앙 가이드의 yaw 토크 경로는 아직 `critical_open`이다.

13. 중앙 yaw 토크 경로 비교
   - 증상: 작은 U-joint가 탈락한 뒤, 어떤 구조가 yaw 토크를 실제로 전달할지 후보 방향이 필요했다.
   - 조치: `calculations/central_yaw_path_comparison.py`, `design_basis/central_yaw_path_comparison.md`, `outputs/reports/central_yaw_path_summary.md`를 추가했다. Ruland US32급 U-joint와 MISUMI ball spline 출처 `SRC-JNT-009`, `SRC-JNT-010`도 추가했다.
   - 결론: YAW-A, 즉 keyed square telescoping guide가 yaw 토크를 전달하고 2축 gimbal은 pitch/roll만 허용하는 방향을 선호안으로 둔다. 대형 U-joint는 예비안, dual anti-yaw guide는 예비안, 단일 16 mm ball spline은 탈락이다.

14. YAW-A 후보 파라미터 정의
   - 증상: YAW-A를 선호한다고만 하면 최종 파라미터 검토에 넣을 수 있는 수치가 부족했다.
   - 조치: `calculations/yaw_a_architecture_screen.py`, `design_basis/yaw_a_architecture_definition.md`, `outputs/reports/yaw_a_architecture_summary.md`를 추가했다.
   - 당시 결론: YAW-A는 tx/ty/rz를 구속하고 tz/rx/ry를 허용하는 rank 3 구조로 정의했다. 이때 후보값은 gimbal 12 deg 설계각, 14 deg 하드스톱이었다. 이후 2026-08-25 사용자 확인 기준에 따라 8 deg/10 deg로 낮췄다.
   - 당시 검증: CSV 출처/열 구조 검사 통과, Phase 0 계산 묶음 실행 통과, 전체 단위 테스트 31개 통과.

15. 최종 후보 파라미터 팩 작성
   - 증상: 계산/표/요약 문서가 늘어나면서 사용자가 판단할 후보값 묶음이 한눈에 보이지 않았다.
   - 조치: `outputs/reports/final_candidate_parameter_pack.md`를 추가해 운동범위, 하중, 액추에이터, 조인트, YAW-A, 프레임, 카트 결합, 제어/전원 후보를 하나의 검토표로 통합했다.
   - 당시 결론: v0.1 후보팩은 100 mm lift, +/-3 deg baseline, +/-5 deg stretch, +/-8 deg sensitivity/rejected baseline, YAW-A central yaw path를 같이 제시했다. 이후 2026-08-25 사용자 확인 기준에 따라 v0.2는 10 kg/+/-3 deg/쉬운 제작 우선으로 갱신했다.

16. 사용자 확인 저하중 기준 반영
   - 증상: 이전 후보팩은 +/-5 deg stretch와 90 kg 보수 스크린이 계속 판단 중심처럼 보였다.
   - 당시 조치: 사용자가 10 kg 가반하중, +/-3 deg 구현, 쉬운 가공/제작/조립 우선을 확인했다. `design_basis/user_confirmed_scope_2026-08-25.md`, `calculations/user_confirmed_baseline.py`, `tests/test_user_confirmed_baseline.py`를 추가했고 후보팩을 v0.2로 갱신했다.
   - 당시 결론: 10 kg 자재, 30 kg 카트, 22 kg 이동 구조, DF 1.5, 50 mm 편심, +/-3 deg 기준에서 최대 액추에이터 축력은 약 912 N이며 Firgelli 450 lbf 후보는 힘 기준으로 통과한다. 이후 빈 카트 약 10 kg 조건이 확인되어 이 값은 보관 민감도로 내려갔다.
   - 당시 검증: CSV 출처/열 구조 검사 통과, 사용자 확인 기준 포함 Phase 0 계산 묶음 실행 통과, 전체 단위 테스트 35개 통과.

17. 사용자 추가 확인 기준 반영
   - 증상: v0.2는 30 kg 카트 보관 민감도 값을 1차 결론처럼 읽을 수 있었다.
   - 조치: 사용자가 빈 카트는 약 10 kg으로 예상하고, 카트는 수평유지장치에 맞게 제작 가능하며, 연결 전 수평유지장치 높이는 250~300 mm 정도면 된다고 확인했다. `calculations/user_confirmed_baseline.py`, `tests/test_user_confirmed_baseline.py`, `design_basis/user_confirmed_scope_2026-08-25.md`, `outputs/reports/final_candidate_parameter_pack.md`를 갱신했다.
   - 결론: 1차 기준은 10 kg 자재, 10 kg 카트, 22 kg 이동 구조 = 42 kg lifted mass다. 최대 액추에이터 축력은 약 618 N, Firgelli 여유는 약 3.24배, YAW-A 설계 yaw torque는 약 16 Nm다.
   - 추가 결론: 저하중 기준 인터페이스 모멘트와 래치 하중도 갱신했다. 활성 worst interface moment는 약 108 Nm, guide-pin shear는 약 154 N, 4개 래치 기준 per-latch uplift는 약 31 N이다.
   - 보관 민감도: 30 kg 카트 기준 62 kg lifted mass, 최대 액추에이터 축력 약 912 N, YAW-A 설계 yaw torque 약 24 Nm는 계속 참고값으로 유지한다.
   - 검증: 전체 단위 테스트 36개 통과, CSV 출처/열 구조 검사 통과, Phase 0 계산 묶음 실행 통과.

18. 카트 리시버 알루미늄 프로파일 방향 반영
   - 증상: 카트 하부 프레임/리시버 제작방식이 아직 미정이라 다음 작업자가 인터페이스 존을 잡기 어려웠다.
   - 조치: 사용자가 알루미늄 프로파일이 좋겠다고 확인했다. `design_basis/cart_profile_receiver_concept_2026-08-25.md`를 추가하고, 후보팩/요구사항/인수인계 문서에 알루미늄 프로파일 리시버 방향을 반영했다.
   - 결론: 카트측 리시버는 볼트 조립식 알루미늄 프로파일을 조절 가능한 골격으로 사용하되, 위치결정핀/받침/래치 키퍼/스토퍼면은 국부 금속 인서트나 플레이트로 분리한다.
   - 보류: 정확한 프로파일 단면, 커넥터 형식, 리시버 레일 간격, 핀/받침/래치 위치는 아직 제작값이 아니며 Phase 1 후보 파라미터로 남긴다.
   - 검증: CSV 파싱 확인, 전체 단위 테스트 36개 통과.

19. CR-01 카트 리시버 배치/질량/하중 스크리닝
   - 증상: 알루미늄 프로파일 방향만으로는 10 kg 빈 카트 목표 안에서 어떤 리시버 구성이 가벼운지 판단하기 어려웠다.
   - 조치: `calculations/cart_profile_receiver_screen.py`, `tests/test_cart_profile_receiver_screen.py`, `design_basis/cart_profile_receiver_layout_screen.md`, `outputs/reports/cart_profile_receiver_summary.md`를 추가했다. 후보팩은 v0.5로 갱신했다.
   - 결론: CR-01은 760 mm x 560 mm 리시버 존에 760 mm HFS8-4040 세로 레일 2개를 사용하는 2-레일 키트다. placeholder 하드포인트 포함 질량은 약 4.50 kg으로, 10 kg 카트 기준의 약 45%다.
   - 예비안: HFS8 사각 서브프레임은 약 6.43 kg으로 가능하지만 무거운 예비안이다. GFS8 2-레일은 약 5.16 kg으로 강성 예비안이다.
   - 하중 스크린: active worst 조건에서 4개 받침 패드는 모두 압축 상태를 유지하고, 최대 패드하중은 약 331 N이다. 마스터 locator가 전단을 모두 받아도 약 154 N, 520 mm span yaw couple force는 약 32 N이다.
   - 보류: 커넥터 강성, 슬롯 미끄럼, 인서트판 두께, locator 상세, rest pad 조절 구조, latch keeper 형상은 아직 미확정이다.
   - 검증: CR-01 포함 Phase 0 계산 묶음 실행 통과, 전체 단위 테스트 41개 통과, CSV 출처 ID/열 구조 검사 통과.

20. CR-01-H1 하드포인트 상세 스크리닝
   - 증상: CR-01 리시버 존은 정해졌지만 locator insert, rest pad, latch keeper, slot fastening을 어떤 후보값으로 둘지 아직 정리되지 않았다.
   - 조치: `calculations/cart_receiver_hardpoint_screen.py`, `tests/test_cart_receiver_hardpoint_screen.py`, `design_basis/cart_receiver_hardpoint_screen.md`, `outputs/reports/cart_receiver_hardpoint_summary.md`를 추가했다. 후보팩은 v0.6으로 갱신했다.
   - 결론: CR-01-H1은 12 mm locator 인터페이스, 8 mm local steel insert 또는 hardened bushing, 40 x 30 mm rest pad contact, 5 mm latch keeper, critical hard point당 M8급 T-slot fastener 2개를 후보 시드로 둔다.
   - 계산 결과: locator insert bearing 약 1.94 MPa, rest pad contact pressure 약 0.28 MPa, latch keeper bearing 약 0.25 MPa(4 latch) 또는 0.49 MPa(2 latch), local tab bending 약 16 MPa다.
   - 시행착오/주의: placeholder clamp/friction으로 slip margin은 약 6.45배지만, 프로파일 슬롯 마찰을 최종 위치 기준으로 승인하면 안 된다. 최종 반복 위치 기준은 dowel/keyed plate/shoulder block/positive stop으로 잡아야 한다.
   - 보류: 정확한 slot nut, backing plate, locator bushing, shim/lock 구조, latch keeper 형상, secondary lock, latch sensor 배치는 아직 미확정이다.
   - 검증: CR-01-H1 포함 Phase 0 계산 묶음 실행 통과, 전체 단위 테스트 47개 통과, CSV 출처 ID/열 구조 검사 통과.

21. CR-01-H2 연결/포지티브 스토퍼 토폴로지 스크리닝
   - 증상: CR-01-H1에서 슬롯 마찰을 최종 위치 기준으로 쓰면 안 된다는 결론은 있었지만, slot nut/backing plate/positive stop 방향이 아직 후보로 좁혀지지 않았다.
   - 조치: `calculations/cart_receiver_connector_topology_screen.py`, `tests/test_cart_receiver_connector_topology_screen.py`, `design_basis/cart_receiver_connector_topology_screen.md`, `outputs/reports/cart_receiver_connector_summary.md`를 추가했다. 후보팩은 v0.7로 갱신한다.
   - 결론: `CR-01-H2-B`를 선호안으로 둔다. 두 M8급 T-slot fastener는 mock-up 조정과 클램프용이고, 최종 반복 위치와 전단/yaw 기준은 shoulder/key/positive stop이 맡는다. 필요 시 6 mm 이상 dowel을 정렬 후 추가한다.
   - 계산 결과: connector demand 약 186 N, friction-only placeholder slip margin 약 6.45배, positive stop bearing 약 0.58 MPa, positive stop tab bending 약 19 MPa, optional 6 mm dowel shear 약 6.6 MPa다.
   - 시행착오/주의: friction-only 방식은 숫자로는 통과하지만 최종 위치결정 정책에 실패하므로 `CR-01-H2-A`로 명시 탈락시켰다.
   - 보류: 정확한 slot nut 형번, profile wall bearing, backing plate 필요 여부, replaceable stop 형상, dowel 위치, sensor 접근성은 아직 미확정이다.
   - 검증: CR-01-H2 단위 테스트 6개 통과. 문서 갱신 후 전체 단위 테스트 53개 통과, Phase 0 계산 묶음 실행 통과, CSV 출처 ID 검사 통과.

22. CR-01-H3 연결 스택/서비스 접근성 스크리닝
   - 증상: H2-B는 선호 토폴로지를 정했지만, master locator, secondary locator, rest pad, latch keeper가 같은 방식으로 구속되면 receiver가 과구속될 수 있었다.
   - 조치: `calculations/cart_receiver_connector_detail_screen.py`, `tests/test_cart_receiver_connector_detail_screen.py`, `design_basis/cart_receiver_connector_detail_screen.md`, `outputs/reports/cart_receiver_connector_detail_summary.md`를 추가했다. 후보팩은 v0.8로 갱신한다.
   - 결론: `CR-01-H3`를 연결 스택 규칙으로 둔다. Master locator는 X/Y 고정, secondary locator는 Y만 고정하고 X를 release, rest pad는 Z seating만, latch keeper는 preload/uplift만 담당한다.
   - 계산 결과: profile wall/stop bearing은 3배 local factor를 넣어 약 1.74 MPa, slot nut clamp contact screen은 4000 N clamp와 18 x 12 mm 접촉 가정에서 약 18.5 MPa다.
   - 시행착오/주의: secondary locator를 round dowel처럼 X/Y 모두 고정하면 조립 반복성이 나빠지고 과구속 위험이 생긴다. Latch hook과 rest pad를 숨은 수평 전단 경로로 쓰면 안 된다.
   - 보류: exact slot nut contact, backing plate 형상, stop block replaceability, dowel 위치, latch-closed/cart-present sensor bracket, 30 cycle mock-up 결과는 아직 미확정이다.
   - 검증: CR-01-H3 단위 테스트 8개 통과. 문서 갱신 후 전체 단위 테스트 61개 통과, CR-01-H3 포함 Phase 0 계산 묶음 실행 통과, CSV 출처 ID 검사 통과.

23. CR-01-H4 조립·목업 하드웨어 시드 스크리닝
   - 증상: H3는 각 하드포인트의 축 역할을 분리했지만, 목업에서 무엇을 조립하고 무엇을 wear item으로 남길지가 아직 모호했다.
   - 조치: `calculations/cart_receiver_hardware_selection_screen.py`, `tests/test_cart_receiver_hardware_selection_screen.py`, `design_basis/cart_receiver_hardware_selection_screen.md`, `outputs/reports/cart_receiver_hardware_selection_summary.md`를 추가했다. 후보팩은 v0.9로 갱신한다.
   - 결론: `CR-01-H4-S1`을 목업 하드웨어 시드로 둔다. Master는 12 mm removable round bushing + replaceable stop, secondary는 X-slot/diamond Y-only locator, rest pad는 40 x 30 mm shim seat, keeper는 5 mm steel + separate mechanical secondary lock으로 둔다.
   - 계산 결과: 3배 local factor에서 bushing bearing 약 5.8 MPa, stop bearing 약 1.7 MPa, stop bending 약 32.7 MPa, optional 6 mm dowel shear 약 19.7 MPa, rest-pad contact 약 0.8 MPa다.
   - 시행착오/주의: 첫 테스트에서 shear allowable 상수가 H2 파일에 정의된 것을 H1에서 가져오려 해 import 오류가 발생했고, 참조 위치를 바로잡아 해결했다. 이 수치는 placeholder 비교이며, fit/torque/stop screw/latch/sensor는 제작값이 아니다.
   - 보류: 정확한 T-slot nut, fastener grade/torque, bushing fit/retention, stop screw pattern, dowel 필요 여부, latch/secondary lock/sensor 형번과 배치는 미확정이다.
   - 검증: CR-01-H4 단위 테스트 8개 통과. 문서 갱신 후 전체 단위 테스트 69개 통과, CR-01-H4 포함 Phase 0 계산 묶음 실행 통과, CSV 출처 ID 검사 통과.

24. JNT-BR-01 HRT8E형 액추에이터 브래킷 패키지 스크리닝
   - 증상: HRT8E는 +/-3 deg joint candidate로 남아 있었지만, 기존 screen이 큰 radial rating을 사용했고 threaded-shank cantilever를 제거하는 실제 bracket seed가 없었다.
   - 조치: `calculations/actuator_bracket_package_screen.py`, `tests/test_actuator_bracket_package_screen.py`, `design_basis/actuator_bracket_package_screen.md`, `outputs/reports/actuator_bracket_package_summary.md`를 추가했다. HRT8E capacity screen은 26.77 kN radial 값이 아닌 5.29 kN axial static 값으로 정정했다.
   - 결론: `JNT-BR-01-HRT8E`를 조건부 하드웨어 시드로 둔다. Two 8 mm steel lug, 8 mm double-shear pin, <=16 mm loaded support span, ball-center load path를 유지하며 threaded-shank spacer와 single-shear primary lug는 탈락시킨다.
   - 계산 결과: Active +/-3 deg/DF 2.0/100 mm eccentricity에서 max axial force는 약 972 N이다. 2x static demand 약 1.94 kN 대비 HRT8E axial static margin은 약 2.72x다. Pin double shear 약 9.7 MPa, pin bending 약 77.4 MPa, lug bearing 약 15.2 MPa, lug-root bending 약 42.7 MPa다.
   - 시행착오/주의: 14 deg catalog articulation에 대해 required articulation이 약 12.94 deg라 residual은 약 1.06 deg다. 수치상 통과만으로 bracket clearance를 주장하면 안 되며, 실제 HRT8E eye width/body envelope/thread engagement/allowed load direction을 제조사 도면으로 확인하고 14 deg no-contact gauge/mock-up을 해야 한다.
   - 보류: actual HRT8E drawing, pin material/retention, lug material/joining, bracket-to-module attachment, edge distance, fatigue/shock test는 미확정이다.
   - 검증: JNT-BR-01 단위 테스트 8개 통과. 문서 갱신 후 전체 단위 테스트 77개 통과, JNT-BR-01 포함 Phase 0 계산 묶음 실행 통과, CSV 출처 ID 검사 통과.

25. CAD 전 YAW-A/작업영역/리미트 계층 재검증
   - 증상: YAW-A는 자유도 표 수준에만 머물렀고, 기존 250 mm 접힘 후보는 15 mm actuator end reserve에서 최저 +/-3 deg 자세의 여유가 약 2.54 mm밖에 남지 않았다. 또한 이전 `10 deg hard stop`이 총 기울기인지 각 핀 회전인지 명시되지 않았다.
   - 조치: `calculations/yaw_a_gimbal_kinematic_screen.py`, `calculations/actuator_geometry.py`, `calculations/workspace_operating_window_screen.py`, `calculations/travel_limit_hierarchy_screen.py`와 단위 테스트를 추가했다. CAD 의존성이 없는 actuator length 계산으로 분리해 작업영역 스크립트가 렌더링 커널 없이도 실행되게 했다.
   - 결론: YAW-A는 하부 fixed +Y pitch pin 다음 상부 local +X roll pin, `R = Ry(pitch)Rx(roll)` 순서로 고정한다. +/-3 deg grid의 selected world-heading yaw는 0이며, four +/-7 deg pin stops는 최악 대각 total tilt 약 9.89 deg로 기존 10 deg envelope 안에 든다. 10 deg는 각 핀의 허용각이 아니다.
   - 작업영역 결론: `WS-01-H20`을 pre-CAD 후보로 둔다. 270 mm 접힘, 100 mm lift, 195 mm outer/220 mm inner keyed guide에서 0/50/75/100 mm와 nine-corner +/-3 deg grid는 334-508 mm actuator command window 안에 들며 최저 soft reserve는 약 11.13 mm, guide overlap은 최소 88 mm다.
   - 리미트 결론: command 334/508 mm, electrical target 329/513 mm, guarded physical-stop boundary 324/518 mm을 사용한다. 이는 길이 좌표의 계획값이며 외부 shoulder/collar, 실제 switch, stop contact, measured overrun이 있어야 닫힌다.
   - 시행착오/주의: 직접 실행한 workspace/limit script는 프로젝트 root path가 없어 처음에는 import에 실패했다. 두 스크립트에 root/vendor path 초기화를 넣었다. CAD placeholder의 가이드 내부 stop block은 실제 stop 형상이 아니며, sliding inner tube를 막지 않는 external stop 구조로 교체해야 한다.
   - 보류: V-01 HRT8E 14 deg gauge, V-02 YAW-A guide/yoke gauge, V-03 actuator limit-before-stop, V-04 CR-01-H4 30-cycle, V-05 mass, V-06 12 V/control architecture는 아직 실제 증거가 없다. 이 항목은 이제 제작 릴리스 전 게이트로 유지한다.

26. `APPROVE CONCEPT` 수신 및 Phase 2 상세 CAD 기준 갱신
   - 승인: 2026-08-26 사용자가 정확히 `APPROVE CONCEPT`를 입력했다.
   - 조치: `cad/parameters.py`를 WS-01-H20의 270 mm 접힘, 185 mm 관절 수직간격, 195/220 mm 가이드로 갱신했다. YAW-A를 고정 하부 +Y 피치 요크, 피치 이동 중간 링, 플랫폼 이동 local +X 롤 요크로 분리했다.
   - 조치: 기존 가이드 관 내부를 막던 solid stop block을 제거했다. 전기 리미트와 별도의 두 수동 텔레스코픽 스톱 카트리지 및 이동 접촉 바를 중앙 가이드 외부에 배치했다.
   - 조치: 액추에이터 양단 요크를 JNT-BR-01 기준 8 mm 핀, 8 mm 러그, 16 mm 내부 간격의 중심 이중전단 시드로 갱신하고 HRT8E형 eye envelope를 액추에이터 모델에 넣었다.
   - 조치: 중앙 서비스 개구, 짐벌-상부프레임 연결 브리지, IMU/케이블 가이드 재배치를 반영했다. 중앙 상세 STEP 2개와 부품 필터 근접 렌더 2개를 추가했다.
   - 시행착오: 최초 외부 고정 포스트 방식은 접힘 상태에서 상판 위로 돌출하고 기존 상판/보강판을 관통했다. 프리뷰와 교차 체적 검사로 확인해 폐기하고, 상판 아래에 머무는 수동 스톱 카트리지 방식으로 교체했다.
   - 시행착오: 첫 근접 렌더는 전체 상부 프레임이 짐벌을 가렸다. 렌더 함수에 부품 필터를 추가해 중앙 가이드/짐벌만 표시하도록 수정했다.
   - 계산 수정: CAD 전 비교 스크립트가 전역 기준이 270 mm로 바뀐 뒤 WS-01-H20에 20 mm를 다시 더하는 회귀가 있었다. 250 mm 비교안은 -20 mm, 승인안은 0 mm 상대 오프셋을 쓰도록 절대 기준으로 고쳤다.
   - 검증: `scripts/run_phase2.ps1` 완료, CAD 14개/렌더 11개 생성, 전체 단위 테스트 94개 통과.

27. LS-01 액추에이터축 기계 스톱·전기 리미트 상세화
   - 증상: 활성 방사형안의 빨간/초록 링은 포락체일 뿐 실제 하중 접촉면, 이동 스트라이커, 스위치 레버와 조절구조가 없었다.
   - 조치: 액추에이터당 12 mm 이동 로드 2개, 고정 캐리어/교체형 부싱, 이동 크로스헤드, 기계식 칼라 4개, 비하중 전기 캠 2개, 슬롯형 브래킷과 Omron D4N 롤러 플런저 포락체 2개를 추가했다. `ls01_actuator_limit_package_neutral.step`과 길이방향/끝보기 렌더를 생성했다.
   - 위치결론: 220 mm 고정 캐리어와 상부 핀에서 42 mm 떨어진 이동 크로스헤드 기준으로 하부 기계/전기 62/67 mm, 상부 전기/기계 251/256 mm다. 양방향에서 전기 캠이 기계 접촉보다 5 mm 먼저 도달한다.
   - 정적 스크린: 42 kg, 정적계수 2.0에서 패키지 기준하중 약 824 N, 로드당 균등반력 약 412 N, 12 mm 로드 축응력 약 3.64 MPa, 칼라면 평균압력 약 0.82 MPa다. 칼라 하나당 최소 824 N push-off/제조사 유지력 확인을 후속 게이트로 둔다.
   - 시행착오: 첫 86 mm 로드 간격에서는 28 mm 칼라와 20 mm 캠이 단순 모터 박스와 교차했다. 중심간격을 104 mm, 캐리어 폭을 132 mm로 늘려 named poses에서 교차체적 0을 확인했다.
   - 시행착오: 첫 근접 카메라는 두 로드를 겹쳐 보이게 했고, 반대 시점은 길이방향 위치를 압축했다. 길이방향 사시도와 단면 방향 끝보기를 분리하고 색상 범례를 추가했다.
   - 보류: 액추에이터 하우징 허용 장착점, 크로스헤드 결합부, 칼라 충격/밀림, 한쪽 로드 집중하중, 가드, 케이블, 정확한 D4N 접점·커넥터와 실측 overrun은 미확정이다.
   - 검증: 신규 LS-01 테스트 7개 포함 전체 104개 통과, CAD 16개, 렌더 21개 생성.

31. Firgelli 공식 STEP 기반 LS-01 datum 정정
   - 증상: 기존 42 mm moving-crosshead offset은 실제 front clevis attachment 근거가 없었고 chrome rod clamp처럼 보이는 형상이 남아 있었다.
   - 조치: actuator, MB21, MB20, MB17 공식 STEP 4종을 보관하고 fixed/moving solids를 분리했다. MB21 50 x 82.854 x 100 mm envelope를 220 mm fixed station에, front-clevis pin centre를 moving datum에 적용했다.
   - 계산: collar/cam offset은 104/109/293/298 mm, rod는 12 x 320 mm로 변경했다. MB21은 source STEP body zone 안에 최소 약 18.73 mm reserve를 갖는다.
   - 시행착오: annular capture가 upper yoke와 49.57 mm3 겹쳐 제거했다. Relieved bridge와 outer keyed straps로 바꾼 뒤 28 mm setback에서 0.99 mm3가 남아 32 mm로 옮겨 모든 named pose에서 교차체적 0을 확인했다.
   - 한계: MB21 packaging fit은 vendor stop-load approval이 아니다. 이후 serial HRT8E adapter는 길이 증가 때문에 기각했고, 공장 아이 중심 `JNT-CG-01` 목업으로 방향을 바꿨다.
   - 산출물: `design_basis/firgelli_mount_datum_review_2026-08-27.md`, source STEP diagnostic renders 2종, revised LS-01 STEP/renders.

32. 정지형 시험대 최소 구성과 JNT-CG-01 전환
   - 범위: 실내·감독하·저속·정지형 시험대로 한정하고 외부 D4N/캠/브래킷 및 전용 산업용 비상정지 SKU를 활성 CAD/BOM에서 제거했다. 내장 종단 리미트, 독립 LS-01M 기계 칼라와 즉시 가능한 시험대 전원 차단은 유지했다.
   - 조인트 결정: 양단 32 mm 직렬 HRT8E 어댑터는 최악 유효 길이 약 281.14 mm로 319 mm 수축 길이를 침범해 기각했다. 공장 아이 M8 핀과 대향 M8 트러니언을 같은 중심에 두는 `JNT-CG-01`을 실측 목업안으로 선택했다.
   - 계산: 약 876 N 활성 설계력에서 M8 double shear 약 8.72 MPa, 22 mm 지지폭 pin bending 약 95.9 MPa, lug bearing 약 18.3 MPa다.
   - 시행착오: 24 mm 지지폭은 약 104.6 MPa로 예비 100 MPa 기준을 넘어서 22 mm로 축소했다. 공식 220 lbf/2-inch family drawing의 아이 폭 수치는 선택 모델 치수로 사용하지 않았다.
   - 제작 게이트: 선택한 450 lbf/8-inch 아이 두께와 핀 스택을 실측한 뒤 조인트 1개와 카세트 1개만 먼저 만들고, 스윕/하중/칼라 push-off를 통과해야 나머지를 복제한다.

## 9. 다음 작업자가 해야 할 일

1. 선택한 450 lbf/8-inch Firgelli front/rear eye 두께, supplied pin stack, shoulder geometry를 실측한다.
2. 실측값으로 shim-adjustable `JNT-CG-01` 1개를 제작해 양축/대각 무간섭, pin bearing, trunnion engagement와 조립 접근성을 검증한다.
3. LS-01M 액추에이터 카세트 1개를 제작해 built-in endpoint, 12 mm twin rod 정렬, 칼라 push-off와 저속 끝단 동작을 확인한다.
4. V-02 컴팩트 중앙 가이드/카단 목업에서 +/-3 deg nine-corner sweep, 각 축 +/-7 deg stop, yaw freeplay <=0.5 deg를 측정한다.
5. Firgelli에 MB21/actuator housing의 external stop reaction 허용 여부를 확인하고, 불허 시 fixed carrier를 lower-yoke-mounted frame으로 변경한다.
6. 단일 조인트/카세트가 통과한 뒤에만 나머지 5개 조인트와 2개 카세트를 복제하고 CAD 질량/BOM을 갱신한다.
7. 시험대 전원은 감독자가 즉시 차단할 수 있게 두고 분기 퓨즈/전류제한을 적용한다. 이동·무인·사람 탑승 용도로 바뀌면 삭제한 외부 리미트/인터록/가드를 재검토한다.

조달 대안 업데이트:

- 초기 검토에서 나비엠알오 등록품 DIHOOL `LA2000-125150 / K92931811`을 재설계 후보로 찾고 수직 관절간격 185 mm와 길이 범위 273.20~385.35 mm를 사용했다. 중간에 A2 200 mm안을 검토했지만 최신 평판 미포함 핀/러그 가정에서 이 185 mm 기준을 다시 선택했다.
- 이 후보는 아직 활성 CAD가 아니다. 주문 전 판매자에게 정확한 150 mm SKU Lmin/Lmax, A1/A2 끝단, Hall 포함 여부, 배선, 전류와 STEP를 확인한다.
- 확인 후 사용자가 이 대안을 선택하면 Firgelli/MB21/LS-01M 종속 형상을 DHLA2000 전용 6 mm 브래킷 및 shared-centre 2축 조인트로 교체하고 전체 CAD/간섭/하중/BOM을 재생성한다.
- 근거와 시행착오는 `design_basis/navimro_dhla2000_redesign_feasibility_2026-08-27.md`에 있다.

최근 검증 결과:

- 전체 단위 테스트 109개 통과.
- `scripts/run_phase2.ps1` 전체 파이프라인 통과: CAD 17개, pipeline 렌더 24개.
- YAW-A/WS-01-H20/travel-limit 계산과 Phase 2 보고서 재생성 통과.
- 마지막 전체 CAD 파이프라인 당시 CSV 검사는 `parameter_decision_table.csv` 150행, `component_candidate_table.csv` 57행, `source_register.csv` 57행이었다. 이후 NAVIMRO 재설계 조사로 후보 부품 3행과 출처 7행을 추가해 현재 각각 60행과 64행이며, 활성 CAD는 아직 변경하지 않았다.
- 활성 BOM 15행 중 HRT8E 구형 joint-package 품목 0건, D4N/A22E 품목 0건. LS-01M 렌더에서 외부 switch/cam 잔존 없음.

## 10. 현재 검증 명령

기존 테스트:

```powershell
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import os, pathlib, sys, unittest; root=pathlib.Path.cwd(); os.environ['XDG_CACHE_HOME']=str(root / '.cache'); os.environ['MPLCONFIGDIR']=str(root / '.mplcache'); sys.path.insert(0, str(root)); sys.path.insert(0, str(root / 'vendor' / 'python')); suite=unittest.defaultTestLoader.discover(str(root / 'tests'), pattern='test_*.py'); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)"
```

Phase 0 계산:

```powershell
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import os, pathlib, runpy, sys; root=pathlib.Path.cwd(); os.environ['XDG_CACHE_HOME']=str(root / '.cache'); os.environ['MPLCONFIGDIR']=str(root / '.mplcache'); sys.path.insert(0, str(root)); sys.path.insert(0, str(root / 'vendor' / 'python')); scripts=['calculations/user_confirmed_baseline.py','calculations/cart_profile_receiver_screen.py','calculations/cart_receiver_hardpoint_screen.py','calculations/cart_receiver_connector_topology_screen.py','calculations/cart_receiver_connector_detail_screen.py','calculations/cart_receiver_hardware_selection_screen.py','calculations/actuator_bracket_package_screen.py','calculations/yaw_a_architecture_screen.py','calculations/central_yaw_path_comparison.py','calculations/joint_detail_screen.py','calculations/joint_candidate_screen.py','calculations/mobility_analysis.py','calculations/combined_workspace.py','calculations/actuator_length_sweep.py','calculations/load_distribution.py','calculations/interface_moments.py','calculations/latch_load.py','calculations/frame_deflection.py','calculations/power_budget.py','calculations/cost_estimate.py']; [print('\n## '+s) or runpy.run_path(str(root / s), run_name='__main__') for s in scripts]"
```

추가 CAD 전 계산은 프로젝트 루트에서 직접 실행할 수 있다.

```powershell
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\calculations\yaw_a_gimbal_kinematic_screen.py
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\calculations\workspace_operating_window_screen.py
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\calculations\travel_limit_hierarchy_screen.py
```

## 11. Git 상태

현재 폴더는 git 저장소가 아니다. `git status` 실행 결과:

```text
fatal: not a git repository (or any of the parent directories): .git
```

따라서 다른 컴퓨터와 공유하려면 이 OneDrive 프로젝트 폴더 전체가 동기화되어야 한다.

## 12. NAVIMRO 단일 주문 패키지 상태

2026-08-27 사용자는 모든 필요한 자재와 부속을 나비엠알오에서 한 번에 구매해야 한다고 확인했다. 이에 따라 액추에이터 후보 확인 수준이던 조사를 49개행의 전체 PoC 구매 패키지로 확장했다. 중간 A2 평판 검토에서 브래킷 수량을 0으로 바꿨다가, 최신 평판 미포함 핀/러그 가정에서 각각 6개로 복원했다.

핵심 산출물:

- `procurement/navimro_single_order_bom.csv`: 상품코드, 수량, VAT 포함 관찰가격, 출하일, 직접 링크와 발주조건.
- `procurement/navimro_single_order_bom.md`: 구매 구조, 절단목록, 상태코드와 보류 항목 설명.
- `procurement/navimro_preorder_inquiry_2026-08-27.md`: 한 번의 통합 견적을 받기 위한 판매처 문의문.
- `design_basis/navimro_single_order_redesign_basis_2026-08-27.md`: 나비엠알오 부품 중심 구조변경 기준.
- `calculations/navimro_single_order_cost.py`: CSV 소계 검증.

현재 핀/러그 가정 기준 알려진 가격은 VAT 포함 2,764,784원이며, 팬/필터 로그인 가격, 장척물 착불비와 현지가공비는 제외된다. 15 mm 아크릴은 900x800 2장 팩을 한 번 구매해 1장을 예비품으로 남기는 구성이다.

새 구조 방향:

- 3개의 DIHOOL `LA2000-125150` 방사형 액추에이터 원리는 유지한다.
- 프레임은 Daeyoung `DF 4040-8` 절단품 18개와 500 mm 각도재 3개로 구성한다.
- 중앙 구속은 12 mm 샤프트 2개, LMF12UU 4개, SK12 4개와 작은 강판 Cardan으로 단순화한다.
- Y710 12 mm 칼라 4개가 독립 Z 기계 스톱, Cardan 강판 돌기가 각 축 +/-7 deg 스톱을 담당한다.
- 카트 결합은 760 mm 프로파일 레일 2개, 강판 locator/stop과 CR-3001 래치 4개다. 래치는 전단 위치결정부가 아니다.
- 제어는 DMD-150 3개, Mega2560 PRO, BNO055, 12 V 29 A PSU와 모터별 DC 차단기로 구성한다.

다음 작업 순서:

1. `procurement/navimro_preorder_inquiry_2026-08-27.md`를 나비엠알오에 보내 서면 회신과 통합견적을 받는다.
2. 회신에서 평판 미포함 여부, M8-to-eye 부속, 핀 중심 Lmin/Lmax, 양단 인터페이스, Hall/배선/전류와 일치 STEP를 우선 확인한다.
3. 정확한 STEP/도면으로 active Firgelli CAD를 DIHOOL 및 twin-shaft guide로 교체한다.
4. named pose 간섭, +/-3 deg 작업영역, 조인트 핀 스택, Cardan stop, 제어함 layout을 재검증한다.
5. 프로파일/강판/아크릴 절단·구멍 도면을 동결하고 나서만 49개행 단일 주문을 승인한다.

중요: 현재 패키지는 완전한 공급처/수량 계획이지만 `click-to-buy` 제작 릴리스는 아니다. 주문제작·반품불가 액추에이터와 브래킷을 판매자 회신 없이 먼저 결제하지 않는다.

단일 주문 패키지는 최신 핀/러그 가정에서 활성 49행이며, 알려진 가격 소계는 2,764,784원이다.

웹 도면 후속 확인:

- 최신 기준은 평판 미포함 핀/러그 구성이다. 185 mm 수직 관절간격에서 273.20~385.35 mm가 필요하고 잠정 255~405 mm 범위에 대해 18.20/19.65 mm 여유로 통과한다.
- 나비엠알오 `K92931811` 상세 이미지가 실제로는 `DHLA6000-A2` 자료를 표시하고 상품 제목도 A1/A2를 구분하지 않는다.
- 따라서 브래킷 치수는 웹 도면으로 CAD에 사용할 수 있지만, 액추에이터 납품형과 Hall/배선은 판매처 서면확인이 필요하다.
- 상세 근거: `design_basis/navimro_web_drawing_review_2026-08-27.md`.
- 웹 도면 A1/A2 회귀 테스트 추가 후 전체 단위 테스트 111개 통과.

## 2026-08-27 A2 기준 선택 - 이후 대체됨

- 사용자는 한때 나비엠알오에서 보이는 A2 평판형으로 진행하는 방향을 검토했다. 이 기준은 아래의 평판 미포함 가정으로 대체됐다.
- `https://www.navimro.com/g/3267413/`은 A1 설명 이미지를 쓰지만 실제 상품은 500 mm 스트로크 `LA2000-125500 / K92931822`이다. 150 mm A1 판매 링크로 사용하지 않는다.
- `https://www.navimro.com/g/3267401/`은 150 mm `LA2000-125150 / K92931811`이지만 상세 이미지가 `DHLA6000-A2`이므로 주문 시 A2 형식과 실제 도면을 명시한다.
- A2 후보 치수는 상/하 반경 400/175 mm, 수직 관절간격 200 mm, 연결 전 높이 285 mm다. 0~100 mm 승강 및 pitch/roll +/-3 deg에서 길이는 282.05~397.65 mm다.
- 잠정 A2 265~415 mm에 대한 수축/신장 여유는 17.05/17.35 mm다.
- A2 평판 양단은 custom orthogonal yoke에 연결한다. 프레임에 양단 강체 고정하지 않는다.
- U/H A1 브래킷은 BOM 수량 0으로 변경했다. 활성 주문행 47개, 감사행 2개, 알려진 합계 2,639,516원이다.
- active CAD는 여전히 Firgelli 기준이다. A2 평판 도면/STEP을 받은 뒤 DIHOOL CAD로 교체한다.
- A2 기준 변경 후 전체 단위 테스트 111개가 통과했다.

## 2026-08-27 평판 미포함 핀/러그 기준 선택

- 사용자는 상세 이미지의 액추에이터 본체와 `Ø10 / M8` 축단 부속 사이 `+` 표기를 근거로 평판이 기본 포함품이 아니라고 가정해 진행하도록 지시했다.
- 최신 계획 인터페이스는 평판 미포함, M8 나사식 축단 부속과 아이/핀 어댑터다. 그림은 DHLA6000-A2 자료라서 확정 도면이 아니라 명시적 가정으로 관리한다.
- 후보 치수는 상/하 반경 400/175 mm, 수직 관절간격 185 mm, 연결 전 높이 270 mm다. 0~100 mm 승강 및 pitch/roll +/-3 deg에서 길이는 273.20~385.35 mm다.
- A1형 공식 255~405 mm를 잠정 핀 중심 범위로 쓰면 수축/신장 여유는 18.20/19.65 mm다.
- 나비엠알오 U/H 6 mm 브래킷은 각각 6개를 다시 BOM에 포함했다. 각 액추에이터 양단에서 U/H와 custom shared-centre outer yoke를 사용한다.
- BOM은 활성 49행, 알려진 합계 2,764,784원으로 복원됐다.
- 발주 전 확인은 평판 미포함 여부, `Ø10 / M8` 부속 포함 수량, 아이 구멍/폭, 양단 인터페이스, 핀 중심 Lmin/Lmax, Hall/배선/전류와 일치 STEP다.
- active CAD는 아직 Firgelli 기준이다. 위 가정으로 재설계 준비는 진행하지만 실제 부품 도면 전에는 제작도면을 릴리스하지 않는다.
- 핀/러그 CAD 시드 추가 후 전체 단위 테스트 112개가 통과했다.
- 독립 예비 CAD `cad/navimro_pin_lug_gimbal.py`, STEP `outputs/cad/step/navimro_pin_lug_gimbal_assumption.step`, 렌더 `outputs/renders/navimro_pin_lug_gimbal_assumption.png`를 추가했다. 실제 축단 치수 전에는 제작용으로 사용하지 않는다.

## 2026-08-27 NAVIMRO 제작 CAD Rev A 완료

사용자가 제작 CAD, 가공도면, 나비엠알오 중심 발주와 400만원 상한을 요청해 이전 예비 시드를 제작 패키지로 확장했다.

현재 산출물:

- `cad/navimro_fabrication_parameters.py`: 단일 치수 기준.
- `cad/navimro_fabrication_assembly.py`: 하부/상부 4040, 액추에이터 3축, moving twin shafts, fixed bushings, laminated Cardan, cart coupling.
- `cad/navimro_fabrication_exports.py`: STEP 6상태, 평철 DXF 14종, 아크릴 DXF, 절단표.
- `calculations/navimro_fabrication_verification.py`: workspace, 하중, 높이, guide engagement, clearance.
- `calculations/navimro_fabrication_budget.py`: 400만원 gate.
- `output/pdf/NAVIMRO_leveling_module_fabrication_drawings_revA.pdf`: A3 11쪽.
- `output/pdf/NAVIMRO_leveling_module_assembly_and_order_pack_revA.pdf`: A4 landscape 11쪽.
- `outputs/navimro_fabrication/artifact_manifest.json`: SHA-256 목록.

현재 수치:

- 전체 corner sweep actuator pin length 273.196~385.349 mm.
- 접힘 전체 높이 300 mm.
- Rev A 당시 known NAVIMRO subtotal 2,799,522원, planned total 3,799,522원, headroom 200,478원. 현재 금액은 Rev D 절을 따른다.
- 전체 테스트 123개 통과.
- 두 PDF 모두 11페이지, 전 페이지 PNG 렌더 검수, 빈 페이지/누락 이미지/대체문자 없음.

중요 시행착오:

- 처음 fixed shaft 구조는 접힘 상태에서 shaft가 상판 위로 돌출했다. Rev A는 shaft를 상부 carriage와 함께 움직이고 LMF12UU를 하부에 고정해 물리 높이를 300 mm로 맞췄다.
- 처음 Cardan cross는 두 rod가 서로 관통하는 형상이었다. 실제 제작 가능한 50x50x6 6장 적층 block + opposed M8 trunnion으로 수정했다.
- fan/filter 가격을 로그인 화면에서 각각 5,489/660원으로 확인해 0원 행을 해소했다. 그 과정에서 old test가 unknown price를 기대해 1회 실패했고 expectation 수정 후 123개 전부 통과했다.
- LMF12UU/SK12/CR-3001 page는 완전한 mounting-hole pattern을 제공하지 않으므로 `NVR-P06/P09/P11/P12`는 outer cut만 하고 입고품으로 transfer-drill한다.

재생성 명령:

```powershell
& .\scripts\run_navimro_fabrication.ps1
```

남은 주문 gate는 액추에이터 실제 pin-center Lmin/Lmax, 양단 M8 암/수 형상과 물림 길이, JFT-8R 적합성, Hall/배선/전류/STEP, CR-3001 keeper/rating과 collar holding data다. 이 회신 전에는 주문제작·반품불가 액추에이터를 결제하지 않는다.

## 2026-08-27 그림 중심 조립 매뉴얼 Rev B

- 사용자 검토에서 기존 조립·발주 패키지의 8단계가 글로만 표현되어 부품의 실제 연결 순서를 알기 어렵다는 문제가 확인됐다.
- `scripts/render_navimro_assembly_guide.py`가 분해도 1장과 누적 조립 그림 8장을 실제 CadQuery 조립체에서 생성한다.
- 각 그림은 해당 단계 신규 부품을 주황색, 앞 단계 조립품을 반투명 회색으로 표시한다.
- `scripts/build_navimro_assembly_manual.py`가 12페이지 `output/pdf/NAVIMRO_visual_assembly_manual_revB.pdf`를 만든다.
- 페이지 구성은 전체 구조, 8단계 상세 조립, 전체 체결 확인, 현장용 한 장 순서표다.
- 마지막 순서표의 안내 문구가 첫 행 카드와 겹치는 것을 PDF 렌더 검토에서 발견해 제거했다. Cardan 확대도도 parallel scale 300에서 220으로 조정했다.
- `scripts/run_navimro_fabrication.py`에 조립 그림과 매뉴얼 생성을 연결했다.
- 확정되지 않은 vendor variant를 암시하던 CAD component 명칭 `DHLA2000_A1_envelope`를 `LA2000_pin_lug_planning_envelope`로 정정했다.
- 모든 CAD component가 정확히 하나의 조립 단계에 배정되는지 확인하는 회귀시험을 추가했고 전체 126개 시험이 통과했다.

## 2026-08-27 Fusion 360 상세 CAD Rev C

- 기존 CAD가 프레임과 구매품 외형 중심이라 볼트/너트 위치와 프로파일-철판 경계를 알기 어렵다는 사용자 피드백을 반영했다.
- `cad/navimro_detailed_assembly.py`에 T-slot 4040, 개별 profile joint plate, M5/M6/M8 screw, washer, T-nut, nyloc, pivot bolt, deck spacer와 모든 주요 철판을 모델링했다.
- neutral 기준 556개 component이며 187개 vendor-dependent component는 노란색 provisional 상태다.
- Fusion 전달물은 `output/NAVIMRO_Fusion360_detailed_CAD_revC.zip`이다. STEP 13개, render 4개, component manifest, BOM, fastener schedule, procurement gaps, provisional-interface list와 import README를 포함한다.
- CadQuery 역수입 검증: neutral 722 solids / 900x800x390 mm, module-only collapsed 664 solids / 900x800x292 mm.
- P06 riser 불일치를 200x50x6 x2로 수정했고 base angle x4와 M8 체결 x8을 추가했다.
- purchased U/H stack을 사용하는 Rev C에서 중복인 custom actuator yoke P02/P05를 active cut list에서 제거했다. Cardan/LMF 수량도 P07 x4, P08 x2, P09 x4로 CAD와 맞췄다.
- Cardan bridges, actuator bracket plates/base bolts, locator plates, latch spreaders/keepers를 상세화했다.
- 기존 단일주문 BOM에 없는 M5/M6 체결품, deck spacer, locator pin을 `NAVIMRO_revC_procurement_gaps.csv`에 기록했다.
- ZIP 26개 파일 CRC 검사 통과, artifact manifest 23개, 전체 회귀시험 132개 통과.
- native F3D는 Fusion 360 API 없이 직접 만들 수 없어 hierarchy/color를 포함한 STEP를 제공한다. Fusion에서 import 후 F3D로 저장한다.

## 2026-08-28 Fusion 360 액추에이터 조립 재검토

- 사용자가 Fusion에서 Rev C 접힘 조립체를 직접 열고 액추에이터 조립 방법이 명확하지 않다고 지적했다.
- Fusion 격리/근접 보기와 `cad/navimro_detailed_assembly.py`를 대조한 결과, 액추에이터와 U/H는 실제 상세부품이 아니라 공급자 확인 전 포락체임을 재확인했다.
- 더 중요한 문제로, 6 mm-hole IPS-B1/IPS-B2 후보에 M8 피벗을 모델링했고 U/H를 독립 두 부품이 아닌 한 rigid compound로 만들었다. 두 번째 직교 피벗, 실제 eye/adapter와 bore도 없다.
- 솔리드 교차 검사에서 actuator 1 기준 bracket/pin 약 603.186 mm3, lower bracket/lower spreader 약 3600 mm3, upper bracket/upper spreader 약 3800 mm3가 검출됐다. actuator body는 lower spreader와 약 18461.867 mm3 교차하고, actuator 2/3은 lower crossmember와 각각 약 16861.5 mm3 교차한다.
- 따라서 Rev C의 전체 방사형 개념은 유지하되 액추에이터 조립부는 제작 기준에서 철회한다. 공급자 STEP/도면 또는 입고 실측 후 한 개의 2축 조인트 카세트를 먼저 다시 모델링·검증하고 여섯 곳으로 복제한다.
- 상세 기록: `design_basis/fusion360_actuator_joint_review_2026-08-28.md`.

## 2026-08-28 Fusion 360 상세 CAD Rev D

- 공식 DIHOOL IPS-B1 U와 IPS-B2 H 도면을 다시 대조한 결과, 두 부품은 중첩형 2축 조인트가 아니라 각각 단일축 장착 대안임을 확인했다. Rev C 이후 잠정 제안했던 separate U/H 직교 스택도 철회한다.
- 활성 액추에이터 관절은 나비엠알오 `K02020097 / JMC JFT-8R` 구면 로드엔드 6개다. BOM의 U/H 행은 이력용 수량 0으로 유지한다.
- 각 액추에이터 끝은 `NVR-P03/P04` 받침판, `NVR-P16` 50x6x27 러그 2장, Ø8.2 관통구멍, 스페이서 2개, M8 피벗과 잠금너트, JFT-8R, provisional M8/A2 어댑터로 모델링했다.
- P16 러그는 Ø8 지그핀으로 동축을 맞춘 뒤 P03/P04 하부에 용접한다. 긴 노출 M8 나사봉은 허용하지 않고 실제 A2 형상에 맞춰 완전 나사물림과 잼너트를 적용한다.
- 하부 액추에이터 크로스멤버를 640 mm, 상부 엔드/크로스멤버를 660 mm로 수정해 프레임 장축재 사이의 기존 40 mm 빈틈을 제거했다.
- full sweep 결과: pin-center 269.040~394.209 mm, 1° 여유 포함 요구 관절각 10.852° < JFT-8R 13°. 예비 최대 축력 876.4 N, JFT 파단하중 여유 4.25배, pin/lug local screen 통과.
- collapsed/neutral/raised/max pitch/max roll/max pitch+roll 전 자세에서 세 액추에이터 포락체와 상·하부 프레임 간 솔리드 교차가 없고, M8 핀과 rod-end/lug/spacer 보어 간 고체 교차가 없다.
- 접힘 module-only STEP 역수입 결과 674 solids, valid, 900x800x300 mm. ACT1 cassette는 38 solids, valid로 복구된다.
- Rev D 중립 모델은 559개 이름 있는 컴포넌트다. STEP 17개, 렌더 5개와 CSV/README/구매·문의·전기제어 체크·DMD 공식 매뉴얼 검토·설계근거/manifest를 포함한 최신 ZIP은 37개 파일, 19,316,995 bytes이며 CRC 오류가 없다. SHA-256은 `0bc2e47336aa593b1dbe29d08c70a4ba8414ab8492cb9165f73e52147ebfa63a`다.
- 전체 회귀시험 138개가 최종 문서 정정 후 121.706초에 통과했다.
- Fusion 360 기존 Rev C 문서에서 Rev D cassette를 자동으로 열려 했으나 로컬 파일 선택 모달이 전면에 남아 자동화 창 핸들을 다시 얻지 못했다. Fusion 프로세스를 종료하거나 기존 문서를 변경하지 않았다. 동일 STEP는 CadQuery 역수입과 별도 CAD 뷰어에서 정상 표시를 확인했다.

현재 전달물:

- `output/NAVIMRO_Fusion360_detailed_CAD_revD.zip`
- `outputs/navimro_fusion360_revD/step/NAVIMRO_detailed_neutral_revD.step`
- `outputs/navimro_fusion360_revD/step/ACT1_complete_mounting_cassette_neutral_revD.step`
- `outputs/navimro_fusion360_revD/renders/actuator_joint_closeup.png`
- `design_basis/fusion360_actuator_joint_rebuild_revD_2026-08-28.md`

남은 발주 gate는 A2 실제 양단 M8 암/수 형상과 물림 길이, 공급자 pin-center Lmin/Lmax 및 STEP, Hall/배선/정격·기동·스톨전류, JFT-8R 입고치수에 따른 spacer/shoulder grip, CR-3001 keeper/rating, collar holding data다. 알려진 나비엠알오 소계는 VAT 포함 2,767,127원이며, 기존 100만원의 운송·가공·공구·소모품·예비비를 더한 계획합계는 3,767,127원, 400만원 상한 대비 232,873원 여유다.

## 2026-08-28 DIHOOL DHLA6000-A2 공식 페이지 확인

- 사용자가 제공한 공식 페이지는 `DHLA6000-A2 24V`이며, A2를 `평판 + M8 나사 설치형`으로 설명하고 중앙 알루미늄 튜브의 장착 헤드가 탈착·교체 가능하다고 명시한다.
- 페이지에는 24 V 기준 2.25 A 표시, 72 W 제품군, 선택형 Hall, 내장 리미트, IP43, 10% duty/연속 2분과 30,000회 이상 수명이 기재돼 있다.
- `DHLA6000-A2.STEP` 다운로드 항목도 있으나 직접 링크는 확인 당시 HTTP 403으로 접근되지 않았다. 판매처 문의문에 정확한 납품품 STEP 자체를 첨부해 달라는 요청을 추가했다.
- 이 자료는 나비엠알오 상세 이미지의 의미를 해석하는 근거일 뿐, 현재 BOM의 `K92931811 / LA2000-125150`이 DHLA6000이라는 증거가 아니다. DHLA2000/6000, A1/A2, 12/24 V를 혼용하지 않는다.
- Rev D CAD는 변경하지 않았고 `A2_M8_INTERFACE_PROVISIONAL`을 유지한다. 판매처가 실제 모델, 양단 M8 암/수와 물림 길이, 포함 평판/어댑터, pin-center Lmin/Lmax, 전류·배선·Hall과 STEP를 회신한 뒤 최종화한다.

## 2026-08-28 NAVIMRO 납품 액추에이터 사양 확정

- 사용자 확인에 따라 `K92931811 / LA2000-125150`의 납품 사양은 DC 12 V, 2000 N, 스트로크 150 mm, 속도 5 mm/s다.
- 네 항목을 Rev D 확정 입력으로 승격하고 주 액추에이터 버스를 12 V로 확정했다. 기존 Firgelli 후보값과 DHLA6000 24 V/6000 N/72 W 값은 Rev D 구매·전원·CAD 입력에 사용하지 않는다.
- 2000 N은 제품 정격값이며 완성 조립체의 허용하중이나 안전 인증을 의미하지 않는다. 현재 계산상 최대 액추에이터 축력은 약 876.4 N이지만 실제 하중·듀티·동기 시험은 별도다.
- 아직 남은 공급자 확인사항은 정확한 제조사 세부 형식과 A1/A2, 양단 M8 암/수·물림 길이, 포함 평판/어댑터, pin-center Lmin/Lmax, Hall/배선, 정격·기동·스톨전류와 납품품 STEP다.

## 2026-08-28 DHLA6000-A2 12 V/24 V 기계부 비교

- 공식 12 V A2와 24 V A2 페이지는 같은 외형도 이미지, 같은 A2 설치 설명, 같은 `DHLA6000-A2.html`과 `DHLA6000-A2.STEP` 파일명을 사용한다.
- 페이지 표시전류는 12 V 4.5 A, 24 V 2.25 A로 다르다. 이 조합은 DHLA6000-A2 내부에서 모터 전압형만 나뉘고 기계 하드웨어는 공유할 가능성이 높다는 강한 근거다.
- 제조사가 전압형 간 기계부 동일성을 문장으로 명시한 것은 아니므로 inference로 기록한다.
- 이 결론은 DHLA6000 제품군 내부에만 적용한다. 선택품 `LA2000-125150`의 2000 N/5 mm/s 조합은 DHLA6000 사양표의 2000 N/15 mm/s와 다르므로, DHLA2000과 DHLA6000의 외형·양단 부품까지 같다고 보지 않는다.

## 2026-08-28 전원·제어 구매 완성도 점검

- 현재 시험대는 배터리식이 아니라 `220 VAC -> 2P 차단기 -> NES-350-12 -> 12 VDC` 구조다. 배터리, BMS, 충전기와 배터리 함체는 의도적으로 제외했다.
- BOM E001~E024에는 DMD-150 3개, Mega2560 PRO, BNO055, 5 V DC-DC, 12 V/29 A PSU, 모터별 DC 차단기, AC 차단기, 단자대, 전력·제어선, 접지선, 함체, 글랜드, 페룰, 냉각과 PCB 지지물이 들어 있다.
- 전용 안전등급 비상정지와 주접촉기는 사용자 승인 정지 시험 축소범위에서 제외했다. 2P AC 차단기는 감독자가 접근 가능한 전원 차단일 뿐 안전등급 E-stop으로 부르지 않는다.
- 후속 제조사 자료 조사로 DMD-150 로직/브레이크 정의는 닫혔다. 확인값은 DC 6.5~41 V, 무냉각 연속 12 A, 단순 냉각 시 15 A, 12 V 180 W, 3.3/5 V TTL 호환, IN1/IN2/PWM이며 `00=brake`, `11=floating/coast`다. 전부하 방향전환 전 약 0.1초 brake와 완만한 PWM 변경을 적용한다.
- DMD-150 매뉴얼은 하강·제동 회생에 의해 SMPS 과전압 보호가 동작할 수 있다고 경고하고 모터단 양방향 TVS를 권장한다. 예시 `1.5KE24CA`의 정확한 나비엠알오 SKU는 찾지 못했으므로 통합견적 문의와 loaded-lowering bus-overshoot 시험 gate를 추가했다.
- 아직 없는 것은 납품 액추에이터의 확정 Hall/limit pinout, 정격·기동·스톨전류, 최종 TVS/회생보호 품목, 최종 배선도·단자번호·하네스와 제어 펌웨어다. 따라서 `구매 하드웨어 대부분 포함`이지 `즉시 통전 가능` 상태는 아니다.
- 상세 체크리스트는 `procurement/electrical_control_completeness_2026-08-28.md`이며 Rev D ZIP에도 포함한다.

## 2026-08-28 전체 조립성 검증 및 Fusion 360 상세 CAD Rev E

- 사용자 요청에 따라 Rev D를 단순 시각 확인이 아니라 실제 B-rep 조립 시험으로 재검토했다. 기존 검사는 액추에이터-프레임 충돌 위주였고 중앙 카단, LMF/SK 구멍, 상판 체결, 조립 순서와 공구 접근을 충분히 다루지 않았다.
- Rev D에서 상부 중앙 420 mm 프로파일 교차, 한 중심을 관통하는 카단 X/Y 핀, 잘못 놓인 SK12, LMF/SK/상판 구멍 누락, 부싱을 통과해야 하는 축 칼라, 하부 프레임을 관통하는 축, 50 mm 평철로 만들 수 없는 50 x 64 스토퍼와 아크릴 내부에 겹친 5 mm 스페이서를 발견했다.
- Rev E는 평행 상부 중앙 레일, Z로 12 mm 분리한 직렬 카단, 4층 50 x 50 x 24 블록, 실제 보어, 단일 240 mm 캐리지, 230 mm 축 2개, 고정 LMF12UU 4개, 이동 SK12 2개와 분할 평철 스토퍼를 사용한다.
- 가이드 리저는 축에서 외측 40 mm로 옮기고 P09를 50 x 76 mm 전사 드릴 탭으로 바꿨다. 고정 스토퍼는 SK M4 볼트 머리 밖에 두고 이동 패드는 50 x 32 및 50 x 40 조각으로 나눴다.
- 상판은 Ø18.2 구멍과 ID8.6/OD18/L15 압축 슬리브 16개를 사용한다. 와셔를 상면으로 옮기고 축 상단 위치를 1 mm 조정해 연결 전 모듈 포락체를 900 x 800 x 300 mm로 맞췄다.
- Z 0~100 mm를 10 mm 간격으로 검사하고 최대 pitch/roll 자세를 더한 14개 자세에서 가이드 충돌 0, 액추에이터-중앙부 충돌 0, 축/핀/나사/슬리브 보어 간섭 0이다. 접힘/상승 스토퍼 여유는 각각 2 mm, 카단 핀 솔리드 간격은 4 mm다.
- 카트 결합 그룹은 실제 카트 치수가 없어 조립 판정에서 제외했다. 상부와 함께 움직이던 잘못된 변환을 제거하고 모듈 아래 56 mm 떨어진 정적 provisional 참조로 표시했다.
- Rev E 중립 조립체는 580개 이름 있는 컴포넌트다. 전체 테스트 148개가 274.842초에 통과했다. STEP 역수입은 중립 757 solids/valid, module-only collapsed 699 solids/valid/900 x 800 x 300 mm다.
- 최종 ZIP은 39 entries, 20,882,315 bytes, CRC 오류 없음이며 SHA-256은 `9d08f6788eb7dc8ce2fd57736646e82d5770bc86cc7ef8ee643ed6967a7396fb`이다.

현재 전달물:

- `output/NAVIMRO_Fusion360_detailed_CAD_revE.zip`
- `outputs/navimro_fusion360_revE/step/NAVIMRO_detailed_neutral_revE.step`
- `outputs/navimro_fusion360_revE/step/NAVIMRO_module_only_collapsed_revE.step`
- `outputs/navimro_fusion360_revE/NAVIMRO_revE_assembly_audit.json`
- `design_basis/fusion360_assembly_validation_revE_2026-08-28.md`

발주 수량은 240 mm 캐리지 1개, SK12 2개입 1팩, 축 칼라 0개로 수정됐다. 현재 가격이 있는 소계는 VAT 포함 2,687,993원이다. A2 실제 양단 형상/STEP, LMF12UU/SK12 실물 구멍, M4 체결품 SKU, 상판 슬리브, JFT-8R 스페이서/어깨볼트, TVS와 카트 결합 치수가 닫히지 않았으므로 아직 일괄 발주 상태는 아니다.

## 2026-08-28 제조사 자료 심화 재조사

- DIHOOL `DHLA2000` 공식 페이지는 12 V 계열에서 5 mm/s와 2000 N 조합, 내장 리미트, 10% duty 및 최대 연속 2분을 확인시킨다. A1 페이지 제품요약에는 `Current: 5 Amp`가 표시되지만 A2 페이지에는 없고 정격/최대/기동/스톨 정의도 없어 예비 전류 스크린으로만 사용한다. Hall과 limit feedback은 선택사양이므로 `K92931811` 납품품 포함 여부는 계속 판매처 서면 확인 대상이다.
- Motorbank 공식 DMD-150 매뉴얼과 Arduino 예제를 `references/vendor_downloads/`에 저장하고 제어 truth table, 로직 레벨, 12 V 출력 정격과 회생 주의사항을 설계 기준에 반영했다.
- 시행착오 정정: 초기 BOM은 판매페이지의 포괄 표기 `15 A / 360 W`를 그대로 사용했고 DMD 입력·브레이크를 미확정으로 남겼다. 공식 매뉴얼 기준 360 W는 24 V 값이며 12 V에서는 180 W다. 제어 논리는 확정됐지만, 회생 TVS가 BOM에서 빠져 있었음이 새로 확인됐다.
- DIHOOL 페이지에 공개된 DHLA2000 A2 STEP/PDF 링크 경로까지 확인했으나 파일 서버가 직접 요청을 HTTP 403으로 거부했다. 공급자에게 실제 납품품 파일 자체를 첨부해 달라는 요청은 유지한다.

## 2026-09-01 나비엠알오 실상품 후보 매핑

- 최신 Rev D의 구조재, 조인트, 체결품, 가공 원소재와 24 V 시험 전장을 나비엠알오 상품코드에 연결한 후보 BOM을 `procurement/profile_radial_revd_navimro_candidate_bom_2026-09-01.csv`와 같은 이름의 설명 문서에 기록했다.
- 현재 상품코드가 확인된 후보 소계는 VAT 포함 1,220,131원이다. 비엔코더 LM4075-F 3개와 6 mm AL5052 대체판까지 단순 합산하면 1,591,887원이지만 두 품목은 현재 설계의 동등품이 아니므로 주문 승인값이 아니다.
- 정확한 `LM4075OE-1075 24 V/100 mm/5 V encoder`, 8 mm 가공 원판, M8x28 스탠드오프는 나비엠알오 특별견적이 필요하다. LMB-10 핀 포함품, JFT-6R CAD 치환, 축별 DC 보호와 DMD-150 회생보호도 발주 전 게이트로 유지한다.
- 400만원 예산 안에 들어갈 가능성은 높지만 단일 주문 조건은 아직 충족하지 않는다. 공급 도면과 전류 데이터를 받은 뒤 Fusion Rev D.1 재검증과 최종 견적 대조를 거쳐야 하며 `purchase_release=false`, `fabrication_release=false`다.

## 2026-09-01 공급처 분할 구매 전환 - 당시 판정, 후속 감사로 승인 철회

- 사용자가 나비엠알오 단일 주문 제약을 해제하고 설계 기준품을 공급처별로 주문하기로 결정했다. 이전 일괄 주문 `NO-GO`는 시행착오 기록으로 유지하지만 최신 구매 지시는 아니다.
- LM4075OE-1075 24 V/100 mm/encoder 5 V는 MotionGearOn, LMB-10은 Motorbank, THK PHS6은 SpeedMall에서 산다. LM4075-F, JFT-6R, 6 mm 어댑터 대체안은 폐기했다.
- 당시에는 A6061 가공품과 45개 나비엠알오 행, `1.5KE24CA`, 5 A 퓨즈를 공급처별로 주문하는 안을 만들었다. 후속 감사에서 45개 행 중 12개 조건부 행과 24 V TVS 부적합 가능성을 찾아 이 발주 절차는 폐기했다.
- 당시 화면가 소계 1,629,755원은 확정 주문가가 아니다. TVS를 제외한 화면가 스크린은 1,618,871원이지만 가공·배송·확정 보호회로와 미해결 조건을 포함하지 않는다.
- 공급처를 나누는 방향만 유지한다. 현재 기준은 `procurement/profile_radial_revd_order_readiness_audit_2026-09-01.md`이며 `purchase_release=false`, `fabrication_release=false`다.
