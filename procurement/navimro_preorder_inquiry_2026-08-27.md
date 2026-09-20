# NAVIMRO Pre-Order Inquiry

Date: 2026-08-27

Purpose: obtain one consolidated quotation and one purchase release for every component required by the stationary leveling-module PoC.

## Message To Send

안녕하세요. 아래 품목들을 한 번의 견적 및 한 번의 발주로 구매하려고 합니다. 주문제작 및 반품불가 품목이 포함되어 있어 주문 전에 아래 기술사항을 서면으로 확인 부탁드립니다. 가능하면 전체 품목을 하나의 견적서와 거래명세/세금계산서로 묶고, 장척물 착불비와 최종 출하계획도 함께 알려주세요.

1. `K92931811 / DIHOOL LA2000-125150` 3개
   - 납품 사양은 **DC 12 V / 2000 N / 스트로크 150 mm / 5 mm/s**로 확인했습니다. 견적서와 명판에도 이 네 항목이 동일하게 표시되는지 확인
   - 나비엠알오 상품명이 `LA2000-125150`인 반면 상세 이미지에는 `DHLA6000-A2` 자료가 섞여 있습니다. 실제 제조사 세부 형식명과 A1/A2 중 어느 설치형인지 도면과 명판 사진으로 확인
   - DIHOOL의 DHLA6000-A2 12 V/24 V 페이지는 동일 A2 도면과 STEP 이름을 사용하지만, 현재 주문품의 `2000 N / 5 mm/s` 조합은 DHLA6000 표의 `2000 N / 15 mm/s`와 다릅니다. DHLA6000 파일이 아니라 실제 `K92931811 / LA2000-125150` 납품품 파일로 회신
   - 현재 설계는 **평판을 사용하지 않고 M8 나사식 축단을 JFT-8R에 연결하는 구성**입니다. 제조사 DHLA6000 자료는 A2를 `평판 + M8 나사 설치형`으로 설명하므로, 납품품에 평판이 포함되는지와 평판을 제거한 상태로 양단 M8 연결이 가능한지 확인
   - 그림의 `Ø10 / M8` 부속이 실제 기본 포함품인지, 품명·수량·재질·M8 나사 체결길이 확인
   - M8 양단 각각의 암/수 형상, 피치, 유효 나사 깊이/돌출 길이, 탈착 가능한 장착 헤드의 외형과 잠금 방법 확인
   - 아이 구멍 직경, 아이 폭, 전후 양단 장착 형상과 핀 중심 기준 최소/최대 길이 확인. DHLA6000 도면 수치가 아니라 실제 `K92931811` 납품품 수치로 회신
   - Hall 센서 포함 여부. 미포함이면 Hall 포함 주문제작 옵션으로 같은 견적에 공급 가능한지
   - Hall 펄스/mm, 내장 리미트 피드백 유무, 전체 배선도와 선 색상/커넥터
   - DIHOOL 공식 DHLA2000 12 V A1 페이지에는 제품 요약으로 `Current: 5 Amp`가 표시되지만 A2 페이지에는 이 항목이 없고 정격/최대/기동/스톨 중 어느 값인지 정의되지 않습니다. 실제 납품 A2/150 mm/5 mm/s 사양에 5 A가 적용되는지, 정격전류와 기동/스톨전류, 권장 분기 보호정격, 3개 동시 운전 권장 전원용량 확인
   - 납품품 및 포함 축단 부속과 일치하는 STEP 파일 제공. DIHOOL 페이지에 표시된 `DHLA6000-A2.STEP` 직접 링크는 2026-08-28 접속 시 403 오류가 발생하므로 견적 회신에 파일 자체를 첨부

2. `K02020097 / JMC JFT-8R` 6개
   - M8x1.25 오른나사 암나사, 구멍 Ø8, 볼 폭 12 mm, 허용 요동각 13°가 납품품과 일치하는지 확인
   - 위 A2 액추에이터 양단에 완전 나사물림으로 체결 가능한지 확인하고, A2 양단이 수나사인지 암나사인지 치수도면으로 회신
   - U/H 브래킷은 공식 도면상 각각 단일축 대안이므로 이번 견적에서는 제외

3. `DF 4040-8` 절단품 19개
   - 840x2, 820x2, 760x2, 660x4, 640x5, 420x2, 240x2 mm
   - 절단공차, 절단면 처리와 개별 길이 상품코드가 견적에 그대로 적용되는지

4. `K48313995` 900x800x15 mm 투명 아크릴 1팩(2장)
   - 실제 1팩이 2장인지, 보호필름 포함 여부와 치수/두께 공차

4-1. `K52633446` 50x6x6000 mm 철 평철 2개
   - 한 본은 `NVR-P01`~`P14` 절단 및 Cardan 50x50x36 적층 block용, 한 본은 transfer-drill 수정/재가공 예비재

5. `K94509383 / Y710028.VBD12` 4개
   - 12 mm 축에 대한 권장 체결토크와 축방향 유지력 자료

6. `K61836622 / CR-3001` 4개
   - 정격 유지하중, 장착도면, 상대측 keeper 포함 여부

7. `K92854706` 14 AWG 실리콘 전선 세트 1개
   - 색상별 릴 수량, 색상별 길이, 허용전압/온도와 도체 단면적

8. `K77669622` 80 mm 12 V 팬과 `K77677462` 80 mm 필터 각 1개
   - 2026-08-27 로그인 확인 VAT 포함 단가 5,489원 / 660원을 통합견적에서 재확인

9. 전원 적합성 확인
   - 위 액추에이터 3개를 `K63669714 DMD-150` 3개, `K47937908 NES-350-12` 1개, `K63064199 5SY4110-7` 3개와 함께 사용할 때 공급사가 권장하는 전류 여유와 차단기 정격
   - DMD-150 제조사 매뉴얼의 12 V 기준 정격은 180 W/채널, 연속전류는 별도 냉각 없이 12 A 및 단순 냉각 시 15 A로 확인했습니다. 실제 액추에이터의 정격·기동·스톨전류와 1/2/3축 동시운전 조건에서 이 구성이 적합한지 확인
   - DMD-150 매뉴얼은 모터 단자에 양방향 TVS를 권장하고 `1.5KE24CA`를 예시합니다. 나비엠알오에서 함께 주문할 수 있는 정확한 상품코드 또는 전기적으로 동등한 제조사 승인품을 제안하고, stand-off/clamp 전압과 pulse 정격 자료 첨부
   - 하강·제동 시 회생전압으로 `NES-350-12`가 과전압 보호에 들어가지 않도록 공급사가 권장하는 흡수/클램프 구성과 배선 방법 확인

전체 BOM은 첨부 CSV의 50개 감사행 중 수량이 0보다 큰 47개 활성 주문행입니다. 품절 또는 단종 품목이 있으면 임의 대체품이 아니라, 동일 기능/치수/정격의 대체 상품코드를 먼저 제안해 주시고 승인 후 견적에 반영해 주세요.

## Required Reply Attachments

- actuator end-interface drawing, matching STEP, and written JFT-8R thread compatibility;
- actuator wiring diagram and Hall option code;
- actuator and supplied rod-end accessory STEP files;
- bidirectional TVS or approved regeneration-protection part number and datasheet;
- latch drawing and rating;
- collar holding/torque information;
- consolidated quote with VAT, freight, expected dispatch and non-returnable flags.

## Release Rule

Do not place the order merely because a product page exists. Release the single purchase only after the written reply is copied into this project folder and the revised NAVIMRO CAD passes workspace, interference and fastener-stack checks.
