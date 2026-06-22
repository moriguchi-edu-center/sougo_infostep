(function () {
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderIllustCard(item, compact) {
    if (!item) return '';
    const title = item.title && item.title !== '(空欄)' ? item.title : '（タイトル未設定）';
    const href = infoBlockLink(item.row);
    const img = illustPath(item);
    const cls = compact ? 'req-illust-card is-compact' : 'req-illust-card';
    if (img) {
      return '<a class="' + cls + '" href="' + href + '" target="_blank" rel="noopener" title="' + escapeHtml(title) + '">' +
        '<img src="' + escapeHtml(img) + '" alt="" loading="lazy">' +
        '<span class="req-illust-label">' + escapeHtml(title) + '</span></a>';
    }
    return '<a class="' + cls + ' no-img" href="' + href + '" target="_blank" rel="noopener">' +
      '<span class="req-illust-ph">画像なし</span>' +
      '<span class="req-illust-label">' + escapeHtml(title) + '</span></a>';
  }

  function renderSkillGroup(skill) {
    const cards = skill.rows.map(function (row) {
      return renderIllustCard(resolveInfoBlockItem(row), true);
    }).join('');
    return '<div class="req-skill-group">' +
      '<div class="req-skill-tag">' + escapeHtml(skill.label) + '</div>' +
      '<div class="req-illust-row">' + cards + '</div></div>';
  }

  function renderGradePanel(gradeKey) {
    const skills = GRADE_REQUIRED_SKILLS[gradeKey] || [];
    const label = GRADE_LABELS[gradeKey] || gradeKey;
    return '<div class="req-grade-panel" data-grade="' + gradeKey + '">' +
      '<h4 class="req-grade-title">' + escapeHtml(label) + '</h4>' +
      skills.map(renderSkillGroup).join('') +
      '</div>';
  }

  function renderGradeIllustStrip(gradeKey, limit) {
    const seen = new Set();
    const items = [];
    (GRADE_REQUIRED_SKILLS[gradeKey] || []).forEach(function (skill) {
      skill.rows.forEach(function (row) {
        if (seen.has(row)) return;
        const item = resolveInfoBlockItem(row);
        if (item) {
          seen.add(row);
          items.push(item);
        }
      });
    });
    const slice = typeof limit === 'number' ? items.slice(0, limit) : items;
    return slice.map(function (item) {
      return renderIllustCard(item, true);
    }).join('');
  }

  function renderBlockIllustForGrade(gradeKey) {
    const html = renderGradeIllustStrip(gradeKey);
    if (!html) return '';
    return '<p class="modal-block-illust-caption">連動イラスト（<a href="' + INFO_BLOCK_BASE + 'index.html" target="_blank" rel="noopener">情報ブロック一覧</a>）</p>' +
      '<div class="req-illust-row">' + html + '</div>';
  }

  function initRequiredSkillsSection() {
    const mount = document.getElementById('required-skills-illust');
    if (!mount) return;

    const grades = ['g3', 'g4', 'g5', 'g6', 'j1', 'j2', 'j3'];
    mount.innerHTML =
      '<div class="req-grade-grid">' +
      grades.map(renderGradePanel).join('') +
      '</div>';

    const mapBody = document.querySelector('#skill-map-with-illust tbody');
    if (mapBody) {
      const keys = Object.keys(SKILL_AREA_ILLUST);
      mapBody.querySelectorAll('tr').forEach(function (tr, i) {
        const key = keys[i];
        if (!key) return;
        const area = SKILL_AREA_ILLUST[key];
        const nameCell = tr.querySelector('.skill-name');
        if (!nameCell || !area) return;
        const strip = document.createElement('div');
        strip.className = 'skill-area-illust';
        strip.innerHTML = area.rows.map(function (row) {
          return renderIllustCard(resolveInfoBlockItem(row), true);
        }).join('');
        nameCell.appendChild(strip);
      });
    }
  }

  window.renderBlockIllustForGrade = renderBlockIllustForGrade;
  window.gradeKeyFromLabel = function (grade) {
    if (!grade) return null;
    if (grade.startsWith('小')) return 'g' + grade.slice(1);
    if (grade.startsWith('中')) return 'j' + grade.slice(1);
    return null;
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRequiredSkillsSection);
  } else {
    initRequiredSkillsSection();
  }
})();
