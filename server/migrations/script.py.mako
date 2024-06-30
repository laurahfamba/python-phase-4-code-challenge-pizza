"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Created On: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identifiers for this revision
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    """This method is called when upgrading the database."""
    ${upgrades if upgrades else "print('No upgrade actions specified.')"}

def downgrade():
    """This method is called when downgrading the database."""
    ${downgrades if downgrades else "print('No downgrade actions specified.')"}
