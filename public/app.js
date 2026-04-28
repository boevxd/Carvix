/* ============================================================
   Carvix — главное SPA-приложение (финансовый модуль).
   Хэш-роутинг: #dashboard | #expenses | #budgets | #tco | #receipts | #audit
   ============================================================ */

const TOKEN = localStorage.getItem('carvix_token');
if (!TOKEN) location.replace('/');

let CURRENT_USER = null;
let CURRENT_CHARTS = [];      // активные Chart.js инстансы (для destroy при смене)
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/* ----------------- Утилиты ----------------- */
function fmtMoney(v) {
  const n = Number(v) || 0;
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(n) + ' ₽';
}
function fmtDate(s) {
  if (!s) return '—';
  const d = new Date(s);
  if (isNaN(d)) return s;
  return d.toLocaleDateString('ru-RU');
}
function fmtDateTime(s) {
  if (!s) return '—';
  const d = new Date(s);
  if (isNaN(d)) return s;
  return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}
function escape(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])
  );
}
function toast(msg, type = '') {
  const t = $('#toast');
  t.className = 'show ' + type;
  t.textContent = msg;
  setTimeout(() => t.classList.remove('show'), 2400);
}

/* ----------------- API ----------------- */
async function api(path, options = {}) {
  const opts = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${TOKEN}`,
      ...(options.headers || {}),
    },
  };
  const res = await fetch(path, opts);
  if (res.status === 401) {
    localStorage.removeItem('carvix_token');
    location.replace('/');
    throw new Error('unauthorized');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data;
}

/* ----------------- Auth ----------------- */
async function loadUser() {
  CURRENT_USER = await api('/api/auth/me');
  $('#userName').textContent = CURRENT_USER.fio;
  $('#userRole').textContent = CURRENT_USER.rol_nazvanie;
  $('#userAvatar').textContent = CURRENT_USER.fio[0] || '?';

  // скрыть вкладки если нет прав
  const role = CURRENT_USER.rol_nazvanie;
  const FINANCE_READ = ['Директор', 'Аналитик', 'Главный механик'];
  if (!FINANCE_READ.includes(role)) {
    ['expenses','budgets','tco','receipts','audit'].forEach(s => {
      const link = document.querySelector(`.nav__item[data-section="${s}"]`);
      if (link) link.style.display = 'none';
    });
  }
  if (!['Директор', 'Аналитик'].includes(role)) {
    const audit = document.querySelector(`.nav__item[data-section="audit"]`);
    if (audit) audit.style.display = 'none';
  }
}

$('#logoutBtn').addEventListener('click', () => {
  localStorage.removeItem('carvix_token');
  location.replace('/');
});

/* ----------------- Router ----------------- */
const ROUTES = {
  dashboard: renderDashboard,
  expenses:  renderExpenses,
  budgets:   renderBudgets,
  tco:       renderTco,
  receipts:  renderReceipts,
  audit:     renderAudit,
};

function navigate() {
  const hash = location.hash.replace('#', '') || 'dashboard';
  const handler = ROUTES[hash] || renderDashboard;

  // подсветка nav
  $$('.nav__item').forEach(a =>
    a.classList.toggle('active', a.dataset.section === hash)
  );

  // destroy старые графики
  CURRENT_CHARTS.forEach(c => c.destroy?.());
  CURRENT_CHARTS = [];

  const root = $('#content');
  root.innerHTML = `<div class="loading-screen"><div class="spinner"></div><div>Загрузка раздела…</div></div>`;

  Promise.resolve(handler(root))
    .catch(e => {
      console.error(e);
      root.innerHTML = `<div class="empty">⚠ ${escape(e.message || 'Ошибка загрузки')}</div>`;
      if (e.status === 403) toast('Недостаточно прав для этого раздела', 'error');
    });
}

window.addEventListener('hashchange', navigate);

/* =========================================================
   1. ДАШБОРД
   ========================================================= */
async function renderDashboard(root) {
  const year = new Date().getFullYear();
  const data = await api(`/api/finance/reports/dashboard?god=${year}`);

  const monthNames = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];
  const kpi = data.kpi;
  const deltaArrow =
    kpi.delta_pct == null ? '' :
    kpi.delta_pct > 0 ? `<span class="kpi-card__hint up">▲ +${kpi.delta_pct}% к предыдущему</span>` :
                        `<span class="kpi-card__hint down">▼ ${kpi.delta_pct}% к предыдущему</span>`;

  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Дашборд</h2>
        <div class="section__subtitle">Финансовый обзор за ${year} год</div>
      </div>
    </div>

    <div class="cards-grid">
      <div class="kpi-card">
        <div class="kpi-card__label">Расходы за месяц</div>
        <div class="kpi-card__value">${fmtMoney(kpi.tek_mesyats)}</div>
        ${deltaArrow}
      </div>
      <div class="kpi-card">
        <div class="kpi-card__label">План на год</div>
        <div class="kpi-card__value">${fmtMoney(kpi.plan_god)}</div>
        <div class="kpi-card__hint">факт: ${fmtMoney(kpi.fakt_god)}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-card__label">Отклонение от плана</div>
        <div class="kpi-card__value" style="color: ${kpi.otklonenie_god < 0 ? 'var(--c-bad)' : 'var(--c-good)'}">
          ${kpi.otklonenie_god < 0 ? '−' : '+'}${fmtMoney(Math.abs(kpi.otklonenie_god))}
        </div>
        <div class="kpi-card__hint">${kpi.otklonenie_god < 0 ? 'перерасход' : 'остаток'}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-card__label">Кол-во машин в топ-5</div>
        <div class="kpi-card__value">${data.top_ts.length}</div>
        <div class="kpi-card__hint">по стоимости владения</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Динамика расходов помесячно</h3>
        <canvas id="dynChart"></canvas>
      </div>
      <div class="chart-card">
        <h3>Структура затрат</h3>
        <canvas id="pieChart"></canvas>
      </div>
    </div>

    <div class="table-card">
      <h3>Топ-5 машин по стоимости владения (TCO)</h3>
      <table class="tbl">
        <thead><tr>
          <th>Гос. №</th><th>Марка / модель</th><th>Подразделение</th>
          <th class="num">Ремонтов</th><th class="num">TCO</th>
        </tr></thead>
        <tbody>
          ${data.top_ts.map(t => `
            <tr>
              <td><strong>${escape(t.gos_nomer)}</strong></td>
              <td>${escape(t.marka)} ${escape(t.model)}</td>
              <td>${escape(t.podrazdelenie)}</td>
              <td class="num">${t.kolvo_remontov}</td>
              <td class="num"><strong>${fmtMoney(t.tco)}</strong></td>
            </tr>
          `).join('') || `<tr><td colspan="5" class="empty">Нет данных</td></tr>`}
        </tbody>
      </table>
    </div>
  `;

  // Линейный график
  CURRENT_CHARTS.push(new Chart($('#dynChart'), {
    type: 'line',
    data: {
      labels: data.dynamics.map(d => monthNames[d.mesyats - 1]),
      datasets: [
        { label: 'Ремонт',    data: data.dynamics.map(d => +d.remont),    borderColor: '#b89460', backgroundColor: 'rgba(184,148,96,.15)', fill: true, tension: .35 },
        { label: 'Запчасти',  data: data.dynamics.map(d => +d.zapchasti), borderColor: '#2f5a9c', backgroundColor: 'rgba(47,90,156,.10)',  fill: true, tension: .35 },
        { label: 'Топливо',   data: data.dynamics.map(d => +d.topliv),    borderColor: '#2f8f5e', backgroundColor: 'rgba(47,143,94,.10)',  fill: true, tension: .35 },
        { label: 'Прочее',    data: data.dynamics.map(d => +d.prochee),   borderColor: '#b94a48', backgroundColor: 'rgba(185,74,72,.10)',  fill: true, tension: .35 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } },
      scales: { y: { ticks: { callback: v => Intl.NumberFormat('ru-RU', { notation: 'compact' }).format(v) } } },
    },
  }));

  // Pie
  CURRENT_CHARTS.push(new Chart($('#pieChart'), {
    type: 'doughnut',
    data: {
      labels: data.struktura.map(s => s.kategoriya),
      datasets: [{
        data: data.struktura.map(s => +s.summa),
        backgroundColor: ['#b89460','#2f5a9c','#2f8f5e','#b94a48','#c69317','#776e63','#9b6b9b'],
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } },
    },
  }));
}

