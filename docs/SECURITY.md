# Deployment and security

No default password is shipped. First-time setup needs the installation API key or a hashed, single-use token expiring after 15 minutes. Passwords use salted scrypt (N=131072, r=8, p=1). Login attempts are bounded by peer and installation. Password changes require the current password and revoke every browser session.

Sessions use random bearer tokens whose hashes are stored in SQLite. Browser cookies are HttpOnly, SameSite=Strict and Secure on HTTPS. Sessions expire after eight hours and after 30 minutes of inactivity; credential editions prevent password-change/login races. Cookie writes require CSRF tokens and reject an explicitly different Origin. Session cookies are scoped to `/solus/api/v1`; the public HTML/assets contain no financial records. API responses have no-store caching, credential validation omits submitted secrets, and the UI uses a strict self-only script/style CSP.

The host binds to loopback by default. Non-loopback HTTP requests are rejected. For remote deployment use a TLS proxy; configure uvicorn's trusted proxy addresses explicitly with `solus serve --host 0.0.0.0 --trusted-proxy ACTUAL_PROXY_IP`. Never trust wildcard forwarded headers. Restrict the backend port so only the proxy reaches it. The application does not install a TLS proxy for you.

Use a strong random `SOLUS_API_KEY` only when needed for trusted service integration. Browser setup can use the one-time CLI link without an API key. A service key authorizes owner operations and is not a least-privilege assistant credential.

The database is plaintext. Protect the data directory with filesystem permissions/full-disk encryption, limit host access and encrypt backups. Use SQLite's backup API or an offline stopped-server snapshot; copying only a live `.db` file can miss WAL transactions. Solus has no bundled off-host backup scheduler or credential recovery process. Keep setup links out of logs and screenshots.

This repository has automated security tests, not a claim of independent security certification. Report vulnerabilities privately through the repository owner's GitHub contact rather than publishing real financial data or credentials in an issue.
