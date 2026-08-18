# Mini Trello — шпаргалка по бэкенду

Pet-project: FastAPI + SQLAlchemy 2.0 (async) + SQLite.  
Цель файла — не туториал, а карта проекта: какая папка за что отвечает и куда класть новый код.

## Запуск

```powershell
.\.venv\Scripts\Activate.ps1
fastapi dev app/main.py
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Проверка жив ли процесс: `GET /health`

Запускать **из корня** `mini_trello_backend`, не из `app/`. Иначе сломается `from app.core...`.

---

## Слои (как идёт запрос)

```text
HTTP
  → router          URL, статус, HTTPException
    → deps          сессия БД, (потом) текущий пользователь
      → model       строка таблицы
        → SQLite
    ← schema Read   что уходит в JSON
```

| Слой | Вопрос | Сюда кладём | Сюда не кладём |
|---|---|---|---|
| `core/` | как приложение настроено и к чему подключено | URL базы, движок, сессии | роуты, поля доски |
| `models/` | как данные лежат в таблицах | колонки, FK, relationship | JSON, JWT, валидация title |
| `schemas/` | какой JSON принимаем и отдаём | Create / Read, Field, EmailStr | SQL, `hashed_password` в ответе |
| `api/routers/` | какие URL существуют | хендлеры, 201/404 | настройки, создание engine |
| `api/deps.py` | что подставить в хендлер до вызова | `get_db`, auth | бизнес-правила доски |
| `services/` | бизнес-логика без HTTP | SQL-запросы и правила CRUD | декораторы `@router`, HTTPException |
| `main.py` | сборка приложения | FastAPI(), include_router, lifespan | CRUD досок |

Аналог Nest: `core` ≈ ConfigModule + DataSource, `models` ≈ Entity, `schemas` ≈ DTO, `routers` ≈ Controller, `deps` ≈ Guard / Inject, `services` ≈ Service.

---

## Дерево проекта

```text
mini_trello_backend/
│
├── .venv/                      виртуальное окружение (как node_modules). В git не кладём
├── .gitignore                  что не коммитить: .venv, .env, *.db, __pycache__
├── requirements.txt            список пакетов (pip freeze). Аналог package.json + lock
├── README.md                   эта шпаргалка
├── mini_trello.db              файл SQLite, появляется после старта. В git не кладём
│
├── tests/                      pytest. Пока пусто
│   └── __init__.py
│
└── app/                        пакет приложения. Точка входа для импортов: from app...
    ├── __init__.py             делает папку пакетом Python (без него импорты ломаются)
    ├── main.py                 создание FastAPI, lifespan, подключение роутеров, /health
    │
    ├── core/                   инфраструктура: одно на весь процесс
    │   ├── __init__.py
    │   ├── config.py           настройки (имя приложения, URL БД) из .env или дефолтов
    │   └── database.py         engine, фабрика сессий, класс Base для моделей
    │
    ├── models/                 SQLAlchemy: таблицы и связи
    │   ├── __init__.py         импортирует все модели — иначе create_all их не увидит
    │   ├── user.py             таблица users
    │   ├── board.py            таблица boards, FK → users
    │   ├── list.py             таблица lists (класс BoardList), FK → boards
    │   └── card.py             таблица cards, FK → lists
    │
    ├── schemas/                Pydantic: контракт HTTP, не таблицы
    │   ├── __init__.py
    │   ├── user.py             UserCreate (есть password) / UserRead (пароля нет)
    │   ├── board.py            BoardCreate / BoardRead
    │   ├── list.py             ListCreate / ListRead
    │   └── card.py             CardCreate / CardRead
    │
    ├── services/               бизнес-логика без HTTP-слоя
    │   ├── __init__.py
    │   ├── board.py            CRUD-логика досок
    │   ├── list.py             CRUD-логика списков
    │   └── cards.py            CRUD-логика карточек
    │
    └── api/                    HTTP-слой
        ├── __init__.py
        ├── deps.py             Depends: сессия БД, текущий пользователь и ownership-проверки
        └── routers/
            ├── __init__.py
            ├── auth.py         регистрация, логин, /auth/me
            ├── boards.py       CRUD для досок
            ├── lists.py        CRUD для списков
            └── cards.py        CRUD для карточек
