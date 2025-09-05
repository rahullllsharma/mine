"""external_key trigger for activities

Revision ID: cc8ce9830941
Revises: b8bcb8de2aa5
Create Date: 2023-03-07 16:24:44.982788

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "cc8ce9830941"
down_revision = "b8bcb8de2aa5"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION activity_external_key_unique_per_tenant()
        RETURNS trigger AS $BODY$

        BEGIN
        IF (
            SELECT COUNT(a.id) FROM activities as a
            INNER JOIN project_locations as l on l.id = a.location_id
            INNER JOIN projects as p on p.id = l.project_id
            WHERE a.external_key = NEW.external_key
            AND p.tenant_id = (
                SELECT p.tenant_id FROM projects as p
                join project_locations as l on p.id = l.project_id
                WHERE NEW.location_id = l.id
            )
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
        CREATE CONSTRAINT TRIGGER verify_external_key_unique_per_tenant_activities AFTER INSERT OR UPDATE
            ON activities
            FOR EACH ROW EXECUTE PROCEDURE activity_external_key_unique_per_tenant();
        """
    )


def downgrade():
    op.execute(
        "DROP TRIGGER verify_external_key_unique_per_tenant_activities ON activities"
    )
    op.execute("DROP FUNCTION IF EXISTS activity_external_key_unique_per_tenant")
