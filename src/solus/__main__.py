"""Run the local server or issue an expiring first-time password setup link."""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
from pathlib import Path
import secrets
import uvicorn
from solus.database import Database
from solus.models import SolusSetupToken, SolusCredential

async def setup_link(base_url):
    data = Path(os.environ.get("SOLUS_DATA_DIR", "./data")).resolve()
    data.mkdir(parents=True, exist_ok=True)
    database = Database(os.environ.get("SOLUS_DATABASE_URL", f"sqlite+aiosqlite:///{(data / 'solus.db').as_posix()}"))
    try:
        await database.initialize()
        async with database.sessions() as db:
            if await db.get(SolusCredential, 1):
                raise SystemExit("Password already configured. Change it in Settings.")
            token = secrets.token_urlsafe(48)
            db.add(SolusSetupToken(token_hash=sha256(token.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)))
            await db.commit()
            print(f"{base_url.rstrip('/')}/solus#setup={token}")
    finally:
        await database.engine.dispose()

def main():
    parser = argparse.ArgumentParser(description="Solus standalone accounting")
    parser.add_argument("action", choices=["serve", "setup-link"], nargs="?", default="serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--trusted-proxy", default="", help="Exact TLS reverse proxy IPs; never '*'.")
    args = parser.parse_args()
    if args.action == "setup-link":
        asyncio.run(setup_link(args.base_url))
    else:
        if "*" in args.trusted_proxy:
            parser.error("Wildcard proxy trust is forbidden; supply actual proxy addresses.")
        uvicorn.run("solus.app:create_app", factory=True, host=args.host, port=args.port,
            proxy_headers=bool(args.trusted_proxy), forwarded_allow_ips=args.trusted_proxy,
            server_header=False)

if __name__ == "__main__":
    main()
