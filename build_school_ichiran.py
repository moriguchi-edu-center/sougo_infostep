# -*- coding: utf-8 -*-
"""各校の総合的な学習の時間計画から守口市フレームワーク対応の一覧表HTMLを生成"""
import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

BASE = os.path.dirname(__file__)
PLAN_DIR = os.path.join(BASE, "各学校総合的な学習の時間計画")
PDF_DIR = os.path.join(PLAN_DIR, "pdf")
SUPPORTED_EXT = {".pdf", ".docx", ".xls", ".xlsx"}
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
OUT_HTML = os.path.join(BASE, "school_joho_ichiran.html")
OUT_JSON = os.path.join(BASE, "school_ichiran_data.json")

THEME_CAT = {
    "chiiki": "地域・まちづくり",
    "kankyo": "環境・SDGs",
    "fukushi": "福祉・人権",
    "kokusai": "国際理解",
    "shokugyo": "職業・キャリア",
    "heiwa": "平和",
}
THEME_KW = {
    "地域": "chiiki", "まち": "chiiki", "まちづくり": "chiiki", "校区": "chiiki", "郷土": "chiiki", "活性化": "chiiki",
    "環境": "kankyo", "SDGs": "kankyo", "SDG": "kankyo", "防災": "kankyo", "ごみ": "kankyo", "食": "kankyo", "農": "kankyo",
    "福祉": "fukushi", "バリアフリー": "fukushi", "ボランティア": "fukushi", "人権": "fukushi", "障がい": "fukushi",
    "国際": "kokusai", "多文化": "kokusai", "交流": "kokusai", "外国": "kokusai",
    "職業": "shokugyo", "キャリア": "shokugyo", "仕事": "shokugyo", "将来": "shokugyo", "進路": "shokugyo",
    "平和": "heiwa", "戦争": "heiwa",
}
INFO_KW = [
    "情報活用", "ICT", "Chromebook", "タブレット", "iPad", "パソコン", "端末", "コンピュータ",
    "検索", "インターネット", "デジタル", "プログラミング", "AI", "生成AI",
    "著作権", "個人情報", "SNS", "動画", "スライド", "プレゼン", "プレゼンテーション",
    "データ", "アンケート", "グラフ", "撮影", "写真", "情報モラル", "メディア", "引用", "ファクトチェック",
    "情報リテラシー", "情報教育",
    "情報に関する学習", "情報に関する取り組み", "情報に関する",
    "情報の収集", "情報の集め方", "情報活用能力", "コンピュータ操作",
]
# 中学校区ごとの掲載順（データ上の学校名）
SCHOOL_DISTRICTS = [
    ("第一中学校区", ["第一中", "守口小", "八雲東小"]),
    ("庭窪中学校区", ["庭窪中", "庭窪小", "金田小", "佐太小"]),
    ("八雲中学校区", ["八雲中", "八雲小"]),
    ("梶中学校区", ["梶中", "梶小", "藤田小"]),
    ("大久保中学校区", ["大久保中", "よつば小"]),
    ("錦中学校区", ["錦中", "錦小"]),
    ("樟風中学校区", ["樟風中", "さくら小", "寺方南小"]),
    ("さつき学園", ["さつき学園"]),
]
SCHOOL_DISPLAY_NAMES = {"さつき": "さつき学園"}
PILLARS = {
    "小3": "問いのはじまり", "小4": "調べてまとめる", "小5": "データで考える", "小6": "提言する",
    "中1": "社会へ発信", "中2": "信頼できる調査", "中3": "問い直して統合",
}
DEPTH = {
    "小3": "Ⅰ", "小4": "Ⅱ", "小5": "Ⅱ", "小6": "Ⅲ",
    "中1": "Ⅱ", "中2": "Ⅲ", "中3": "Ⅲ",
}
SKILLS_6 = {
    "小3": ["撮影・記録", "デジタルメモ", "ファイル保存・整理", "発表（型通り）"],
    "小4": ["検索・情報収集", "引用・出典記載", "メディア選択", "インタビュー同意"],
    "小5": ["AND/OR検索", "表・グラフ整理", "出典・信頼性確認", "情報の偏り認識"],
    "小6": ["アンケート設計", "一次データ収集・集計", "グラフの誠実な提示", "AI批判的比較"],
    "中1": ["著作権・肖像権の実践判断", "SNS発信リスク管理", "クラウド協働"],
    "中2": ["個人情報保護の実践", "ファクトチェック", "データ匿名化", "AI出力の検証"],
    "中3": ["データバイアス認識", "AI責任ある利用", "メディアリテラシー実践", "情報活用自己評価"],
}
BLOCK_7 = {
    "小3": "端末の正しい使い方・ファイル保存・肖像権（初歩）",
    "小4": "著作権・引用の基礎・インタビュー同意・メディアの特性",
    "小5": "AND/OR検索・データの著作権と出典・グラフの読み方",
    "小6": "アンケート設計の倫理・グラフの見せ方・情報推薦AI",
    "中1": "著作権法の基礎・肖像権・SNS発信リスク",
    "中2": "個人情報保護法・ファクトチェック・AI生成情報の特性",
    "中3": "データバイアス・生成AIの責任ある利用・情報と権力",
}
MINI_8 = {
    "小3": "「見つけた『いいな』を写真1枚で紹介」（まちたんけん助走）",
    "小4": "「校区内1か所を調べ、Web情報1件を引用してレポートに」",
    "小5": "「家庭の電気使用量を記録・グラフ化しクラスで比較」",
    "小6": "「本探究テーマでクラス内アンケートを設計・実施・改善」",
    "中1": "「取材候補地1か所でSNS投稿文と著作権チェックリストを作成」",
    "中2": "「ニュース2本をファクトチェックし情報源選定基準を決定」",
    "中3": "「オープンデータ1つを選びバイアスを注記した図にまとめる」",
}
GRADE_ORDER = ["小3", "小4", "小5", "小6", "中1", "中2", "中3"]
ZEN = {"１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8", "９": "9"}


