/* ============================================================================
   kigo_pad — ポケット歳時記（実機・504グリッド / 基本季語700から配置）
   ----------------------------------------------------------------------------
   Seeed XIAO RP2040 + SSD1306(128x64) + 6タッチパッド (QPad)

   72候(左右) × 7分類(上下) = 504マス。時候の行=七十二候、他=きごさい基本季語。
   ←→ = 候を歩く（時間）/ ↑↓ = 分類を変える
   q0 タップ = 説明 / 長押し = 採集 ／ q5 = 場所（504マスの現在地マップ）

   準備: Arduino-Pico / XIAO RP2040 / USB Stack=Adafruit TinyUSB
         Adafruit SSD1306, Adafruit GFX ／ kigo_font.h,kigo_data.h(build_grid.py)
   ========================================================================== */
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <LittleFS.h>
#include "kigo_font.h"
#include "kigo_data.h"

#define SCREEN_W 128
#define SCREEN_H 64
#define OLED_ADDR 0x3C
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);
#define PIN_RED 17
#define PIN_GREEN 16
#define PIN_BLUE 25

// パッド（Yui の実機マップ）: ↑26 ↓2 ←27 →1  q0=4  q5=3
enum { P_LEFT, P_RIGHT, P_UP, P_DOWN, P_ZIN, P_ZOUT, N_PAD };
int PAD_PIN[N_PAD] = { 27, 1, 26, 2, 4, 3 };

// タッチ（Quentin 準拠）
bool touchNow[N_PAD]={false}, touchPast[N_PAD]={false};
uint32_t pressStart[N_PAD]={0};
const int TOUCH_THRESHOLD=6, TOUCH_TMAX=200; const uint16_t HOLD_MS=400;
int readTouch(int pin){ pinMode(pin,OUTPUT);digitalWriteFast(pin,LOW);delayMicroseconds(25);
  pinMode(pin,INPUT_PULLUP); int t=0;while(!digitalReadFast(pin)&&t<TOUCH_TMAX)t++; return t; }

int col=0, row=0, zoom=0;   // zoom: -1 場所 / 0 語 / +1 説明
bool q0Saved=false; uint16_t savedCount=0; uint32_t enteredAt=0;
int CI(){ return col*NROW + row; }
bool filled(int c,int r){ return GW[c*NROW+r][0] != 0; }

// ===== 文字描画 =====
int utf8Next(const char* s,int i,uint32_t& cp){ uint8_t c=(uint8_t)s[i];
  if(c<0x80){cp=c;return 1;} else if((c>>5)==0x6){cp=((c&0x1F)<<6)|(s[i+1]&0x3F);return 2;}
  else if((c>>4)==0xE){cp=((c&0x0F)<<12)|((s[i+1]&0x3F)<<6)|(s[i+2]&0x3F);return 3;}
  else{cp=((c&0x07)<<18)|((s[i+1]&0x3F)<<12)|((s[i+2]&0x3F)<<6)|(s[i+3]&0x3F);return 4;} }
int utf8Count(const char* s){ int n=0;uint32_t cp;for(int i=0;s[i];){i+=utf8Next(s,i,cp);n++;}return n; }
int glyphIndex(const uint16_t* t,int n,uint16_t cp){ int lo=0,hi=n-1;while(lo<=hi){int m=(lo+hi)>>1;uint16_t v=t[m];if(v==cp)return m;if(v<cp)lo=m+1;else hi=m-1;}return -1; }
void blit(const uint8_t* base,int size,int gi,int x,int y){ if(gi<0)return;int rb=(size+7)/8;const uint8_t* p=base+(uint32_t)gi*rb*size;
  for(int yy=0;yy<size;yy++)for(int xb=0;xb<rb;xb++){uint8_t b=p[yy*rb+xb];for(int bit=0;bit<8;bit++)if(b&(0x80>>bit)){int xx=xb*8+bit;if(xx<size)display.drawPixel(x+xx,y+yy,SSD1306_WHITE);}} }
