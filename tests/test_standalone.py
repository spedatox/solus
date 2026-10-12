from dataclasses import replace
from hashlib import sha256
import pytest
import httpx
from solus.app import create_app
from solus.ai import command_tool, propose, approve_proposal
from solus.coordinator import run_financial_command
from test_ledger import ledger

async def test_proposal_needs_exact_owner_approval(ledger):
    context, _, book, _ = ledger
    proposal = propose({"operation":"account_create","command_key":"ai-proposal-fixture-1",
        "book_id":book,"name":"AI proposed food","account_type":"expense"})
    assert proposal.sha256 == sha256(proposal.canonical_json.encode()).hexdigest()
    assert "oneOf" in command_tool()["input_schema"]
    with pytest.raises(ValueError, match="approve"):
        await approve_proposal(context, proposal, approved_sha256="incorrect")
    with pytest.raises(ValueError, match="approve"):
        await approve_proposal(replace(context, agent_id="assistant"), proposal, approved_sha256=proposal.sha256)
    with pytest.raises(ValueError, match="approval"):
        await run_financial_command(replace(context, agent_id="assistant"), proposal.command())
    receipt = await approve_proposal(context, proposal, approved_sha256=proposal.sha256)
    assert receipt["status"] == "success"
    assert await approve_proposal(context, proposal, approved_sha256=proposal.sha256) == receipt

async def test_standalone_lifespan_and_https_boundary(tmp_path):
    app = create_app(f"sqlite+aiosqlite:///{(tmp_path/'host.db').as_posix()}", api_key="host-test-key")
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,client=("203.0.113.8",12345)),base_url="http://remote.test") as client:
            assert (await client.get("/solus/api/v1/auth-status")).status_code == 403
            assert (await client.get("/solus/api/v1/auth-status",headers={"X-Forwarded-Proto":"https"})).status_code == 403
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="https://host.test") as client:
            assert (await client.get("/health")).json() == {"status":"ready"}
            assert (await client.get("/solus/api/v1/books")).status_code == 401
            result = await client.get("/solus/api/v1/books",headers={"X-API-Key":"host-test-key"})
            assert result.status_code == 200
            assert (await client.get("/solus/api/v1/auth-status")).json() == {"configured":False}

async def test_actual_body_limit_without_content_length(ledger):
    _, factory, _, _ = ledger
    from fastapi import FastAPI
    from solus.routes import router
    from solus.services.http import SolusHTTP
    from solus.app import AccessMiddleware
    app = FastAPI()
    app.state.solus_http = SolusHTTP(factory)
    app.state.api_key = "body-fixture-key"
    app.include_router(router)
    app.add_middleware(AccessMiddleware)
    async def chunks():
        for _ in range(3):
            yield b"x" * 1_000_000
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="https://body.test") as client:
        response = await client.post("/solus/api/v1/commands", headers={"X-API-Key":"body-fixture-key"},content=chunks())
        assert response.status_code == 413