def school_name(fname):
    m = re.match(r"【(.+?)】", fname)
    raw = m.group(1) if m else fname
    return SCHOOL_DISPLAY_NAMES.get(raw, raw)


def detect_type(name):
    if "小中" in name or name in ("さつき", "さつき学園"):
        return "elem_jhs"
    if "小" in name:
        return "elem"
    if "中" in name:
        return "jhs"
    return "other"


def type_label(t):
    return {"elem": "小学校", "jhs": "中学校", "elem_jhs": "小中一貫"}.get(t, "その他")


def default_grades(stype):
    if stype == "elem":
        return ["小3", "小4", "小5", "小6"]
    if stype == "jhs":
        return ["中1", "中2", "中3"]
    if stype == "elem_jhs":
        return ["小3", "小4", "小5", "小6", "中1", "中2", "中3"]
    return []


def normalize_grade(g, stype):
    g = g.translate(str.maketrans(ZEN))
    g = g.replace("第", "").replace("学年", "年").strip()
    if re.match(r"^[1-6]年$", g):
        n = g[0]
        return ("小" if stype in ("elem", "elem_jhs") and int(n) <= 6 else "中") + n
    if re.match(r"^[1-9]年$", g):
        n = int(g[0])
        if stype == "elem_jhs":
            return f"小{n}" if n <= 6 else f"中{n - 6}"
    m = re.match(r"^(小|中)([1-6])$", g)
    if m:
        return m.group(1) + m.group(2)
    return None


def parse_grades(text, stype):
    found = set()
    for g in re.findall(r"小[1-6]|中[1-3]", text):
        found.add(g)
    for g in re.findall(r"第[１２３４５６1-6]学年", text):
        ng = normalize_grade(g, stype)
        if ng:
            found.add(ng)
    for g in re.findall(r"[１２３４５６1-6]年", text):
        ng = normalize_grade(g + "年", stype)
        if ng:
            found.add(ng)
    grades = [g for g in GRADE_ORDER if g in found]
    if not grades:
        grades = default_grades(stype)
    return grades


