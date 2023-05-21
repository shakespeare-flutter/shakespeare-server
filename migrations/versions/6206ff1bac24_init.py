"""init

Revision ID: 6206ff1bac24
Revises: 
Create Date: 2023-05-20 18:12:32.274057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6206ff1bac24'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'Book',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('identifier', sa.String, nullable=False),
        sa.Column('language', sa.String, nullable=False),
        sa.Column('path', sa.String, nullable=True),
        sa.Column('result', sa.String, nullable=True)
    )

def downgrade() -> None:
    op.drop_table('Book')
