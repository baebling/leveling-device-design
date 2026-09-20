#include <EEPROM.h>
#include <Wire.h>

// Rev E stationary bench PoC controller. This is not safety-rated firmware.

enum ControllerState : uint8_t { INIT, HOMING, IDLE, MOVING, LEVELING, FAULT };
enum FaultCode : uint8_t {
  FAULT_NONE,
  FAULT_NOT_HOMED,
  FAULT_CALIBRATION_MISSING,
  FAULT_ENCODER_NO_PULSE,
  FAULT_ENCODER_DIRECTION,
  FAULT_IMU_STALE,
  FAULT_TILT_LIMIT,
  FAULT_MOTION_TIMEOUT,
  FAULT_TRAVEL_LIMIT,
  FAULT_BAD_COMMAND
};

constexpr uint8_t AXES = 3;
constexpr uint8_t ENC_A[AXES] = {2, 3, 18};
constexpr uint8_t ENC_B[AXES] = {22, 23, 24};
constexpr uint8_t MOTOR_PWM[AXES] = {5, 6, 7};
constexpr uint8_t MOTOR_DIR[AXES] = {30, 31, 32};
constexpr uint8_t UNUSED_PWM = 8;
constexpr uint8_t UNUSED_DIR = 33;
constexpr uint8_t MPU_ADDR = 0x68;

constexpr uint32_t TELEMETRY_PERIOD_MS = 100;
constexpr uint32_t IMU_STALE_MS = 200;
constexpr uint32_t NO_PULSE_MS = 500;
constexpr uint32_t REVERSE_PAUSE_MS = 100;
constexpr uint32_t MOTION_TIMEOUT_MS = 30000;
constexpr uint32_t HOME_AXIS_TIMEOUT_MS = 15000;
constexpr uint32_t LEVEL_HOLD_MS = 10000;
constexpr float LEVEL_TOLERANCE_DEG = 0.5f;
constexpr float TILT_FAULT_DEG = 5.0f;
constexpr float LEVEL_STEP_MM = 0.25f;
constexpr float MAX_POSITION_MM = 100.0f;
constexpr uint8_t HOME_PWM = 70;
constexpr uint8_t MOVE_PWM = 105;
constexpr uint8_t PWM_RAMP_STEP = 5;
constexpr uint32_t PWM_RAMP_PERIOD_MS = 20;

struct Calibration {
  uint32_t magic;
  float countsPerMm[AXES];
  float dLengthDpitch[AXES];
  float dLengthDroll[AXES];
  float imuPitchZero;
  float imuRollZero;
};

constexpr uint32_t CAL_MAGIC = 0x52455645UL;
Calibration cal = {
  CAL_MAGIC,
  {0.0f, 0.0f, 0.0f},
  {-0.194842f, 3.006702f, -2.811860f},
  {3.359349f, -1.510936f, -1.848413f},
  0.0f,
  0.0f
};

volatile long encoderCount[AXES] = {0, 0, 0};
volatile uint32_t encoderPulseMs[AXES] = {0, 0, 0};

ControllerState state = INIT;
FaultCode faultCode = FAULT_NONE;
bool homed = false;
float pitchDeg = 0.0f;
float rollDeg = 0.0f;
uint32_t lastImuMs = 0;
uint32_t lastTelemetryMs = 0;
uint32_t levelWithinToleranceSinceMs = 0;

struct AxisMotion {
  bool active;
  uint8_t axis;
  int8_t direction;
  long startCount;
  long targetCount;
  uint8_t pwm;
  uint32_t startedMs;
  uint32_t lastRampMs;
  uint32_t reverseReadyMs;
};

AxisMotion motion = {false, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t appliedPwm[AXES] = {0, 0, 0};
bool liftActive = false;
float liftTargetMm = 0.0f;
uint8_t homeAxis = 0;
uint32_t homeAxisStartedMs = 0;
long homeLastCount = 0;
uint32_t homeLastChangeMs = 0;

char commandBuffer[128];
uint8_t commandLength = 0;

const char *stateName(ControllerState value) {
  switch (value) {
    case INIT: return "INIT";
    case HOMING: return "HOME";
    case IDLE: return "IDLE";
    case MOVING: return "MOVING";
    case LEVELING: return "LEVELING";
    case FAULT: return "FAULT";
  }
  return "UNKNOWN";
}

void encoderEdge(uint8_t axis) {
  bool a = digitalRead(ENC_A[axis]);
  bool b = digitalRead(ENC_B[axis]);
  encoderCount[axis] += (a == b) ? 1 : -1;
  encoderPulseMs[axis] = millis();
}

void encoder0() { encoderEdge(0); }
void encoder1() { encoderEdge(1); }
void encoder2() { encoderEdge(2); }

long atomicCount(uint8_t axis) {
  noInterrupts();
  long value = encoderCount[axis];
  interrupts();
  return value;
}

void setAtomicCount(uint8_t axis, long value) {
  noInterrupts();
  encoderCount[axis] = value;
  encoderPulseMs[axis] = millis();
  interrupts();
}

bool calibrationValid() {
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    if (!isfinite(cal.countsPerMm[axis]) || cal.countsPerMm[axis] <= 0.0f) return false;
    if (!isfinite(cal.dLengthDpitch[axis]) || !isfinite(cal.dLengthDroll[axis])) return false;
  }
  return cal.magic == CAL_MAGIC;
}