def parse_theme_cats(text):
    cats = []
    for kw, cat in THEME_KW.items():
        if kw in text and cat not in cats:
            cats.append(cat)
    return cats


def parse_info_keywords(text):
    found = []
    for kw in sorted(INFO_KW, key=len, reverse=True):
        if kw in text and kw not in found:
            found.append(kw)
    return found


def parse_grade_themes(text, grades, stype):
    """学年別の探求テーマ・学習課題を抽出"""
    result = {g: "" for g in grades}
    patterns = [
        r"(小[3-6]|中[1-3]|[３４５６3-6]年|第[３４５６3-6]学年).{0,6}[（(]?([^）)\n]{2,40}?)[）)]?",
        r"学年\s*[３４５６3-6]\s*年?\s*(.{2,30}?)(?:学習課題|テーマ|探求)",
    ]
    # 守口小形式: 学年 3年 4年 ... テーマ 地域 福祉
    m = re.search(r"学年\s*([3-6])\s*年\s*([3-6])\s*年\s*([3-6])\s*年\s*([3-6])\s*年\s*テーマ\s*(.+?)(?:探求|探\s*求)", text)
    if m:
        themes = re.split(r"\s+", m.group(5).strip())
        gs = [f"小{i}" for i in range(3, 7)]
        for g, th in zip(gs, themes):
            if g in result:
                result[g] = th[:40]
    # 藤田小形式: ３年（地域）…
    for m in re.finditer(r"[３４５６3-6]年[（(]([^）)]+)[）)]", text):
        raw = m.group(0)
        n = raw.translate(str.maketrans(ZEN))[0]
        g = f"小{n}" if stype != "jhs" else f"中{n}"
        if g in result:
            result[g] = m.group(1)[:40]
    # 庭窪小形式
    m = re.search(
        r"学年\s*３\s*年\s*４\s*年\s*５\s*年\s*６\s*年\s*テーマ\s*(.+?)\s*学習課題\s*(.+?)\s*学習対象",
        text,
    )
    if m:
        themes = re.split(r"\s{2,}|\s+", m.group(1).strip())
        tasks = re.split(r"\s{2,}|\s+", m.group(2).strip())
        for i, g in enumerate(["小3", "小4", "小5", "小6"]):
            if g in result:
                t = themes[i] if i < len(themes) else ""
                k = tasks[i] if i < len(tasks) else ""
                result[g] = (t + "／" + k).strip("／")[:50]
    # 錦小形式
    m = re.search(r"学年\s*３年\s*４年.*?探求課題\s*(.+?)\s*知識", text, re.DOTALL)
    if m:
        parts = re.findall(r"（[^）]+）|[^（）\s]{4,20}", m.group(1))
        gs = ["小3", "小4"]
        for i, p in enumerate(parts[:2]):
            if gs[i] in result:
                result[gs[i]] = p[:40]
    m2 = re.search(r"探求活動テーマ\s*(.+?)\s*知識", text, re.DOTALL)
    if m2:
        parts = re.findall(r"（[^）]+）|[^（）\s]{4,25}", m2.group(1))
        gs = ["小5", "小6"]
        for i, p in enumerate(parts[:2]):
            if gs[i] in result:
                result[gs[i]] = p[:40]
    # 佐太小・八雲小: 学習課題列
    tasks = re.findall(
        r"◎([^◎○\s]{4,20})|○([^○\s]{4,20})",
        text,
    )
    flat = [a or b for a, b in tasks if (a or b)]
    if flat and stype == "elem":
        gs = ["小3", "小4", "小5", "小6"]
        for i, t in enumerate(flat[:4]):
            if gs[i] in result and not result[gs[i]]:
                result[gs[i]] = t[:40]
    # さくら小: テーマ名から推定
    if "学ぼう私たちの町" in text:
        mapping = {"小3": "学ぼう私たちの町1・校区", "小4": "日本全国旅物語", "小5": "環境にやさしいまち物語", "小6": "人にやさしいまち物語"}
        for g, v in mapping.items():
            if g in result and not result[g]:
                result[g] = v
    return result


