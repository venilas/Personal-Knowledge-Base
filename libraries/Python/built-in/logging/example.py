"""
Python logging — Справочник по API и примеры использования
===========================================================
Файл предназначен для изучения и быстрого поиска нужного паттерна.
Запускать целиком не рекомендуется — каждый блок самодостаточен.
"""

import logging
import logging.config

# =============================================================================
# РАЗДЕЛ 1: Основные классы и их параметры
# =============================================================================

# -----------------------------------------------------------------------------
# logging.Formatter — настройка формата вывода
# -----------------------------------------------------------------------------
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    # fmt         — шаблон строки. Поля: %(asctime)s, %(levelname)s, %(name)s,
    #               %(message)s, %(filename)s, %(funcName)s, %(lineno)d, %(process)d и др.
    # %-8s        — выравнивание по левому краю, минимум 8 символов
    datefmt="%Y-%m-%d %H:%M:%S",
    # datefmt     — формат для %(asctime)s: %Y год, %m месяц, %d день,
    #               %H час, %M минута, %S секунда
    style="%",
    # style       — тип форматирования: "%" (по умолчанию), "{" (.format()), "$" (Template)
)

# -----------------------------------------------------------------------------
# logging.FileHandler — запись в файл
# -----------------------------------------------------------------------------
file_handler = logging.FileHandler(
    filename="app.log",  # путь к файлу
    mode="a",            # режим: "a" (append, по умолчанию), "w" (перезапись)
    encoding="utf-8",    # кодировка файла
    delay=False,         # True — открыть файл только при первой записи
    errors=None,         # обработка ошибок кодировки (None = 'strict')
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # минимальный уровень для этого хендлера

# -----------------------------------------------------------------------------
# logging.StreamHandler — вывод в поток (stdout/stderr)
# -----------------------------------------------------------------------------
import sys
stream_handler = logging.StreamHandler(
    stream=sys.stdout,  # по умолчанию sys.stderr
)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)

# -----------------------------------------------------------------------------
# logging.basicConfig — быстрая настройка root-логгера
# -----------------------------------------------------------------------------
# ВАЖНО: работает только ОДИН РАЗ. При повторном вызове игнорируется,
# если у root-логгера уже есть хендлеры. Используй force=True для сброса.
logging.basicConfig(
    level=logging.DEBUG,                          # минимальный уровень root-логгера
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # filename="app.log",                         # если задан → создаётся FileHandler
    # filemode="a",                               # режим файла (только с filename)
    # stream=sys.stdout,                          # поток (не совместимо с filename)
    # handlers=[file_handler, stream_handler],    # свои хендлеры (не совместимо с filename/stream)
    # force=True,                                 # сбросить предыдущие хендлеры и настроить заново
    # encoding="utf-8",                           # кодировка (только с filename)
)

# =============================================================================
# РАЗДЕЛ 2: Создание и использование логгеров
# =============================================================================

# Стандартный паттерн — в каждом модуле своя строка:
logger = logging.getLogger(__name__)
# __name__ == "__main__" при запуске файла напрямую
# __name__ == "package.module" при импорте — формирует иерархию логгеров

# Уровни сообщений
logger.debug("Отладка: подробная информация для разработки")
logger.info("Инфо: программа работает штатно")
logger.warning("Предупреждение: потенциальная проблема")
logger.error("Ошибка: функциональность нарушена")
logger.critical("Критично: программа может упасть")

# Передача переменных (предпочтительный способ — через % или f-строку)
user = "Ilyas"
logger.info("Пользователь вошёл: %s", user)          # ленивое форматирование (рекомендуется)
logger.info(f"Пользователь вошёл: {user}")            # f-строка (тоже допустимо)

# =============================================================================
# РАЗДЕЛ 3: Логирование исключений
# =============================================================================

try:
    result = int("не число")
except ValueError:
    logger.exception("Ошибка преобразования типа")
    # logger.exception = logger.error + автоматически прикладывает traceback
    # Эквивалент: logger.error("...", exc_info=True)

# =============================================================================
# РАЗДЕЛ 4: Продвинутая настройка через dictConfig
# =============================================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # не отключать уже существующие логгеры
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "app.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "my_app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,  # не передавать сообщения root-логгеру
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
app_logger = logging.getLogger("my_app")
app_logger.info("Настройка через dictConfig")

# =============================================================================
# РАЗДЕЛ 5: Иерархия логгеров и propagate
# =============================================================================

parent = logging.getLogger("app")
child = logging.getLogger("app.db")    # дочерний логгер (через точку)
grandchild = logging.getLogger("app.db.query")

# По умолчанию propagate=True: сообщение идёт вверх по иерархии
# child → parent → root
# Чтобы остановить передачу:
# child.propagate = False
