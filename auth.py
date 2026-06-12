from __future__ import annotations

import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class BearerTokenMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        bearer_token: str,
        protected_prefixes: tuple[str, ...],
        public_paths: tuple[str, ...] = ("/", "/health", "/v1/capabilities"),
    ) -> None:
        super().__init__(app)
        self.bearer_token = bearer_token
        self.protected_prefixes = protected_prefixes
        self.public_paths = public_paths

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.public_paths:
            return await call_next(request)

        protected = any(
            path == prefix or path.startswith(f"{prefix}/")
            for prefix in self.protected_prefixes
        )
        if not protected:
            return await call_next(request)

        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if (
            scheme.lower() != "bearer"
            or not token
            or not secrets.compare_digest(token, self.bearer_token)
        ):
            return JSONResponse(
                {
                    "error": "unauthorized",
                    "message": "Falta un bearer token valido para acceder al endpoint MCP.",
                },
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
