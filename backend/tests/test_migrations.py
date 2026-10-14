"""Alembic history must be linear and match the SQLAlchemy models exactly."""

from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from alembic import command
from app.models import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def alembic_cfg(tmp_path):
    db_url = f"sqlite:///{(tmp_path / 'migrations.db').as_posix()}"
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.attributes["configure_logger"] = False
    return cfg, db_url


def test_single_migration_head(alembic_cfg):
    cfg, _ = alembic_cfg
    heads = ScriptDirectory.from_config(cfg).get_heads()
    assert len(heads) == 1, f"Multiple Alembic heads {heads}: rebase and fix down_revision"


def test_upgrade_matches_models_and_downgrade_cleans_up(alembic_cfg):
    cfg, db_url = alembic_cfg
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = compare_metadata(ctx, Base.metadata)
    assert diff == [], f"Models and migrations differ; add a migration: {diff}"

    command.downgrade(cfg, "base")
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}
    engine.dispose()
