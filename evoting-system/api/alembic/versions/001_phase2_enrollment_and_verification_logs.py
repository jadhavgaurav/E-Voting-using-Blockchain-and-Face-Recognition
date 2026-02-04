"""Phase 2: enrollment_templates and verification_logs

Revision ID: 001
Revises:
Create Date: Phase 2 initial

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enrollment_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("voter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("algorithm_version", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_enrollment_templates_voter_id", "enrollment_templates", ["voter_id"], unique=True)

    op.create_table(
        "verification_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("voter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("election_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("face_score", sa.Float(), nullable=False),
        sa.Column("pad_result", sa.String(32), nullable=False),
        sa.Column("pad_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_verification_logs_request_id", "verification_logs", ["request_id"], unique=True)
    op.create_index("ix_verification_logs_voter_id", "verification_logs", ["voter_id"], unique=False)
    op.create_index("ix_verification_logs_voter_created", "verification_logs", ["voter_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_verification_logs_voter_created", table_name="verification_logs")
    op.drop_index("ix_verification_logs_voter_id", table_name="verification_logs")
    op.drop_index("ix_verification_logs_request_id", table_name="verification_logs")
    op.drop_table("verification_logs")
    op.drop_index("ix_enrollment_templates_voter_id", table_name="enrollment_templates")
    op.drop_table("enrollment_templates")
