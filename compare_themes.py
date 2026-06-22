# -*- coding: utf-8 -*-
import json
from collections import Counter

with open("school_ichiran_data.json", encoding="utf-8") as f:
    schools = json.load(f)

TABLE_CATS = ["地域・まちづくり", "環境・自然・SDGs", "福祉・共生", "国際理解", "職業・キャリア", "平和・人権"]
TABLE_MAP = {
    "chiiki": "地域・まちづくり", "kankyo": "環境・自然・SDGs", "fukushi": "福祉・共生",
    "kokusai": "国際理解", "shokugyo": "職業・キャリア", "heiwa": "平和・人権",
}

MORI_THEMES = {
    "校区探検・私たちの町": ["校区", "私たちの町", "まちたんけん", "郷土", "地域理解", "にわくぼ", "土居", "学ぼう私たちの町"],
    "SDGs・環境まちづくり": ["SDGs", "SDG", "環境にやさしい", "Save The Earth", "水とゴミ", "米作り", "米づくり"],
    "バリアフリー・福祉": ["バリアフリー", "福祉", "障がい", "ボランティア", "高齢者", "ユニバーサル"],
    "平和学習・戦争": ["平和", "戦争", "広島", "沖縄", "空襲", "原爆"],
    "国際・多文化共生": ["国際理解", "多文化", "外国", "ルーツ", "在日"],
    "キャリア・進路": ["キャリア", "進路", "職場体験", "将来", "職業"],
    "防災": ["防災", "防災バッグ"],
    "林間学習": ["林間"],
    "情報・ICT": ["情報活用", "情報教育", "ICT", "タブレット", "情報モラル", "プログラミング"],
    "いのちの学習": ["いのちの学習", "薬物", "LGBT", "性の多様"],
    "人権・同和": ["人権", "同和", "部落"],
}


def school_text(s):
    t = s.get("plan_summary", "")
    for r in s["grade_rows"]:
        t += r.get("plan_theme", "")
    return t


out = []
out.append(f"=== テーマ表6分類の出現（{len(schools)}校） ===")
cat_cnt = Counter()
for s in schools:
    for c in s["theme_cats"]:
        cat_cnt[TABLE_MAP[c]] += 1
for cat in TABLE_CATS:
    out.append(f"{cat}: {cat_cnt[cat]}/{len(schools)}校")

out.append("")
out.append("=== 守口市でよく見られる具体テーマ ===")
for name, kws in MORI_THEMES.items():
    cnt = sum(1 for s in schools if any(kw in school_text(s) for kw in kws))
    out.append(f"{name}: {cnt}/{len(schools)}校")

out.append("")
out.append("=== テーマ表との対応評価 ===")
mapping = {
    "校区探検・私たちの町": "地域・まちづくり（小3まちたんけん等）",
    "SDGs・環境まちづくり": "環境・自然・SDGs",
    "バリアフリー・福祉": "福祉・共生",
    "平和学習・戦争": "平和・人権",
    "国際・多文化共生": "国際理解",
    "キャリア・進路": "職業・キャリア",
    "防災": "環境行の中1「防災・地域安全」に包含",
    "林間学習": "テーマ表に独立行なし（体験学習として各校計画にあり）",
    "情報・ICT": "テーマ表に独立行なし（⑥情報活用スキルで扱う設計）",
    "いのちの学習": "テーマ表に独立行なし（中学校の年間計画に多い）",
    "人権・同和": "平和・人権行＋福祉行に分散",
}
for name, note in mapping.items():
    kws = MORI_THEMES[name]
    cnt = sum(1 for s in schools if any(kw in school_text(s) for kw in kws))
    out.append(f"[{cnt}校] {name} → {note}")

with open("theme_compare.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n".join(out))
