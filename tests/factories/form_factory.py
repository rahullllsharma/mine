from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.form_models import (
    ComponentData,
    Form,
    FormCopyRebriefSettings,
    FormProperties,
    FormsMetadata,
    FormStatus,
    FormUpdateRequest,
    LocationDetails,
    SupervisorDetails,
    WorkPackageDetails,
)
from ws_customizable_workflow.models.shared_models import WorkTypeBase


class FormFactory(ModelFactory):
    __model__ = Form
    type: ElementType = ElementType.FORM
    is_archived: bool = False


class WorkPackageDetailsFactory(ModelFactory):
    __model__ = WorkPackageDetails
    name = "Test Work Package"
    id = "c5c70348-c39d-4e4c-9c03-753f0c4b425f"


class LocationDetailsFactory(ModelFactory):
    __model__ = LocationDetails
    name = "Test Location"
    id = "c7b9dfab-6037-47c4-a8bf-a7612caa1e66"


class WorkTypeBaseFactory(ModelFactory):
    __model__ = WorkTypeBase
    name: str = Faker().random_element(
        elements=[
            "Gas Transmission Construction",
            "Electric Distribution",
            "Gas Distribution",
            "Electric Transmission Construction",
        ]
    )


class SupervisorFactory(ModelFactory):
    __model__ = SupervisorDetails
    id = "65ae4024-c328-47df-875f-c6626fa56f0f"
    name = "Test Supervisor"
    email = "test.supervisor@details.com"


class FormCopyRebriefSettingsFactory(ModelFactory):
    __model__ = FormCopyRebriefSettings

    copy_linked_form_id = "65ae4024-c328-47df-875f-c6626fa56f0f"
    rebrief_linked_form_id = "65ae4024-c328-47df-875f-c6626fa56f0f"
    linked_form_id = "65ae4024-c328-47df-875f-c6626fa56f0f"


class FormsMetadataFactory(ModelFactory):
    __model__ = FormsMetadata

    work_package = WorkPackageDetailsFactory.build()
    location = LocationDetailsFactory.build()
    work_types = [WorkTypeBaseFactory.build()]
    supervisor = [SupervisorFactory.build()]
    copy_and_rebrief = FormCopyRebriefSettingsFactory.build()


# class FormsComponentDataFactory(ModelFactory):
#     __model__ = ComponentData
#     activities_tasks = [
#         {
#             "id": "33026100-6040-4898-b884-f59da211d2ce",
#             "isCritical": False,
#             "criticalDescription": None,
#             "name": "Above-ground Welding + Confined Space Entry",
#             "status": "IN_PROGRESS",
#             "startDate": "2025-02-12",
#             "endDate": "2025-02-12",
#             "taskCount": 3,
#             "tasks": [
#                 {
#                     "id": "9464aee6-1ddb-4e65-94e2-6007fabeea02",
#                     "name": "Above-ground welding - Preheating with blankets",
#                     "fromWorkOrder": True,
#                     "riskLevel": "UNKNOWN",
#                     "recommended": True,
#                     "selected": True,
#                 },
#                 {
#                     "id": "ac1e15a5-7021-48a6-a88d-b9799b6355ea",
#                     "name": "Confined space entry",
#                     "fromWorkOrder": True,
#                     "riskLevel": "UNKNOWN",
#                     "recommended": True,
#                     "selected": True,
#                 },
#                 {
#                     "id": "f859c660-0513-4470-9d86-06c5c9643314",
#                     "name": "Above-ground welding - Pipe face preheating / Post weld heat treatment",
#                     "fromWorkOrder": True,
#                     "riskLevel": "UNKNOWN",
#                     "recommended": True,
#                     "selected": True,
#                 },
#             ],
#         },
#         {
#             "id": "e1585670-3f24-4f1c-9dbe-cb77cc489848",
#             "isCritical": False,
#             "criticalDescription": None,
#             "name": "Confined Space Entry",
#             "status": "NOT_STARTED",
#             "startDate": "2025-02-25",
#             "taskCount": 1,
#             "tasks": {
#                 "id": "1a080b07-eadd-4793-8404-28ce6b1e19f9",
#                 "name": "Confined space entry",
#                 "fromWorkOrder": True,
#                 "riskLevel": "RECALCULATING",
#                 "recommended": True,
#                 "selected": True,
#             },
#         },
#     ]

