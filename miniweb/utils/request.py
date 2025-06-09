# miniweb/utils/request.py

import json
from typing import Any, Dict
from urllib.parse import parse_qs

# Предполагаем, что Request у вас предоставляет:
# - request.headers: dict с HTTP-заголовками (ключи в любом регистре)
# - request.body: bytes или строку (сырое тело запроса)

def parse_json(request) -> Dict[str, Any]:
    """
    Парсит JSON-тело запроса и возвращает словарь.
    Если Content-Type ≠ application/json или тело пустое — возвращает {}.
    В случае некорректного JSON — бросает ValueError.
    """
    content_type = request.headers.get("Content-Type", "")
    if "application/json" not in content_type.lower():
        return {}
    body = request.body
    if not body:
        return {}
    # Если body — bytes, декодируем в utf-8
    if isinstance(body, (bytes, bytearray)):
        body = body.decode("utf-8")
    data = json.loads(body)  # ValueError при некорректном JSON
    if not isinstance(data, dict):
        raise ValueError("JSON payload is not an object")
    return data

def parse_form(request) -> Dict[str, Any]:
    """
    Парсит тело x-www-form-urlencoded и возвращает «плоский» словарь.
    Если Content-Type ≠ application/x-www-form-urlencoded или тело пустое — {}.
    """
    content_type = request.headers.get("Content-Type", "")
    if "application/x-www-form-urlencoded" not in content_type.lower():
        return {}
    body = request.body
    if not body:
        return {}
    if isinstance(body, (bytes, bytearray)):
        body = body.decode("utf-8")
    # parse_qs возвращает List[str] для каждого ключа, распаковываем первый элемент
    raw = parse_qs(body, keep_blank_values=True)
    return {k: v[0] if v else "" for k, v in raw.items()}