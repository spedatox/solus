"""Standalone application assembly. No dependency on Igor or an AI provider."""
from contextlib import asynccontextmanager
import hmac
import ipaddress
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from solus.database import Database
from solus.services.http import SolusHTTP
from solus.routes import router

class AccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        peer = request.client.host if request.client else ""
        try:
            local = ipaddress.ip_address(peer).is_loopback
        except ValueError:
            local = False
        # Uvicorn is configured to ignore forwarded headers by default. Operators
        # must explicitly configure the actual TLS proxy's address to enable them.
        if not local and request.url.scheme != "https" and path != "/health":
            return JSONResponse({"detail": "HTTPS is required for non-loopback access."}, status_code=403)
        public = path in {"/", "/health", "/solus", "/solus/", "/solus/api/v1/login",
            "/solus/api/v1/setup", "/solus/api/v1/auth-status"} or path.startswith("/solus/assets/")
        key = request.headers.get("X-API-Key", "")
        authorized = bool(key and request.app.state.api_key and hmac.compare_digest(key, request.app.state.api_key))
        if not public and not authorized:
            if not path.startswith("/solus/api/v1/") or not await request.app.state.solus_http.authenticate(request):
                return JSONResponse({"detail": "Authentication required."}, status_code=401)
        response = await call_next(request)
        response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer", "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        if path.startswith("/solus/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

def create_app(database_url=None, api_key=None):
    data = Path(os.environ.get("SOLUS_DATA_DIR", "./data")).resolve()
    if database_url is None:
        data.mkdir(parents=True, exist_ok=True)
        database_url = os.environ.get("SOLUS_DATABASE_URL", f"sqlite+aiosqlite:///{(data / 'solus.db').as_posix()}")
    @asynccontextmanager
    async def lifespan(app):
        database = Database(database_url)
        await database.initialize()
        app.state.database = database
        app.state.solus_http = SolusHTTP(database.sessions)
        app.state.api_key = api_key if api_key is not None else os.environ.get("SOLUS_API_KEY", "")
        try:
            yield
        finally:
            await database.engine.dispose()
    app = FastAPI(title="Solus", version="0.1.0", lifespan=lifespan,
        docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(AccessMiddleware)
    app.include_router(router)
    @app.get("/health")
    async def health():
        return {"status": "ready"}
    @app.get("/")
    async def home():
        return RedirectResponse("/solus")
    return app
