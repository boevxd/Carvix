<div align="center">
  <img src="images/logo.png" alt="Carvix" width="240" />
  <h1>Carvix</h1>
  <p><b>Веб-система управления автопарком, ТО и ремонтами.</b></p>
  <p>
    <img alt="Node" src="https://img.shields.io/badge/Node.js-18%2B-43853D?logo=node.js&logoColor=white" />
    <img alt="Express" src="https://img.shields.io/badge/Express-4.x-000000?logo=express&logoColor=white" />
    <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white" />
    <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens" />
    <img alt="Render" src="https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=white" />
    <img alt="License" src="https://img.shields.io/badge/license-MIT-1c1b17" />
  </p>
</div>

---

## О проекте

**Carvix** — учебно-демонстрационный full-stack проект: бэкенд + фронтенд для управления автопарком предприятия.
Учёт техники, заявки на ТО и ремонт, аналитика для руководства, контроль запчастей и поставок.

На текущий момент готов первый блок — **система авторизации и регистрации сотрудников** с ролями и подразделениями,
JWT-сессией и личным кабинетом.

| Часть | Стек |
|-------|------|
| **Backend** | Node.js, Express 4, `pg` (node-postgres), bcryptjs, jsonwebtoken, dotenv, cors |
| **Frontend** | Vanilla JS + HTML5 + CSS3 (без сборщика) — Manrope + Cormorant Garamond, glass-morphism, анимации |
| **БД** | PostgreSQL (DDL — `schema.sql`, демо-данные — `seed_data.sql`) |
| **Хостинг** | Render: free Web Service + free PostgreSQL (одной командой через `render.yaml`) |
| **Безопасность** | bcrypt-хэши паролей, JWT в `Authorization: Bearer …` |

## Структура проекта

```
.
├── server.js              # Express-сервер (статика + /api/auth + /images)
├── db.js                  # PG-пул с mysql2-совместимым адаптером ("?" → "$N")
├── schema.sql             # PG DDL (14 таблиц, IF NOT EXISTS)
├── seed.js                # авто-применяется при старте: создаёт таблицы + базовые роли/подразделения
├── seed-demo.js           # `npm run seed:demo` — заливает полный набор демо-данных
├── seed_data.sql          # SQL-скрипт демо-данных (PostgreSQL)
├── render.yaml            # Конфиг Render: Web + Postgres в один клик
├── routes/auth.js         # /api/auth/{roles, podrazdeleniya, register, login, me}
├── middleware/auth.js     # JWT middleware
├── public/
│   ├── index.html         # страница Login / Register
│   ├── dashboard.html     # личный кабинет после входа
│   ├── styles.css
│   └── script.js
├── images/logo.png
├── script_bd.txt          # ИСТОРИЧЕСКИЙ MySQL DDL (для архивных целей)
├── .env.example
└── package.json
```

## Локальный запуск

> Требуется **Node.js ≥ 18** и **PostgreSQL ≥ 14**.

```bash
git clone https://github.com/boevxd/Carvix.git
cd Carvix
cp .env.example .env
# отредактируйте .env (DB_USER, DB_PASSWORD …)

npm install

# Создаём БД (в psql или GUI)
createdb carvix

npm start
```

При первом старте `seed.js` сам:

1. Применит `schema.sql` (создаст 14 таблиц).
2. Добавит **6 ролей** (`Аналитик / Диспетчер / Механик / Главный механик / Директор / Пользователь`).
3. Добавит **4 подразделения** (`Главное управление / Автопарк №1 / Автопарк №2 / Ремонтный цех`).

После старта откройте http://localhost:3000.

### Залить демо-данные

```bash
npm run seed:demo
```

Скрипт **полностью очистит** таблицы и зальёт 12 сотрудников, 12 машин, 14 заявок, 8 ремонтов и т. д.

## Деплой на Render

Проект полностью готов к **бесплатному** хостингу на Render: один Web Service + один free Postgres.

### Вариант 1 — через `render.yaml` (рекомендуется)

1. Залогиньтесь на https://render.com (через GitHub).
2. **New +** → **Blueprint** → выберите репозиторий `boevxd/Carvix`.
3. Render прочитает `render.yaml` и сам предложит создать:
   - **PostgreSQL** `carvix-db` (free)
   - **Web Service** `carvix` (free) с уже подключённым `DATABASE_URL`
