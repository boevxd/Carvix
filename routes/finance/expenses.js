/**
 * Carvix — реестр всех расходов автопарка.
 *
 *   GET    /api/finance/expenses        список с фильтрами и пагинацией
 *   POST   /api/finance/expenses        добавить прочий расход
 *   DELETE /api/finance/expenses/:id    удалить прочий расход
 *
 * Реестр объединяет три источника:
 *   1. remont.stoimost_rabot       (категория «remont»)
 *   2. remont.stoimost_zapchastey  (категория «zapchasti»)
 *   3. prochiy_raskhod             (топливо, страховка, налоги, мойка...)
 */

const express = require('express');
const pool = require('../../db');
const { authRequired } = require('../../middleware/auth');
const { requireFinanceRead, requireFinanceWrite } = require('../../middleware/rbac');

const router = express.Router();

const ALLOWED_KATEGORIY = [
  'remont', 'zapchasti', 'topliv', 'strakhovka', 'nalog', 'moyka', 'prochee',
];

// Унифицированная подзапрос-витрина (CTE)
const UNIFIED_CTE = `
  SELECT
    'remont_rabot' AS source,
    r.id::text     AS source_id,
    r.data_okonchaniya::date AS data,
    'remont'       AS kategoriya,
    r.stoimost_rabot AS summa,
    ts.id          AS ts_id,
    ts.gos_nomer,
    ts.podrazdelenie_id,
    pd.nazvanie    AS podrazdelenie_nazvanie,
    'Стоимость работ ремонта №' || r.id AS opisanie
  FROM remont r
  JOIN zayavka z                ON z.id = r.zayavka_id
  JOIN transportnoe_sredstvo ts ON ts.id = z.ts_id
  JOIN podrazdelenie pd         ON pd.id = ts.podrazdelenie_id
  WHERE r.data_okonchaniya IS NOT NULL AND r.stoimost_rabot > 0

  UNION ALL

  SELECT
    'remont_zapchasti' AS source,
    r.id::text         AS source_id,
    r.data_okonchaniya::date,
    'zapchasti',
    r.stoimost_zapchastey,
    ts.id, ts.gos_nomer,
    ts.podrazdelenie_id, pd.nazvanie,
    'Стоимость запчастей ремонта №' || r.id
  FROM remont r
  JOIN zayavka z                ON z.id = r.zayavka_id
  JOIN transportnoe_sredstvo ts ON ts.id = z.ts_id
  JOIN podrazdelenie pd         ON pd.id = ts.podrazdelenie_id
  WHERE r.data_okonchaniya IS NOT NULL AND r.stoimost_zapchastey > 0

  UNION ALL

  SELECT
    'prochiy' AS source,
    pr.id::text,
    pr.data,
    pr.kategoriya,
    pr.summa,
    pr.ts_id,
    ts.gos_nomer,
    COALESCE(pr.podrazdelenie_id, ts.podrazdelenie_id) AS podrazdelenie_id,
    pd.nazvanie,
    pr.opisanie
  FROM prochiy_raskhod pr
  LEFT JOIN transportnoe_sredstvo ts ON ts.id = pr.ts_id
  LEFT JOIN podrazdelenie pd ON pd.id = COALESCE(pr.podrazdelenie_id, ts.podrazdelenie_id)
`;

