"""Explicit request state shared by adapters and the engine."""
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class AgentContext:
    agent_id: str
    user_id: int
    request_id: str
    db: AsyncSession
    timezone: str = "UTC"
    session_id: int = 0
    triggered_by: str = "user"
    trigger_payload: dict = field(default_factory=dict)
    output_mode: str = "respond"
    model: str = ""
    system_prompt: str = ""
    conversation_history: list = field(default_factory=list)
