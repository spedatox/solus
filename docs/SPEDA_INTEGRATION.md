# A module of SPEDA Mark VI

Solus is the accounting subsystem of SPEDA Mark VI, the backend of a personal executive digital assistant. Igor hosts the original engine, Sentinel is its finance agent, and the standalone Solus UI gives the owner direct authenticated access to the same accounting commands and reports.

In SPEDA, Solus is registered as a Tier-1 Python capability. Sentinel submits strict commands rather than editing markdown ledgers or calculating balances through language-model reasoning. Igor's financial coordinator commits source evidence, the SQL ledger, mechanically derived memory views and retry receipts together. Existing legacy records remain separate until an explicit reviewed migration.

This repository publishes the module as a runnable reference and portfolio edition. It includes the ledger, schedules, statements, imports, reconciliation, investment records, browser security and Vue UI. A minimal independent host replaces SPEDA-specific orchestration, source admission and memory projections. The proposal adapter demonstrates how another trusted host can connect an assistant without making model output authoritative.

The integrated module remains in [SPEDA Mark VI](https://github.com/spedatox/speda-mark6), under `packages/igor/app/services/solus`, with models/schemas/routers/skills in their Igor layers and the UI in `packages/solus`. Nothing was moved out of SPEDA. Changes in this separately published edition do not automatically update the production integration; they must be reviewed and synchronized deliberately.

Module concept and architecture: Ahmet Erol Bayrak. Development: AI-assisted engineering within SPEDA Mark VI.
