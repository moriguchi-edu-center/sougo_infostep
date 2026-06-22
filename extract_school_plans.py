# -*- coding: utf-8 -*-
"""各校の総合的な学習の時間計画からテキストを抽出するスクリプト"""
import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET

BASE = os.path.join(os.path.dirname(__file__), "各学校総合的な学習の時間計画")
OUT = os.path.join(os.path.dirname(__file__), "school_plans_extracted.json")

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def school_name(fname):
    m = re.match(r"【(.+?)】", fname)
    return m.group(1) if m else re.sub(r"_sanitized\..*$", "", fname)


def clean_text(t):
    t = re.sub(r"\s+", " ", t)
    t = t.replace("\xa0", " ")
    return t.strip()


def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    texts = [el.text for el in root.iter(W_NS + "t") if el.text]
    return clean_text("".join(texts))


def extract_xlsx(path):
    try:
        import openpyxl
    except ImportError:
        return None
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    parts = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                parts.append(" | ".join(cells))
    wb.close()
    return clean_text("\n".join(parts))


def extract_xls(path):
    try:
        import xlrd
    except ImportError:
        return None
    wb = xlrd.open_workbook(path)
    parts = []
    for ws in wb.sheets():
        for r in range(ws.nrows):
            cells = [str(ws.cell_value(r, c)).strip() for c in range(ws.ncols) if str(ws.cell_value(r, c)).strip()]
            if cells:
                parts.append(" | ".join(cells))
    return clean_text("\n".join(parts))


def extract_pdf(path):
    try:
        import fitz  # pymupdf
    except ImportError:
        try:
            import PyPDF2
        except ImportError:
            return None
        text = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return clean_text("\n".join(text))
    doc = fitz.open(path)
    text = [page.get_text() for page in doc]
    doc.close()
    return clean_text("\n".join(text))


def extract_rtf(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    # simple RTF strip
    raw = re.sub(r"\\'[0-9a-fA-F]{2}", lambda m: bytes.fromhex(m.group(0)[2:]).decode("cp932", errors="ignore"), raw)
    raw = re.sub(r"\\[a-z]+\d* ?|[{}]|\\\\", "", raw)
    return clean_text(raw)


def extract_doc(path):
    # try antiword / textract fallback: read as binary and grep unicode
    try:
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command", f"(New-Object -ComObject Word.Application) | Out-Null"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass
    with open(path, "rb") as f:
        data = f.read()
    # UTF-16 LE chunks in .doc
    chunks = re.findall(rb"(?:[\x20-\x7e\u3000-\u9fff]{4,})", data, re.UNICODE) if False else []
    texts = []
    for enc in ("utf-16-le", "cp932"):
        try:
            decoded = data.decode(enc, errors="ignore")
            jp = re.findall(r"[\u3040-\u30ff\u4e00-\u9fff\u3000-\u303f]{3,}", decoded)
            if len(jp) > 5:
                texts.extend(jp)
        except Exception:
            pass
    return clean_text(" ".join(texts[:500])) if texts else None


def extract_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".xlsx":
        return extract_xlsx(path)
    if ext == ".xls":
        return extract_xls(path)
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".rtf":
        return extract_rtf(path)
    if ext == ".doc":
        return extract_doc(path)
    return None


def parse_plan(text, school):
    """計画テキストから学年・テーマ・情報関連を粗く抽出"""
    if not text:
        return {"school": school, "grades": [], "themes": [], "info_keywords": [], "raw_preview": ""}

    grade_patterns = [
        (r"小[1-6]", "小"),
        (r"中[1-3]", "中"),
        (r"[1-6]年", "年"),
    ]
    grades = sorted(set(re.findall(r"小[1-6]|中[1-3]|[1-6]年生", text)))

    theme_keywords = [
        "地域", "まち", "環境", "SDGs", "国際", "福祉", "職業", "平和", "人権",
        "防災", "食", "農", "健康", "文化", "伝統", "多文化", "情報", "デジタル",
        "AI", "プログラミング", "探究", "まちづくり", "活性化",
    ]
    themes = [k for k in theme_keywords if k in text]

    info_keywords = [
        "情報活用", "ICT", "Chromebook", "タブレット", "iPad", "パソコン", "端末",
        "検索", "インターネット", "デジタル", "プログラミング", "AI", "生成AI",
        "著作権", "個人情報", "SNS", "動画", "スライド", "プレゼン", "データ",
        "アンケート", "グラフ", "撮影", "写真", "動画制作", "コーディング",
        "情報モラル", "メディア", "ファクトチェック", "引用",
    ]
    info_found = [k for k in info_keywords if k in text]

    # 学年別テーマらしき行
    grade_themes = []
    for m in re.finditer(r"(小[1-6]|中[1-3]|[1-6]年生).{0,80}?(地域|環境|福祉|国際|職業|平和|防災|食|農|文化|まち|SDGs|探究|情報)", text):
        grade_themes.append(m.group(0)[:100])

    return {
        "school": school,
        "grades": grades[:20],
        "themes": themes,
        "info_keywords": info_found,
        "grade_themes": grade_themes[:30],
        "raw_preview": text[:3000],
        "text_length": len(text),
    }


def main():
    results = []
    if not os.path.isdir(BASE):
        print("dir not found", BASE)
        return

    for fname in sorted(os.listdir(BASE)):
        if fname == "pdf" or fname.startswith("."):
            continue
        path = os.path.join(BASE, fname)
        if not os.path.isfile(path):
            continue
        school = school_name(fname)
        ext = os.path.splitext(fname)[1].lower()
        try:
            text = extract_file(path)
            parsed = parse_plan(text, school)
            parsed["file"] = fname
            parsed["ext"] = ext
            parsed["extract_ok"] = text is not None and len(text or "") > 50
            results.append(parsed)
        except Exception as e:
            results.append({"school": school, "file": fname, "error": str(e), "extract_ok": False})

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(results)} schools to {OUT}")


if __name__ == "__main__":
    main()