#     hazards_controls = [
#         {
#             "id": "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880",
#             "energyLevel": "LOW_ENERGY",
#             "energyType": "BIOLOGICAL",
#             "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg",
#             "isApplicable": True,
#             "name": "Insects, animals, or poisonous plants",
#             "archivedAt": None,
#             "controls": [
#                 {
#                     "id": "52182601-b5ef-4526-ad02-5d63f5b75e84",
#                     "name": "Insect repellant",
#                     "ppe": None,
#                 }
#             ],
#         },
#         {
#             "id": "bb5c5324-d3bc-45da-bfff-5ea78aed8dba",
#             "energyLevel": "HIGH_ENERGY",
#             "energyType": "RADIATION",
#             "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/HighDoseOfToxicChemicalOrRadiation.svg",
#             "isApplicable": True,
#             "name": "High dose of toxic chemical or radiation",
#             "archivedAt": None,
#             "controls": [],
#         },
#     ]

#     site_conditions = [
#         {
#             "librarySiteConditionId": "73929607-e45a-4460-a41b-4abc197722a6",
#             "hazards": [
#                 {
#                     "libraryHazardId": "23041379-366e-4ab2-a0db-a18b569bdafb",
#                     "isApplicable": True,
#                     "controls": [
#                         {
#                             "libraryControlId": "1f482f5a-820b-4710-8ecf-d6a816d6e96b",
#                             "isApplicable": True,
#                         }
#                     ],
#                 }
#             ],
#             "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
#         },
#         {
#             "librarySiteConditionId": "b9a1bc0e-0152-41e7-b14e-10172fa09a11",
#             "hazards": [
#                 {
#                     "libraryHazardId": "e1ae99cc-ffd7-46cc-8bdd-2e6bffa37b8a",
#                     "isApplicable": True,
#                     "controls": [
#                         {
#                             "libraryControlId": "873def37-dd23-4abe-acdb-81eab0602c08",
#                             "isApplicable": True,
#                         }
#                     ],
#                 }
#             ],
#             "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
#         },
#     ]


