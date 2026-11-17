"""ai safety flag and feedback details

Adds:
- ai_suggestions.input_flagged  (instruction-like text was removed before analysis)
- ai_feedback.actor, ai_feedback.comment (who gave the feedback, optional note)
- CHECK constraints on ai_feedback final values

Revision ID: a3c1e7d2b9f0
Revises: f49711cdbf1a
Create Date: 2026-11-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3c1e7d2b9f0'
down_revision: Union[str, Sequence[str], None] = 'f49711cdbf1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ai_suggestions',
                  sa.Column('input_flagged', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('ai_feedback', sa.Column('actor', sa.String(length=100), nullable=True))
    op.add_column('ai_feedback', sa.Column('comment', sa.Text(), nullable=True))
    op.create_check_constraint('ck_feedback_priority', 'ai_feedback',
                               "final_priority IN ('Low','Medium','High')")
    op.create_check_constraint('ck_feedback_category', 'ai_feedback',
                               "final_category IN ('Hardware','Software','Network','Access','Other')")


def downgrade() -> None:
    op.drop_constraint('ck_feedback_category', 'ai_feedback', type_='check')
    op.drop_constraint('ck_feedback_priority', 'ai_feedback', type_='check')
    op.drop_column('ai_feedback', 'comment')
    op.drop_column('ai_feedback', 'actor')
    op.drop_column('ai_suggestions', 'input_flagged')
