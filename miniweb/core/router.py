import re
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Tuple

Handler = Callable[..., Any]


class Router:
    def __init__(self) -> None:
        self.static: Dict[str, Dict[str, Handler]] = defaultdict(dict)
        self.dynamic: Dict[str, list[Tuple[re.Pattern, Handler, Dict[str, Callable]]]] = defaultdict(list)
        self._handler_404: Optional[Handler] = None

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        method = method.upper()
        if "<" not in path:
            self.static[method][path] = handler
            return

        parts = []
        converters: Dict[str, Callable] = {}
        for segment in path.strip("/").split("/"):
            if segment.startswith("<") and segment.endswith(">"):
                typ, name = segment[1:-1].split(":", 1)
                if typ == "int":
                    regex, converters[name] = rf"(?P<{name}>\d+)", int
                elif typ == "float":
                    regex, converters[name] = rf"(?P<{name}>[\d.]+)", float
                elif typ == "path":
                    regex, converters[name] = rf"(?P<{name}>.+)", str
                else:
                    regex, converters[name] = rf"(?P<{name}>[^/]+)", str
                parts.append(regex)
            else:
                parts.append(re.escape(segment))
        pattern = re.compile("^/" + "/".join(parts) + "$")
        self.dynamic[method].append((pattern, handler, converters))

    def set_404(self, handler: Handler) -> None:
        self._handler_404 = handler

    def match(self, method: str, path: str) -> Tuple[Handler, Dict[str, Any]]:
        method = method.upper()
        if path in self.static[method]:
            return self.static[method][path], {}

        for pattern, handler, conv in self.dynamic[method]:
            m = pattern.match(path)
            if m:
                params = {k: conv[k](v) for k, v in m.groupdict().items()}
                return handler, params

        if self._handler_404:
            return self._handler_404, {}
        raise FileNotFoundError(f"Route not found: {method} {path}")