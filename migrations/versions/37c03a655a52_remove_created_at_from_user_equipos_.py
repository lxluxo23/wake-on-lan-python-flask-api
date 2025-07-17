"""remove created_at from user_equipos table

Revision ID: 37c03a655a52
Revises: 9a81297418b4
Create Date: 2025-07-16 18:47:42.379805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37c03a655a52'
down_revision = '9a81297418b4'
branch_labels = None
depends_on = None


def upgrade():
    # Recrear la tabla user_equipos sin la columna created_at
    op.execute('CREATE TABLE user_equipos_new (user_id INTEGER, equipo_id INTEGER, PRIMARY KEY (user_id, equipo_id))')
    op.execute('INSERT INTO user_equipos_new (user_id, equipo_id) SELECT user_id, equipo_id FROM user_equipos')
    op.execute('DROP TABLE user_equipos')
    op.execute('ALTER TABLE user_equipos_new RENAME TO user_equipos')


def downgrade():
    # Recrear la tabla con la columna created_at
    op.execute('CREATE TABLE user_equipos_new (user_id INTEGER, equipo_id INTEGER, created_at DATETIME, PRIMARY KEY (user_id, equipo_id))')
    op.execute('INSERT INTO user_equipos_new (user_id, equipo_id) SELECT user_id, equipo_id FROM user_equipos')
    op.execute('DROP TABLE user_equipos')
    op.execute('ALTER TABLE user_equipos_new RENAME TO user_equipos')
