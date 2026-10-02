# 2026-09-04 전장 도면·배선표 사용 금지 안내

이 폴더의 `RevE_point_to_point_wiring.csv`, `RevE_terminal_map.csv`, `RevE_SL902_enclosure_layout_RC.step` 및 동시기 자료는 **과거 Mega2560 + Cytron MDD10A 제어 구성**을 기준으로 한다. 2026-10-02 현재의 **Portenta Machine Control + DMC-200 3대 + ZMEC485DI** 구성에 연결하거나 재사용하면 안 된다.

특히 과거 배선표의 `Mega-D2`, `D1-CH1-PWM`, `X2`, `14 AWG` 등의 접속점·전선 길이·퓨즈 정격은 현재 BOM의 물리 접속을 나타내지 않는다. 이력 STEP의 SL902 함체와 단자 배열도 현행 배치 검증 결과가 아니다.

최신 전장 검수 범위와 보류 이유는 [Rev E 연속검증 기록](../../20261002_reve_followthrough/연속검증_중간기록.md)을 따른다. 현재 `PURCHASE_RELEASE=FALSE`, `CONTROL_POWER_TEST_RELEASE=FALSE`, `MOTOR_POWER_RELEASE=FALSE`이며, 기존 배선표는 제작·통전용으로 사용하지 않는다. 회로·단자·속판을 실제 선정한 뒤 새 버전의 배선도를 발행한다.

`PRELIMINARY PoC DESIGN — NOT APPROVED FOR FABRICATION`
