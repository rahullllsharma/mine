"""add_hydro_one_electric_distribution_tasks

Revision ID: 795d1a2b2db0
Revises: eacb03e5092f
Create Date: 2022-10-12 12:59:30.424981

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "795d1a2b2db0"
down_revision = "eacb03e5092f"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('f8e7acfa-cc2d-46f2-9100-2a82a01654d5', 'Excavation - D-Line Grading', '210', 'CIVIL', 'ELEC DIST 009', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('7ebf6ae3-0cbe-455c-a677-396b132c0563', 'Excavation - Excavation of soil', '223', 'CIVIL', 'ELEC DIST 010', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('68d4fe67-2873-42c1-81cf-38d941b365d8', 'Excavation - Soil Management /Disposal', '210', 'CIVIL', 'ELEC DIST 011', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('61584f3f-39ca-4968-b1f9-75df32e5ad42', 'Receiving , transporting and staging Material (e.g., poles, insulators, airbreaks, primary and secondary conductors, pole top reclosers, etc) - loading/transporting/unloading', '140', 'Material handling', 'ELEC DIST 012', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('707c89f3-69f5-44ef-855d-1285c37bc19b', 'Hydro-vac', '201', 'CIVIL', 'ELEC DIST 013', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('e76ac93a-3460-40e0-9c67-2ba771be2306', 'Excavation/Vertical drilling', '302', 'CIVIL', 'ELEC DIST 014', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('47946e56-d353-4d09-ba02-948403fe4acc', 'Take a Clearance -Red Tag Air Gap/Switch(s) to ensure new circuit line isolated from system', '10', 'Switching and Tagging/C&C (Clerance and Control)', 'ELEC DIST 015', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('f422cab2-a7be-4015-80d4-ddfc2a30e717', 'Installing new wood poles (various lengths) - Hoisting & Rigging loads', '200', 'Overhead Construction', 'ELEC DIST 016', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('527054e9-88e8-44e9-b006-f72eb7934436', 'Installing new wood poles - Tamping', '300', 'Overhead Construction', 'ELEC DIST 017', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('58e446e5-f278-4a65-aea1-a1e2604da5bb', 'Install anchors/guys - Rigging loads', '310', 'Overhead Construction', 'ELEC DIST 018', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('b7975a77-1cc9-45c4-8e90-9173f2e2ce5f', 'Install line hardware: insulators, airbreaks, pole top reclosers, vibration dampers, bird diverters.', '301', 'Overhead Construction - Replace', 'ELEC DIST 019', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('8fa3aba3-66fe-41ea-b315-ba070785bbcf', 'Running primary conductor (477 Spacer Cable/15kv for example) - Rigging & Hoisting', '200', 'Overhead Construction', 'ELEC DIST 020', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('831d5978-5338-449b-97b1-feededfa0238', 'Running/securing primary conductor - Rigging & Hoisting', '200', 'Overhead Construction', 'ELEC DIST 021', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('1867f569-da9d-4428-8081-189b9ff10c60', 'Running/securing secondary conductor - Hoisting & Rig', '200', 'Overhead Construction', 'ELEC DIST 022', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('3ddc633b-f712-4f39-aa6b-ababefb6fbce', 'Terminating primary conductors to equipment (i.e./xfmr/recloser/airbreak) - Strip/prep/Pressing/bolting connectors', '300', 'Overhead Construction', 'ELEC DIST 023', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('598bf4fd-4c5f-4bce-919b-1aa56929f4b8', 'terminating secondary conductors to equipment (i.e -xformer/disc sw/metering) - Strip/prep/Pressing/bolting connectors', '300', 'Overhead Construction', 'ELEC DIST 024', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('92ca4761-59c8-4682-96f1-e4942f1dc400', 'Torquing/bolt up - Securement', '120', 'Overhead Construction', 'ELEC DIST 025', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('065b1971-6107-4e99-b84b-a44662262866', 'Release Clearance for testing/phasing', '10', 'Switching and Tagging/C&C (Clerance and Control)', 'ELEC DIST 026', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('abf3d9dc-2de8-4ea5-9f26-16c3b1fd55a5', 'Switching for Phasing', '132', 'Switching and Tagging/C&C (Clerance and Control)', 'ELEC DIST 027', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('ba3283c2-4a73-4306-bc01-ecb61a69b982', 'Phasing', '130', 'Testing', 'ELEC DIST 028', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('a5ae7d47-0f09-4636-9d96-b998b62f8f5d', 'Load Checks', '131', 'Switching and Tagging/C&C (Clerance and Control)', 'ELEC DIST 029', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('ba622c1d-dee9-4b51-a0e4-d98acefd1092', 'Energize new circuit', '122', 'Switching and Tagging/C&C (Clerance and Control)', 'ELEC DIST 030', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('1b6fad18-62cc-4eec-af79-fba6bcb65cdd', 'Site restoration (Backfilling, Grading) - Grading', '120', 'CIVIL', 'ELEC DIST 031', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('a27c5ce6-d0ba-428f-af2e-1b01768df242', 'Rigging/Securing/Transporting', '310', 'Demobilization', 'ELEC DIST 032', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('7da1893e-0657-4c7c-ab14-043f3f731691', 'Re-tensioning guy wires', '100', 'Overhead Construction - Replace', 'ELEC DIST 034', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('4643f8d2-0379-4119-b30e-10086ce2bc14', 'Install switches, fuses, pole mounted transformers', '301', 'Overhead Construction - Replace', 'ELEC DIST 037', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('f5304c43-efbb-4767-84ba-a679c428b0d1', 'Install overhead ground wire and neutral', '300', 'Overhead Construction - Replace', 'ELEC DIST 038', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('43974f5a-8576-49e4-a2b3-7c2caa56b8e2', 'Build duct bank - Concreting', '231', 'Underground - Civil', 'ELEC DIST 039', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('65f285d4-cf2f-4ff5-b490-1deeeea38d94', 'Install vaults/manholes', '400', 'Underground - Civil', 'ELEC DIST 040', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('2b09776f-7c33-46e9-b90c-e28df4320e49', 'Laying conduit', '220', 'Underground - Civil', 'ELEC DIST 041', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('e9ba4860-d0c2-4b84-a4af-4d2b29dc8da3', 'Pulling cable', '210', 'Underground - Civil', 'ELEC DIST 042', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('e57a4ddb-dec3-4aac-836b-b5661428d788', 'Install Ground Fault Indicators', '201', 'Underground - Civil', 'ELEC DIST 043', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('0d43e37f-0c51-4315-9dc4-56d0c6028bba', 'Cut Meter Seal', '320', 'Metering', 'ELEC DIST 044', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('e95730a6-1ca7-4582-95f3-d0fca91644f7', 'Remove Meter', '320', 'Metering', 'ELEC DIST 045', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('3ccbb149-9243-4377-835c-c2ffb7963775', 'Voltage Test', '320', 'Metering', 'ELEC DIST 046', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('744eaba2-7220-4ce1-9b0c-eb1850898926', 'Install meter', '320', 'Metering', 'ELEC DIST 047', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('c28d58f4-d149-4970-b224-7c6350b03972', 'Remove Seal', '320', 'Metering', 'ELEC DIST 048', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('002ddb94-2cc9-4fb5-92a9-76d6f2581e31', 'Install new seal', '320', 'Metering', 'ELEC DIST 049', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) VALUES ('33cb8b7f-fd2f-4b3a-b253-e04c1cc10b27', 'Test/Survey Meter', '320', 'Metering', 'ELEC DIST 050', '33377fa1-dfc5-4149-94a7-feefb6467e75') ON CONFLICT DO NOTHING;"""
        )
    )


def downgrade():
    pass
