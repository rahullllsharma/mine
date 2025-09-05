"""Update Control Library

Revision ID: c399168483bf
Revises: 1648b9794234
Create Date: 2022-02-18 15:13:42.185855

"""
from typing import Any, Callable
from uuid import UUID

from alembic import op
from sqlmodel import Session, select

from worker_safety_service.models import (
    LibraryControl,
    LibrarySiteConditionRecommendations,
    LibraryTaskRecommendations,
    SiteConditionControl,
    TaskControl,
)

# revision identifiers, used by Alembic.
revision = "c399168483bf"
down_revision = "1648b9794234"
branch_labels = None
depends_on = None


def upgrade() -> None:
    def get_by_id(session: Session, ClassName: Callable, id: UUID) -> Any:
        statement = select(ClassName).where(ClassName.id == id)  # type: ignore
        results = session.exec(statement)
        model = results.first()
        return model

    def delete(session: Session, ClassName: Callable, id: UUID) -> None:
        model = get_by_id(session, ClassName, id)
        if model is None:
            return

        session.delete(model)
        session.commit()

    def link_task_models(
        session: Session, task_id: UUID, hazard_id: UUID, control_id: UUID
    ) -> None:
        LTR = LibraryTaskRecommendations  # abbreviation hack
        statement = (
            select(LTR)
            .where(LTR.library_task_id == task_id)
            .where(LTR.library_hazard_id == hazard_id)
            .where(LTR.library_control_id == control_id)
        )
        recommendation = session.exec(statement).first()
        if recommendation:
            return  # Recommendation already registered
        recommendation = LibraryTaskRecommendations(
            library_task_id=task_id,
            library_hazard_id=hazard_id,
            library_control_id=control_id,
        )
        session.add(recommendation)
        session.commit()

    def link_site_condition_models(
        session: Session, site_condition_id: UUID, hazard_id: UUID, control_id: UUID
    ) -> None:
        LSCR = LibrarySiteConditionRecommendations  # abbreviation hack
        statement = (
            select(LSCR)
            .where(LSCR.library_site_condition_id == site_condition_id)
            .where(LSCR.library_hazard_id == hazard_id)
            .where(LSCR.library_control_id == control_id)
        )
        recommendation = session.exec(statement).first()
        if recommendation:
            return  # Recommendation already registered
        recommendation = LibrarySiteConditionRecommendations(
            library_site_condition_id=site_condition_id,
            library_hazard_id=hazard_id,
            library_control_id=control_id,
        )
        session.add(recommendation)
        session.commit()

    with Session(bind=op.get_bind()) as session:
        # Renames
        renames = {
            "712c64dd-9f74-4a8a-9dcd-3b55bfe5bb0c": "Inspect ladders and scaffold",
            "e767c285-3f2d-4b59-a7fa-881921ba5317": "Placement of sandbags or timber skids",
            "cfd7b6a5-45f2-42d2-83ce-f6426667095b": "Continuous atmospheric monitoring",
            "da3696b1-530b-4fc0-a624-9fbc77c26b00": "Competent person inspect excavation before each shift",
            "5ad9c296-febb-41b1-bd83-c21910101a10": "Inspect rigging",
            "cf25cc91-be50-4117-aced-c8a8f83db846": "Proper body and tool position",
            "8241c09d-c55b-4953-984e-ca6ca8154098": "Wind direction",
            "ef04b4a5-9196-4122-b6f4-0b787190dff0": "360 walk around",
            "b9be969d-9811-4546-8494-13f95f63fa0e": "Walk down of isolation points",
            "9445a787-c4cb-4fb2-8a49-1b9947f55876": "Machine guarding",
            "6abcda1e-947c-4f1e-b913-18bc96c23334": "Double eye protection",
            "c2efdade-aac5-40c6-aa29-34687d2114f3": "Hard hat",
            "f42676bc-01c7-4f57-a55b-8c07b5904c56": "Eye protection",
            "d8251088-33df-44b9-8286-3e11d80645d1": "Hearing protection",
            "d1a3a929-254a-4dbe-82b4-2c9272a8481a": "Inspect all electrical cords and ensure proper grounding",
            "0899d101-6a06-41f4-910e-1fbba2de1458": "Handle",
            "5ddd6a21-1f39-45fc-af9d-1dc783eba9a5": "Respirator",
            "8b1698a3-a055-499c-95e5-56059e3cdd89": "Fill in gaps and holes in mats",
            "610c3314-762f-4985-9701-6cfe44059cd8": "Pressure relief valves",
            "8b781386-e309-44d5-9b8d-35230f80119a": "Proper PPE as outlined by Safety Data Sheet",
            "496344fb-1c4d-4b89-bc32-9ba7b50f619e": "Ramps placed no more than 25’ laterally from one another, Inspect daily by competent person",
            "42c7d15f-00c4-49cc-bcce-7e58927d09b6": "Deadman switch (emergency shut-down)",
            "6f005259-0fc3-4fd2-bcf7-b2bf67d44766": "Long pants and sleeves",
            "8d9dc6bf-cb00-4d8d-bcfe-9aa498fc2de3": "Install trench boxes",
            "7bd1b8f8-020a-46bd-bff0-d4fba5910cac": "Impact rated gloves",
            "bc886bd6-602f-49d5-8508-01b987fe7ed7": "Lift director communicates with operator",
            "5224cf50-d219-4f8b-a5e3-7e652b6e648f": "Safe limits of approach",
            "59052adf-ceb6-48af-9884-751a9cc07903": "Inspect hoses and fittings",
            "5ebf83da-3097-4739-8f5c-28fb21a4e124": "Inspect all equipment and ensure proper guarding",
            "c8202f22-79a8-4037-b566-5c7ea9dfe935": "Traffic control devices ( eg. barricades, delineators, signs)",
            "00cf6e41-877a-480a-974a-7eea86e66486": "Inspected and erected by trained and competent person/s",
            "845518bd-2a56-47c7-92d7-220087939243": "Exclusion zone",
            "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e": "Cutting goggles",
            "1b79d139-38b2-44f7-aefc-e2871e2d46d9": "Combustible gas indicators",
            "ddb617a0-9e06-4599-9b99-3e36e7b5ee28": "Controlled access zone",
            "ea323b12-7f98-4064-873c-92886cef07ec": "Welding hood",
            "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": "Situational jobsite awareness",
            "dc925cd9-a7bd-4a68-b61b-389fe09289d9": "Back in parking",
            "f5fb0d9d-1e01-42b7-835e-7c5e46482119": "Erection of proper barricades and warning signs",
            "8358a4b3-7972-441d-918f-dbdb6b8a836f": "Gas detectors",
            "09cf14aa-3069-469a-ae4a-d2bb7e50d767": "Welding gloves",
            "62ca2539-c0c4-4920-aca8-60e8536e725d": "Spotters",
            "5d06c932-2434-4990-8609-45afc42f9864": "Pipe holders",
            "98d73996-ac36-4dbd-8b6c-fa2682c421d4": "Ensure proper benching/shoring",
            "23d96813-1901-4a25-b6d7-5579a2799a10": "Asbestos abatement",
            "4df673d5-943d-481f-83e7-cf0f0e6f7b47": "Lift plan",
            "08bbff19-ce5b-47c1-a680-4cd5d6d8866f": "Use proper lifting technique, Use team lift or equipment if necessary",
            "1f9a5ff0-3394-4895-b45c-089ac6643003": "Keep body parts away from end of hose",
            "4092d3b1-67d7-495b-84b4-de224a1b9894": "Training and qualification",
            "eb982aae-a4a6-4f8b-b5b9-418f9df86b22": "Pre-shift inspection",
            "730d586c-f9fc-48c2-bab9-018e5474b81c": "Cut resistant gloves",
            "8aac579e-b59c-4252-8939-c799b7f9166d": "Fire extinguisher",
            "33e934a7-c837-4a28-b896-9e4612a6c810": "Full sleeve natural fibers (100% cotton) or FR garment",
            "f52b676d-516e-4068-8878-050dfb32313f": "Police detail",
            "a1944ad5-2895-436f-afa9-9a752dd81ecc": "Isotopes stored and handled properly",
            "8897d760-3e77-499b-a3b8-ef060ac5fbd9": "Safety toe boots",
            "14652da3-051a-4ff9-b7d1-34ea9ed4be81": "Goal post",
            "b4380ba8-f086-4c83-b3f6-876d94d00239": "Radiation monitoring device",
            "d9b46efa-f00e-4ac9-b550-0541dda61246": "Supplied fresh air and/or air movers",
            "253829fa-56ea-40a7-a938-cceee82cd7d6": "Rebar caps",
            "359a02e2-7330-4175-a5b6-ef918e7d4158": "Bonding of material and equipment",
            "52182601-b5ef-4526-ad02-5d63f5b75e84": "Repellant",
            "6c9d1d49-53f1-4baf-a382-abcb11d9f40d": "Hydro-vac",
            "2cef1dab-d0bd-4c3c-a0b8-79ff3e67b6d1": "Proper ladder usage",
            "c8bdcb66-e7e4-440b-aea9-6cb4fd97cd38": 'Use a spotter to maintain at least 12" clearance from utilities',
            "7d39bcf4-6f3d-4daa-914d-6335018fbcf8": "Stretch and flex",
            "b4affcfd-2c5a-471e-bf27-61d20dac834b": "Bend over nails",
            "9ad431e2-a945-4e5a-8108-64a734717dfa": "Maintain an exclusion zone around excavator and loading trucks",
            "fdfdc2f6-af19-413b-aacc-e0819cae5f5d": "Redundant tag lines",
            "48319073-8386-49c9-9bab-735def7b1872": "Do not wear loose fitting clothes",
            "0f2534da-adad-4dab-a700-8d1493f5ba82": "Fall protection / Arrest",
            "1f482f5a-820b-4710-8ecf-d6a816d6e96b": "3 points of contact",
            "53a4afff-cfd5-4b30-89af-3d875f62722a": "Whip checks",
            "f03198ec-d56a-434b-aa72-f21a7e80eed2": "Mechanical steak driver",
            "097a4aec-a6b7-4e3c-8862-b927ab19a93f": "Ladders",
            "9e21d7c7-3276-406e-951e-a710c5c3f35a": "Housekeeping",
            "4ad1bc4a-ec30-4246-8796-23315c9d9f88": "keep hands away from bender head",
            "873def37-dd23-4abe-acdb-81eab0602c08": "Work rest cycle",
            "8035cbfb-4b42-4c1f-9ae3-b8f57983660b": "Inspect equipment",
            "b4b3b004-49a6-4471-84d6-7b6d0a4a7004": "Wall for public safety",
            "b22839ca-d7a1-4308-88ab-11d617bcdbff": "Adhere to traffic control plan",
            "a033267d-7322-42c8-b011-4015d68b2bc2": "Insulating gloves",
            "0707486a-fd22-4959-887c-a0cd930ec087": "Chaps",
            "e92f3626-be91-47da-b197-77e6154f5a15": "Inspect entrances for signs of animal habitation prior to entry",
            "ff161bca-e057-4045-a3fe-708b6569ab8a": "LOTO procedures",
            "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a": "811 locate tickets in place and utilities clearly marked",
            "25ae5c04-3dab-4c7d-bf0d-2317fd997619": "Face shield",
        }
        for c in renames.keys():
            control = get_by_id(session, LibraryControl, c)
            if control:
                control.name = renames[c]
                session.commit()
                session.refresh(control)

        # Multi
        multi = {
            "c60c5f88-26f0-4387-a8c8-7d238a10662b": [
                "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
                "5ad9c296-febb-41b1-bd83-c21910101a10",
            ],
            "2ed7717c-9f7e-465b-9b65-2800a4d0b543": [
                "5ad9c296-febb-41b1-bd83-c21910101a10",
                "845518bd-2a56-47c7-92d7-220087939243",
            ],
            "f71044a0-9c6d-4bf2-a285-0b5701f0ee56": [
                "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
                "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            ],
            "66315d84-418f-4144-be7d-b33d727f65db": [
                "33e934a7-c837-4a28-b896-9e4612a6c810",
                "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            ],
            "f5eaab07-de2f-4252-ac4e-5013cd4301fa": [
                "62ca2539-c0c4-4920-aca8-60e8536e725d",
                "845518bd-2a56-47c7-92d7-220087939243",
                "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            ],
        }
        LTR = LibraryTaskRecommendations  # abbreviation hack
        LSCR = LibrarySiteConditionRecommendations  # abbreviation hack
        PLSCHC = SiteConditionControl
        PLTHC = TaskControl
        for c in multi.keys():
            statement = select(LTR).where(LTR.library_control_id == c)
            recommendations = session.exec(statement)
            for r in recommendations:
                for new in multi[c]:
                    link_task_models(
                        session, r.library_task_id, r.library_hazard_id, new
                    )
                session.delete(r)
                session.commit()

            statement = select(LSCR).where(LSCR.library_control_id == c)
            recommendations = session.exec(statement)
            for r in recommendations:
                for new in multi[c]:
                    link_site_condition_models(
                        session, r.library_site_condition_id, r.library_hazard_id, new
                    )
                session.delete(r)
                session.commit()

            statement = select(PLSCHC).where(PLSCHC.library_control_id == c)
            pjst = session.exec(statement)
            for p in pjst:
                for new in multi[c]:
                    n = PLSCHC(
                        project_location_site_condition_hazard_id=p.project_location_site_condition_hazard_id,
                        library_control_id=new,
                        archived_at=p.archived_at,
                        user_id=p.user_id,
                        is_applicable=p.is_applicable,
                        position=p.position,
                    )
                    session.add(n)
                session.delete(p)
                session.commit()

            statement = select(PLTHC).where(PLTHC.library_control_id == c)
            pjh = session.exec(statement)
            for p in pjh:
                for new in multi[c]:
                    n = PLTHC(
                        project_location_task_hazard_id=p.project_location_task_hazard_id,
                        library_control_id=new,
                        archived_at=p.archived_at,
                        user_id=p.user_id,
                        is_applicable=p.is_applicable,
                        position=p.position,
                    )
                    session.add(n)
                session.delete(p)
                session.commit()

            delete(session, LibraryControl, c)

        # Replace to-be-discontinued with specificied controls
        replacement = {
            # to_be_discontinued : replacement
            "a70e6291-b970-412d-ae2c-377bbd8ed509": "5ad9c296-febb-41b1-bd83-c21910101a10",
            "e747d786-6a08-424d-87cc-2f902434b567": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "2faf19ad-168b-421b-b80b-6780ac9ad5c6": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "73ff403d-b017-4e08-9e98-363eb14a2b85": "5ad9c296-febb-41b1-bd83-c21910101a10",
            "c0c5d686-b373-48f8-9275-299b4c88b17c": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "b4f4cd80-fd4e-4b61-be7b-1e13990c4e3f": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "bedf3b52-a5ae-4463-b0bb-612f62aaaa2d": "845518bd-2a56-47c7-92d7-220087939243",
            "59fb94f1-e582-43c8-b210-f461303d49a1": "9445a787-c4cb-4fb2-8a49-1b9947f55876",
            "6f861d56-fe24-413d-89d1-3a3eed715e6c": "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            "a787c2f6-9a87-4b3f-b4dd-c07473ca8bd9": "5ad9c296-febb-41b1-bd83-c21910101a10",
            "fc57a419-2cf2-43f6-b900-f91d72f2990e": "33e934a7-c837-4a28-b896-9e4612a6c810",
            "85a126d4-e9a4-4a59-a2c2-cd63e0c623e8": "cf25cc91-be50-4117-aced-c8a8f83db846",
            "30743dcd-1239-4a86-b944-22bc299a581b": "cf25cc91-be50-4117-aced-c8a8f83db846",
            "b9a8f9c8-7812-436b-9092-78e276684502": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "88bb926b-a96a-4e6b-8a6e-87086473079a": "496344fb-1c4d-4b89-bc32-9ba7b50f619e",
            "df8f4f56-490c-4c38-930f-04eba30d9d55": "cf25cc91-be50-4117-aced-c8a8f83db846",
            "c348abad-147c-4db5-ab5e-a54510e4539e": "08bbff19-ce5b-47c1-a680-4cd5d6d8866f",
            "486f23c1-0312-402a-847f-1c476a1fee64": "9445a787-c4cb-4fb2-8a49-1b9947f55876",
            "b2b5efdb-fc6f-491f-a490-1995c0b35c97": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "7d1fccd0-5229-419b-b803-d32f721049c9": "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e",
            "8d165049-7ce1-42c4-adc1-1086a343f207": "8035cbfb-4b42-4c1f-9ae3-b8f57983660b",
            "78332276-730a-4bc6-93c8-b7b0281a8057": "8b781386-e309-44d5-9b8d-35230f80119a",
            "2e56dfb6-917f-49e4-b0b9-352e757e4835": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "81d00a35-6ea2-48de-8ab0-cecfdcc752ee": "cfd7b6a5-45f2-42d2-83ce-f6426667095b",
            "87aa7ed0-0c33-46c6-93e4-eb99566e1c49": "9445a787-c4cb-4fb2-8a49-1b9947f55876",
            "a1189cef-8b87-4fac-b8d0-7fd6a1951ccc": "ea323b12-7f98-4064-873c-92886cef07ec",
            "1e5c31d1-30b6-45de-bfd6-1bf9b4e4b8d8": "b9be969d-9811-4546-8494-13f95f63fa0e",
            "cf405f9f-0a0f-44aa-9fa0-c57a7a39fc1a": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "9c95fe6e-4a53-4c31-9329-d54ba58e1acc": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "42363b92-8d59-47d9-b4a5-9ee089453dd9": "1b79d139-38b2-44f7-aefc-e2871e2d46d9",
            "77b51992-e01f-435a-b1df-bcd65452d493": "5ddd6a21-1f39-45fc-af9d-1dc783eba9a5",
            "ad7f1739-3788-43f2-bb07-29909e451b5e": "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e",
            "6a63f574-e5a5-490a-974c-1f645b97254b": "d1a3a929-254a-4dbe-82b4-2c9272a8481a",
            "08f6f584-7350-469d-a684-d11eea6a7654": "62ca2539-c0c4-4920-aca8-60e8536e725d",
            "44ade03f-ae30-403d-8778-b269b096695f": "6abcda1e-947c-4f1e-b913-18bc96c23334",
            "2cd5dd4a-c4e6-4746-a2e8-a8a524ad58b9": "cfd7b6a5-45f2-42d2-83ce-f6426667095b",
            "4a20b41b-8d93-4ce9-b82c-aeefaa5682a6": "f5fb0d9d-1e01-42b7-835e-7c5e46482119",
            "a79a8839-24be-4897-a125-c6923b252c50": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "b0ec7069-b7ed-4d62-ae12-25bfd471949e": "09cf14aa-3069-469a-ae4a-d2bb7e50d767",
            "bc5b3ea5-3880-4d61-bb98-d4c8edc1065c": "5d06c932-2434-4990-8609-45afc42f9864",
            "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9": "25ae5c04-3dab-4c7d-bf0d-2317fd997619",
            "15d9206b-2e93-4711-bf0b-b737c1ee75f1": "09cf14aa-3069-469a-ae4a-d2bb7e50d767",
            "c614eddc-4066-4771-b176-e69c67c6d4ac": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "0eac0c4b-d924-4d76-b6f2-3e377e2a40f0": "da3696b1-530b-4fc0-a624-9fbc77c26b00",
            "775863d4-e06d-427c-8017-0cd33b8798d5": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "dfcdd14a-842f-498b-a5e9-3f7256848a1d": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "cf7dd162-f754-410e-ab3a-f94d40c567e8": "9445a787-c4cb-4fb2-8a49-1b9947f55876",
            "ce618f10-a03e-4d7b-a85c-8ddfe29e09d7": "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            "dc5a7ab2-1ab7-482a-9abb-f4b56b60d9df": "730d586c-f9fc-48c2-bab9-018e5474b81c",
            "f3bba684-228b-4184-aa75-d1f7d9fe85f5": "33e934a7-c837-4a28-b896-9e4612a6c810",
            "3187aea7-6dfe-4a27-a8bd-75eb3d64cb29": "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            "73c6e1dc-d439-4bdc-85a1-b2ba107ce449": "9445a787-c4cb-4fb2-8a49-1b9947f55876",
            "1d0797ca-4a43-4b79-aea2-375b624ee691": "98d73996-ac36-4dbd-8b6c-fa2682c421d4",
            "c4db73b3-3426-448b-9491-17da56c65430": "33e934a7-c837-4a28-b896-9e4612a6c810",
            "27d43f9a-3c96-4e17-b371-bc3d1dc734ac": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "4f6f6d2f-485c-41a9-92f5-ef002c2f4aca": "8897d760-3e77-499b-a3b8-ef060ac5fbd9",
            "d1dc631e-cc9a-45fb-b4cb-b4d1a5645ba2": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "dd827587-1ce5-4f5d-94e9-1dd15276e902": "f42676bc-01c7-4f57-a55b-8c07b5904c56",
            "5260c1fe-12c3-4296-b29e-bcf88acc219c": "8aac579e-b59c-4252-8939-c799b7f9166d",
            "032aa7ca-251f-40e7-9163-f6f124793703": "62ca2539-c0c4-4920-aca8-60e8536e725d",
            "6d786aab-bf9b-4aff-b796-9de143702d5b": "14652da3-051a-4ff9-b7d1-34ea9ed4be81",
            "a91ac8de-0735-4b4d-b983-7389af8336c1": "7bd1b8f8-020a-46bd-bff0-d4fba5910cac",
            "bc1dcee0-2d8f-4417-9a5c-cff503dd6c24": "5ad9c296-febb-41b1-bd83-c21910101a10",
            "e7e0b603-197e-455e-bc16-7fc287e0e3d1": "f5fb0d9d-1e01-42b7-835e-7c5e46482119",
            "877c18f0-c1a7-4b9c-a0ff-70614bfa4d30": "b9434a7d-62cc-4dc7-9e8e-02d418af7f7a",
            "22576867-9d2c-4ddb-a0a0-21871509f3e9": "ea323b12-7f98-4064-873c-92886cef07ec",
            "e391f3c9-367b-4de8-9a9e-e5e01822f6f1": "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            "4901113b-6b90-494f-95fa-e350fe2fe766": "98d73996-ac36-4dbd-8b6c-fa2682c421d4",
            "00cbc4f6-a2d5-420a-92e0-7d1951c88513": "0f2534da-adad-4dab-a700-8d1493f5ba82",
            "88c78e16-2d02-4638-b784-e66a98e4ba2c": "33e934a7-c837-4a28-b896-9e4612a6c810",
            "3b8db435-dec2-44b0-877f-35956b87e033": "f5fb0d9d-1e01-42b7-835e-7c5e46482119",
            "848f3d9e-76e9-43b2-80da-83dd8e05e3c5": "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
            "fb6721c8-c93c-426d-b860-ef82a328609a": "14652da3-051a-4ff9-b7d1-34ea9ed4be81",
            "2acd4471-54d8-4fb1-86b3-b9209fca34a8": "0f2534da-adad-4dab-a700-8d1493f5ba82",
            "fb7730a4-2d51-49ab-9d3d-9530c25d6d77": "9e21d7c7-3276-406e-951e-a710c5c3f35a",
            "3fbbacf5-e5e4-4dcc-b17c-485cc22eefd3": "53a4afff-cfd5-4b30-89af-3d875f62722a",
            "17090705-e8d4-48a3-bf95-a787f18e9b73": "cfd7b6a5-45f2-42d2-83ce-f6426667095b",
            "b4e12e36-9def-4c51-9d9b-2a7f3f04263b": "25ae5c04-3dab-4c7d-bf0d-2317fd997619",
            "0e2b63e7-a997-4f9d-8fb2-839b572a1ec6": "ff161bca-e057-4045-a3fe-708b6569ab8a",
            "d0cbe3ec-bc57-4e48-9e14-7cfe195e1131": "08bbff19-ce5b-47c1-a680-4cd5d6d8866f",
        }

        LTR = LibraryTaskRecommendations  # abbreviation hack
        LSCR = LibrarySiteConditionRecommendations  # abbreviation hack
        PLSCHC = SiteConditionControl
        PLTHC = TaskControl
        for c in replacement.keys():
            # LibraryTaskRecommendations
            statement = select(LTR).where(LTR.library_control_id == c)
            recommendations = session.exec(statement)
            for r in recommendations:
                link_task_models(
                    session, r.library_task_id, r.library_hazard_id, replacement[c]
                )  # won't do anything if Recommendation already exists
                session.delete(r)
                session.commit()

            # LibrarySiteConditionRecommendations
            statement = select(LSCR).where(LSCR.library_control_id == c)
            recommendations = session.exec(statement)
            for r in recommendations:
                link_site_condition_models(
                    session,
                    r.library_site_condition_id,
                    r.library_hazard_id,
                    replacement[c],
                )  # won't do anything if Recommendation already exists
                session.delete(r)
                session.commit()

            # ProjectLocationSiteConditionHazardControl
            statement = select(PLSCHC).where(PLSCHC.library_control_id == c)
            pjst = session.exec(statement)
            for p in pjst:
                # doesn't check for existance, but the table is empty anyways
                n = PLSCHC(
                    project_location_site_condition_hazard_id=p.project_location_site_condition_hazard_id,
                    library_control_id=replacement[c],
                    archived_at=p.archived_at,
                    user_id=p.user_id,
                    is_applicable=p.is_applicable,
                    position=p.position,
                )
                session.add(n)
                session.delete(p)
                session.commit()

            # ProjectLocationTaskHazardControl
            statement = select(PLTHC).where(PLTHC.library_control_id == c)
            pjh = session.exec(statement)
            for p in pjh:
                # doesn't check for existance, but the table is empty anyways
                n = PLTHC(
                    project_location_task_hazard_id=p.project_location_task_hazard_id,
                    library_control_id=replacement[c],
                    archived_at=p.archived_at,
                    user_id=p.user_id,
                    is_applicable=p.is_applicable,
                    position=p.position,
                )
                session.add(n)
                session.delete(p)
                session.commit()

            # All references were substituted, Control can be deleted
            delete(session, LibraryControl, c)

        # This control is an empty string and must be removed
        c = "b1b04397-8654-465f-ba91-25ca387e5f4c"

        # Remove entries where a user added the empty string as a control
        statement = select(PLTHC).where(PLTHC.library_control_id == c)
        bad_associations = session.exec(statement)
        for b in bad_associations:
            session.delete(b)

        statement = select(LTR).where(LTR.library_control_id == c)
        recommendations = session.exec(statement)
        for r in recommendations:
            session.delete(r)

        statement = select(LSCR).where(LSCR.library_control_id == c)
        recommendations = session.exec(statement)
        for r in recommendations:
            session.delete(r)

        delete(session, LibraryControl, c)

        session.commit()


def downgrade():
    pass
