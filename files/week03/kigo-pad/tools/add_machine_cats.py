#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_machine_cats.py — 「機械の分類」を data/kigo.json に足す
------------------------------------------------------------------------
人の分類（時候/天文/地理/生活/行事/動物/植物 = モノの種類）に対し、
機械は「語の主題＝意味」でまとめ直す、という対比を作る。

ここでは言語モデル(私)が各語を主題で7群に分類した結果を埋め込む。
将来は本物の埋め込みベクトル(UMAP/クラスタリング)に差し替え可能。

追加するキー:
  db["mcats"]     … 機械の分類名(7)
  db["ko_mcat"]   … 72候それぞれの機械分類 index
  overlay[k]["m"] … 各季語の機械分類 index

※ 時間軸(col=72候)は人・機械で共通。縦軸(分類)だけが違う、という設計。
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "kigo.json")

# 機械の分類（主題ベース。人の「モノの種類」とは切り口が違う）
MCATS = ["光・天象", "水", "風・気", "草木", "生きもの", "人の営み", "土・地"]
# index:  0          1     2        3      4            5            6

# 72候の機械分類（主題＝その候の中心にある事物で判定）
KO_MCAT = [
    2, 4, 4, 6, 0, 3, 4, 3, 4, 4,   # 0-9   東風/鶯/魚/土/霞/草木/虫/桃/蝶/雀
    3, 0, 4, 4, 0, 3, 3, 3, 4, 4,   # 10-19 桜/雷/燕/雁/虹/葭/苗/牡丹/蛙/蚯蚓
    3, 4, 3, 3, 4, 4, 3, 3, 3, 3,   # 20-29 竹笋/蚕/紅花/麦/螳螂/蛍/梅/乃東/菖蒲/半夏
    2, 3, 4, 3, 2, 1, 2, 4, 0, 3,   # 30-39 温風/蓮/鷹/桐/溽暑/大雨/涼風/蝉/霧/綿
    2, 3, 1, 4, 4, 0, 4, 1, 4, 3,   # 40-49 天地粛/禾/露/鶺鴒/燕去/雷収/虫坏/水涸/雁来/菊
    4, 1, 1, 3, 3, 6, 3, 0, 2, 3,   # 50-59 蟋蟀/霜/霎/楓蔦/山茶/地凍/金盞/虹蔵/朔風/橘
    2, 4, 4, 3, 4, 3, 3, 1, 4, 3,   # 60-69 閉塞冬/熊/鮭/乃東生/麋/雪下麦/芹/水泉/雉/款冬
    1, 4,                            # 70-71 水沢/鶏
]

# 分類マスの季語の機械分類
OV_MCAT = {
    "1-2": 1, "3-1": 0, "6-6": 3, "7-5": 4, "8-5": 4, "10-6": 3, "11-4": 5,
    "18-6": 3, "25-5": 4, "26-1": 1, "29-4": 5, "30-3": 5, "31-1": 0, "33-5": 4,
    "34-1": 1, "37-2": 5, "39-5": 4, "40-4": 5, "41-1": 0, "43-1": 0, "47-5": 4,
    "50-6": 3, "54-1": 1, "57-2": 6, "60-1": 1, "61-3": 5, "64-3": 5, "66-4": 5,
    "68-5": 4, "70-6": 3,
}

def main():
    db = json.load(open(PATH, encoding="utf-8"))
    assert len(KO_MCAT) == 72, f"KO_MCAT must be 72, got {len(KO_MCAT)}"
    assert set(OV_MCAT.keys()) == set(db["overlay"].keys()), "overlay keys mismatch"

    db["mcats"] = MCATS
    db["ko_mcat"] = KO_MCAT
    for k, m in OV_MCAT.items():
        db["overlay"][k]["m"] = m

    json.dump(db, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 集計（人と機械で分布がどう違うか）
    from collections import Counter
    human = Counter()
    machine = Counter()
    for i in range(72):
        human["時候"] += 1
        machine[MCATS[KO_MCAT[i]]] += 1
    for k, o in db["overlay"].items():
        human[db["cats"][int(k.split("-")[1])]] += 1
        machine[MCATS[o["m"]]] += 1
    print("人の分類 分布:", dict(human))
    print("機械の分類 分布:", dict(machine))
    print(f"wrote {PATH}")

if __name__ == "__main__":
    main()
