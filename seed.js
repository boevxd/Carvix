/**
 * Carvix — стартовый бутстрап БД.
 *
 * 1. Применяет schema.sql (CREATE TABLE IF NOT EXISTS …) — таблицы
 *    создаются автоматически при первом запуске на чистой БД (Render).
 * 2. Гарантирует наличие 6 базовых ролей и 4 подразделений.
 *
 * Демо-данные (12 сотрудников, машины, заявки …) — отдельно через
 * `npm run seed:demo`.
 */

const fs = require('fs');
const path = require('path');
const pool = require('./db');

const ROLES = [
  'Аналитик',
  'Диспетчер',
  'Механик',
  'Главный механик',
  'Директор',
  'Пользователь',
];

const DEFAULT_PODRAZDELENIYA = [
  'Главное управление',
  'Автопарк №1',
  'Автопарк №2',
  'Ремонтный цех',
];

async function applySchema() {
  const ddl = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
  await pool.raw(ddl);
}

async function ensureRows(table, items) {
  for (const name of items) {
    const [rows] = await pool.execute(
      `SELECT id FROM ${table} WHERE nazvanie = ? LIMIT 1`,
      [name]
    );
    if (rows.length === 0) {
      await pool.execute(`INSERT INTO ${table} (nazvanie) VALUES (?)`, [name]);
      const label = table === 'rol' ? 'роль' : 'подразделение';
      console.log(`[seed] Добавлено ${label}: ${name}`);
    }
  }
}

async function seed() {
  await applySchema();
  await ensureRows('rol', ROLES);
  await ensureRows('podrazdelenie', DEFAULT_PODRAZDELENIYA);
}

module.exports = seed;