```

Пустой `__init__.py` — не мусор, а метка пакета. Исключение: `app/models/__init__.py` не пустой, там реэкспорт моделей.

---

## Файлы по одному

### Корень

**`.venv/`**  
Изолированный Python проекта. Пакеты ставятся сюда, не в систему. Активация: `.\.venv\Scripts\Activate.ps1`.

**`requirements.txt`**  
Что должно быть установлено. На новой машине: `pip install -r requirements.txt`.

**`.gitignore`**  
Секреты (`.env`), база (`*.db`), кэши, `.venv`. В репозиторий уходит только код.

**`mini_trello.db`**  
Сама база. `create_all` создаёт таблицы, но **не меняет** уже существующие. Ошибся в схеме колонок — удали файл и перезапусти сервер. Потом это заменит Alembic.

---

### `app/main.py`

Сборка, не домен.

- `FastAPI(title=..., lifespan=...)` — объект приложения, его импортирует uvicorn (`app.main:app`)
- `lifespan` — код до старта и после остановки. Сейчас: `Base.metadata.create_all`
- `import app.models` — побочный эффект: модели регистрируются на `Base`. Без этого на пустой БД не будет таблиц `lists`/`cards`, если их никто не импортировал
- `include_router(...)` — подключить URL из файла роутера. Файл роутера сам по себе эндпоинты не публикует
- `GET /health` — жив ли процесс. Не про доски, поэтому лежит здесь

---

### `app/core/`

**`config.py`**  
Класс `Settings` (Pydantic `BaseSettings`) + синглтон `settings`.  
Сейчас: `app_name`, `database_url`. Потом сюда же JWT-секрет.  
Имена из `.env`: `DATABASE_URL` → поле `database_url`.  
URL SQLite обязательно с драйвером: `sqlite+aiosqlite:///./mini_trello.db`.

**`database.py`**  
- `engine` — пул соединений, один на процесс  
- `AsyncSessionLocal` — фабрика сессий: на каждый HTTP-запрос своя сессия  
- `Base` — предок моделей. `class Board(Base)` вешает таблицу на `Base.metadata`  
- `echo=True` — печатать SQL в терминал (для учёбы; в проде выключить)  
- `expire_on_commit=False` — после commit поля объекта не «забываются», ответ можно собрать без лишнего SELECT  

Сессию в хендлер этот файл не отдаёт — это `deps.get_db`.

---

### `app/models/`

Таблица ≠ JSON. Здесь колонки, ключи, связи.

```text
User 1 ──< Board 1 ──< BoardList 1 ──< Card
```

- `Mapped[str]` / `mapped_column` — стиль SQLAlchemy 2.0 (как типы в TypeORM)
- `id` — UUID-строка (`str(uuid.uuid4())`), не int
- `ForeignKey("users.id", ondelete="CASCADE")` — правило **базы**: удалили родителя → удалятся дети
- `relationship(..., back_populates="...")` — навигация в Python (`board.lists`). Колонку не создаёт. Имена сторон должны совпасть (`board` ↔ `lists`)
- класс колонки называется `BoardList`, таблица — `lists` (чтобы не затенить встроенный `list`)
- `position` у колонки и карточки — место в списке, для drag-and-drop позже

`models/__init__.py` обязан импортировать User, Board, BoardList, Card.

---

### `app/schemas/`

Контракт API. FastAPI рисует `/docs` и валидирует JSON по этим классам.

На сущность два класса:

| Класс | Когда | Что внутри |
|---|---|---|
| `XxxCreate` | тело запроса | только то, что клиент имеет право прислать |
| `XxxRead` | ответ | id, даты, без секретов; `from_attributes=True` |

