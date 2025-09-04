"""change id to uuid

Revision ID: change_id_to_uuid
Revises: add_missing_user_fields
Create Date: 2025-07-27 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'change_id_to_uuid'
down_revision: Union[str, Sequence[str], None] = 'add_missing_user_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем default значение и sequence
    op.execute('ALTER TABLE users ALTER COLUMN id DROP DEFAULT')
    op.execute('DROP SEQUENCE IF EXISTS users_id_seq')

    # Изменяем тип id с INTEGER на UUID
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE UUID USING gen_random_uuid()')

    # Добавляем новый default для UUID
    op.execute('ALTER TABLE users ALTER COLUMN id SET DEFAULT gen_random_uuid()')


def downgrade() -> None:
    """Downgrade schema."""
    # Изменяем тип id обратно с UUID на INTEGER
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE INTEGER USING (id::text)::integer')