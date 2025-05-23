"""Fix lat/long again

Revision ID: 158aece2d1b6
Revises: 71f652efa744
Create Date: 2025-05-13 10:31:33.733957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '158aece2d1b6'
down_revision: Union[str, None] = '71f652efa744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
