"""Agregar columna IdUsuarioProveedor

Revision ID: f4e282ba9038
Revises: e390599aa0b4
Create Date: 2025-05-13 15:18:21.118513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4e282ba9038'
down_revision: Union[str, None] = 'e390599aa0b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('UsuarioProveedor', sa.Column('IdUsuarioProveedor', sa.Integer(), nullable=False))
    op.create_primary_key('UsuarioProveedor_pkey', 'UsuarioProveedor', ['IdUsuarioProveedor'])

def downgrade() -> None:
    op.drop_constraint('UsuarioProveedor_pkey', 'UsuarioProveedor', type_='primary')
    op.drop_column('UsuarioProveedor', 'IdUsuarioProveedor')

