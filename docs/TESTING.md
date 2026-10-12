# Verification

The accounting suite exercises integer-money allocation properties, rejection of invalid decimals, balanced native currencies, explicit FX, isolated transactions, identical retries, concurrent retries, changed-key rejection, immutable SQL history, reversal dependencies, partial settlements, period closure, calendar editions, shifted statement boundaries, source-preserving atomic imports, stale reconciliations, and investment cost allocation.

HTTP tests exercise password setup/login/change, hashed one-use setup tokens, session revocation and API scope, CSRF/Origin rejection, persistent throttling, secret-free validation, public confined compiled assets and uncertain-save resolution. Application lifecycle tests exercise the independently assembled standalone host.

`ui/tests/api.test.mjs` tests retry identity across timeouts/refresh and lost-form recovery without storing financial data. `ui/tests/browser.mjs` drives a real Chromium browser through first password setup, books/accounts, card configuration, an installment purchase, statement reporting, password change and a mobile viewport. It uses synthetic values and writes screenshots outside the checkout.

To run browser tests after building the UI:

```sh
# Terminal 1, root of repo:
PYTHONDONTWRITEBYTECODE=1 python tests/browser_server.py
# Terminal 2:
cd ui
npx playwright install chromium
node tests/browser.mjs
```

The fixture server creates a fresh database in an OS temporary directory. Its API key and passwords are test-only fixtures. Do not deploy it or point the browser test at a real owner database.
