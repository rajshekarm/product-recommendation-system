"""phase 1 foundation"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_phase1"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table("users", sa.Column("id", sa.String(128), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("products", sa.Column("id", sa.String(128), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("category", sa.String(80), nullable=False), sa.Column("brand", sa.String(120)), sa.Column("color", sa.String(80)), sa.Column("style", sa.String(80)), sa.Column("image_url", sa.String(2048)), sa.Column("price_cents", sa.Integer()), sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_available", "products", ["available"])
    op.create_table("user_interactions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("event_id", sa.String(128), nullable=False), sa.Column("user_id", sa.String(128), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.String(128), sa.ForeignKey("products.id"), nullable=False), sa.Column("interaction_type", sa.String(32), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.Column("weight", sa.Float(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("event_id", name="uq_user_interactions_event_id"))
    op.create_index("ix_user_interactions_user_id", "user_interactions", ["user_id"])
    op.create_index("ix_user_interactions_product_id", "user_interactions", ["product_id"])
    op.create_table("product_embeddings", sa.Column("product_id", sa.String(128), sa.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True), sa.Column("embedding", Vector(512), nullable=False), sa.Column("model_name", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("user_preferences", sa.Column("user_id", sa.String(128), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("preference_vector", Vector(512)), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

def downgrade():
    op.drop_table("user_preferences")
    op.drop_table("product_embeddings")
    op.drop_index("ix_user_interactions_product_id", table_name="user_interactions")
    op.drop_index("ix_user_interactions_user_id", table_name="user_interactions")
    op.drop_table("user_interactions")
    op.drop_index("ix_products_available", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_table("products")
    op.drop_table("users")

