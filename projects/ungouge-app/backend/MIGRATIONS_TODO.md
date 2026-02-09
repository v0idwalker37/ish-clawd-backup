# Database Migrations — TODO

Alembic is already in `requirements.txt` but has **not been initialized** yet.
The app currently uses `Base.metadata.create_all()` on startup (in `main.py`),
which only creates new tables — it cannot alter existing ones.

## Setup Steps

1. **Initialize Alembic** (run once from `backend/`):
   ```bash
   alembic init alembic
   ```

2. **Configure `alembic.ini`**:
   - Set `sqlalchemy.url` to match `DATABASE_URL` env var
   - Or better: override it in `alembic/env.py` from `os.environ`

3. **Edit `alembic/env.py`**:
   - Import `Base` from `models.database`
   - Set `target_metadata = Base.metadata`
   - Configure async engine support (we use `aiosqlite`):
     ```python
     from sqlalchemy.ext.asyncio import create_async_engine
     ```

4. **Generate initial migration** (snapshot current schema):
   ```bash
   alembic revision --autogenerate -m "initial schema"
   ```

5. **Remove `create_all()` from `main.py`** lifespan once migrations are active.

6. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

## New Tables Added

The `token_blacklist` table was added via SQLAlchemy model (`BlacklistedToken`
in `services/token_blacklist.py`). It will be auto-created by `create_all()`
for now, but should be captured in the first Alembic migration.

## Production Workflow

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "describe change"

# Review the generated migration file!
# Then apply:
alembic upgrade head
```

Always review auto-generated migrations before applying — Alembic can miss
renames, data migrations, and some constraint changes.