void allStop() {
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    analogWrite(MOTOR_PWM[axis], 0);
    appliedPwm[axis] = 0;
  }
  analogWrite(UNUSED_PWM, 0);
  digitalWrite(UNUSED_DIR, LOW);
  motion.active = false;
}

void enterFault(FaultCode code) {
  allStop();
  faultCode = code;
  state = FAULT;
}

void clearFault() {
  allStop();
  faultCode = FAULT_NONE;
  state = homed ? IDLE : INIT;
}

bool readMpu6050() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(MPU_ADDR, static_cast<uint8_t>(14), static_cast<uint8_t>(true)) != 14) return false;

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();
  Wire.read(); Wire.read();
  Wire.read(); Wire.read();
  Wire.read(); Wire.read();
  Wire.read(); Wire.read();

  float rawRoll = atan2f(static_cast<float>(ay), static_cast<float>(az)) * 57.2957795f;
  float rawPitch = atan2f(-static_cast<float>(ax), sqrtf(static_cast<float>(ay) * ay + static_cast<float>(az) * az)) * 57.2957795f;
  rollDeg = rawRoll - cal.imuRollZero;
  pitchDeg = rawPitch - cal.imuPitchZero;
  lastImuMs = millis();
  return true;
}

void startAxisCounts(uint8_t axis, long deltaCounts, uint8_t requestedPwm) {
  if (axis >= AXES || deltaCounts == 0) return;
  long start = atomicCount(axis);
  int8_t direction = deltaCounts > 0 ? 1 : -1;
  allStop();
  digitalWrite(MOTOR_DIR[axis], direction > 0 ? HIGH : LOW);
  motion = {true, axis, direction, start, start + deltaCounts, 0, millis(), millis(), millis() + REVERSE_PAUSE_MS};
  motion.pwm = min(requestedPwm, static_cast<uint8_t>(200));
}

bool startAxisMm(uint8_t axis, float deltaMm, uint8_t requestedPwm = MOVE_PWM) {
  if (!calibrationValid()) {
    enterFault(FAULT_CALIBRATION_MISSING);
    return false;
  }
  long deltaCounts = lroundf(deltaMm * cal.countsPerMm[axis]);
  if (deltaCounts == 0) deltaCounts = deltaMm > 0.0f ? 1 : -1;
  float targetMm = static_cast<float>(atomicCount(axis) + deltaCounts) / cal.countsPerMm[axis];
  if (targetMm < 0.0f || targetMm > MAX_POSITION_MM) {
    enterFault(FAULT_TRAVEL_LIMIT);
    return false;
  }
  startAxisCounts(axis, deltaCounts, requestedPwm);
  return true;
}

void serviceMotion() {
  if (!motion.active) return;
  uint32_t now = millis();
  long current = atomicCount(motion.axis);
  long traveled = current - motion.startCount;

  if (now - motion.startedMs > MOTION_TIMEOUT_MS) {
    enterFault(FAULT_MOTION_TIMEOUT);
    return;
  }
  if (now > motion.startedMs + 250 && traveled != 0 && ((traveled > 0) != (motion.direction > 0))) {
    enterFault(FAULT_ENCODER_DIRECTION);
    return;
  }
  if (now > motion.startedMs + NO_PULSE_MS && now - encoderPulseMs[motion.axis] > NO_PULSE_MS) {
    enterFault(FAULT_ENCODER_NO_PULSE);
    return;
  }
  if ((motion.direction > 0 && current >= motion.targetCount) ||
      (motion.direction < 0 && current <= motion.targetCount)) {
    analogWrite(MOTOR_PWM[motion.axis], 0);
    appliedPwm[motion.axis] = 0;
    motion.active = false;
    if (state == MOVING && !liftActive) state = IDLE;
    return;
  }
  if (now >= motion.reverseReadyMs && now - motion.lastRampMs >= PWM_RAMP_PERIOD_MS) {
    uint8_t &applied = appliedPwm[motion.axis];
    if (applied < motion.pwm) applied = min(static_cast<int>(motion.pwm), static_cast<int>(applied + PWM_RAMP_STEP));
    analogWrite(MOTOR_PWM[motion.axis], applied);
    motion.lastRampMs = now;
  }
}

