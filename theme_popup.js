(function () {
  const THEMES = ['chiiki', 'kankyo', 'fukushi', 'kokusai', 'shokugyo', 'heiwa', 'joho'];
  const GRADES = ['g3', 'g4', 'g5', 'g6', 'j1', 'j2', 'j3'];
  const CYC_CLASS = { 1: 'cyc-1', 2: 'cyc-2', 3: 'cyc-3', 4: 'cyc-4', 0: '' };

  const modal = document.getElementById('theme-modal');
  if (!modal) return;

  const backdrop = modal.querySelector('.theme-modal-backdrop');
  const closeBtn = modal.querySelector('.theme-modal-close');
  const titleEl = document.getElementById('modal-title');
  const metaEl = document.getElementById('modal-meta');
  const flowBridgeEl = document.getElementById('modal-flow-bridge');
  const trans1El = document.getElementById('modal-trans-1');
  const trans2El = document.getElementById('modal-trans-2');
  const heroThemeEl = document.getElementById('modal-hero-theme');
  const heroQuestionEl = document.getElementById('modal-hero-question');
  const heroSummaryEl = document.getElementById('modal-hero-summary');
  const cycleNoteEl = document.getElementById('modal-cycle-note');
  const cycleEl = document.getElementById('modal-cycle');
  const blockEl = document.getElementById('modal-block');
  const blockUseEl = document.getElementById('modal-block-use');
  const miniEl = document.getElementById('modal-mini');

  function bindCells() {
    document.querySelectorAll('.theme-table tbody tr').forEach((row, ri) => {
      row.querySelectorAll('.skill-cell').forEach((cell, ci) => {
        const key = THEMES[ri] + '-' + GRADES[ci];
        cell.dataset.key = key;
        cell.classList.add('clickable');
        cell.setAttribute('role', 'button');
        cell.setAttribute('tabindex', '0');
        cell.setAttribute('aria-label', '詳細を表示');
        cell.addEventListener('click', () => openModal(key));
        cell.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openModal(key);
          }
        });
      });
    });
  }

  function gradeToKey(grade) {
    if (grade.startsWith('小')) return 'g' + grade.slice(1);
    if (grade.startsWith('中')) return 'j' + grade.slice(1);
    return null;
  }

  function mergeDetail(key) {
    const base = THEME_DETAIL_DATA[key] || {};
    const hon = (typeof HON_INQUIRY_DATA !== 'undefined' && HON_INQUIRY_DATA[key]) || {};
    return Object.assign({}, base, hon);
  }

  const PHASE_LABELS = {
    1: '課題の設定', 2: '情報の収集', 3: '整理・分析', 4: 'まとめ・表現・振り返り'
  };
  const MINI_SHORT = { 1: '課題', 2: '収集', 3: '整理', 4: '表現' };

  function deferPhasesForGrade(gradeKey) {
    const set = new Set();
    const notes = (typeof DEFER_PHASE_NOTE !== 'undefined' && DEFER_PHASE_NOTE[gradeKey]) || {};
    Object.keys(notes).forEach((p) => set.add(Number(p)));
    return { set, notes };
  }

  function mergedSkills(key) {
    const d = THEME_DETAIL_DATA[key];
    if (!d) return {};
    const deepen = (typeof SKILL_DEEPEN !== 'undefined' && SKILL_DEEPEN[key]) || {};
    return Object.assign({}, deepen, d.skills || {});
  }

  function deepenTag(gradeKey, phase) {
    const notes = (typeof DEFER_PHASE_NOTE !== 'undefined' && DEFER_PHASE_NOTE[gradeKey]) || {};
    return notes[phase] ? `<span class="cyc-deepen-tag">（${notes[phase]}）</span>` : '';
  }

  function renderSkillLines(key) {
    const d = THEME_DETAIL_DATA[key];
    if (!d) return '';
    const gradeKey = key.split('-')[1];
    const skills = mergedSkills(key);
    const { set: deferSet } = deferPhasesForGrade(gradeKey);
    return [1, 2, 3, 4].map((p) => {
      const cls = CYC_CLASS[p];
      const mini = MINI_SHORT[p];
      const text = skills[p];
      const tag = deferSet.has(p) ? deepenTag(gradeKey, p) : '';
      if (text) {
        return `<div class="theme-skill-line"><span class="cyc-mini ${cls}">${mini}</span>${text}${tag}</div>`;
      }
      return `<div class="theme-skill-line"><span class="cyc-mini ${cls}">${mini}</span>—${tag}</div>`;
    }).join('');
  }

  function normalizeSkillCells() {
    document.querySelectorAll('.theme-table tbody tr').forEach((row, ri) => {
      row.querySelectorAll('.skill-cell').forEach((cell, ci) => {
        const key = THEMES[ri] + '-' + GRADES[ci];
        cell.querySelectorAll('.theme-skill-line').forEach((el) => el.remove());
        const depth = cell.querySelector('.theme-depth');
        const html = renderSkillLines(key);
        if (depth) depth.insertAdjacentHTML('afterend', html);
        else cell.insertAdjacentHTML('beforeend', html);
      });
    });
  }

  function renderCycleNote(d) {
    const focus = GRADE_CYCLE_FOCUS[gradeToKey(d.grade)];
    if (!focus) return '';
    let html = focus.note;
    if (focus.defer && focus.defer.length) {
      html += ` <strong>${focus.defer.join('・')}</strong>はその学年の重点外だが、学習活動の中で深化・準備として扱う（「未実施」ではない）。`;
    }
    return html;
  }

  function renderCycle(d, key) {
    const hon = d.honCycle || {};
    const gradeKey = gradeToKey(d.grade);
    const gradeBase = GRADE_CYCLE[gradeKey] || [];
    const baseByPhase = {};
    gradeBase.forEach((item) => { if (item.p) baseByPhase[item.p] = item.base; });
    const { set: deferSet } = deferPhasesForGrade(gradeKey);
    const skills = key ? mergedSkills(key) : {};

    return [1, 2, 3, 4].map((phase) => {
      const cls = CYC_CLASS[phase];
      const badge = `<span class="cyc-badge ${cls}">${PHASE_LABELS[phase]}</span>`;
      const isDefer = deferSet.has(phase);
      const honEx = hon[phase];
      const base = baseByPhase[phase];
      const skillEx = skills[phase];
      const tag = isDefer ? deepenTag(gradeKey, phase) : '';
      const parts = [];

      if (honEx) parts.push(`<span class="modal-hon-ex">${honEx}</span>${tag}`);
      else if (skillEx) parts.push(`<span class="modal-hon-ex">${skillEx}</span>${tag}`);
      else if (tag) parts.push(`<span class="modal-hon-ex">—${tag}</span>`);

      if (base) parts.push(`<span class="modal-grade-skill">到達水準：${base}</span>`);

      if (!parts.length) {
        return `<div class="modal-cyc-row ${cls}">${badge}<span class="modal-defer-text">—</span></div>`;
      }
      return `<div class="modal-cyc-row ${cls}">${badge}${parts.join('')}</div>`;
    }).join('');
  }

  function renderMini(d) {
    const steps = d.miniSteps.map((s) => `<li>${s}</li>`).join('');
    return `
      <p class="modal-mini-title">${d.miniTitle}</p>
      <ol class="modal-mini-steps">${steps}</ol>
      <p class="modal-mini-note">${d.miniNote}</p>
    `;
  }

  function miniLabel(d) {
    if (!d.miniTitle) return 'ミニ探究';
    return d.miniTitle.replace(/^「/, '').replace(/」$/, '');
  }

  function renderFlowBridge(d) {
    const mini = miniLabel(d);
    const hon = d.honTheme || '本探究';
    return `同テーマ・同素材で段階的に深める：<strong>①</strong>情報提供（ミニ内）→ <strong>②</strong>「${mini}」を<strong>合算1〜2時間</strong>で体験 → <strong>③</strong>「${hon}」へ約1か月で本格展開`;
  }

  function renderTrans1(d) {
    return `①の情報提供が、②ミニ探究「${miniLabel(d)}」の探究実践のなかで<strong>必然として使われる</strong>場面をつくる（⑦⑧は合算1〜2時間）`;
  }

  function renderTrans2(d) {
    const hon = d.honTheme || '本探究';
    return `②の助走体験をもとに、③本探究「${hon}」で<strong>同じ問いを本格的な課題へ移行</strong>する`;
  }

  function openModal(key) {
    const d = mergeDetail(key);
    if (!d.theme) return;
    titleEl.textContent = `${d.theme}　${d.grade}`;
    metaEl.innerHTML = `表の学習例：<strong>${d.example}</strong>　探究深度：<span class="depth-badge d${d.depth === 'Ⅰ' ? '1' : d.depth === 'Ⅱ' ? '2' : '3'}">${d.depth}</span>`;
    flowBridgeEl.innerHTML = renderFlowBridge(d);
    trans1El.innerHTML = renderTrans1(d);
    trans2El.innerHTML = renderTrans2(d);
    heroThemeEl.textContent = d.honTheme || '—';
    heroQuestionEl.textContent = d.honQuestion || (d.honCycle && d.honCycle[1]) || '—';
    heroSummaryEl.textContent = d.honSummary || '';
    cycleNoteEl.innerHTML = renderCycleNote(d);
    cycleEl.innerHTML = renderCycle(d, key);
    blockEl.textContent = d.block;
    blockUseEl.textContent = d.blockUse;
    miniEl.innerHTML = renderMini(d);
    modal.hidden = false;
    document.body.classList.add('modal-open');
    closeBtn.focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove('modal-open');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) closeModal();
  });

  normalizeSkillCells();
  bindCells();
})();
