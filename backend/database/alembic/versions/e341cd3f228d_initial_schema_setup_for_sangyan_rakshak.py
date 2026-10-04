"""Initial schema setup for Sangyan Rakshak

Revision ID: e341cd3f228d
Revises: None
Create Date: 2026-10-04 10:40:12.716242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e341cd3f228d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'grievance_drafts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_session_id', sa.String(length=255), nullable=False),
        sa.Column('dispute_type', sa.String(length=100), nullable=False),
        sa.Column('intermediary_name', sa.String(length=255), nullable=False),
        sa.Column('amount_lost', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('incident_summary', sa.Text(), nullable=False),
        sa.Column('generated_scores_dossier', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'COPIED', 'SUBMITTED', name='grievancestatus', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('grievance_drafts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_grievance_drafts_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_grievance_drafts_user_session_id'), ['user_session_id'], unique=False)

    op.create_table(
        'sebi_intermediaries',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('reg_number', sa.String(length=64), nullable=False),
        sa.Column('entity_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.Enum('RIA', 'RA', 'StockBroker', 'PMS', name='intermediarycategory', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'EXPIRED', name='intermediarystatus', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('complaint_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('sebi_intermediaries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sebi_intermediaries_entity_name'), ['entity_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_sebi_intermediaries_reg_number'), ['reg_number'], unique=True)

    op.create_table(
        'unregistered_blacklists',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('entity_name', sa.String(length=255), nullable=False),
        sa.Column('channel_handle', sa.String(length=255), nullable=True),
        sa.Column('domain_or_apk', sa.String(length=255), nullable=True),
        sa.Column('scam_type', sa.Enum('DABBA_TRADING', 'FAKE_SEBI_SCHEME', 'GUARANTEED_RETURN', 'RECOVERY_FRAUD', name='scamtype', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('reporter_count', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('date_flagged', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('unregistered_blacklists', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_unregistered_blacklists_channel_handle'), ['channel_handle'], unique=False)
        batch_op.create_index(batch_op.f('ix_unregistered_blacklists_date_flagged'), ['date_flagged'], unique=False)
        batch_op.create_index(batch_op.f('ix_unregistered_blacklists_entity_name'), ['entity_name'], unique=False)

    op.create_table(
        'verification_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('input_hash', sa.String(length=64), nullable=False),
        sa.Column('input_type', sa.Enum('TEXT', 'AUDIO', 'IMAGE_OCR', 'APK', name='inputtype', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('extracted_reg_number', sa.String(length=64), nullable=True),
        sa.Column('extracted_upi', sa.String(length=255), nullable=True),
        sa.Column('verdict', sa.Enum('SAFE', 'SUSPICIOUS', 'HIGH_RISK', 'CRITICAL_FRAUD', name='verdicttype', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('fraud_markers', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['extracted_reg_number'], ['sebi_intermediaries.reg_number'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('verification_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_verification_logs_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_verification_logs_extracted_reg_number'), ['extracted_reg_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_verification_logs_extracted_upi'), ['extracted_upi'], unique=False)
        batch_op.create_index(batch_op.f('ix_verification_logs_input_hash'), ['input_hash'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('verification_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_verification_logs_input_hash'))
        batch_op.drop_index(batch_op.f('ix_verification_logs_extracted_upi'))
        batch_op.drop_index(batch_op.f('ix_verification_logs_extracted_reg_number'))
        batch_op.drop_index(batch_op.f('ix_verification_logs_created_at'))

    op.drop_table('verification_logs')
    with op.batch_alter_table('unregistered_blacklists', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_unregistered_blacklists_entity_name'))
        batch_op.drop_index(batch_op.f('ix_unregistered_blacklists_date_flagged'))
        batch_op.drop_index(batch_op.f('ix_unregistered_blacklists_channel_handle'))

    op.drop_table('unregistered_blacklists')
    with op.batch_alter_table('sebi_intermediaries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sebi_intermediaries_reg_number'))
        batch_op.drop_index(batch_op.f('ix_sebi_intermediaries_entity_name'))

    op.drop_table('sebi_intermediaries')
    with op.batch_alter_table('grievance_drafts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_grievance_drafts_user_session_id'))
        batch_op.drop_index(batch_op.f('ix_grievance_drafts_created_at'))

    op.drop_table('grievance_drafts')
