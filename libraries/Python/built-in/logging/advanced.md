# `logging` — Продвинутые темы

## 1. RotatingFileHandler — ротация по размеру

Автоматически создаёт новый файл лога, когда текущий превышает заданный размер.  
Старые файлы сохраняются с суффиксом `.1`, `.2`, ... до `backupCount`.

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    filename='app.log',
    maxBytes=5 * 1024 * 1024,  # 5 MB — при превышении файл ротируется
    backupCount=3,              # хранить app.log, app.log.1, app.log.2, app.log.3
    encoding='utf-8',
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logger.addHandler(handler)

logger.info('Запись в ротируемый файл')
```

**Как работает ротация:**
```
app.log        ← текущий (активная запись)
app.log.1      ← предыдущий
app.log.2      ← ещё старее
app.log.3      ← самый старый (при следующей ротации удаляется)
```

---

## 2. TimedRotatingFileHandler — ротация по времени

Создаёт новый файл лога по расписанию: каждый день, час, неделю и т.д.

```python
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('app.timed')
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler(
    filename='app.log',
    when='midnight',    # 'S' сек, 'M' мин, 'H' час, 'D' день, 'midnight', 'W0'–'W6' (пн–вс)
    interval=1,         # каждые 1 единицу (1 день при when='midnight')
    backupCount=7,      # хранить логи за 7 дней
    encoding='utf-8',
    utc=False,          # использовать локальное время
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logger.addHandler(handler)

logger.info('Запись в файл с ежедневной ротацией')
```

**Параметры `when`:**

| Значение      | Ротация             |
|---------------|---------------------|
| `'S'`         | Каждую секунду      |
| `'M'`         | Каждую минуту       |
| `'H'`         | Каждый час          |
| `'D'`         | Каждый день         |
| `'midnight'`  | В полночь           |
| `'W0'`–`'W6'` | По дню недели (0=пн)|

---

## 3. Кастомный Filter — фильтрация по условию

`Filter` позволяет отсеивать записи по любой логике: имени логгера, тексту, переменным и т.д.

```python
import logging

class SensitiveDataFilter(logging.Filter):
    """Блокирует записи, содержащие ключевое слово 'password'."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Вернуть True — пропустить запись
        # Вернуть False — заблокировать
        return 'password' not in record.getMessage().lower()


class LevelRangeFilter(logging.Filter):
    """Пропускает только записи в диапазоне уровней [min_level, max_level]."""

    def __init__(self, min_level: int, max_level: int):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


# Применение
logger = logging.getLogger('app.filtered')
logger.setLevel(logging.DEBUG)
logger.propagate = False

handler = logging.StreamHandler()
handler.addFilter(SensitiveDataFilter())
# Фильтр можно добавить и на логгер: logger.addFilter(SensitiveDataFilter())

logger.addHandler(handler)

logger.info('Обычное сообщение — выведется')
logger.warning('Пользователь ввёл password — заблокируется')
```

---

## 4. NullHandler — правило для библиотек

Если ты пишешь **библиотеку** (не приложение), никогда не настраивай хендлеры.  
Добавь только `NullHandler` — это передаёт решение о настройке пользователю библиотеки.

```python
# my_library/__init__.py
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
# Теперь пользователь сам решает, как и куда логировать
```

> **Правило:** библиотека логирует, приложение настраивает.

---

## 5. Structured Logging — JSON-логи

Машиночитаемые логи в формате JSON — стандарт для облачных сервисов, ELK, Datadog.

```python
# pip install python-json-logger
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger('app.json')
logger.setLevel(logging.DEBUG)
logger.propagate = False

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('Пользователь вошёл', extra={'user_id': 42, 'ip': '127.0.0.1'})
# {"asctime": "2024-01-15T10:30:00", "levelname": "INFO", "name": "app.json",
#  "message": "Пользователь вошёл", "user_id": 42, "ip": "127.0.0.1"}
```

**Без сторонних библиотек** — через кастомный Formatter:

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'time':    self.formatTime(record, self.datefmt),
            'level':   record.levelname,
            'logger':  record.name,
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger('app.json.manual')
logger.addHandler(handler)
logger.propagate = False
logger.warning('JSON без зависимостей')
```

---

## 6. Логирование в многопоточных приложениях

`logging` **потокобезопасен** из коробки — стандартные хендлеры защищены внутренними блокировками.  
Для высоконагруженных сценариев используй `QueueHandler` + `QueueListener`, чтобы не блокировать рабочие потоки.

```python
import logging
import logging.handlers
import queue
import threading

# Очередь для передачи записей между потоками
log_queue = queue.Queue()

# QueueHandler — не блокирует, просто кладёт запись в очередь
queue_handler = logging.handlers.QueueHandler(log_queue)

# QueueListener — в фоновом потоке достаёт записи и передаёт хендлерам
real_handler = logging.StreamHandler()
real_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(threadName)-12s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
))
listener = logging.handlers.QueueListener(log_queue, real_handler)
listener.start()

# Настройка логгера
logger = logging.getLogger('app.threaded')
logger.addHandler(queue_handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False

def worker(n: int) -> None:
    logger.info(f'Поток {n} начал работу')
    logger.warning(f'Поток {n} завершил работу')

threads = [threading.Thread(target=worker, args=(i,), name=f'Worker-{i}') for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

listener.stop()  # важно: остановить listener при завершении
```

**Почему QueueHandler:**
- Рабочий поток не ждёт записи в файл/сеть — только кладёт в очередь
- Реальная запись происходит в одном фоновом потоке — нет конкуренции за файл

---

## 7. dictConfig — рекомендуемая настройка для приложений

Описывает всю конфигурацию логирования в одном словаре. Легко хранить в `settings.py`, передавать через `.env` и тестировать.

```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            # pip install python-json-logger
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "app.log",
            "maxBytes": 10_485_760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")
logger.info("Приложение запущено")
```

---

## 8. Production Setup

### Docker / Kubernetes

В контейнерной среде **не пишем в файл** — пишем в `stdout/stderr`.  
Платформа сама собирает логи (Fluentd, Loki, CloudWatch и т.д.).

```python
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,   # stdout → собирается оркестратором
)
```

| Среда       | Куда писать    | Кто собирает          |
|-------------|----------------|-----------------------|
| Docker      | stdout/stderr  | Docker log driver     |
| Kubernetes  | stdout/stderr  | Fluentd / Loki        |
| VM / Bare   | Файл           | Logrotate / Filebeat  |
| Cloud       | stdout         | CloudWatch / Stackdriver |

### Добавление request_id

В web-приложениях полезно добавлять `request_id` к каждой записи через `extra` или `LoggerAdapter`:

```python
import logging
import uuid

class RequestAdapter(logging.LoggerAdapter):
    """Добавляет request_id к каждой записи."""
    def process(self, msg, kwargs):
        return f"[{self.extra['request_id']}] {msg}", kwargs

base_logger = logging.getLogger("app.api")

# В начале каждого запроса:
request_id = str(uuid.uuid4())[:8]
logger = RequestAdapter(base_logger, {"request_id": request_id})

logger.info("Запрос получен")
logger.warning("Медленный запрос — 2.3s")
# [a1b2c3d4] Запрос получен
# [a1b2c3d4] Медленный запрос — 2.3s
```

### Что не логировать

- Пароли, токены, API-ключи
- Персональные данные (email, телефон, паспортные данные)
- Тела запросов без фильтрации (могут содержать секреты)
