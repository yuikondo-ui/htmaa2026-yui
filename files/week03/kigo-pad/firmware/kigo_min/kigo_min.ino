/* ============================================================================
   kigo_min — 「ポケット歳時記」実機の関門テスト
   ----------------------------------------------------------------------------
   目的: SSD1306(128x64) に漢字を 32px で表示できることを確かめる最小スケッチ。
        生成した kigo_font.h / kigo_table.h を使い、七十二候を自動で送っていく。

   ボード : Seeed XIAO RP2040  (arduino-pico / earlephilhower コア)
   配線   : OLED は I2C。XIAO の既定 Wire は SDA=D4(GPIO6), SCL=D5(GPIO7)＝QPad と一致。
   準備   : ライブラリ "Adafruit SSD1306" と "Adafruit GFX" を導入。
            USB Stack は後段(LittleFS/HID)を見据えて Adafruit TinyUSB 推奨。

   ※ ヘッダは tools/make_font.py が data/kigo.json から生成する。編集しない。
   ========================================================================== */
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "kigo_font.h"     // GLYPH32[], GLYPH32_CP[], GLYPH16[], GLYPH16_CP[]
#include "kigo_table.h"    // KO_NAME[72], KO_YOMI[72], KO_SEASON[72]

#define SCREEN_W 128
#define SCREEN_H 64
#define OLED_ADDR 0x3C
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

const char* SEASON_CH[4] = { "春", "夏", "秋", "冬" };

// ---- UTF-8 を1文字ずつ codepoint に。戻り値=消費バイト数 ----
int utf8Next(const char* s, int i, uint32_t& cp) {
  uint8_t c = (uint8_t)s[i];
  if (c < 0x80)            { cp = c;                                             return 1; }
  else if ((c >> 5) == 0x6){ cp = ((c & 0x1F) << 6) | (s[i+1] & 0x3F);          return 2; }
  else if ((c >> 4) == 0xE){ cp = ((c & 0x0F) << 12) | ((s[i+1] & 0x3F) << 6)
                                  | (s[i+2] & 0x3F);                             return 3; }
  else                     { cp = ((c & 0x07) << 18) | ((s[i+1] & 0x3F) << 12)
                                  | ((s[i+2] & 0x3F) << 6) | (s[i+3] & 0x3F);    return 4; }
}
int utf8Count(const char* s) {
  int n = 0; uint32_t cp;
  for (int i = 0; s[i]; ) { i += utf8Next(s, i, cp); n++; }
  return n;
}

// ---- codepoint → グリフ番号（二分探索） ----
int glyphIndex(const uint16_t* cpTable, int n, uint16_t cp) {
  int lo = 0, hi = n - 1;
  while (lo <= hi) {
    int m = (lo + hi) >> 1;
    uint16_t v = cpTable[m];
    if (v == cp) return m;
    if (v < cp) lo = m + 1; else hi = m - 1;
  }
  return -1;
}

// ---- 1グリフを描画（size=32 or 16, base=対応する配列） ----
void drawGlyph(const uint8_t* base, int size, int gi, int x, int y) {
  if (gi < 0) return;
  int rowBytes = (size + 7) / 8;
  const uint8_t* p = base + (uint32_t)gi * rowBytes * size;
  for (int yy = 0; yy < size; yy++)
    for (int xb = 0; xb < rowBytes; xb++) {
      uint8_t b = p[yy * rowBytes + xb];
      for (int bit = 0; bit < 8; bit++)
        if (b & (0x80 >> bit)) {
          int xx = xb * 8 + bit;
          if (xx < size) display.drawPixel(x + xx, y + yy, SSD1306_WHITE);
        }
    }
}

// ---- 文字列を 32px で中央に ----
void draw32Centered(const char* s, int y) {
  int nc = utf8Count(s);
  int w  = nc * 32;
  int x0 = (SCREEN_W - w) / 2;
  if (x0 < 0) x0 = 0;                       // 4文字=128pxちょうど。5文字以上は左詰めでクリップ
  uint32_t cp; int i = 0, k = 0;
  while (s[i]) {
    i += utf8Next(s, i, cp);
    int gi = glyphIndex(GLYPH32_CP, N_GLYPH32, (uint16_t)cp);
    drawGlyph(GLYPH32, 32, gi, x0 + k * 32, y);
    k++;
  }
}

// ---- 文字列を 16px で中央に（長い読みは間隔を詰める） ----
void draw16Centered(const char* s, int y) {
  int nc = utf8Count(s);
  int step = (nc * 16 <= SCREEN_W) ? 16 : (SCREEN_W - 2) / nc;  // はみ出す時だけ詰める
  if (step < 8) step = 8;
  int x0 = (SCREEN_W - step * nc) / 2;
  if (x0 < 0) x0 = 0;
  uint32_t cp; int i = 0, k = 0;
  while (s[i]) {
    i += utf8Next(s, i, cp);
    int gi = glyphIndex(GLYPH16_CP, N_GLYPH16, (uint16_t)cp);
    drawGlyph(GLYPH16, 16, gi, x0 + k * step, y);
    k++;
  }
}

void showKo(int idx) {
  display.clearDisplay();
  // 左上: 季節（16px 漢字）
  uint32_t cp; utf8Next(SEASON_CH[KO_SEASON[idx]], 0, cp);
  drawGlyph(GLYPH16, 16, glyphIndex(GLYPH16_CP, N_GLYPH16, (uint16_t)cp), 2, 1);
  // 右上: 通し番号（内蔵ASCIIフォントで十分）
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(96, 4);
  display.print(idx + 1); display.print("/72");
  // 中央: 候名 32px
  draw32Centered(KO_NAME[idx], 20);
  // 下: 読み 16px
  draw16Centered(KO_YOMI[idx], SCREEN_H - 16);
  display.display();
}

int idx = 0;
uint32_t lastStep = 0;

void setup() {
  Serial.begin(115200);
  // XIAO RP2040 / QPad の I2C を明示（arduino-pico）
  Wire.setSDA(6);
  Wire.setSCL(7);
  Wire.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306 not found");
    for (;;) {}
  }
  Serial.printf("glyphs: %d(32px) %d(16px)\n", N_GLYPH32, N_GLYPH16);
  showKo(idx);
  lastStep = millis();
}

void loop() {
  // 2.5秒ごとに次の候へ（フォント表＋二分探索が全72候で動くことの確認）
  if (millis() - lastStep >= 2500) {
    idx = (idx + 1) % N_CO;
    showKo(idx);
    lastStep = millis();
  }
}
