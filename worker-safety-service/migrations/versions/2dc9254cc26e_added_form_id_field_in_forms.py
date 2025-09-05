"""added form_id field in forms

Revision ID: 2dc9254cc26e
Revises: e237ff10ad53
Create Date: 2024-06-26 17:07:24.192561

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2dc9254cc26e"
down_revision = "e237ff10ad53"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add form_id column to jsbs table
    op.add_column("jsbs", sa.Column("form_id", sa.String(length=10), nullable=True))

    # Add form_id column to energy_based_observations table
    op.add_column(
        "energy_based_observations",
        sa.Column("form_id", sa.String(length=10), nullable=True),
    )
    op.add_column(
        "daily_reports",
        sa.Column("form_id", sa.String(length=10), nullable=True),
    )
    op.add_column(
        "natgrid_jsbs",
        sa.Column("form_id", sa.String(length=10), nullable=True),
    )
    op.execute(
        "DROP FUNCTION IF EXISTS generate_form_id(TEXT, UUID, TIMESTAMP WITH TIME ZONE)"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS generate_form_id_for_existing_forms(TEXT, UUID, TIMESTAMP WITH TIME ZONE)"
    )
    # Create the sequence for form_id generation
    op.execute(
        """
        CREATE SEQUENCE form_id_seq
            INCREMENT BY 1
            START WITH 1
            MINVALUE 1
            MAXVALUE 99999
            CACHE 1;
    """
    )
    # Create function to generate form_id based on tenant_id and created_at timestamp
    op.execute(
        """
    CREATE OR REPLACE FUNCTION generate_form_id(p_table_name TEXT, tenant_id UUID, created_at TIMESTAMP WITH TIME ZONE)
    RETURNS TEXT AS $$
    DECLARE
        current_month TEXT := to_char(CURRENT_TIMESTAMP, 'YYMM');
        last_form_id TEXT;
        new_form_id TEXT;
        last_seq_val INT;
        query TEXT;
    BEGIN
        -- Construct the query dynamically
        query := format('
            SELECT form_id
            FROM %I
            WHERE tenant_id = ''%s''
            ORDER BY created_at DESC, form_id DESC
            LIMIT 1', p_table_name, tenant_id, current_month);
        BEGIN
            EXECUTE query INTO last_form_id;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                last_form_id := NULL;
        END;
        -- If last_form_id exists, extract the sequence value and increment
        IF last_form_id IS NOT NULL THEN
            last_seq_val := (substring(last_form_id from 5)::int);
            new_form_id := current_month || LPAD((last_seq_val + 1)::TEXT, 5, '0');
        ELSE
            new_form_id := current_month || '00001';
        END IF;

        RETURN new_form_id;
    END;
    $$ LANGUAGE plpgsql;
    """
    )
    # Create function to generate form_id for existing forms based on tenant_id and created_at timestamp
    op.execute(
        """
    CREATE OR REPLACE FUNCTION generate_form_id_for_existing_forms(p_table_name TEXT, p_tenant_id UUID, p_created_at TIMESTAMP WITH TIME ZONE)
    RETURNS TEXT AS $$
    DECLARE
        current_month TEXT := to_char(p_created_at, 'YYMM');
        new_form_id TEXT;
        last_seq_val INT;
        last_month TEXT;
        query TEXT;
    BEGIN
        -- Construct the query dynamically to get the last form_id for the current tenant and month
        query := format('
            SELECT COALESCE(MAX(SUBSTRING(form_id FROM 5)::INT), 0)
            FROM %I
            WHERE tenant_id = ''%s''
              AND to_char(created_at, ''YYMM'') = ''%s''', p_table_name, p_tenant_id, current_month);

        -- Execute the query to get the last sequence value
        EXECUTE query INTO last_seq_val;

        -- Construct another query to get the last month in the database for the tenant
        query := format('
            SELECT to_char(MAX(created_at), ''YYMM'')
            FROM %I
            WHERE tenant_id = ''%s''', p_table_name, p_tenant_id);

        -- Execute the query to get the last month
        EXECUTE query INTO last_month;

        -- Increment the sequence value if within the same month
        IF current_month = to_char(p_created_at, 'YYMM') THEN
            last_seq_val := last_seq_val + 1;
        ELSE
            -- Reset sequence value to 1 for a new month
            last_seq_val := 1;
        END IF;

        -- If last month in database is earlier, reset sequence to 1
        IF last_month IS NOT NULL AND last_month < current_month THEN
            last_seq_val := 1;
        END IF;

        -- Format the new form_id
        new_form_id := current_month || LPAD(last_seq_val::TEXT, 5, '0');

        RETURN new_form_id;
    END;
    $$ LANGUAGE plpgsql;
    """
    )
    # Create trigger function to set form_id on insert
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_form_id_trigger()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.form_id IS NULL THEN
                NEW.form_id := generate_form_id(TG_TABLE_NAME, NEW.tenant_id, NEW.created_at);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )
    # Create triggers for all forms tables
    op.execute(
        """
        CREATE TRIGGER jsbs_set_form_id_trigger
        BEFORE INSERT ON jsbs
        FOR EACH ROW
        EXECUTE FUNCTION set_form_id_trigger();
        """
    )
    op.execute(
        """
        CREATE TRIGGER energy_based_observations_set_form_id_trigger
        BEFORE INSERT ON energy_based_observations
        FOR EACH ROW
        EXECUTE FUNCTION set_form_id_trigger();
        """
    )
    op.execute(
        """
        CREATE TRIGGER daily_reports_set_form_id_trigger
        BEFORE INSERT ON daily_reports
        FOR EACH ROW
        EXECUTE FUNCTION set_form_id_trigger();
        """
    )
    op.execute(
        """
        CREATE TRIGGER natgrid_jsbs_set_form_id_trigger
        BEFORE INSERT ON natgrid_jsbs
        FOR EACH ROW
        EXECUTE FUNCTION set_form_id_trigger();
        """
    )
    # Update jsbs table
    op.execute(
        """
        UPDATE jsbs AS j
        SET form_id = generate_form_id_for_existing_forms('jsbs', j.tenant_id, j.created_at)
        FROM (
            SELECT id, tenant_id, created_at
            FROM jsbs
        ) AS sub
        WHERE j.id = sub.id
          AND (j.form_id IS NULL OR j.form_id != generate_form_id_for_existing_forms('jsbs', sub.tenant_id, sub.created_at));
        """
    )
    # Update energy_based_observations table
    op.execute(
        """
        UPDATE energy_based_observations AS e
        SET form_id = generate_form_id_for_existing_forms('energy_based_observations', e.tenant_id, e.created_at)
        FROM (
            SELECT id, tenant_id, created_at
            FROM energy_based_observations
        ) AS sub
        WHERE e.id = sub.id
          AND (e.form_id IS NULL OR e.form_id != generate_form_id_for_existing_forms('energy_based_observations', sub.tenant_id, sub.created_at));
        """
    )
    # Update daily_reports table
    op.execute(
        """
        UPDATE daily_reports AS e
        SET form_id = generate_form_id_for_existing_forms('daily_reports', e.tenant_id, e.created_at)
        FROM (
            SELECT id, tenant_id, created_at
            FROM daily_reports
        ) AS sub
        WHERE e.id = sub.id
          AND (e.form_id IS NULL OR e.form_id != generate_form_id_for_existing_forms('daily_reports', sub.tenant_id, sub.created_at));
        """
    )
    op.execute(
        """
        UPDATE natgrid_jsbs AS e
        SET form_id = generate_form_id_for_existing_forms('natgrid_jsbs', e.tenant_id, e.created_at)
        FROM (
            SELECT id, tenant_id, created_at
            FROM natgrid_jsbs
        ) AS sub
        WHERE e.id = sub.id
          AND (e.form_id IS NULL OR e.form_id != generate_form_id_for_existing_forms('natgrid_jsbs', sub.tenant_id, sub.created_at));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS natgrid_jsbs_set_form_id_trigger ON natgrid_jsbs;
    """
    )
    op.execute(
        """
        DROP FUNCTION IF EXISTS set_form_id_trigger() CASCADE;
    """
    )
    op.execute(
        """
       DROP FUNCTION IF EXISTS generate_form_id(TEXT, UUID, TIMESTAMP WITH TIME ZONE)
        """
    )
    op.execute(
        """
       DROP FUNCTION IF EXISTS generate_form_id_for_existing_forms(TEXT, UUID, TIMESTAMP WITH TIME ZONE)
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS energy_based_observations_set_form_id_trigger ON energy_based_observations;
    """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS jsbs_set_form_id_trigger ON jsbs;
    """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS daily_reports_set_form_id_trigger ON daily_reports;
    """
    )
    op.execute(
        """
        DROP SEQUENCE IF EXISTS form_id_seq;
    """
    )
    op.drop_column("energy_based_observations", "form_id")
    op.drop_column("jsbs", "form_id")
    op.drop_column("daily_reports", "form_id")
    op.drop_column("natgrid_jsbs", "form_id")
