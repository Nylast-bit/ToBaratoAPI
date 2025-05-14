"""ID PK en Usuario Proveedor

Revision ID: d09d3861f119
Revises: 62689abcb007
Create Date: 2025-05-13 15:01:02.587177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd09d3861f119'
down_revision: Union[str, None] = '62689abcb007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
