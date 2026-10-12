"""Provider-neutral structured proposals. No model has ledger write authority."""
from dataclasses import dataclass
import hashlib
import json
from pydantic import TypeAdapter
from solus.schemas import SolusCommandInput, parse_command
from solus.coordinator import run_financial_command
from solus.services.commands import SolusError

@dataclass(frozen=True)
class Proposal:
    canonical_json: str
    sha256: str

    def command(self):
        return json.loads(self.canonical_json)

def command_tool():
    """Return a provider-neutral tool definition for collecting proposals.

    The caller must adapt this JSON Schema to its provider's tool protocol.
    Returning a proposal never posts a journal or makes an accounting assertion.
    Review the exact proposal and accounts before invoking approve_proposal.
    """
    return {"name": "propose_accounting_command", "description":
        "Propose a structured accounting command for owner review. Use this when the owner asks to record an evidenced financial event. Do not use it to guess missing amounts, accounts, dates or statement rules. Returns a validated proposal; a separate owner approval is required before posting.",
        "input_schema": TypeAdapter(SolusCommandInput).json_schema()}

def propose(payload):
    validated = parse_command(payload).model_dump(mode="json")
    canonical = json.dumps(validated, sort_keys=True, separators=(",", ":"))
    return Proposal(canonical, hashlib.sha256(canonical.encode()).hexdigest())

async def approve_proposal(context, proposal, *, approved_sha256):
    """The trusted application obtains approval for the exact displayed hash.

    Do not register this approval function as an LLM tool. The UI or host owns
    authorization; an AI-supplied true/false field is never owner approval.
    """
    actual = hashlib.sha256(proposal.canonical_json.encode()).hexdigest()
    if context.agent_id != "owner" or actual != proposal.sha256 or actual != approved_sha256:
        raise SolusError("The owner must approve this exact proposal.", 403)
    return await run_financial_command(context, proposal.command())
