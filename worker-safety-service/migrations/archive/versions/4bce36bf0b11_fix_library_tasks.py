"""Fix library tasks

Revision ID: 4bce36bf0b11
Revises: 42e6d3e6b268
Create Date: 2022-07-25 20:33:36.449798

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "4bce36bf0b11"
down_revision = "42e6d3e6b268"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO library_tasks (id, name, hesp, category, unique_task_id) VALUES
            ('ef47dd41-2502-4659-98b4-9bfe12d2198b', 'Material handling', 140, 'Material handling', 'GASTRANS016')
        ON CONFLICT DO NOTHING;
        """
    )
    op.execute(
        "UPDATE library_tasks SET name = 'Above-ground welding - Pipe face preheating / Post weld heat treatment' WHERE id = 'f859c660-0513-4470-9d86-06c5c9643314'"
    )
    connection = op.get_bind()
    connection.execute(
        # Locates / Mark-outs
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '37a72bab-91b2-41b4-bd83-107a5a4b4951'"
        ),
        {"hesp": 44},
    )
    connection.execute(
        # Surveying & staking
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'ed717165-b18b-4f07-ba6a-f4a4e046123b'"
        ),
        {"hesp": 21},
    )
    connection.execute(
        # Clearing & grading
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '223b04e9-62fa-4cf9-97f7-42d7e63994f0'"
        ),
        {"hesp": 216},
    )
    connection.execute(
        # Matting install / removal
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '7b79a1b8-fe2c-4fe5-94a0-81409c033212'"
        ),
        {"hesp": 305},
    )
    connection.execute(
        # Excavation of road / subsurface
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '35a07126-c052-4f57-b386-95581220cf05'"
        ),
        {"hesp": 31},
    )
    connection.execute(
        # Excavation of soil (using means other than hydro-vac)
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '1d4de35b-2025-4fd4-b9f9-e6f29548c304'"
        ),
        {"hesp": 230},
    )
    connection.execute(
        # Timber shoring install / removal
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'e7c23039-78b3-46be-ab03-844a3140f358'"
        ),
        {"hesp": 203},
    )
    connection.execute(
        # Excavation of soil using hydro-vac
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'a3de1387-17a5-4b9f-a6ea-391990d4a199'"
        ),
        {"hesp": 54},
    )
    connection.execute(
        # Vertical drilling / core sampling
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '195f89bf-b80a-4853-8c73-972017ba8a50'"
        ),
        {"hesp": 155},
    )
    connection.execute(
        # Tieback install/removal
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'c0406c51-8e6f-4e27-bf72-cf80ac508277'"
        ),
        {"hesp": 245},
    )
    connection.execute(
        # Loading / unloading materials (e.g., pipe, fittings, valves, etc) during receiving / staging / demobilization
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'a180f2d7-213c-4b12-8bfe-6640e4c47e98'"
        ),
        {"hesp": 131},
    )
    connection.execute(
        # Rigging and lifting activities - Non-critical lift
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '13973c9b-95e5-424c-b2ca-930682b57cbd'"
        ),
        {"hesp": 141},
    )
    connection.execute(
        # Rigging and lifting activities - Critical lift
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '20758fec-c71a-4954-b1fa-6284e6782afc'"
        ),
        {"hesp": 321},
    )
    connection.execute(
        # Field bending pipe
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'bf77f03b-0088-4161-b20d-2e12681693a5'"
        ),
        {"hesp": 147},
    )
    connection.execute(
        # Torquing / bolt up (Using wrench tool)
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '2593f81a-3c6a-4916-8590-51fc9b934207'"
        ),
        {"hesp": 66},
    )
    connection.execute(
        # High Torque / bolt up (Using high torque machine)
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '9c924f91-1675-42e7-b62d-8cca55a6e4c0'"
        ),
        {"hesp": 93},
    )
    connection.execute(
        # Cut and remove existing pipe
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '7a16673f-0ef8-4d12-8d33-9586cbfe1f54'"
        ),
        {"hesp": 172},
    )
    connection.execute(
        # Above-ground welding - Pipe face preheating / Post weld heat treatment
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'f859c660-0513-4470-9d86-06c5c9643314'"
        ),
        {"hesp": 46},
    )
    connection.execute(
        # Above-ground welding - Pipe face alignment
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '7a91aaf5-b54f-4586-ab38-66d0bb3b22bd'"
        ),
        {"hesp": 15},
    )
    connection.execute(
        # In- trench welding
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'ee5fe360-3225-4deb-a51e-441ccddce65d'"
        ),
        {"hesp": 323},
    )
    connection.execute(
        # Grinding
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'ff20527c-5375-4bb6-91e0-b280e9d6ffca'"
        ),
        {"hesp": 66},
    )
    connection.execute(
        # Tie-ins / hot tapping (Steel, cast iron, plastic)
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'c0e9be57-d54a-4b59-8710-3ff9d964e414'"
        ),
        {"hesp": 252},
    )
    connection.execute(
        # Purging gas
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '22232ece-c66b-45db-9dd1-162c3c92d017'"
        ),
        {"hesp": 165},
    )
    connection.execute(
        # Install pipe - Boring / HDD
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'c2fed5e6-58c5-4b6b-b299-09d617f99f39'"
        ),
        {"hesp": 402},
    )
    connection.execute(
        # Install large diameter pipe (>12") - Open trench / above ground
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '637eba71-e353-42cc-8be8-7f40ad440514'"
        ),
        {"hesp": 302},
    )
    connection.execute(
        # Install small diameter pipe / fittings (<=12") - Open trench / above ground
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '4880814a-ec17-4825-8757-67d8ff7862df'"
        ),
        {"hesp": 104},
    )
    connection.execute(
        # Vault installation
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '85c2c126-7d1c-4e39-8d73-03ebbf894804'"
        ),
        {"hesp": 316},
    )
    connection.execute(
        # Confined space entry
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = 'ac1e15a5-7021-48a6-a88d-b9799b6355ea'"
        ),
        {"hesp": 138},
    )
    connection.execute(
        # Install fences and/or barricades
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '2ce1dddc-72d6-4fae-b639-f855171abf00'"
        ),
        {"hesp": 23},
    )
    connection.execute(
        # Demo of retired facilities
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '7b9bcd4f-cc64-48eb-8d38-ab8988dda7f6'"
        ),
        {"hesp": 84},
    )
    connection.execute(
        # Structural fabrication / assembly
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '23631748-7c0c-48f0-b0f8-e7e7bc676c18'"
        ),
        {"hesp": 246},
    )
    connection.execute(
        # Micropile installation
        text(
            "UPDATE library_tasks SET hesp = :hesp WHERE id = '450a47f4-a174-47d4-8c46-54d2fc12555f'"
        ),
        {"hesp": 237},
    )
    connection.execute(
        # Driving equipment and vehicles
        text(
            "UPDATE library_tasks SET unique_task_id = :unique_task_id, hesp = :hesp WHERE id = 'ad7a3d5c-ea72-45ed-a849-96540c68d337'"
        ),
        {"unique_task_id": "GENERAL001", "hesp": 10},
    )
    connection.execute(
        # Traffic control (Site set-up)
        text(
            "UPDATE library_tasks SET unique_task_id = :unique_task_id, hesp = :hesp WHERE id = 'b1738bbd-1570-482d-91ee-ad64ccfb3aea'"
        ),
        {"unique_task_id": "GENERAL002", "hesp": 101},
    )


def downgrade():
    pass
