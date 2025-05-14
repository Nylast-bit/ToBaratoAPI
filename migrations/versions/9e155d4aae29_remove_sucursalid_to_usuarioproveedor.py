"""remove SucursalId to UsuarioProveedor

Revision ID: 9e155d4aae29
Revises: fb228b79d012
Create Date: 2025-05-13 09:17:04.096075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e155d4aae29'
down_revision: Union[str, None] = 'fb228b79d012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
