# Manual 3-RPS M2R2-S220

승인된 개념을 장바구니 미스미 대체품으로 치환한 Phase 2 CAD 검토본이다. 하부 관절을 기존 4080 슬롯 안쪽으로 옮겨 700×700×299.2 mm 중립 형상을 만들었다. 사용자 가공은 없고 프로파일 길이 지정만 필요하다. 현행 사용범위는 상부 패널 없이 알루미늄 프로파일을 노출하고 카트와 적재물을 올리지 않는 자중 전용 감독하 시연이다.

## 검증 결과

- ±3° 169자세: 링크 265.42~293.31 mm, 구속 랭크 3/잠금 랭크 6
- 대표 9자세: 예상 밖 부품 교차 0, 형상 오류 0
- 중립·±3° 복합자세 공구축: 예상 밖 방해 0
- STEP 3개 재읽기: 유효 형상 및 부피 일치
- A2 하부 SHAT12를 180° 돌려 인접 A3와의 M4 공구축 충돌을 제거함

## 파일

- `step/M2R2S220_NEUTRAL.step`: 중립 전체 조립체
- `step/M2R2S220_P3_R3.step`: pitch +3°, roll +3°
- `step/M2R2S220_SINGLE_LINK.step`: 한 축 상세
- `renders/`: 중립, 복합자세, 노출 링크, 한 축 이미지
- `M2R2S220_AUDIT.json`: 자세·간섭·공구·STEP 검증
- `FASTENING_STACK_AUDIT.json`: M5/M8 체결 깊이 검토
- `BOM.csv`: 주문 목록과 미결 품목
- `ASSEMBLY.md`: 위치와 조립 순서

IKO PHS12L은 공식 카탈로그의 보수 허용 편각8°가 계산 요구1.95°를 만족한다. 사용자 결정으로 독립 과조절 스토퍼, 전용 받침, 전용 시험대 고정품과 카트 래치는 현행 구매에서 제외한다. 이는 기계식 스토퍼나 하중 안전성이 검증됐다는 뜻이 아니다. 남은 구매 전 항목은 활성 20행 재검산과 최종 견적이다. 따라서 `PURCHASE_RELEASE=FALSE_PENDING_FINAL_QUOTE`, `FABRICATION_RELEASE=FALSE`다.

구매 전 점검: `../../verification/m2r2s220_no_cart_pre_purchase_audit_2026-09-07.md`

`PRELIMINARY PoC DESIGN — NOT APPROVED FOR FABRICATION — REQUIRES MECHANICAL ENGINEERING REVIEW`