/* =========================================================
   2. РЕЕСТР РАСХОДОВ
   ========================================================= */
async function renderExpenses(root) {
  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Расходы</h2>
        <div class="section__subtitle">Объединённая лента всех затрат</div>
      </div>
      <button class="btn dark" id="addExpenseBtn">+ Добавить расход</button>
    </div>

    <div class="filters">
      <label>С даты <input type="date" id="fFrom" /></label>
      <label>По дату <input type="date" id="fTo" /></label>
      <label>Категория
        <select id="fKat">
          <option value="">Все</option>
          <option value="remont">Ремонт</option>
          <option value="zapchasti">Запчасти</option>
          <option value="topliv">Топливо</option>
          <option value="strakhovka">Страховка</option>
          <option value="nalog">Налог</option>
          <option value="moyka">Мойка</option>
          <option value="prochee">Прочее</option>
        </select>
      </label>
      <label>Источник
        <select id="fSrc">
          <option value="all">Все</option>
          <option value="prochiy">Прочие</option>
          <option value="remont_rabot">Работы</option>
          <option value="remont_zapchasti">Запчасти ремонтов</option>
        </select>
      </label>
      <div class="spacer"></div>
      <button class="btn" id="applyBtn">Применить</button>
      <button class="btn" id="resetBtn">Сбросить</button>
    </div>

    <div class="table-card">
      <div id="expensesTbl"><div class="loading-screen"><div class="spinner"></div></div></div>
    </div>
  `;

  async function load() {
    const params = new URLSearchParams();
    if ($('#fFrom').value) params.set('from', $('#fFrom').value);
    if ($('#fTo').value)   params.set('to', $('#fTo').value);
    if ($('#fKat').value)  params.set('kategoriya', $('#fKat').value);
    if ($('#fSrc').value)  params.set('source', $('#fSrc').value);
    params.set('limit', '200');

    const data = await api('/api/finance/expenses?' + params);
    const html = `
      <table class="tbl">
        <thead><tr>
          <th>Дата</th><th>Категория</th><th>Гос. №</th>
          <th>Подразделение</th><th>Описание</th><th class="num">Сумма</th><th></th>
        </tr></thead>
        <tbody>
          ${data.items.map(it => `
            <tr>
              <td>${fmtDate(it.data)}</td>
              <td><span class="chip ${chipColor(it.kategoriya)}">${escape(it.kategoriya)}</span></td>
              <td>${escape(it.gos_nomer || '—')}</td>
              <td>${escape(it.podrazdelenie_nazvanie || '—')}</td>
              <td>${escape(it.opisanie || '—')}</td>
              <td class="num"><strong>${fmtMoney(it.summa)}</strong></td>
              <td>
                ${it.source === 'prochiy'
                   ? `<button class="btn danger" data-del="${it.source_id}">×</button>`
                   : ''}
              </td>
            </tr>
          `).join('') || `<tr><td colspan="7" class="empty">Расходы не найдены</td></tr>`}
        </tbody>
      </table>
      <div class="tbl-foot">
        <span>Всего записей: ${data.total}</span>
        <span>Сумма: <strong>${fmtMoney(data.total_summa)}</strong></span>
      </div>
    `;
    $('#expensesTbl').innerHTML = html;

    $$('button[data-del]', $('#expensesTbl')).forEach(b => {
      b.onclick = async () => {
        if (!confirm('Удалить этот расход?')) return;
        try {
          await api('/api/finance/expenses/' + b.dataset.del, { method: 'DELETE' });
          toast('Удалено', 'success');
          load();
        } catch (e) { toast(e.message, 'error'); }
      };
    });
  }

  $('#applyBtn').onclick = load;
  $('#resetBtn').onclick = () => {
    $$('.filters input, .filters select').forEach(el => { el.value = ''; });
    $('#fSrc').value = 'all';
    load();
  };
  $('#addExpenseBtn').onclick = () => openExpenseModal(load);
  load();
}

function chipColor(k) {
  if (k === 'remont') return 'amber';
  if (k === 'zapchasti') return 'blue';
  if (k === 'topliv') return 'green';
  if (k === 'strakhovka' || k === 'nalog') return 'red';
  return '';
}

async function openExpenseModal(onSaved) {
  // Подгружаем подразделения и ТС для select
  const [pd, ts] = await Promise.all([
    api('/api/auth/podrazdeleniya'),
    fetch('/api/auth/me', { headers: { Authorization: `Bearer ${TOKEN}` } })
      .then(() => Promise.resolve([])), // ts эндпоинта пока нет — сделаем без него
  ]);

  const bg = document.createElement('div');
  bg.className = 'modal-bg';
  bg.innerHTML = `
    <div class="modal">
      <h3>Добавить расход</h3>
      <div class="form-grid">
        <label class="full">Категория
          <select id="mKat">
            <option value="topliv">Топливо</option>
            <option value="strakhovka">Страховка</option>
            <option value="nalog">Налог</option>
            <option value="moyka">Мойка</option>
            <option value="prochee">Прочее</option>
          </select>
        </label>
        <label>Дата
          <input type="date" id="mData" value="${new Date().toISOString().slice(0,10)}" />
        </label>
        <label>Сумма, ₽
          <input type="number" id="mSum" min="1" step="100" />
        </label>
        <label class="full">Подразделение
          <select id="mPd">
            <option value="">— не указано —</option>
            ${pd.map(p => `<option value="${p.id}">${escape(p.nazvanie)}</option>`).join('')}
          </select>
        </label>
        <label class="full">Описание
          <textarea id="mDesc" rows="2"></textarea>
        </label>
      </div>
      <div class="modal-actions">
        <button class="btn" id="mCancel">Отмена</button>
        <button class="btn dark" id="mSave">Сохранить</button>
      </div>
    </div>
  `;
  document.body.appendChild(bg);
  bg.addEventListener('click', e => { if (e.target === bg) bg.remove(); });
  $('#mCancel', bg).onclick = () => bg.remove();
  $('#mSave', bg).onclick = async () => {
    const body = {
      kategoriya:       $('#mKat', bg).value,
      data:             $('#mData', bg).value,
      summa:            +$('#mSum', bg).value,
      podrazdelenie_id: $('#mPd', bg).value ? +$('#mPd', bg).value : null,
      opisanie:         $('#mDesc', bg).value || null,
    };
    if (!body.summa || !body.data) return toast('Заполните дату и сумму', 'error');
    try {
      await api('/api/finance/expenses', { method: 'POST', body: JSON.stringify(body) });
      toast('Расход добавлен', 'success');
      bg.remove();
      onSaved && onSaved();
    } catch (e) { toast(e.message, 'error'); }
  };
}

/* =========================================================
   3. БЮДЖЕТЫ (план/факт)
   ========================================================= */
async function renderBudgets(root) {
  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Бюджеты — план / факт</h2>
        <div class="section__subtitle">Сравнение плановых и фактических расходов</div>
      </div>
    </div>

    <div class="filters">
      <label>Год <input type="number" id="bGod" value="${new Date().getFullYear()}" min="2020" max="2100" /></label>
      <label>Месяц
        <select id="bMes">
          <option value="">Все</option>
          ${[...Array(12).keys()].map(i => `<option value="${i+1}">${i+1}</option>`).join('')}
        </select>
      </label>
      <label>Категория
        <select id="bKat">
          <option value="">Все</option>
          <option value="remont">Ремонт</option>
          <option value="zapchasti">Запчасти</option>
          <option value="topliv">Топливо</option>
          <option value="prochee">Прочее</option>
        </select>
      </label>
      <div class="spacer"></div>
      <button class="btn" id="bApply">Применить</button>
    </div>

    <div class="cards-grid" id="bTotals"></div>

    <div class="table-card">
      <div id="bTbl"></div>
    </div>
  `;

  async function load() {
    const params = new URLSearchParams();
    if ($('#bGod').value) params.set('god', $('#bGod').value);
    if ($('#bMes').value) params.set('mesyats', $('#bMes').value);
    if ($('#bKat').value) params.set('kategoriya', $('#bKat').value);

    const data = await api('/api/finance/budgets/plan-fakt?' + params);

    $('#bTotals').innerHTML = `
      <div class="kpi-card"><div class="kpi-card__label">План</div>
        <div class="kpi-card__value">${fmtMoney(data.totals.plan)}</div></div>
      <div class="kpi-card"><div class="kpi-card__label">Факт</div>
        <div class="kpi-card__value">${fmtMoney(data.totals.fakt)}</div></div>
      <div class="kpi-card"><div class="kpi-card__label">Отклонение</div>
        <div class="kpi-card__value" style="color: ${data.totals.otklonenie < 0 ? 'var(--c-bad)' : 'var(--c-good)'}">
          ${data.totals.otklonenie < 0 ? '−' : '+'}${fmtMoney(Math.abs(data.totals.otklonenie))}
        </div></div>
      <div class="kpi-card"><div class="kpi-card__label">% исполнения</div>
        <div class="kpi-card__value">${data.totals.protsent}%</div></div>
    `;

    $('#bTbl').innerHTML = `
      <table class="tbl">
        <thead><tr>
          <th>Подразделение</th><th>Период</th><th>Категория</th>
          <th class="num">План</th><th class="num">Факт</th>
          <th class="num">Отклонение</th><th class="num">% исп.</th>
        </tr></thead>
        <tbody>
          ${data.items.map(it => `
            <tr>
              <td>${escape(it.podrazdelenie_nazvanie)}</td>
              <td>${it.mesyats}/${it.god}</td>
              <td><span class="chip ${chipColor(it.kategoriya)}">${escape(it.kategoriya)}</span></td>
              <td class="num">${fmtMoney(it.plan_summa)}</td>
              <td class="num">${fmtMoney(it.fakt_summa)}</td>
              <td class="num" style="color: ${+it.otklonenie < 0 ? 'var(--c-bad)' : 'var(--c-good)'}">
                ${+it.otklonenie < 0 ? '−' : ''}${fmtMoney(Math.abs(it.otklonenie))}
              </td>
              <td class="num">
                <span class="chip ${+it.protsent_ispolneniya > 100 ? 'red' : 'green'}">
                  ${it.protsent_ispolneniya}%
                </span>
              </td>
            </tr>
          `).join('') || `<tr><td colspan="7" class="empty">Бюджеты не найдены</td></tr>`}
        </tbody>
      </table>
    `;
  }

  $('#bApply').onclick = load;
  load();
}

