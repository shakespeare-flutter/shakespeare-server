"""raw

Revision ID: b9f5de5b8447
Revises: 6206ff1bac24
Create Date: 2023-05-23 11:13:27.215532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9f5de5b8447'
down_revision = '6206ff1bac24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'Book',
        sa.Column('raw', sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_column('Book', 'raw')
    pass
