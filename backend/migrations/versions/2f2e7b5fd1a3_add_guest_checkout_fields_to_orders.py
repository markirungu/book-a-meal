"""add guest checkout fields to orders

Revision ID: 2f2e7b5fd1a3
Revises: da14ab27cc6d
Create Date: 2026-04-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f2e7b5fd1a3'
down_revision = 'da14ab27cc6d'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('orders', 'customer_id', existing_type=sa.Integer(), nullable=True)
    op.add_column('orders', sa.Column('guest_name', sa.String(length=120), nullable=True))
    op.add_column('orders', sa.Column('guest_email', sa.String(length=120), nullable=True))
    op.add_column('orders', sa.Column('guest_phone', sa.String(length=40), nullable=True))
    op.add_column('orders', sa.Column('delivery_info', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('orders', 'delivery_info')
    op.drop_column('orders', 'guest_phone')
    op.drop_column('orders', 'guest_email')
    op.drop_column('orders', 'guest_name')
    op.alter_column('orders', 'customer_id', existing_type=sa.Integer(), nullable=False)
