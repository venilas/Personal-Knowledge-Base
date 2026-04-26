# Python `logging` — Стандартная библиотека логирования

## Overview

`logging` — встроенная библиотека Python для регистрации событий во время работы программы.  
Позволяет записывать отладочные сообщения, предупреждения, ошибки и критические события — как из собственного кода, так и из сторонних модулей.

**Ключевые особенности:**
- Иерархическая система логгеров (root → parent → child)
- Гибкая маршрутизация через Handler'ы (файл, консоль, сеть и т.д.)
- Форматирование вывода через Formatter
- Потокобезопасность из коробки

---

## Файлы раздела

| Файл | Назначение |
|------|------------|
| [README.md](./README.md) | Обзор, концепции, примеры, pitfalls |
| [example.ipynb](./example.ipynb) | Интерактивный справочник (Jupyter) — запускай по ячейке |
| [cheatsheet.md](./cheatsheet.md) | Одностраничная шпаргалка: все поля, уровни, форматы |
| [advanced.md](./advanced.md) | Продвинутые темы: RotatingFileHandler, JSON-логи, потоки |

---

## Уровни логирования

| Уровень    | Числовое значение | Назначение                                      | По умолчанию |
|------------|:-----------------:|-------------------------------------------------|:------------:|
| `DEBUG`    | 10                | Подробная отладочная информация                 | ❌           |
| `INFO`     | 20                | Подтверждение штатной работы                    | ❌           |
| `WARNING`  | 30                | Потенциальная проблема, программа ещё работает  | ✅           |
| `ERROR`    | 40                | Ошибка, часть функциональности недоступна       | ✅           |
| `CRITICAL` | 50                | Критическая ошибка, программа может упасть      | ✅           |

> Выводятся все сообщения с уровнем **≥** установленному. Уровень `WARNING` — дефолтный для root-логгера.

---

## Основные компоненты

```
Logger → Handler → Formatter
           ↓
        Filter (опционально)
```

| Компонент   | Роль                                                           |
|-------------|----------------------------------------------------------------|
| `Logger`    | Точка входа. Принимает сообщения и передаёт их Handler'ам     |
| `Handler`   | Определяет **куда** писать (файл, консоль, email, ...)        |
| `Formatter` | Определяет **как** форматировать сообщение                    |
| `Filter`    | Дополнительная фильтрация записей (опционально)               |

---

## Быстрый старт

### 1. Минимальный пример (basicConfig)

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

logger.debug("Отладочное сообщение")
logger.info("Всё работает нормально")
logger.warning("Что-то подозрительное")
logger.error("Произошла ошибка")
logger.critical("Критический сбой")
```

**Вывод:**
```
2024-01-15 10:30:00 | DEBUG    | __main__ | Отладочное сообщение
2024-01-15 10:30:00 | INFO     | __main__ | Всё работает нормально
2024-01-15 10:30:00 | WARNING  | __main__ | Что-то подозрительное
2024-01-15 10:30:00 | ERROR    | __main__ | Произошла ошибка
2024-01-15 10:30:00 | CRITICAL | __main__ | Критический сбой
```

### 2. Запись в файл + консоль одновременно

```python
import logging

logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Handler для консоли
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # В консоль — только WARNING и выше

# Handler для файла
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # В файл — всё

# Форматтер
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("Это попадёт только в файл")
logger.error("Это попадёт и в файл, и в консоль")
```

### 3. Логирование исключений

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("Деление на ноль!")  # Автоматически добавляет traceback
    # Эквивалент: logger.error("...", exc_info=True)
```

---

## Поля Formatter (`fmt`)

| Поле                  | Описание                                      |
|-----------------------|-----------------------------------------------|
| `%(asctime)s`         | Время создания записи                         |
| `%(levelname)s`       | Уровень логирования (`DEBUG`, `INFO`, ...)    |
| `%(levelno)s`         | Числовой код уровня                           |
| `%(name)s`            | Имя логгера                                   |
| `%(message)s`         | Текст сообщения                               |
| `%(filename)s`        | Имя файла                                     |
| `%(pathname)s`        | Полный путь к файлу                           |
| `%(module)s`          | Имя модуля (без расширения)                   |
| `%(funcName)s`        | Имя функции, откуда вызван лог                |
| `%(lineno)d`          | Номер строки                                  |
| `%(process)d`         | PID процесса                                  |
| `%(thread)d`          | ID потока                                     |
| `%(exc_info)s`        | Информация об исключении (если есть)          |

**Трюк выравнивания:** `%(levelname)-8s` — поле займёт минимум 8 символов (выравнивание влево).

---

## Pitfalls

- **`basicConfig` не работает повторно** — он настраивает root-логгер только один раз. Повторный вызов игнорируется, если хендлеры уже добавлены. Используй `force=True` для перезаписи.
- **Не используй root-логгер в библиотеках** — вызов `logging.warning(...)` напрямую загрязняет root. В библиотеках всегда используй `logging.getLogger(__name__)`.
- **Уровень логгера vs уровень хендлера** — оба фильтруют независимо. Если логгер стоит на `ERROR`, хендлер с `DEBUG` всё равно не увидит `DEBUG`-сообщения.
- **`print` вместо `logging`** — не делай так в продакшн-коде. `print` нельзя фильтровать, форматировать и перенаправлять.

---

## Notes

- Логгеры образуют иерархию по имени через точку: `app` → `app.db` → `app.db.query`
- Дочерний логгер **пробрасывает** сообщения родителю (`propagate=True` по умолчанию)
- Стандартный паттерн для каждого модуля: `logger = logging.getLogger(__name__)`
- Для продакшн-проектов рассмотри `logging.config.dictConfig()` или `logging.config.fileConfig()` для конфигурации через словарь/файл

---

## References

- [Официальная документация Python — logging](https://docs.python.org/3/library/logging.html)
- [Logging HOWTO — Python Docs](https://docs.python.org/3/howto/logging.html)
- [Logging Cookbook — Python Docs](https://docs.python.org/3/howto/logging-cookbook.html)
