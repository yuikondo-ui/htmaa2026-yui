// Press-to-Hide : 4-corner capacitive force sensing (step response, tx/rx)
// XIAO RP2040
//   TX  : D10  -> copper tape ring under the acrylic flange (one wire, all 4 corners)
//   RX  : A0..A3 (D0..D3) -> copper tape on each corner pad
//         each RX pin: 1M to 3V3 and 1M to GND (bias to mid-supply)
//   foam (~3 mm, soft) between ring and pad electrode
//   Corner order: A0 = top-left, A1 = top-right, A2 = bottom-left, A3 = bottom-right
//   Serial  : "f x y | c0 c1 c2 c3"   (open Serial Plotter / Monitor, 115200)
//   Serial1 : "x,y,f\n" on D6 (TX) for the matrix driver board

const int TX_PIN = D10;
const int RX_PIN[4] = {A0, A1, A2, A3};
const int NSAMP = 100;          // samples per channel (more = smoother, slower)
const float F_ON = 40;          // total signal above baseline that counts as a press (tune)

long base[4];
float val[4];

long readCh(int ch) {
  long acc = 0;
  for (int i = 0; i < NSAMP; i++) {
    digitalWrite(TX_PIN, HIGH);
    int up = analogRead(RX_PIN[ch]);      // read right after the rising edge
    delayMicroseconds(100);               // let the RX node settle back to bias
    digitalWrite(TX_PIN, LOW);
    int down = analogRead(RX_PIN[ch]);    // read right after the falling edge
    delayMicroseconds(100);
    acc += (up - down);
  }
  return acc;
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  analogReadResolution(12);
  delay(1500);                            // keep hands off: plate resting = baseline
  for (int c = 0; c < 4; c++) {
    long s = 0;
    for (int k = 0; k < 8; k++) s += readCh(c);
    base[c] = s / 8;
  }
}

void loop() {
  float tot = 0;
  for (int c = 0; c < 4; c++) {
    float d = (float)(readCh(c) - base[c]) / NSAMP;   // pressing -> gap shrinks -> coupling up
    if (d < 0) d = 0;
    val[c] = 0.6 * val[c] + 0.4 * d;                 // light smoothing
    tot += val[c];
  }
  float x = -1, y = -1;
  if (tot > F_ON) {
    x = (val[1] + val[3]) / tot;          // 0 = left, 1 = right
    y = (val[2] + val[3]) / tot;          // 0 = top,  1 = bottom
  }
  Serial.print(tot); Serial.print(' ');
  Serial.print(x, 3); Serial.print(' ');
  Serial.print(y, 3); Serial.print(" | ");
  for (int c = 0; c < 4; c++) { Serial.print(val[c], 1); Serial.print(' '); }
  Serial.println();
  if (x >= 0) { Serial1.print(x, 3); Serial1.print(','); Serial1.print(y, 3); Serial1.print(','); Serial1.println(tot, 1); }
}
