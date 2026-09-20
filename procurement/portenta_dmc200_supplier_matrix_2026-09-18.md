# Portenta·DMC-200 공급처·호환성 게이트

작성일: 2026-09-18  
적용 범위: 승인된 상부 수평유지·승강 PoC 제어계 개정의 발주 전 증빙  
상태: **구매 릴리스 금지 - DMC-200 핵심 호환성 `HOLD_VENDOR_REPLY`**

## 1. 판정 규칙

- 판정값은 `PASS`, `HOLD_VENDOR_REPLY`, `REJECT`만 사용한다.
- `PASS`는 공개 원문 또는 공급처 서면 답변으로 요구조건이 확인된 경우에만 부여한다.
- `HOLD_VENDOR_REPLY`는 형번은 맞지만 전기 호환성, 실제 출고조건, 프로토콜 변형 또는 납기가 아직 서면 확정되지 않은 경우다.
- `REJECT`는 확인된 사실이 승인 구매기준과 충돌하는 구매경로에 부여한다.
- DMC-200과 `LM4075OE-1075` 엔코더의 직접 호환성이 `PASS`가 되기 전에는 Task 2 이후 구매 릴리스를 진행하지 않는다.

## 2. 고정 후보와 공급 증빙

Step 3 고정 세트는 **WitMotion `HWT905-RS485` 2대 + Weintek `MT8072iP` 1대** 한 조합이다. 두 품목 모두 G마켓 국내배송·다음 영업일 출발 표시가 있는 카드결제 경로를 사용한다. 원산지는 중국이지만 주문수입 경로가 아니라 국내 판매자 출고 경로로 분류한다.

