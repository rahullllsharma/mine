"""Fix library controls

Revision ID: 0328b833a037
Revises: 9558ae8dce10
Create Date: 2022-07-14 19:48:56.710702

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "0328b833a037"
down_revision = "9558ae8dce10"
branch_labels = None
depends_on = None

EXPECTED_CONTROLS = {
    "cf25cc91-be50-4117-aced-c8a8f83db846": {
        "name": "Work positioning device/restraint",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "ef04b4a5-9196-4122-b6f4-0b787190dff0": {
        "name": "360 walk around",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "9445a787-c4cb-4fb2-8a49-1b9947f55876": {
        "name": "Machine guards",
        "merge": {
            "48319073-8386-49c9-9bab-735def7b1872": "Do not wear loose fitting clothes",
            "0899d101-6a06-41f4-910e-1fbba2de1458": "Handle",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "6abcda1e-947c-4f1e-b913-18bc96c23334": {
        "name": "Safety glasses",
        "merge": {
            "f42676bc-01c7-4f57-a55b-8c07b5904c56": "Eye protection",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "c2efdade-aac5-40c6-aa29-34687d2114f3": {
        "name": "Hard hat",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "d8251088-33df-44b9-8286-3e11d80645d1": {
        "name": "Hearing protection",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "5ddd6a21-1f39-45fc-af9d-1dc783eba9a5": {
        "name": "Respirator",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "8b1698a3-a055-499c-95e5-56059e3cdd89": {
        "name": "Fill in gaps and holes in mats",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "610c3314-762f-4985-9701-6cfe44059cd8": {
        "name": "Pressure relief devices",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "8b781386-e309-44d5-9b8d-35230f80119a": {
        "name": "PPE as directed by SDS",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "496344fb-1c4d-4b89-bc32-9ba7b50f619e": {
        "name": "Stairways, ladders, ramps placed no more than 25’ laterally from one another",
        "merge": {
            "097a4aec-a6b7-4e3c-8862-b927ab19a93f": "Ladders",
            "2cef1dab-d0bd-4c3c-a0b8-79ff3e67b6d1": "Proper ladder usage",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "42c7d15f-00c4-49cc-bcce-7e58927d09b6": {
        "name": "Automatic shut-off",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "6f005259-0fc3-4fd2-bcf7-b2bf67d44766": {
        "name": "Cover up",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "8d9dc6bf-cb00-4d8d-bcfe-9aa498fc2de3": {
        "name": "Trench box",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "7bd1b8f8-020a-46bd-bff0-d4fba5910cac": {
        "name": "Impact rated gloves",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "bc886bd6-602f-49d5-8508-01b987fe7ed7": {
        "name": "Proper communication",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "845518bd-2a56-47c7-92d7-220087939243": {
        "name": "Exclusion zone",
        "merge": {
            "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": "Situational jobsite awareness",
            "4ad1bc4a-ec30-4246-8796-23315c9d9f88": "keep hands away from bender head",
            "9ad431e2-a945-4e5a-8108-64a734717dfa": "Maintain an exclusion zone around excavator and loading trucks",
            "e767c285-3f2d-4b59-a7fa-881921ba5317": "Placement of sandbags or timber skids",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e": {
        "name": "Cutting goggles",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "1b79d139-38b2-44f7-aefc-e2871e2d46d9": {
        "name": "Gas detection monitoring",
        "merge": {
            "8358a4b3-7972-441d-918f-dbdb6b8a836f": "Gas detectors",
            "cfd7b6a5-45f2-42d2-83ce-f6426667095b": "Continuous atmospheric monitoring",
            "8241c09d-c55b-4953-984e-ca6ca8154098": "Wind direction",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "ddb617a0-9e06-4599-9b99-3e36e7b5ee28": {
        "name": "Controlled access zone",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "ea323b12-7f98-4064-873c-92886cef07ec": {
        "name": "Full face UV protective shield",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "dc925cd9-a7bd-4a68-b61b-389fe09289d9": {
        "name": "Seat belt and airbag",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "f5fb0d9d-1e01-42b7-835e-7c5e46482119": {
        "name": "Radiation shielding",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "62ca2539-c0c4-4920-aca8-60e8536e725d": {
        "name": "Spotters",
        "merge": {
            "d31a11ea-37e9-44c0-8d8b-17ddf95f0850": "spotters",
            "c8bdcb66-e7e4-440b-aea9-6cb4fd97cd38": 'Use a spotter to maintain at least 12" clearance from utilities',
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "98d73996-ac36-4dbd-8b6c-fa2682c421d4": {
        "name": "Sloping and benching",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "23d96813-1901-4a25-b6d7-5579a2799a10": {
        "name": "Asbestos abatement",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "08bbff19-ce5b-47c1-a680-4cd5d6d8866f": {
        "name": "Correct lifting procedures and techniques",
        "merge": {
            "4df673d5-943d-481f-83e7-cf0f0e6f7b47": "Lift plan",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "1f9a5ff0-3394-4895-b45c-089ac6643003": {
        "name": "Tool that forces safe distance/MAD",
        "merge": {
            "5224cf50-d219-4f8b-a5e3-7e652b6e648f": "Safe limits of approach",
        },
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "4092d3b1-67d7-495b-84b4-de224a1b9894": {
        "name": "Training",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "730d586c-f9fc-48c2-bab9-018e5474b81c": {
        "name": "Cut resistant gloves",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "8aac579e-b59c-4252-8939-c799b7f9166d": {
        "name": "Firefighting equipment (e.g. extinguisher, shovel, ax)",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "33e934a7-c837-4a28-b896-9e4612a6c810": {
        "name": "Fire-resistant (FR) clothing",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "f52b676d-516e-4068-8878-050dfb32313f": {
        "name": "Police detail",
        "merge": {
            "dcbbe649-9372-4f75-9cea-14cccbd29523": "Pre-inspection checklist",
            "803d7f67-8c8f-459b-80b9-7dae729caa02": "Security presence",
            "3df87226-b750-4993-934d-3bf0e7a52301": "Secure jobsite",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "a1944ad5-2895-436f-afa9-9a752dd81ecc": {
        "name": "Isotopes stored and handled properly",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "8897d760-3e77-499b-a3b8-ef060ac5fbd9": {
        "name": "Safety toed footwear",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "b4380ba8-f086-4c83-b3f6-876d94d00239": {
        "name": "Radiation monitoring",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "d9b46efa-f00e-4ac9-b550-0541dda61246": {
        "name": "Exhaust fans",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "253829fa-56ea-40a7-a938-cceee82cd7d6": {
        "name": "Use of rebar caps",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "359a02e2-7330-4175-a5b6-ef918e7d4158": {
        "name": "Grounding",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "52182601-b5ef-4526-ad02-5d63f5b75e84": {
        "name": "Insect repellant",
        "merge": {
            "4a13e5ed-a01f-4181-820b-22117e0558ab": "Repellants",
            "23b51248-40b2-4d23-9a17-a23618f71f7b": "Vegetation clearing",
            "cb16a961-0c90-4b53-8ec7-fc5be0fdd59d": "Jobsite inspection",
            "a212e2a9-cd72-4399-ac1e-73b2011fd517": "Bears / Mountain Lions awareness training",
            "c6bf3348-5b7c-4ff9-87ab-aaba79aaf4a8": "Self checks",
            "013671f3-75d8-49a6-b325-469663b04b4b": "Store food in bear-safe containers",
            "26fc35ae-ab0e-42bd-aecc-70ae333e1ab4": "Poison",
            "cfa2cc28-d8ed-4f62-b044-fa58f4712eb4": "Knowledge of allergies and treatment",
            "658a85c0-091a-42e1-a39b-d0d722b56f50": "Electric fence",
            "5ec8d174-e46c-44f3-832b-5e0c8020d0b4": "Boots",
            "66927a93-240a-4534-88d9-4ca43c834ef6": "Bite resistant clothing",
            "cc3f773f-b107-4fdc-8523-11c735ef28b4": "Bear spray",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "6c9d1d49-53f1-4baf-a382-abcb11d9f40d": {
        "name": "Hydro-vac",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "7d39bcf4-6f3d-4daa-914d-6335018fbcf8": {
        "name": "Stretch and flex",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "b4affcfd-2c5a-471e-bf27-61d20dac834b": {
        "name": "Bend over protruding nails",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "fdfdc2f6-af19-413b-aacc-e0819cae5f5d": {
        "name": "Double rigging/redundancy",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "0f2534da-adad-4dab-a700-8d1493f5ba82": {
        "name": "Fall protection",
        "merge": {
            "0e9a05da-6753-42ce-aa0e-0448c397c4e8": "Guard rails",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "1f482f5a-820b-4710-8ecf-d6a816d6e96b": {
        "name": "3 points of contact",
        "merge": {
            "c9eb9013-7801-4a47-ade5-509eec23c5ae": "Traction control footwear",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "53a4afff-cfd5-4b30-89af-3d875f62722a": {
        "name": "Whip restraint",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "f03198ec-d56a-434b-aa72-f21a7e80eed2": {
        "name": "Mechanical steak driver",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "9e21d7c7-3276-406e-951e-a710c5c3f35a": {
        "name": "Housekeeping",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "873def37-dd23-4abe-acdb-81eab0602c08": {
        "name": "Work rest cycle",
        "merge": {
            "48024368-7a73-4440-a062-5965f3156eb3": "Hydration",
            "0ca8ae31-79c3-4357-b81b-bd161c2e221b": "Cool down stations",
            "cbac5c9a-ae06-4c4c-8190-c00e3136a610": "Cold weather rated clothing (boots ,  gloves,  etc)",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "b4b3b004-49a6-4471-84d6-7b6d0a4a7004": {
        "name": "Flash protection boundary with hard physical barriers",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "a033267d-7322-42c8-b011-4015d68b2bc2": {
        "name": "Insulting gloves, sleeves, shoes, etc.",
        "merge": {
            "09cf14aa-3069-469a-ae4a-d2bb7e50d767": "Welding gloves",
            "5d06c932-2434-4990-8609-45afc42f9864": "Pipe holders",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "0707486a-fd22-4959-887c-a0cd930ec087": {
        "name": "Chaps",
        "merge": {"257a7f05-942d-4405-8dd4-6ba5cd9ff7b3": "and chaps"},
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "e92f3626-be91-47da-b197-77e6154f5a15": {
        "name": "Inspection",
        "merge": {
            "712c64dd-9f74-4a8a-9dcd-3b55bfe5bb0c": "Inspect ladders and scaffold",
            "8035cbfb-4b42-4c1f-9ae3-b8f57983660b": "Inspect equipment",
            "eb982aae-a4a6-4f8b-b5b9-418f9df86b22": "Pre-shift inspection",
            "59052adf-ceb6-48af-9884-751a9cc07903": "Inspect hoses and fittings",
            "5ad9c296-febb-41b1-bd83-c21910101a10": "Inspect rigging",
            "00cf6e41-877a-480a-974a-7eea86e66486": "Inspected and erected by trained and competent person/s",
            "d1a3a929-254a-4dbe-82b4-2c9272a8481a": "Inspect all electrical cords and ensure proper grounding",
            "5ebf83da-3097-4739-8f5c-28fb21a4e124": "Inspect all equipment and ensure proper guarding",
            "a9b4b502-cc1b-43b6-8c7e-9e5a15e4f1e7": "Lighting",
            "da3696b1-530b-4fc0-a624-9fbc77c26b00": "Competent person inspect excavation before each shift",
            "d6655e42-e43b-404d-bdac-e55cc37205a1": "Pre-job coordination",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "ff161bca-e057-4045-a3fe-708b6569ab8a": {
        "name": "Lock-out tag-out (LOTO)",
        "merge": {
            "b9be969d-9811-4546-8494-13f95f63fa0e": "Walk down of isolation points",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a": {
        "name": "811 locate tickets in place and utilities clearly marked",
        "merge": {
            "2840b102-d910-4cb3-80cc-b0aba53c74ec": "Locate control lines",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "25ae5c04-3dab-4c7d-bf0d-2317fd997619": {
        "name": "Face shield",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "2c285dc8-124f-4ebb-b913-3ca8ebf49f5a": {
        "name": "Traffic control zone with physical barriers",
        "merge": {
            "bc5a8143-674b-4c22-a6ba-7999fe27a867": "Fencing / barriers / signage",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "c8202f22-79a8-4037-b566-5c7ea9dfe935": {
        "name": "Traffic control devices (eg. barricades, delineators, signs)",
        "merge": {
            "b22839ca-d7a1-4308-88ab-11d617bcdbff": "Adhere to traffic control plan",
        },
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "058e7079-eb40-4b9d-a02a-126102ea8322": {
        "name": "Life jacket / buoyancy aid",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "a1331fdc-0331-4ef0-984a-3acaa5c3b8e7": {
        "name": "Covers over holes",
        "merge": {
            "b860c7d1-ceb3-456a-bf46-7b78319034bc": "Mark out tripping hazards with orange paint",
        },
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "1a4fcf20-634f-4959-bf07-7baef3cbcd55": {
        "name": "Electrical isolation and grounding",
        "merge": {
            "14652da3-051a-4ff9-b7d1-34ea9ed4be81": "Goal post",
        },
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "54e26d98-c66d-45fb-929c-d6c7c2dc7d31": {
        "name": "Emergency response plan",
        "merge": {
            "7b762a64-300d-4d12-b476-679ff208b8ae": "First aid training",
            "7c1faa79-f11e-494f-92c7-e1cd11830174": "Radio / satellite communications",
            "5c405e26-7c53-4843-b6fe-3c41be279098": "Defibrillator",
        },
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "3305bcf8-5a86-4206-855e-604c33546100": {
        "name": "Shelter area",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "946381c0-6040-4576-b1c9-dbd9d6a607d1": {
        "name": "Drop zone",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "4ccb55b6-34d4-4bd7-b0e1-4d84a4018520": {
        "name": "Ground tracking system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "97066ea2-1ef9-447c-85aa-e04f23f8c7da": {
        "name": "Fire blankets",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "4ae1251c-d1ea-4ed1-b0b5-9a27b800ff3e": {
        "name": "Hard physical barrier",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "4c2ff3f4-5c1b-4022-a3fa-8917246c6a37": {
        "name": "Dust abatement",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "2f25f1b4-2fa2-47f6-b478-2cfe145d3f4a": {
        "name": "Motor control center (MCC) panel enclosure",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "acf79932-d38e-43f8-96b7-a2ab7711cbdb": {
        "name": "Hotline sticks",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "4ff781dd-8f2e-47ef-91b0-132ecfdee586": {
        "name": "Safety vest",
        "for_tasks": True,
        "for_site_conditions": True,
    },
    "ea909801-3911-44e8-a00d-a734892db9b7": {
        "name": "Pressure release valve",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "89fe7159-5576-4696-9356-75a34e8da4ea": {
        "name": "Vibration resistant gloves",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "21def986-03d8-4f81-a5c6-9e8c5c4ecedf": {
        "name": "Steam suits",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "3fea8b7e-2712-40a7-9a73-332a26cf397e": {
        "name": "Self-retracting lifeline",
        "for_tasks": False,
        "for_site_conditions": True,
    },
    "80391027-0232-4e5e-9633-e0078b846b03": {
        "name": "Proper bonding of materials",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "a0950811-11e6-4f48-b4e6-7e99ca98f4ed": {
        "name": "Hoist break",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "02a2b6d9-6615-4408-9740-7638b4f68423": {
        "name": "Local ventilation",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "63b91dec-9934-46c6-ac90-782284bb3dd6": {
        "name": "Surface insulation",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "0b3a5e47-7edd-4515-8d2b-50b2a0068cf9": {
        "name": "Active cooling system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "6feddda5-4ba9-459b-8aa3-335bccb66eba": {
        "name": "Sprinkler system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "3adf7a3a-8b6f-41ab-8e34-64f2bbc959c6": {
        "name": "Equipotential zones",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "000fb3b7-df08-450b-a96a-f5d181dad37c": {
        "name": "Flash-rated equipment (suit, glasses, face shield)",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "72259630-a8c0-4ff7-b931-5006a53f3d5a": {
        "name": "Area curtains",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "9146e674-044f-415c-a367-b72675befc88": {
        "name": "Labeling",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "08147bb3-98a3-469f-87c3-8ce969bf22a1": {
        "name": "Load limiting devices",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "ff3d5da3-84b6-4022-a533-a4094423b8ed": {
        "name": "Inerting to exclude O2",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "e97d0d5c-4e40-435a-ad26-879fba56958c": {
        "name": "Fuel source separation",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "ee1ecee4-3e4d-4f79-a757-b953c0c1b3f8": {
        "name": "Explosive ordnance disposal (EOD) suit",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "5703e161-bf0c-46a4-bd1a-34378e8233b5": {
        "name": "Roll cage",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "4c51e9cb-0bce-49cb-a3e0-2362864013eb": {
        "name": "Self contained breathing apparatus",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "8bed5e34-6430-46aa-b31f-b068080ca543": {
        "name": "Proper storage of hazardous / radioactive substances",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "82535dbe-142a-4b6e-93d1-bebe078e560a": {
        "name": "Air bag",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "cd8547c6-f097-421d-80e1-10aea991f6f9": {
        "name": "Machines with sensing devices/auto-shutoff",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "897af0ed-1181-440c-8f9b-9ec8161a6155": {
        "name": "Insulating barriers",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "96cd2365-cba8-45f3-a909-8805a359e260": {
        "name": "Remote fuel shut off",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "9c8907e3-7f4c-45c9-91b5-122d9d1722f5": {
        "name": "Rated rigging equipment and attachment points",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "8282db17-1e36-4022-b03b-0d81a6815d13": {
        "name": "Heat resistant clothing/thermal suits/kevlar sleeves",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "fdc8d6bf-a966-4d13-8c52-4101aa5058c5": {
        "name": "Tool tethers",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "92bbf08c-be1c-4a19-8b7c-65ff1f8350cd": {
        "name": "Ground fault circuit interrupters",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "08b4618d-b0b9-4b32-8c56-3f322c3c42c6": {
        "name": "Rupture discs",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "85abffe4-0558-462b-b17f-65d8f6ecb910": {
        "name": "Proper signage",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "925b15dc-4e0e-42ab-9fab-3b8eb128a414": {
        "name": "Boom angle sensors/limiters",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "3cc421b0-1a2d-4750-b308-ed0ceaa0a200": {
        "name": "Relief valve",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "d70916ec-4afc-4d6f-bba9-0f88b3edcee9": {
        "name": "Collision avoidance system",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "52151cc5-0110-41e6-8109-a2adec515524": {
        "name": "Gary guard",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "fdb3e8e9-cf7b-4da5-99bf-bc815e20f042": {
        "name": "Blast blanks",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "cb624eaf-2cda-4558-8c8a-d1778ec9df6e": {
        "name": "Insulated and/or voltage-rated equipment and tools",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "be579806-35df-41d4-988f-43c773c10f37": {
        "name": "De-energization w/zero voltage test",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "0bffca91-4b8f-4a4d-b714-fec1cd26be42": {
        "name": "Explosion suppression system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "e44236e7-c210-46b8-b32c-c8507e0c814b": {
        "name": "2-hand switches",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "e3f0620c-d26d-48fb-a74a-e5e7118da855": {
        "name": "Electrical hazard and/or dielectric footwear",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "39005682-22f1-4888-a64b-71f70c0de936": {
        "name": "Assistance from additional worker",
        "for_tasks": True,
        "for_site_conditions": False,
    },
    "c6ea2eb6-1127-49d5-93ed-45aaf2abd78b": {
        "name": "Crawl speed on hoist",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "209177a4-7639-4f6b-9cc2-60393301bdb0": {
        "name": "Spill kits",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "0e2ccce5-9fd9-441c-9bff-80a9e2966b42": {
        "name": "Fire protection system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "157f439d-8fcb-4182-b172-eaacee5f9ff0": {
        "name": "Groung Device Identification Ticket (GDIT)",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "42382149-d040-448b-98fd-740737702b09": {
        "name": "Remote racking devices",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "80364238-c3fb-49d3-a4f3-29e7372b9acf": {
        "name": "Evacuation zones",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "a96e2cca-97dd-46d3-a6d2-8aa9b02f8342": {
        "name": "Chemical suit and gloves",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "f8905cd2-75b4-4386-890d-624de84cce29": {
        "name": "Eye wash stations",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "bb525844-3ff4-4c98-8a15-894cfc324715": {
        "name": "First aid kit",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "1989b8fd-6dd1-426d-b8a1-f8cce760dfd5": {
        "name": "Pressure indicators",
        "for_tasks": False,
        "for_site_conditions": False,
    },
    "0859196b-172b-453f-802a-b94699db4710": {
        "name": "Excavation support system",
        "for_tasks": False,
        "for_site_conditions": False,
    },
}


def upgrade():
    connection = op.get_bind()
    db_controls = {
        str(i.id): i
        for i in connection.execute(text("SELECT * FROM library_controls")).fetchall()
    }
    duplicated_ids = {}

    for control_id, control in EXPECTED_CONTROLS.items():
        db_control = db_controls.pop(control_id, None)
        if not db_control:
            connection.execute(
                text(
                    "INSERT INTO library_controls (id, name, for_tasks, for_site_conditions) VALUES (:id, :name, :for_tasks, :for_site_conditions)"
                ),
                {
                    "id": control_id,
                    "name": control["name"],
                    "for_tasks": control["for_tasks"],
                    "for_site_conditions": control["for_site_conditions"],
                },
            )
        else:
            to_update = {
                key: control[key]
                for key in ("name", "for_tasks", "for_site_conditions")
                if getattr(db_control, key) != control[key]
            }
            if to_update:
                update_columns = ", ".join(f"{i} = :{i}" for i in to_update.keys())
                connection.execute(
                    text(
                        f"UPDATE library_controls SET {update_columns} WHERE id = '{control_id}'"
                    ),
                    to_update,
                )

        # Delete duplicates
        merge = control.get("merge")
        if merge:
            for merge_id in merge.keys():
                db_merge = db_controls.pop(merge_id, None)
                if db_merge:
                    duplicated_ids[merge_id] = control_id
                    for table_name in ("site_condition_controls", "task_controls"):
                        connection.execute(
                            text(
                                f"UPDATE {table_name} SET library_control_id = '{control_id}' WHERE library_control_id = '{merge_id}'"
                            )
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
                        f"SELECT {column_name}, library_hazard_id, library_control_id FROM {table_name} WHERE library_control_id IN ('{to_ids_str}')"
                    )
                )
            }

            for record in connection.execute(
                text(
                    f"SELECT {column_name}, library_hazard_id, library_control_id FROM {table_name} WHERE library_control_id IN ('{duplicated_ids_str}')"
                )
            ):
                column_id = str(getattr(record, column_name))
                library_hazard_id = str(record.library_hazard_id)
                library_control_id = str(record.library_control_id)
                new_library_control_id = duplicated_ids[library_control_id]
                filter_query = f"{column_name} = '{column_id}' AND library_hazard_id = '{library_hazard_id}' AND library_control_id = '{library_control_id}'"
                record_key = (column_id, library_hazard_id, new_library_control_id)
                if record_key in existing_ids:
                    connection.execute(
                        text(f"DELETE FROM {table_name} WHERE {filter_query}")
                    )
                else:
                    existing_ids.add(record_key)
                    connection.execute(
                        text(
                            f"UPDATE {table_name} SET library_control_id = '{new_library_control_id}' WHERE {filter_query}"
                        )
                    )

    # Fix audit
    for record in connection.execute(
        text(
            "SELECT id, old_values, new_values FROM public.audit_event_diffs WHERE object_type IN ('site_condition_control', 'task_control')"
        )
    ):
        to_update = {}
        for attribute in ("old_values", "new_values"):
            values = getattr(record, attribute)
            if values:
                library_control_id = values.get("library_control_id")
                if library_control_id:
                    to_library_control_id = duplicated_ids.get(library_control_id)
                    if to_library_control_id:
                        values["library_control_id"] = to_library_control_id
                        to_update[attribute] = json.dumps(values)
        if to_update:
            update_columns = ", ".join(f"{i} = :{i}" for i in to_update.keys())
            query = f"UPDATE public.audit_event_diffs SET {update_columns} WHERE id = '{record.id}'"
            connection.execute(text(query), to_update)

    # Disable other controls
    # We don't delete it because we don't know for what it should be migrated
    if db_controls:
        library_control_ids_str = "', '".join(db_controls.keys())
        connection.execute(
            text(
                f"UPDATE library_controls SET for_tasks = false, for_site_conditions = false WHERE id IN ('{library_control_ids_str}')"
            )
        )

    # Now let's delete the library control entry
    if duplicated_ids:
        duplicated_ids_str = "', '".join(duplicated_ids.keys())
        connection.execute(
            text(f"DELETE FROM library_controls WHERE id IN ('{duplicated_ids_str}')")
        )


def downgrade():
    pass
