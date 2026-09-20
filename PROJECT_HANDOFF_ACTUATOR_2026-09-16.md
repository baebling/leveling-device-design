# 액추에이터형 전환 인수인계 — 2026-09-16

## 한 줄 현황

산단 요청으로 수동 턴버클형 구매는 보류하고, 기존에 가장 많이 검증된 전동 3-RPS Rev E를 출발점으로 액추에이터형 요구조건과 BOM을 다시 확정한다. 현재 구매·제작·배선·통전 승인은 모두 `false`다.

## 가장 먼저 읽을 파일

1. `requirements/current_variant_priority_2026-09-16.md` — 현재 우선순위와 재개 게이트
2. `references/수평유지장치 요구사항.txt` — 전체 요구사항과 결정 이력
3. `verification/RevE_PoC_release_candidate_audit_2026-09-04.md` — 전동안 디지털 검증과 열린 위험
4. `logs/reve_poc_implementation_2026-09-04.md` — 구현 결과와 산출물 위치

이 문서와 2026-09-16 우선순위 문서가 2026-09-07 이후의 수동 우선순위 기록보다 최신이다. 이전 기록은 삭제하지 말고 설계 이력으로만 사용한다.

## 최신 결정과 해석

- 사용자 전달: “산단에서 액추에이터 버전으로 하라고 하네요.”
- 현행 해석: 전동 액추에이터 방식으로 전환한다.
- 산단이 다른 조건을 바꿨다는 정보는 없으므로, 우선은 카트·적재물·사람이 없는 자중 전용 공개형 시연 범위를 유지한다.
- 기존 수동안에서 생략했던 독립 과조절 스토퍼는 전동 구동에 그대로 생략 적용하지 않는다.
- 새 요구조건이 닫히기 전에는 기존 Rev E 형번도 최종 발주품으로 확정하지 않는다.

## 재활성화할 기준안

`POWERED_PROFILE_RADIAL_3RPS_REVE_POC_RC1`

- 기구: 3-RPS, Z/pitch/roll 허용, X/Y/yaw 구속
- 기존 액추에이터 후보: `LM4075OE-1075` 3개
- 기존 주요 전장 후보: MDD10A 2개, Mega2560 호환 보드, MPU6050, LRS-350-24, 5 V DC-DC
- 과거 운동범위: Z 0/25/50 mm, pitch/roll -3/0/+3°
- 주의: 과거 10 kg 합격조건은 현행 요구사항이 아니다. 산단이 시험하중을 요구하는지 먼저 확인한다.

### 이미 존재하는 핵심 산출물