/* =========================================================
   4. TCO ПО МАШИНАМ
   ========================================================= */
async function renderTco(root) {
  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Парк — TCO</h2>
        <div class="section__subtitle">Стоимость владения по каждому транспортному средству</div>
      </div>
    </div>

    <div class="filters">
      <label>Сортировка
        <select id="tSort">
          <option value="tco_desc">TCO по убыванию</option>
          <option value="tco_asc">TCO по возрастанию</option>
          <option value="remontov">Кол-во ремонтов</option>
          <option value="gos_nomer">Гос. номер</option>
        </select>
      </label>
      <div class="spacer"></div>
      <button class="btn" id="tApply">Применить</button>
    </div>

    <div id="tDetail"></div>
    <div class="table-card">
      <div id="tList"><div class="loading-screen"><div class="spinner"></div></div></div>
    </div>
  `;

  async function load() {
    const data = await api('/api/finance/reports/tco?sort=' + $('#tSort').value);

    $('#tList').innerHTML = `
      <table class="tbl">
        <thead><tr>
          <th>Гос. №</th><th>Марка / модель</th><th>Подразделение</th>
          <th class="num">Ремонтов</th>
          <th class="num">Работы</th><th class="num">Запчасти</th>
          <th class="num">Прочее</th><th class="num">TCO итого</th>
        </tr></thead>
        <tbody>
          ${data.items.map(t => `
            <tr style="cursor:pointer" data-ts="${t.ts_id}">
              <td><strong>${escape(t.gos_nomer)}</strong></td>
              <td>${escape(t.marka_nazvanie || '')} ${escape(t.model_nazvanie || '')}</td>
              <td>${escape(t.podrazdelenie_nazvanie || '—')}</td>
              <td class="num">${t.kolvo_remontov}</td>
              <td class="num">${fmtMoney(t.itogo_rabot)}</td>
              <td class="num">${fmtMoney(t.itogo_zapchastey)}</td>
              <td class="num">${fmtMoney(t.itogo_prochee)}</td>
              <td class="num"><strong>${fmtMoney(t.tco_obshchee)}</strong></td>
            </tr>
          `).join('') || `<tr><td colspan="8" class="empty">Нет данных</td></tr>`}
        </tbody>
      </table>
      <div class="tbl-foot">
        <span>Машин: ${data.items.length}</span>
        <span>Итого TCO: <strong>${fmtMoney(data.totals.tco)}</strong></span>
      </div>
    `;
    $$('tr[data-ts]').forEach(tr => {
      tr.onclick = () => loadTcoDetail(tr.dataset.ts);
    });
  }

  async function loadTcoDetail(tsId) {
    const d = await api('/api/finance/reports/tco/' + tsId);
    $('#tDetail').innerHTML = `
      <div class="table-card" style="margin-bottom: 14px;">
        <h3>📋 ${escape(d.summary.gos_nomer)} — ${escape(d.summary.marka_nazvanie)} ${escape(d.summary.model_nazvanie)}</h3>
        <div class="dtl-grid">
          <div>
            <div class="kpi-card__label">Подразделение</div>
            <div>${escape(d.summary.podrazdelenie_nazvanie || '—')}</div>
          </div>
          <div>
            <div class="kpi-card__label">Заявок / ремонтов</div>
            <div>${d.summary.kolvo_zayavok} / ${d.summary.kolvo_remontov}</div>
          </div>
          <div>
            <div class="kpi-card__label">TCO итого</div>
            <div><strong>${fmtMoney(d.summary.tco_obshchee)}</strong></div>
          </div>
          <div>
            <div class="kpi-card__label">В т.ч. работы / запчасти / прочее</div>
            <div>${fmtMoney(d.summary.itogo_rabot)} / ${fmtMoney(d.summary.itogo_zapchastey)} / ${fmtMoney(d.summary.itogo_prochee)}</div>
          </div>
        </div>
        <h3 style="margin-top:16px">История ремонтов</h3>
        <table class="tbl">
          <thead><tr><th>Тип</th><th>Начало</th><th>Окончание</th><th>Механик</th><th class="num">Итого</th></tr></thead>
          <tbody>
            ${d.remonty.map(r => `
              <tr>
                <td>${escape(r.tip_remonta)} <span class="chip">${escape(r.kategoriya)}</span></td>
                <td>${fmtDate(r.data_nachala)}</td>
                <td>${fmtDate(r.data_okonchaniya)}</td>
                <td>${escape(r.mekhanik || '—')}</td>
                <td class="num"><strong>${fmtMoney(r.itogo)}</strong></td>
              </tr>
            `).join('') || `<tr><td colspan="5" class="empty">Ремонтов нет</td></tr>`}
          </tbody>
        </table>
      </div>
    `;
    $('#tDetail').scrollIntoView({ behavior: 'smooth' });
  }

  $('#tApply').onclick = load;
  load();
}

/* =========================================================
   5. ПРИХОДЫ ЗАПЧАСТЕЙ
   ========================================================= */
async function renderReceipts(root) {
  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Приходные накладные</h2>
        <div class="section__subtitle">Закупки запчастей у поставщиков</div>
      </div>
    </div>

    <div class="table-card">
      <div id="rList"><div class="loading-screen"><div class="spinner"></div></div></div>
    </div>
    <div id="rDetail"></div>
  `;

  const data = await api('/api/finance/parts/receipts');
  $('#rList').innerHTML = `
    <table class="tbl">
      <thead><tr>
        <th>Дата</th><th>№ накладной</th><th>Поставщик</th>
        <th>Создал</th>
        <th class="num">Позиций</th><th class="num">Единиц</th>
        <th class="num">Сумма</th>
      </tr></thead>
      <tbody>
        ${data.map(r => `
          <tr style="cursor:pointer" data-id="${r.id}">
            <td>${fmtDate(r.data_prikhoda)}</td>
            <td><strong>${escape(r.nomer_nakl || '—')}</strong></td>
            <td>${escape(r.postavshik_nazvanie)}</td>
            <td>${escape(r.sozdatel_fio || '—')}</td>
            <td class="num">${r.kolvo_pozitsiy}</td>
            <td class="num">${r.itogo_edinic}</td>
            <td class="num"><strong>${fmtMoney(r.summa_obshaya)}</strong></td>
          </tr>
        `).join('') || `<tr><td colspan="7" class="empty">Накладных нет</td></tr>`}
      </tbody>
    </table>
  `;

  $$('tr[data-id]').forEach(tr => {
    tr.onclick = async () => {
      const d = await api('/api/finance/parts/receipts/' + tr.dataset.id);
      $('#rDetail').innerHTML = `
        <div class="table-card" style="margin-top: 14px;">
          <h3>Накладная № ${escape(d.nomer_nakl || d.id)}</h3>
          <div class="dtl-grid">
            <div><div class="kpi-card__label">Поставщик</div><div>${escape(d.postavshik_nazvanie)}</div></div>
            <div><div class="kpi-card__label">Дата</div><div>${fmtDate(d.data_prikhoda)}</div></div>
            <div><div class="kpi-card__label">Создал</div><div>${escape(d.sozdatel_fio || '—')}</div></div>
            <div><div class="kpi-card__label">Сумма</div><div><strong>${fmtMoney(d.summa_obshaya)}</strong></div></div>
          </div>
          ${d.kommentariy ? `<div style="color:var(--c-muted);font-style:italic;margin-bottom:10px">${escape(d.kommentariy)}</div>` : ''}
          <table class="tbl">
            <thead><tr>
              <th>Запчасть</th><th>Артикул</th>
              <th class="num">Кол-во</th><th class="num">Цена</th><th class="num">Итого</th>
            </tr></thead>
            <tbody>
              ${d.pozitsii.map(p => `
                <tr>
                  <td>${escape(p.naimenovanie)}</td>
                  <td>${escape(p.artikul || '—')}</td>
                  <td class="num">${p.kolichestvo}</td>
                  <td class="num">${fmtMoney(p.tsena_za_edinicu)}</td>
                  <td class="num"><strong>${fmtMoney(p.itogo_pozitsii)}</strong></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
      $('#rDetail').scrollIntoView({ behavior: 'smooth' });
    };
  });
}

