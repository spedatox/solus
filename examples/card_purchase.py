"""Synthetic library demo. Writes to a fresh OS temporary directory only."""
import asyncio
from pathlib import Path
import tempfile
from uuid import uuid4
from solus.context import AgentContext
from solus.coordinator import run_financial_command
from solus.database import Database
from solus.services import reports

async def main():
    with tempfile.TemporaryDirectory(prefix="solus-demo-") as folder:
        database = Database(f"sqlite+aiosqlite:///{(Path(folder) / 'demo.db').as_posix()}")
        try:
            await database.initialize()
            async with database.sessions() as db:
                context = AgentContext("owner", 1, str(uuid4()), db)
                async def command(**payload):
                    return await run_financial_command(context, {"command_key": str(uuid4()), **payload})
                book = (await command(operation="book_create", name="Synthetic demo", kind="personal"))["book_id"]
                food = (await command(operation="account_create", book_id=book, name="Food", account_type="expense"))["account_id"]
                card = (await command(operation="account_create", book_id=book, name="Demo card", account_type="liability"))["account_id"]
                await command(operation="card_calendar_put", book_id=book, account_id=card,
                    closing_day=12, due_offset=10, expected_version=0)
                await command(operation="post", book_id=book, occurrence_key="demo-groceries-001",
                    kind="card_purchase", description="Synthetic grocery purchase", occurred_on="2026-08-13", installments=3,
                    lines=[{"account_id": food, "side": "debit", "amount": "1000.00"},
                           {"account_id": card, "side": "credit", "amount": "1000.00"}])
                async with database.sessions() as reader:
                    for period in ["2026-09", "2026-10", "2026-11"]:
                        result = await reports.statement(reader, 1, book, card, period)
                        print(period, result)
        finally:
            await database.engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
