from base64 import b64decode
from dataclasses import dataclass
import json
from urllib.parse import parse_qsl
from typing import Any, TypeVar

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


Self = TypeVar("Self", bound="Request")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query_params: MultiDictProxy[str]
    headers: CIMultiDictProxy[str]
    body: str
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls: type[Self], event: dict[str, Any]) -> Self:
        if "http" not in event:
            # Not a web event.
            ...

        http = event["http"]
        if "body" not in http or "queryString" not in http:
            # not a raw web event.
            ...

        query_params = MultiDictProxy(MultiDict(parse_qsl(http["queryString"])))
        headers = CIMultiDictProxy(CIMultiDict(http["headers"]))
        body = http["body"]
        if http.get("isBase64Encoded", False):
            body = b64decode(body).decode()

        return cls(
            method=http["method"],
            path=http["path"],
            query_params=query_params,
            headers=headers,
            body=body,
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )

    def json(self) -> Any:
        return json.loads(self.body)

    def form(self) -> MultiDictProxy[Any]:
        return MultiDictProxy(MultiDict(parse_qsl(self.body)))
