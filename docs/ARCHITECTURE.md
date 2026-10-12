# Architecture

Solus is a Python library plus a FastAPI host and compiled Vue UI. `Database` owns an async SQLAlchemy engine/session factory; each app has its own database and security services on `app.state`. The HTTP routes only adapt requests to services. All request identity, timezone and database state travel through `AgentContext`.

`schemas.py` defines a strict discriminated command union. `services/commands.py` computes validated SQL effects without committing. `coordinator.py` opens an isolated writer, acquires SQLite `BEGIN IMMEDIATE`, checks an owner-scoped idempotency key and applies the command. Its original canonical payload, evidence references, SQL effects and receipt commit together. A reused key with changed input fails. A failed extension rolls back the entire command. An unresolved browser save can be fenced by a cancellation receipt, preventing a late request from posting.

Money is accepted as plain decimal strings, converted to integer minor units and stored in integer columns. Every currency must balance independently. Allocation distributes quotient/remainder units deterministically from the first installment. The original purchase is recognized in the journal; installment schedules describe obligations rather than recording the expense again.

Posted events, posting lines, schedules, settlements, receipts, import originals, reconciliation records and investment observations are immutable. SQLite triggers protect these invariants even through direct SQL. Corrections use linked reversal events. Accounts retain their currency/type semantics after use. Closed accounting periods reject backdated postings.

Credit-card calendars retain dated editions. Effective statement boundaries use actual statement overrides when provided, otherwise the configured rules. Reports recompute effective schedule dates without rewriting the original purchase. Each report reads one database snapshot. Python integer aggregation avoids overflowing SQLite SUM when many individually valid amounts accumulate.

Reports expose bounded journal/schedule pages, per-currency totals, credit-card billed balances, unpaid obligations, business balances/aging, reconciliations, holdings and forecasts. Forecast estimates remain distinct from confirmed obligations and actual journals.

The standalone edition has one login/owner. Library callers may scope multiple owner IDs, but the browser host is not a multi-tenant service. Only SQLite is supported. Schema creation is idempotent; this initial version has no general-purpose schema-upgrade migration framework. Back up before upgrades.

Igor's source admission and derived-memory integration remain in SPEDA. Standalone receipts retain the exact authorized source command, and `after_apply` is a transaction-local extension hook for a host's derived views. A hook must not commit or perform model calls inside the writer transaction.
