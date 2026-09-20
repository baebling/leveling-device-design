# Profile Radial 3-RPS Rev E CAD 단계 검증 기록

작성일: 2026-09-02  
상태: `CAD_STAGE_COMPLETE`, `PURCHASE_RELEASE=FALSE`, `FABRICATION_RELEASE=FALSE`, `COMMISSIONING_RELEASE=FALSE`

## 1. CAD 기준선

우선순위 1은 허브판 없이 알루미늄 프로파일 두 프레임을 세 개의 방사형 R-P-S 축으로 연결하는 전동식 Rev E다. 하부는 4040, 상부는 3030 프로파일이며 중앙의 큰 판재는 사용하지 않는다. 맞춤품은 액추에이터별 소형 어댑터 3장과 독립 기계식 스톱 부품으로 제한했다.

| 항목 | Rev E 값 |
|---|---:|
| 전체 평면 포락체 | 700 x 700 mm |
| 연결 전 높이 | 300 mm |
| 명령 Z 범위 | 0-50 mm |
| pitch/roll | 각각 +/-3 deg |
| 하부 지지 반경 | 95 mm |
| 상부 지지 반경 | 250 mm |
| 지지 방위각 | 90/210/330 deg |
| 액추에이터 핀 중심 포락체 | 205-305 mm |
| 해석 자세 | Z 0/25/50 x pitch -3/0/3 x roll -3/0/3 = 27자세 |

좌표계는 하부 프레임 중심을 원점으로 하고 +Z를 상승, +X/+Y를 프레임 두 변 방향으로 둔다. 허용 자유도는 Z, pitch, roll이며 X, Y, yaw는 세 하부 회전축의 평면 구속으로 종속된다.

## 2. 실제 공급자 형상

- 프로젝트 보관 STEP: `references/vendor_cad/LM4075OE-1075-100mm.stp`
- SHA-256: `1BC86009BADDCF6458EEB63FB1FCAC349FD80B6B64F9A0DDFA7C4B824DF52F3B`
- XCAF 구성명: `UP`, `END`, `MOTER`, `WAIKE`, `FENGTOU`, `NEIGUAN`
- STEP에서 측정한 접힘 핀 중심거리: 205.0 mm
- 후면 아이 폭: 약 18 mm
- 전면 아이 폭: 구멍부 약 19 mm, 최대 돌출부 약 20.07 mm
- 양쪽 피벗 보어: 약 Ø6.4 mm

실제 STEP 여섯 바디를 축마다 그대로 넣어 총 18개 공급자 바디를 사용했다. 판매 상세페이지의 100 mm 행정과 STEP의 205 mm 접힘 핀 중심거리를 함께 사용했으며, 사진만으로 판독한 값은 LMB-10 항목에 한정해 별도 미확정으로 남겼다.

## 3. 반복 1: CadQuery/OpenCascade

1. 27자세 위치해석과 11개 대표 자세 STEP를 생성했다.
2. 프로파일, LMB 외형, 실제 액추에이터 여섯 바디, PHS6, 축볼트, 와셔, 너트, 스톱을 조립했다.
3. B-rep 교차체적, 피벗축 직교성, 구면 로드엔드 굴절, 스트로크, 스톱 여유를 검사했다.

결과:

| 검사 | 결과 |
|---|---:|
| 27자세 최소 핀 중심거리 | 210.771741 mm |
| 27자세 최대 핀 중심거리 | 276.937115 mm |
| 접힘측 행정 여유 | 5.771741 mm |
| 신장측 행정 여유 | 28.062885 mm |
| 최대 PHS6 굴절 | 4.096369 deg / 허용 8 deg |
| 최대 구속 잔차 | 9.95e-14 mm |
| 예상하지 않은 교차체적 | 0 mm3 |
| 판정 | PASS |

주요 수정 이력:

- 75 mm 하부 지지 반경은 실제 액추에이터와 프레임 배치 여유가 부족해 95 mm로 확대했다.
- 연결 전 높이를 300 mm로 맞추기 위해 상부 링 기준 Z를 235 mm에서 246 mm로 조정했다.
- 하부 중앙 횡재를 Y=75/-37.5 mm에서 Y=95/-47.5 mm로 옮겼다.
- 세 어댑터가 겹치지 않도록 위치를 다시 풀었고 A3 프로파일 홀을 local X=-70/+30 mm의 비대칭 100 mm 피치로 바꿨다.
- 초기 단순 PHS6 모델에서 링과 스템이 겹쳐 자기 간섭이 생겼다. 두 형상을 합집합한 뒤 Ø6.4 보어를 다시 관통 가공해 자기 간섭과 피벗 막힘을 제거했다.
- 상부 축 적층은 전면 아이 약 19 mm + PHS6 폭 9 mm + M6 평와셔 1.5 mm 두 장으로 모델링했다.

