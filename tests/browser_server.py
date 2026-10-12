"""Disposable synthetic browser fixture; never use production configuration."""
from pathlib import Path
import tempfile
import uvicorn
from solus.app import create_app

if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="solus-browser-") as folder:
        app = create_app(f"sqlite+aiosqlite:///{(Path(folder) / 'fixture.db').as_posix()}",
                         api_key="solus-browser-fixture-key")
        uvicorn.run(app, host="127.0.0.1", port=8767, proxy_headers=False, server_header=False)
