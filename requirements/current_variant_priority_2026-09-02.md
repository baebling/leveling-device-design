# 현재 설계안 우선순위

작성일: 2026-09-02  
근거: 사용자 결정 `기계식으로 바꾸기 전 전자식 설계와 BOM을 우선순위 1번으로 하고 현행 기계식을 2번`  
상태: 이 문서는 전동/기계식 설계안의 현재 우선순위를 정하는 최신 기준이다.

## 우선순위 1 - 전동 자동수평 3-RPS Rev E

- 형식: 120 deg 방사형 3-RPS
- 액추에이터: `LM4075OE-1075` DC24V/100 mm/엔코더 5 V 6 ppr, 3개
- 구동: `Cytron MDD10A` 2채널 드라이버 2개, 4채널 중 3채널 사용
- 상위 제어: `SunFounder TS0481 Mega2560 호환` 1개
- 자세 센서: `MPU6050/GY-521` 1개
- 전원: `Mean Well LRS-350-24` 24 V/14.6 A 1개와 5 V DC-DC 1개
- 목표: Z 0-50 mm, pitch/roll 각각 +/-3 deg, 총 지지질량 약 20 kg
- 기계 기준: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`
- 제어 기준: `design_basis/priority1_powered_control_architecture_2026-09-02.md`
- BOM 기준: `procurement/profile_radial_reve_domestic_master_bom_2026-09-02.csv`

이 안은 다시 최우선 개발 후보가 됐지만 아직 주문 승인 상태는 아니다. 펌웨어와 최종 배선도도 완성되지 않았다.

```text
PRIORITY = 1
ACTIVE_VARIANT = POWERED_PROFILE_RADIAL_3RPS_REVE_ACTUAL_VENDOR
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
COMMISSIONING_RELEASE = FALSE
```

주문 전 게이트:

1. LM4075OE 세 대의 24 V/100 mm/5 V encoder/6 ppr 정확 옵션과 동일 배선 리비전을 서면 확인한다. 공급 STEP는 확보했고 해시를 기록했다.
2. 정격·기동·스톨전류와 엔코더 핀맵을 확보한다.
3. LMB-10 치수도면과 Ø6 핀/리테이너가 축마다 포함되는지 확인한다.
4. A6061 맞춤가공품과 스탠드오프 견적, 배송·세금 포함 총액이 4,000,000원 이하인지 확인한다.
5. 무부하 단축 통전으로 MDD10A, 5 A 퓨즈와 24 V 전원 버스 전압을 검증한다.
6. 최종 회로도·단자표·배선표와 최소 자동수평 펌웨어를 작성한다.

## 우선순위 2 - 수동 턴버클 3-RPS Rev M2

- 형식: 공통 Z가 없는 pitch/roll +/-3 deg 수동 조절식 3-RPS
- 조절부: `STB-M12 + BJ761/BJ762 + PHS12L` 3축
- 상태: 디지털 조립·간섭·자립성 검증 완료, 실물 압축 proof test와 일부 구매품 확정 전
- 설계 기준: `design_basis/manual_turnbuckle_rev_m2_2026-09-02.md`
- BOM 기준: `outputs/manual_turnbuckle_rev_m2/Manual_3RPS_RevM2_BOM.csv`

```text
PRIORITY = 2
BACKUP_VARIANT = MANUAL_TURNBUCKLE_3RPS_REV_M2
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
```

수동안은 폐기하지 않는다. 전동안의 구매승인, 전기 호환성 또는 통전시험이 막힐 경우 기능축소 백업안으로 사용한다.

## 공통 경계

- 카트 본체, 바퀴, 주행계와 AMR/AGV는 설계하지 않는다.
- 사람 탑승용으로 사용하거나 표현하지 않는다.
- 실제 카트 치수와 체결부는 제공값 없이 추정하지 않는다.
- 우선순위 변경은 주문 또는 제작 승인을 의미하지 않는다.
