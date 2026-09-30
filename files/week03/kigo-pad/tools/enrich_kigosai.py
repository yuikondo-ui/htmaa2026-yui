#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_kigosai.py — 基本季語700 の各ページから 読み＋解説 を取り、長い解説は要約
------------------------------------------------------------------------
入力 : data/kigo_basic.json（import_kigosai.py が作る；w,id,season,part,cat）
出力 : 同ファイルに yomi, desc(要約) を追記
キャッシュ : /tmp/kigo_pages/<id>.html（再実行が速い・サーバに優しい）

使い方:
  python3 tools/enrich_kigosai.py --limit 8     # まず8語だけ試す
  python3 tools/enrich_kigosai.py               # 全部
"""
import re, json, os, time, argparse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = "/tmp/kigo_pages"
DESC_LIMIT = 48   # 要約の目安文字数（実機は先頭〜24字表示、プロトタイプ/カードは全文）

def fetch(kid):
    os.makedirs(PAGES, exist_ok=True)
    fp = os.path.join(PAGES, f"{kid}.html")
    if os.path.exists(fp) and os.path.getsize(fp) > 1000:
        return open(fp, encoding="utf-8", errors="ignore").read()
    url = f"https://kigosai.sub.jp/001/archives/{kid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    h = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    open(fp, "w", encoding="utf-8").write(h)
    time.sleep(0.15)   # 少し待つ
    return h

def parse_yomi(h):
    m = re.search(r"<title>([^（(]+)[（(]([^）)]+)[）)]", h)
    if not m:
        return ""
    # 旧かな併記などは最初の読みだけ採用
    return re.split(r"[、，]", m.group(2))[0].strip()

def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&#8211;", "—").replace("&nbsp;", " ")
    return re.sub(r"\s+", "", s).strip()

def parse_desc(h):
    m = re.search(r"【解説】(.*?)【", h, re.S)
    if not m:
        return ""
    return strip_tags(m.group(1))

def summarize(t, limit=DESC_LIMIT):
    t = t.strip()
    if len(t) <= limit:
        return t
    out = ""
    for sent in re.split(r"(?<=。)", t):
        if not sent:
            continue
        if out and len(out) + len(sent) > limit:
            break
        out += sent
    return out or (t[:limit] + "…")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)   # 0 = 全部
    args = ap.parse_args()
    p = os.path.join(ROOT, "data", "kigo_basic.json")
    data = json.load(open(p, encoding="utf-8"))
    items = data if args.limit == 0 else data[:args.limit]

    done = 0
    for i, k in enumerate(items):
        try:
            h = fetch(k["id"])
            k["yomi"] = parse_yomi(h)
            raw = parse_desc(h)
            k["desc"] = summarize(raw)
            k["desc_full_len"] = len(raw)
            done += 1
        except Exception as e:
            k["yomi"] = k.get("yomi", "")
            k["desc"] = k.get("desc", "")
            print(f"  ! {k['w']} ({k['id']}): {e}")
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(items)} …")
            json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)  # 途中保存

    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # レポート
    shown = items[:8]
    for k in shown:
        print(f"  {k['w']}（{k.get('yomi','')}）{k['cat']}: {k.get('desc','')}")
    longs = sum(1 for k in items if k.get("desc_full_len", 0) > DESC_LIMIT)
    print(f"完了 {done}/{len(items)}  要約が効いた語: {longs}")

if __name__ == "__main__":
    main()
