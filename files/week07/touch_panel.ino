// Touch panel test — XIAO RP2040, HTMAA input devices week
// D0 : copper electrode (step response with the internal pull-up, no resistor)
// D8 : panel LED through R1 (100 ohm) -> J2
//
// Serial Plotter shows: raw, base, on (threshold)
// Each tap steps the LED: 100 -> 60 -> 25 -> 0 -> 100 %

#include <Arduino.h>
#include "hardware/gpio.h"

const int SENSE_PIN = D0;      // GP26
const int SENSE_GP  = 26;      // raw GPIO number for fast reads
const int LED_PIN   = D8;      // GP2

const int SAMPLES = 128;   // 32 → 128      // averaging per reading
const uint32_t TIMEOUT = 20000;

// thresholds above the untouched baseline (tune after looking at the plot)
float TH_ON  = 8.0;            // touch starts when raw > base + TH_ON
float TH_OFF = 4.0;            // touch ends   when raw < base + TH_OFF

const int LEVELS[] = {255, 153, 64, 0};   // 100, 60, 25, 0 %
int level = 0;
float shown = 255;             // brightness currently on the LED (for fading)

float base = 0;
bool touched = false;

// one step-response reading: discharge the pin, release it to the pull-up,
// count how long it takes to read HIGH. A finger adds capacitance -> slower.
uint32_t readOnce() {
  pinMode(SENSE_PIN, OUTPUT);
  digitalWrite(SENSE_PIN, LOW);
  delayMicroseconds(20);
  uint32_t n = 0;
  noInterrupts();
  pinMode(SENSE_PIN, INPUT_PULLUP);
  while (!gpio_get(SENSE_GP) && n < TIMEOUT) n++;
  interrupts();
  return n;
}

float readSensor() {
  uint32_t sum = 0;
  for (int i = 0; i < SAMPLES; i++) sum += readOnce();
  return (float)sum / SAMPLES;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, LEVELS[level]);

  delay(1500);                 // keep hands off the panel while it calibrates
  float s = 0;
  for (int i = 0; i < 100; i++) { s += readSensor(); delay(5); }
  base = s / 100;
}

void loop() {
  float raw = readSensor();

  if (!touched && raw > base + TH_ON) {          // finger arrived
    touched = true;
    level = (level + 1) % 4;                       // next brightness step
  } else if (touched && raw < base + TH_OFF) {   // finger left
    touched = false;
  }

  // follow slow drift of the untouched value (temperature, cable moving)
  if (!touched) base += (raw - base) * 0.01;

  // fade toward the target brightness (~0.5 s)
  shown += (LEVELS[level] - shown) * 0.15;
  analogWrite(LED_PIN, (int)shown);

  // Serial Plotter / CSV
  Serial.print("raw:");  Serial.print(raw);
  Serial.print(" base:"); Serial.print(base);
  Serial.print(" on:");   Serial.print(base + TH_ON);
  Serial.print(" led:");  Serial.println(LEVELS[level] / 10.0);

  delay(10);
}
