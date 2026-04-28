require('dotenv').config();
const path = require('path');
const express = require('express');
const cors = require('cors');

const seed = require('./seed');
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/images', express.static(path.join(__dirname, 'images')));

app.use('/api/auth', authRoutes);

app.get('/health', (_, res) => res.json({ ok: true }));

(async () => {
  try {
    await seed();
    app.listen(PORT, () => {
      console.log(`\n  Carvix запущен:  http://localhost:${PORT}\n`);
    });
  } catch (e) {
    console.error('Не удалось инициализировать приложение:', e);
    process.exit(1);
  }
})();
