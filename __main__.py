from __future__ import annotations

import uvicorn

from server import app, settings

uvicorn.run(app, host=settings.host, port=settings.port)
