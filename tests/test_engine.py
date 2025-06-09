# tests/test_engine.py

import pytest
from miniweb.templates import engine

def test_render_template_success(tmp_path):
    # 1) Создаём папку templates и в ней файл test.html
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    f = tpl_dir / "hello.html"
    f.write_text("<p>Hello, {{ name }}!</p>")

    # 2) Инициализируем движок с нашей папкой
    engine.init_template_engine(enabled=True, templates_dir=str(tpl_dir))

    # 3) Рендерим шаблон и проверяем результат
    out = engine.render_template("hello.html", {"name": "PyTest"})
    assert out.strip() == "<p>Hello, PyTest!</p>"

def test_render_template_not_found(tmp_path):
    tpl_dir = tmp_path / "empty"
    tpl_dir.mkdir()
    engine.init_template_engine(enabled=True, templates_dir=str(tpl_dir))

    with pytest.raises(FileNotFoundError) as exc:
        engine.render_template("nope.html", {})
    assert "nope.html" in str(exc.value)

def test_render_template_disabled(tmp_path):
    # Когда шаблонизатор отключён – всегда RuntimeError
    engine.init_template_engine(enabled=False, templates_dir=str(tmp_path))
    with pytest.raises(RuntimeError) as exc:
        engine.render_template("any.html", {})
    assert "Шаблонизатор отключён" in str(exc.value)