- `UserCreate.password` — plaintext. В модели поле `hashed_password`. В `UserRead` пароля нет
- `BoardCreate` — только `title`. `id` генерит uuid, `owner_id` берётся из Depends, не из JSON
- `Field(min_length=1)` — пустая строка → **422**, хендлер не вызовется
- `EmailStr` — нужна библиотека `email-validator` (уже есть)
- `ConfigDict(from_attributes=True)` — можно вернуть ORM-объект, Pydantic снимет атрибуты (`board.title`)
- схема не импортирует модель: иначе слои слипаются

`response_model=BoardRead` и `return board` должны совпадать по форме. Конверт `{ message, data }` при схеме `BoardRead` даёт **500** (ResponseValidationError) уже **после** commit.

---

### `app/api/deps.py`

Общие зависимости. Хендлер пишет `db: AsyncSession = Depends(get_db)` — FastAPI вызовет функцию, подставит результат.

- `get_db` — открыть сессию, `yield`, закрыть даже при ошибке (`async with`)
- `get_current_user` — читает JWT (`Authorization: Bearer ...`), достаёт пользователя из БД
- `get_owned_board` / `get_owned_list` / `get_owned_card` — проверяют, что сущность принадлежит текущему пользователю

`Depends(get_db)` внутри другой Depends: на один запрос сессия одна и та же.

---

### `app/api/routers/*`

Контроллеры (`auth`, `boards`, `lists`, `cards`).

- `APIRouter(prefix="/boards", tags=["boards"])` — все пути с `/boards`, в Swagger группа
- `POST ""` + prefix = `POST /boards`. Не дублировать `/boards` в декораторе
- `GET ""` держать **выше** `GET /{board_id}`
- `payload: BoardCreate` — вход
- `response_model=BoardRead` — выход в JSON
- SQL вынесен в `services/*`; роутеры делают только `Depends`, валидацию входа и HTTP-ответ
- для отсутствующей/чужой сущности роутер возвращает `HTTPException(404)`
- для удаления используется `204 No Content` (без тела ответа)

Подключение только через `app.include_router` в `main.py`.

---

### `app/services/`

Сервисы уже используются в `boards`, `lists`, `cards`.  
Паттерн: сервис возвращает `model | None` / `bool`, а роутер решает, какой HTTP-код вернуть (`404`, `204` и т.д.).

---

### `tests/`

Сюда pytest. Пока не пишем.

---

## Поток данных на примере POST /boards

1. Клиент: `{"title": "Моя доска"}`
2. FastAPI собирает `BoardCreate`, проверяет длину title
3. `get_db` открывает сессию
4. `get_current_user` проверяет JWT и отдаёт текущего пользователя
5. Роутер вызывает `services.board.create_board(...)`
6. `return board` (ORM)
7. `response_model=BoardRead` + `from_attributes` → JSON `{ id, title, owner_id, created_at }`
8. сессия закрывается

---

## Короткие правила

1. Папка без `__init__.py` — не пакет, импорт может не найтись.
2. Имя файла = путь импорта. Переименовал `boards.py` → `board.py` — сразу поправь `from app.models.board import Board`.
3. Модель и схема — разные классы. Read сверяй с колонками **этой** таблицы.
4. `relationship` не колонка. Имена `back_populates` должны совпасть с атрибутами с обеих сторон.
5. UUID: `str(uuid.uuid4())` со скобками. Без скобок — одна и та же строка-мусор на все записи.
6. Async-сессия: везде `await` (`commit`, `refresh`, `execute`, `get`).
7. `create_all` не мигрирует схему. Нужен Alembic или удаление `.db`.
8. Запуск из корня проекта.

---

## Что уже есть / чего нет

**Есть:** каркас, модели четырёх сущностей, схемы, JWT auth (`register/login/me`), CRUD для `boards/lists/cards`, сервисный слой, Swagger.

**Временно:** `create_all` вместо миграций, `echo=True`, ручное тестирование через Swagger (без pytest).

**Дальше по плану:** Alembic, pytest, перестановка `position` при reorder/delete, Postgres, Redis/WebSocket.
