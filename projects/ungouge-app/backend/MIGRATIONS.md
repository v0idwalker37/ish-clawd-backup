# Database Migrations — UnGouge.ai

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations.

## Quick Reference

```bash
# Apply all pending migrations
cd backend
alembic upgrade head

# Create a new migration (after changing models)
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade <revision_id>

# Show current migration state
alembic current

# Show migration history
alembic history --verbose
```

## How It Works

- **Models live in:** `models/database.py` and `services/token_blacklist.py`
- **Migration scripts live in:** `alembic/versions/`
- **Alembic config:** `alembic.ini` + `alembic/env.py`
- **Database URL:** read from `DATABASE_URL` env var (defaults to `sqlite+aiosqlite:///./ungouge.db`)

When you modify a SQLAlchemy model, run `alembic revision --autogenerate -m "description"` to generate a migration script, then review it before applying.

## Development Workflow

1. **Modify models** in `models/database.py`
2. **Generate migration:**
   ```bash
   alembic revision --autogenerate -m "add foo column to users"
   ```
3. **Review the generated file** in `alembic/versions/` — autogenerate is not perfect, check:
   - Server defaults are correct
   - Index names make sense
   - `render_as_batch=True` handles SQLite ALTER TABLE limitations
4. **Apply:**
   ```bash
   alembic upgrade head
   ```
5. **Commit** the migration file alongside your model changes

## Production Migration Procedure

### Pre-Migration Checklist

- [ ] Migration tested locally against a copy of production data
- [ ] Migration tested in staging environment
- [ ] Database backup completed (see below)
- [ ] Downtime window communicated (if needed)
- [ ] Rollback plan verified

### Backup Steps

```bash
# PostgreSQL
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# SQLite
cp ungouge.db ungouge_backup_$(date +%Y%m%d_%H%M%S).db
```

### Deploy

```bash
# 1. Take backup (see above)

# 2. Check current state
alembic current

# 3. Preview what will run
alembic upgrade head --sql   # Dry-run: prints SQL without executing

# 4. Apply migrations
alembic upgrade head

# 5. Verify
alembic current
# Run a quick smoke test against the API
```

### Rollback

```bash
# Roll back the last migration
alembic downgrade -1

# If that fails, restore from backup:
# PostgreSQL:
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -c backup_YYYYMMDD_HHMMSS.dump

# SQLite:
cp ungouge_backup_YYYYMMDD_HHMMSS.db ungouge.db
```

## Existing Databases

If deploying Alembic against a database that was created by `Base.metadata.create_all()` (the current startup behavior in `main.py`), you need to stamp the database to tell Alembic the initial schema already exists:

```bash
# Mark the database as already at the initial migration
alembic stamp 0001
```

After stamping, future migrations will apply normally.

> **Recommended next step:** Once Alembic is managing schema, remove the
> `create_all()` call from `main.py`'s lifespan handler and rely solely on
> `alembic upgrade head` for schema management.

## SQLite Notes

- `render_as_batch=True` is enabled in `env.py` — this is required because SQLite doesn't support most `ALTER TABLE` operations natively
- Alembic's batch mode recreates the table behind the scenes to apply changes
- This is transparent but means migrations may be slower on large tables
