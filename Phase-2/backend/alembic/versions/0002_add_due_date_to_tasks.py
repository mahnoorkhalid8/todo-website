"""Add due_date column to tasks table

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-07 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add due_date column to tasks table
    op.add_column('task', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove due_date column from tasks table
    op.drop_column('task', 'due_date')