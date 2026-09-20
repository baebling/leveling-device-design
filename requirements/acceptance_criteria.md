# Phase 1 승인 기준

개념 승인 전 다음 조건을 모두 검토한다.

- [x] 최신 프롬프트, PDF, 참고 이미지 2개를 확인했다.
- [x] 설계 범위와 제외 범위를 분리했다.
- [x] 실제 카트 치수를 이미지에서 추정하지 않았다.
- [x] 3점, 4점, 리프트/2축 분리형을 동일 기준으로 비교했다.
- [x] 3점 방식에서 X/Y/Yaw 구속 메커니즘을 포함했다.
- [x] ±3°, ±5°, ±8°와 0/50/100 mm 리프트 조합의 개념 스트로크를 계산했다.
- [x] 하중, 카트 질량, 편심 및 인장 반력 위험을 표시했다.
- [x] 수축/중립/완전 상승 높이를 범위값으로 보고했다.
- [x] 카트 결합부에 반복 정렬, 들림 방지, 무전원 유지, 센서 확인 개념을 포함했다.
- [x] 독립 기계식 스토퍼와 전기 리미트를 구분했다.
- [x] 필수 5종 개념도와 전체 모듈 평면도 1종, 미해결 질문을 제공했다.
- [x] 상세 CAD/제작도/제어코드로 진행하지 않았다.
- [x] HRT8E-style lower bracket is narrowed only to the JNT-BR-01 preliminary centered double-shear seed; no fabrication geometry was released.
- [x] YAW-A physical axis order, yaw-heading constraint screen, and total-tilt/per-pin stop interpretation are documented.
- [x] WS-01-H20 combined 0/50/75/100 mm and nine-corner +/-3 degree workspace passes a 15 mm soft-end reserve and guide-overlap screen.
- [x] Static-bench command limits, factory built-in electrical endpoints, and independent physical-stop boundaries are separated.
- [ ] V-01 selected Firgelli eye/pin-stack measurement and JNT-CG-01 two-axis no-contact gauge are recorded.
- [ ] V-02 YAW-A guide/yoke no-bind, stop-contact, and yaw-freeplay mock-up is recorded.
- [ ] V-03 real actuator built-in endpoint, mechanical-stop reserve, and repeatability check is recorded.
- [ ] V-04 CR-01-H4 30-cycle receiver mock-up is recorded.

## 승인 후 Phase 2 진입 조건

다음 사용자 입력이 있어야 한다.

`APPROVE CONCEPT`

승인 시에도 새 카트 인터페이스 치수, 질량 분리, 보정각 작업공간, 높이 포락선 상세 여유가 미확정이면 해당 값을 파라미터로 유지한다. 현재 사용자 확인 기준은 10 kg 적재, 약 10 kg 카트, 연결 전 장치 높이 250~300 mm, Pitch/Roll ±3°이다.

2026-08-25 현재 카트측 리시버는 CR-01 2-레일 알루미늄 프로파일 후보, CR-01-H1 하드포인트 후보, CR-01-H2-B 연결/포지티브 스토퍼 토폴로지, CR-01-H3 연결 스택 규칙, CR-01-H4-S1 목업 하드웨어 시드로 좁혔지만, 이는 Phase 1 배치/하드포인트/토폴로지/스택/하드웨어 후보이며 제작 승인값이 아니다. 정확한 슬롯너트, 백킹플레이트, 인서트판, bushing fit, locator/rest pad/latch keeper 상세, stop screw/dowel/keyed plate, latch model, latch-closed/cart-present sensor는 `APPROVE CONCEPT` 전까지 미확정으로 유지한다.

JNT-BR-01-HRT8E는 Phase 2 상세 시드로 갱신되었다. 공식 8 mm bore, 23 mm body, 11 mm eye, 14 deg 자료를 반영해 8 mm pin/lug와 18 mm supported span을 사용한다. 수치 포락선은 통과하지만 실제 HRT8E, 스페이서, 핀 고정, 브래킷 체결/접합, edge distance, fatigue/shock 및 14 deg 무간섭 목업은 여전히 미확정이다.
