"""Align schema with the SQLAlchemy models

Revision ID: 7a1c9f2d4b6e
Revises: be9906a7d2c3
Create Date: 2026-11-01 12:00:00.000000

The original initial migration was generated against an earlier model draft:
``model_versions`` used ``model_name``/``model_metadata`` and
``monitoring_logs`` used ``model_version_id`` while the ORM expects
``name``/``version_metadata`` and ``version_id``. This migration brings an
existing database to the current schema and adds the newer monitoring and
settings tables.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "7a1c9f2d4b6e"
down_revision = "be9906a7d2c3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("full_name", sa.String(length=100), nullable=True))

    with op.batch_alter_table("model_versions") as batch_op:
        batch_op.alter_column("model_name", new_column_name="name", existing_type=sa.String())
        batch_op.alter_column(
            "model_metadata",
            new_column_name="version_metadata",
            existing_type=sa.JSON(),
        )

    op.create_index("uq_model_version", "model_versions", ["name", "version"], unique=True)

    with op.batch_alter_table("monitoring_logs") as batch_op:
        batch_op.alter_column(
            "model_version_id",
            new_column_name="version_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_index("ix_monitoring_logs_metric_name", ["metric_name"], unique=False)
        batch_op.create_index("ix_monitoring_logs_timestamp", ["timestamp"], unique=False)

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.create_index("ix_audit_logs_timestamp", ["timestamp"], unique=False)

    with op.batch_alter_table("compliance_records") as batch_op:
        batch_op.create_index(
            "ix_compliance_records_regulation_type", ["regulation_type"], unique=False
        )

    op.create_table(
        "system_metric_samples",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_system_metric_samples_id", "system_metric_samples", ["id"], unique=False)
    op.create_index(
        "ix_system_metric_samples_resource",
        "system_metric_samples",
        ["resource"],
        unique=False,
    )
    op.create_index(
        "ix_system_metric_samples_timestamp",
        "system_metric_samples",
        ["timestamp"],
        unique=False,
    )

    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade():
    op.drop_table("system_settings")

    op.drop_index("ix_system_metric_samples_timestamp", table_name="system_metric_samples")
    op.drop_index("ix_system_metric_samples_resource", table_name="system_metric_samples")
    op.drop_index("ix_system_metric_samples_id", table_name="system_metric_samples")
    op.drop_table("system_metric_samples")

    with op.batch_alter_table("compliance_records") as batch_op:
        batch_op.drop_index("ix_compliance_records_regulation_type")

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_index("ix_audit_logs_timestamp")

    with op.batch_alter_table("monitoring_logs") as batch_op:
        batch_op.drop_index("ix_monitoring_logs_timestamp")
        batch_op.drop_index("ix_monitoring_logs_metric_name")
        batch_op.alter_column(
            "version_id",
            new_column_name="model_version_id",
            existing_type=sa.Integer(),
            nullable=True,
        )

    op.drop_index("uq_model_version", table_name="model_versions")

    with op.batch_alter_table("model_versions") as batch_op:
        batch_op.alter_column(
            "version_metadata",
            new_column_name="model_metadata",
            existing_type=sa.JSON(),
        )
        batch_op.alter_column("name", new_column_name="model_name", existing_type=sa.String())

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("full_name")
