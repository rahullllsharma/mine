"""seed work_type_ids to library_task

Revision ID: bc639a411cc2
Revises: fd04d01d1510
Create Date: 2022-10-06 16:04:21.100080

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "bc639a411cc2"
down_revision = "fd04d01d1510"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """UPDATE library_tasks set work_type_id='5f12b55b-710f-4613-92f6-48bf0448c025' WHERE id in (
                'a6c64af7-4968-452e-9501-b2b1f050cbf6',
                '7b79a1b8-fe2c-4fe5-94a0-81409c033212',
                '35a07126-c052-4f57-b386-95581220cf05',
                '1d4de35b-2025-4fd4-b9f9-e6f29548c304',
                'e7c23039-78b3-46be-ab03-844a3140f358',
                '8d379ebc-493e-48ab-a519-a201359d0ad7',
                'a3de1387-17a5-4b9f-a6ea-391990d4a199',
                '195f89bf-b80a-4853-8c73-972017ba8a50',
                '238d46eb-72ba-47ee-8742-99ed25567366',
                'c0406c51-8e6f-4e27-bf72-cf80ac508277',
                '13973c9b-95e5-424c-b2ca-930682b57cbd',
                '20758fec-c71a-4954-b1fa-6284e6782afc',
                'bf77f03b-0088-4161-b20d-2e12681693a5',
                '2593f81a-3c6a-4916-8590-51fc9b934207',
                '9c924f91-1675-42e7-b62d-8cca55a6e4c0',
                '7a16673f-0ef8-4d12-8d33-9586cbfe1f54',
                '199ce778-1eed-4a6f-9401-3fefe1b1baac',
                'b48e5589-9674-41eb-91f0-e4e7777cf4b2',
                'f859c660-0513-4470-9d86-06c5c9643314',
                '7a91aaf5-b54f-4586-ab38-66d0bb3b22bd',
                'a36c2136-e8ad-45e7-a32e-1f515edca089',
                'ee5fe360-3225-4deb-a51e-441ccddce65d',
                'eebe5e56-d8c2-4816-b819-3ba0da0d6566',
                'ff20527c-5375-4bb6-91e0-b280e9d6ffca',
                'aa5c660c-2a51-40c4-bbf4-4543052ec064',
                '77cc07b4-fdcf-4a2b-a5e0-cc77e8c4ecc4',
                '9464aee6-1ddb-4e65-94e2-6007fabeea02',
                '9748890b-d2da-4371-b324-a6570a4d22f2',
                'c0e9be57-d54a-4b59-8710-3ff9d964e414',
                '22232ece-c66b-45db-9dd1-162c3c92d017',
                '07236ab1-19c5-439d-8403-d5d544f31ab5',
                '69bfb299-4543-4292-98bd-c52d05319666',
                'beb35c74-0e4e-443c-8061-b91eb35d4bed',
                '48253a67-cad2-4fe0-bce8-9089465936e0',
                '66ef2d32-22fe-4a07-8d6c-2dde41a9df50',
                '9071983c-5123-475f-9f1c-351c6756a5a5',
                'ec04a3b9-8029-428d-95fe-62ae33873cd2',
                '422df780-6c14-4321-8525-32853c93b712',
                'a1b21057-f86f-466a-bdce-1a2fafc4bfdd',
                '1e2a329c-a413-41a4-90f3-9c2d6f3fe6b3',
                '88b99733-ead6-4278-917f-bc1b72442a35',
                'c2fed5e6-58c5-4b6b-b299-09d617f99f39',
                '637eba71-e353-42cc-8be8-7f40ad440514',
                '4880814a-ec17-4825-8757-67d8ff7862df',
                '8e0a24ec-0575-4a33-a4bd-ff1795b390f3',
                '85c2c126-7d1c-4e39-8d73-03ebbf894804',
                '24a278d2-7563-4030-8d0e-c68c67523290',
                'f89ac6f3-7598-490c-98e8-07b5986fcd0c',
                '9ef25e64-91ba-430d-9e24-e0d6f9ad561b',
                'c7f383d0-c01e-43fc-8d62-c262862aca69',
                'ac1e15a5-7021-48a6-a88d-b9799b6355ea',
                '29a8acf6-8312-4f26-b773-7908d67d437f',
                '3dc04aa4-58b9-40b2-a34b-bb3c59d91120',
                '9d9464e3-c15d-4653-b2dc-25959015bb61',
                '2ce1dddc-72d6-4fae-b639-f855171abf00',
                '7b9bcd4f-cc64-48eb-8d38-ab8988dda7f6',
                '23631748-7c0c-48f0-b0f8-e7e7bc676c18',
                '4609fbd4-c55b-4cdc-9302-7c0a8794643f',
                '450a47f4-a174-47d4-8c46-54d2fc12555f',
                'b0702e49-5604-4c8a-a0b6-8bd51ba1db68',
                'ed0a3403-fa19-460b-b2fe-32ca0d1063e1',
                'f4202f63-3ec3-442a-8c44-788d8d9c8fee',
                'd280ee9d-ad2d-4a83-8af8-f61bca0a7057',
                'd8217652-973e-4216-aea5-28ced89eac26',
                '01baa494-99c5-43bf-aa8a-53a6f4732924',
                '335ca6b6-798b-4a21-9825-5cb499154f45',
                '590f0c15-1ff2-4de1-9488-124388f94fd3',
                'e0d4426a-400b-48b3-abdc-940648d53c28',
                '9d37a2f3-d5c4-4cbf-839c-96ef5fc4c497',
                '3fc9c105-f594-41be-9f24-c5c74cb495ad',
                '27a4547a-3167-4087-be03-cc7568097936',
                'a180f2d7-213c-4b12-8bfe-6640e4c47e98',
                'ef47dd41-2502-4659-98b4-9bfe12d2198b');
"""
        )
    )
    conn.execute(
        text(
            """
    UPDATE library_tasks SET work_type_id = '43974dda-0338-4e76-9856-2a76a472fda5' WHERE id in (
        'ad7a3d5c-ea72-45ed-a849-96540c68d337',
        'b1738bbd-1570-482d-91ee-ad64ccfb3aea',
        '37a72bab-91b2-41b4-bd83-107a5a4b4951',
        'ed717165-b18b-4f07-ba6a-f4a4e046123b',
        '223b04e9-62fa-4cf9-97f7-42d7e63994f0'
    );
"""
        )
    )
    op.alter_column("library_tasks", sa.Column("work_type_id", nullable=False))


def downgrade():
    op.alter_column("library_tasks", sa.Column("work_type_id", nullable=True))
