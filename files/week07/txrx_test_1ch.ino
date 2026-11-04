// 1-channel tx/rx step-response test (XIAO RP2040)
// TX: D10 -> top copper electrode      RX: A0 (D0) -> bottom copper electrode
// RX bias: 1M A0->3V3, 1M A0->GND      foam between the two electrodes
// Open Serial Plotter @115200: press the foam and watch the line go up.
const int TX_PIN = D10, RX_PIN = A0, NSAMP = 100;

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  analogReadResolution(12);
}

void loop() {
  long acc = 0;
  for (int i = 0; i < NSAMP; i++) {
    digitalWrite(TX_PIN, HIGH);
    int up = analogRead(RX_PIN);
    delayMicroseconds(100);
    digitalWrite(TX_PIN, LOW);
    int down = analogRead(RX_PIN);
    delayMicroseconds(100);
    acc += up - down;
  }
  Serial.println((float)acc / NSAMP);
}
