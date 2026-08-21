# Mini Trello — шпаргалка по бэкенду

Pet-project: FastAPI + SQLAlchemy 2.0 (async) + Postgres (Docker) / SQLite для тестов.  
Цель файла — не туториал, а карта проекта: какая папка за что отвечает и куда класть новый код.

## Запуск

```powershell
.\.venv\Scripts\Activate.ps1
copy .env.example .env          # один раз: создать локальный .env
docker compose up -d            # Postgres на порту 5433
alembic upgrade head            # применить миграции
fastapi dev app/main.py
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Проверка: `GET /health`

Запускать **из корня** `mini_trello_backend`, не из `app/`. Иначе сломается `from app.core...`.

Без `.env` / без Docker приложение возьмёт дефолт из `config.py` (SQLite-файл). Для учёбы и «как в проде» используй Postgres через Docker.

### Postgres в pgAdmin

| Поле | Значение |
|---|---|
| Host | `127.0.0.1` |
| Port | `5433` |
| Database | `mini_trello` |
| User | `trello` |
| Password | `trello` |

Порт **5433** на хосте специально: локальный Postgres часто занимает `5432`.

Через терминал:
```powershell
docker exec -it mini_trello_backend-db-1 psql -U trello -d mini_trello
```

### Тесты

```powershell
pytest tests/ -v
```

Тесты ходят в **SQLite in-memory**, не в Docker-Postgres. Рабочую БД не трогают.

---

## Слои (как идёт запрос)

```text
HTTP
  → router          URL, статус, HTTPException
    → deps          сессия БД, текущий пользователь (JWT)
      → service     SQL / бизнес-правила
        → model     строка таблицы
          → Postgres
    ← schema Read   что уходит в JSON
```

| Слой | Вопрос | Сюда кладём | Сюда не кладём |
|---|---|---|---|
| `core/` | как приложение настроено и к чему подключено | URL базы, движок, сессии, JWT | роуты, поля доски |
| `models/` | как данные лежат в таблицах | колонки, FK, relationship | JSON, JWT, валидация title |
| `schemas/` | какой JSON принимаем и отдаём | Create / Read / Update / Move | SQL, `hashed_password` в ответе |
| `api/routers/` | какие URL существуют | хендлеры, 201/404/204 | настройки, создание engine |
| `api/deps.py` | что подставить в хендлер до вызова | `get_db`, auth, ownership | бизнес-правила доски |
| `services/` | бизнес-логика без HTTP | SQL-запросы и правила CRUD/move | декораторы `@router`, HTTPException |
| `main.py` | сборка приложения | FastAPI(), include_router | CRUD, create_all |

Аналог Nest: `core` ≈ ConfigModule + DataSource, `models` ≈ Entity, `schemas` ≈ DTO, `routers` ≈ Controller, `deps` ≈ Guard / Inject, `services` ≈ Service.

---

## Дерево проекта

```text
mini_trello_backend/
│
├── .venv/                      виртуальное окружение. В git не кладём
├── .env                        локальные секреты. В git не кладём
├── .env.example                шаблон для .env (без секретов) — в git кладём
├── .gitignore
├── requirements.txt
├── README.md
├── docker-compose.yml          Postgres 16
├── alembic.ini
├── pytest.ini
│
├── migrations/                 Alembic
│   ├── env.py                  async + Base.metadata
│   └── versions/               файлы миграций
│
├── tests/                      pytest + httpx
│   ├── conftest.py             in-memory SQLite, auth_client
│   ├── test_auth.py
│   ├── test_boards.py
│   ├── test_lists.py
│   └── test_cards.py
│
└── app/
    ├── main.py                 FastAPI, include_router, /health
    ├── core/
    │   ├── config.py           Settings из .env
    │   ├── database.py         async engine / session / Base
    │   └── security.py         JWT (AuthX) + хеш пароля
    ├── models/
    ├── schemas/
    ├── services/               board / list / cards
    └── api/
        ├── deps.py
        └── routers/            auth, boards, lists, cards
```

---

## Файлы по одному

### Корень

**`.env` / `.env.example`**  
`.env` — локальные значения (`DATABASE_URL`, `JWT_SECRET_KEY`). В git не коммитить.  
`.env.example` — шаблон: скопировал → поправил → работает.

**`docker-compose.yml`**  
Один сервис `db`: Postgres 16, пользователь `pgdata`, порт хоста `5433` → контейнер `5432`.

**`alembic.ini` + `migrations/`**  
Схема БД через миграции, не через `create_all`.  
`migrations/env.py` берёт URL из `settings.database_url` (то есть из `.env`).

**`requirements.txt`**  
`pip install -r requirements.txt` на новой машине.

---

### `app/main.py`

Сборка приложения: `FastAPI()`, `include_router`, `/health`.  
Таблицы создаёт **Alembic**, не lifespan/`create_all`.

---

### `app/core/`

**`config.py`** — `Settings` + `settings`.  
Из `.env`: `DATABASE_URL` → `database_url`, `JWT_SECRET_KEY` → `jwt_secret_key`.

**`database.py`** — async engine, `AsyncSessionLocal`, `Base`.

**`security.py`** — AuthX (JWT) + `pwdlib` (хеш пароля).

---

### `app/models/` / `schemas/` / `services/` / `api/`

Как раньше: модель = таблица, схема = JSON-контракт, сервис = SQL без HTTP, роутер = Depends + статусы.

Move:
- `PATCH /cards/{card_id}/move` — тело `CardMove { position }`
- `PATCH /lists/{list_id}/move` — тело `ListMove { position }`

Вход Move / ответ Read — разные схемы.

---

### `tests/`

`conftest.py`: in-memory SQLite + `dependency_overrides` для `get_db` + фикстура `auth_client` (register → login → Bearer).

---

## Короткие правила

1. Запуск из корня проекта.
2. `.env` в git не класть; в репозитории только `.env.example`.
3. Схема БД — только Alembic (`upgrade head` / новая `revision --autogenerate`).
4. Async-сессия: везде `await`.
5. Сервис возвращает `None`/`False`, роутер кидает `HTTPException`.
6. Для URL с переменными всегда `f"..."` (`f"/lists/{list_id}"`).
7. Тесты ≠ Docker-Postgres.

---

## Что уже есть / чего нет

**Есть:** JWT auth, CRUD boards/lists/cards, move (reorder), сервисы, Alembic, pytest, Postgres в Docker, Swagger, pgAdmin-подключение.

**Временно:** `echo=True` в SQLAlchemy, SQLite как дефолт без `.env`.

**Дальше по плану:** move карточки в другой список, CORS под фронт, Redis/WebSocket.
