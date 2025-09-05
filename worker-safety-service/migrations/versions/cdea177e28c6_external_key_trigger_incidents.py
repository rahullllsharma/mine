"""external_key_trigger_incidents

Revision ID: cdea177e28c6
Revises: 3f5c709d7117
Create Date: 2023-10-04 19:24:01.786770

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "cdea177e28c6"
down_revision = "ccc5f4318ed8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION incident_external_key_unique_per_tenant()
        RETURNS trigger AS $BODY$
        BEGIN
        IF (
            SELECT COUNT(a.id) FROM incidents as a
            WHERE a.external_key = NEW.external_key
            AND a.tenant_id = NEW.tenant_id
        ) > 1 THEN
            RAISE EXCEPTION 'ExternalKey must be unique within a Tenant';
        ELSE
            RETURN NEW;
        END IF;
        END;
        $BODY$
        LANGUAGE 'plpgsql';
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER verify_external_key_unique_per_tenant_incidents AFTER INSERT OR UPDATE
            ON incidents
            FOR EACH ROW EXECUTE PROCEDURE incident_external_key_unique_per_tenant();
        """
    )


def downgrade():
    op.execute(
        "DROP TRIGGER verify_external_key_unique_per_tenant_incidents ON incidents"
    )
    op.execute("DROP FUNCTION IF EXISTS incident_external_key_unique_per_tenant")
