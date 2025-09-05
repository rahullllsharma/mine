"""library task activity group seed

Revision ID: cbc89b4df39b
Revises: cbd1cb535cf6
Create Date: 2022-09-29 15:36:08.650458

"""

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "cbc89b4df39b"
down_revision = "cbd1cb535cf6"
branch_labels = None
depends_on = None


insert_above_ground_welding = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '8cfa3513-a393-4834-98e7-f2f279fc8ac1', id from library_tasks where unique_task_id in (
        'GASTRANS027',
        'GASTRANS026',
        'GASTRANS024',
        'GASTRANS025',
        'GASTRANS033',
        'GASTRANS030'
    );
    """

insert_in_trench_welding = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '10821d15-975a-4698-8c9d-b4a1936609dd', id from library_tasks where unique_task_id in (
        'GASTRANS028',
        'GASTRANS031',
        'GASTRANS032',
        'GASTRANS034',
        'GASTRANS030'
    );
"""

insert_confined_space_entry = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '13e0a520-8de1-4579-9d77-c76c54982828', id from library_tasks where unique_task_id='GASTRANS057';
"""

insert_demolition = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '6693defe-d58d-4f5a-a7da-b269d4a581d9', id from library_tasks where unique_task_id='GASTRANS062';
"""

insert_drilling = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'ba227d34-44bc-4384-8da8-3d58cc4fc075', id from library_tasks where unique_task_id in (
        'GASTRANS048',
        'GASTRANS065'
    );
"""

insert_driving = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'a0da67f3-8c07-46b1-a527-3eb761c61f5f', id from library_tasks where unique_task_id='GENERAL001';
"""

insert_electrical = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '3d62c233-1c09-499c-a7ac-bb4f895cda04', id from library_tasks where unique_task_id in (
        'GASTRANS071',
        'GASTRANS070',
        'GASTRANS073',
        'GASTRANS072'
    );
"""

insert_excavation = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '524bcf3a-1ddb-4b2d-91e6-97013241689b', id from library_tasks where unique_task_id in (
        'GASTRANS014',
        'GASTRANS008',
        'GASTRANS009',
        'GASTRANS012',
        'GASTRANS007',
        'GASTRANS011',
        'GASTRANS006',
        'GASTRANS015',
        'GASTRANS010',
        'GASTRANS013'
    );
"""

insert_field_coating = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '3a522493-0a25-4719-b7ce-8d87b91c7452', id from library_tasks where unique_task_id in (
        'GASTRANS043',
        'GASTRANS042',
        'GASTRANS047',
        'GASTRANS046',
        'GASTRANS040',
        'GASTRANS041',
        'GASTRANS044',
        'GASTRANS045'
    );
"""

insert_install = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '1e4c6c0a-c675-4be0-a451-2692467fd25a', id from library_tasks where unique_task_id in (
        'GASTRANS054',
        'GASTRANS053',
        'GASTRANS052'
    );
"""

insert_labor = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '66958300-e5ee-4809-b6bc-34d74338eab3', id from library_tasks where unique_task_id='GENERAL005';
"""

insert_material_bending = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'a53c4860-62f2-40b9-89cb-4e89c0480a29', id from library_tasks where unique_task_id='GASTRANS019';
"""

insert_material_handling = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '314350b9-79e3-43ea-8167-4ede2a4eca4a', id from library_tasks where unique_task_id in (
        'GASTRANS016',
        'GASTRANS018',
        'GASTRANS017'
    );
"""

insert_non_destructive_examination = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '7ce5d4ec-e20d-4703-bedd-eb1ae870a580', id from library_tasks where unique_task_id in (
        'GASTRANS038',
        'GASTRANS037',
        'GASTRANS039'
    );
"""

insert_other = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '313e6685-b8c0-460e-b384-9ef415311a03', id from library_tasks where unique_task_id='GASTRANS023';
"""

insert_pigging = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'd5f625a0-ea44-4dc9-990c-e94b25877ff1', id from library_tasks where unique_task_id='GASTRANS056';
"""

