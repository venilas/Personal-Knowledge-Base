# `logging` — Шпаргалка

## Уровни логирования

| Уровень    | Число | Метод               |
|------------|:-----:|---------------------|
| `DEBUG`    | 10    | `logger.debug()`    |
| `INFO`     | 20    | `logger.info()`     |
| `WARNING`  | 30    | `logger.warning()`  |
| `ERROR`    | 40    | `logger.error()`    |
| `CRITICAL` | 50    | `logger.critical()` |

---

## Поля fmt

| Поле                  | Описание                              |
|-----------------------|---------------------------------------|
| `%(asctime)s`         | Время создания записи                 |
| `%(levelname)s`       | Уровень (`DEBUG`, `INFO`, ...)        |
| `%(levelno)s`         | Числовой код уровня                   |
| `%(name)s`            | Имя логгера                           |
| `%(message)s`         | Текст сообщения                       |
| `%(filename)s`        | Имя файла (с расширением)             |
| `%(module)s`          | Имя модуля (без расширения)           |
| `%(pathname)s`        | Полный путь к файлу                   |
| `%(funcName)s`        | Имя функции                           |
| `%(lineno)d`          | Номер строки                          |
| `%(process)d`         | PID процесса                          |
| `%(processName)s`     | Имя процесса                          |
| `%(thread)d`          | ID потока                             |
| `%(threadName)s`      | Имя потока                            |
| `%(created)f`         | Время в формате `time.time()`         |
| `%(msecs)d`           | Миллисекунды из asctime               |
| `%(relativeCreated)d` | Мс с момента инициализации logging    |
| `%(exc_info)s`        | Информация об исключении (если есть)  |

**Выравнивание:** `%(levelname)-8s` — минимум 8 символов, влево; `%(levelname)8s` — вправо.

---

## Поля datefmt

| Директива | Описание         | Пример  |
|:---------:|------------------|---------|
| `%Y`      | Год (4 цифры)    | `2024`  |
| `%m`      | Месяц (01–12)    | `01`    |
| `%d`      | День (01–31)     | `15`    |
| `%H`      | Час (00–23)      | `14`    |
| `%M`      | Минута (00–59)   | `30`    |
| `%S`      | Секунда (00–59)  | `05`    |

---

## Готовые форматы

```python
# Минимальный
'%(levelname)s: %(message)s'

# Стандартный
'%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

# Детальный (с файлом и строкой)
'%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s'

# Для консоли в разработке
'[%(levelname)s] %(name)s — %(message)s'
```

---

## Стандартный паттерн (в каждый модуль)

```python
import logging

logger = logging.getLogger(__name__)
```

---

## Быстрая настройка (basicConfig)

```python
import logging, sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
    force=True,   # сброс предыдущих хендлеров
)
```

---

## Хендлеры

| Хендлер                    | Импорт                         | Ключевые параметры                    |
|----------------------------|--------------------------------|---------------------------------------|
| `StreamHandler`            | `logging`                      | `stream=sys.stdout`                   |
| `FileHandler`              | `logging`                      | `filename`, `mode`, `encoding`        |
| `RotatingFileHandler`      | `logging.handlers`             | `maxBytes`, `backupCount`             |
| `TimedRotatingFileHandler` | `logging.handlers`             | `when`, `interval`, `backupCount`     |
| `NullHandler`              | `logging`                      | —  (для библиотек)                    |

---

## Правила

| ✅ Делай                                              | ❌ Не делай                                  |
|------------------------------------------------------|----------------------------------------------|
| `logging.getLogger(__name__)` в каждом модуле        | `logging.warning(...)` в библиотеках         |
| `logger.exception(...)` внутри `except`              | `print()` вместо `logging`                   |
| `force=True` при повторном `basicConfig`             | Повторный `basicConfig` без `force=True`     |
| Разные уровни у логгера и хендлера осознанно         | Путать уровень логгера с уровнем хендлера    |

---

## Best Practices

- **Не используй `print`** — `logging` умеет то, что `print` не может: фильтровать, форматировать, перенаправлять
- **Structured logging** — в production пиши JSON (`python-json-logger`) для интеграции с ELK / Grafana
- **Не логируй секреты** — пароли, токены, API-ключи, персональные данные
- **`NullHandler` в библиотеках** — не навязывай настройку хендлеров пользователям библиотеки
- **Разные уровни для разных окружений** — `DEBUG` в dev, `INFO`/`WARNING` в production
- **`dictConfig` для приложений** — вместо цепочки вызовов в коде; конфиг легко менять без правок кода
