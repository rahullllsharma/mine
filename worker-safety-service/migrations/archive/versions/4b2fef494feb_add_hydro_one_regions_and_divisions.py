"""add hydro one regions and divisions

Revision ID: 4b2fef494feb
Revises: dc4e15df1895
Create Date: 2022-09-30 15:22:01.443341

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4b2fef494feb"
down_revision = "dc4e15df1895"
branch_labels = None
depends_on = None

divisions = {
    "8f94ea19-bb4b-46e9-976c-f461c174b23d": "Zone 2 - Southern",
    "c80625e3-5a19-4aa6-bb9d-783461d2023c": "Zone 7 - Northern",
    "7cdb9f05-e9c2-4316-af8d-be1e217bbc47": "Zone 6 - Northern",
    "4d863807-91a1-42e9-be8c-988d9d11238e": "Zone 3B - Eastern",
    "70161eab-9508-4d8e-bf1c-be49bd2c07f9": "Zone 4 - Eastern",
    "8a88a392-01ae-4658-9f56-688300827f37": "Zone 1 - Southern",
    "c6f7e8fe-c8ae-443e-b1d1-06de7664223a": "Zone 3A - Central",
    "c103f290-990e-4644-8bb1-99cf9f443450": "Zone 5 - Central",
}

regions = {
    "241041b0-1eef-4b85-b415-ca7e57cd12db": "Sudbury",
    "e598a9a6-bed2-4f66-a49f-30d5ee393c66": "Listowell",
    "9591e189-be1d-4274-a7c7-51ee26314398": "Perth",
    "12b0676b-c84b-4fce-9af3-6c57596df49d": "Barrie",
    "a396e022-0566-400a-98de-0787a49814a3": "Eary Falls",
    "df2cf003-2003-4d7f-af6a-f72220ec961b": "Thunder Bay",
    "a9bf12eb-71a7-4854-80e1-afba5c190c0f": "North Bay",
    "45f81fe9-e913-43eb-9f38-c2341b86b173": "Orleans",
    "107bd5c0-601a-42f0-aa77-426c078f1b7d": "Beachville",
    "ec40e6ad-c127-4567-8490-872b1e05bc5d": "Kirkland Lake",
    "cf757018-ac33-496e-a3f5-6e1ca30dcbcc": "Huntsville",
    "f4a62b59-58fd-4875-b35e-0a3345220bc4": "Cobden",
    "2a465529-9dd5-44ed-97d1-cc6526a6af92": "Newmarket",
    "349e81b3-71ba-486a-a84b-bbd7418958ca": "Lions Head",
    "d32b20e7-7653-4ca0-a6d9-abd93b831c3c": "Haldimand",
    "b8c40b69-7981-4d67-952c-f77d74033f7d": "Kapuskasing",
    "ab308d81-4303-4330-ae61-8b6e91bc096a": "Dundas",
    "0b6ff73a-e5e0-4c5c-bed2-d89e011ca5dd": "New Liskeard",
    "e44512fb-70be-4bf3-997e-dbaa05ac4118": "Clinton",
    "77cb94da-07c8-4e76-8f71-40b4fbca02f8": "Lampton",
    "0260659a-0a53-49cd-b9d3-9edf34a7b6a5": "Picton",
    "8caa42b8-35d3-47a4-8704-c799cb7bd015": "Project",
    "00254f09-dbb4-4dbf-bf0f-93e4e3422074": "Peterborough",
    "d8274785-c095-494c-a046-b5a9978207c1": "Bracebridge",
    "fa708166-7388-4897-ad2d-9ebd96a2f4b6": "Dryden",
    "991ba367-6791-4f9a-b86f-bfcbcc7545ab": "Manitoulin",
    "9f9111e0-e952-4df7-b9d3-53c5aedb541e": "Owend Sound",
    "98cde154-a5d1-43fd-b707-e1f43cec8217": "Arnprior",
    "1137a9ee-ef9c-4b84-b09f-c2fe74e59dff": "Minden",
    "e07ceeba-a225-44de-87bf-b8fb09d1c9f6": "Parry Sound",
    "f64e6164-671b-4feb-a03e-7465af67beed": "Nipigon",
    "7d3ff63e-783d-43af-a266-e6060971a679": "Aylmer",
    "96c11986-ceba-4089-80df-1bfc19652e42": "Kenora",
    "608960eb-08c2-4ccd-83c4-1345c02b62a8": "Alliston",
    "d3488dbf-d70e-4e8a-82f6-8e1ba99ed3e6": "Barrys Bay",
    "1bfdc316-ba71-47b9-b2d2-1bb3e92782a5": "Woodstock",
    "ec3f9e80-924f-41be-a371-21796761bbf1": "Bolton",
    "6ad8bbbf-aae6-4f24-839a-6b802177a3d5": "Fenelon Falls",
    "e73d7cc7-e400-4f5e-a170-178e3f29cc34": "Kingston",
    "dc6784f2-857d-401d-8261-d92095cac8f9": "Trenton",
    "e32ab559-d2d5-4d10-ac7d-f715dfb10b0c": "Vankleek Hill",
    "0a3a34bb-e949-4f45-954e-e3a7d7474750": "Guelph",
    "5ad56100-f4ef-4285-950f-5b88c9c7e136": "Strathroy",
    "722528cc-2d47-4b6c-b95c-abe85c92786d": "Winchester",
    "eb622170-2d54-4f01-8547-765b8aa36b55": "Penetang",
    "74f1deef-15a8-4169-bbaa-b5a4674e332e": "Tweed",
    "add1277b-1c68-4d30-8607-152f0b10603c": "Bowmanville",
    "c992c1b8-5cd4-4598-a186-5f09b4def999": "Timmins",
    "dec72613-6253-4013-8237-7050ce1af0d8": "Brockville",
    "81b9fc72-ef83-4977-ad27-0a9abfa5f8d4": "Geraldine",
    "322bdd89-2982-45c4-b4a9-401377038f64": "Fort Frances",
    "bb64f991-de87-4b12-afd5-f804949248b9": "Marathon",
    "f9797e45-7a9c-423a-9b20-2349ef77cb19": "Walkerton",
    "4421b4bf-dd88-4d15-abfa-cf4deb0a6ffc": "Orangeville",
    "ec413835-98a5-4429-954d-340726ff5d95": "Thorold",
    "01229ac4-00b0-43dc-b638-1b3931002bd7": "Bancroft",
    "18440667-71c4-4df7-b389-63ce0682e58f": "Essex",
    "36317467-19ac-424a-bb87-b43b989e35a0": "Campbellford",
    "49b67ecd-e4ed-4507-a09f-e1210580da44": "Kent",
    "a5e093c2-4fcb-49db-bd50-1b3aa8a1bad1": "Algoma",
    "212a3e6e-7011-4541-9d6e-382d10255004": "Orillia",
    "01d4c965-1c56-463b-803f-cffe007ae08a": "Simcoe",
    "c8bb95bb-3f5a-4749-b0b9-23449e136552": "NA",
}

hydro_one_tenants = [
    "'3635376a-5635-46c9-a25a-b6d16e5f463a'",  # uat-hydroone - production
    "'0f531133-91fb-4284-935e-436287569a3a'",  # hydro1       - staging
]


def upgrade():
    conn = op.get_bind()
    # get existing tables (this is slow)
    metadata = sa.MetaData(bind=conn)
    library_regions = sa.Table("library_regions", metadata, autoload_with=conn)
    library_divisions = sa.Table("library_divisions", metadata, autoload_with=conn)
    lrtl = sa.Table("library_region_tenant_link", metadata, autoload_with=conn)
    ldtl = sa.Table("library_division_tenant_link", metadata, autoload_with=conn)

    # bulk insert new regions & divisions
    op.bulk_insert(
        library_regions,
        [{"id": str(rid), "name": name} for rid, name in regions.items()],
    )
    op.bulk_insert(
        library_divisions,
        [{"id": str(did), "name": name} for did, name in divisions.items()],
    )

    # link new regions & divisions to hydro-one
    tenants = conn.execute(
        sa.text(f"select id from tenants where id in ({','.join(hydro_one_tenants)})")
    ).all()
    for tenant in tenants:
        tid = str(tenant.id)
        op.bulk_insert(
            lrtl,
            [
                {"library_region_id": str(rid), "tenant_id": tid}
                for rid, _ in regions.items()
            ],
        )
        op.bulk_insert(
            ldtl,
            [
                {"library_division_id": str(did), "tenant_id": tid}
                for did, _ in divisions.items()
            ],
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            f"delete from library_region_tenant_link where tenant_id in ({','.join(hydro_one_tenants)})"
        )
    )
    conn.execute(
        sa.text(
            f"delete from library_division_tenant_link where tenant_id in ({','.join(hydro_one_tenants)})"
        )
    )
    format_divisions = [f"'{division}'" for division in divisions.values()]
    format_regions = [f"'{region}'" for region in regions.values()]
    conn.execute(
        sa.text(
            f"delete from library_divisions where name in ({','.join(format_divisions)})"
        )
    )
    conn.execute(
        sa.text(
            f"delete from library_regions where name in ({','.join(format_regions)})"
        )
    )