| 게이트 | 고정 모델·수량 | 공급처·SKU | 확인 가격(VAT 포함) | 재고·납기 근거 | URL | 판정 | 근거와 남은 조건 |
|---|---:|---|---:|---|---|---|---|
| 주제어기 기술 | Arduino Portenta Machine Control `AKX00032` ×1 | Arduino | - | 제조사 현행 데이터시트 수정일 2026-09-15 | [공식 제품](https://docs.arduino.cc/hardware/portenta-machine-control) / [데이터시트](https://docs.arduino.cc/resources/datasheets/AKX00032-datasheet.pdf) | `PASS` | 24 VDC ±20%, Arduino 프레임워크, RS-232/422/485 소프트웨어 구성, RS485 반/전이중과 온보드 종단이 공식 자료에 명시된다. 전용 엔코더 2채널은 본 구조에서 DMC-200이 축별 엔코더를 읽으므로 병목이 아니다. |
| 주제어기 구매 | `AKX00032` ×1 | 디바이스마트 `13963538` | 546,667원 | 보존한 2026-09-18 화면상 구매가능수량 244개, 평균준비 4~5일; Digi-Key 관리 해외구매·취소/반품 불가 표기 | [상품](https://www.devicemart.co.kr/goods/view?no=13963538) | `PASS` | 보존 HTML의 `gl_goods_price = 546667`, `(VAT 포함) 546,667원`, `구매가능수량 244개`를 기준으로 고정했다. 결제 직전 가격·수량은 다시 캡처한다. |
| 축 제어기 상품 | MotorBank `DMC-200` ×3 | 모터뱅크 `1000008040` | 94,380원/대, 283,140원/3대 | 페이지 재고 카운트 233; 실제 출고일 미표기 | [상품](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000008040) | `HOLD_VENDOR_REPLY` | 8~35 V, 정격 8 A, 200 W급, A/B/5V/GND와 병렬 D+/D-/GND 단자는 확인된다. 그러나 판매 제목·모델은 DMC-200인데 페이지 `제품스펙` 값은 `EMD-200`으로 불일치한다. 납기와 납품 라벨·리비전도 서면 확정해야 한다. |
| 축 제어기 프로토콜 기본 구조 | MC-RS485-AG V1.0.1 | 모터뱅크 기술자료 `sno=121` | - | PDF 원문 저장 완료 | [게시물](https://www.motorbank.kr/board/view.php?bdId=technicaldata&sno=121) / [PDF](https://www.motorbank.kr/board/download.php?bdId=technicaldata&sno=121&fid=0) | `PASS` | ID, baud, 응답지연, 엔코더 펄스, 감속비, 절대/상대 위치, 위치·속도 피드백 명령의 문서 존재와 기본 구조를 확인했다. 아래 14/15번 opcode 모순과 `LM4075OE-1075` 전기 호환성은 이 판정에 포함하지 않는다. |
| DMC-200 명령 14/15 opcode 매핑 | 제어 방향 설정 / 위치 초기화 | 모터뱅크 서면 확인 필요 | - | MC-RS485-AG V1.0.1 PDF 2쪽 내부 모순 | [PDF](https://www.motorbank.kr/board/download.php?bdId=technicaldata&sno=121&fid=0) | `HOLD_VENDOR_REPLY` | 표의 14번 제어 방향은 mode `0x0E`인데 예제 패킷은 `0x0F`; 표의 15번 위치 초기화는 mode `0x0F`인데 예제 패킷은 `0x0E`다. 어느 opcode가 권위값인지 공급처가 서면 확정하기 전 두 명령을 구현·시험 기준으로 사용하지 않는다. |
| DMC-200 ↔ 액추에이터 | `LM4075OE-1075`, 24 V, 부하전류 1.5 A, 5 V A/B상 6 ppr, 감속비 1/20, 리드 3.175 mm | 모터뱅크 서면 확인 필요 | - | - | [DMC-200 상품문의 경로](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000008040) | `HOLD_VENDOR_REPLY` | 입력 임계값, 엔코더 출력전류, A/B 출력회로, pull-up, x1/x2/x4 계수, 내부 리미트 역방향 복귀, 초기화 기준이 공개자료로 확정되지 않는다. 이 행이 전체 구매 릴리스를 막는다. |
| 3대 RS485 멀티드롭 | DMC-200 ×3, ID 1/2/3 예정 | 동일 버스 | - | 프로토콜상 ID 0~254와 broadcast 255, 병렬 단자 존재 | [상품](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000008040) | `HOLD_VENDOR_REPLY` | 주소 기능은 확인됐지만 3대 동시 배선의 종단·바이어스·GND·최소 폴링주기·응답 충돌 조건은 서면 확인이 필요하다. |
| 상·하부 경사센서 기술 | WitMotion `HWT905-RS485` ×2 | 제조사 표기 `HWT905-485`; G마켓 옵션 표기 `HWT905-RS485` | - | 제조사 현행 제품 페이지·데이터시트·RS485 매뉴얼·Modbus 프로토콜 보존 | [제조사 제품](https://witmotion-sensor.com/products/accelerometer-with-self-recovering-magnetic-ield-chip-inclinometer-hwt905-ttl-mpu-9250) / [현행 데이터시트](https://drive.google.com/file/d/1FEDNzXmRpfTZghg__9BRl9SHY73Oh6Ou/view?usp=drive_link) / [프로토콜](https://drive.google.com/file/d/1GbW99zNE7WUNvqR5bC6isotGgrGXzQaB/view?usp=share_link) | `PASS` | 9~36 V, RS485 Modbus master-slave, X/Y 각도 정확도 0.05°, X ±180°/Y ±90°, 0.2~200 Hz, 최대 230400 bps를 확인했다. Modbus 문서는 장치 주소 레지스터 `0x1A`와 Roll/Pitch 레지스터 `0x3D~0x40`을 정의한다. Portenta의 RS485 인터페이스를 그대로 사용하므로 승인 아키텍처를 바꾸지 않는 동등품이다. |
| 경사센서 구매경로 | `HWT905-RS485` ×2 | G마켓 케이일레븐홀딩스, 상품번호 `3973625857`, 옵션 `03 HWT905-RS485(+46200원)` | 기본 할인가 136,330원 + 옵션 46,200원 = 182,530원/대; 365,060원/2대 | `오늘출발`, 2026-09-21 출발 예정, 국내배송 전용, 무료배송; 절대 재고수량은 미표시 | [상품](https://item.gmarket.co.kr/Item?goodsCode=3973625857) | `PASS` | 새상품·과세상품·신용카드 전표 발행 가능, 서울 소재 판매자 출고다. 원산지는 중국이다. 공개 화면의 다음 영업일 출발을 국내 판매자 보유분 근거로 사용하며 결제 직전 옵션과 출발일을 재확인한다. |
| HMI 기술 | Weintek `MT8072iP` ×1 | Weintek | - | 현행 제품 페이지·다운로드 색인 및 EasyBuilder Pro V6.10.01 공식 사용자 매뉴얼 보존 | [공식 제품](https://www.weintek.com/Product/Model/MT8072iP) / [공식 다운로드](https://www.weintek.com/Download/ProductSpecification/MT8072iP) / [EasyBuilder Pro 매뉴얼](https://dl.weintek.com/public/EBPro/UserManual/eng/EasyBuilder-Pro-V61001-UserManual-eng.pdf) | `PASS` | 7인치 800×480, 24±20% VDC, RS485 2W/4W, Ethernet, EasyBuilder Pro와 Modbus 장치 구성을 확인했다. |
| HMI 핵심 요구 불변성 | `MT8072iP` | Weintek | - | 현행 웹과 보존 PDF의 CPU·소비전류는 다르지만 7인치·24 V·RS485·Ethernet 요구는 양쪽 동일 | [공식 공개 PDF](https://dl.weintek.com/public/MT8000iP/Datasheet/eng/MT8072iP_Datasheet_ENG.pdf) | `PASS` | CPU/소비전류 리비전 차이는 입고검사 기록 대상으로 남긴다. 승인된 HMI 인터페이스 요구에는 영향을 주지 않으므로 구매 고정 게이트를 차단하지 않는다. 명판 모델과 포트는 개봉 전 확인한다. |
| HMI 구매경로 | `MT8072iP` ×1 | G마켓 `(주)오토센코리아`, 상품번호 `4729242374` | 264,000원/대; 배송비 3,000원, 합계 267,000원 | `오늘출발`, 2026-09-21 출발 예정, 국내배송 전용, 주문 후 1~3일; 절대 재고수량은 미표시 | [상품](https://item.gmarket.co.kr/Item?goodsCode=4729242374) | `PASS` | 새상품·과세상품·신용카드 전표·세금계산서 발급사업자 표시, 서울 구로 판매자 출고다. 결제 직전 구매 가능 상태와 출발일을 재확인한다. |

## 3. 엔코더 환산 검토와 확인 경계

공급처가 `6 ppr`을 A상 1주기 기준으로 해석하고 엔코더가 모터축에 있으며 감속비가 정확히 20:1이라면, 계산 후보는 다음과 같다.

- 출력축 1회전당 A상 주기: `6 ppr × 20 = 120 cycles/rev`
- DMC-200이 A/B 모든 에지를 x4 계수하면: `6 × 4 × 20 = 480 counts/rev`
- 출력축 1회전의 리드 이동: `3.175 mm`
- A상 주기 기준: `120 / 3.175 = 37.7953 cycles/mm`, `0.0264583 mm/cycle`
- x4 기준: `480 / 3.175 = 151.1811 counts/mm`, `0.00661458 mm/count`

이 값들은 **가설 계산**이며 DMC-200 공개문서는 x4 해석과 `encoder pulse=6` 입력의 의미를 확정하지 않는다. 공급처가 “엔코더 펄스 설정=6, 감속비 설정=20.0”과 실제 출력축 360°/3.175 mm 이동의 관계를 서면으로 확인할 때까지 제어상수로 사용하지 않는다.

### HWT905-RS485 2대 갱신률 검토

제조사 원문은 HWT905-RS485의 출력률을 0.2~200 Hz, RS485를 Modbus 질의응답 방식, 통신속도를 최대 230400 bps로 규정한다. Roll/Pitch 네 레지스터(`0x3D~0x40`)를 한 번에 읽을 때 표준 Modbus RTU 요청 8 byte와 응답 13 byte를 가정하면 한 센서당 21 byte다. UART 1 byte를 start/stop 포함 10 bit로 잡으면 두 센서를 각각 20 Hz로 읽는 선로 부하는 다음과 같다.

`21 byte/transaction × 10 bit/byte × 2 sensors × 20 Hz = 8,400 bit/s`

115200 bps에서 원시 선로 점유율은 약 7.3%, 230400 bps에서는 약 3.6%이므로 프로토콜 대역폭상 각각 20 Hz 폴링이 가능하다. 실제 응답지연·종단·바이어스·Portenta 태스크 지터는 입고 후 두 장치 주소를 다르게 설정한 벤치시험에서 확인한다. 이 시험은 성능 인수조건이며 현재 공개자료에 근거한 구매 고정을 막는 공급처 질의 항목은 아니다.

## 4. 예산 게이트

기존 `reve_final_order_bom_2026-09-17.csv`의 `BASE` 합계는 1,495,105원이다. 승인 명세상 삭제 대상과 그 전용품으로 본 검토에서 제외한 행은 `E01`, `E02`, `E03`, `E05`, `E25`, `E26`이며 합계 146,498원, 잔존 기준액은 1,348,607원이다.

현재 화면가로 더한 값은 다음과 같다.

| 항목 | 금액 |
|---|---:|
| 잔존 Rev E 기준액 | 1,348,607원 |
| Portenta `AKX00032` ×1 | 546,667원 |
| DMC-200 ×3 | 283,140원 |
| HWT905-RS485 ×2 | 365,060원 |
| MT8072iP ×1 | 264,000원 |
| MT8072iP 국내배송비 | 3,000원 |
| 확인된 소계 | 2,810,474원 |

이 소계는 고정한 HMI·센서와 그 표시 배송비를 포함하지만, 절연 RS485, 통신선·종단·커넥터, 로그 저장매체, 기타 배송비, 가공 견적 갱신을 포함하지 않으므로 아직 “전체 확정가”가 아니다. 따라서 380만원 미만 추가품 조건은 아직 발동하지 않는다. 독립 100 mm 변위계, 추가 절연 RS485 장치, 전장함 내부 장착판은 이번 단계에서 추가하지 않는다. 예비 액추에이터·중복 제어기·용도 없는 수량 증가도 금지한다.

## 5. 최종 게이트 요약

| 게이트 | 판정 | 릴리스 조건 |
|---|---|---|
| Portenta 모델·인터페이스 | `PASS` | 결제 직전 가격·수량 재확인 |
| DMC-200 프로토콜 기본 구조 | `PASS` | 저장 원문 해시 유지 |
| DMC-200 명령 14/15 opcode 매핑 | `HOLD_VENDOR_REPLY` | 제어 방향과 위치 초기화 중 `0x0E`/`0x0F`의 권위 매핑을 공급처가 서면 확정 |
| DMC-200 ↔ LM4075OE 직접 호환 | `HOLD_VENDOR_REPLY` | 작성된 질의의 전기레벨·pull-up·5 V 출력·환산·리미트·초기화 전 항목에 서면 답변 |
| DMC-200 3대 멀티드롭 | `HOLD_VENDOR_REPLY` | 주소·종단·바이어스·응답주기 서면 답변 |
| HWT905-RS485 기술요건 | `PASS` | 24 V, RS485 Modbus, X/Y 각도와 20 Hz 이상 대역폭 원문 확인 |
| HWT905-RS485 국내 구매경로 | `PASS` | G마켓 옵션 2대, VAT 포함 표시가·카드전표·국내배송·다음 영업일 출발 고정 |
| MT8072iP 기술요건 | `PASS` | 7인치·24 V·RS485·Ethernet·Modbus 문서 유지 |
| MT8072iP 국내 구매경로 | `PASS` | 오토센코리아 G마켓 1대, VAT 포함 표시가·카드전표·국내배송·1~3일 고정 |
| 전체 구매 릴리스 | `HOLD_VENDOR_REPLY` | 위 HOLD 해소 후에만 다음 구매 단계 진행 |

## 6. 원문 보존

원문 스냅샷과 PDF는 `references/vendor_downloads/portenta_dmc200/`에 저장했다. URL, 수집시각, 상대경로, SHA-256은 `references/vendor_downloads/portenta_dmc200/source_manifest.csv`에 기록했다. 2026-09-20 수정 2/5에서 HWT905 공식 제품 페이지, 현행 RS485 데이터시트, RS485 매뉴얼, Modbus 프로토콜과 두 G마켓 구매 관련 필드 추출본을 추가했다. G마켓은 직접 HTML 다운로드에 HTTP 403을 반환했으므로 전체 HTML이라고 오인하지 않도록 추출본의 성격과 원 URL을 파일 안에 명시했다.

## 7. Task 단계 완료성

- Step 1: **완료**. 고정 모델의 상품/기술 페이지와 DMC, HWT905-RS485, MT8072iP 관련 원문을 manifest에 연결했다.
- Step 2: **완료**. DMC 전기·환산·리미트·초기화·멀티드롭 질의와 14/15 opcode 모순 확인 문항을 작성했다. 외부 발송은 하지 않았다.
- Step 3: **완료**. `HWT905-RS485` 2대와 `MT8072iP` 1대를 국내배송·VAT 포함 표시가·카드증빙·출발일이 있는 한 세트로 고정했다.
- Step 4: **완료(추가 선정 없음)**. 전체 확정가가 아니므로 380만원 미만 조건을 발동하지 않았다.
- Step 5: **완료**. 게이트 판정은 세 허용 상태만 사용했고 전체 구매 릴리스는 `HOLD_VENDOR_REPLY`다.

따라서 Task 1의 산출물과 Step 1~5는 완료했다. 다만 DMC-200 ↔ 액추에이터와 DMC 명령 14/15 opcode가 `HOLD_VENDOR_REPLY`이므로 **전체 구매 릴리스는 계속 금지**된다.
