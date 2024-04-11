"""Описание изменений

Revision ID: aef07c3194ce
Revises: 
Create Date: 2023-11-30 00:49:05.250323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aef07c3194ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('model_clothing',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('material_consumption', sa.Numeric(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('model_clothing', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_model_clothing_name'), ['name'], unique=False)

    op.create_table('pattern',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('sizes', sa.String(length=255), nullable=True),
    sa.Column('photo', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('additional_info_for_model_clothing',
    sa.Column('model_clothing_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('care_instructions', sa.Text(), nullable=True),
    sa.Column('materials', sa.Text(), nullable=True),
    sa.Column('cost', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['model_clothing_id'], ['model_clothing.id'], ),
    sa.PrimaryKeyConstraint('model_clothing_id')
    )
    with op.batch_alter_table('additional_info_for_model_clothing', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_additional_info_for_model_clothing_model_clothing_id'), ['model_clothing_id'], unique=True)

    op.create_table('model_pattern',
    sa.Column('model_clothing_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('pattern_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['model_clothing_id'], ['model_clothing.id'], ),
    sa.ForeignKeyConstraint(['pattern_id'], ['pattern.id'], ),
    sa.PrimaryKeyConstraint('model_clothing_id', 'pattern_id')
    )
    op.create_table('model_photo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('model_clothing_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['model_clothing_id'], ['model_clothing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('model_photo')
    op.drop_table('model_pattern')
    with op.batch_alter_table('additional_info_for_model_clothing', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_additional_info_for_model_clothing_model_clothing_id'))

    op.drop_table('additional_info_for_model_clothing')
    op.drop_table('pattern')
    with op.batch_alter_table('model_clothing', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_model_clothing_name'))

    op.drop_table('model_clothing')
    # ### end Alembic commands ###
