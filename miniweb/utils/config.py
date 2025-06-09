import argparse
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "HOST": "127.0.0.1",
    "PORT": 8000,
    "DB_PATH": "app.db",
    "TEMPLATES_ENABLED": True,
    "DEBUG": False
}

def load_config_from_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog="web_framework",
        description="Запуск минимального web-фреймворка на Python"
    )
    parser.add_argument("--host", default=DEFAULT_CONFIG["HOST"], help="Hostname/IP для bind")
    parser.add_argument("--port", type=int, default=DEFAULT_CONFIG["PORT"], help="Порт для bind")
    parser.add_argument("--db", default=DEFAULT_CONFIG["DB_PATH"], help="Путь к SQLite-файлу БД")
    parser.add_argument("--no-templates", action="store_true", help="Отключить шаблонизатор")
    parser.add_argument("--debug", action="store_true", help="Включить режим отладки")

    args = parser.parse_args()

    return {
        "HOST": args.host,
        "PORT": args.port,
        "DB_PATH": args.db,
        "TEMPLATES_ENABLED": not args.no_templates,
        "DEBUG": args.debug
    }