def alignment_status(info_kw, grade_themes, stype):
    if info_kw:
        return "明示"
    if any("情報" in t for t in grade_themes.values()):
        return "部分"
    return "要検討"


def extract_pdf(path):
    reader = PdfReader(path)
    return re.sub(r"\s+", " ", "".join((p.extract_text() or "") for p in reader.pages))


def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    texts = [el.text for el in root.iter(W_NS + "t") if el.text]
    return re.sub(r"\s+", " ", "".join(texts))


def extract_xls(path):
    import xlrd
    wb = xlrd.open_workbook(path)
    parts = []
    for ws in wb.sheets():
        for r in range(ws.nrows):
            cells = [
                str(ws.cell_value(r, c)).strip()
                for c in range(ws.ncols)
                if str(ws.cell_value(r, c)).strip()
            ]
            if cells:
                parts.append(" | ".join(cells))
    wb.release_resources()
    return re.sub(r"\s+", " ", " ".join(parts))


def extract_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    parts = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                parts.append(" | ".join(cells))
    wb.close()
    return re.sub(r"\s+", " ", " ".join(parts))


def extract_plan_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".xls":
        return extract_xls(path)
    if ext == ".xlsx":
        return extract_xlsx(path)
    return ""


def collect_plan_sources():
    """pdf/ を優先し、未掲載校は計画フォルダ直下の docx/xls 等も取り込む。"""
    sources = []
    seen = {}
    if os.path.isdir(PDF_DIR):
        for fname in sorted(os.listdir(PDF_DIR)):
            if not fname.lower().endswith(".pdf"):
                continue
            school = school_name(fname)
            if school in seen:
                continue
            seen[school] = fname
            sources.append((os.path.join(PDF_DIR, fname), fname))
    if os.path.isdir(PLAN_DIR):
        for fname in sorted(os.listdir(PLAN_DIR)):
            if fname in ("pdf",) or fname.startswith("."):
                continue
            path = os.path.join(PLAN_DIR, fname)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SUPPORTED_EXT:
                continue
            school = school_name(fname)
            if school in seen:
                continue
            seen[school] = fname
            sources.append((path, fname))
    return sources


def order_schools(schools):
    """中学校区の並びに従ってソートし、district フィールドを付与する。"""
    by_name = {s["school"]: s for s in schools}
    ordered = []
    listed = set()
    for district, names in SCHOOL_DISTRICTS:
        for name in names:
            if name not in by_name:
                continue
            s = dict(by_name[name])
            s["district"] = district
            ordered.append(s)
            listed.add(name)
    for s in schools:
        if s["school"] in listed:
            continue
        s2 = dict(s)
        s2["district"] = "その他"
        ordered.append(s2)
    return ordered


def build():
    schools = []
    for path, fname in collect_plan_sources():
        school = school_name(fname)
        text = extract_plan_text(path)
        stype = detect_type(school)
        grades = parse_grades(text, stype)
        theme_cats = parse_theme_cats(text)
        info_kw = parse_info_keywords(text)
        grade_themes = parse_grade_themes(text, grades, stype)
        status = alignment_status(info_kw, grade_themes, stype)

        rows = []
        for g in grades:
            rows.append({
                "grade": g,
                "pillar": PILLARS.get(g, ""),
                "depth": DEPTH.get(g, ""),
                "plan_theme": grade_themes.get(g, ""),
                "skills_6": SKILLS_6.get(g, []),
                "block_7": BLOCK_7.get(g, ""),
                "mini_8": MINI_8.get(g, ""),
            })

        schools.append({
            "school": school,
            "type": stype,
            "type_label": type_label(stype),
            "file": fname,
            "grades": grades,
            "theme_cats": theme_cats,
            "theme_labels": [THEME_CAT[c] for c in theme_cats],
            "info_keywords": info_kw,
            "alignment": status,
            "grade_rows": rows,
            "plan_summary": text[:500],
        })

    schools = order_schools(schools)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)

    html = render_html(schools)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {len(schools)} schools -> {OUT_HTML}")


