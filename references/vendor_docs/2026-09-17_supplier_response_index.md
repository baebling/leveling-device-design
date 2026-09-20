# 전동 3-RPS 공급자료 인덱스 — 2026-09-17

## 판정 원칙

- `공개페이지 확인`은 판매자가 특정 수량·납기·사용조건을 서면 보증한 것이 아니다.
- 동적 판매페이지의 가격·주문가능수량·예상일은 확인시각 이후 바뀔 수 있으므로 결제 직전 다시 확인한다.
- 제조사/판매사 상세 이미지에 완결된 치수가 있으면 PoC CAD 입력값으로 사용하고, 입고 후 실측으로 확인한다.
- 공개자료로 제품 인터페이스는 동결하되 가격·재고·납기는 결제 직전에 다시 확인한다.

## 확보 자료

| 형번/항목 | 자료 제공처 | 확인일 | 원본/링크 | 확인된 값 | 미해결 질문 | 설계 상태 |
|---|---|---:|---|---|---|---|
| `LM4075OE-1075` 기본성능 | 엘레파츠/motorbank | 2026-09-17 | [EPYGW8HL](https://eleparts.co.kr/goods/view?no=17315391) | 12/24 V, 10 mm/s, 750 N, self-lock 2,000 N, 6 ppr; VAT 포함 123,500원; 옵션에 `24V/100mm` 존재 | 결제 직전 3대 재고·출고일 확인 | `PUBLIC-DATA-ACCEPTED / STOCK-CHECK` |
| `LM4075OE-1075` 옵션/엔코더 상세 | motorbank | 2026-09-17 | [제품 페이지](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000035578) | `24V 100mm 5V` 선택 가능; 24 V 무부하/부하전류 0.4/1.5 A; 듀티 20%(고속 10%); 내장 리미트; 6 ppr A/B상; 감속비 1/20, 리드 3.175 mm; `S≤500`에서 `L1=105+S`이므로 100 mm형 명목 205~305 mm. 초기값은 채널당 37.795 pulse/mm, x4 복호 151.181 count/mm | 실제 스위치 작동점과 counts/mm는 입고 후 50 mm 이동으로 보정; 재고·납기는 결제 직전 확인 | `PUBLIC-DATA-ACCEPTED / SAMPLE-CHECK` |
| `LMB-10` | motorbank | 2026-09-17 | [제품 페이지](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000007655) | 폭 26, 내부폭 20, 길이 56, 바닥홀 Ø8, 핀축-바닥홀 중심거리 36, 전체높이 44, 핀중심높이 36, 판두께 3.0, 피벗홀 Ø6.2, 선단 R8, 후단높이 17 mm. 상세사진에 브래킷 2개·핀 2개·R클립 2개가 표시됨. VAT 포함 4,400원 | 입고 후 치수와 동봉품 대조, 결제 직전 3개 재고 확인 | `DRAWING-CLOSED / SAMPLE-CHECK` |
| LDK `PHS 6` | 엘레파츠/RS/LDK | 2026-09-17 | [EPYDPV96](https://eleparts.co.kr/goods/view?no=16325532), [LDK 데이터시트](https://docs.rs-online.com/ed97/0900766b816d875e.pdf), `2026-09-17_RS_LDK_PHS6_datasheet.pdf` | 오른나사 M6-6H, 보어 6, B 9, C1 6.75, d1 8.9, d2 18, h1 30, L3 13, L4 39, L5 5, d4 10, d5 13, SW 11 mm; 볼 12.7 mm; 허용 편각 13°; 동정격 3.2 kN, 정정격 8.1 kN; 0.025 kg; VAT 포함 33,000원/개; 화면상 주문가능 22개, 평균 12근무일(10/08 표시) | 화면 수량은 실제 재고와 다를 수 있음; 3개 확정 출고일 필요 | `DRAWING-ACQUIRED / OPEN-CAD` |

## 결제·조립 시 남은 확인

1. `24 V / 100 mm / 5 V 엔코더` 3대의 재고와 출고일. 예비 1대는 별도 선택견적으로 둔다.
2. 액추에이터·LMB-10·PHS 6의 입고 치수 및 구성품 대조.
3. 축별 50 mm 저속 이동으로 엔코더 counts/mm 보정, 내장 리미트 작동과 반대방향 탈출 확인.
4. 최종 선정 전원·드라이버·E-stop 부품의 데이터시트 정격과 재고 확인.

기술 질의 회신은 CAD 착수의 선행조건이 아니다. 재고·납기가 주문화면에서 불명확할 때만 판매자에게 짧게 문의한다.

## 원본 무결성

- `2026-09-17_RS_LDK_PHS6_datasheet.pdf`
  - SHA-256: `80F064C87AF1A226BD73F21471638DE5CA7E1ABACD9542601C2198BFD8D7DF8B`
  - 1쪽 이미지형 PDF이며, 렌더링 후 PHS6 행과 치수기호를 시각 대조했다.

## 현재 게이트

```text
SUPPLIER_INQUIRY_SENT = FALSE
ACTUATOR_INTERFACE_FROZEN = TRUE
LMB10_INTERFACE_FROZEN = TRUE
PHS6_DATASHEET_ACQUIRED = TRUE
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
```