int put16(const char* s,int x,int y){ uint32_t cp;for(int i=0;s[i];){i+=utf8Next(s,i,cp);blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x,y);x+=16;}return x; }
void put16cp(uint32_t cp,int x,int y){ blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x,y); }
void put32Centered(const char* s,int y){ int n=utf8Count(s),x0=(SCREEN_W-n*32)/2;if(x0<0)x0=0;uint32_t cp;int k=0;for(int i=0;s[i];){i+=utf8Next(s,i,cp);blit(GLYPH32,32,glyphIndex(GLYPH32_CP,N_GLYPH32,(uint16_t)cp),x0+k*32,y);k++;} }
void put16Centered(const char* s,int y){ int n=utf8Count(s);int step=(n*16<=SCREEN_W)?16:(SCREEN_W-2)/n;if(step<8)step=8;int x0=(SCREEN_W-step*n)/2;if(x0<0)x0=0;uint32_t cp;int k=0;for(int i=0;s[i];){i+=utf8Next(s,i,cp);blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x0+k*step,y);k++;} }
int put16Wrap(const char* s,int x,int y,int ml){ int per=(SCREEN_W-x)/16;if(per<1)per=1;uint32_t cp;int k=0,line=0;
  for(int i=0;s[i];){i+=utf8Next(s,i,cp);if(k>=per){k=0;line++;y+=16;if(line>=ml)break;}blit(GLYPH16,16,glyphIndex(GLYPH16_CP,N_GLYPH16,(uint16_t)cp),x+k*16,y);k++;}return y; }

// ===== ビュー =====
void drawStatus(){
  int x=0; x=put16(SEASON_NAME[KO_SEASON[col]],x,0); x=put16(SEKKI_NAME[col/3],x,0);
  uint32_t cp; utf8Next(PHASE_NAME[col%3],0,cp); put16cp(cp,x,0);
  const char* cat=CAT_NAME[row]; put16(cat,SCREEN_W-16*utf8Count(cat),0);
}
void drawWord(){ drawStatus(); const char* w=GW[CI()];
  if(w[0]){ int n=utf8Count(w); if(n<=4)put32Centered(w,16); else put16Centered(w,24);
    const char* y=GY[CI()]; if(y[0])put16Centered(y,48); }
  else put32Centered("──",16);
}
void drawExplain(){ const char* w=GW[CI()];
  if(!w[0]){ put16("この場所に季語はありません",0,24); return; }
  put16(w,0,0);
  const char* d=GD[CI()];
  if(d[0]) put16Wrap(d,0,18,3);
  else { const char* y=GY[CI()]; if(y[0])put16(y,0,18); }
}
void drawPlace(){
  const char* w=GW[CI()]; if(w[0]) put16(w,0,0); else put16("──",0,0);
  int x0=2,y0=20,w2=SCREEN_W-4,h=32;                 // 番号を画面内に収めるため少し上げる
  display.drawRect(x0,y0,w2,h,SSD1306_WHITE);
  for(int s=1;s<4;s++){ int sx=x0+w2*s/4; for(int yy=y0;yy<y0+h;yy+=3)display.drawPixel(sx,yy,SSD1306_WHITE); }
  // 埋まっているマスを点で
  for(int c=0;c<NCOL;c++) for(int r=0;r<NROW;r++) if(filled(c,r)){
    int px=x0+ (int)((long)c*(w2-1)/(NCOL-1));
    int py=y0+ (int)((long)r*(h-1)/(NROW-1));
    display.drawPixel(px,py,SSD1306_WHITE);
  }
  // 現在地
  int cx=x0+(int)((long)col*(w2-1)/(NCOL-1)), cy=y0+(int)((long)row*(h-1)/(NROW-1));
  display.drawFastVLine(cx,y0,h,SSD1306_WHITE);
  display.fillCircle(cx,cy,2,SSD1306_WHITE);
  display.setTextSize(1); display.setTextColor(SSD1306_WHITE); display.setCursor(2, SCREEN_H-9);
  display.print(col+1); display.print("/72");   // 分類名は日本語なので内蔵フォントでは出さない
}
void render(){ display.clearDisplay(); if(zoom==1)drawExplain(); else if(zoom==-1)drawPlace(); else drawWord(); display.display(); }