def render_html(schools):
    data_json = json.dumps(schools, ensure_ascii=False)
    school_options = "".join(f'<option value="{s["school"]}">{s["school"]}</option>' for s in schools)

    rows_overview = ""
    current_district = None
    for s in schools:
        if s.get("district") != current_district:
            current_district = s.get("district")
            rows_overview += f"""
    <tr class="district-row" data-district="{current_district}">
      <td colspan="6">{current_district}</td>
    </tr>"""
        cats = "".join(f'<span class="cat-tag cat-{c}">{THEME_CAT[c]}</span>' for c in s["theme_cats"][:4])
        info = "".join(f'<span class="skill-tag">{k}</span>' for k in s["info_keywords"][:6])
        if not info:
            info = '<span class="muted">計画に明示なし</span>'
        align_cls = {"明示": "align-yes", "部分": "align-part", "要検討": "align-todo"}[s["alignment"]]
        align_txt = {"明示": "情報活用を計画に記載", "部分": "テーマに情報要素あり", "要検討": "フレーム⑥⑦⑧で設計"}[s["alignment"]]
        grades = "・".join(s["grades"])
        rows_overview += f"""
    <tr data-school="{s['school']}" data-district="{s.get('district', '')}">
      <td class="school-cell"><strong>{s['school']}</strong><span class="type-badge">{s['type_label']}</span></td>
      <td class="grades-cell">{grades}</td>
      <td class="cats-cell">{cats or '<span class="muted">—</span>'}</td>
      <td class="info-cell">{info}</td>
      <td class="align-cell"><span class="align-badge {align_cls}">{align_txt}</span></td>
      <td class="act-cell"><button type="button" class="detail-btn" data-school="{s['school']}">学年別</button></td>
    </tr>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>守口市　総合的な学習の時間　情報活用能力　各校一覧</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600&family=Noto+Sans+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --ink:#1a1916; --ink2:#4a4843; --ink3:#888580; --rule:#dedad4; --bg:#faf9f6; --bg2:#f2f0eb;
  --teal:#0f6e56; --teal-l:#e1f5ee; --teal-m:#1d9e75;
  --blue:#185fa5; --blue-l:#e6f1fb; --amber:#854f0b; --amber-l:#faeeda; --amber-m:#ba7517;
  --serif:'Noto Serif JP',serif; --sans:'Noto Sans JP',sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:var(--sans);background:var(--bg);color:var(--ink);font-size:14px;line-height:1.75}}
.top-bar{{position:sticky;top:0;z-index:100;background:#e8f4f0;border-bottom:1.5px solid #9dd0c0;padding:0 1.25rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}}
.top-bar-title{{font-family:var(--serif);font-size:12px;font-weight:600;color:#2a6b58;padding:12px 0;margin-right:.25rem}}
.top-bar a{{font-size:11px;color:#3a8a72;text-decoration:none;white-space:nowrap}}
.top-bar a:hover{{color:var(--teal)}}
.top-bar a.is-current{{font-weight:700;color:var(--teal);pointer-events:none}}
.cover{{background:linear-gradient(135deg,#d4eee6 0%,#c8e6f0 60%,#ddeaf8 100%);padding:2.5rem 2rem 2rem;border-bottom:1.5px solid #9dd0c0}}
.cover-label{{font-size:11px;letter-spacing:.12em;color:var(--teal);font-weight:600;margin-bottom:.5rem}}
.cover h1{{font-family:var(--serif);font-size:clamp(18px,2.5vw,26px);font-weight:600;color:#1a3a30;margin-bottom:.5rem}}
.cover-sub{{font-size:13px;color:#3a6858;margin-bottom:1rem}}
.container{{max-width:1200px;margin:0 auto;padding:0 1.25rem 3rem}}
h2.section{{font-family:var(--serif);font-size:16px;font-weight:600;padding:2rem 0 .6rem;border-bottom:.5px solid var(--rule);margin-bottom:.75rem}}
.lead{{font-size:13px;color:var(--ink2);line-height:1.8;margin-bottom:1rem;max-width:800px}}
.note{{border-radius:4px;padding:.6rem .9rem;font-size:12px;line-height:1.7;margin:.6rem 0}}
.note-teal{{background:var(--teal-l);color:var(--teal);border-left:3px solid var(--teal-m)}}
.note-amber{{background:var(--amber-l);color:var(--amber);border-left:3px solid var(--amber-m)}}
.filter-row{{display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;margin-bottom:.75rem;font-size:12px}}
.filter-row select,.filter-row input{{font-family:var(--sans);font-size:12px;padding:.35rem .5rem;border:1px solid var(--rule);border-radius:4px;background:#fff}}
.ichiran-table{{width:100%;border-collapse:collapse;font-size:11px;margin-bottom:1.5rem}}
.ichiran-table th,.ichiran-table td{{padding:7px 8px;border:.5px solid var(--rule);vertical-align:top;line-height:1.55}}
.ichiran-table thead th{{background:var(--bg2);font-weight:700;text-align:left;font-size:10px}}
.school-cell strong{{display:block;font-size:12px}}
.type-badge{{display:inline-block;font-size:9px;padding:1px 5px;border-radius:2px;background:var(--bg3,#e8e5de);color:var(--ink2);margin-top:2px}}
.cat-tag{{display:inline-block;font-size:9px;padding:1px 4px;border-radius:2px;margin:1px;background:var(--teal-l);color:var(--teal)}}
.skill-tag{{display:inline-block;font-size:9px;padding:1px 4px;border-radius:2px;margin:1px;background:var(--bg2);border:.5px solid var(--rule)}}
.muted{{color:var(--ink3);font-size:10px}}
.align-badge{{display:inline-block;font-size:9px;padding:2px 6px;border-radius:3px;font-weight:600}}
.align-yes{{background:#e1f5ee;color:#085041}}
.align-part{{background:var(--blue-l);color:var(--blue)}}
.align-todo{{background:var(--amber-l);color:var(--amber)}}
.district-row td{{background:var(--bg2);font-weight:700;font-size:11px;color:var(--teal);padding:8px 10px;border:.5px solid var(--rule)}}
.detail-btn{{font-size:10px;padding:3px 8px;border:1px solid var(--teal-m);background:#fff;color:var(--teal);border-radius:3px;cursor:pointer}}
.detail-btn:hover{{background:var(--teal-l)}}
.detail-panel{{display:none;margin:1rem 0;padding:1rem;background:#fff;border:1px solid var(--rule);border-radius:8px}}
.detail-panel.open{{display:block}}
.detail-panel h3{{font-size:14px;margin-bottom:.5rem;font-family:var(--serif)}}
.grade-table{{width:100%;border-collapse:collapse;font-size:10px}}
.grade-table th,.grade-table td{{padding:5px 6px;border:.5px solid var(--rule);vertical-align:top}}
.grade-table thead th{{background:var(--bg2);font-size:9px}}
.g-grade{{font-weight:700;white-space:nowrap;background:var(--bg2);text-align:center}}
.pillar{{font-weight:600;color:var(--teal);font-size:10px}}
.depth{{display:inline-block;font-size:9px;padding:1px 5px;border-radius:2px;background:var(--amber-l);color:var(--amber);font-weight:700}}
.layer-blk{{background:#f8fbff}} .layer-mini{{background:#f6fcfa}} .layer-hon{{background:#fffcf6}}
.legend{{display:flex;flex-wrap:wrap;gap:8px;font-size:10px;color:var(--ink2);margin-bottom:.75rem}}
.legend span{{padding:2px 6px;border-radius:3px}}
.stats{{display:flex;flex-wrap:wrap;gap:1rem;font-size:11px;color:var(--ink2);margin-bottom:1rem}}
.stats strong{{color:var(--teal)}}
.footer{{border-top:.5px solid var(--rule);padding:1.5rem 0;text-align:center}}
.footer p{{font-size:11px;color:var(--ink3)}}
@media print{{.top-bar,.filter-row,.detail-btn{{display:none}} .district-row{{display:table-row}}}}
</style>
</head>
<body>
<div class="top-bar">
  <span class="top-bar-title">守口市　総合的な学習の時間　情報活用能力　各校一覧</span>
  <a href="joho_katsuyo_stepup_sheet.html">ステップアップシート</a>
  <a href="joho_katsuyo_stepup_sheet.html#theme-skill">テーマ一覧</a>
  <a href="joho_katsuyo_stepup_sheet.html#required-skills">必須スキルイラスト</a>
  <a href="情報ブロックミニ探究ユニット/index.html">情報ブロック一覧</a>
  <a href="school_joho_ichiran.html" class="is-current" aria-current="page">各校一覧</a>
  <a href="sougou_gakunen_framework.html">設計フレームワーク</a>
</div>
<div class="cover">
  <div class="cover-label">守口市教育センター　2026年度</div>
  <h1>総合的な学習の時間<br>情報活用能力　各校計画一覧</h1>
  <p class="cover-sub">各校の全体計画を守口市フレームワーク（⑥情報活用スキル・⑦情報ブロック・⑧ミニ探究）に照合</p>
</div>
<div class="container">
  <h2 class="section">一覧の見方</h2>
  <p class="lead">
    各校の<strong>総合的な学習の時間の全体計画</strong>（PDF・Word・Excel 等）からテキストを抽出し、
    守口市教育センターの<strong>情報活用能力育成ステップアップシート</strong>の学年別柱（問いのはじまり→…→問い直して統合）と
    <strong>⑥⑦⑧三層</strong>を対応づけた一覧である。
    計画に情報活用の記載がない学校は、フレームワーク上の推奨スキルを「要検討」として示す。
  </p>
  <div class="legend">
    <span class="align-yes">明示＝計画に情報活用・ICT等の記載あり</span>
    <span class="align-part">部分＝テーマ・活動に情報要素</span>
    <span class="align-todo">要検討＝フレーム⑥⑦⑧で設計を補完</span>
  </div>
  <div class="stats" id="stats"></div>
  <div class="filter-row">
    <label>校種 <select id="filter-type"><option value="">すべて</option><option value="elem">小学校</option><option value="jhs">中学校</option><option value="elem_jhs">小中一貫</option></select></label>
    <label>整合 <select id="filter-align"><option value="">すべて</option><option value="明示">明示</option><option value="部分">部分</option><option value="要検討">要検討</option></select></label>
    <label>検索 <input type="search" id="filter-text" placeholder="学校名・テーマ"></label>
  </div>
  <div class="note note-teal">
    <strong>設計の流れ（守口市）：</strong>本探究の課題設定（④）→ 連動する情報活用スキル（⑥）→ 情報ブロック（⑦）→ ミニ探究ユニット（⑧・1〜2h）→ 本探究（約1か月）
  </div>
  <h2 class="section">各校サマリー（{len(schools)}校）</h2>
  <table class="ichiran-table" id="overview-table">
    <thead>
      <tr>
        <th style="width:12%">学校</th>
        <th style="width:14%">対象学年</th>
        <th style="width:22%">テーマ軸（守口市分類）</th>
        <th style="width:22%">計画上の情報活用</th>
        <th style="width:18%">フレーム整合</th>
        <th style="width:8%"></th>
      </tr>
    </thead>
    <tbody>{rows_overview}
    </tbody>
  </table>
  <div id="detail-container"></div>
  <div class="note note-amber">
    <strong>注意：</strong>学年別テーマはPDFの表構造により自動抽出の精度が異なる。詳細は各校の原本PDFと<a href="joho_katsuyo_stepup_sheet.html">ステップアップシート</a>を照合してください。
  </div>
</div>
<div class="footer"><p>守口市教育センター　総合的な学習の時間　情報活用能力　各校一覧　2026年度</p></div>
<script>
const SCHOOLS = {data_json};
const THEME_CAT = {json.dumps(THEME_CAT, ensure_ascii=False)};

function renderStats() {{
  const n = SCHOOLS.length;
  const explicit = SCHOOLS.filter(s => s.alignment === '明示').length;
  document.getElementById('stats').innerHTML =
    `<span><strong>${{n}}</strong>校を掲載</span>` +
    `<span>情報活用<strong>明示</strong> ${{explicit}}校</span>` +
    `<span>要検討 <strong>${{n - explicit}}</strong>校（フレームで補完）</span>`;
}}

function renderDetail(school) {{
  const s = SCHOOLS.find(x => x.school === school);
  if (!s) return;
  const rows = s.grade_rows.map(r => `
    <tr>
      <td class="g-grade">${{r.grade}}</td>
      <td><span class="pillar">${{r.pillar}}</span> <span class="depth">${{r.depth}}</span></td>
      <td>${{r.plan_theme || '<span class="muted">（計画から未抽出）</span>'}}</td>
      <td>${{r.skills_6.map(sk => `<span class="skill-tag">${{sk}}</span>`).join('')}}</td>
      <td class="layer-blk">${{r.block_7}}</td>
      <td class="layer-mini">${{r.mini_8}}</td>
    </tr>`).join('');
  const container = document.getElementById('detail-container');
  container.innerHTML = `
    <div class="detail-panel open" id="detail-panel">
      <h3>${{s.school}}　学年別　情報活用能力マップ</h3>
      <p class="lead" style="margin-bottom:.5rem">計画ファイル：${{s.file}}</p>
      <table class="grade-table">
        <thead><tr>
          <th>学年</th><th>柱・深度</th><th>計画上のテーマ・課題</th>
          <th>⑥情報活用スキル（フレーム）</th><th>⑦情報ブロック</th><th>⑧ミニ探究助走</th>
        </tr></thead>
        <tbody>${{rows}}</tbody>
      </table>
    </div>`;
  container.scrollIntoView({{behavior:'smooth',block:'nearest'}});
}}

function applyFilters() {{
  const type = document.getElementById('filter-type').value;
  const align = document.getElementById('filter-align').value;
  const text = document.getElementById('filter-text').value.toLowerCase();
  const visibleDistricts = {{}};
  document.querySelectorAll('#overview-table tbody tr[data-school]').forEach(tr => {{
    const school = tr.dataset.school;
    const s = SCHOOLS.find(x => x.school === school);
  if (!s) return;
    const matchType = !type || s.type === type;
    const matchAlign = !align || s.alignment === align;
    const hay = (s.school + s.theme_labels.join('') + s.info_keywords.join('') + (s.district || '')).toLowerCase();
    const matchText = !text || hay.includes(text);
    const show = matchType && matchAlign && matchText;
    tr.style.display = show ? '' : 'none';
    if (show && tr.dataset.district) visibleDistricts[tr.dataset.district] = true;
  }});
  document.querySelectorAll('#overview-table tbody tr.district-row').forEach(tr => {{
    tr.style.display = visibleDistricts[tr.dataset.district] ? '' : 'none';
  }});
}}

document.querySelectorAll('.detail-btn').forEach(btn => {{
  btn.addEventListener('click', () => renderDetail(btn.dataset.school));
}});
['filter-type','filter-align','filter-text'].forEach(id => {{
  document.getElementById(id).addEventListener('input', applyFilters);
  document.getElementById(id).addEventListener('change', applyFilters);
}});
renderStats();
</script>
</body>
</html>"""


if __name__ == "__main__":
    build()
