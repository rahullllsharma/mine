"""clustering

Revision ID: 8b21b0692c70
Revises: c67a195dddfe
Create Date: 2022-11-23 22:45:31.760230

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8b21b0692c70"
down_revision = "cc8ce9830941"
branch_labels = None
depends_on = None

CLUSTERING_ZOOM = 12


def upgrade():
    for zoom in range(CLUSTERING_ZOOM + 1):
        op.execute(
            f"""
            CREATE OR REPLACE FUNCTION clustering_{zoom}(i _uuid)
                RETURNS uuid
                LANGUAGE plpgsql IMMUTABLE AS
            $func$
            BEGIN
                return i[{zoom + 1}];
            END;
            $func$
            """
        )

    op.execute(
        """
        CREATE TABLE public.locations_clustering (
            id uuid NOT NULL,
            tenant_id uuid NOT NULL,
            zoom int2 NOT NULL,
            geom public.geometry('POLYGON') NOT NULL,
            geom_centroid public.geometry('POINT') NOT NULL,
            CONSTRAINT locations_clustering_pkey PRIMARY KEY (id),
            CONSTRAINT locations_clustering_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
        )
        """
    )
    op.create_index(
        "locations_clustering_tenant_id_zoom_ix",
        "locations_clustering",
        ["tenant_id", "zoom"],
        unique=False,
    )
    op.create_index(
        "locations_clustering_geom_ix",
        "locations_clustering",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.execute("ALTER TABLE public.project_locations ADD COLUMN clustering _uuid")
    op.execute("UPDATE project_locations SET clustering = '{}'")
    op.alter_column("project_locations", "clustering", nullable=False)

    for zoom in range(CLUSTERING_ZOOM + 1):
        op.create_index(
            f"locations_clustering_{zoom}_ix",
            "project_locations",
            [sa.text(f"clustering_{zoom}(clustering)")],
            unique=False,
            postgresql_where="archived_at IS NULL",
        )


def downgrade():
    op.drop_column("project_locations", "clustering")
    op.drop_table("locations_clustering")

    for zoom in range(CLUSTERING_ZOOM + 1):
        op.execute(f"DROP FUNCTION IF EXISTS clustering_{zoom}")
