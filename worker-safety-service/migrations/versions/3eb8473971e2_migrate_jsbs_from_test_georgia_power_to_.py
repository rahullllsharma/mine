"""migrate JSBs from test-georgia-power to georgia-power v2

Revision ID: 3eb8473971e2
Revises: 3e4a21abd72c
Create Date: 2024-12-20 11:50:49.395371

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3eb8473971e2"
down_revision = "3e4a21abd72c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    query = """
        SELECT
        jsbs.id as id,
        jsbs.tenant_id as tenant_id,
        jsbs.contents as contents,
        jsbs.date_for,
        u.first_name,
        u.last_name,
        u.email as email
    FROM
        jsbs
    INNER JOIN
        users u ON u.id = jsbs.created_by_id
    WHERE
        jsbs.tenant_id = (SELECT id FROM tenants WHERE tenant_name = 'test-georgia-power')
        AND u.email IN ('jamtillm@southernco.com',
                        'btwright@southernco.com',
                        'chalelee@southernco.com',
                        'dbanford@southernco.com',
                        'dlestes@southernco.com',
                        'jfaucett@southernco.com'
                        )
    ORDER BY
        jsbs.date_for desc
    """
    result = connection.execute(sa.text(query))
    query2 = """
        SELECT id, email
        FROM public.users
        WHERE email IN (
            'jamtillm@southernco.com',
            'btwright@southernco.com',
            'chalelee@southernco.com',
            'dbanford@southernco.com',
            'dlestes@southernco.com',
            'jfaucett@southernco.com'
        ) and tenant_id = (SELECT id FROM tenants WHERE tenant_name = 'georgia-power') ;
        """
    users = connection.execute(sa.text(query2))
    user_list = {item["email"]: item["id"] for item in users}
    for row in result:
        contents = row["contents"]
        email = row["email"]
        if contents and "completions" in contents:
            user_id = user_list.get(email, None)
            if user_id is not None:
                completions = contents["completions"]
                if completions:
                    for item in completions:
                        item["completed_by_id"] = str(user_id)
                    contents["completions"] = completions
                    updated_contents = json.dumps(contents)
                    update_query = """
                        UPDATE public.jsbs
                        SET contents = :contents,
                            tenant_id = (SELECT id FROM tenants WHERE tenant_name = 'georgia-power'),
                            created_by_id = :created_by_id,
                            completed_by_id = :completed_by_id
                        WHERE id = :id;
                    """
                    connection.execute(
                        sa.text(update_query),
                        {
                            "id": row["id"],
                            "contents": updated_contents,
                            "created_by_id": user_id,
                            "completed_by_id": user_id,
                        },
                    )
                else:
                    update_query = """
                        UPDATE public.jsbs
                        SET tenant_id = (SELECT id FROM tenants WHERE tenant_name = 'georgia-power'),
                            created_by_id = :created_by_id
                        WHERE id = :id;
                    """
                    connection.execute(
                        sa.text(update_query),
                        {"id": row["id"], "created_by_id": user_id},
                    )


def downgrade() -> None:
    return
