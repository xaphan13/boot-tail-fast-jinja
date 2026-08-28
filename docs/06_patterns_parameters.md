# 06. Чему учит проект: извлечение параметров и валидация pydantic

> Часть 6 из 7. См. также: [05_patterns_di.md](05_patterns_di.md), [07_patterns_data_layer.md](07_patterns_data_layer.md).

Здесь разбираем самый показательный учебный блок проекта: **один и тот же эндпоинт `GET /my_items/{item_id}` реализован четырьмя способами**. Он достаёт из запроса `Path`, `Query`, `Header`, `Cookie`, а также `Request`/`Response`, и одинаково обрабатывает их. Разница — только в стиле объявления параметров. Сравнивать их построчно и есть учебная цель.

---

## Что общего у всех четырёх эндпоинтов

`api/my_routes_dep/my_param_fast_cls.py` (стиль 1) — эталон, все четыре делают одно:

```python
@router_param_fast_cls_old.get("/my_items/{item_id}", response_model=RespFieldStyle)
def fastapi_class_old(
    path_item_id: int = Path(alias="item_id", ge=1, description="Path - item_id должен быть больше 0"),
    query_param_id: int | None = Query(default=None, alias="param_id", description="Query - первый параметр"),
    header_user_id: str | None = Header(default=None, alias="user-id", description="Header - ай-ди клиента"),
    cookie_number_req: int = Cookie(default=1, alias="number-req", description="Cookie - количество запросов от клиента"),
    request: Request = ...,
    response: Response = ...,
):
    response.headers["X-Custom-Header"] = "Processed-By-FastAPI"
    response.set_cookie(key="visited", value="true")
    response.set_cookie(key="number-req", value=str(cookie_number_req + 1))

    return {
        "path": path_item_id,
        "query": query_param_id,
        "header": header_user_id,
        "cookie": cookie_number_req,
        "request": request.client.port,
    }
```

### Какую задачу решает

Эндпоинт демонстрирует **все основные источники данных HTTP-запроса** в одном месте:

- `item_id` — переменная из пути `/my_items/{item_id}`;
- `param_id` — query-параметр `?param_id=...`;
- `user-id` — заголовок запроса;
- `number-req` — cookie;
- `request`/`response` — служебные объекты Starlette.

И дополнительно — **модификацию ответа**: подстановку заголовка и двух cookies. Cookie `number-req` инкрементируется на единицу и возвращается клиенту — «счётчик запросов».

### Почему это правильно

- `Path(alias="item_id", ge=1)` — `alias` связывает имя аргумента `path_item_id` с `{item_id}` в URL, а `ge=1` даёт **валидацию на уровне источника**: значение меньше 1 → 422, ещё до входа в функцию.
- `Query(default=None, alias="param_id")` — необязательный параметр с явным default.
- `request.client.port` — показывает, как достать информацию о клиенте.
- `response.set_cookie(...)` / `response.headers[...]` — как управлять ответом.

### Почему «не совсем»

- `request: Request = ...` и `response: Response = ...` — `Ellipsis` (`...`) здесь **избыточен**. FastAPI распознаёт эти типы по одной только аннотации, default-значение не нужно. Это KISS-нарушение, замечание повторяется во всех четырёх файлах.
- `request.client.port` за прокси (nginx) вернёт порт прокси, а не клиента — `ProxyHeadersMiddleware` не включён (см. 03).

---

## Четыре стиля: что именно они сравнивают

### Стиль 1 — классы FastAPI как default-значения

```python
path_item_id: int = Path(alias="item_id", ge=1)
query_param_id: int | None = Query(default=None, alias="param_id")
```

Параметр объявлен как `имя: тип = Path(...)`. FastAPI понимает `Path`/`Query`/`Header`/`Cookie` как **default-значения** и строит по ним метаданные.

**Минус:** тип и дефолт «слиты» в одно выражение, а сам тип `int` стоит до `=`. Для IDE тип аргумента виден, но читается хуже.

### Стиль 2 — то же через `Annotated`

`my_param_fast_ann.py`:

```python
path_item_id: Annotated[int, Path(alias="item_id", ge=1)],
query_param_id: Annotated[int | None, Query(alias="param_id")] = None,
cookie_number_req: Annotated[int, Cookie(alias="number-req")] = 1,
```

**Что меняется:** метаданные (`Path`, `Query`, ...) уходят **внутрь** `Annotated`, а default-значение (`= None`, `= 1`) выносится **наружу**.

**Почему это правильнее:**
- Тип `int | None` теперь стоит на своём месте — сразу виден IDE и линтерам.
- Дефолт отделён от метаданных: `= None` читается как «необязательный», `Path(...)` — как «как извлечь».
- Это **рекомендуемый современный стиль FastAPI** (документация прямо советует `Annotated`). Он же используется в `Depends` и в типах колонок БД — единый стиль по всему проекту.

