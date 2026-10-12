# AI integration

An assistant is an intent interface. It never computes authoritative balances or edits ledger tables.

```python
from solus.ai import command_tool, propose, approve_proposal

tool_definition = command_tool()  # adapt input_schema to your provider
proposal = propose(model_output_dict)  # validation only; no database write
# Display proposal.command() and proposal.sha256 in a trusted owner UI.
# After that UI obtains explicit approval:
receipt = await approve_proposal(owner_context, proposal,
                                 approved_sha256=owner_approved_hash)
```

The host constructs an authenticated `AgentContext` with `agent_id="owner"`, owner ID, request UUID and its SQLAlchemy session. Do not allow the model to construct that context, choose another owner, supply the approval hash on the owner's behalf or access the approval function as a tool. Missing accounts, amounts, dates, currency or card rules require owner input rather than guesses.

The REST endpoint `POST /solus/api/v1/commands` accepts the same strict commands and is an authorized write surface. A service API key grants owner-level authority: keep it outside model prompts, browser storage and untrusted tools. If you expose writes to an assistant, your host must implement the same explicit review gate. Read reports using authenticated GET endpoints; return their exact values without re-aggregating them in prose.

Every write needs a stable `command_key`. Every source occurrence needs an independent `occurrence_key` for journal operations. Preserve a key when retrying identical input. Change it only after resolving an uncertain request or starting a genuinely new operation. The response is the durable commit receipt.

Use `solus.schemas.parse_command` and its JSON Schema as the source of truth. The included adapter is provider-neutral; it does not call a model, enforce provider-specific schema subsets or verify documentary evidence outside the host. The SPEDA integration adds original-source evidence admission and transactional memory projections separately.

For evidenced statement imports, `post.billed_on` may record the printed closing date separately from the source purchase date. `card_statement_put.event_ids` links actual non-scheduled movements to the printed cycle; do not include a scheduled `card_purchase`, duplicate links, another book/card, or a future occurrence. `card_calendar_put.unbilled_account_id` optionally links a separate same-book/currency liability account for full purchase cost not yet billed. These fields require explicit source evidence and never turn a missing statement into a transaction.
