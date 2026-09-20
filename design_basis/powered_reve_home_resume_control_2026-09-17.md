# Rev E HOME 재개·정상창 복귀 제어 기준 — 2026-09-17

## 적용 범위와 상태

이 문서는 기존 Rev E 유지형상과 공개식으로 확인된 명목 하한 205 mm에 대한 예비 제어 기준이다. 초기 엔코더 환산값은 151.181 count/mm(x4)로 두고 실물 50 mm 이동으로 보정한다. LMB-10 상세치수는 확보했으며, 최종 CAD 반영과 입고 후 리미트 작동점 확인이 남아 있다.

```text
HOME_POLICY_STATUS = PRELIMINARY_LIVE_SESSION_RESUME_CLOSED
POWER_LOSS_AUTO_RESUME = PROHIBITED
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
MOTOR_POWER_RELEASE = FALSE
```

## 선택 경로

- 정상운전창: 절대 핀 길이 210~280 mm
- HOME 접근: 축당 1 mm 이하 단계, `A3→A2→A1` 교대수축
- HOME 종단: 세 축의 실측 하한 리미트
- 정상창 복귀: 같은 `A3→A2→A1` 순서로 축당 1 mm 이하 교대신장하여 세 축 모두 210 mm 이상
- 속도: HOME 접근과 정상창 복귀 모두 1.0±0.2 mm/s
- 정상창 복귀 전 `LIFT`, `LEVEL`, 일반 `JOG` 금지

명목 205→210 mm 복귀는 여섯 순환순서 모두 예비 통과했다. 제어 분기를 줄이기 위해 HOME 접근과 동일한 순서를 선택한다. 선택 경로는 시작상태를 포함해 16개 길이상태이며 최대 기울기 0.232856477°, 기존 조인트 모델 최대 편각 0.208048630°다.

## 명령 허용 상태

| 현재 상태 | `HOME` 처리 |
|---|---|
| `READY_HOMED`, 같은 전원 세션, 엔코더 카운트 연속 | HOME 준비자세로 이동한 뒤 교대수축 시작 가능 |
| `LIFT_ACTIVE`, `LEVEL_ACTIVE`, `JOG_ACTIVE` | 현재 동작을 안전정지하고 같은 세션의 유효 카운트로 `HOME_PARK=(Z0,pitch0,roll0)` 이동을 완료한 뒤에만 HOME 접근 허용 |
| `HOME_PAUSED`, 같은 전원 세션, 카운트 연속 | 저장된 활성축·목표카운트·다음 위상으로만 재개 |
| `HOME_AT_LOW` | 운전자 재시작 명령 후 실측 하한에서 210 mm 정상창 복귀만 허용 |
| MCU reset, 제어전원 상실, 카운트 불연속, 기록 CRC 오류 | `HOME_START_UNVERIFIED`; 자동 HOME·자동 재개 거부 |
| E-stop 작동 | 모든 PWM=0, 드라이버 disable, 모터 24 V 차단. 자동 재개 금지 |

## 같은 전원 세션의 위상 보존

RAM 상태에는 최소한 다음 값을 보존한다.

- `home_state`
- `active_axis`
- `active_step_target_count`
- `next_phase_index` (`0=A3`, `1=A2`, `2=A1` 순환에서 다음 실행 위치)
- 축별 현재 카운트와 해당 카운트의 유효 플래그
- 마지막 명령 방향
- timeout과 fault 코드

각 1 mm 단계는 다음 순서로 처리한다.

1. `active_axis`, 목표카운트와 현재 `next_phase_index`를 RAM에 설정한다.
2. 선택된 한 축만 구동한다.
3. 목표카운트 또는 종단판정에 도달하면 PWM=0과 driver disable을 먼저 수행한다.
4. 카운트·전류·리미트 상태를 검증한다.
5. 검증 후에만 `next_phase_index`를 다음 축으로 전진시키고 `active_axis=NONE`으로 커밋한다.

소프트웨어 STOP이 한 단계 도중 발생하면 해당 단계의 나머지를 먼저 완료한 후 다음 위상으로 간다. 처음 축부터 순환을 다시 시작하지 않는다.

## 전원상실 재개 금지

LM4075OE의 공개자료는 증분형 펄스만 보여 주며 절대 위치를 제공하지 않는다. NVM 쓰기와 실제 축 이동을 물리적으로 원자화할 수 없으므로, 마지막 저장카운트와 위상만으로 전원상실 후 위치를 확정하지 않는다.

공개 사양의 6 ppr, 감속비 1/20, 스크루 리드 3.175 mm를 적용하면 채널당 `6×20/3.175=37.795 pulse/mm`, A/B x4 복호 시 `151.181 count/mm`다. 이 값은 최초 제어 상수이며 축별 50 mm 실측으로 보정한다.

- NVM에는 마지막 정상종료 상태를 진단용으로 남길 수 있지만 자동 재개의 권위값으로 사용하지 않는다.
- MCU reset, 제어전원 상실 또는 E-stop 이후에는 `HOME_START_UNVERIFIED`로 진입한다.
- 복구는 전원차단·블록지지 상태에서 세 핀 길이 ±1 mm 실측 후 `COMMISSIONING_HOME` 절차로만 수행한다.
- 별도 절대위치센서나 전원상실 중 이동검출 수단이 추가될 때만 전원상실 자동복귀를 재검토한다.

## 계산 증거와 한계

- `verification/reve_home_resume_closure_2026-09-17.json`: 1,859개 조밀 시작자세의 선택 HOME 경로 216,951개 중간상태에서 위상 보존 재개가 원래 접미 경로와 모두 일치했다.
- `verification/reve_home_normal_window_escape_2026-09-17.json`: 명목 205→210 mm 여섯 순환순서 예비검사.
- `verification/reve_command_jog_path_audit_2026-09-17.json`: 조밀 1,859자세에서 HOME 준비자세로 가는 선분 1,859개와 조밀 인접 JOG 선분 5,122개, 총 89,707개 표본이 핀 210~280 mm·기울기 5°·PHS 13° 한계를 예비 통과했다.
- 이 결과는 경로 생성기의 길이상태와 기존 기구학 모델에 대한 디지털 증거다.
- 1 mm 상태 사이의 연속 CAD 충돌, 변경 LMB/PHS, 독립 스토퍼, 실제 리미트 작동점과 전류·펄스 신뢰성은 아직 검증되지 않았다.
- 임의의 두 자세를 직접 잇는 모든 명령경로는 검사하지 않았다. HOME 요청은 검증된 준비자세 이동을 거치도록 제한한다.