4. Нажмите **Apply** — через 2–3 минуты сайт поднимется на `https://carvix.onrender.com`.

### Вариант 2 — вручную

1. **New +** → **PostgreSQL** → план **Free** → создать `carvix-db`.
2. **New +** → **Web Service** → подключить репозиторий.
3. Настройки:
   - **Build Command**: `npm install`
   - **Start Command**: `node server.js`
   - **Environment Variables**:
     - `DATABASE_URL` → копируем из `Internal Database URL` Postgres-сервиса
     - `JWT_SECRET` → длинная случайная строка
     - `JWT_EXPIRES_IN` = `7d`
     - `NODE_ENV` = `production`
4. **Create Web Service** — после деплоя `seed.js` автоматически создаст таблицы и базовые роли/подразделения.

### Залить демо-данные на Render

В дашборде Web Service → **Shell** → выполнить:

```bash
node seed-demo.js
```

## Тестовые учётные записи

После `npm run seed:demo` (или `node seed-demo.js` на Render) появятся 12 сотрудников.
**Пароль у всех — `password`**.

| Логин | ФИО | Роль |
|-------|-----|------|
| `ivanov` | Иванов И. И. | Директор |
| `petrov` | Петров П. П. | Главный механик |
| `sidorov` | Сидоров А. О. | Механик |
| `kuznetsov` | Кузнецов Д. С. | Механик |
| `morozova` | Морозова А. В. | Диспетчер |
| `volkova` | Волкова Е. И. | Аналитик |
| `sokolov` | Соколов М. А. | Пользователь |
| `lebedev` | Лебедев А. В. | Пользователь |
| `novikov` | Новиков Ю. П. | Механик |
| `orlova` | Орлова С. Н. | Диспетчер |

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET`  | `/api/auth/roles`          | Список ролей |
| `GET`  | `/api/auth/podrazdeleniya` | Список подразделений |
| `POST` | `/api/auth/register`       | Регистрация (`fio`, `login`, `password`). Роль и подразделение проставляются по умолчанию: `Пользователь` / `Главное управление` |
| `POST` | `/api/auth/login`          | Вход (`login`, `password`). Возвращает `{ token, user }` |
| `GET`  | `/api/auth/me`             | Текущий пользователь (требует `Authorization: Bearer <token>`) |

### Пример

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"ivanov","password":"password"}'
```

```json
{
  "token": "eyJhbGciOi…",
  "user": {
    "id": 1,
    "fio": "Иванов Иван Иванович",
    "login": "ivanov",
    "rol_nazvanie": "Директор",
    "podrazdelenie_nazvanie": "Главное управление"
  }
}
```

## Почему PostgreSQL, а не MySQL?

Изначально проект писался под MySQL (`script_bd.txt` остался в репозитории как референс).
При деплое на бесплатный план Render-а доступен только **PostgreSQL**, поэтому проект мигрирован:

- `mysql2` → `pg`.
- `db.js` сохраняет mysql2-совместимый интерфейс (`pool.execute`, `[rows]` деструктуризация, `?` плейсхолдеры) — роуты не пришлось переписывать.
- `AUTO_INCREMENT` → `SERIAL`, `DATETIME` → `TIMESTAMP`, `INSERT … RETURNING id` вместо `result.insertId`.

## Дизайн и анимации

- Палитра **белый / бежевый / серый**, шрифты `Manrope` + `Cormorant Garamond`.
- Glass-morphism карточка с тонкой светящейся гранью сверху.
- Скользящий индикатор табов `Вход ↔ Регистрация` (CSS Grid + transform).
- Floating-labels, иконки слева, eye-toggle паролей.
- Плывущие беж-блобы фоном + точечная сетка с радиальной маской.
- Декоративные пунктирные кольца `spin-slow` и shimmer на бренд-панели.
- Чек-иконки в beige-плитках вместо обычных bullet-точек.
- Микро-анимации: `logo-glide` у логотипа, `shake` при ошибке формы, `feat-in` появление пунктов.

## Дальнейшее развитие

- [ ] Раздел «Транспортные средства» (CRUD + фильтры)
- [ ] Заявки на ремонт (с прикреплением фото)
- [ ] Канбан для механиков
- [ ] Аналитический дашборд (графики по простоям, расходу запчастей)
- [ ] Управление складом
- [ ] Роли и права на эндпоинтах (RBAC middleware)

## Лицензия

MIT © 2026 Carvix
