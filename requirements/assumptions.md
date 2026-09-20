# 가정 및 임시 파라미터

> 2026-09-05 최종: 현재는 `current_turnbuckle_priority_2026-09-05.md`와 `../design_basis/manual_revm2_minimal_completion_2026-09-05.md`를 따른다. 아래 M3 300 mm 예시는 보관되었다. Rev M2 700 mm 외곽/지지반경은 기존 모델 기준으로 재사용하되 실제 카트 치수로 간주하지 않는다. 기존 20 kg 총질량 가정, 부시/핀, 압축 정격과 잠금부품을 재확인해야 한다.

> 2026-09-05: 아래의 과거 활성 가정은 역사 자료다. 현재는 `current_manual_priority_2026-09-05.md` 및 `../concepts/manual_crossed_hinge_m3_2026-09-05.md`의 M3 가정을 따른다. 300 mm급 외형, 250 mm 레버암, 총 이동질량 15/25 kg는 예시이며 실측값/제작치수가 아니다. 독립 상승 제외 및 카트 통합 수준 축소는 실행 가정이다. 종속 중심 이동, 경첩/클램프 정격, 비용비목 및 성과 인정은 미확정이다.

2026-09-01 사용자의 수동 조절식 PoC 전환이 아래의 전동 액추에이터 관련 가정보다 우선한다. 현재 활성 가정은 `requirements/current_manual_scope_2026-09-01.md`와 `design_basis/manual_adjustable_3rps_baseline_2026-09-01.md`를 따른다. LM4075OE, DMD-150, IMU와 24 V 전장은 역사 비교 및 향후 전동화 자료다.

아래 값은 실제 치수나 구매 확정 사양이 아니라 Phase 1 비교 계산용이다. 상세설계 전에 현물 입력값으로 교체해야 한다.

## 1. 기준 입력

| 파라미터 | Phase 1 값 | 상태/근거 |
|---|---:|---|
| `platform_length_mm` | 700 | 최소 PoC 외곽 후보; 알루미늄 구조 상세 전 예비값 |
| `platform_width_mm` | 700 | 최소 PoC 외곽 후보; 알루미늄 구조 상세 전 예비값 |
| `disconnected_device_height_mm` | 250-300 | 2026-08-25 사용자 확인 |
| `collapsed_height_target_mm` | 250 preferred, 300 max envelope | 250 mm 우선, 필요 시 300 mm까지 허용 |
| `lift_target_mm` | 50 | 2026-08-31 LM4075OE 100 mm stroke 선택에 따른 활성 PoC 기준 |
| `payload_cases_kg` | 5, 10 primary; 20 archive | 10 kg 사용자 확인 |
| `cart_mass_cases_kg` | 10 primary; 20, 30 archive | 빈 카트 약 10 kg 사용자 확인 |
| `cart_receiver_layout` | CR-01 two-rail aluminum profile receiver seed | 사용자 선호 반영, 제작치수 아님 |
| `cart_receiver_zone_mm` | 760 x 560 | Phase 1 리시버 존 스크리닝 시드 |
| `cart_receiver_hardpoint_seed` | CR-01-H1 | locator/rest pad/latch keeper 1차 하드포인트 스크리닝, 제작치수 아님 |
| `cart_receiver_connector_seed` | CR-01-H2-B | T-slot clamp/adjustment plus shoulder/key/positive stop topology, 제작치수 아님 |
| `cart_receiver_connector_stack` | CR-01-H3 | hardpoint-specific stack rules and service access, 제작치수 아님 |
| `cart_receiver_hardware_seed` | CR-01-H4-S1 | mock-up hardware seed and first-order local screens, 제작치수 아님 |
| `actuator_bracket_seed` | JNT-BR-01-HRT8E | centered double-shear bracket seed; HRT8E drawing and physical clearance check required, 제작치수 아님 |
| `moving_structure_mass_kg` | 15-22 | 저하중 PoC 범위, BOM 전 미확정 |
| `gravity_m_s2` | 9.80665 | 표준중력 |
| `preliminary_safety_factor` | 2.0 | 정지/저속 PoC의 개념 비교용, 최종 안전율 아님 |
| `manual_strut_pin_range_mm` | 205-305 | 수동 스트럿 예비 포락체; 실제 스크루와 조인트 선정 전 미확정 |
| `manual_strut_required_range_mm` | 212.137-297.864 | Z 0-50 mm, pitch/roll +/-3 deg의 기존 27자세 이상모델 결과 |
| `archived_powered_actuator` | LM4075OE-1075, DC 24 V, 750 N push, 100 mm stroke, 5 V encoder | 현재 주문 금지; 향후 전동화 참고용 |

## 2. 권장 3점 방식의 임시 좌표

플랫폼 중심을 원점으로 두고 상부/하부 조인트의 중립 X/Y 좌표를 동일하게 둔다.

