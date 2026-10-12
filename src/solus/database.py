"""Database factory; engines and sessions belong to the application instance."""
from sqlalchemy import Integer, String, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Owner")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

class Database:
    def __init__(self, url):
        if not url.startswith("sqlite+aiosqlite:///"):
            raise ValueError("This release requires SQLite with aiosqlite.")
        self.engine = create_async_engine(url)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        @event.listens_for(self.engine.sync_engine, "connect")
        def pragmas(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=15000")
    async def initialize(self):
        from solus import models
        from solus.services.guards import install_guards
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            await connection.run_sync(install_guards)
        async with self.sessions() as session:
            if not await session.get(User, 1):
                session.add(User(id=1, name="Owner", timezone="UTC"))
                await session.commit()
