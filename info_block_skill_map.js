/** 統合ステップアップ表⑥・スキル蓄積マップ ↔ 情報ブロックミニ探究ユニット（data.js の row） */
const INFO_BLOCK_BASE = '情報ブロックミニ探究ユニット/';

const GRADE_REQUIRED_SKILLS = {
  g3: [
    { label: '撮影・記録', rows: [89, 30] },
    { label: 'デジタルメモ', rows: [125, 18] },
    { label: 'ファイル保存・整理', rows: [98, 96] },
    { label: '発表（型通り）', rows: [66, 73] }
  ],
  g4: [
    { label: '検索・情報収集', rows: [19, 113, 13] },
    { label: '引用・出典記載', rows: [28, 137, 139] },
    { label: 'メディア選択', rows: [64, 172] },
    { label: 'インタビュー同意', rows: [17, 130, 143] }
  ],
  g5: [
    { label: 'AND/OR検索', rows: [10, 185] },
    { label: '表・グラフ整理', rows: [59, 169] },
    { label: '出典・信頼性確認', rows: [28, 137] },
    { label: '情報の偏り認識', rows: [29, 177, 148] }
  ],
  g6: [
    { label: 'アンケート設計', rows: [20, 182] },
    { label: '一次データ収集・集計', rows: [21, 60] },
    { label: 'グラフの誠実な提示', rows: [147, 169] },
    { label: 'AI批判的比較', rows: [160, 175] }
  ],
  j1: [
    { label: '著作権・肖像権', rows: [131, 130, 139] },
    { label: 'SNS発信リスク', rows: [140, 159, 144] },
    { label: 'クラウド協働', rows: [118, 136] },
    { label: 'メディア選択（深化）', rows: [64, 172] }
  ],
  j2: [
    { label: '個人情報保護', rows: [128, 129] },
    { label: 'ファクトチェック', rows: [181, 158] },
    { label: 'AI出力の検証', rows: [160, 175] },
    { label: '倫理的調査', rows: [17, 143] }
  ],
  j3: [
    { label: 'データバイアス', rows: [176, 147] },
    { label: 'AI責任ある利用', rows: [175, 174, 165] },
    { label: 'メディアリテラシー', rows: [145, 177, 178] },
    { label: '情報活用自己評価', rows: [79, 76] }
  ]
};

const SKILL_AREA_ILLUST = {
  record: { name: '記録・整理（撮影・ファイル・メモ）', rows: [89, 98, 125, 30, 18] },
  search: { name: '検索・情報収集', rows: [19, 113, 10, 13, 24] },
  cite: { name: '引用・出典・著作権', rows: [28, 137, 139, 131] },
  media: { name: 'メディア選択・発信設計', rows: [64, 172, 72, 71] },
  graph: { name: '表・グラフ・データ読解', rows: [59, 169, 147, 168] },
  survey: { name: '一次データ収集（アンケート・取材）', rows: [20, 21, 17, 182] },
  factcheck: { name: '信頼性・批判的検討', rows: [181, 29, 158, 160] },
  ethics: { name: '個人情報・倫理的判断', rows: [128, 130, 143, 129] },
  ai: { name: 'AI批判的活用・出力検証', rows: [175, 160, 165, 176] },
  selfeval: { name: '情報活用自己評価', rows: [79, 76] }
};

const GRADE_LABELS = {
  g3: '小3', g4: '小4', g5: '小5', g6: '小6',
  j1: '中1', j2: '中2', j3: '中3'
};

function resolveInfoBlockItem(row) {
  const data = (typeof INFO_BLOCK_DATA !== 'undefined' && INFO_BLOCK_DATA) || [];
  return data.find(function (d) { return d.row === row; }) || null;
}

function illustPath(item) {
  if (!item || !item.image) return '';
  return INFO_BLOCK_BASE + item.image;
}

function infoBlockLink(row) {
  return INFO_BLOCK_BASE + 'index.html?row=' + row;
}