// ===== LittleFS / ログ =====
void logLine(const char* file,const String& line){ File f=LittleFS.open(file,"a");if(f){f.println(line);f.close();} }
void logMove(char ev){ uint32_t now=millis(),dw=now-enteredAt; String s=String(ev)+","+col+","+row+","+now+","+dw; logLine("/track.csv",s); Serial.println(s); enteredAt=now; }

// ===== 動作 =====
void moveTo(int dc,int dr){ if(dc||dr)logMove('M'); col=((col+dc)%NCOL+NCOL)%NCOL; row=row+dr; if(row<0)row=0; if(row>NROW-1)row=NROW-1; render(); }
void zoomIn(){ if(zoom<1){zoom++;render();} }
void zoomOut(){ if(zoom>-1){zoom--;render();} }
void doSave(){ if(!GW[CI()][0]){ display.invertDisplay(true);delay(60);display.invertDisplay(false); return; }
  logMove('S'); logLine("/saved.csv",String(col)+","+row+","+millis()); savedCount++;
  display.invertDisplay(true); delay(120); display.invertDisplay(false); render(); }

void onPress(int i){ switch(i){
  case P_LEFT: moveTo(-1,0); break; case P_RIGHT: moveTo(+1,0); break;
  case P_UP: moveTo(0,-1); break;  case P_DOWN: moveTo(0,+1); break;
  case P_ZOUT: zoomOut(); break;   case P_ZIN: q0Saved=false; break; } }
void onRelease(int i){ if(i==P_ZIN && !q0Saved) zoomIn(); }

// ===== シリアル =====
void dumpFile(const char* file){ File f=LittleFS.open(file,"r");if(f){while(f.available())Serial.write(f.read());f.close();} Serial.println("END"); }
void handleSerial(){ static String cmd;
  while(Serial.available()){ char ch=Serial.read();
    if(ch=='\n'){ cmd.trim();
      if(cmd=="HELLO") Serial.printf("QPAD-SAIJIKI grid  saved=%u\n",savedCount);
      else if(cmd=="DUMP") dumpFile("/track.csv");
      else if(cmd=="SAVED") dumpFile("/saved.csv");
      else if(cmd=="CLR"){ LittleFS.remove("/track.csv");LittleFS.remove("/saved.csv");savedCount=0;Serial.println("OK"); }
      cmd="";
    } else if(ch!='\r') cmd+=ch; } }

// ===== setup / loop =====
void setup(){
  Serial.begin(115200); LittleFS.begin();
  Wire.setSDA(6); Wire.setSCL(7); Wire.begin();
  if(!display.begin(SSD1306_SWITCHCAPVCC,OLED_ADDR)){ Serial.println("SSD1306 not found"); for(;;){} }
  pinMode(PIN_RED,OUTPUT);pinMode(PIN_GREEN,OUTPUT);pinMode(PIN_BLUE,OUTPUT);
  digitalWrite(PIN_RED,HIGH);digitalWrite(PIN_GREEN,HIGH);digitalWrite(PIN_BLUE,HIGH);
  enteredAt=millis(); render();
}
void loop(){
  uint32_t now=millis();
  for(int i=0;i<N_PAD;i++){ int v=readTouch(PAD_PIN[i]); touchPast[i]=touchNow[i]; touchNow[i]=(v>TOUCH_THRESHOLD);
    if(touchNow[i]&&!touchPast[i]){ pressStart[i]=now; onPress(i); }
    else if(!touchNow[i]&&touchPast[i]){ onRelease(i); } }
  if(touchNow[P_ZIN] && !q0Saved && now-pressStart[P_ZIN]>=HOLD_MS){ q0Saved=true; doSave(); }
  handleSerial(); delay(20);
}
