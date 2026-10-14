# Module Ownership

Fill in the **Member** column with real names and GitHub usernames, then
update `.github/CODEOWNERS` to match. The **Lead** (repository owner) owns the
shared files and reviews every PR touching them.

| # | Module | Member | GitHub | Branch prefix |
|---|---|---|---|---|
| L | Integration lead (shared files) | _TBD_ (repo owner) | @ArjunG8 | `chore/` |
| 1 | Authentication & Argon2id | _TBD_ | | `m1/` |
| 2 | AES-256-GCM file encryption | _TBD_ | | `m2/` |
| 3 | RSA-OAEP key management | _TBD_ | | `m3/` |
| 4 | RSA-PSS digital signatures | _TBD_ | | `m4/` |
| 5 | Secure sharing & access control | _TBD_ | | `m5/` |
| 6 | Tamper-evident audit logging | _TBD_ | | `m6/` |
| 7 | Isolation Forest anomaly detection | _TBD_ | | `m7/` |
| 8 | LLM security event analysis | _TBD_ | | `m8/` |
| 9 | Crypto verification & attack testing | _TBD_ | | `m9/` |
| 10 | HTTPS/TLS & transport security | _TBD_ | | `m10/` |

(The Lead can also be one of the ten module members.)

## Exact file ownership

A member may freely edit files they own. Editing someone else's file requires
their approving review. "Lead" files are shared integration points: change
them in small PRs.

### Shared (Lead)
```
backend/app/main.py
backend/app/core/*                       (config.py, database.py, errors.py, modules.py)
backend/app/api/router.py
backend/app/schemas/common.py
backend/app/models/__init__.py, backend/app/models/base.py
backend/alembic/env.py, backend/alembic.ini, backend/alembic/versions/0001_initial_schema.py
backend/tests/conftest.py, test_health.py, test_api_contract.py, test_migrations.py,
  test_models.py, test_config.py, test_not_implemented.py
backend/requirements*.txt, backend/pyproject.toml, backend/Dockerfile
frontend/src/main.jsx, App.jsx, index.css, api/client.js, components/**,
  features/status/**
frontend/package.json, vite.config.js, frontend/Dockerfile
docker-compose.yml, .env.example, .gitignore, README.md, docs/**, .github/**
```
Adding a dependency to `requirements.txt` / `package.json` is allowed for any
member — keep the PR diff to that one line plus the lockfile.

### Per module

| # | Backend | Model file(s) | Frontend | Tests |
|---|---|---|---|---|
| 1 | `app/modules/auth/**`, `app/api/deps.py` | `models/user.py` (`User`, `AuthSession`) | `features/auth/**`, `context/AuthContext.jsx` | `tests/modules/test_auth.py` |
| 2 | `app/modules/encryption/**` | `models/file.py` (except signature columns) | `features/files/**` | `tests/modules/test_encryption.py` |
| 3 | `app/modules/keys/**` | `models/key.py` (`UserKey`) | `features/keys/**` | `tests/modules/test_keys.py` |
| 4 | `app/modules/signatures/**` | `models/file.py` columns `signature`, `signature_algorithm`, `signing_key_id` | `features/signatures/**` | `tests/modules/test_signatures.py` |
| 5 | `app/modules/sharing/**` | `models/share.py` (`FileAccessGrant`) | `features/sharing/**` | `tests/modules/test_sharing.py` |
| 6 | `app/modules/audit/**` | `models/audit.py` (`AuditLog`) | `features/audit/**` | `tests/modules/test_audit.py` |
| 7 | `app/modules/anomaly/**` | `models/anomaly.py` (`AnomalyDetection`) | `features/anomaly/**` | `tests/modules/test_anomaly.py` |
| 8 | `app/modules/llm_analysis/**` | `models/analysis.py` (`SecurityAnalysis`) | `features/analysis/**` | `tests/modules/test_llm_analysis.py` |
| 9 | `app/modules/verification/**` | `models/verification.py` (`VerificationRun`) | `features/verification/**` | `tests/security/**`, `tests/modules/test_verification.py` |
| 10 | `app/modules/transport/**`, `infra/nginx/**`, `scripts/gen-dev-certs.sh` | – | `features/transport/**` | `tests/modules/test_transport.py` |

Each member also owns any Alembic migration they add for their tables
(`alembic/versions/NNNN_mX_<description>.py`).

## Dependencies between tasks

```
            ┌──────────── M10 (independent; integrate last) ───────────┐
            │                                                          │
 M6 audit ──┼──▶ everyone calls record_event (stub-safe from day 1)    │
            │                                                          │
 M1 auth ───┼──▶ get_current_user ──▶ M2, M3, M4, M5, M6, M7, M8, M9   │
            │                                                          │
 M3 keys ───┼──▶ wrap/unwrap ──▶ M2 upload/download, M5 sharing        │
            │      └─▶ signing keys ──▶ M4                             │
 M2 enc ────┼──▶ encrypt/decrypt ──▶ M5, M9                            │
 M4 sig ────┼──▶ sign/verify ──▶ M2 download, M9                       │
 M5 share ──┼──▶ require_access ──▶ M2 download/list, M4, M9           │
 M6 audit ──┴──▶ events ──▶ M7 features ──▶ M8 analysis                │
                                     M9 tests everything ◀─────────────┘
```

### Suggested schedule (adjust to your deadline)

| Phase | Work | Can start immediately? |
|---|---|---|
| Week 1 | **M1** hashing + register/login; **M3** keygen/wrap/unwrap (pure functions + unit tests); **M2** `encrypt_bytes`/`decrypt_bytes` (pure); **M4** sign/verify (pure); **M6** hash chain + `record_event`; **M10** nginx + certs + headers middleware; **M7** feature extraction on synthetic data; **M8** redaction + prompt builder (provider disabled); **M9** write failing/`skip` attack tests from the spec | Yes — all pure-crypto work needs no other module |
| Week 2 | M1 `get_current_user` merged ⇒ M2 upload/download endpoints using M3+M4; M5 grants + `require_access`; M6 `/audit` endpoints | After M1 + M3 |
| Week 3 | M5 sharing endpoints; M7 trains on real audit data; M8 analysis over audit + anomalies; M9 enables attack tests as features land | After M2, M5, M6 |
| Week 4 | Frontend pages for every module, end-to-end run via `docker compose --profile tls up`, report | — |

**Unblocking rule:** if you need another module's function before it is
merged, code against its `service.py` signature and mock it in your tests
(`monkeypatch.setattr(...)`). Do not write your own copy of their logic.
