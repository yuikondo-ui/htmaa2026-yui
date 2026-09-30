#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_font.py — 「ポケット歳時記」データ → 実機用ヘッダ + 検証PNG を生成
------------------------------------------------------------------------
入力 : data/kigo.json   (単一ソース・オブ・トゥルース)
出力 :
  firmware/kigo_font.h   使う文字だけの 32x32(漢字) と 16x16(かな) 1bpp ビットマップ
  firmware/kigo_table.h  72候 + 分類オーバーレイのセル表（UTF-8文字列で保持）
  kigo-data.js           ブラウザ・プロトタイプ用（kigo.json から再生成して同期）
  tools/preview.png      生成したビットマップから描き戻した確認画像（目視検証用）

使い方 :
  python3 tools/make_font.py                 # 既定フォントで生成
  python3 tools/make_font.py --font X.otf    # フォント指定

必要 : Pillow  (pip install Pillow) と 日本語明朝フォント
注意 : RP2040 は flash がメモリマップされ PROGMEM 不要なので、
       生成ヘッダは素の const 配列（pgm_read 不要）。
"""
import json, os, sys, argparse, shutil
from PIL import Image, ImageDraw, ImageFont

# ヘッダは各スケッチ(.ino)と同じフォルダに要る（Arduinoはフォルダ単位でコンパイル）
SKETCH_DIRS = ["kigo_min", "kigo_pad"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 大きい見出し(32px)は明朝で美しく。小さいステータス(16px)は太ゴシックで潰れず読める。
DEFAULT_FONTS = [
    "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    "/System/Library/Fonts/Supplemental/NotoSerifCJK-jp.ttc",
    os.path.join(HERE, "NotoSerifJP-SemiBold.otf"),
]
DEFAULT_FONTS16 = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
]

def find_font(explicit, cands):
    for p in ([explicit] if explicit else []) + cands:
        if p and os.path.exists(p):
            return p
    sys.exit("フォントが見つかりません。--font / --font16 で指定してください。\n候補: " + ", ".join(cands))

def render_glyph(ch, size, font, thresh, scale=0.94):
    """ch を size×size の 1bpp ビットマップ(bytes)にする。行=size, 1行=ceil(size/8)バイト。"""
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font, int(size * scale))
    d.text((size / 2, size / 2), ch, font=fnt, fill=255, anchor="mm")
    px = img.load()
    row_bytes = (size + 7) // 8
    out = bytearray()
    for y in range(size):
        for xb in range(row_bytes):
            v = 0
            for bit in range(8):
                x = xb * 8 + bit
                if x < size and px[x, y] > thresh:   # 二値化しきい値
                    v |= 0x80 >> bit
            out.append(v)
    return bytes(out)

def collect_chars(db):
    kanji, kana = set(), set()
    for name, yomi in db["ko"]:
        kanji.update(name)
        kana.update(yomi)
    for o in db["overlay"].values():
        kanji.update(o["k"])
        kana.update(o["y"])
    # ステータス表示用（季節・節気・候相・分類）の漢字。32/16 の両方で使えるよう両テーブルに入れる。
    ui = set()
    for s in db["sekki"]:
        ui.update(s["n"]); ui.update(s["s"])
    for p in db["phases"]:
        ui.update(p)
    for c in db["cats"]:
        ui.update(c)
    for c in db.get("mcats", []):     # 機械の分類名（ステータス表示用）
        ui.update(c)
    ui.update("春夏秋冬人機械の地図")
    kanji |= ui
    kana |= ui   # 16px 側でも節気・分類をステータスに描けるように

    # 説明ビュー（16px）で使う：解説文・俳句・作者・候の自動解説テンプレート
    small = set()
    KO_DESC_TMPL = "の。草木や生きものの気配で名づけられた候"  # `${sekki}の${phase}。…候。` の固定部分
    small.update(KO_DESC_TMPL)
    # 説明ビューは季語名も 16px で描くので、名前の漢字も 16px 側へ
    for name, _ in db["ko"]:
        small.update(name)
    for o in db["overlay"].values():
        small.update(o["k"])
    for d in db.get("ko_desc", []):     # 72候のやさしい説明
        small.update(d)
    for o in db["overlay"].values():
        for fld in ("d", "h", "a"):
            small.update(o.get(fld) or "")
    small.update("「」—・")
    kana |= small     # 説明は 16px で描くので 16px 側に入れる
    return sorted(kanji, key=ord), sorted(kana, key=ord)

def emit_glyph_block(f, name, chars, size, font, thresh):
    row_bytes = (size + 7) // 8
    glyph_bytes = row_bytes * size
    f.write(f"// ---- {size}x{size} : {len(chars)} glyphs ----\n")
    f.write(f"#define {name}_SIZE   {size}\n")
    f.write(f"#define {name}_BYTES  {glyph_bytes}\n")
    f.write(f"#define N_{name}      {len(chars)}\n")
    f.write(f"const uint8_t {name}[] = {{\n")
    for ch in chars:
        b = render_glyph(ch, size, font, thresh)
        assert len(b) == glyph_bytes
        f.write("  " + ",".join(f"0x{x:02X}" for x in b) + f",  // U+{ord(ch):04X} {ch}\n")
    f.write("};\n")
    f.write(f"const uint16_t {name}_CP[N_{name}] = {{"
            + ",".join(str(ord(c)) for c in chars) + "};\n\n")

def c_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default=None, help="32px 見出し用（明朝推奨）")
    ap.add_argument("--font16", default=None, help="16px ステータス/読み用（太ゴシック推奨）")
    args = ap.parse_args()
    font32 = find_font(args.font, DEFAULT_FONTS)
    font16 = find_font(args.font16, DEFAULT_FONTS16)

    db = json.load(open(os.path.join(ROOT, "data", "kigo.json"), encoding="utf-8"))
    kanji, kana = collect_chars(db)
    print(f"font32 : {font32}")
    print(f"font16 : {font16}")
    print(f"kanji  : {len(kanji)} unique  → 32x32 ({len(kanji)*128} bytes)")
    print(f"kana   : {len(kana)} unique  → 16x16 ({len(kana)*32} bytes)")

    # ---------- kigo_font.h ----------
    fp = os.path.join(ROOT, "firmware", "kigo_font.h")
    with open(fp, "w", encoding="utf-8") as f:
        f.write("// AUTOGENERATED by tools/make_font.py — do not edit by hand.\n")
        f.write("#pragma once\n#include <Arduino.h>\n\n")
        emit_glyph_block(f, "GLYPH32", kanji, 32, font32, 110)
        emit_glyph_block(f, "GLYPH16", kana, 16, font16, 90)
    print(f"wrote  : {fp}")

    # ---------- kigo_table.h ----------
    seasons = ["春", "夏", "秋", "冬"]
    tp = os.path.join(ROOT, "firmware", "kigo_table.h")
    with open(tp, "w", encoding="utf-8") as f:
        f.write("// AUTOGENERATED by tools/make_font.py — do not edit by hand.\n")
        f.write("#pragma once\n#include <Arduino.h>\n\n")
        # 表示用の名前テーブル
        f.write("const char* const SEASON_NAME[4] = {" + ",".join(c_str(s) for s in seasons) + "};\n")
        f.write("const char* const SEKKI_NAME[24] = {" + ",".join(c_str(s["n"]) for s in db["sekki"]) + "};\n")
        f.write("const char* const PHASE_NAME[3]  = {" + ",".join(c_str(p) for p in db["phases"]) + "};\n")
        f.write(f"#define N_CAT {len(db['cats'])}\n")
        f.write("const char* const CAT_NAME[N_CAT] = {" + ",".join(c_str(c) for c in db["cats"]) + "};\n\n")

        f.write("#define N_CO 72\n")
        f.write("const char* const KO_NAME[N_CO] = {\n")
        for name, _ in db["ko"]:
            f.write(f"  {c_str(name)},\n")
        f.write("};\n")
        f.write("const char* const KO_YOMI[N_CO] = {\n")
        for _, yomi in db["ko"]:
            f.write(f"  {c_str(yomi)},\n")
        f.write("};\n")
        # 候ごとの季節 index (0..3)。節気=col/3, 候相=col%3 で引ける。
        f.write("const uint8_t KO_SEASON[N_CO] = {")
        f.write(",".join(str(seasons.index(db["sekki"][i // 3]["s"])) for i in range(72)))
        f.write("};\n")
        # 72候のやさしい説明（説明ビュー用）
        ko_desc = db.get("ko_desc", [""]*72)
        f.write("const char* const KO_DESC[N_CO] = {\n")
        for d in ko_desc:
            f.write(f"  {c_str(d)},\n")
        f.write("};\n\n")
        # overlay（分類マスの季語）
        ov = sorted(db["overlay"].items(), key=lambda kv: (int(kv[0].split("-")[0]), int(kv[0].split("-")[1])))
        f.write(f"#define N_OV {len(ov)}\n")
        f.write("const uint8_t OV_COL[N_OV]  = {" + ",".join(k.split("-")[0] for k, _ in ov) + "};\n")
        f.write("const uint8_t OV_ROW[N_OV]  = {" + ",".join(k.split("-")[1] for k, _ in ov) + "};\n")
        f.write("const char* const OV_KIGO[N_OV]   = {" + ",".join(c_str(v["k"]) for _, v in ov) + "};\n")
        f.write("const char* const OV_YOMI[N_OV]   = {" + ",".join(c_str(v["y"]) for _, v in ov) + "};\n")
        f.write("const char* const OV_DESC[N_OV]   = {" + ",".join(c_str(v.get("d","")) for _, v in ov) + "};\n")
        f.write("const char* const OV_HAIKU[N_OV]  = {" + ",".join(c_str(v.get("h","")) for _, v in ov) + "};\n")
        f.write("const char* const OV_AUTHOR[N_OV] = {" + ",".join(c_str(v.get("a","")) for _, v in ov) + "};\n")
    print(f"wrote  : {tp}")

    # 各スケッチフォルダにヘッダをコピー（.ino と同じ場所に必要）
    for d in SKETCH_DIRS:
        dd = os.path.join(ROOT, "firmware", d)
        if os.path.isdir(dd):
            shutil.copy(fp, os.path.join(dd, "kigo_font.h"))
            shutil.copy(tp, os.path.join(dd, "kigo_table.h"))
            print(f"copied : firmware/{d}/(kigo_font.h, kigo_table.h)")

    # ---------- kigo-data.js (regenerate for the browser prototype) ----------
    jp = os.path.join(ROOT, "kigo-data.js")
    with open(jp, "w", encoding="utf-8") as f:
        f.write("// AUTOGENERATED by tools/make_font.py from data/kigo.json — do not edit by hand.\n")
        f.write("window.KIGO_DB = ")
        f.write(json.dumps(db, ensure_ascii=False, indent=2))
        f.write(";\n")
    print(f"wrote  : {jp}")

    # ---------- preview.png (描き戻して目視検証) ----------
    make_preview(db, font32, font16)

def _blit(canvas, glyph_bytes, size, x0, y0, scale):
    row_bytes = (size + 7) // 8
    d = ImageDraw.Draw(canvas)
    for y in range(size):
        for xb in range(row_bytes):
            b = glyph_bytes[y * row_bytes + xb]
            for bit in range(8):
                if b & (0x80 >> bit):
                    x = xb * 8 + bit
                    if x < size:
                        d.rectangle([x0 + x * scale, y0 + y * scale,
                                     x0 + x * scale + scale - 1, y0 + y * scale + scale - 1], fill=255)

def make_preview(db, font32, font16):
    """生成した *ビットマップから* 128x64 OLED 相当を描いて確認する。フォント直描きではない。"""
    def g32(ch): return render_glyph(ch, 32, font32, 110)
    def g16(ch): return render_glyph(ch, 16, font16, 90)

    SCALE = 4
    W, H = 128, 64
    canvas = Image.new("L", (W * SCALE, H * SCALE), 0)

    name, yomi = db["ko"][0]              # 東風解凍 / はるかぜこおりをとく
    # 32px 漢字を中央に横並び
    n = len(name)
    total = n * 32
    x0 = (W - total) // 2
    for i, ch in enumerate(name):
        _blit(canvas, g32(ch), 32, (x0 + i * 32) * SCALE, 4 * SCALE, SCALE)
    # 16px 読みを下に（長いので詰めて描画: 10px送り）
    step = min(10, W // max(1, len(yomi)))
    yx = (W - step * len(yomi)) // 2
    for i, ch in enumerate(yomi):
        _blit(canvas, g16(ch), 16, (yx + i * step) * SCALE, 46 * SCALE, SCALE)

    out = os.path.join(HERE, "preview.png")
    # 反転して白地・黒字の方が確認しやすいので、そのまま白字黒地で保存（OLED相当）
    canvas.save(out)
    print(f"wrote  : {out}   ({name} / {yomi})")

if __name__ == "__main__":
    main()
