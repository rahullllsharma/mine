"""TileBBox

Revision ID: f292e0100502
Revises: 7793c2ea8970
Create Date: 2022-11-11 13:02:51.548987

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f292e0100502"
down_revision = "7793c2ea8970"
branch_labels = None
depends_on = None


def upgrade():
    # From: https://github.com/mapbox/postgis-vt-util
    op.execute(
        """
        create or replace function TileBBox (z int, x int, y int, srid int = 3857)
            returns geometry
            language plpgsql immutable as
        $func$
        declare
            max numeric := 20037508.34;
            res numeric := (max*2)/(2^z);
            bbox geometry;
        begin
            bbox := ST_MakeEnvelope(
                -max + (x * res),
                max - (y * res),
                -max + (x * res) + res,
                max - (y * res) - res,
                3857
            );
            if srid = 3857 then
                return bbox;
            else
                return ST_Transform(bbox, srid);
            end if;
        end;
        $func$;
        """
    )


def downgrade():
    op.execute("DROP FUNCTION IF EXISTS TileBBox")
