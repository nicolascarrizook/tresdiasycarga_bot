"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.Column('verification_expires_at', sa.DateTime(), nullable=True),
        sa.Column('reset_token', sa.String(255), nullable=True),
        sa.Column('reset_expires_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', JSON, nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False),
        sa.Column('language', sa.String(5), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('totp_secret', sa.String(255), nullable=True),
        sa.Column('backup_codes', JSON, nullable=True),
        sa.Column('is_2fa_enabled', sa.Boolean(), nullable=False),
        sa.Column('api_key', sa.String(255), nullable=True),
        sa.Column('api_key_expires_at', sa.DateTime(), nullable=True),
        sa.Column('rate_limit_remaining', sa.Integer(), nullable=False),
        sa.Column('rate_limit_reset_at', sa.DateTime(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('api_key')
    )
    
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=True),
        sa.Column('telegram_username', sa.String(100), nullable=True),
        sa.Column('telegram_first_name', sa.String(100), nullable=True),
        sa.Column('telegram_last_name', sa.String(100), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('sex', sa.String(10), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('initial_weight', sa.Float(), nullable=True),
        sa.Column('target_weight', sa.Float(), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('objective', sa.String(50), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('supplements', JSON, nullable=True),
        sa.Column('pathologies', JSON, nullable=True),
        sa.Column('restrictions', JSON, nullable=True),
        sa.Column('allergies', JSON, nullable=True),
        sa.Column('medications', JSON, nullable=True),
        sa.Column('preferences', JSON, nullable=True),
        sa.Column('dislikes', JSON, nullable=True),
        sa.Column('favorite_foods', JSON, nullable=True),
        sa.Column('schedule', JSON, nullable=True),
        sa.Column('economic_level', sa.String(10), nullable=False),
        sa.Column('peso_tipo', sa.String(10), nullable=False),
        sa.Column('main_meals_count', sa.Integer(), nullable=False),
        sa.Column('snacks_enabled', sa.Boolean(), nullable=False),
        sa.Column('snack_type', sa.String(50), nullable=True),
        sa.Column('last_weight_update', sa.DateTime(), nullable=True),
        sa.Column('weight_history', JSON, nullable=True),
        sa.Column('progress_notes', sa.Text(), nullable=True),
        sa.Column('special_conditions', sa.Text(), nullable=True),
        sa.Column('consultation_notes', sa.Text(), nullable=True),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('is_active_patient', sa.Boolean(), nullable=False),
        sa.Column('next_consultation', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('search_vector', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_user_id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('preparation', sa.Text(), nullable=False),
        sa.Column('cooking_time', sa.Integer(), nullable=True),
        sa.Column('prep_time', sa.Integer(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(10), nullable=False),
        sa.Column('economic_level', sa.String(10), nullable=False),
        sa.Column('dietary_restrictions', JSON, nullable=True),
        sa.Column('allergens', JSON, nullable=True),
        sa.Column('calories', sa.Float(), nullable=True),
        sa.Column('protein', sa.Float(), nullable=True),
        sa.Column('carbs', sa.Float(), nullable=True),
        sa.Column('fat', sa.Float(), nullable=True),
        sa.Column('fiber', sa.Float(), nullable=True),
        sa.Column('sugar', sa.Float(), nullable=True),
        sa.Column('sodium', sa.Float(), nullable=True),
        sa.Column('macros', JSON, nullable=True),
        sa.Column('micronutrients', JSON, nullable=True),
        sa.Column('embedding_vector', JSON, nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('search_vector', sa.Text(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('validated_by', sa.Integer(), nullable=True),
        sa.Column('validation_score', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create recipe_ingredients table
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('is_optional', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('calories_per_unit', sa.Float(), nullable=True),
        sa.Column('protein_per_unit', sa.Float(), nullable=True),
        sa.Column('carbs_per_unit', sa.Float(), nullable=True),
        sa.Column('fat_per_unit', sa.Float(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recipe_id', 'name'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create plans table
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('plan_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('plan_data', JSON, nullable=False),
        sa.Column('calories_total', sa.Float(), nullable=True),
        sa.Column('protein_total', sa.Float(), nullable=True),
        sa.Column('carbs_total', sa.Float(), nullable=True),
        sa.Column('fat_total', sa.Float(), nullable=True),
        sa.Column('fiber_total', sa.Float(), nullable=True),
        sa.Column('macros', JSON, nullable=True),
        sa.Column('days_duration', sa.Integer(), nullable=False),
        sa.Column('main_meals_count', sa.Integer(), nullable=False),
        sa.Column('snacks_count', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('generation_context', JSON, nullable=True),
        sa.Column('ai_model_used', sa.String(100), nullable=True),
        sa.Column('generation_time', sa.Float(), nullable=True),
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(), nullable=True),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('deactivated_at', sa.DateTime(), nullable=True),
        sa.Column('adherence_score', sa.Float(), nullable=True),
        sa.Column('patient_feedback', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('validated_by', sa.Integer(), nullable=True),
        sa.Column('validation_score', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('conversation_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('telegram_chat_id', sa.Integer(), nullable=True),
        sa.Column('telegram_message_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('messages', JSON, nullable=False),
        sa.Column('current_state', sa.String(100), nullable=True),
        sa.Column('context_data', JSON, nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=False),
        sa.Column('result_data', JSON, nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('embedding_type', sa.String(50), nullable=False),
        sa.Column('vector', JSON, nullable=False),
        sa.Column('vector_dimension', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('source_field', sa.String(100), nullable=True),
        sa.Column('language', sa.String(5), nullable=False),
        sa.Column('content_length', sa.Integer(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('processing_tokens', sa.Integer(), nullable=True),
        sa.Column('similarity_threshold', sa.Float(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('retrieval_count', sa.Integer(), nullable=False),
        sa.Column('last_retrieved_at', sa.DateTime(), nullable=True),
        sa.Column('chroma_id', sa.String(255), nullable=True),
        sa.Column('chroma_collection', sa.String(100), nullable=False),
        sa.Column('metadata_json', JSON, nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash', 'model_name'),
        sa.UniqueConstraint('content_hash'),
        sa.UniqueConstraint('chroma_id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_method', sa.String(10), nullable=True),
        sa.Column('request_path', sa.String(500), nullable=True),
        sa.Column('request_params', JSON, nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('old_values', JSON, nullable=True),
        sa.Column('new_values', JSON, nullable=True),
        sa.Column('changed_fields', JSON, nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('additional_data', JSON, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create cache_entries table
    op.create_table(
        'cache_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('cache_key', sa.String(255), nullable=False),
        sa.Column('cache_type', sa.String(50), nullable=False),
        sa.Column('data', JSON, nullable=False),
        sa.Column('data_size', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('ttl_seconds', sa.Integer(), nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('is_compressed', sa.Boolean(), nullable=False),
        sa.Column('compression_ratio', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cache_key'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes
    create_indexes()


def create_indexes():
    """Create database indexes for performance optimization."""
    
    # Users indexes
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'])
    op.create_index('idx_users_username_active', 'users', ['username', 'is_active'])
    op.create_index('idx_users_role_active', 'users', ['role', 'is_active'])
    op.create_index('idx_users_verification', 'users', ['verification_token', 'verification_expires_at'])
    op.create_index('idx_users_reset', 'users', ['reset_token', 'reset_expires_at'])
    op.create_index('idx_users_api_key', 'users', ['api_key', 'api_key_expires_at'])
    
    # Patients indexes
    op.create_index('idx_patients_telegram_user', 'patients', ['telegram_user_id'])
    op.create_index('idx_patients_name_active', 'patients', ['name', 'is_active'])
    op.create_index('idx_patients_email_active', 'patients', ['email', 'is_active'])
    op.create_index('idx_patients_objective_active', 'patients', ['objective', 'is_active'])
    op.create_index('idx_patients_activity_type', 'patients', ['activity_type'])
    op.create_index('idx_patients_economic_level', 'patients', ['economic_level'])
    op.create_index('idx_patients_user_active', 'patients', ['user_id', 'is_active'])
    op.create_index('idx_patients_search', 'patients', ['search_vector'])
    
    # Recipes indexes
    op.create_index('idx_recipes_name', 'recipes', ['name'])
    op.create_index('idx_recipes_category', 'recipes', ['category'])
    op.create_index('idx_recipes_subcategory', 'recipes', ['subcategory'])
    op.create_index('idx_recipes_economic_level', 'recipes', ['economic_level'])
    op.create_index('idx_recipes_difficulty', 'recipes', ['difficulty'])
    op.create_index('idx_recipes_calories', 'recipes', ['calories'])
    op.create_index('idx_recipes_protein', 'recipes', ['protein'])
    op.create_index('idx_recipes_search', 'recipes', ['search_vector'])
    op.create_index('idx_recipes_category_economic', 'recipes', ['category', 'economic_level'])
    op.create_index('idx_recipes_validated', 'recipes', ['is_validated', 'is_active'])
    
    # Recipe ingredients indexes
    op.create_index('idx_recipe_ingredients_recipe', 'recipe_ingredients', ['recipe_id'])
    op.create_index('idx_recipe_ingredients_name', 'recipe_ingredients', ['name'])
    op.create_index('idx_recipe_ingredients_order', 'recipe_ingredients', ['recipe_id', 'order'])
    
    # Plans indexes
    op.create_index('idx_plans_patient', 'plans', ['patient_id'])
    op.create_index('idx_plans_type', 'plans', ['plan_type'])
    op.create_index('idx_plans_status', 'plans', ['status'])
    op.create_index('idx_plans_active', 'plans', ['is_active'])
    op.create_index('idx_plans_dates', 'plans', ['start_date', 'end_date'])
    op.create_index('idx_plans_patient_active', 'plans', ['patient_id', 'is_active'])
    op.create_index('idx_plans_patient_status', 'plans', ['patient_id', 'status'])
    op.create_index('idx_plans_calories', 'plans', ['calories_total'])
    
    # Conversations indexes
    op.create_index('idx_conversations_telegram_chat', 'conversations', ['telegram_chat_id'])
    op.create_index('idx_conversations_type', 'conversations', ['conversation_type'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])
    op.create_index('idx_conversations_state', 'conversations', ['current_state'])
    op.create_index('idx_conversations_user', 'conversations', ['user_id'])
    op.create_index('idx_conversations_patient', 'conversations', ['patient_id'])
    op.create_index('idx_conversations_plan', 'conversations', ['plan_id'])
    op.create_index('idx_conversations_started', 'conversations', ['started_at'])
    op.create_index('idx_conversations_last_message', 'conversations', ['last_message_at'])
    op.create_index('idx_conversations_active', 'conversations', ['status', 'started_at'])
    
    # Embeddings indexes
    op.create_index('idx_embeddings_content_hash', 'embeddings', ['content_hash'])
    op.create_index('idx_embeddings_type', 'embeddings', ['embedding_type'])
    op.create_index('idx_embeddings_model', 'embeddings', ['model_name'])
    op.create_index('idx_embeddings_source', 'embeddings', ['source_type', 'source_id'])
    op.create_index('idx_embeddings_language', 'embeddings', ['language'])
    op.create_index('idx_embeddings_chroma', 'embeddings', ['chroma_id'])
    op.create_index('idx_embeddings_collection', 'embeddings', ['chroma_collection'])
    op.create_index('idx_embeddings_quality', 'embeddings', ['quality_score'])
    op.create_index('idx_embeddings_retrieval', 'embeddings', ['retrieval_count', 'last_retrieved_at'])
    
    # Audit logs indexes
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_session', 'audit_logs', ['session_id'])
    op.create_index('idx_audit_logs_ip', 'audit_logs', ['ip_address'])
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_logs_success', 'audit_logs', ['success'])
    op.create_index('idx_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])
    op.create_index('idx_audit_logs_resource_action', 'audit_logs', ['resource_type', 'action'])
    
    # Cache entries indexes
    op.create_index('idx_cache_entries_key', 'cache_entries', ['cache_key'])
    op.create_index('idx_cache_entries_type', 'cache_entries', ['cache_type'])
    op.create_index('idx_cache_entries_expires', 'cache_entries', ['expires_at'])
    op.create_index('idx_cache_entries_active', 'cache_entries', ['is_active', 'expires_at'])
    op.create_index('idx_cache_entries_type_active', 'cache_entries', ['cache_type', 'is_active'])
    op.create_index('idx_cache_entries_size', 'cache_entries', ['data_size'])
    op.create_index('idx_cache_entries_access', 'cache_entries', ['access_count', 'last_accessed_at'])


def downgrade() -> None:
    """Drop all tables and indexes."""
    op.drop_table('cache_entries')
    op.drop_table('audit_logs')
    op.drop_table('embeddings')
    op.drop_table('conversations')
    op.drop_table('plans')
    op.drop_table('recipe_ingredients')
    op.drop_table('recipes')
    op.drop_table('patients')
    op.drop_table('users')