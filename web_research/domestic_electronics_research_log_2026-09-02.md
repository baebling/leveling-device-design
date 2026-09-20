# 국내 구매형 전동 제어부 조사 기록

조사·검증 구간: 2026-09-02 20:55-23:15 KST  
주의: 위 시간은 CAD 대조, 페이지 조사와 BOM 검증을 포함한 전체 작업 구간이며 연속적인 웹 탐색 시간만을 뜻하지 않는다.

## 결론

세 액추에이터에 전용 제어기 세 대를 붙이는 구성을 폐기하고, 국내 판매 페이지에서 확인 가능한 범용 부품 5종을 핵심 제어부로 선정했다.

| 기능 | 선정품 | 수량 | 2026-09-02 VAT 포함 화면가 | 근거 |
|---|---|---:|---:|---|
| 3축 모터 전력단 | Cytron MDD10A 2채널 | 2 | 39,930원/대 | 5-30 V, 10 A continuous/channel, PWM+DIR |
| 상위 제어 | SunFounder TS0481 Mega2560 호환 | 1 | 34,980원 | I/O가 충분하고 Type-C 케이블 포함 |
| 자세 센서 | VLT-GY006 MPU6050/GY-521 | 1 | 6,490원 | 정지 시험대의 저속 수평 피드백에 충분한 PoC 후보 |
| 24 V 전원 | Mean Well LRS-350-24 | 1 | 45,650원 | 24 V, 14.6 A, 350 W |
| 5 V 로직 전원 | SZH-BPM003 | 1 | 9,350원 | 15-40 V 입력, 5 V/3 A 출력 |

전력·제어 흐름은 `PC(선택) -> Mega2560 -> MDD10A 2대의 3채널 -> LM4075OE 3대`다. MPU6050은 I2C, 세 엔코더는 A/B 펄스로 Mega에 연결한다. PC는 설정·로그에만 쓰고 실시간 모터 PWM은 Mega가 처리한다.

## 확인한 국내 페이지

- MDD10A: https://www.devicemart.co.kr/goods/view?no=1280280
- MDD10A 제조사 사양: https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels
- Mega2560 호환 TS0481: https://www.devicemart.co.kr/goods/view?no=1382306
- MPU6050/GY-521: https://www.devicemart.co.kr/goods/view?no=15960724
- LRS-350-24: https://www.devicemart.co.kr/goods/view?no=13231965
- 24 V-5 V 강압모듈: https://www.devicemart.co.kr/goods/view?no=1330743
- 방수 ATO 홀더: https://www.devicemart.co.kr/goods/view?no=12170196
- ATO 5 A: https://www.devicemart.co.kr/goods/view?no=11509
- ATO 1 A: https://www.devicemart.co.kr/goods/view?no=16020344
- 35 mm DIN 레일: https://www.devicemart.co.kr/goods/view?no=12538843
- LM4075OE-1075: https://motiongearon.com/product/detail.html?item_code=P0000COB00BU&product_no=1717

페이지 가격과 재고는 변할 수 있으므로 실제 결제 전 다시 확인한다.

## 기각·보류한 대안

- `DMC-200 x3`: 축별 전용 제어기를 세 대 사야 해 비용과 배선 복잡도가 커진다.
- `DMD-150 x3`: 동작은 가능하지만 단일채널 3대보다 MDD10A 2대/3채널 구성이 더 싸고 단순하다.
- `WT901C/UART` 또는 `WT901C-CAN`: 완제품 AHRS의 편의성은 있으나 정지 저속 PoC 기준으로 비용 절감 폭이 큰 MPU6050을 우선했다.
- `SDCMG3260T + WT901C-CAN`: 국내 즉시 구매 페이지와 세 LM4075OE 엔코더/모터를 직접 닫는 통합배선 자료를 확인하지 못했다.
- `BTS7960` 모듈: 국내 저가 보드는 판매처별 회로·정품 여부·연속전류 품질 편차가 커 세 축 발주 기준품으로 채택하지 않았다.
- Raspberry Pi Pico 계열: 가격은 낮지만 3.3 V 로직과 5 V 엔코더 인터페이스 검토가 추가된다. Mega의 I/O와 5 V 계열 인터페이스가 이 PoC에 더 단순하다.
- Jetson Nano 직접 PWM: 보유품 활용은 가능하지만 Linux 호스트가 모터 안전 정지와 실시간 펄스 계수까지 직접 맡는 구조는 오히려 복잡해진다. Jetson은 후속 상위 명령/로깅 호스트로 연결할 수 있다.
- 외장 `SMCJ24CA`, `1.5KE24CA`: 실제 회생 과도전압을 측정하지 않고 24 V 모터 출력 양단에 고정하면 정상 PWM과 보호 동작 경계가 불명확하다. MDD10A의 회생 H-브리지를 기본으로 두고, 버스 과도전압은 한 축 시험에서 측정한 뒤 별도 보호를 재선정한다.

## 남은 전기 검증

1. LM4075OE의 정격·기동·스톨전류와 엔코더 선색/출력레벨을 판매자에게 받는다.
2. 한 축 무부하에서 5 A 퓨즈로 시작해 기동·정상·정지·역전 전류와 24 V 버스 최고전압을 계측한다.
3. MDD10A의 역극성 보호 부재를 반영해 PSU 극성과 분기 퓨즈를 확인한다.
4. 세 축 동시기동을 금지한 순차 제어로 시작하고, 전류 합이 LRS-350-24의 14.6 A 이내인지 확인한다.
5. 최종 회로도, 단자번호, 접지점, 케이블 규격과 전장함 배치를 동결한다.

본 조사로 부품 후보와 비용은 줄였지만 통전 승인까지 완료한 것은 아니다.
