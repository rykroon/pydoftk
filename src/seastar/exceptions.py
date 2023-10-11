from collections.abc import Mapping
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Optional


@dataclass
class HttpException(Exception):
    status_code: int
    detail: Optional[str] = None
    headers: Mapping[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.detail is None:
            self.detail = HTTPStatus(self.status_code).phrase
            super().__init__(self.status_code, self.detail)
    
    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"