| 지지점 | X (mm) | Y (mm) | 역할 |
|---|---:|---:|---|
| A1 | 0 | +250 | 전방 중앙 |
| A2 | -216.5 | -125 | 후방 좌측 |
| A3 | +216.5 | -125 | 후방 우측 |

- 접힘 기준 액추에이터 핀 중심 간 수직거리 후보 `d0 = 230 mm`는 100 mm stroke의 205~305 mm 범위에 Z 0~50 mm와 pitch/roll ±3°를 약 7.14 mm 양단 여유로 넣기 위한 값이며, 현물 적층 후 확정한다.
- 중앙 카단은 사용하지 않는다. 상·하 조인트 X/Y 좌표가 동일한 3-RPS 이상모델에서 상판 중심을 자세 기준점으로 둔다.
- 회전 순서는 `R = Ry(Pitch) · Rx(Roll)`로 둔다. 작은 각도에서는 순서 영향이 작지만 Phase 2에서 명시적으로 유지한다.
- 상부 연결점은 `t + R·p_i`, 하부 연결점은 `b_i`이며 액추에이터 길이는 `||t + R·p_i - b_i||`로 계산한다.

## 3. 4점 방식의 임시 좌표

비교를 위해 네 점을 `(±300, ±250) mm`에 둔다. 모든 액추에이터와 상부판의 강성이 동일하다는 이상조건에서만 하중 분담을 비교한다. 실제 4점 구조는 위치 오차로 과구속될 수 있다.

## 4. 분리형 방식의 임시 지오메트리

- Pitch 유효 레버암: 300 mm
- Roll 유효 레버암: 250 mm
- 중앙 피벗과 직접 리프트 가이드를 사용한다고 가정
- 틸트 액추에이터 실제 설치각, 레버 오프셋, 감속비는 미정

## 5. 하중과 편심

- 현재 1차 상부 이동질량 기준은 `moving_structure + cart + payload = 22 + 10 + 10 = 42 kg`이다.
- 30 kg 카트 보관 민감도에서는 같은 식으로 62 kg을 사용한다.
- CR-01 리시버 키트 질량 스크린은 placeholder 하드포인트 포함 약 4.50 kg이며, 실제 커넥터/인서트/카트 프레임 BOM 전까지 임시값이다.
- CR-01-H1 하드포인트 스크린은 12 mm locator, 8 mm local insert, 40 x 30 mm rest pad, 5 mm latch keeper를 시드로 사용한다. CR-01-H2-B는 슬롯 체결을 mock-up 조정/클램프에 쓰고 최종 반복 위치 기준은 shoulder/key/positive stop, 필요 시 dowel로 잡는 토폴로지 시드다. CR-01-H3는 master locator X/Y 고정, secondary locator Y-only, rest pad Z-only, latch keeper preload/uplift-only 스택 규칙이다. CR-01-H4-S1은 이를 12 mm removable master bushing, 40 x 8 mm replaceable stop, X-slot/diamond secondary, 40 x 30 mm shim pad, 5 mm keeper/secondary lock의 목업용 하드웨어 시드로 좁힌다.
- HRT8E actuator-axis capacity is checked against the 5.29 kN catalog axial static value, not its 26.77 kN radial static value. Official 8 mm bore, 23 mm body and 11 mm eye dimensions are reflected in JNT-BR-01-HRT8E. The active detailed seed uses two 8 mm steel lugs, one 8 mm double-shear pin, an 18 mm inner gap, replaceable 12 x 8.2 x 8 mm lug bushings and 3.5 mm misalignment-spacer envelopes. Physical articulation, fits and bracket attachment remain unconfirmed.
- 초기 편심 비교는 플랫폼 중심에서 X/Y 각각 최대 150 mm로 둔다.
- 카트 무게중심 높이, 자재 높이 및 실제 편심은 제공되지 않았다.
- 중앙 가이드와 액추에이터 연결부는 압축뿐 아니라 인장 반력도 전달할 수 있다고 가정한다. 삼각 지지영역 밖에 무게중심이 위치하면 한 지지점에 들림 반력이 발생할 수 있기 때문이다.

## 6. 외형·질량·비용 추정의 해석

- 3개 방식의 높이, 구조질량, 비용은 구성 비교를 위한 범위값이며 제작 견적이 아니다.
- 나비엠알오 DC 12 V/2000 N/150 mm/5 mm/s안과 LM4075OE-1075 24 V/100 mm/5 V 엔코더형은 모두 전동안 보관 후보다. 현재 최소 PoC는 전원을 사용하지 않는 수동 나사조절식 지지대를 선정한다.
- 참고 이미지에서 카트 프레임 치수, 재료, 볼트 위치를 측정하거나 추정하지 않는다.
- 100 kg 표기는 참고 슬라이드에 존재하지만 최신 텍스트 프롬프트와 상충하므로 기준 하중에서 제외한다.
