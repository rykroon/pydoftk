from base64 import b64decode
from functools import cached_property
import json
from typing import Any
from urllib.parse import parse_qsl

from starlette.datastructures import FormData, Headers, QueryParams
from starlette.exceptions import HTTPException
from starlette.requests import cookie_parser

from seastar.exceptions import NonWebFunction
from seastar.exceptions import NotRawHttp
from seastar.types import Event


class Request:

    def __init__(self, event: Event):
        if "http" not in event:
            raise NonWebFunction("Event is not a web event.")
        self.event = event

    @cached_property
    def method(self) -> str:
        return self.event["http"]["method"]

    @cached_property
    def path(self) -> str:
        return self.event["http"]["path"]

    @cached_property
    def path_params(self):
        return self.event["http"].get("path_params", {})

    @cached_property
    def query_params(self):
        if "queryString" not in self.event["http"]:
            raise NotRawHttp("Must activate raw http to use query params.")

        return QueryParams(self.event["http"]["queryString"])

    @cached_property
    def headers(self) -> Headers:
        return Headers(self.event["http"]["headers"])

    @cached_property
    def cookies(self):
        if "cookie" in self.headers:
            return cookie_parser(self.headers["cookie"])
        return None

    @cached_property
    def body(self) -> str:
        if "body" not in self.event["http"]:
            raise NotRawHttp("Must activate raw http to use body.")

        body = self.event["http"]["body"]
        if self.event["http"].get("isBase64Encoded", False):
            body = b64decode(body).decode()
        return body

    @cached_property
    def parameters(self):
        return {
            k: v
            for k, v in self.event.items()
            if not k.startswith("__") and k != "http"
        }

    def json(self) -> Any:
        if self.headers.get("content-type") != "application/json":
            raise HTTPException(415)

        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise HTTPException(400)

    def form(self) -> FormData:
        return FormData(parse_qsl(self.body))
