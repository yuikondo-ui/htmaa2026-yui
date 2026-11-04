// Press to Hide : 4 copper electrodes -> 4 zones x 4 press levels
// step response (tx/rx), XIAO RP2040 (or XIAO ESP32S3: same pins)
//   TX : D10 -> copper tape ring on the back of the acrylic flange (one wire)
//   RX : A0..A3 -> copper tape on the 4 corner pads, foam 3 mm on top
//        each RX pin: 1M to 3V3 + 1M to GND
//   corners / zones:  A0 = top-left   A1 = top-right
//                     A2 = bottom-left A3 = bottom-right
//   level: 0 = not pressed, 1 = light (60%), 2 = medium (25%), 3 = hard (0% = hidden)
// Serial  (115200): "zone level total | c0 c1 c2 c3"   <- use this to tune the thresholds
// Serial1 (D6 TX) : "zone,level\n" when it changes      <- for the matrix driver

const int TX_PIN = D10;
const int RX_PIN[4] = {A0, A1, A2, A3};
const int NSAMP = 100;

// press-strength thresholds on the total (tune after looking at the Serial numbers)
float TH[3] = {30, 80, 150};     // light / medium / hard
const float HYST = 0.8;          // release when total < TH * HYST (stops flicker)

long base[4];
float val[4];
int zone = -1, level = 0;

long readCh(int ch) {
  long acc = 0;
  for (int i = 0; i < NSAMP; i++) {
    digitalWrite(TX_PIN, HIGH);
    int up = analogRead(RX_PIN[ch]);
    delayMicroseconds(100);
    digitalWrite(TX_PIN, LOW);
    int down = analogRead(RX_PIN[ch]);
    delayMicroseconds(100);
    acc += up - down;
  }
  return acc;
}

void calibrate() {               // plate resting, nobody touching
  for (int c = 0; c < 4; c++) {
    long s = 0;
    for (int k = 0; k < 8; k++) s += readCh(c);
    base[c] = s / 8;
    val[c] = 0;
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  analogReadResolution(12);
  delay(1500);
  calibrate();
}

void loop() {
  float tot = 0;
  for (int c = 0; c < 4; c++) {
    float d = (float)(readCh(c) - base[c]) / NSAMP;
    if (d < 0) d = 0;
    val[c] = 0.6 * val[c] + 0.4 * d;
    tot += val[c];
  }

  // level with hysteresis
  int newLevel = 0;
  for (int i = 0; i < 3; i++) {
    float th = (i < level) ? TH[i] * HYST : TH[i];
    if (tot > th) newLevel = i + 1;
  }

  // zone = corner with the biggest share (only while pressed)
  int newZone = zone;
  if (newLevel > 0) {
    int best = 0;
    for (int c = 1; c < 4; c++) if (val[c] > val[best]) best = c;
    if (zone < 0 || level == 0) newZone = best;            // lock zone at the start of a press
  } else newZone = -1;

  if (newLevel != level || newZone != zone) {
    level = newLevel; zone = newZone;
    Serial1.print(zone); Serial1.print(','); Serial1.println(level);
  }

  Serial.print(zone); Serial.print(' ');
  Serial.print(level); Serial.print(' ');
  Serial.print(tot, 1); Serial.print(" | ");
  for (int c = 0; c < 4; c++) { Serial.print(val[c], 1); Serial.print(' '); }
  Serial.println();

  if (Serial.read() == 'c') calibrate();   // type c in Serial Monitor to re-zero
}