void beginHomeAxis() {
  if (homeAxis >= AXES) {
    allStop();
    homed = true;
    state = IDLE;
    return;
  }
  allStop();
  digitalWrite(MOTOR_DIR[homeAxis], LOW);
  homeAxisStartedMs = millis();
  homeLastChangeMs = homeAxisStartedMs;
  homeLastCount = atomicCount(homeAxis);
  analogWrite(MOTOR_PWM[homeAxis], HOME_PWM);
}

void serviceHoming() {
  uint32_t now = millis();
  long current = atomicCount(homeAxis);
  if (current != homeLastCount) {
    homeLastCount = current;
    homeLastChangeMs = now;
  }
  if (now - homeAxisStartedMs > HOME_AXIS_TIMEOUT_MS) {
    enterFault(FAULT_MOTION_TIMEOUT);
    return;
  }
  // The actuator's internal retract limit removes motor power. No pulse is used
  // only during supervised HOME as the endpoint indication.
  if (now - homeLastChangeMs > 700) {
    analogWrite(MOTOR_PWM[homeAxis], 0);
    setAtomicCount(homeAxis, 0);
    ++homeAxis;
    beginHomeAxis();
  }
}

void serviceLeveling() {
  if (motion.active) return;
  float maxError = max(fabsf(pitchDeg), fabsf(rollDeg));
  if (maxError <= LEVEL_TOLERANCE_DEG) {
    if (levelWithinToleranceSinceMs == 0) levelWithinToleranceSinceMs = millis();
    if (millis() - levelWithinToleranceSinceMs >= LEVEL_HOLD_MS) state = IDLE;
    return;
  }
  levelWithinToleranceSinceMs = 0;

  float correction[AXES];
  float mean = 0.0f;
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    correction[axis] = -(cal.dLengthDpitch[axis] * pitchDeg + cal.dLengthDroll[axis] * rollDeg);
    mean += correction[axis];
  }
  mean /= AXES;
  uint8_t selected = 0;
  float selectedCorrection = 0.0f;
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    correction[axis] -= mean;
    if (fabsf(correction[axis]) > fabsf(selectedCorrection)) {
      selected = axis;
      selectedCorrection = correction[axis];
    }
  }
  float step = selectedCorrection >= 0.0f ? LEVEL_STEP_MM : -LEVEL_STEP_MM;
  startAxisMm(selected, step, MOVE_PWM);
}

void serviceLift() {
  if (!liftActive || motion.active || state == FAULT) return;
  uint8_t selected = AXES;
  float largest = 0.0f;
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    float delta = liftTargetMm - static_cast<float>(atomicCount(axis)) / cal.countsPerMm[axis];
    if (fabsf(delta) > fabsf(largest)) {
      largest = delta;
      selected = axis;
    }
  }
  if (selected == AXES || fabsf(largest) <= 0.05f) {
    liftActive = false;
    state = IDLE;
    return;
  }
  startAxisMm(selected, largest);
}

void printTelemetry() {
  uint32_t now = millis();
  if (now - lastTelemetryMs < TELEMETRY_PERIOD_MS) return;
  lastTelemetryMs = now;
  Serial.print(now); Serial.print(',');
  Serial.print(stateName(state)); Serial.print(',');
  Serial.print(pitchDeg, 3); Serial.print(',');
  Serial.print(rollDeg, 3);
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    Serial.print(','); Serial.print(atomicCount(axis));
  }
  for (uint8_t axis = 0; axis < AXES; ++axis) {
    Serial.print(','); Serial.print(axis == motion.axis && motion.active ? motion.pwm : 0);
    Serial.print(','); Serial.print(axis == motion.axis && motion.active ? motion.direction : 0);
  }
  Serial.print(','); Serial.println(static_cast<int>(faultCode));
}

