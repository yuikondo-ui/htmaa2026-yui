/* ============================================================================
   kigo_pad — ポケット歳時記（実機ファームウェア）
   ----------------------------------------------------------------------------
   Seeed XIAO RP2040 + SSD1306(128x64) + 6タッチパッド (QPad)

   操作:
     4方向        … 移動（左右=候, 上下=分類）
     q0 タップ    … ズームイン（説明を読む）
     q0 長押し    … 採集（LittleFSに保存＋画面フラッシュ）
     q5           … ズームアウト（場所＝現在地マップ）
     ズーム軸: 場所 ← 語 → 説明

   準備:
     - Arduino-Pico (earlephilhower) コア / ボード = Seeed XIAO RP2040
     - ライブラリ: Adafruit SSD1306, Adafruit GFX
     - Tools → USB Stack → Adafruit TinyUSB（LittleFS + Serial 同居のため）
     - Tools → Flash Size → 好みで LittleFS 領域を確保（例 1MB FS）

   生成物 kigo_font.h / kigo_table.h を同じフォルダに置く（make_font.py が作る）。

   タッチは Quentin の test_touch_RP2040 準拠：
      pins {3,4,2,27,1,26}（pad0..5）, INPUT_PULLUP で立ち上がり計数, 閾値6。
   ⚠️ 各パッドの「物理位置 → 役割」だけ実機で確認し、ズレていれば PAD_PIN[] の番号を入替。
   ========================================================================== */
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <LittleFS.h>
#include "kigo_font.h"
#include "kigo_table.h"

// ---------- 表示 ----------
#define SCREEN_W 128
#define SCREEN_H 64
#define OLED_ADDR 0x3C
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

// XIAO RP2040 の RGB LED（active-low = HIGHで消灯）。眩しくないよう消しておく。
#define PIN_RED 17
#define PIN_GREEN 16
#define PIN_BLUE 25

// ---------- パッドのピン（役割順）----------
// Yui の実機マップ（OLEDを上に持った時）：左に十字4枚＋右に2枚
//   ↑上=左上=GPIO26  ↓下=左下=GPIO2  ←左=左左=GPIO27  →右=左右=GPIO1
//   q0=右下(右-左)=GPIO4   q5=右上(右-右)=GPIO3   ← q0/q5が逆なら 4 と 3 を入替
enum { P_LEFT, P_RIGHT, P_UP, P_DOWN, P_ZIN, P_ZOUT, N_PAD };
//                    LEFT RIGHT UP DOWN q0 q5
int PAD_PIN[N_PAD] = {  27,   1, 26,  2,  4, 3 };

// ---------- タッチ検出（Quentin の test_touch_RP2040 準拠）----------
bool     touchNow[N_PAD]   = { false };
bool     touchPast[N_PAD]  = { false };
uint32_t pressStart[N_PAD] = { 0 };
const int      TOUCH_THRESHOLD = 6;    // Quentin と同じ
const int      TOUCH_TMAX      = 200;
const uint16_t HOLD_MS         = 400;  // q0 これ以上で採集

// 1パッドの静電容量：LOWで放電 → プルアップで充電 → 立ち上がるまでの回数
int readTouch(int pin){
  pinMode(pin, OUTPUT); digitalWriteFast(pin, LOW);   // 放電
  delayMicroseconds(25);                               // settle
  pinMode(pin, INPUT_PULLUP);                           // プルアップで充電
  int t = 0; while (!digitalReadFast(pin) && t < TOUCH_TMAX) t++;
  return t;                                             // 指が触れると大きくなる
}

// ---------- 現在地とズーム ----------
int col = 0, row = 0;      // row: 0=時候 … 6=植物
int zoom = 0;              // -1 場所 / 0 語 / +1 説明
bool q0Saved = false;
uint16_t savedCount = 0;
uint32_t enteredAt = 0;    // このマスに入った時刻（滞在時間の計測）

// ---------- セル参照 ----------
int ovIndex(int c, int r){ for (int i=0;i<N_OV;i++) if (OV_COL[i]==c && OV_ROW[i]==r) return i; return -1; }
const char* cellKigo(int c, int r){ if (r==0) return KO_NAME[c]; int i=ovIndex(c,r); return i<0?nullptr:OV_KIGO[i]; }
const char* cellYomi(int c, int r){ if (r==0) return KO_YOMI[c]; int i=ovIndex(c,r); return i<0?"":OV_YOMI[i]; }
const char* seasonStr(int c){ return SEASON_NAME[KO_SEASON[c]]; }
const char* sekkiStr (int c){ return SEKKI_NAME[c/3]; }
const char* phaseStr (int c){ return PHASE_NAME[c%3]; }
const char* catStr   (int r){ return r==0 ? "時候" : CAT_NAME[r]; }