### Стиль 3 — параметры собраны в классы (через `Depends`)

`my_param_dep_cls.py` + `dep_cls_schema.py`:

```python
# dep_cls_schema.py — «классы-зависимости»
class PathData:
    def __init__(self, item_id: Annotated[int, Path(alias="item_id", ge=1)]):
        self.path_item_id = item_id

class QueryData:
    def __init__(self, param_id: Annotated[int | None, Query(alias="param_id")] = None):
        self.query_param_id = param_id

# my_param_dep_cls.py — обработчик
def depends_class_annotated(
    path_cls: Annotated[PathData, Depends()],
    query_cls: Annotated[QueryData, Depends()],
    header_cls: Annotated[HeaderData, Depends()],
    cookie_cls: Annotated[CookieData, Depends()],
    request: Request = ...,
    response: Response = ...,
):
    ...
    return {
        "path": path_cls.path_item_id,
        "query": query_cls.query_param_id,
        ...
    }
```

**Какую задачу решает:** каждый источник данных (Path/Query/Header/Cookie) выносится в отдельный класс. `PathData`, `QueryData` и т.д. — это **обычные классы, не pydantic-модели**: FastAPI читает аннотации их `__init__`, извлекает значения и сохраняет в атрибуты вида `self.path_item_id`. Обработчик получает сгруппированные объекты.

**Почему это удобно:** сигнатура обработчика становится короткой (4 объекта вместо 4+ отдельных аргументов), а логику извлечения каждого источника можно переиспользовать и юнит-тестировать отдельно.

**Почему «не совсем»:** `Depends()` без аргумента — необычная запись (пустой `Depends()` с классом в `Annotated`). Плюс создаётся по объекту на каждый источник — это скорее демонстрация «как можно», чем то, что стоит делать для пары параметров. Для большого набора параметров лучше pydantic-модель.

### Стиль 4 — параметры собраны в функции (через `Depends`)

`my_param_dep_func.py` + `dep_func_schema.py`:

```python
# dep_func_schema.py
def get_item_id(item_id: Annotated[int, Path(alias="item_id", ge=1)]) -> int:
    """Извлекает и валидирует ID из пути."""
    return item_id

def get_param_id(param_id: Annotated[int | None, Query(alias="param_id")] = None) -> int | None:
    """Извлекает параметр из строки запроса."""
    return param_id

# my_param_dep_func.py
def depends_function_annotated(
    path_item_id: Annotated[int, Depends(get_item_id)],
    query_param_id: Annotated[int | None, Depends(get_param_id)],
    header_user_id: Annotated[str | None, Depends(get_user_id)],
    cookie_number_req: Annotated[int, Depends(get_number_req)],
    ...
):
    return {
        "path": path_item_id,
        "query": query_param_id,
        ...
    }
```

**Какую задачу решает:** каждый источник выносится в **отдельную функцию-зависимость** с docstring. Обработчик вызывает их через `Depends(get_item_id)` и т.д.

**Почему это удобно:** функции можно переиспользовать в любом эндпоинте, у них есть явная документация («Извлекает и валидирует ID из пути»), их легко тестировать. Это «функциональный» вариант стиля 3.

**Почему «не совсем»:** для такого простого случая (просто вернуть аргумент) 4 функции — это много кода. Здесь же спрятан **настоящий дефект**: `RespDecorValid.validate_query_safe` (см. ниже в этом файле) падает на `None`, а `query_param_id` по умолчанию как раз `None`. То есть этот эндпоинт возвращает 500 на обычный запрос без `param_id`.

---

## Сравнительная таблица четырёх стилей

| Стиль | Файл | Объявление | Плюс | Минус |
|---|---|---|---|---|
| 1. FastAPI-классы как default | `my_param_fast_cls.py` | `x: int = Path(...)` | Просто | Тип и метаданные слиты |
| 2. `Annotated` | `my_param_fast_ann.py` | `x: Annotated[int, Path(...)] = None` | Современный, читаемый | — |
| 3. Классы + `Depends` | `my_param_dep_cls.py` | `x: Annotated[PathData, Depends()]` | Группировка, переиспользование | Много объектов |
| 4. Функции + `Depends` | `my_param_dep_func.py` | `x: Annotated[int, Depends(get_item_id)]` | Переиспользование, docstring | Много кода + дефект валидации |

**Учебный вывод:** стиль 2 (`Annotated`) — базовый и рекомендуемый. Стили 3–4 показывают, как выносить извлечение в переиспользуемые зависимости, когда набор параметров большой или повторяется. Стиль 1 — исторический, знать его полезно для чтения старого кода.

---

## Паттерн: `Field(...)` против `Annotated[T, Field(...)]` в pydantic-схемах

`api/my_routes_dep/pydantic_schema.py`:

