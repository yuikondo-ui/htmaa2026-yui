#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_kigosai.py — きごさい「5000季語一覧」索引を構造化して取り込む（個人利用）
------------------------------------------------------------------------
索引1ページ( https://kigosai.sub.jp/001/27701-2 )だけから
  (季語, id, 季節, 時期, 分類) を全部抜き出す。個別ページは叩かない。

出力: data/kigosai_index.json  … [{"w":語, "id":n, "season":春, "part":初春, "cat":時候}, ...]
※ 読み・解説はこの索引に無い（個別ページ）。必要時に別途取得＆要約する。
※ 語・季節・分類は事実データ。再配布はしない前提での個人/授業利用。
"""
import re, json, os, sys, argparse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = ["時候", "天文", "地理", "生活", "行事", "動物", "植物"]
PARTS = ["三春","初春","仲春","晩春","三夏","初夏","仲夏","晩夏",
         "三秋","初秋","仲秋","晩秋","三冬","初冬","仲冬","晩冬","新年","暮"]
PART_MARK = "春夏秋冬年暮"   # <a name="..."> 用

def load_html(url, cache):
    if os.path.exists(cache) and os.path.getsize(cache) > 1000:
        return open(cache, encoding="utf-8", errors="ignore").read()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    h = urllib.request.urlopen(req).read().decode("utf-8", "ignore")
    open(cache, "w", encoding="utf-8").write(h)
    return h

def season_of(h2text):
    for s in ("春", "夏", "秋", "冬"):
        if f"{s}の季語" in h2text:
            return s
    if "新年" in h2text:
        return "新年"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://kigosai.sub.jp/001/%e5%9f%ba%e6%9c%ac%e5%ad%a3%e8%aa%9e700")
    ap.add_argument("--out", default="kigo_basic.json")
    ap.add_argument("--cache", default="/tmp/kigo_basic.html")
    args = ap.parse_args()
    h = load_html(args.url, args.cache)
    # イベントを位置つきで集め、出現順に状態を更新しながら語を割り当てる
    events = []
    for m in re.finditer(r"<h[234][^>]*>(.*?)</h[234]>", h, re.S):   # h2/h4 両対応
        s = season_of(re.sub(r"<[^>]+>", "", m.group(1)))
        if s: events.append((m.start(), "season", s))
    for m in re.finditer(r'<a name="([^"]+)"></a>', h):              # 5000索引の時期見出し
        name = m.group(1)
        if any(c in name for c in PART_MARK):
            events.append((m.start(), "part", name))
    for m in re.finditer(r"<p>\s*(" + "|".join(PARTS) + r")\s*</p>", h):  # 700ページの時期見出し
        events.append((m.start(), "part", m.group(1)))
    for m in re.finditer(r"【(" + "|".join(CATS) + r")】", h):
        events.append((m.start(), "cat", m.group(1)))
    for m in re.finditer(r'<a href="https://kigosai\.sub\.jp/001/archives/(\d+)"[^>]*>([^<]+)</a>', h):
        events.append((m.start(), "kigo", (int(m.group(1)), m.group(2).strip())))

    events.sort(key=lambda e: e[0])
    season = part = cat = None
    seen = set()
    out = []
    for _, typ, val in events:
        if typ == "season": season, part, cat = val, None, None
        elif typ == "part": part = val
        elif typ == "cat":  cat = val
        elif typ == "kigo":
            kid, w = val
            if kid in seen or not season or not cat:   # 分類が確定した本文だけ採用（ナビ等は除外）
                continue
            seen.add(kid)
            out.append({"w": w, "id": kid, "season": season, "part": part, "cat": cat})

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    p = os.path.join(ROOT, "data", args.out)
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # レポート
    from collections import Counter
    bs = Counter(x["season"] for x in out)
    bc = Counter(x["cat"] for x in out)
    print(f"取り込み: {len(out)} 語  → {p}")
    print("季節別 :", dict(bs))
    print("分類別 :", dict(bc))
    print("例     :", [(x["w"], x["season"], x["part"], x["cat"]) for x in out[:6]])

if __name__ == "__main__":
    main()
