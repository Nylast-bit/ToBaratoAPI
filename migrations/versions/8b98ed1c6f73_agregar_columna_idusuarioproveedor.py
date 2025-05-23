"""Agregar columna IdUsuarioProveedor

Revision ID: 8b98ed1c6f73
Revises: f4e282ba9038
Create Date: 2025-05-13 16:47:34.475585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b98ed1c6f73'
down_revision: Union[str, None] = 'f4e282ba9038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
