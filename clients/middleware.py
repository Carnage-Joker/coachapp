from __future__ import annotations

import time
from typing import Callable

from django.http import HttpRequest, HttpResponse


class RequestLoggingMiddleware:
    """Lightweight request logger for development.

    Adds X-Request-Duration header and prints method/path/status to console.
    Safe for dev; no PII is logged.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        try:
            response["X-Request-Duration"] = str(duration_ms)
        except Exception:
            pass
        print(f"[REQ] {request.method} {request.path} -> {getattr(response, 'status_code', '?')} ({duration_ms}ms)")
        return response

