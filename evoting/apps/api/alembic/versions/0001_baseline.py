"""Baseline schema.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-10

This baseline creates the full schema from the application's SQLAlchemy metadata so
the initial migration cannot drift from the models. Subsequent migrations should be
generated with ``alembic revision --autogenerate`` and use explicit op.* calls.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from app.db import models  # noqa: F401  (register tables on Base.metadata)
from app.db.base import Base

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