/* ----------------------------------------------------------------- */
/*  GET /api/finance/expenses                                        */
/* ----------------------------------------------------------------- */
router.get('/', authRequired, requireFinanceRead, async (req, res) => {
  try {
    const {
      from, to,
      podrazdelenie_id,
      kategoriya,
      ts_id,
      source,                       // remont_rabot | remont_zapchasti | prochiy | all
      limit = 50,
      offset = 0,
    } = req.query;

    const where = [];
    const params = [];

    if (from) { params.push(from); where.push(`x.data >= $${params.length}::date`); }
    if (to)   { params.push(to);   where.push(`x.data <= $${params.length}::date`); }
    if (podrazdelenie_id) { params.push(podrazdelenie_id); where.push(`x.podrazdelenie_id = $${params.length}`); }
    if (kategoriya)       { params.push(kategoriya);       where.push(`x.kategoriya = $${params.length}`); }
    if (ts_id)            { params.push(ts_id);            where.push(`x.ts_id = $${params.length}`); }
    if (source && source !== 'all') {
      params.push(source);
      where.push(`x.source = $${params.length}`);
    }

    const whereSQL = where.length ? 'WHERE ' + where.join(' AND ') : '';

    const lim = Math.min(parseInt(limit, 10) || 50, 500);
    const off = parseInt(offset, 10) || 0;

    const dataSQL = `
      SELECT * FROM (${UNIFIED_CTE}) x
      ${whereSQL}
      ORDER BY x.data DESC, x.summa DESC
      LIMIT ${lim} OFFSET ${off}
    `;
    const totalSQL = `
      SELECT COUNT(*)::int AS total, COALESCE(SUM(x.summa), 0)::numeric AS total_summa
      FROM (${UNIFIED_CTE}) x
      ${whereSQL}
    `;

    const [{ rows: items }, { rows: agg }] = await Promise.all([
      pool.pool.query(dataSQL, params),
      pool.pool.query(totalSQL, params),
    ]);

    res.json({
      items,
      total: agg[0].total,
      total_summa: Number(agg[0].total_summa),
      limit: lim,
      offset: off,
    });
  } catch (e) {
    console.error('[expenses] GET error:', e);
    res.status(500).json({ error: 'Ошибка получения расходов' });
  }
});

/* ----------------------------------------------------------------- */
/*  POST /api/finance/expenses                                       */
/*    создаёт запись в prochiy_raskhod                               */
/* ----------------------------------------------------------------- */
router.post('/', authRequired, requireFinanceWrite, async (req, res) => {
  try {
    const { ts_id, podrazdelenie_id, data, kategoriya, summa, opisanie } = req.body;

    if (!data) return res.status(400).json({ error: 'Поле data обязательно' });
    if (!ALLOWED_KATEGORIY.includes(kategoriya))
      return res.status(400).json({ error: 'Недопустимая категория' });
    if (summa === undefined || isNaN(Number(summa)) || Number(summa) <= 0)
      return res.status(400).json({ error: 'Сумма должна быть числом > 0' });
    if (!ts_id && !podrazdelenie_id)
      return res.status(400).json({ error: 'Укажите ts_id или podrazdelenie_id' });

    const [rows] = await pool.execute(
      `INSERT INTO prochiy_raskhod (ts_id, podrazdelenie_id, data, kategoriya, summa, opisanie)
       VALUES (?, ?, ?, ?, ?, ?)
       RETURNING *`,
      [ts_id || null, podrazdelenie_id || null, data, kategoriya, Number(summa), opisanie || null]
    );

    // лог
    await pool.execute(
      `INSERT INTO finansoviy_log (sotrudnik_id, tip_operatsii, obyekt_tablitsa, obyekt_id, summa, kommentariy)
       VALUES (?, 'DOBAVLEN_RASKHOD', 'prochiy_raskhod', ?, ?, ?)`,
      [req.user.id, rows[0].id, Number(summa),
       `Добавлен расход категории «${kategoriya}» (${rows[0].opisanie || 'без описания'})`]
    );

    res.status(201).json(rows[0]);
  } catch (e) {
    console.error('[expenses] POST error:', e);
    res.status(500).json({ error: 'Ошибка добавления расхода' });
  }
});

/* ----------------------------------------------------------------- */
/*  DELETE /api/finance/expenses/:id                                 */
/* ----------------------------------------------------------------- */
router.delete('/:id', authRequired, requireFinanceWrite, async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (!id) return res.status(400).json({ error: 'Неверный id' });

    const [existing] = await pool.execute(
      'SELECT id, summa, kategoriya FROM prochiy_raskhod WHERE id = ?',
      [id]
    );
    if (!existing.length) return res.status(404).json({ error: 'Не найдено' });

    await pool.execute('DELETE FROM prochiy_raskhod WHERE id = ?', [id]);

    await pool.execute(
      `INSERT INTO finansoviy_log (sotrudnik_id, tip_operatsii, obyekt_tablitsa, obyekt_id, summa, kommentariy)
       VALUES (?, 'UDALEN_RASKHOD', 'prochiy_raskhod', ?, ?, ?)`,
      [req.user.id, id, Number(existing[0].summa),
       `Удалён расход категории «${existing[0].kategoriya}»`]
    );

    res.json({ ok: true, deleted_id: id });
  } catch (e) {
    console.error('[expenses] DELETE error:', e);
    res.status(500).json({ error: 'Ошибка удаления' });
  }
});

module.exports = router;
