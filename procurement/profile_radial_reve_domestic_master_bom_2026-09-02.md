# Profile Radial 3-RPS Rev E 국내 구매형 CAD 단계 BOM

> 기준일: 2026-09-02  
> 상태: `CAD_STAGE_COMPLETE`, `purchase_release=false`, `fabrication_release=false`, `commissioning_release=false`

검토용 Excel 파일: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Domestic_BOM_2026-09-02.xlsx`

## 판정

- 총 60개 BOM 행이며, 화면가가 있는 품목의 합계는 **1,268,724원**다.
- 400만원 예산에서 화면가 기준 잔액은 **2,731,276원**다. 다만 맞춤가공 9행, 배송비, 전장함 가공, 세금 변동은 미포함이다.
- CAD 단계의 부품 구성은 닫혔지만 `M01` 액추에이터 전류/배선, `M02` LMB-10 공급도면과 동봉핀, 맞춤판 제작도면이 닫히지 않아 지금 주문하면 안 된다.
- 외장 TVS 다이오드 행은 삭제했다. MDD10A가 회생형 H-브리지이므로 모터 출력 양단에 검증되지 않은 24 V TVS를 고정 적용하지 않는다.
- USB 데이터 케이블 행은 삭제했다. 선택한 TS0481에 Type-C 케이블이 포함된다.

## 제어 구조

`PC(선택) -> Mega2560 1대 -> MDD10A 2대/3채널 -> LM4075OE 3대`

`MPU6050 -> I2C -> Mega2560`, `액추에이터 엔코더 A/B 3조 -> Mega2560`, `24 V PSU -> 모터`, `24->5 V buck -> 로직/엔코더`

이 구성은 축마다 제어기를 한 대씩 사지 않는다. Mega 한 대가 수평 제어와 세 엔코더를 처리하고, 2채널 드라이버 두 대 중 세 채널만 사용한다.

## 공급처별 화면가

| 공급처 | 화면가 합계 | 비고 |
|---|---:|---|
| NAVIMRO | 609,268원 | 배송/결제 화면 재확인 |
| MotionGearOn | 390,000원 | 배송/결제 화면 재확인 |
| DeviceMart | 203,808원 | 배송/결제 화면 재확인 |
| SpeedMall | 52,448원 | 배송/결제 화면 재확인 |
| Motorbank | 13,200원 | 배송/결제 화면 재확인 |
| SKB-QUOTE | 0원 | 견적 필요 |

## 주문 전 필수 게이트

1. `M01`: 세 액추에이터가 DC24V/100 mm/10 mm/s/750 N/5 V 6ppr 엔코더 옵션인지 견적서에 문자열로 명시한다.
2. `M01`: 정격, 기동, 스톨전류와 엔코더 배선색/출력레벨을 판매자에게 서면 확인한다.
3. `M02`: LMB-10의 내부 폭, 전체 외형, 바닥홀 피치, 핀 중심 위치, 핀/리테이너 동봉 여부가 표시된 치수도면을 받는다.
4. `C01-C03`: LMB-10 공급도면을 반영해 Rev E 제작용 DXF와 공차도를 다시 발행하고 Fusion 간섭검사를 3회 반복한다.
5. `E01/E04/E09B`: 한 축 무부하 통전시험으로 기동·정상·정지·스톨 직전 전류와 회생 과도전압을 측정한 뒤 퓨즈와 동시구동 조건을 동결한다.
6. 가공견적, 배송, 세금, 예비품을 포함한 총액이 400만원 이하인지 다시 합산한다.

## 전체 BOM

| ID | 시스템 | 품목 | 정확 사양 | 사용/주문 | 공급처·코드 | 화면가 합계 | 상태 |
|---|---|---|---|---:|---|---:|---|
| `S01` | 구조 | [알루미늄 프로파일](https://www.navimro.com/p/K92787708/) | DNF4040/M8, 40x40, 700 mm, 흑색, 직각 절단 | 2/2 EA | NAVIMRO `K92787708` | 43,978원 | `CAD_STAGE_SELECTED` |
| `S02` | 구조 | [알루미늄 프로파일](https://www.navimro.com/p/K92787705/) | DNF4040/M8, 40x40, 620 mm, 흑색, 직각 절단 | 4/4 EA | NAVIMRO `K92787705` | 79,156원 | `CAD_STAGE_SELECTED` |
| `S03` | 구조 | [알루미늄 프로파일](https://www.navimro.com/p/K42296106/) | DNF3030-6/M6, 30x30, 700 mm, 직각 절단 | 2/2 EA | NAVIMRO `K42296106` | 15,378원 | `CAD_STAGE_SELECTED` |
| `S04` | 구조 | [알루미늄 프로파일](https://www.navimro.com/p/K42296071/) | DNF3030-6/M6, 30x30, 640 mm, 직각 절단 | 4/4 EA | NAVIMRO `K42296071` | 26,356원 | `CAD_STAGE_SELECTED` |
| `S05` | 구조 | [40시리즈 직각 브래킷](https://www.navimro.com/p/K92782553/) | 4035, 다이캐스트 | 8/8 EA | NAVIMRO `K92782553` | 7,304원 | `CAD_STAGE_SELECTED` |
| `S06` | 구조 | [30시리즈 직각 브래킷](https://www.navimro.com/p/K56842696/) | DCB3025 | 8/8 EA | NAVIMRO `K56842696` | 5,280원 | `CAD_STAGE_SELECTED` |
| `M01` | 구동 | [광학엔코더 리니어 액추에이터](https://motiongearon.com/product/%EA%B4%91%ED%95%99%EC%97%94%EC%BD%94%EB%8D%94-%EB%A6%AC%EB%8B%88%EC%96%B4%EC%95%A1%EC%B6%94%EC%97%90%EC%9D%B4%ED%84%B0-lm4075oe-1075-%EA%B3%A0%EC%A0%95%EB%B0%80-%EC%8B%A4%EB%A6%B0%EB%8D%94-1224v-10mms-750n/1717/) | LM4075OE-1075, DC24V, stroke 100 mm, encoder 5V/6ppr, 10 mm/s, 750 N | 3/3 EA | MotionGearOn `LM4075OE-1075` | 390,000원 | `HOLD_EXACT_OPTION_AND_CURRENT_VERIFY` |
| `M02` | 구동 | [LMB-10 고정 브래킷](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000007655) | LM4075용, 강재, 6 mm 피벗 계열; 핀과 코터핀 포함 구성 | 3/3 EA | Motorbank `1000007655/LMB-10` | 13,200원 | `HOLD_VENDOR_DRAWING_AND_PIN_CHECK` |
| `M03` | 구동 | [암나사 로드엔드 베어링](https://www.speedmall.co.kr/product/LCGJ5) | THK PHS6 RH, M6x1, bore 6, OD18, width 9 | 3/4 EA | SpeedMall `LCGJ5/THK-PHS6` | 52,448원 | `CAD_STAGE_SELECTED` |
| `C01` | 가공 | [A1 LMB 방사형 어댑터](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 120x70x8; 2xD9 profile holes at X +/-48; 2xM8x1.25 LMB taps at 36 mm pitch | 1/1 EA | SKB-QUOTE `A1_LMB_RADIAL_ADAPTER_REVE_120x70x8` | 견적 | `HOLD_REVE_DXF_AND_LMB_DRAWING` |
| `C02` | 가공 | [A2 LMB 방사형 어댑터](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 120x70x8; 2xD9 profile holes at local X +/-48; 2xM8x1.25 LMB taps at 36 mm pitch | 1/1 EA | SKB-QUOTE `A2_LMB_RADIAL_ADAPTER_REVE_120x70x8` | 견적 | `HOLD_REVE_DXF_AND_LMB_DRAWING` |
| `C03` | 가공 | [A3 LMB 방사형 어댑터](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 120x70x8; 2xD9 profile holes at local X -70/+30; 2xM8x1.25 LMB taps at 36 mm pitch | 1/1 EA | SKB-QUOTE `A3_LMB_RADIAL_ADAPTER_REVE_120x70x8` | 견적 | `HOLD_REVE_DXF_AND_LMB_DRAWING` |
| `C04` | 가공 | [하부 스톱 포획판 FRONT](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 90x125x8; D50 1개, D9 2개 | 1/1 EA | SKB-QUOTE `STOP_CATCH_FRONT_90x125x8_D50.dxf` | 견적 | `QUOTE_REQUIRED` |
| `C05` | 가공 | [하부 스톱 포획판 REAR](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 90x125x8; D50 1개, D9 2개 | 2/2 EA | SKB-QUOTE `STOP_CATCH_REAR_90x125x8_D50.dxf` | 견적 | `QUOTE_REQUIRED` |
| `C06` | 가공 | [상부 스톱 앵커 FRONT](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 80x85x6; D10.5 1개, D6.8 2개 | 1/1 EA | SKB-QUOTE `STOP_UPPER_ANCHOR_FRONT_80x85x6.dxf` | 견적 | `QUOTE_REQUIRED` |
| `C07` | 가공 | [상부 스톱 앵커 REAR](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 80x85x6; D10.5 1개, D6.8 2개 | 2/2 EA | SKB-QUOTE `STOP_UPPER_ANCHOR_REAR_80x85x6.dxf` | 견적 | `QUOTE_REQUIRED` |
| `C08` | 가공 | [스톱 접촉바](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061-T6, 70x20x4; 중앙 D10.5 | 6/6 EA | SKB-QUOTE `STOP_CONTACT_BAR_70x20x4_D10_5.dxf` | 견적 | `QUOTE_REQUIRED` |
| `C09` | 가공 | [원형 관통 스탠드오프](https://www.skb-steel.com/product/detail.html?product_no=235) | A6061, OD16, ID8.4 +0.2/0, L28 +/-0.1, 모따기/디버링 | 6/6 EA | SKB-QUOTE `M8x28-CUSTOM` | 견적 | `QUOTE_REQUIRED` |
| `F01` | 체결 | [육각렌치볼트](https://www.navimro.com/p/K53536280/) | M8x16, SCM435 10.9, 완전나사, 1PK(36EA) | 22/1 PK_36 | NAVIMRO `K53536280` | 7,579원 | `CAD_STAGE_SELECTED` |
| `F02` | 체결 | [육각렌치볼트](https://www.navimro.com/p/K53536246/) | M6x15, SCM435 10.9, 완전나사, 1PK(57EA) | 22/1 PK_57 | NAVIMRO `K53536246` | 6,039원 | `CAD_STAGE_SELECTED` |
| `F03` | 체결 | [육각렌치볼트](https://www.navimro.com/p/K53536553/) | M8x20, SCM435 10.9, 완전나사, 1PK(34EA) | 6/1 PK_34 | NAVIMRO `K53536553` | 7,359원 | `CAD_STAGE_SELECTED` |
| `F04` | 체결 | [M8 평와셔](https://www.navimro.com/p/K06130485/) | SUS304, 8.5x17x1, 1PK(100EA) | 6/1 PK_100 | NAVIMRO `K06130485` | 5,049원 | `CAD_STAGE_SELECTED` |
| `F05` | 체결 | [M8 스프링와셔](https://www.navimro.com/p/K15785747/) | SUS304, 8.4x14x2, 낱개 | 6/6 EA | NAVIMRO `K15785747` | 2,640원 | `CAD_STAGE_SELECTED` |
| `F06` | 체결 | [40시리즈 스프링너트](https://www.navimro.com/p/K14671419/) | SP408, M8, 1PK(100EA) | 28/1 PK_100 | NAVIMRO `K14671419` | 25,289원 | `CAD_STAGE_SELECTED` |
| `F07` | 체결 | [30시리즈 스프링너트](https://www.navimro.com/p/K14671215/) | SP306, M6, 1PK(100EA) | 25/1 PK_100 | NAVIMRO `K14671215` | 25,289원 | `CAD_STAGE_SELECTED` |
| `F08` | 체결 | [반나사 육각볼트](https://www.navimro.com/p/K53672105/) | M6x50, 나사부 18 mm, 비나사부 약 32 mm, 1PK(10EA) | 3/1 PK_10 | NAVIMRO `K53672105` | 3,410원 | `HOLD_FINAL_STACK_CONFIRM` |
| `F09` | 체결 | [M6 평와셔](https://www.navimro.com/p/K02197839/) | M6, t1.5 nominal, plain washer; upper pivot lateral centering | 6/1 PK_100 | NAVIMRO `K02197839` | 2,189원 | `HOLD_FINAL_STACK_CONFIRM` |
| `F10` | 체결 | [M6 나일론 인서트 너트](https://www.navimro.com/p/K14536539/) | SUS304, 1PK(100EA) | 3/1 PK_100 | NAVIMRO `K14536539` | 8,789원 | `CAD_STAGE_SELECTED` |
| `F11` | 체결 | [M6 전산볼트](https://www.navimro.com/p/K54170097/) | M6x285, 완전나사 | 1/1 EA | NAVIMRO `K54170097` | 869원 | `HOLD_CUT_LENGTH_CONFIRM` |
| `F12` | 체결 | [M6 잼너트](https://www.navimro.com/p/K14532615/) | SCM435 니켈, 1PK(100EA) | 6/1 PK_100 | NAVIMRO `K14532615` | 4,169원 | `CAD_STAGE_SELECTED` |
| `F13` | 체결 | [M10 전산볼트](https://www.navimro.com/p/K54170031/) | M10x285, 완전나사 | 3/3 EA | NAVIMRO `K54170031` | 3,927원 | `HOLD_CUT_LENGTH_CONFIRM` |
| `F14` | 체결 | [M10 잼너트](https://www.navimro.com/p/K14532693/) | SCM435 니켈, 1PK(50EA) | 18/1 PK_50 | NAVIMRO `K14532693` | 8,349원 | `CAD_STAGE_SELECTED` |
| `F16` | 체결 | [M8x45 육각볼트](https://www.navimro.com/p/K15696590/) | 강재, 완전나사, 낱개 | 6/6 EA | NAVIMRO `K15696590` | 5,280원 | `CAD_STAGE_SELECTED` |
| `F17` | 체결 | [중강도 나사고정제](https://www.navimro.com/p/K64647607/) | LOCTITE 243, 10 ml | 1/1 EA | NAVIMRO `K64647607` | 9,889원 | `CAD_STAGE_SELECTED` |
| `F18` | 체결 | [M4 더블샘스볼트](https://www.navimro.com/p/K14364804/) | M4x25, 니켈도금, 평와셔+스프링와셔 결합, 1PK(100EA) | 20/1 PK_100 | NAVIMRO `K14364804` | 18,139원 | `HOLD_ELECTRICAL_LAYOUT` |
| `F19` | 체결 | [M4 육각너트](https://www.navimro.com/p/K06130054/) | SUS304, M4x0.7, 1PK(50EA) | 20/1 PK_50 | NAVIMRO `K06130054` | 1,529원 | `HOLD_ELECTRICAL_LAYOUT` |
| `E01` | 전장 | [2채널 양방향 DC 모터 드라이버](https://www.devicemart.co.kr/goods/view?no=1280280) | Cytron MDD10A, 5-30 VDC, 10 A continuous/channel, PWM+DIR, regenerative H-bridge | 2/2 EA | DeviceMart `1280280/MDD10A` | 79,860원 | `HOLD_ACTUATOR_CURRENT_COMMISSIONING` |
| `E02` | 전장 | [Mega2560 호환 제어보드](https://www.devicemart.co.kr/goods/view?no=1382306) | SunFounder TS0481 Mega 2560 R3 compatible, USB Type-C cable included | 1/1 EA | DeviceMart `1382306/TS0481` | 34,980원 | `CAD_STAGE_SELECTED` |
| `E03` | 전장 | [6축 IMU 모듈](https://www.devicemart.co.kr/goods/view?no=15960724) | VOLT GY-521 / MPU6050, I2C, 3-axis gyro + 3-axis accelerometer | 1/1 EA | DeviceMart `15960724/VLT-GY006` | 6,490원 | `CAD_STAGE_SELECTED_CALIBRATION_REQUIRED` |
| `E04` | 전장 | [24 V AC-DC 전원공급기](https://www.devicemart.co.kr/goods/view?no=13231965) | Mean Well LRS-350-24, 24 VDC, 14.6 A, 350 W | 1/1 EA | DeviceMart `13231965/LRS-350-24` | 45,650원 | `HOLD_ACTUATOR_CURRENT_COMMISSIONING` |
| `E05` | 전장 | [방수형 24 V-5 V 강압 모듈](https://www.devicemart.co.kr/goods/view?no=1330743) | SZH-BPM003, input 15-40 VDC, output 5 VDC 3 A | 1/1 EA | DeviceMart `1330743/SZH-BPM003` | 9,350원 | `CAD_STAGE_SELECTED` |
| `E06` | 전장 | [ABS 전장함](https://www.navimro.com/p/K07636024/) | SL902, 400x500x155 mm | 1/1 EA | NAVIMRO `K07636024` | 27,489원 | `HOLD_ELECTRICAL_LAYOUT` |
| `E07` | 전장 | [접지 전원코드](https://www.navimro.com/p/K08345728/) | DYP-G15B, 2 m, 1.5 sq x 3C | 1/1 EA | NAVIMRO `K08345728` | 4,389원 | `CAD_STAGE_SELECTED` |
| `E08` | 전장 | [2극 배선용 차단기](https://www.navimro.com/p/K04115335/) | ABE32b, 2P2E, 10 A | 1/1 EA | NAVIMRO `K04115335` | 23,089원 | `CAD_STAGE_SELECTED_SUPERVISED_BENCH` |
| `E09A` | 전장 | [방수 인라인 ATO 퓨즈홀더](https://www.devicemart.co.kr/goods/view?no=12170196) | SZH-FU005, ATO/ATC blade fuse holder | 4/4 EA | DeviceMart `12170196/SZH-FU005` | 7,480원 | `CAD_STAGE_SELECTED` |
| `E09B` | 전장 | [ATO 블레이드 퓨즈 5 A](https://www.devicemart.co.kr/goods/view?no=11509) | 32 VDC automotive blade fuse, 5 A; pack minimum/order quantity 10 | 3/10 EA | DeviceMart `11509/ATO-5A` | 1,100원 | `HOLD_ACTUATOR_CURRENT_COMMISSIONING` |
| `E09C` | 전장 | [ATO 블레이드 퓨즈 1 A](https://www.devicemart.co.kr/goods/view?no=16020344) | 32 VDC automotive blade fuse, 1 A | 1/3 EA | DeviceMart `16020344/ATO-1A` | 2,178원 | `CAD_STAGE_SELECTED` |
| `E11` | 전장 | [스크루 단자대](https://www.navimro.com/p/K02216060/) | JOTB-20-10, 20A, 10P | 2/2 EA | NAVIMRO `K02216060` | 5,478원 | `CAD_STAGE_SELECTED` |
| `E12` | 전장 | [14AWG 실리콘 전선 세트](https://www.navimro.com/p/K92854706/) | 적/흑/백, 판매 구성 길이 결제 전 재확인 | 1/1 SET | NAVIMRO `K92854706` | 82,489원 | `HOLD_VENDOR_CONTENT_VERIFY` |
| `E13` | 전장 | [24AWG 제어전선 세트](https://www.navimro.com/p/K92843703/) | UL1007, 6색, 총 60 m | 1/1 SET | NAVIMRO `K92843703` | 34,089원 | `CAD_STAGE_SELECTED` |
| `E15` | 전장 | [열수축튜브 키트](https://www.navimro.com/p/K52569152/) | 12종, 750 pcs | 1/1 SET | NAVIMRO `K52569152` | 12,089원 | `CAD_STAGE_SELECTED` |
| `E16` | 전장 | [케이블 글랜드](https://www.navimro.com/p/K22571959/) | PG13.5, 6-12 mm, 1PK(10EA) | 7/1 PK_10 | NAVIMRO `K22571959` | 6,919원 | `CAD_STAGE_SELECTED` |
| `E17` | 전장 | [페룰 키트](https://www.navimro.com/p/K92839991/) | DY6330, 0.5/0.75/1.0/1.5/2.5 sq | 1/1 SET | NAVIMRO `K92839991` | 43,989원 | `CAD_STAGE_SELECTED` |
| `E18` | 전장 | [케이블 타이](https://www.navimro.com/p/K01415707/) | J-200 black, 200x4.8 mm, 1PK(1000EA) | 1/1 PK_1000 | NAVIMRO `K01415707` | 17,039원 | `CAD_STAGE_SELECTED` |
| `E19` | 전장 | [흑색 PVC 절연테이프](https://www.navimro.com/p/K40799280/) | 10 m x 19 mm | 3/3 EA | NAVIMRO `K40799280` | 1,650원 | `CAD_STAGE_SELECTED` |
| `E20` | 전장 | [35 mm DIN 레일](https://www.devicemart.co.kr/goods/view?no=12538843) | JTRN 4, steel, 1 m; cut to enclosure layout length | 1/1 EA | DeviceMart `12538843/JTRN-4-1M` | 16,720원 | `HOLD_ENCLOSURE_LAYOUT_CUT_LENGTH` |
| `E21` | 전장 | [녹/황 접지선](https://www.navimro.com/p/K55027039/) | TFR-GV 2.5 sq, 0.6/1 kV, m 단위 | 3/3 M | NAVIMRO `K55027039` | 4,257원 | `CAD_STAGE_SELECTED` |
| `E22` | 전장 | [절연 압착단자 키트](https://www.navimro.com/p/K92807634/) | 링/포크 단자 150 pcs | 1/1 SET | NAVIMRO `K92807634` | 7,249원 | `HOLD_SIZE_VERIFY` |
| `E23` | 전장 | [M3 PCB 서포트·나사 키트](https://www.navimro.com/p/K28009916/) | NT-KIT-E018, 플라스틱 M3 | 1/1 SET | NAVIMRO `K28009916` | 14,289원 | `CAD_STAGE_SELECTED` |
| `E24` | 전장 | [2.54 mm 점퍼 케이블](https://www.navimro.com/p/K28006026/) | 40P M/F, 20 cm, KEYES | 1/1 EA | NAVIMRO `K28006026` | 1,529원 | `CAD_STAGE_SELECTED` |

## 상태 집계

| 상태 | 행 수 |
|---|---:|
| `CAD_STAGE_SELECTED` | 34 |
| `CAD_STAGE_SELECTED_CALIBRATION_REQUIRED` | 1 |
| `CAD_STAGE_SELECTED_SUPERVISED_BENCH` | 1 |
| `HOLD_ACTUATOR_CURRENT_COMMISSIONING` | 3 |
| `HOLD_CUT_LENGTH_CONFIRM` | 2 |
| `HOLD_ELECTRICAL_LAYOUT` | 3 |
| `HOLD_ENCLOSURE_LAYOUT_CUT_LENGTH` | 1 |
| `HOLD_EXACT_OPTION_AND_CURRENT_VERIFY` | 1 |
| `HOLD_FINAL_STACK_CONFIRM` | 2 |
| `HOLD_REVE_DXF_AND_LMB_DRAWING` | 3 |
| `HOLD_SIZE_VERIFY` | 1 |
| `HOLD_VENDOR_CONTENT_VERIFY` | 1 |
| `HOLD_VENDOR_DRAWING_AND_PIN_CHECK` | 1 |
| `QUOTE_REQUIRED` | 6 |

## 제외한 과거 항목

- `DMD-150` 3대: MDD10A 2대로 대체.
- `WT901C`: MPU6050 모듈로 대체. PoC 정지 시험대에서 고가 AHRS는 필수가 아니다.
- `DMC-200` 3대: 축별 독립 전용제어기 비용이 커서 제외.
- `SDCMG3260T + WT901C-CAN`: 국내 즉시 구매·통합자료를 확인하지 못했고 제어 단순화 효과가 불명확해 제외.
- `SMCJ24CA/1.5KE24CA`: 실제 모터단 파형 검증 없이 24 V 출력에 고정 적용하는 것이 부적절해 제외.
- 별도 USB 케이블: TS0481 동봉품과 중복되어 제외.

세부 치수, 절단 위치와 조립 검증 근거는 `design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md`를 따른다.
