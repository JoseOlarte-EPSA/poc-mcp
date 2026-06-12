from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    server_version: str
    host: str
    port: int
    mcp_path: str
    transport: str
    auth_mode: str
    bearer_token: str
    excel_path: str

    def validate(self) -> "Settings":
        if self.auth_mode not in {"none", "bearer"}:
            raise ValueError("MCP_AUTH_MODE debe ser 'none' o 'bearer'.")
        if self.auth_mode == "bearer" and not self.bearer_token:
            raise ValueError("MCP_BEARER_TOKEN es obligatorio cuando MCP_AUTH_MODE=bearer.")
        return self

    @property
    def auth_enabled(self) -> bool:
        return self.auth_mode == "bearer"


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("SERVER_NAME", "CRM_MCP"),
        server_version=os.getenv("SERVER_VERSION", "0.1.0"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        mcp_path=(os.getenv("MCP_PATH", "/mcp").strip() or "/mcp"),
        transport=(os.getenv("MCP_TRANSPORT", "streamable-http").strip() or "streamable-http"),
        auth_mode=os.getenv("MCP_AUTH_MODE", "none").strip().lower(),
        bearer_token=os.getenv("MCP_BEARER_TOKEN", "").strip(),
        excel_path=os.getenv("EXCEL_PATH", "").strip(),
    ).validate()
