# secure-file-sharing-system

**Secure File Sharing System** is a Cryptography and Network Security college
project. It is one web application (React frontend, FastAPI backend,
PostgreSQL database) built by ten members. Each member owns one security
module.

> **Project status: foundation only.** The architecture, database schema, API
> contracts and skeleton are in place. **None of the ten security modules is
> implemented yet.** Every module endpoint returns `501 not_implemented`, and
> the Module Status page in the UI shows exactly what is built.

| # | Module | Status |
|---|---|---|
| 1 | Authentication & Argon2id password security | not implemented |
| 2 | AES-256-GCM file encryption | not implemented |
| 3 | RSA-OAEP key management | not implemented |
| 4 | RSA-PSS digital signatures | not implemented |
| 5 | Secure file sharing & access control | not implemented |
| 6 | Tamper-evident audit logging | not implemented |
| 7 | Isolation Forest anomaly detection | not implemented |
| 8 | LLM-based security event analysis | not implemented |
| 9 | Cryptographic verification & attack testing | not implemented |
| 10 | HTTPS/TLS & transport security | not implemented |

## Documentation

| Doc | Contents |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Repository layout, request pipelines, database design, module interfaces, frontend, testing |
| [docs/api-contracts.md](docs/api-contracts.md) | Every endpoint, request/response schema and error code |
| [docs/security-design.md](docs/security-design.md) | Threat model and the exact cryptographic parameters for each module |
| [docs/module-ownership.md](docs/module-ownership.md) | Who owns which files, task dependencies, schedule |
| [docs/integration-guide.md](docs/integration-guide.md) | Setup, Git workflow, how to implement and integrate a module |

## Tech stack

React 19 + Vite + Tailwind CSS v4 · Python 3.12 + FastAPI · PostgreSQL 16 ·
SQLAlchemy 2 + Alembic · Pytest + HTTPX · Vitest · scikit-learn · Docker Compose · nginx (TLS)

## Quick start (local, without Docker)

Prerequisites: Python 3.12+, Node 20+. Run the backend against PostgreSQL;
SQLite is fine for tests only.

```bash
cp .env.example .env        # then fill in the empty secrets (instructions are inside the file)

cd backend
python -m venv .venv
.venv/Scripts/activate       # Windows (Git Bash: source .venv/Scripts/activate)
# source .venv/bin/activate  # macOS / Linux
pip install -r requirements-dev.txt
pytest                       # backend tests
alembic upgrade head         # needs DATABASE_URL pointing at a running PostgreSQL
uvicorn --factory app.main:create_app --reload

cd ../frontend
npm install
npm test                     # frontend tests
npm run dev                  # http://localhost:5173 (proxies /api to :8000)
```

API docs while the backend runs: http://localhost:8000/api/docs

## Quick start (Docker Compose)

```bash
cp .env.example .env         # fill in POSTGRES_PASSWORD, JWT_SECRET_KEY, MASTER_KEY_ENCRYPTION_KEY, AUDIT_HMAC_KEY
docker compose up --build    # http://localhost:5173
```

HTTPS through the nginx proxy (Module 10, not yet verified):

```bash
sh scripts/gen-dev-certs.sh
docker compose --profile tls up --build    # https://localhost
```

## Security rules for contributors

- Never commit `.env`, private keys, certificates or API keys. `.gitignore`
  blocks the common cases, but check `git status` before every commit anyway.
- Never mark a module implemented, or claim a feature works, until its code
  and tests are merged.
- All work goes through pull requests. Nobody pushes directly to `main`.
