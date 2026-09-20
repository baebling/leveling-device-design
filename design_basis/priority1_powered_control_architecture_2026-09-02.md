# 우선순위 1 전동 자동수평 제어 아키텍처

작성일: 2026-09-02  
상태: `REVE_CAD_STAGE_COMPLETE`, `PURCHASE_RELEASE=FALSE`, `COMMISSIONING_RELEASE=FALSE`

## 1. 현재 기준

2026-09-02 사용자 결정에 따라 전동 프로파일 방사형 3-RPS를 우선순위 1로 유지하고, 실제 액추에이터 STEP를 사용한 Rev E CAD로 갱신한다. 수동 턴버클 Rev M2는 우선순위 2 백업안이다.

```text
LM4075OE-1075 encoder actuator x3
  <- Cytron MDD10A dual motor driver x2, 3 of 4 channels used
  <- SunFounder TS0481 Mega2560-compatible x1
  <- MPU6050/GY-521 IMU x1

220 VAC
  -> 2-pole breaker
  -> Mean Well LRS-350-24, 24 V / 14.6 A
  -> branch fuse x3 -> MDD10A motor channels x3
  -> 1 A branch fuse -> 24 V-to-5 V DC-DC
  -> Mega2560 + MPU6050 + encoder logic
```

비싼 지능형 단축 제어기 3대를 사용하는 방식이 아니다. `Mega2560` 한 대가 상위 제어기이고 2채널 `MDD10A` 두 대 중 세 채널이 각 DC 모터의 정·역회전/PWM 전력단이다. PC 또는 보유 Jetson Nano는 설정·로그·상위 명령 호스트로 선택 연결할 수 있다.

## 2. 기계 목표

| 항목 | 기준 |
|---|---|
| 기구 | 하부 R + 액추에이터 P + 상부 S, 120 deg 방사형 3축 |
| 액추에이터 | 24 V, stroke 100 mm, encoder 5 V/6 ppr, 10 mm/s, 750 N |
| 운동 | Z 0-50 mm, pitch/roll 각각 +/-3 deg |
| 지지질량 | 빈 카트 약 10 kg + 적재 10 kg |
| 프레임 | 하부 DNF4040, 상부 DNF3030 |
| 포락체 | 약 700 x 700 x 300 mm |

## 3. 제어 개발 순서

1. 액추에이터 한 대와 MDD10A 한 채널의 무부하 정·역회전 및 엔코더 카운트를 확인한다.
2. 기동·정지·스톨전류와 하강 제동 시 24 V 버스 최고전압을 측정한다.
3. 3축 개별 수동 UP/DOWN과 종단 제한을 확인한다.
4. 엔코더 기반 길이 영점과 상대 위치제어를 구현한다.
5. MPU6050의 pitch/roll을 읽고 저속 순차 보정으로 자동수평을 구현한다.
6. 10 kg 적재에서 +/-3 deg 입력, 반복오차와 복귀시간을 기록한다.

초기 PoC는 세 축을 동시에 고속 동기제어하지 않는다. 한 축씩 짧게 구동하고 IMU를 다시 읽는 순차 보정으로 제어 복잡도와 전원 피크를 줄인다.

## 4. 현재 열린 게이트

- LM4075OE 정확 주문 옵션, 동일 배선 리비전, 정격·기동·스톨전류
- 모터/엔코더 핀맵과 정격·기동·스톨전류
- LMB-10 핀·리테이너 포함 구성
- A6061 가공견적과 배송·세금 포함 4,000,000원 예산 확인
- 최종 회로도, 단자번호, 하네스와 펌웨어
- MDD10A/LRS-350-24/5 A 퓨즈의 실측 시운전 적합성

## 5. 연결 자료

- 최종 60행 국내 구매형 BOM: `procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv`
- BOM 설명: `procurement/profile_radial_reve_domestic_master_bom_2026-09-02.md`
- Fusion 조립체: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`
- 기계/CAD 검증: `design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md`
- 국내 제어부 조사: `web_research/domestic_electronics_research_log_2026-09-02.md`
- 전동→수동 전환 당시 기록: `design_basis/archived_powered_control_architecture_2026-09-01.md`

본 문서는 구매, 제작, 통전 또는 사람 탑승 적합성을 승인하지 않는다.
