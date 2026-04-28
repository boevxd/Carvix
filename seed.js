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

async function seed() {
  const conn = await pool.getConnection();
  try {
    for (const name of ROLES) {
      const [rows] = await conn.execute(
        'SELECT id FROM rol WHERE nazvanie = ? LIMIT 1',
        [name]
      );
      if (rows.length === 0) {
        await conn.execute('INSERT INTO rol (nazvanie) VALUES (?)', [name]);
        console.log(`[seed] Добавлена роль: ${name}`);
      }
    }

    for (const name of DEFAULT_PODRAZDELENIYA) {
      const [rows] = await conn.execute(
        'SELECT id FROM podrazdelenie WHERE nazvanie = ? LIMIT 1',
        [name]
      );
      if (rows.length === 0) {
        await conn.execute(
          'INSERT INTO podrazdelenie (nazvanie) VALUES (?)',
          [name]
        );
        console.log(`[seed] Добавлено подразделение: ${name}`);
      }
    }
  } finally {
    conn.release();
  }
}

module.exports = seed;
