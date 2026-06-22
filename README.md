# 守口市「総合的な学習の時間」情報活用フレームワーク

守口市内各校の「総合的な学習の時間」全体計画をもとに、**情報活用能力（⑥⑦⑧）**の段階的な育成を可視化した資料一式です。

## 主なファイル

| ファイル | 内容 |
|----------|------|
| [joho_katsuyo_stepup_sheet.html](joho_katsuyo_stepup_sheet.html) | 統合ステップアップ表・テーマ表・必須スキルイラスト・スキル蓄積マップ（メイン） |
| [sougou_gakunen_framework.html](sougou_gakunen_framework.html) | 設計フレームワーク（学年別の柱・探究サイクル） |
| [school_joho_ichiran.html](school_joho_ichiran.html) | 市内20校の情報活用・探究マップ一覧 |
| [情報ブロックミニ探究ユニット/index.html](情報ブロックミニ探究ユニット/index.html) | 情報ブロック188件の一覧・印刷・詳細表示 |
| `info_block_skill_map.js` / `required_skills_illust.js` | 必須スキルと情報ブロックイラストの連動 |
| `theme_popup.js` / `theme_popup_data.js` / `hon_inquiry_data.js` | テーマ表モーダル用データ |
| `build_school_ichiran.py` | 一覧表の再生成スクリプト |
| `extract_school_plans.py` | PDF計画書の抽出スクリプト |
| `情報ブロックミニ探究ユニット/build_data.py` | Excel → `data.json` 生成 |

## 使い方

1. `joho_katsuyo_stepup_sheet.html` をブラウザで開く
2. テーマ表のセルをクリックすると、ミニ探究・本探究の詳細が表示される
3. 「必須スキルイラスト」から情報ブロックのイラストへジャンプできる
4. 各校の実態は `school_joho_ichiran.html` と照合

### 一覧表の再生成

```bash
pip install pypdf xlrd openpyxl
python extract_school_plans.py   # PDF → JSON（初回または計画更新時）
python build_school_ichiran.py   # school_joho_ichiran.html を再生成（pdf/ ＋ 計画フォルダ直下の docx/xls も取り込み）
```

### 情報ブロックデータの再生成

```bash
cd 情報ブロックミニ探究ユニット
pip install openpyxl
python build_data.py             # 情報ブロック説明.xlsx → data.json / data.js
python build_data.py --report    # タイトルとイラストのずれを確認
```

## データソース

`各学校総合的な学習の時間計画/` に各校の全体計画（sanitized 版）を格納しています。  
抽出結果は `school_plans_pdf.json` / `school_ichiran_data.json` に保存されています。

## Git での履歴管理

```bash
# 変更確認
git status
git diff

# コミット（例）
git add .
git commit -m "変更内容の要約"

# 初回のみ：GitHub で空リポジトリを作成し、リモートを登録
git remote add origin https://github.com/<ユーザー名>/<リポジトリ名>.git
git push -u origin main
```

ブランチは `main` を使用しています。大きな変更の前にブランチを切る場合:

```bash
git checkout -b feature/作業名
# 作業後
git checkout main
git merge feature/作業名
```

## GitHub Pages（任意）

リポジトリの **Settings → Pages** で **Branch: main / root** を選ぶと、HTML をそのまま公開できます。  
エントリーポイント: `joho_katsuyo_stepup_sheet.html`

## 注意

- 各校の計画書は教育委員会・学校の公開資料に基づく sanitized 版です
- 公開リポジトリにする場合は、関係者の確認を推奨します