- RC 전달 ZIP: `output/Profile_Radial_3RPS_RevE_PoC_RC1_2026-09-04.zip`
- 실제 공급자 반영 Fusion: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`
- 액추에이터 STEP: `references/vendor_cad/LM4075OE-1075-100mm.stp`
- 후보 BOM: `procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv`
- RC 제작자료: `fabrication/profile_radial_revE_release_candidate_2026-09-04`
- RC 전장/기타 산출물: `outputs/profile_radial_revE_poc_release_candidate`
- 검증 감사: `verification/RevE_PoC_release_candidate_audit_2026-09-04.md`
- 과거 시험 프로토콜: `verification/RevE_PoC_test_protocol_2026-09-04.md`

## 기존 전동안의 검증 수준

- 27자세 운동학·간섭 디지털 검사 통과
- 핀 거리 210.771741~276.937115 mm
- PHS6 최대 편각 4.096369°
- 예상 밖 Fusion 간섭 0건
- DXF 9개, 제작 PDF 9장, 홀/절단/조립 자료 존재
- 전장 회로·단자·하네스·I/O 및 제어함 후보 자료 존재
- Mega 펌웨어 컴파일 완료: flash 15,296 bytes, SRAM 901 bytes
- 당시 회귀시험 226개 및 RC 시험 10개 통과

이는 구매·제작 가능성을 높여 주는 디지털 증거일 뿐 실제 제품 정격, 배선, 물리 간섭, 전류, 하중, 안전 합격을 의미하지 않는다.

## 반드시 남아 있는 위험

- `LM4075OE-1075`의 정격/기동/스톨 전류, 정확한 엔코더 배선·레벨, 내장 리미트 동작, 듀티사이클
- LMB-10 공급자 도면 또는 초도품 실측
- 제어함 백플레이트와 PCB 실장홀의 실물 대조
- 독립 기계식 종단 스토퍼, 비상정지, 전원 차단 및 회생에너지 처리
- 1축 샘플시험과 3축 자중시험
- 산단이 요구하는 자동수평 여부, 시험하중, 납기와 제출물

## 수동 MISUMI 구매안 상태

수동안은 삭제하지 않고 비교·재사용 검토용으로 보관한다.

```text
STATUS = HOLD_DO_NOT_SUBMIT_OR_ORDER_PENDING_ACTUATOR_REBASELINE
QUOTE_NO = EA11159E2F
QUOTE_DATE = 2026-09-15
QUOTE_VALID_UNTIL = 2026-10-15
SUPPLY = 1,084,910 KRW
VAT = 108,491 KRW
DELIVERY = 2,500 KRW
DELIVERY_DISCOUNT = -2,500 KRW
TOTAL = 1,193,401 KRW
```

- 당시 미스미 견적과 엑셀은 20개 품목·수량이 일치하는 것으로 검토했다.
- 현재 폴더에서 가장 최근 수정된 관련 통합문서는 `outputs/quote_materials_20260915/2026 BIZ-Lab 창업클럽 시제품 재료비관리 현황_SAFELOCK.xlsx`다.
- 과거 PDF 견적 원본은 이전 대화에서 검토됐지만, 이 인수인계 작성 시점에는 사용자가 처음 제시한 Downloads 경로에서 확인되지 않았다. 위 금액은 검토 기록값이다.
- 20개 수동 품목 중 전동안에서 재사용할 수 있는 품목과 불필요한 품목을 새 BOM과 행별로 대조해야 한다. 전부 재사용 가능하다고 가정하지 않는다.

### 보류 중인 수동 20품목

| 형번 | 수량 |
|---|---:|
| PHS12A | 3 |
| HNT3-ST-M12 | 6 |
| HFS8-4040-700 | 4 |
| HFS8-4040-620 | 4 |
| HFS8-4080-620 | 2 |
| HFS8-4080-450 | 2 |
| HBLSSB8-SET | 24 |
| SHAT12 | 12 |
| SFU12-100 | 6 |
| SCSJ12-6 | 12 |
| HNTT8-5 | 24 |
| CB5-16 | 24 |
| FWSSB-D9-V5.5-T1 | 24 |
| PCIMR12-18-1.0 | 2팩(팩당 30개) |
| CIMR12-18-0.5 | 6 |
| CIMR12-18-0.2 | 12 |
| STB-M12 | 3 |
| BJ761-12011N | 3 |
| NTFL12-36 | 3 |
| HNT1-ST-M12 | 3 |

공구류 `13013`, `NA530-150S`, `TMRU-24`, `SBW-9G`는 기존 엑셀과 구매안에서 제외한 상태다.

## 다음 채팅에서 할 일

1. 산단 요구를 최소 질문으로 재확인한다: 자동수평 여부, 동작범위, 시험하중, 카트 결합 범위, 제출기한.
2. Rev E와 새로운 요구를 비교해 변경점을 표로 만든다.
3. `LM4075OE-1075` 및 제어부의 현재 판매처, 가격, 재고, 납기, 부가세, 배송비와 공급자 기술자료를 다시 확인한다.
4. 수동 20품목과 전동안 BOM의 재사용/불용/신규구매 차이표를 만든다.
5. 전체 주문 전에 1축 샘플 구매·시험이 필요한지 판정한다.
6. 요구사항, BOM, 시험계획이 서로 일치한 뒤에만 최종 구매 승인을 요청한다.

## 새 채팅에 붙여넣을 시작 프롬프트

```text
이 프로젝트는 수평유지/승강 상부 모듈입니다. 산단 요청으로 2026-09-16부터 수동 M2R2-S220 구매를 보류하고 액추에이터형으로 전환했습니다.

먼저 다음 파일을 읽고 그 내용을 최신 기준으로 사용해주세요.
1) requirements/current_variant_priority_2026-09-16.md
2) PROJECT_HANDOFF_ACTUATOR_2026-09-16.md
3) references/수평유지장치 요구사항.txt
4) verification/RevE_PoC_release_candidate_audit_2026-09-04.md

기존 전동 3-RPS Rev E를 출발점으로 사용하되, 기존 형번을 바로 발주하지 마세요. 우선 산단 요구 중 자동수평 여부, Z/pitch/roll 범위, 시험하중, 카트 결합 범위, 제출기한을 확인하고 요구사항 재기준화와 수동 MISUMI 20품목 대비 BOM 차이 감사를 진행해주세요. 현행 기본 가정은 카트·적재물·사람 없음, 상판 없는 공개형, 자중 전용 시연입니다. 구매·제작·배선·통전은 모두 미승인 상태입니다. 실제 카트 치수나 하중은 추정하지 말고, 불확실한 값은 매개변수와 미결정 항목으로 기록해주세요.
```

