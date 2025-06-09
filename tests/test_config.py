# tests/test_config.py

import sys
import pytest
from miniweb.utils.config import load_config_from_args, DEFAULT_CONFIG

def test_default_args(monkeypatch):
    # эмулируем запуск без дополнительных опций
    monkeypatch.setattr(sys, "argv", ["prog"])
    cfg = load_config_from_args()
    assert cfg["HOST"] == DEFAULT_CONFIG["HOST"]
    assert cfg["PORT"] == DEFAULT_CONFIG["PORT"]
    assert cfg["DB_PATH"] == DEFAULT_CONFIG["DB_PATH"]
    assert cfg["TEMPLATES_ENABLED"] is True
    assert cfg["DEBUG"] is False

def test_override_all(monkeypatch):
    # эмулируем полный набор флагов
    monkeypatch.setattr(sys, "argv", [
        "prog",
        "--host", "0.0.0.0",
        "--port", "1234",
        "--db", "/tmp/app.db",
        "--no-templates",
        "--debug"
    ])
    cfg = load_config_from_args()
    assert cfg["HOST"] == "0.0.0.0"
    assert cfg["PORT"] == 1234
    assert cfg["DB_PATH"] == "/tmp/app.db"
    assert cfg["TEMPLATES_ENABLED"] is False
    assert cfg["DEBUG"] is True

def test_help_flag_exits(monkeypatch, capsys):
    # argparse при --help вызывает SystemExit(0) и печатает помощь
    monkeypatch.setattr(sys, "argv", ["prog", "--help"])
    with pytest.raises(SystemExit) as se:
        load_config_from_args()
    assert se.value.code == 0
    captured = capsys.readouterr()
    assert "Запуск минимального web-фреймворка" in captured.out