class FormsComponentDataFactory(ModelFactory):
    __model__ = ComponentData

    # Original data sources (as currently defined in your snippet or implied by it)
    # These would be used to build the 'hazards_controls' object below.
    # For clarity, let's assume these are available:
    _source_activities_tasks = [
        {
            "id": "33026100-6040-4898-b884-f59da211d2ce",
            "isCritical": False,
            "criticalDescription": None,
            "name": "Above-ground Welding + Confined Space Entry",
            "status": "IN_PROGRESS",
            "startDate": "2025-02-12",
            "endDate": "2025-02-12",
            "taskCount": 3,
            "tasks": [
                {
                    "id": "9464aee6-1ddb-4e65-94e2-6007fabeea02",
                    "name": "Above-ground welding - Preheating with blankets",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
                {
                    "id": "ac1e15a5-7021-48a6-a88d-b9799b6355ea",
                    "name": "Confined space entry",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
                {
                    "id": "f859c660-0513-4470-9d86-06c5c9643314",
                    "name": "Above-ground welding - Pipe face preheating / Post weld heat treatment",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
            ],
        },
        {
            "id": "e1585670-3f24-4f1c-9dbe-cb77cc489848",
            "isCritical": False,
            "criticalDescription": None,
            "name": "Confined Space Entry",
            "status": "NOT_STARTED",
            "startDate": "2025-02-25",
            "taskCount": 1,
            "tasks": {  # Note: This is an object, treated as a single task list
                "id": "1a080b07-eadd-4793-8404-28ce6b1e19f9",
                "name": "Confined space entry",
                "fromWorkOrder": True,
                "riskLevel": "RECALCULATING",
                "recommended": True,
                "selected": True,
            },
        },
    ]

    _source_hazards_for_manual_addition = [  # This is from your original 'hazards_controls' list
        {
            "id": "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880",
            "energyLevel": "LOW_ENERGY",
            "energyType": "BIOLOGICAL",
            "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg",
            "isApplicable": True,
            "name": "Insects, animals, or poisonous plants",
            "archivedAt": None,
            "controls": [
                {
                    "id": "52182601-b5ef-4526-ad02-5d63f5b75e84",
                    "name": "Insect repellant",
                    "ppe": None,
                }
            ],
        },
        {
            "id": "bb5c5324-d3bc-45da-bfff-5ea78aed8dba",
            "energyLevel": "HIGH_ENERGY",
            "energyType": "RADIATION",
            "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/HighDoseOfToxicChemicalOrRadiation.svg",
            "isApplicable": True,
            "name": "High dose of toxic chemical or radiation",
            "archivedAt": None,
            "controls": [],
        },
    ]

    _source_site_conditions_data = [
        {
            "librarySiteConditionId": "73929607-e45a-4460-a41b-4abc197722a6",
            "hazards": [
                {
                    "libraryHazardId": "23041379-366e-4ab2-a0db-a18b569bdafb",
                    "isApplicable": True,
                    "controls": [
                        {
                            "libraryControlId": "1f482f5a-820b-4710-8ecf-d6a816d6e96b",
                            "isApplicable": True,
                        }
                    ],
                }
            ],
            "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
        },
        {
            "librarySiteConditionId": "b9a1bc0e-0152-41e7-b14e-10172fa09a11",
            "hazards": [
                {
                    "libraryHazardId": "e1ae99cc-ffd7-46cc-8bdd-2e6bffa37b8a",
                    "isApplicable": True,
                    "controls": [
                        {
                            "libraryControlId": "873def37-dd23-4abe-acdb-81eab0602c08",
                            "isApplicable": True,
                        }
                    ],
                }
            ],
            "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
        },
    ]
    activities_tasks = [
        {
            "id": "33026100-6040-4898-b884-f59da211d2ce",
            "isCritical": False,
            "criticalDescription": None,
            "name": "Above-ground Welding + Confined Space Entry",
            "status": "IN_PROGRESS",
            "startDate": "2025-02-12",
            "endDate": "2025-02-12",
            "taskCount": 3,
            "tasks": [
                {
                    "id": "9464aee6-1ddb-4e65-94e2-6007fabeea02",
                    "name": "Above-ground welding - Preheating with blankets",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
                {
                    "id": "ac1e15a5-7021-48a6-a88d-b9799b6355ea",
                    "name": "Confined space entry",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
                {
                    "id": "f859c660-0513-4470-9d86-06c5c9643314",
                    "name": "Above-ground welding - Pipe face preheating / Post weld heat treatment",
                    "fromWorkOrder": True,
                    "riskLevel": "UNKNOWN",
                    "recommended": True,
                    "selected": True,
                },
            ],
        },
        {
            "id": "e1585670-3f24-4f1c-9dbe-cb77cc489848",
            "isCritical": False,
            "criticalDescription": None,
            "name": "Confined Space Entry",
            "status": "NOT_STARTED",
            "startDate": "2025-02-25",
            "taskCount": 1,
            "tasks": {
                "id": "1a080b07-eadd-4793-8404-28ce6b1e19f9",
                "name": "Confined space entry",
                "fromWorkOrder": True,
                "riskLevel": "RECALCULATING",
                "recommended": True,
                "selected": True,
            },
        },
    ]

    # The 'hazards_controls' attribute should be assigned the structured object:
    hazards_controls = {
        "tasks": [
            # Derived from _source_activities_tasks[0].tasks
            {
                "id": "9464aee6-1ddb-4e65-94e2-6007fabeea02",
                "name": "Above-ground welding - Preheating with blankets",
                "isCritical": False,  # From _source_activities_tasks[0].isCritical
                "hazards": [],
                "__typename": "LibraryTask",
            },
            {
                "id": "ac1e15a5-7021-48a6-a88d-b9799b6355ea",
                "name": "Confined space entry",
                "isCritical": False,  # From _source_activities_tasks[0].isCritical
                "hazards": [],
                "__typename": "LibraryTask",
            },
            {
                "id": "f859c660-0513-4470-9d86-06c5c9643314",
                "name": "Above-ground welding - Pipe face preheating / Post weld heat treatment",
                "isCritical": False,  # From _source_activities_tasks[0].isCritical
                "hazards": [],
                "__typename": "LibraryTask",
            },
            # Derived from _source_activities_tasks[1].tasks
            {
                "id": "1a080b07-eadd-4793-8404-28ce6b1e19f9",
                "name": "Confined space entry",
                "isCritical": False,  # From _source_activities_tasks[1].isCritical
                "hazards": [],
                "__typename": "LibraryTask",
            },
        ],
        "manually_added_hazards": [
            # Derived from _source_hazards_for_manual_addition
            {
                "id": "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880",
                "energyLevel": "LOW_ENERGY",
                "energyType": "BIOLOGICAL",
                "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg",
                "isApplicable": True,
                "name": "Insects, animals, or poisonous plants",
                "controls": [
                    {
                        "id": "52182601-b5ef-4526-ad02-5d63f5b75e84",
                        "name": "Insect repellant",
                        "isApplicable": True,
                        "__typename": "LibraryControl",
                    }
                ],
            },
            {
                "id": "bb5c5324-d3bc-45da-bfff-5ea78aed8dba",
                "energyLevel": "HIGH_ENERGY",
                "energyType": "RADIATION",
                "imageUrl": "https://storage.googleapis.com/worker-safety-public-icons/HighDoseOfToxicChemicalOrRadiation.svg",
                "isApplicable": True,
                "name": "High dose of toxic chemical or radiation",
                "controls": [],
            },
        ],
        "site_conditions": _source_site_conditions_data,  # Using the source data directly here
    }

    # If 'activities_tasks' and 'site_conditions' are also direct fields on ComponentData
    # and should be populated from the original lists, they would be defined here as well:
    # activities_tasks = _source_activities_tasks
    # site_conditions = _source_site_conditions_data # (already used above)
    # However, the question specifically asks for 'hazards_controls'.
    site_conditions = [
        {
            "librarySiteConditionId": "73929607-e45a-4460-a41b-4abc197722a6",
            "hazards": [
                {
                    "libraryHazardId": "23041379-366e-4ab2-a0db-a18b569bdafb",
                    "isApplicable": True,
                    "controls": [
                        {
                            "libraryControlId": "1f482f5a-820b-4710-8ecf-d6a816d6e96b",
                            "isApplicable": True,
                        }
                    ],
                }
            ],
            "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
        },
        {
            "librarySiteConditionId": "b9a1bc0e-0152-41e7-b14e-10172fa09a11",
            "hazards": [
                {
                    "libraryHazardId": "e1ae99cc-ffd7-46cc-8bdd-2e6bffa37b8a",
                    "isApplicable": True,
                    "controls": [
                        {
                            "libraryControlId": "873def37-dd23-4abe-acdb-81eab0602c08",
                            "isApplicable": True,
                        }
                    ],
                }
            ],
            "locationId": "9dd1d542-f3c2-459f-b1dc-bbb0447b33b4",
        },
    ]
    location_data = {
        "name": "Test Location",
        "gps_coordinates": {"latitude": 0.0, "longitude": 0.0},
        "description": "Test location description",
        "manual_location": False,
        "other": False,
        "distance": "100m",
    }
    nearest_hospital = {
        "name": "Test Hospital",
        "gps_coordinates": {"latitude": 0.0, "longitude": 0.0},
        "description": "Test hospital description",
        "phone_number": "1234567890",
    }


class FormPropertiesFactory(ModelFactory):
    __model__ = FormProperties
    title = "Test Template Title"
    description = "Default Template Description"
    status = FormStatus.INPROGRESS


class FormUpdateRequestFactory(ModelFactory):
    __model__ = FormUpdateRequest
    contents = ["content1", "content2"]
    properties = FormPropertiesFactory.build()
    metadata = FormsMetadataFactory.build()
    component_data = FormsComponentDataFactory.build()
