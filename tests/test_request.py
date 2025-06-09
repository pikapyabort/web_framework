# tests/test_request.py

import pytest
from miniweb.utils.request import parse_json, parse_form

class DummyRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body

def test_parse_json_empty():
    req = DummyRequest({}, b"")
    assert parse_json(req) == {}

def test_parse_json_wrong_type():
    req = DummyRequest({"Content-Type": "text/plain"}, b'{"a":1}')
    assert parse_json(req) == {}

def test_parse_json_success():
    req = DummyRequest({"Content-Type": "application/json"}, b'{"x": 10, "y":"ok"}')
    assert parse_json(req) == {"x": 10, "y": "ok"}

def test_parse_json_invalid():
    req = DummyRequest({"Content-Type": "application/json"}, b'{"x":1')
    with pytest.raises(ValueError):
        parse_json(req)

def test_parse_form_empty():
    req = DummyRequest({"Content-Type": "application/x-www-form-urlencoded"}, b"")
    assert parse_form(req) == {}

def test_parse_form_success():
    body = b"foo=bar&baz=42&baz=43"
    req = DummyRequest({"Content-Type": "application/x-www-form-urlencoded"}, body)
    result = parse_form(req)
    assert result == {"foo": "bar", "baz": "42"}

def test_parse_form_wrong_type():
    req = DummyRequest({"Content-Type": "application/json"}, b"foo=bar")
    assert parse_form(req) == {}