insert_retire_remove = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'c3d0d6ee-33f2-43bd-8acf-b8486a78c94c', id from library_tasks where unique_task_id='GASTRANS022';
"""

insert_pipe_fusion = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'cc13a4a3-00fa-43af-9709-bf5767d99a24', id from library_tasks where unique_task_id='GASTRANS029';
"""

insert_pipe_installation = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '989a3cae-4be2-4ac6-aa3b-a5ebbd459f79', id from library_tasks where unique_task_id in (
        'GASTRANS049',
        'GASTRANS050',
        'GASTRANS051'
    );
"""

insert_plumbing = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '4d4b0fd2-7a93-4478-874a-db5b542a0f36', id from library_tasks where unique_task_id='GASTRANS077';
"""

insert_pressure_test = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '44965da2-5d7c-412f-97ee-c6b4c0ade8ff', id from library_tasks where unique_task_id='GASTRANS055';
"""

insert_purging = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '1255dac3-e7b2-421c-b532-dfb53268e09b', id from library_tasks where unique_task_id='GASTRANS036';
"""

insert_purging_gas_in = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '22172a0d-dfcb-46b6-b543-3593d5084873', id from library_tasks where unique_task_id='GASTRANS076';
"""

insert_site_setup_mobilization = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '263b01e7-f705-44a2-a8c1-82290b713ec8', id from library_tasks where unique_task_id in (
        'GENERAL007',
        'GENERAL003',
        'GENERAL004',
        'GASTRANS063',
        'GENERAL006',
        'GENERAL002',
        'GENERAL008',
        'GASTRANS007'
    );
"""

insert_site_setup_restoration = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '2c227a95-c883-4758-8350-92c5528ee6cf', id from library_tasks where unique_task_id='GASTRANS064';
"""

insert_site_restoration = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'b5d41b25-58c6-4b0d-9f31-1d3df4ce5ce4', id from library_tasks where unique_task_id in (
        'GASTRANS058',
        'GASTRANS061',
        'GASTRANS059',
        'GASTRANS060',
        'GASTRANS068',
        'GASTRANS066',
        'GASTRANS067',
        'GASTRANS069'
    );
"""

insert_tie_in = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'eedcdbc9-f25f-45f1-b2c3-87e7aa5b80f1', id from library_tasks where unique_task_id='GASTRANS035';
"""

insert_torquing = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select 'c0d44bd5-d17c-4d45-9452-dc195e432e71', id from library_tasks where unique_task_id in (
        'GASTRANS021',
        'GASTRANS020'
    );
"""

insert_corrosion = """
    INSERT into library_task_activity_groups (activity_group_id, library_task_id) select '0416f434-43d5-45c8-a032-e10dc53a96e7', id from library_tasks where unique_task_id in (
        'GASTRANS074',
        'GASTRANS075'
    );
"""


def upgrade():
    conn = op.get_bind()
    conn.execute(text(insert_above_ground_welding))
    conn.execute(text(insert_in_trench_welding))
    conn.execute(text(insert_confined_space_entry))
    conn.execute(text(insert_demolition))
    conn.execute(text(insert_drilling))
    conn.execute(text(insert_driving))
    conn.execute(text(insert_electrical))
    conn.execute(text(insert_excavation))
    conn.execute(text(insert_field_coating))
    conn.execute(text(insert_install))
    conn.execute(text(insert_labor))
    conn.execute(text(insert_material_bending))
    conn.execute(text(insert_material_handling))
    conn.execute(text(insert_non_destructive_examination))
    conn.execute(text(insert_other))
    conn.execute(text(insert_pigging))
    conn.execute(text(insert_retire_remove))
    conn.execute(text(insert_pipe_fusion))
    conn.execute(text(insert_pipe_installation))
    conn.execute(text(insert_plumbing))
    conn.execute(text(insert_pressure_test))
    conn.execute(text(insert_purging))
    conn.execute(text(insert_purging_gas_in))
    conn.execute(text(insert_site_setup_mobilization))
    conn.execute(text(insert_site_setup_restoration))
    conn.execute(text(insert_site_restoration))
    conn.execute(text(insert_tie_in))
    conn.execute(text(insert_torquing))
    conn.execute(text(insert_corrosion))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("DELETE FROM library_task_activity_groups;"))
