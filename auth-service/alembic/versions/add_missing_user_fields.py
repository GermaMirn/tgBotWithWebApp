"""add missing user fields

Revision ID: add_missing_user_fields
Revises: 13c880ed3d4e
Create Date: 2025-07-27 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_missing_user_fields'
down_revision: Union[str, Sequence[str], None] = '13c880ed3d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем недостающие поля
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True, server_default='student'))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, server_default='Europe/Kaliningrad'))


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем добавленные поля
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'role')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'email')
    op.drop_column('users', 'phone_number')