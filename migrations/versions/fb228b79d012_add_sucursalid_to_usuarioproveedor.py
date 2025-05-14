"""add SucursalId to UsuarioProveedor

Revision ID: fb228b79d012
Revises: 630a3d865f96
Create Date: 2025-05-13 09:03:57.142365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb228b79d012'
down_revision: Union[str, None] = '630a3d865f96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
