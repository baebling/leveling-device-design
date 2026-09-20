# 구매 가능 부품 조사

확인일: 2026-08-23. 가격·재고·배송 가능 여부는 변동하므로 발주 직전 공식 판매처에서 재확인해야 합니다.

## 권장 액추에이터

- [Firgelli Super Duty Hall actuator](https://www.firgelliauto.com/products/super-duty-actuators?variant=39956755316807): F-SD-H-450-12V-8in 구성, 450 lbf, 203.2 mm stroke, 319/523 mm retract/extend, 12 V, 최대 5.5 A, 무부하 6 mm/s, 25% duty, IP66, Hall 41.1 pulses/mm. 8.2 mm 양단 clevis와 internal non-adjustable limits를 사용한다.
- [Firgelli MB21 body bracket](https://www.firgelliauto.com/products/mb-21-bracket-for-super-duty-actuators): Super Duty 본체에 직접 고정하는 fixed-position support다. 공식 STEP를 보관하고 LS-01 고정 datum의 포락체로 사용했지만, 외부 stop reaction 전달 허용은 제조사 확인 전 open이다.
- [TiMOTION TA2P](https://www.timotion.com/kr/products/linear-actuators/ta2p-series): 3500 N push/2000 N pull, 20–1000 mm stroke, Hall 또는 가변저항 피드백, IP66M. 설치 길이는 stroke+108 mm 이상으로 더 낮은 패키징이 가능해 보이나 가격·MOQ·납기는 [TiMOTION Korea](https://pre.timotion.com/kr/contact/china) 견적 필요. 기구 높이를 낮추려면 우선 RFQ할 대안입니다.

## 프레임·결합·제어

- [MISUMI HFS8-4040](https://us.misumi-ec.com/pdf/fa/2010/p2315.pdf): 40×40 mm, A6005CSS-T5, 약 1.73 kg/m. 절단 길이와 지역 가격은 견적.
- [DESTACO 323-R](https://www.destaco.com/toggle-lock/product/323-R): pull-action latch, 360 lbf holding capacity. 4개 적용하되 전단 위치결정은 가이드 핀이 담당.
- [Arduino Mega 2560 Rev3](https://store.arduino.cc/products/arduino-mega-2560-rev3), [Cytron MD13S](https://www.cytron.io/p-13amp-6v-30v-dc-motor-driver), [Adafruit BNO085](https://www.adafruit.com/product/4754): PoC 제어용. 안전기능은 별도 하드와이어 회로로 분리.
- [Mean Well LRS-350-12](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF): 12 V/29 A, 348 W로 3×5.5 A 액추에이터의 정격 최대전류 합을 수치상 상회. 실제 돌입전류·배선·퓨즈·EMI 검토 필요.
- [Omron A22E](https://automation.omron.com/en/ca/products/family/A22E-Estop): 22/25 mm 패널형 비상정지 스위치 계열. 안전 릴레이/접촉기 구성은 별도 설계.

공식 Firgelli 8-inch actuator, MB21, MB20, MB17 STEP 원본은 `references/vendor/firgelli/`에 보존했습니다. 해시는 `design_basis/firgelli_mount_datum_review_2026-08-27.md`에 기록했습니다.
