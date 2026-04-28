<div align="center">
  <img src="images/logo.png" alt="Carvix" width="240" />
  <h1>Carvix</h1>
  <p><b>Веб-система управления автопарком, ТО и ремонтами.</b></p>
  <p>
    <img alt="Node" src="https://img.shields.io/badge/Node.js-18%2B-43853D?logo=node.js&logoColor=white" />
    <img alt="Express" src="https://img.shields.io/badge/Express-5.x-000000?logo=express&logoColor=white" />
    <img alt="MySQL" src="https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white" />
    <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens" />
    <img alt="License" src="https://img.shields.io/badge/license-MIT-1c1b17" />
  </p>
</div>

---

## О проекте

**Carvix** — учебный/демонстрационный проект, реализующий бэкенд и фронтенд для управления автопарком предприятия:
учёт техники, заявки на ТО и ремонт, аналитика для руководства, контроль запчастей и поставок.

На текущий момент готов первый блок — **система авторизации и регистрации сотрудников** с ролями и подразделениями,
JWT-сессией и личным кабинетом.

| Часть | Стек |
|-------|------|
| **Backend** | Node.js, Express 5, mysql2/promise, bcryptjs, jsonwebtoken, dotenv, cors |
| **Frontend** | Vanilla JS, HTML5, CSS3 (без сборщика) — Manrope + Cormorant Garamond, glass-morphism, анимации |
| **БД** | MySQL 8 (схема `script_bd.txt`, наполнение `seed_data.sql`) |
| **Безопасность** | bcrypt-хэши паролей, JWT в `Authorization: Bearer …` |

## Скриншоты

> Палитра проекта — **белый / бежевый / серый**. Фирменный логотип — `images/logo.png`.

| Страница входа / регистрации | Личный кабинет |
|---|---|
| Glass-карточка с двумя панелями: бренд слева, формы справа. Скользящий индикатор табов, floating-labels, shimmer на бренд-панели, плавающие беж-блобы фоном. | После входа — карточка с информацией сотрудника: ФИО, логин, роль (badge), подразделение. |

## Структура проекта

```
.
├── server.js              # Express-сервер (статика + /api/auth + /images)
├── db.js                  # пул mysql2/promise
├── seed.js                # авто-сидер ролей и базовых подразделений при старте
├── routes/
│   └── auth.js            # /api/auth/{roles, podrazdeleniya, register, login, me}
├── middleware/
│   └── auth.js            # JWT middleware
├── public/
│   ├── index.html         # страница Login / Register
│   ├── dashboard.html     # личный кабинет после входа
│   ├── styles.css         # стили + анимации
│   └── script.js          # клиент-логика
├── images/
│   └── logo.png           # фирменный логотип
├── script_bd.txt          # DDL — схема БД (14 таблиц)
├── seed_data.sql          # DML — наполнение демо-данными
├── .env.example           # шаблон переменных окружения
├── .env                   # ваши настройки (в .gitignore)
└── package.json
```

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/boevxd/Carvix.git
cd Carvix
```

### 2. Создать БД и применить схему

В MySQL Workbench (или через CLI) выполнить:

```sql
CREATE DATABASE IF NOT EXISTS carvix DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE carvix;
SOURCE script_bd.txt;
```

> При желании сразу залить демо-данные:
> ```sql
> SOURCE seed_data.sql;
> ```

### 3. Настроить `.env`

Скопируйте шаблон и подставьте свои значения:

```bash
cp .env.example .env
```

```env
PORT=3000
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=ваш_пароль
DB_NAME=carvix
JWT_SECRET=замените_на_длинную_случайную_строку
JWT_EXPIRES_IN=7d
```

### 4. Установить зависимости и запустить

```bash
npm install
npm start
```

Откроется http://localhost:3000.

При первом старте `seed.js` сам добавит **6 ролей** (`Аналитик / Диспетчер / Механик / Главный механик / Директор / Пользователь`) и **4 подразделения** (`Главное управление / Автопарк №1 / Автопарк №2 / Ремонтный цех`).

## Тестовые учётные записи

После применения `seed_data.sql` в БД появятся 12 сотрудников. **Пароль у всех — `password`**.

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
| `GET`  | `/api/auth/roles`            | Список ролей |
| `GET`  | `/api/auth/podrazdeleniya`   | Список подразделений |
| `POST` | `/api/auth/register`         | Регистрация (`fio`, `login`, `password`). Роль и подразделение проставляются по умолчанию: `Пользователь` / `Главное управление` |
| `POST` | `/api/auth/login`            | Вход (`login`, `password`). Возвращает `{ token, user }` |
| `GET`  | `/api/auth/me`               | Текущий пользователь (требует `Authorization: Bearer <token>`) |

### Пример запроса

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
    "rol_id": 5,
    "rol_nazvanie": "Директор",
    "podrazdelenie_id": 1,
    "podrazdelenie_nazvanie": "Главное управление"
  }
}
```

## Схема базы данных (14 таблиц)

```
marka ──┐
        ├── model ──┐
        │           ├── transportnoe_sredstvo ──┐
podrazdelenie ──────┘                           │
        ├── sotrudnik ──┐                       │
rol ────┘               ├── zayavka ────────────┤
                        │       │               │
                        │       ├── remont ──┐  │
status ─────────────────┘       │            │  │
tip_remonta ────────────────────┘            │  │
                                             │  │
postavshik ── zapchast ── ispolzovanie_zapchastey
                                             │
                                vlozhenie ───┘  (zayavka_id ИЛИ remont_id)
```

Подробное DDL — в `script_bd.txt`. Демо-данные (марки, модели, сотрудники, заявки, ремонты, использование запчастей и т. д.) — в `seed_data.sql`.

## Дизайн и анимации

- Палитра **белый / бежевый / серый**, шрифты `Manrope` + `Cormorant Garamond`.
- Glass-morphism карточка с тонкой светящейся гранью сверху.
- Скользящий индикатор табов `Вход ↔ Регистрация` (CSS Grid + transform).
- Floating-labels, иконки слева, eye-toggle паролей.
- Плывущие беж-блобы фоном + точечная сетка с радиальной маской.
- Декоративные пунктирные кольца `spin-slow` на бренд-панели.
- Shimmer-блик через `conic-gradient` на бренд-панели.
- Микро-анимации: `dot-pulse` у точек фич, `logo-glide` у логотипа, `shake` при ошибке формы, `f-in` появление полей при первом показе формы (повторно не воспроизводится при переключении табов).

## Дальнейшее развитие

- [ ] Раздел «Транспортные средства» (CRUD + фильтры)
- [ ] Заявки на ремонт (с прикреплением фото)
- [ ] Канбан для механиков
- [ ] Аналитический дашборд (графики по простоям, расходу запчастей)
- [ ] Управление складом
- [ ] Роли и права на эндпоинтах (RBAC middleware)

## Лицензия

MIT © 2026 Carvix