void parseCommand(char *line) {
  char *command = strtok(line, " ,\t");
  if (!command) return;
  for (char *p = command; *p; ++p) *p = toupper(*p);

  if (!strcmp(command, "STATUS")) {
    printTelemetry();
  } else if (!strcmp(command, "STOP")) {
    liftActive = false;
    allStop();
    clearFault();
  } else if (!strcmp(command, "HOME")) {
    liftActive = false;
    clearFault();
    homed = false;
    homeAxis = 0;
    state = HOMING;
    beginHomeAxis();
  } else if (!strcmp(command, "ZERO_IMU")) {
    cal.imuPitchZero += pitchDeg;
    cal.imuRollZero += rollDeg;
    pitchDeg = 0.0f;
    rollDeg = 0.0f;
  } else if (!strcmp(command, "SAVE_CAL")) {
    float values[9];
    for (uint8_t i = 0; i < 9; ++i) {
      char *token = strtok(nullptr, " ,\t");
      if (!token) { enterFault(FAULT_BAD_COMMAND); return; }
      values[i] = atof(token);
    }
    for (uint8_t i = 0; i < AXES; ++i) cal.countsPerMm[i] = values[i];
    for (uint8_t i = 0; i < AXES; ++i) cal.dLengthDpitch[i] = values[3 + i];
    for (uint8_t i = 0; i < AXES; ++i) cal.dLengthDroll[i] = values[6 + i];
    cal.magic = CAL_MAGIC;
    if (!calibrationValid()) { enterFault(FAULT_BAD_COMMAND); return; }
    EEPROM.put(0, cal);
    clearFault();
  } else if (!strcmp(command, "JOG")) {
    char *axisToken = strtok(nullptr, " ,\t");
    char *distanceToken = strtok(nullptr, " ,\t");
    if (!homed) { enterFault(FAULT_NOT_HOMED); return; }
    if (!axisToken || !distanceToken) { enterFault(FAULT_BAD_COMMAND); return; }
    int axis = atoi(axisToken) - 1;
    float distance = atof(distanceToken);
    if (axis < 0 || axis >= AXES || distance == 0.0f) { enterFault(FAULT_BAD_COMMAND); return; }
    liftActive = false;
    state = MOVING;
    startAxisMm(axis, distance);
  } else if (!strcmp(command, "LIFT")) {
    char *heightToken = strtok(nullptr, " ,\t");
    if (!homed) { enterFault(FAULT_NOT_HOMED); return; }
    if (!heightToken) { enterFault(FAULT_BAD_COMMAND); return; }
    float height = atof(heightToken);
    if (height < 0.0f || height > 50.0f || !calibrationValid()) { enterFault(FAULT_BAD_COMMAND); return; }
    liftTargetMm = height;
    liftActive = true;
    state = MOVING;
    serviceLift();
  } else if (!strcmp(command, "LEVEL")) {
    if (!homed) { enterFault(FAULT_NOT_HOMED); return; }
    if (!calibrationValid()) { enterFault(FAULT_CALIBRATION_MISSING); return; }
    liftActive = false;
    levelWithinToleranceSinceMs = 0;
    state = LEVELING;
  } else {
    enterFault(FAULT_BAD_COMMAND);
  }
}

void serviceSerial() {
  while (Serial.available()) {
    char value = Serial.read();
    if (value == '\n' || value == '\r') {
      if (commandLength) {
        commandBuffer[commandLength] = '\0';
        parseCommand(commandBuffer);
        commandLength = 0;
      }
    } else if (commandLength < sizeof(commandBuffer) - 1) {
      commandBuffer[commandLength++] = value;
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);

  for (uint8_t axis = 0; axis < AXES; ++axis) {
    pinMode(ENC_A[axis], INPUT_PULLUP);
    pinMode(ENC_B[axis], INPUT_PULLUP);
    pinMode(MOTOR_PWM[axis], OUTPUT);
    pinMode(MOTOR_DIR[axis], OUTPUT);
    analogWrite(MOTOR_PWM[axis], 0);
  }
  pinMode(UNUSED_PWM, OUTPUT);
  pinMode(UNUSED_DIR, OUTPUT);
  analogWrite(UNUSED_PWM, 0);
  digitalWrite(UNUSED_DIR, LOW);
  attachInterrupt(digitalPinToInterrupt(ENC_A[0]), encoder0, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A[1]), encoder1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A[2]), encoder2, CHANGE);

  Calibration stored;
  EEPROM.get(0, stored);
  if (stored.magic == CAL_MAGIC) cal = stored;
  state = INIT;
  Serial.println("ms,state,pitch_deg,roll_deg,enc1,enc2,enc3,pwm1,dir1,pwm2,dir2,pwm3,dir3,fault");
}

void loop() {
  serviceSerial();
  readMpu6050();

  if (state != INIT && state != FAULT && millis() - lastImuMs > IMU_STALE_MS) enterFault(FAULT_IMU_STALE);
  if (state != INIT && state != HOMING && state != FAULT &&
      (fabsf(pitchDeg) > TILT_FAULT_DEG || fabsf(rollDeg) > TILT_FAULT_DEG)) enterFault(FAULT_TILT_LIMIT);

  if (state == HOMING) serviceHoming();
  if (state == MOVING || state == LEVELING) serviceMotion();
  if (state == MOVING) serviceLift();
  if (state == LEVELING && !motion.active) serviceLeveling();
  printTelemetry();
}
