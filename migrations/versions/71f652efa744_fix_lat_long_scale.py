"""fix lat/long scale

Revision ID: 71f652efa744
Revises: 9e155d4aae29
Create Date: 2025-05-13 10:18:54.346957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71f652efa744'
down_revision: Union[str, None] = '9e155d4aae29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
