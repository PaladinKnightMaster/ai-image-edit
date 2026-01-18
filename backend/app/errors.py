from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import logging_utils

class APIError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: Any | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def error_payload(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error_handler(_, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload("validation_error", "Invalid request.", exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload("http_error", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_, exc: Exception) -> JSONResponse:
        logging_utils.log_error("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content=error_payload("internal_error", "Unexpected server error."),
        )
