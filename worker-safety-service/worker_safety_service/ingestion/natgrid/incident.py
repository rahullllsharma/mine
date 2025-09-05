from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class NatgridIncidentMapper(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    external_key: str = Field(..., alias="IncidentID")
    incident_type: Optional[str] = Field(None, alias="IncidentTypes")
    incident_date: str = Field(..., alias="IncDate")
    person_impacted_type: Optional[str] = Field(None, alias="IncEmpType")
    supervisor_id: Optional[str] = Field(None, alias="IncReportByDeptID")
    contractor: Optional[str] = Field(None, alias="CompanyName")
    location_description: Optional[str] = Field(None, alias="IncLocName")
    street_number: Optional[str] = Field(None, alias="IncLocAddress1")
    street: Optional[str] = Field(None, alias="IncLocAddress2")
    city: Optional[str] = Field(None, alias="IncLocCity")
    state: Optional[str] = Field(None, alias="IncLocState")
    job_type_1: Optional[str] = Field(None, alias="OrgDescription02")
    job_type_2: Optional[str] = Field(None, alias="OrgDescription03")
    job_type_3: Optional[str] = Field(None, alias="OrgDescription04")
    environmental_outcome: Optional[str] = Field(None, alias="Environmental_Outcome")
    person_impacted_severity_outcome: Optional[str] = Field(None, alias="OSHASeverity")
    motor_vehicle_outcome: Optional[str] = Field(None, alias="MotorVehicle_Outcome")
    public_outcome: Optional[str] = Field(None, alias="Public_Outcome")
    process_safety_outcome: Optional[str] = Field(None, alias="ProcessSafety_Outcome")
    asset_outcome: Optional[str] = Field(None, alias="Asset_Outcome")
    task_type: Optional[str] = Field(None, alias="TaskTxt")
    description: Optional[str] = Field(None, alias="IncDescription")

    @validator("*")
    def cast_na_to_none(cls, v: str) -> Optional[Any]:
        if v == "NA" or v == "":
            return None
        return v
