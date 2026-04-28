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

/**
 * Если SEED_DEMO=true и в БД нет ни одного сотрудника — автоматически
 * прогоняем полный seed_data.sql. Это позволяет на бесплатном плане Render
 * (без Shell) развернуть систему «из коробки» с готовыми тестовыми учётками.
 *
 * После первого успешного автозалива в БД появятся 12 сотрудников и при
 * следующем рестарте этот блок ничего не сделает (sotrudnik > 0).
 */
async function autoSeedDemoIfEmpty() {
  if (String(process.env.SEED_DEMO).toLowerCase() !== 'true') {
    return;
  }

  // Проверяем количество сотрудников. Если таблица только что создана — 0 строк.
  const [rows] = await pool.execute('SELECT COUNT(*)::int AS n FROM sotrudnik');
  const count = rows[0]?.n ?? 0;

  if (count > 0) {
    console.log(`[seed] SEED_DEMO=true, но в БД уже есть ${count} сотрудников — пропускаю автозалив.`);
    return;
  }

  const sqlFile = path.join(__dirname, 'seed_data.sql');
  if (!fs.existsSync(sqlFile)) {
    console.warn('[seed] SEED_DEMO=true, но seed_data.sql не найден.');
    return;
  }

  console.log('[seed] БД пустая + SEED_DEMO=true → запускаю seed_data.sql …');
  const sql = fs.readFileSync(sqlFile, 'utf8');
  await pool.raw(sql);
  console.log('[seed] Демо-данные успешно загружены. Тестовые логины: ivanov / petrov / volkova (пароль: password)');
}

async function seed() {
  await applySchema();
  await ensureRows('rol', ROLES);
  await ensureRows('podrazdelenie', DEFAULT_PODRAZDELENIYA);
  await autoSeedDemoIfEmpty();
}

module.exports = seed;
