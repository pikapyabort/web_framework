import asyncio
import inspect
import functools
from http.client import responses
from collections import namedtuple
from typing import Any, Dict
import time

from .router import Router


Request = namedtuple("Request", ["method", "path", "headers", "body"])
Response = namedtuple("Response", ["status", "headers", "body"])


class App:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.router = Router()

    def route(self, path: str, method: str = "GET"):
        def decorator(func):
            self.router.add_route(method, path, func)
            return func
        return decorator

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            raw = await reader.readuntil(b"\r\n\r\n")
        except asyncio.IncompleteReadError:
            writer.close()
            return

        text = raw.decode()
        lines = text.split("\r\n")
        method, path, *_ = lines[0].split(" ")
        headers = {}
        idx = 1
        while lines[idx]:
            key, val = lines[idx].split(":", 1)
            headers[key.strip()] = val.strip()
            idx += 1

        body = b""
        if "Content-Length" in headers:
            length = int(headers["Content-Length"])
            body = await reader.readexactly(length)

        request = Request(method, path, headers, body)

        try:
            handler, params = self.router.match(method, path)
            if inspect.iscoroutinefunction(handler):
                result = await handler(request, **params)
            else:
                result = handler(request, **params)

            if isinstance(result, Response):
                resp = result
            else:
                content = result.encode() if isinstance(result, str) else result
                resp = Response(200, {"Content-Type": "text/html"}, content)
        except FileNotFoundError:
            resp = Response(404, {"Content-Type": "text/plain"}, b"404 Not Found")
        except Exception as e:
            resp = Response(500, {"Content-Type": "text/plain"}, str(e).encode())

        await self._write_response(writer, resp)
        writer.close()

    async def _write_response(self, writer, response: Response):
        writer.write(f"HTTP/1.1 {response.status} {responses.get(response.status, '')}\r\n".encode())
        for k, v in response.headers.items():
            if k.lower() == "content-type" and "charset" not in v.lower():
                v += "; charset=utf-8"
            writer.write(f"{k}: {v}\r\n".encode())
        writer.write(b"\r\n")
        writer.write(response.body)
        await writer.drain()

    def start(self) -> None:
        async def runner():
            server = await asyncio.start_server(self._handle_client, self.host, self.port)
            print(f"* Running on http://{self.host}:{self.port}")
            async with server:
                await server.serve_forever()
        asyncio.run(runner())

    def run(self, host: str = None, port: int = None, debug: bool = False) -> None:
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if debug:
            print("[DEBUG MODE ENABLED]")
        self.start()