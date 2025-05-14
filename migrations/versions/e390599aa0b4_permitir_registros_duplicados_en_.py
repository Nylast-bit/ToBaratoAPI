"""Permitir registros duplicados en UsuarioProveedor

Revision ID: e390599aa0b4
Revises: d09d3861f119
Create Date: 2025-05-13 15:05:45.237109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e390599aa0b4'
down_revision: Union[str, None] = 'd09d3861f119'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Eliminar la clave primaria compuesta
    op.drop_constraint('UsuarioProveedor_pkey', 'UsuarioProveedor', type_='primary')

    # Agregar la columna 'Id' como nueva clave primaria
    

    op.add_column('UsuarioProveedor', sa.Column('IdUsuarioProveedor', sa.Integer(), nullable=False))
    op.create_primary_key('UsuarioProveedor_pkey', 'UsuarioProveedor', ['IdUsuarioProveedor'])
    # No eliminamos las restricciones de FK, ya que queremos mantenerlas
    # Si las claves foráneas están definidas como deben ser, no es necesario hacer más aquí.


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar la clave primaria 'Id'
    op.drop_constraint('UsuarioProveedor_pkey', 'UsuarioProveedor', type_='primary')
    op.drop_column('UsuarioProveedor', 'Id')

    # Restaurar la clave primaria compuesta original
    op.create_primary_key('UsuarioProveedor_pkey', 'UsuarioProveedor', ['IdProveedor', 'IdUsuario'])