/* =========================================================
   6. АУДИТ-ЛОГ
   ========================================================= */
async function renderAudit(root) {
  root.innerHTML = `
    <div class="section__head">
      <div>
        <h2 class="section__title">Журнал операций</h2>
        <div class="section__subtitle">Все финансовые действия пользователей</div>
      </div>
    </div>
    <div class="table-card">
      <div id="aTbl"><div class="loading-screen"><div class="spinner"></div></div></div>
    </div>
  `;

  const data = await api('/api/finance/audit-log?limit=200');
  $('#aTbl').innerHTML = `
    <table class="tbl">
      <thead><tr>
        <th>Дата / время</th><th>Сотрудник</th><th>Роль</th>
        <th>Операция</th><th>Объект</th>
        <th class="num">Сумма</th><th>Комментарий</th>
      </tr></thead>
      <tbody>
        ${data.items.map(it => `
          <tr>
            <td>${fmtDateTime(it.data_operatsii)}</td>
            <td><strong>${escape(it.sotrudnik_fio || '—')}</strong></td>
            <td>${escape(it.sotrudnik_rol || '—')}</td>
            <td><span class="chip blue">${escape(it.tip_operatsii)}</span></td>
            <td>${escape(it.obyekt_tablitsa || '')}${it.obyekt_id ? ' #' + it.obyekt_id : ''}</td>
            <td class="num">${it.summa ? fmtMoney(it.summa) : '—'}</td>
            <td>${escape(it.kommentariy || '')}</td>
          </tr>
        `).join('') || `<tr><td colspan="7" class="empty">Журнал пуст</td></tr>`}
      </tbody>
    </table>
    <div class="tbl-foot">
      <span>Записей: ${data.total}</span>
    </div>
  `;
}

/* ----------------- Bootstrap ----------------- */
loadUser()
  .then(navigate)
  .catch(e => {
    console.error(e);
    $('#content').innerHTML = `<div class="empty">Ошибка авторизации: ${escape(e.message)}</div>`;
  });
