from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class NatgridObservationMapper(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    observation_id: str = Field(..., alias="ActID2")
    observation_type: str = Field(..., alias="AssessmentFormType2")
    observation_datetime: str = Field(..., alias="ActCompleteDt2")
    person_type_reporting: Optional[str] = Field(None, alias="ActEmpType2")
    supervisor_id: Optional[str] = Field(None, alias="TMDeptIDCurrent2")
    project_id: Optional[str] = Field(None, alias="ProjectNo2")
    contractor_involved: Optional[str] = Field(None, alias="ContractCompName2")
    location_name: Optional[str] = Field(None, alias="ActLocationName2")
    street: Optional[str] = Field(None, alias="ActLocationAddress2")
    city: Optional[str] = Field(None, alias="ActLocationCity2")
    state: Optional[str] = Field(None, alias="ActLocationState2")
    job_type_1: Optional[str] = Field(None, alias="OrgDescription3")
    job_type_2: Optional[str] = Field(None, alias="OrgDescription4")
    job_type_3: Optional[str] = Field(None, alias="OrgDescription5")
    task_type: Optional[str] = Field(None, alias="TaskTxt2")
    task_detail: Optional[str] = Field(None, alias="ActTaskDetail2")
    observation_comments: Optional[str] = Field(None, alias="ActComments2")
    action_id: Optional[str] = Field(None, alias="AIID3")
    action_type: Optional[str] = Field(None, alias="AIText3")
    action_datetime: Optional[str] = Field(None, alias="AICompletedt3")
    action_category: Optional[str] = Field(None, alias="QCatTxt")
    action_topic: Optional[str] = Field(None, alias="QText")
    response: Optional[str] = Field(None, alias="QChoiceText")
    response_specific_id: Optional[str] = Field(None, alias="AIID2")
    response_specific_action_comments: Optional[str] = Field(None, alias="AIText2")
    response_specific_action_datetime: Optional[str] = Field(
        None, alias="AICompletedt2"
    )

    @validator(
        "observation_datetime",
        "action_datetime",
        "response_specific_action_datetime",
        pre=True,
    )
    def cast_to_valid_iso8601_timestamp(cls, v: str) -> str:
        if v:
            return datetime.strptime(v, "%m/%d/%Y").isoformat()
        return v

    @validator("*")
    def cast_na_to_none(cls, v: str) -> Optional[Any]:
        if v == "NA" or v == "":
            return None
        return v
