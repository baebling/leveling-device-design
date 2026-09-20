# 2026-09-05 최신 우선순위 — 최소 수동 시제품
> SUPERSEDED: 같은 날짜의 후속 사용자 결정으로 턴버클 Rev M2가 재활성화되었다. 현재 기준은 `current_turnbuckle_priority_2026-09-05.md`다. 아래 M3는 비교 이력이다.
상태: PHASE 1 CONCEPT / PRELIMINARY — NOT APPROVED FOR FABRICATION

## 사용자 결정과 실행 가정
사용자는 연구과제 미선정, 제한된 작업시간, 기자재 구매 제한 때문에 빠른 마무리와 재료 중심 조달을 원한다. 기계식을 1순위로 전환하고 기존 구조에 얽매이지 않는 단순 설계를 요청했다.
- 1순위: MANUAL_CROSSED_HINGE_M3_CONCEPT — 직교 2축 경첩 + 조절나사 2개.
- Rev M2와 전동 Rev E는 비교/복귀용 보관안. 기존 BOM을 현재 주문표로 사용하지 않는다.
- 이번 실행 가정: 독립 Z 상승, 자동 수평보정, 전장 제외. 수동 pitch/roll ±3° 조절 후 고정.
- 고정된 실내 시험대에 볼트로 장착하고 무부하로 조절한 뒤 10 kg 시험하중을 얹는 시연.
- 실제 카트 체결은 실측 인터페이스를 사용해야 한다. 소형 모듈 시험과 카트 통합 완료를 구분한다.
- 700 mm 외곽, 250~300 mm 높이는 재사용 의무가 아니다. 새 300 mm급 예시는 계산 가정이며 실제 카트 크기가 아니다.
- 기자재/재료비 분류 및 성과 축소 수용 여부는 담당자 확인 전이다. 기계부품이라고 재료비 인정된다고 단정하지 않는다.
- 예산 상한 4,000,000원. 소진 목표 없음. 견적 전 가격/납기/공급처 확정하지 않는다.

## 자유도와 한계
독립 운동은 pitch/roll 두 축, 두 조절나사 잠금 후 0축을 목표로 한다.
X/Y/yaw의 독립 자유도는 경첩 연결로 구속한다. 다만 떨어진 경첩축 때문에 상판 중심 X/Y/Z는 기울기에 따라 종속 이동한다.
X/Y가 절대 이동하지 않아야 한다는 해석에는 이 안이 부합하지 않는다. 중심 고정이 필수로 확인되면 교차축 피벗 구조로 재검토하고 단순성/수고를 다시 비교한다.

## 현재 판정
CONCEPT_SELECTED_FOR_REVIEW = TRUE
DETAILED_CAD_STARTED = FALSE
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
PHYSICAL_TESTS_EXECUTED = FALSE

새 개념 상세설계는 현행 AGENTS.md의 APPROVE CONCEPT 게이트를 따른다.
개념 문서: concepts/manual_crossed_hinge_m3_2026-09-05.md
계산: outputs/calculations/manual_crossed_hinge_m3_screen_2026-09-05.json
