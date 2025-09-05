"""Fix library hazards

Revision ID: 9558ae8dce10
Revises: 573ca3433695
Create Date: 2022-07-14 12:45:56.711846

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "9558ae8dce10"
down_revision = "573ca3433695"
branch_labels = None
depends_on = None

EXPECTED_HAZARDS = {
    "20b5689a-ce74-40f8-a922-e2d5dc9a91f5": {
        "name": "Exposure to high pressure",
        "merge": {
            "24277cc9-c07c-40cb-916a-6fc7fb42909a": "Hoses and equipment under pressure",
            "d80218dc-ca1b-4faa-b318-d9974e8ff728": "Hoses, pipe, and equipment under pressure",
            "208e1317-908b-4930-a360-68a83cc5106a": "Failure of hose fittings",
            "4774d7dc-c7a0-4bd5-a2b0-66fa7159859a": "Hoses, clamps, and fittings coming loose",
        },
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "23041379-366e-4ab2-a0db-a18b569bdafb": {
        "name": "Slips, trips, and falls",
        "merge": {
            "89038c5b-a343-407d-bed6-4f8dd3e874b0": "Slips, trips, and falls due to inadequate lighting",
            "1c17f15a-3933-4468-b567-3e9064fde41e": "Uneven surfaces and debris",
            "5c65958a-266a-4f30-b4fa-1da14312aa54": "Tripping on timber matting",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "affd787b-1e6c-4c9d-a2d4-42d38e9c72b8": {
        "name": "Pinch points",
        "merge": {
            "971151da-656d-437d-a10a-eba7e4003cff": "Pinch points to hands and fingers",
            "2a4671f4-fb14-4b9f-bf4c-d45512ac0135": "Pinch points",
            "ec4c82da-0923-4040-b142-b693bf382d1a": "Pinch point",
            "bbaa12bb-0ef0-4f9e-bd91-fc8417bcba55": "Pinching of hands and fingers",
            "ed7bfa03-5c1e-4c69-9695-33266dbe21fe": "Hands and fingers caught between torque tool and bolt",
            "049a8013-e4c4-4bda-9dde-7a20f317c201": "Pinch points from pounding and prying",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "2330705c-290e-4010-9be4-62e7cb5d0477": {
        "name": "Contact with buried utilities",
        "merge": {
            "325227e4-fef3-464b-a8d2-1e7da2503bff": "Damage to high pressure utilities",
            "01f5f6db-6635-4090-8e0e-9c1ea24c8d82": "Damage to buried electrical utilities",
            "203c1d2a-1831-4a96-b031-e106120c1b3f": "Contact with utilities",
            "271cd95b-4725-47f2-ab54-ce40bcc6a80b": "Damage to other utilities",
            "4336636d-093e-43b4-97ac-10b32ba19dc0": "Exposure to buried facilities",
            "90733cdd-2d60-4819-9738-1274af4e3f2c": "Exposure to buried high pressure utilities",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880": {
        "name": "Biological hazards - Insects, animals, poisonous plants",
        "merge": {
            "be566662-c5ae-45e7-8f02-ea108847b10f": "Insects and animals",
            "3f444e0f-7ea6-4256-acb6-b3a20166652a": "Contact with wildlife / mauling / death",
            "26362139-0c6e-4405-928d-e84b5d1f3895": "Transmission of disease / venom",
            "b6829707-53e0-46bb-bfcd-3b749c7d7e85": "Transmission of venom",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "25a02bff-ad3c-4291-8f57-b7cff5018a88": {
        "name": "Inadequate access and egress",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "29ba89ae-b023-4799-a333-acce29102862": {
        "name": "Fine particulate and dust",
        "merge": {
            "f34fdc2d-5dc2-4db2-852a-275f50fbc580": "Silica and fine particulate",
            "450e2223-58da-431c-8cc1-e09b001e4764": "Particles in eye",
            "72f1cef7-3fd2-42af-8e60-c834b27d4860": "Skin and eye irritant",
            "e6798938-30da-4aab-bc3e-9a8b6ab73759": "Eye and skin irritation",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "98c1f174-ca8d-4c5a-98d7-827ebfc2a1c8": {
        "name": "Exposure to release of stored energy",
        "merge": {
            "5bd09b75-9bc3-4afa-9cf4-012c4efe0dbe": "Explosive release of stored energy",
            "bbf5dbe5-57df-4cfb-a28a-d050a496ce1d": "Stored energy in bent pipe",
            "b8130b46-bc9d-43f9-8749-6e1f4d9cd4ed": "Kick back",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "23b011d4-4cb2-4526-9761-e247d506557a": {
        "name": "Exposure to high dB",
        "merge": {"23b011d4-4cb2-4526-9761-e247d506557a": "Exposure to high dB"},
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "ab2071b5-e299-454a-adf0-f42ac141c936": {
        "name": "Exposure to toxic substances (e.g. asbestos, battery fumes)",
        "merge": {
            "87b77997-08cc-4a49-ad31-22a8353b445d": "Oxygen deficient atmosphere / exposure to CO",
            "ab3e8daf-b193-47fb-9beb-d6b399d4f775": "Hazardous atmosphere",
            "a550e66b-bedc-44e4-82fc-bb24da083a66": "Flammable or toxic atmosphere",
            "a6223133-ffa9-462c-abff-b0e109fc171b": "Exposure to harmful substances (e.g. asbestos)",
            "c7dfba23-7b73-4a35-a2ab-c760c3d48523": "Exposure to hazardous substances",
            "cd6c66ba-a50a-4049-abe6-2fd6693e38dc": "Radiation sickness / injury and / or biological changes",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "604bab16-64c3-4870-bd2e-52ea93e73e9e": {
        "name": "Exposure to extreme heat",
        "merge": {
            "87abca2a-fa66-40c2-b203-7ebfc9b0bbae": "Exposure to hot equipment surfaces",
            "e79c6a50-05e9-4375-9b3d-412dc5172f02": "Heat illness",
            "9d1e99b6-e939-4a57-bb13-ab69dc901053": "Burns/Fire",
            "b967e3e8-ca66-4039-91ee-688f33ac31d7": "Fire",
            "0de4f8b2-b328-49de-9e29-2c41d96b7ee8": "Burns/fire",
            "f9055396-775d-4e0a-af3d-be2b60401814": "Burns from welding and cutting",
            "444fc4b3-3b98-4b08-abbe-dbb799903c4c": "Burns",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "63256499-6af9-4600-8afd-3e9c24b3ea63": {
        "name": "Excavation or trench (>5ft)",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "5075adf0-dc06-485a-9943-113e770334c1": {
        "name": "Cuts and lacerations",
        "merge": {
            "31470545-a49e-4225-9963-b450699e4f33": "Lacerations, metal debris eye hazards",
            "fa5af647-023e-4036-ae46-eea36569a010": "Lacerations",
            "5c1433af-833d-46c2-8343-c1681aa8274e": "Cut by metal shavings",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "cc751338-928a-499a-b1dd-87b9ecc573fd": {
        "name": "Heavy rotating equipment",
        "merge": {
            "a14c123b-057a-4caa-88a2-aec0d378a1fe": "Struck by rotating equipment or material",
            "b01022ea-430a-4ed5-ba3c-c80a4e5d517b": "Exposure to rotating hand and power tools",
            "05c466d4-af6b-4405-96e1-53dbea5d5b5a": "Caught in rotating equipment",
            "b9b412f5-ba59-4a22-bb4e-986489b88684": "Caught by rotating equipment",
            "d2125a81-38bc-4eb5-95a7-0d099068532c": "Exposure to rotating equipment",
            "07a16322-d9f4-49b8-87a3-d30f754da7ae": "Contact with hand and power tools",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "aaf65ad9-2589-488a-87bd-52697e2fdc8b": {
        "name": "Caught in between",
        "merge": {
            "12da934f-0077-40cc-823d-10956ff8954a": "Caught in between bevel machine",
            "655f79c5-8455-416d-8dfb-b286b485a653": "Caught in between matting or road plates",
            "87edc574-5a43-4ca7-a154-cd933b78f505": "Caught in between matting",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "79548b0a-9a11-4a9f-bd66-e1aa601a77d8": {
        "name": "Ergonomic, repetitive motion hazards",
        "merge": {
            "f198b507-80e7-4c4d-a59b-f1f962ac3a05": "Heavy lifting with manual labor",
            "a066ef73-a9ab-452e-bdfc-c7cf5a9cf725": "Improper lifting",
            "376234b2-1346-4e1f-9cb3-057d853b6628": "Heavy lifting",
            "c76648c4-5473-41e7-9058-7e5b079cf1d4": "Heavy Lifting with Manual Labor",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "3c3e7da5-5a46-4ad8-a12c-533555359614": {
        "name": "Arc flash",
        "merge": {"1625a8d4-3330-4a9a-8054-f29948dde211": "Eye Flash"},
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6": {
        "name": "Struck by equipment",
        "merge": {
            "7cbd62ff-c094-4847-a980-ccaf6996adce": "Struck by moving vehicles and equipment",
            "0fe9d64c-4223-4f21-bd66-ab6b38d2ed2f": "Struck by moving equipment and vehicles",
            "58c16421-62fc-4ce4-ac8f-7de43b475958": "Struck by moving equipment and material",
            "9a389c13-b759-461c-91e1-4b9841c22463": "Struck by moving equipment",
            "29873325-60f9-4ada-8590-9ed47bdadc94": "Struck by material or equipment",
            "225a322e-3c38-4285-ace7-da31b9ea5c41": "Struck by falling material",
            "1f35e6ad-063b-44dd-ae08-f8405750ea57": "Struck by equipment / vehicles",
            "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": "Struck by equipment and material",
            "7ca419a8-fa36-43f3-b936-6330a7d7eb39": "Struck by moving vehicles",
            "78bd1d30-057a-47f0-b122-08a8c1f3e12c": "Contact with people, property, environment",
            "e4834f5d-e71c-4140-a47d-67dcdacc3bc8": "Tool striking foot",
            "0c5901fb-896e-4c1b-bc13-013edb2bb538": "Struck by whipping hoses",
            "4a572114-311a-4acd-b85d-5c4a3bceccbf": "Struck by hammer (injuries to hands)",
            "10702f3f-726a-448a-bef6-c160ed05f58b": "Moving equipment and material",
            "6c792f6a-1f89-431a-8a75-944d37d05c44": "Moving equipment",
            "d690719f-f822-4ae5-8cff-c34299d09259": "Moving equipment / vehicles in a congested area",
            "2aee0714-eb88-4cac-9c26-35af3607fa5a": "Struck by shifting or rolling pipe",
            "0ea0c26f-3cf4-4e2d-9e1b-b8399896bbd3": "Struck by pipe / pinch points",
            "34b2d6ee-34b7-4a62-bed5-2dda4e0ca0cf": "Struck by pig",
            "6ef6502b-8311-4338-8785-c11f7f235ecf": "Struck by pipe/pinch points",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "b8ad2b92-18e3-4ba4-a833-cbad42648f0b": {
        "name": "Suspended loads",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "7924f0e9-090a-4121-9e67-ad1e0a9d5998": {
        "name": "Exposure to sharp objects (e.g. rebar, nails, metal debris)",
        "merge": {
            "1720b10f-c28e-4f56-aea1-ca63db3166cf": "Sharp objects",
            "c88475a5-e5fc-48a4-904c-6e54a344f647": "Sharp edges/metal shavings",
            "fa4b2dad-0c14-4dfa-ac5d-a82b5ddceb89": "Power saw",
            "ec37cf5b-26c9-494b-baee-b878ab1cab62": "Impaled by nails",
            "8367b17d-af49-4c8b-acfb-535b72fc0b8f": "Impaled by exposed rebar ends",
            "179c69cf-2762-4b61-ad3b-36aee3ba9c69": "Flying hot debris",
            "ec37cf5b-26c9-494b-baee-b878ab1cab62": "Impaled by nails",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "064e56c8-0024-4cf5-8b11-8acce96c67da": {
        "name": "Falling objects, equipment, debris, dust",
        "merge": {
            "a62c25ba-41a9-4850-b0de-23a33b0e50d2": "Flying debris and dust",
            "d5f817c0-200a-4fc7-9738-65567b514c4c": "Flying debris",
            "7a6c1a11-c920-406f-be16-29781269b581": "Falling objects and debris",
            "e8b47167-e74b-48cd-85bb-5bc367f33732": "Falling equipment",
            "d869805c-e7a8-4ceb-8d04-e0e017487256": "Falling dirt and rock",
            "700671bb-dbd0-4f31-be94-68f83ea3e63e": "Falling debris",
            "4c9a74d2-a290-416e-ad85-ea4129cceb0a": "Exposure to falling debris and objects",
            "3bea337f-0799-4658-b0c3-c60fb79b4c13": "Overhead loads",
            "02a3567f-833e-46a4-8d62-89603dad2f65": "Collapse of scaffold",
            "3f26dd05-7084-4ad2-95a6-1f6b4673e9f0": "Material handling",
            "674a48d5-b9c0-4466-84b0-1a044e17821f": "Falling pipe stems",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "9413f34f-91f8-4ae6-b7bc-c56916977337": {
        "name": "High crime area",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "b1b09768-2194-493f-ab23-1dc0db20ddc0": {
        "name": "Injury requiring medical intervention",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "e1ae99cc-ffd7-46cc-8bdd-2e6bffa37b8a": {
        "name": "Exposure to sub-zero temperatures",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "5a7861e6-948f-451e-8f2e-0c4fc1a2aced": {
        "name": "Electric contact with source (>50V)",
        "merge": {
            "5965c7c9-3ccc-4cd6-b382-8f1b2d413ea7": "Exposure to electrical current",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "6cf6a4fc-b8f9-4335-97c8-c3c8347643d8": {
        "name": "Drowning",
        "merge": {
            "7621c279-b7df-4b91-b53d-646ff65eac97": "Fall into water body",
        },
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "a12b15fd-d553-4eb5-86a6-3d4af789f5c3": {
        "name": "Mobile equipment and workers on foot",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "6f63f138-c0b6-4dca-8cde-e4e1b882fadc": {
        "name": "Lightning",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "78f5391a-d554-45ff-b13a-de230817806c": {
        "name": "Fall from elevation (>4')",
        "merge": {
            "b2e83054-cd9b-4105-ab0f-a7af807b96b2": "Fall to lower level",
            "94f174da-bd95-4a23-8dda-967a04ad4547": "Working at heights",
            "de0cc258-75ed-4271-92c1-254edc1bfede": "Fall to ground ",
            "f423ac41-c9a2-4481-b2c0-b6337ea622e0": "Fall from heights",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "dcf1f3c6-4e43-40da-b8cd-b9094b06cf2f": {
        "name": "Exposure to flying shrapnel, or other sharp objects",
        "merge": {
            "f5122c82-f343-4f0d-93fd-fc4d64c9cb8b": "Shaver",
            "c3d364df-34a4-4606-a343-77da4f35067d": "Masonry saw cutting",
            "bcb1b595-592c-4cd0-9da1-4c4e49fbf062": "High velocity blasting media",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "10dcd38c-60e9-46dc-99cf-5931b343d68d": {
        "name": "Exposure to emissions / pollution",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "894c82ea-4cc4-476d-8eb4-555f53686f7b": {
        "name": "Fire with sustained fuel source",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "be591329-a272-4e0f-8277-98df369fc821": {
        "name": "Static discharge",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "17e26f9f-a273-478e-9b51-097c3f84ea94": {
        "name": "Explosion",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "016a66cb-ed49-469f-a494-facf0fddbeba": {
        "name": "Exposure to high surface temperature (>150F)",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "fd29c2cf-d3b4-4528-a919-d2dc9dbf9a08": {
        "name": "Breaker Operation",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "bb5c5324-d3bc-45da-bfff-5ea78aed8dba": {
        "name": "High dose of a toxic chemical or radiation",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "f48a4c9d-83d2-4eb9-a4d7-95fde05e0173": {
        "name": "Congested work space",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "d450fd01-39a6-443e-9b04-2c0eaaa1e99f": {
        "name": "Equipment Failure",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "a672f799-585f-4005-a515-069f7750c59c": {
        "name": "Back feed",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "c08520e9-bbeb-45c9-a1ad-ee890fb3e71c": {
        "name": "Swinging loads, trees, branches, booms",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "1e49583a-08c8-4ea7-9ff7-4a81b166a753": {
        "name": "Exposure to blinding light",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "46c34c31-2f88-4885-94d2-f973cd3aa963": {
        "name": "Improper use of equipment or tools",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "c320a9da-bb14-4d0b-8998-97ca037cc30e": {
        "name": "Motor Vehicle Incident (Occupant) >30mph",
        "for_tasks": True,
        "for_site_conditions": False,
    },
}


def upgrade():
    connection = op.get_bind()
    db_hazards = {
        str(i.id): i
        for i in connection.execute(text("SELECT * FROM library_hazards")).fetchall()
    }
    duplicated_ids = {}

    for hazard_id, hazard in EXPECTED_HAZARDS.items():
        db_hazard = db_hazards.pop(hazard_id, None)
        if not db_hazard:
            connection.execute(
                text(
                    "INSERT INTO library_hazards (id, name, for_tasks, for_site_conditions) VALUES (:id, :name, :for_tasks, :for_site_conditions)"
                ),
                {
                    "id": hazard_id,
                    "name": hazard["name"],
                    "for_tasks": hazard["for_tasks"],
                    "for_site_conditions": hazard["for_site_conditions"],
                },
            )
        else:
            to_update = {
                key: hazard[key]
                for key in ("name", "for_tasks", "for_site_conditions")
                if getattr(db_hazard, key) != hazard[key]
            }
            if to_update:
                update_columns = ", ".join(f"{i} = :{i}" for i in to_update.keys())
                connection.execute(
                    text(
                        f"UPDATE library_hazards SET {update_columns} WHERE id = '{hazard_id}'"
                    ),
                    to_update,
                )

        # Delete duplicates
        merge = hazard.get("merge")
        if merge:
            for merge_id in merge.keys():
                db_merge = db_hazards.pop(merge_id, None)
                if db_merge:
                    duplicated_ids[merge_id] = hazard_id
                    for table_name in ("site_condition_hazards", "task_hazards"):
                        connection.execute(
                            text(
                                f"UPDATE {table_name} SET library_hazard_id = :library_hazard_id WHERE library_hazard_id = '{merge_id}'"
                            ),
                            {"library_hazard_id": hazard_id},
                        )

    # Migrate merged recommendations
    # On future migrations we are going to fix recommendations
    if duplicated_ids:
        duplicated_ids_str = "', '".join(duplicated_ids.keys())
        to_ids_str = "', '".join(set(duplicated_ids.values()))
        for table_name, column_name in (
            ("library_site_condition_recommendations", "library_site_condition_id"),
            ("library_task_recommendations", "library_task_id"),
        ):
            existing_ids = {
                (
                    str(getattr(record, column_name)),
                    str(record.library_hazard_id),
                    str(record.library_control_id),
                )
                for record in connection.execute(
                    text(
                        f"SELECT {column_name}, library_hazard_id, library_control_id FROM {table_name} WHERE library_hazard_id IN ('{to_ids_str}')"
                    )
                )
            }

            for record in connection.execute(
                text(
                    f"SELECT {column_name}, library_hazard_id, library_control_id FROM {table_name} WHERE library_hazard_id IN ('{duplicated_ids_str}')"
                )
            ):
                column_id = str(getattr(record, column_name))
                library_hazard_id = str(record.library_hazard_id)
                new_library_hazard_id = duplicated_ids[library_hazard_id]
                library_control_id = str(record.library_control_id)
                filter_query = f"{column_name} = '{column_id}' AND library_hazard_id = '{library_hazard_id}' AND library_control_id = '{library_control_id}'"
                record_key = (column_id, new_library_hazard_id, library_control_id)
                if record_key in existing_ids:
                    connection.execute(
                        text(f"DELETE FROM {table_name} WHERE {filter_query}")
                    )
                else:
                    existing_ids.add(record_key)
                    connection.execute(
                        text(
                            f"UPDATE {table_name} SET library_hazard_id = '{new_library_hazard_id}' WHERE {filter_query}"
                        )
                    )

    # Fix audit
    for record in connection.execute(
        text(
            "SELECT id, old_values, new_values FROM public.audit_event_diffs WHERE object_type IN ('site_condition_hazard', 'task_hazard')"
        )
    ):
        to_update = {}
        for attribute in ("old_values", "new_values"):
            values = getattr(record, attribute)
            if values:
                library_hazard_id = values.get("library_hazard_id")
                if library_hazard_id:
                    to_library_hazard_id = duplicated_ids.get(library_hazard_id)
                    if to_library_hazard_id:
                        values["library_hazard_id"] = to_library_hazard_id
                        to_update[attribute] = json.dumps(values)
        if to_update:
            update_columns = ", ".join(f"{i} = :{i}" for i in to_update.keys())
            query = f"UPDATE public.audit_event_diffs SET {update_columns} WHERE id = '{record.id}'"
            connection.execute(text(query), to_update)

    # Disable other hazards
    # We don't delete it because we don't know for what it should be migrated
    if db_hazards:
        library_hazard_ids_str = "', '".join(db_hazards.keys())
        connection.execute(
            text(
                f"UPDATE library_hazards SET for_tasks = :for_tasks, for_site_conditions = :for_site_conditions WHERE id IN ('{library_hazard_ids_str}')"
            ),
            {
                "for_tasks": False,
                "for_site_conditions": False,
            },
        )

    # Now let's delete the library hazard entry
    if duplicated_ids:
        duplicated_ids_str = "', '".join(duplicated_ids.keys())
        connection.execute(
            text(f"DELETE FROM library_hazards WHERE id IN ('{duplicated_ids_str}')")
        )


def downgrade():
    pass
