"""New ExternalKey field for Location model

Revision ID: 12673078d1fd
Revises: 997bec38bb0b
Create Date: 2022-11-28 11:42:05.827845

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "12673078d1fd"
down_revision = "997bec38bb0b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_locations",
        sa.Column("external_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION external_key_uniqueness_insert()
        RETURNS trigger AS $BODY$

        BEGIN
        IF (
            SELECT COUNT(l.id) FROM project_locations as l
            INNER JOIN projects as p on p.id = l.project_id
            WHERE l.external_key = NEW.external_key
            AND p.tenant_id = (
                SELECT tenant_id FROM projects
                WHERE id = NEW.project_id
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
        CREATE CONSTRAINT TRIGGER verify_insert_unique_location_external_key AFTER INSERT OR UPDATE
            ON project_locations
            FOR EACH ROW EXECUTE PROCEDURE external_key_uniqueness_insert();
        """
    )


def downgrade():
    op.execute(
        "DROP TRIGGER verify_insert_unique_location_external_key ON project_locations"
    )
    op.execute("DROP FUNCTION IF EXISTS external_key_uniqueness_insert")
    op.drop_column("project_locations", "external_key")