참고: 마지막 CadQuery 내보내기 프로세스는 모든 STEP, 렌더, JSON 및 manifest를 기록한 뒤 종료코드 1을 반환했다. 예외 메시지는 없었고 산출물 존재, 파일 크기, SHA-256 manifest와 독립 검증 JSON을 다시 확인해 데이터 검증은 PASS로 유지했다. 자동화 래퍼의 종료상태 이상은 후속 정리 대상이다.

## 4. 반복 2: Fusion 360 네이티브 조립체

Fusion에서 최종 조립체를 생성하고 `Design.analyzeInterference`를 동일 조건으로 3회 실행했다. 각 회차는 150개 leaf occurrence를 검사했다.

| 회차 | Fusion 검출 | 예상하지 않은 간섭 | 판정 |
|---:|---:|---:|---|
| 1 | 3 | 0 | PASS |
| 2 | 3 | 0 | PASS |
| 3 | 3 | 0 | PASS |

세 회차에 공통으로 검출된 3건은 각 액추에이터 `NEIGUAN`의 Ø6.4 보어와 상부 M6 피벗축 사이의 `0.000116-0.001377 mm3` 수치 허용오차 접촉이다. 실체 끼워맞춤 간섭으로 판정하지 않았다. 세 결과의 부품쌍과 체적 서명은 동일해 `repeatable=true`, `all_zero_unexpected=true`다.

단면검사는 X=0, +3, -3 mm의 세 평면에서 수행해 피벗축, 어댑터, 스톱, 프로파일 관통을 확인했다. 조립 전체 이미지와 A1 상세 이미지도 별도로 저장했다.

## 5. BOM 재대조 반복

Rev E BOM 60행을 CAD occurrence와 다시 대조했다.

- 하부/상부 프로파일: 700 mm 세로재 각 2개, 하부 620 mm 횡재 4개, 상부 640 mm 횡재 4개가 일치한다.
- 직각 브래킷: 4035 8개, DCB3025 8개와 각 체결축 방향이 일치한다.
- 구동축: LM4075OE 3개, LMB-10 3개, PHS6 사용 3개가 일치한다.
- 어댑터: C01/C02는 96 mm 대칭 피치, C03은 100 mm 비대칭 피치가 CAD와 일치한다.
- 상부 피벗: M6x50 반나사 볼트 3개, 평와셔 사용 6개, 나일론너트 3개가 일치한다.
- 전장: 구조 간섭 대상이 아닌 전장함 내부 부품은 별도 배치 검증 전 상태로 BOM에 유지했다.

이 BOM 대조 뒤 기구해석, OpenCascade 교차검사, Fusion 간섭검사를 한 번 더 반복했으며 최종 수치는 위 표와 동일했다.

## 6. CAD 산출물

- Fusion 단일 조립체: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.f3d`
- 교환용 전체 STEP: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_ACTUAL_VENDOR.step`
- 대표 11자세 STEP: `outputs/profile_radial_revE_actual_vendor/step`
- 그룹별 STEP: `outputs/profile_radial_revE_actual_vendor/fusion_groups`
- Fusion 검증 JSON: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Fusion_validation.json`
- OpenCascade 검증 JSON: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_actual_step_validation.json`
- 간섭 원시 결과: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Fusion_interference.json`
- 조립 이미지: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Fusion.png`
- A1 상세: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_A1_JOINT_DETAIL.png`
- 단면 3회: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_SECTION_PASS_1.png` 외 2개
- 동작 GIF: `outputs/profile_radial_revE_actual_vendor/renders/Profile_Radial_3RPS_RevE_pitch_roll_motion.gif`
- 산출물 해시: `outputs/profile_radial_revE_actual_vendor/artifact_manifest.json`
- 타 PC 핵심 패키지: `output/Profile_Radial_3RPS_RevE_CAD_Package_2026-09-02.zip`

## 7. CAD 완료와 주문 가능의 구분

Rev E는 요구 운동범위와 디지털 조립성에 대한 **CAD 단계 기준선**이다. 다음 사항 때문에 제작·발주 승인은 아니다.

1. LMB-10은 치수도면이 없어 내부 폭, 핀 중심 오프셋과 동봉품을 사진 기반 외형으로 모델링했다.
2. C01-C03 제작용 DXF와 공차도는 LMB-10 도면을 받은 뒤 다시 발행해야 한다.
3. 액추에이터 정격·기동·스톨전류와 엔코더 핀맵을 판매자에게 확인해야 한다.
4. 전장함의 실제 내부 배치, 열, 접지, 케이블 굴곡과 단자번호는 전기 상세설계 단계에서 검사해야 한다.
5. 실제 프로파일 슬롯/브래킷 제조공차, 볼트 머리 접근성과 공구 공간은 한 축 실물 조립으로 최종 확인해야 한다.

따라서 현재 판정은 `CAD_STAGE_COMPLETE`이면서 `purchase_release=false`, `fabrication_release=false`다.
