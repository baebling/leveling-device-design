# 프로파일 방사형 3-RPS Rev D 발주표 재감사

작성일: 2026-09-01  
최신 판정: **현재 표는 전체 확정 BOM이 아니며 주문 금지**  
상태: `purchase_release=false`, `fabrication_release=false`

## 1. 사용자가 확인한 표의 정체

`profile_radial_revd_split_source_order_groups_2026-09-01.csv`는 완성품 한 대의 모든 부품을 한 행씩 적은 BOM이 아니다. 공급처별 주문을 9개 행으로 접은 요약표다. 특히 G04 한 행은 아래 후보 CSV의 45개 행과 1,132,329원을 통째로 묶어 표시한다.

- 상세 후보표: `profile_radial_revd_navimro_candidate_bom_2026-09-01.csv`
- 후보표 전체: 57행
- G04에서 제외: M01, M01A, M02, M03, C01, C01A, C02, C03, F15, E09, E10, E20
- G04에 남은 품번 보유 후보: 45행

따라서 요약표만 보면 프로파일, 볼트, 슬롯너트, 드라이버, 전원, 함체, 배선 등이 보이지 않는다. 이상해 보이는 이유는 실제 사용부품, 구매 포장, 예비품, 길이 선택용 키트, 소모품, 미확정 보호회로가 같은 표에 섞여 있기 때문이다.

## 2. G04 45행의 실제 상태

| 상태 묶음 | 행 수 | 의미 |
|---|---:|---|
| `READY_CANDIDATE` | 28 | 상품 후보만 확인됨 |
| `READY_FOR_POC` / `READY_FOR_SUPERVISED_BENCH` | 4 | 시험용 후보 |
| `READY_AS_ADJUSTMENT_KIT` | 1 | 조립 공차 대응용 여유품 |
| `READY_AFTER_*` | 5 | 절단계획, 함체/DIN 배치, 크기, 판매자 확인 후 확정 |
| `HOLD_*` | 4 | 치수, 전류, 회생, 스탠드오프 조건 미해결 |
| `FIT_KIT_HOLD_FINAL_SELECTION` | 3 | M6 피벗 길이 35/40/45 mm 중 실측 후 선택 |
| **합계** | **45** | **12행은 조건이 닫히지 않음** |

그러므로 G04를 `READY_TO_CART`로 표시한 것은 잘못이었다. 상태를 `HOLD_12_CONDITIONAL_ROWS`로 정정했다.

## 3. TVS 다이오드 판정

`1.5KE24CA`는 전원 정류용 다이오드가 아니라 모터 감속·하강 시 발생하는 과도전압을 제한하는 양방향 TVS다. 보호 목적 자체는 타당하다.

하지만 DMD-150 매뉴얼 6쪽은 이 부품을 참고 예로 제시하면서 실제 적용 전 스탠드오프 조건을 충분히 검토하라고 명시한다. Littelfuse 데이터시트 값은 다음과 같다.

- reverse stand-off `VRWM = 20.5 V`
- breakdown `VBR = 22.8~25.2 V`
- maximum clamp `VC = 33.2 V`

현재 모터 PWM은 24 V이므로 `VRWM`보다 높고, 부품에 따라 정상 24 V 출력에서도 breakdown 구간에 들어갈 수 있다. 따라서 `1.5KE24CA`를 모터단에 바로 병렬 연결하는 발주안은 승인할 수 없다. 주문수량을 0으로 바꾸고 `DO_NOT_ORDER_UNVALIDATED_24V`로 정정했다.

필요한 후속조건은 DMD-150 판매자 또는 제조사의 24 V 승인 보호회로, 실제 액추에이터 회생 파형, 드라이버 40 V 한계 아래의 클램프 전압, 반복 펄스 에너지와 열 검토다. 이 조건이 닫히기 전에는 다른 TVS 번호도 추정으로 주문하지 않는다.

## 4. 현재 그룹별 발주 상태

| 그룹 | 현재 상태 | 남은 조건 |
|---|---|---|
| G01 액추에이터 | HOLD | 정확 옵션가격, 동일 배선 리비전, 아이 폭, 기동/스톨전류, 엔코더 핀맵 |
| G01 LMB-10 | HOLD | Ø6 핀과 리테이너 포함 여부 |
| G02 로드엔드 | HOLD | PHS6 유지 또는 JFT-6R 치환 최종 결정 |
| G03 가공품 | 견적 가능 | 15개 판재와 6개 스탠드오프 견적·가공성 확인 |
| G04 나비엠알오 45행 | HOLD | 12개 조건부 행 해소 및 평탄 주문표 생성 |
| G05 퓨즈 계통 | HOLD | 액추에이터 기동/스톨전류로 5 A 정격 확인 |
| G05 TVS | 주문 금지 | 24 V 승인 회생보호 회로 재선정 |

## 5. 정상적인 전체 BOM의 최종 형식

최종 주문표는 공급처 요약행을 쓰지 않고 다음 항목을 한 행씩 보여야 한다.

- 실제 조립 사용수량
- 판매 포장 단위와 실제 주문수량
- 예비품 여부
- 정확 모델·전압·스트로크·나사·길이
- 공급처 상품코드와 링크
- VAT 포함 단가와 배송비
- `READY_TO_ORDER` 또는 구체적인 HOLD 사유
- CAD 부품명과 조립 위치

현재 자료는 이 형식으로 평탄화하기 전 단계다. 위 그룹의 HOLD가 닫히기 전에는 장바구니 결제나 가공 착수를 승인하지 않는다.

## 6. 근거

- `references/vendor_downloads/DMD-150_users_manual.pdf`, 6쪽
- `design_basis/dmd150_official_manual_review_2026-08-28.md`
- Littelfuse 1.5KE 데이터시트: <https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_1_5ke_datasheet.pdf.pdf>
- `profile_radial_revd_navimro_candidate_bom_2026-09-01.csv`
- `profile_radial_revd_split_source_order_groups_2026-09-01.csv`
