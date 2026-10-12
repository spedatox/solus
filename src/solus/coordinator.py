"""Atomic command boundary. AI proposals require explicit owner approval.

The host integration can add a transactional projection through after_apply.
It must use the supplied writer session and must never commit independently.
"""
import hashlib
import json
from dataclasses import replace
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from solus.models import SolusCommand
from solus.schemas import parse_command
from solus.services.commands import apply, SolusError

async def after_apply(db, context, receipt, command, evidence):
    """Extension point for derived views in the same transaction."""

async def run_financial_command(context, payload):
    command = parse_command(payload)
    canonical = command.model_dump(mode="json")
    fingerprint = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if context.agent_id != "owner":
        raise SolusError("AI proposals require explicit owner approval before posting.", 403)
    bind = context.db.bind
    if bind is None or bind.dialect.name != "sqlite":
        raise SolusError("Solus requires the configured SQLite engine.", 409)
    async with AsyncSession(bind=bind, expire_on_commit=False) as writer:
        try:
            await writer.execute(text("BEGIN IMMEDIATE"))
            previous = await writer.scalar(select(SolusCommand).where(
                SolusCommand.user_id == context.user_id, SolusCommand.command_key == command.command_key))
            if previous:
                if previous.payload_hash != fingerprint:
                    raise SolusError("Idempotency key already belongs to a different command.", 409)
                receipt = dict(previous.receipt)
                await writer.rollback()
                return receipt
            local = replace(context, db=writer)
            evidence = [{"ref": f"solus-command:{command.command_key}",
                "quote": json.dumps(canonical, ensure_ascii=False), "source_sha256": fingerprint,
                "source_authority": "owner"}]
            result = await apply(writer, command, local, evidence)
            receipt = {"status": "success", "command_key": command.command_key, **result}
            await after_apply(writer, local, receipt, command, evidence)
            writer.add(SolusCommand(user_id=context.user_id, command_key=command.command_key,
                payload_hash=fingerprint, payload=canonical, receipt=receipt,
                actor=context.agent_id, request_id=context.request_id))
            await writer.commit()
            return receipt
        except IntegrityError as exc:
            await writer.rollback()
            raise SolusError("Accounting identity or journal constraint failed; nothing saved.", 409) from exc
        except Exception:
            await writer.rollback()
            raise

async def resolve_financial_command(context, command_key):
    if context.agent_id != "owner" or not 8 <= len(command_key) <= 200:
        raise SolusError("Only the owner can resolve a valid uncertain command key.")
    async with AsyncSession(bind=context.db.bind, expire_on_commit=False) as writer:
        await writer.execute(text("BEGIN IMMEDIATE"))
        saved = await writer.scalar(select(SolusCommand).where(
            SolusCommand.user_id == context.user_id, SolusCommand.command_key == command_key))
        if saved:
            receipt = dict(saved.receipt)
            await writer.rollback()
            return receipt
        payload = {"operation": "cancel_uncertain", "command_key": command_key}
        receipt = {"status": "cancelled", "command_key": command_key}
        writer.add(SolusCommand(user_id=context.user_id, command_key=command_key,
            payload_hash=hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            payload=payload, receipt=receipt, actor=context.agent_id, request_id=context.request_id))
        await writer.commit()
        return receipt
