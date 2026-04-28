-- =========================================================
-- Carvix — DDL (PostgreSQL)
-- Идемпотентная схема: безопасно выполнять много раз.
-- =========================================================

-- 1. Марка
CREATE TABLE IF NOT EXISTS marka (
  id        SERIAL PRIMARY KEY,
  nazvanie  VARCHAR(255) NOT NULL
);

-- 2. Модель
CREATE TABLE IF NOT EXISTS model (
  id        SERIAL PRIMARY KEY,
  marka_id  INT NOT NULL REFERENCES marka(id),
  nazvanie  VARCHAR(255) NOT NULL
);

-- 3. Подразделение
CREATE TABLE IF NOT EXISTS podrazdelenie (
  id        SERIAL PRIMARY KEY,
  nazvanie  VARCHAR(255) NOT NULL
);

-- 4. Роль
CREATE TABLE IF NOT EXISTS rol (
  id        SERIAL PRIMARY KEY,
  nazvanie  VARCHAR(255) NOT NULL
);

-- 5. Сотрудник
CREATE TABLE IF NOT EXISTS sotrudnik (
  id                SERIAL PRIMARY KEY,
  fio               VARCHAR(255) NOT NULL,
  login             VARCHAR(100) NOT NULL UNIQUE,
  parol_hash        VARCHAR(255) NOT NULL,
  rol_id            INT NOT NULL REFERENCES rol(id),
  podrazdelenie_id  INT NOT NULL REFERENCES podrazdelenie(id)
);

-- 6. Транспортное средство
CREATE TABLE IF NOT EXISTS transportnoe_sredstvo (
  id                    SERIAL PRIMARY KEY,
  gos_nomer             VARCHAR(50) NOT NULL,
  invent_nomer          VARCHAR(50) NOT NULL,
  model_id              INT NOT NULL REFERENCES model(id),
  podrazdelenie_id      INT NOT NULL REFERENCES podrazdelenie(id),
  probeg                INT,
  data_vypuska          DATE,
  tekuschee_sostoyanie  VARCHAR(100)
);

-- 7. Статус
CREATE TABLE IF NOT EXISTS status (
  id        SERIAL PRIMARY KEY,
  nazvanie  VARCHAR(100) NOT NULL
);

-- 8. Тип ремонта
CREATE TABLE IF NOT EXISTS tip_remonta (
  id          SERIAL PRIMARY KEY,
  nazvanie    VARCHAR(100) NOT NULL,
  kategoriya  VARCHAR(100)
);

-- 9. Поставщик
CREATE TABLE IF NOT EXISTS postavshik (
  id        SERIAL PRIMARY KEY,
  nazvanie  VARCHAR(255) NOT NULL,
  kontakty  VARCHAR(255),
  adres     VARCHAR(255)
);

-- 10. Запчасть
CREATE TABLE IF NOT EXISTS zapchast (
  id                 SERIAL PRIMARY KEY,
  naimenovanie       VARCHAR(255) NOT NULL,
  artikul            VARCHAR(100),
  postavshik_id      INT REFERENCES postavshik(id),
  tsena              NUMERIC(10,2),
  ostatok_na_sklade  INT,
  kategoriya         VARCHAR(100)
);

-- 11. Заявка
CREATE TABLE IF NOT EXISTS zayavka (
  id              SERIAL PRIMARY KEY,
  data_sozdaniya  TIMESTAMP NOT NULL,
  sozdatel_id     INT NOT NULL REFERENCES sotrudnik(id),
  ts_id           INT NOT NULL REFERENCES transportnoe_sredstvo(id),
  tip_remonta_id  INT NOT NULL REFERENCES tip_remonta(id),
  opisanie        TEXT,
  status_id       INT NOT NULL REFERENCES status(id),
  prioritet       INT,
  data_rezhima    TIMESTAMP
);

-- 12. Ремонт
CREATE TABLE IF NOT EXISTS remont (
  id                   SERIAL PRIMARY KEY,
  zayavka_id           INT NOT NULL REFERENCES zayavka(id),
  data_nachala         TIMESTAMP,
  data_okonchaniya     TIMESTAMP,
  mekhanik_id          INT REFERENCES sotrudnik(id),
  glavniy_mekhanik_id  INT REFERENCES sotrudnik(id),
  stoimost_rabot       NUMERIC(10,2),
  stoimost_zapchastey  NUMERIC(10,2),
  kommentariy          TEXT,
  itog                 VARCHAR(255)
);

-- 13. Использование запчастей
CREATE TABLE IF NOT EXISTS ispolzovanie_zapchastey (
  remont_id        INT NOT NULL REFERENCES remont(id),
  zapchast_id      INT NOT NULL REFERENCES zapchast(id),
  kolichestvo      INT NOT NULL,
  tsena_na_moment  NUMERIC(10,2),
  PRIMARY KEY (remont_id, zapchast_id)
);

-- 14. Вложения
CREATE TABLE IF NOT EXISTS vlozhenie (
  id             SERIAL PRIMARY KEY,
  zayavka_id     INT REFERENCES zayavka(id),
  remont_id      INT REFERENCES remont(id),
  put_faila      VARCHAR(255) NOT NULL,
  tip_faila      VARCHAR(50),
  data_zagruzki  TIMESTAMP
);
