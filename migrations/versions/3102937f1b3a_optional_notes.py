"""Optional notes

Revision ID: 3102937f1b3a
Revises: 12d9b0374b03
Create Date: 2024-11-21 16:25:49.416088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3102937f1b3a'
down_revision: Union[str, None] = '12d9b0374b03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contacts', 'notes',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contacts', 'notes',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    # ### end Alembic commands ###
