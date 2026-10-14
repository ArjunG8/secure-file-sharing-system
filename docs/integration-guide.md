# Integration Guide

How ten people build one application without stepping on each other.

## 1. One-time setup (every member)

```bash
git clone https://github.com/ArjunG8/secure-file-sharing-system.git
cd secure-file-sharing-system
cp .env.example .env            # then fill in secrets (see security-design.md §3)

# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest                           # must be green before you start

# Frontend
cd ../frontend
npm install
npm test
```

Full stack with Docker: `docker compose up --build` (add `--profile tls` once
M10's proxy and dev certs exist).

## 2. GitHub collaboration workflow

1. **Never commit to `main`.** The Lead enables branch protection on `main`:
   require a PR, 1 approving review, passing CI, linear history.
2. Branch from latest `main`: `git switch main && git pull && git switch -c m3/rsa-oaep-wrap`.
3. Small PRs (≤ ~400 lines). One concern per PR.
4. Commit messages: `m3: add RSA-OAEP key wrapping` (module prefix + imperative).
5. Before pushing: `pytest` and `npm test` pass locally; rebase on `main`
   (`git pull --rebase origin main`).
6. Open the PR using the template; link the issue; fill the security checklist.
7. Reviewers: CODEOWNERS are auto-requested. Cross-module changes need the
   other module owner's approval.
8. Squash-merge. Delete the branch.
9. Track work in GitHub Issues with labels `module:m1` … `module:m10`,
   `type:feature`, `type:bug`, `type:test`, `blocked`.

## 3. Implementing your module — checklist

1. Read your section in `security-design.md` and `api-contracts.md`.
2. Implement `backend/app/modules/<name>/service.py` functions (replace the
   `NotImplementedFeature` raises). Keep the signatures; if you must change
   one, update `architecture.md` §4 and notify consumers.
3. Implement `router.py` endpoints using your `schemas.py` models.
4. Call `audit.service.record_event(...)` for every security-relevant action.
5. Write tests in `backend/tests/modules/test_<name>.py` (happy + negative).
6. Remove your endpoints from the list in `backend/tests/test_not_implemented.py`.
7. Set `implemented=True` in your module's `__init__.py` **only when** all of
   your endpoints work and are tested.
8. Build your frontend page in `frontend/src/features/<name>/`.

## 4. Integration points (where modules touch)

### Adding a route (backend)
Already done — `app/api/router.py` includes every module's `router`. You only
add endpoints inside your own `router.py`.

### Adding a page (frontend)
Your page component is already registered in `src/App.jsx` and in the nav.
Edit your page file; only touch `App.jsx` if you need an extra route.

### Adding/changing a table
1. Edit **your** model file in `app/models/`.
2. Generate a migration against a running PostgreSQL:
   ```bash
   cd backend
   alembic revision --autogenerate -m "m5 add grant note column"
   ```
   Rename the file to `NNNN_m5_add_grant_note_column.py`, review it by hand.
3. Before opening the PR: `git pull --rebase origin main`, then make sure
   `alembic heads` shows **one** head. If two, set your `down_revision` to the
   other head.
4. `pytest tests/test_migrations.py` must pass (detects model/migration drift).

### Calling another module
```python
from app.modules.keys import service as keys_service
from app.modules.audit import service as audit_service
from app.modules.audit.schemas import AuditEventIn

wrapped = keys_service.wrap_key_for_user(db, user.id, file_key)
audit_service.record_event(db, AuditEventIn(event_type="file.upload", actor_user_id=user.id, ...))
```

### Stubs and the audit hook
Until M6 lands, `audit.service.record_event` logs a warning and returns
`None` — it does **not** persist anything, and the warning says so. All other
unimplemented service functions raise `NotImplementedFeature`, which the API
returns as `501 not_implemented` with the owning module number.

### Mocking a dependency that isn't merged yet
```python
def test_upload_wraps_key(client, monkeypatch):
    monkeypatch.setattr(keys_service, "wrap_key_for_user", lambda db, uid, k: WrappedKey(b"x", uuid4()))
```

## 5. Definition of done (per module)

- [ ] All endpoints in `api-contracts.md` for the module implemented
- [ ] Unit + API tests, including negative/attack cases, pass in CI
- [ ] No secrets in code; config via `app.core.config.get_settings()`
- [ ] Audit events emitted
- [ ] Frontend page works against the real backend
- [ ] `MODULE_INFO.implemented = True`
- [ ] Short write-up of design + limitations added to `docs/modules/mN-<name>.md`

## 6. Final integration (Week 4)

1. Lead freezes contracts; only bug-fix PRs.
2. `docker compose --profile tls up --build` on a clean machine.
3. Run the demo script: register two users → upload → share → download as
   recipient → revoke → tamper a blob on disk and show verification failure
   → edit an audit row and show chain break → run anomaly scoring → run LLM
   analysis (if a provider key is configured) → show TLS/HSTS in browser.
4. M9 runs the full `tests/security` suite and records results for the report.