// ================= 文字描画（生成ビットマップ） =================
int utf8Next(const char* s, int i, uint32_t& cp){
  uint8_t c = (uint8_t)s[i];
  if (c < 0x80)            { cp=c;                                              return 1; }
  else if ((c>>5)==0x6)    { cp=((c&0x1F)<<6)|(s[i+1]&0x3F);                    return 2; }
  else if ((c>>4)==0xE)    { cp=((c&0x0F)<<12)|((s[i+1]&0x3F)<<6)|(s[i+2]&0x3F);return 3; }
  else                     { cp=((c&0x07)<<18)|((s[i+1]&0x3F)<<12)|((s[i+2]&0x3F)<<6)|(s[i+3]&0x3F); return 4; }
}
int utf8Count(const char* s){ int n=0; uint32_t cp; for(int i=0;s[i];){ i+=utf8Next(s,i,cp); n++; } return n; }
int glyphIndex(const uint16_t* t, int n, uint16_t cp){
  int lo=0, hi=n-1; while(lo<=hi){ int m=(lo+hi)>>1; uint16_t v=t[m];
    if(v==cp) return m; if(v<cp) lo=m+1; else hi=m-1; } return -1;
}
void blit(const uint8_t* base, int size, int gi, int x, int y){
  if (gi<0) return;
  int rb=(size+7)/8; const uint8_t* p = base + (uint32_t)gi*rb*size;
  for (int yy=0; yy<size; yy++) for (int xb=0; xb<rb; xb++){
    uint8_t b = p[yy*rb+xb];
    for (int bit=0; bit<8; bit++) if (b & (0x80>>bit)){ int xx=xb*8+bit; if(xx<size) display.drawPixel(x+xx,y+yy,SSD1306_WHITE); }
  }
}
// 16px を左詰めで1文字ずつ（戻り値=次のx）
int put16(const char* s, int x, int y){
  uint32_t cp; for(int i=0;s[i];){ i+=utf8Next(s,i,cp);
    blit(GLYPH16, 16, glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp), x, y); x+=16; } return x;
}
// 16px 1文字
void put16cp(uint32_t cp, int x, int y){ blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x,y); }
// 32px 中央寄せ
void put32Centered(const char* s, int y){
  int nc=utf8Count(s), x0=(SCREEN_W-nc*32)/2; if(x0<0)x0=0;
  uint32_t cp; int k=0; for(int i=0;s[i];){ i+=utf8Next(s,i,cp);
    blit(GLYPH32,32,glyphIndex(GLYPH32_CP,N_GLYPH32,(uint16_t)cp),x0+k*32,y); k++; }
}
// 16px 中央寄せ（長いと詰める）
void put16Centered(const char* s, int y){
  int nc=utf8Count(s); int step = (nc*16<=SCREEN_W)?16:(SCREEN_W-2)/nc; if(step<8)step=8;
  int x0=(SCREEN_W-step*nc)/2; if(x0<0)x0=0;
  uint32_t cp; int k=0; for(int i=0;s[i];){ i+=utf8Next(s,i,cp);
    blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x0+k*step,y); k++; }
}
// 16px 折り返し（8文字/行）。戻り値=次のy
int put16Wrap(const char* s, int x, int y, int maxLines){
  int per = (SCREEN_W - x)/16; if(per<1) per=1;
  uint32_t cp; int k=0, line=0;
  for(int i=0;s[i];){ i+=utf8Next(s,i,cp);
    if(k>=per){ k=0; line++; y+=16; if(line>=maxLines) break; }
    blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x+k*16,y); k++;
  }
  return y+16;
}

// ================= ビュー =================
void drawStatus(int c, int r){                 // y0..16
  int x = 0;
  x = put16(seasonStr(c), x, 0);               // 季節1字
  x = put16(sekkiStr(c),  x, 0);               // 節気2字
  uint32_t cp; utf8Next(phaseStr(c), 0, cp);   // 候相の頭1字（初/次/末）
  put16cp(cp, x, 0);
  const char* cat = catStr(r);
  put16(cat, SCREEN_W - 16*utf8Count(cat), 0); // 分類は右詰め
}
void drawWord(int c, int r){
  drawStatus(c, r);
  const char* k = cellKigo(c,r);
  if (k) put32Centered(k, 16); else put32Centered("──", 16);
  const char* y = cellYomi(c,r);
  if (y && y[0]) put16Centered(y, 48);
}
void drawExplain(int c, int r){
  const char* k = cellKigo(c,r);
  if (!k){ put16("ここに季語はありません", 0, 24); return; }
  put16(k, 0, 0);                              // 季語（上に1行）
  const char* d = "";                          // 説明
  int i = ovIndex(c,r);
  if (i>=0) d = OV_DESC[i];
  else if (r==0) d = KO_DESC[c];
  if (d && d[0]) put16Wrap(d, 0, 18, 3);       // 8字×3行 まで
}
void drawPlace(int c, int r){
  // 上：72候の帯（4季）＋現在地。下：ラベル。
  int x0=2, y0=2, w=SCREEN_W-4, h=40;
  display.drawRect(x0,y0,w,h,SSD1306_WHITE);
  for(int s=1;s<4;s++){ int sx=x0 + w*s/4; for(int yy=y0; yy<y0+h; yy+=3) display.drawPixel(sx,yy,SSD1306_WHITE); }
  int px = x0 + (int)((float)col/72*w);
  int py = y0 + (int)((float)row/6*(h-1));
  display.drawFastVLine(px, y0, h, SSD1306_WHITE);
  display.fillCircle(px, py, 3, SSD1306_WHITE);
  // ラベル
  int x=0; x=put16(seasonStr(c),x,46); x=put16(sekkiStr(c),x,46);
  uint32_t cp; utf8Next(phaseStr(c),0,cp); put16cp(cp,x,46);
}
void render(){
  display.clearDisplay();
  if (zoom==1)      drawExplain(col,row);
  else if (zoom==-1) drawPlace(col,row);
  else               drawWord(col,row);
  display.display();
}

