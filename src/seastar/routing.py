from dataclasses import dataclass, field
import inspect
from typing import Any

from seastar.exceptions import HttpException
from seastar.middleware.web import WebEventMiddleware
from seastar.types import Context, Event, EventHandler


@dataclass(order=True)
class Route:
    path: str
    methods: list[str]
    app: EventHandler

    def __post_init__(self):
        if inspect.isfunction(self.app) or inspect.ismethod(self.app):
            self.app = WebEventMiddleware(self.app)

    def __call__(self, event: Event, context: Context) -> Any:
        assert "http" in event, "Expected a web event."
        if self.path != event["http"]["path"]:
            raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            raise HttpException(405, headers=headers)

        return self.app(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[Route] = field(default_factory=list)

    def __call__(self, event: Event, context: Context) -> Any:
        assert "http" in event, "Expected a web event."
        path = event["http"]["path"]
        method = event["http"]["method"]

        for route in self.routes:
            path_match, method_match = route.matches(path, method)
            if not path_match:
                continue

            if not method_match:
                headers = {"Allow": ", ".join(route.methods)}
                raise HttpException(405, headers=headers)

            return route(event, context)

        raise HttpException(404)

    def add_route(self, route: Route):
        self.routes.append(route)
