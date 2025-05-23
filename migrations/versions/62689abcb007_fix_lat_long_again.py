"""Fix lat/long again

Revision ID: 62689abcb007
Revises: 158aece2d1b6
Create Date: 2025-05-13 14:59:53.865769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62689abcb007'
down_revision: Union[str, None] = '158aece2d1b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