// ================= LittleFS ログ =================
void logLine(const char* file, const String& line){
  File f = LittleFS.open(file, "a"); if(f){ f.println(line); f.close(); }
}
void logMove(char ev){
  uint32_t now = millis(), dwell = now - enteredAt;
  String s = String(ev)+","+col+","+row+","+now+","+dwell;
  logLine("/track.csv", s);
  Serial.println(s);
  enteredAt = now;
}

// ================= 動作 =================
void doSave(){
  const char* k = cellKigo(col,row);
  if(!k){ display.invertDisplay(true); delay(60); display.invertDisplay(false); return; } // 空マスは採れない
  logMove('S');
  logLine("/saved.csv", String(col)+","+row+","+millis());
  savedCount++;
  display.invertDisplay(true); delay(120); display.invertDisplay(false);  // 採った手応え
  render();
}
void moveTo(int dc, int dr){
  if(dc||dr) logMove('M');
  col = ((col + dc) % 72 + 72) % 72;
  row = row + dr; if(row<0)row=0; if(row>6)row=6;
  render();   // （スライドアニメを足すならここで。まずは確実に動く即描画）
}
void zoomIn(){  if(zoom<1){ zoom++; render(); } }
void zoomOut(){ if(zoom>-1){ zoom--; render(); } }

void onPress(int i){
  switch(i){
    case P_LEFT:  moveTo(-1,0); break;
    case P_RIGHT: moveTo(+1,0); break;
    case P_UP:    moveTo(0,-1); break;
    case P_DOWN:  moveTo(0,+1); break;
    case P_ZOUT:  zoomOut();    break;
    case P_ZIN:   q0Saved=false; break;   // タップ/長押しは hold と release で判定
  }
}
void onRelease(int i){
  if(i==P_ZIN && !q0Saved) zoomIn();      // 短押し = ズームイン
}

// ================= シリアル（PC連携） =================
void dumpFile(const char* file){
  File f = LittleFS.open(file, "r");
  if(f){ while(f.available()) Serial.write(f.read()); f.close(); }
  Serial.println("END");
}
void handleSerial(){
  static String cmd;
  while(Serial.available()){
    char ch = Serial.read();
    if(ch=='\n'){
      cmd.trim();
      if(cmd=="HELLO") Serial.printf("QPAD-SAIJIKI v1  saved=%u\n", savedCount);
      else if(cmd=="DUMP")  dumpFile("/track.csv");
      else if(cmd=="SAVED") dumpFile("/saved.csv");
      else if(cmd=="CLR"){ LittleFS.remove("/track.csv"); LittleFS.remove("/saved.csv"); savedCount=0; Serial.println("OK"); }
      cmd = "";
    } else if(ch!='\r') cmd += ch;
  }
}

// ================= setup / loop =================
void setup(){
  Serial.begin(115200);
  LittleFS.begin();
  Wire.setSDA(6); Wire.setSCL(7); Wire.begin();     // XIAO RP2040 の既定 I2C = QPad の OLED
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)){ Serial.println("SSD1306 not found"); for(;;){} }
  pinMode(PIN_RED,OUTPUT); pinMode(PIN_GREEN,OUTPUT); pinMode(PIN_BLUE,OUTPUT);
  digitalWrite(PIN_RED,HIGH); digitalWrite(PIN_GREEN,HIGH); digitalWrite(PIN_BLUE,HIGH); // 消灯
  enteredAt = millis();
  render();
}

void loop(){
  uint32_t now = millis();
  for(int i=0;i<N_PAD;i++){
    int v = readTouch(PAD_PIN[i]);
    touchPast[i] = touchNow[i];
    touchNow[i]  = (v > TOUCH_THRESHOLD);
    if(touchNow[i] && !touchPast[i]){ pressStart[i]=now; onPress(i); }    // 押した瞬間
    else if(!touchNow[i] && touchPast[i]){ onRelease(i); }                 // 離した瞬間
  }
  // q0 長押し → 採集（押しっぱなしの間に一度だけ）
  if(touchNow[P_ZIN] && !q0Saved && now-pressStart[P_ZIN] >= HOLD_MS){ q0Saved=true; doSave(); }

  handleSerial();
  delay(20);   // Quentin と同様、少し落ち着かせる
}
