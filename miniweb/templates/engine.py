from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from typing import Optional


_env: Optional[Environment] = None
_templates_enabled: bool = True

def init_template_engine(enabled: bool = True, templates_dir: str = "templates") -> None:
    global _env, _templates_enabled
    _templates_enabled = enabled

    if not enabled:
        _env = None
        return


    _env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=True
    )


def render_template(template_name: str, context: dict) -> str:
    if not _templates_enabled:
        raise RuntimeError("Шаблонизатор отключён настройками приложения")
    if _env is None:
        raise RuntimeError("Шаблонное окружение не инициализировано")

    try:
        template = _env.get_template(template_name)
    except TemplateNotFound:
        raise FileNotFoundError(f"Шаблон «{template_name}» не найден")

    return template.render(**context)