```python
# Стиль 1: Field как default-значение
class RespFieldStyle(BaseModel):
    path: int = Field(..., description="ID из пути URL")
    query: int | None = Field(None, description="ID из параметров запроса")

# Стиль 2: Field внутри Annotated
class RespAnnotated(BaseModel):
    path: Annotated[int, Field(description="ID из пути URL")]
    query: Annotated[int | None, Field(description="ID из параметров запроса")] = None
```

**Что учит:** тот же принцип, что и в стиле 2 параметров — метаданные в `Annotated`, дефолт наружу. `Annotated`-стиль единообразен: для полей pydantic, для параметров FastAPI и для колонок SQLAlchemy в проекте используется одна и та же идиома. Это согласованность — важный учебный момент.

---

## Паттерн: `AfterValidator` против `@field_validator`

`api/my_routes_dep/pydantic_validator.py` — два способа наложить валидацию:

```python
# Способ 1: Annotated + AfterValidator (валидация «вшита» в тип)
def check_port_range(v: int) -> int:
    if not (1024 <= v <= 65535):
        raise ValueError("Порт должен быть в диапазоне 1024-65535")
    return v

PortNumber = Annotated[int, AfterValidator(check_port_range)]

class RespAfterValid(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)
    path: PathID                       # PathID = Annotated[int, Field(ge=1)]
    query: QueryID = None              # QueryID = Annotated[int | None, Field(ge=1, le=1000)]
    request: PortNumber
```

```python
# Способ 2: декоратор @field_validator (валидация «вшита» в класс)
class RespDecorValid(BaseModel):
    path: int
    query: int | None = None
    request: int

    @field_validator("path")
    @classmethod
    def validate_path_is_even(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Path ID должен быть больше 0")
        return v

    @field_validator("query")
    @classmethod
    def validate_query_safe(cls, v: int | None) -> int | None:
        if 1 <= v <= 1000:
            return v
        raise ValueError("либо None, либо число от 1 до 1000")
```

### Какую задачу решают оба

Ограничить значения полей: порт — в диапазоне 1024–65535, `query` — 1..1000, `path` — положительный.

### Почему `AfterValidator`-подход правильнее

1. **Переиспользуемость типов.** `QueryID`, `PathID`, `PortNumber` — это типы. Один и тот же тип можно использовать в нескольких моделях, не дублируя логику.
2. **Декларативность.** Ограничение видно сразу у поля: `query: QueryID` читается как «query — это ID запроса (1..1000)».
3. **`Field(ge=1, le=1000)` вместо ручного сравнения** — декларативное описание, не ошибается.
4. **`frozen=True` + `str_strip_whitespace`** — показан `model_config`, который делает модель иммутабельной и чистит пробелы. Хорошая практика для response-моделей.

### Почему `@field_validator`-подход «не совсем» (здесь целых 3 дефекта)

1. **`validate_query_safe` падает на `None`** (P1-дефект, см. 04): поле объявлено `int | None = None`, но код пишет `if 1 <= v <= 1000`. При `v is None` сравнение `1 <= None` бросит `TypeError` → 500. Эндпоинт `/api/v1/depends_function_annotated/...` ломается на **любом** запросе без `param_id` — то есть в дефолтном сценарии. Правильно: `if v is None or 1 <= v <= 1000: return v`.
2. **`validate_path_is_even` не соответствует ни имени, ни сообщению:** имя обещает проверку чётности (её нет), условие `if v < 0` пропускает `0`, хотя сообщение говорит «должен быть больше 0». Само ограничение уже задано в `Path(ge=1)` — валидатор избыточен.
3. **Валидация порта ломает ответ:** `request` — это исходящий порт клиента, и он непредсказуем. Клиент с портом < 1024 получит 500 на валидации **ответа** при полностью корректном запросе. Нельзя валидировать данные, которыми вы не управляете, в response-модели.

**Учебный вывод:** `AfterValidator` + `Annotated`-типы — современный, переиспользуемый и декларативный способ. `@field_validator` годится для сложной логики, затрагивающей несколько полей, но требует осторожности с `None` и граничными значениями. А главный практический урок: **не валидируйте то, что не контролируете** (порт клиента), и **не проверяйте вручную то, что уже покрыто декларативными ограничениями**.

---

## Итог по блоку параметров

| Тема | Правильный приём | Ошибка-ловушка |
|---|---|---|
| Объявление параметров | `Annotated[int, Path(...)]` (стиль 2) | `Path(...)` как default (стиль 1) — устаревший |
| Дефолт | выносить за `Annotated` | прятать внутрь |
| Группировка параметров | классы/функции через `Depends` при большом наборе | для 1–2 параметров — избыточно |
| Валидация | `Annotated` + `AfterValidator` + `Field(ge=, le=)` | `@field_validator` без обработки `None` → 500 |
| Response-модель | `frozen=True`, не валидировать чужой ввод | валидация порта клиента → 500 |
