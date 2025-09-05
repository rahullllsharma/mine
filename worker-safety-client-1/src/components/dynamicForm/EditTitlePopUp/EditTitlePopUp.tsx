import type { EditTitlePopUpProps } from "@/components/templatesComponents/customisedForm.types";
import { CaptionText, ComponentLabel } from "@urbint/silica";
import React from "react";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import Modal from "@/components/shared/modal/Modal";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { Toggle } from "@/components/forms/Basic/Toggle";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import { InputRaw } from "@/components/forms/Basic/Input";
import { SummaryHistoricalIncidentSetting } from "../SummaryComponent/utils";

const EditTitlePopUp = ({
  isEditModalOpen,
  setIsEditModalOpen,
  titleName,
  setTitleName,
  onSaveTitle,
  onUpdateAdditionalField,
  isSmartAddressChecked = true, // Default value set to true
  setIsSmartAddressChecked,
  item,
  subTitle,
  isEnergyWheelEnabled,
  setSubTitle,
  setIsEnergyWheelEnabled,
  isHistoricalIncidentEnabled = false,
  setIsHistoricalIncidentEnabled,
  historicalIncidentLabel = "",
  setHistoricalIncidentLabel,
}: EditTitlePopUpProps) => {
  const getTitle = (componentType?: string): string => {
    switch (componentType) {
      case CWFItemType.Attachment:
        return item.properties?.attachment_type === "photo"
          ? "Photo Attachments Setting"
          : "Documents Attachments Setting";
      case CWFItemType.ActivitiesAndTasks:
        return "Activities and Task Setting";
      case CWFItemType.HazardsAndControls:
        return "Hazards and Controls Setting";
      case CWFItemType.Summary:
        return "Summary Setting";
      case CWFItemType.SiteConditions:
        return "Site Conditions Setting";
      case CWFItemType.Location:
        return "Location Setting";
      case CWFItemType.NearestHospital:
        return "Nearest Hospital Setting";
      case CWFItemType.PersonnelComponent:
        return "Personnel Component Setting";
      default:
        return "Settings";
    }
  };

  const isHazardsSetting = item.type.includes("hazards");

  const handleSave = (component?: string) => {
    if (!titleName.trim()) {
      return;
    }

    switch (component) {
      case CWFItemType.Summary:
        if (isHistoricalIncidentEnabled && !historicalIncidentLabel.trim()) {
          return;
        }
        break;
      case CWFItemType.HazardsAndControls:
        if (!subTitle.trim()) {
          return;
        }
        break;
      default:
        break;
    }

    onSaveTitle(component || "");
  };

  const getAdditionalField = (componentType?: string): JSX.Element => {
    switch (componentType) {
      case CWFItemType.Location:
        return (
          <div className="flex w-full gap-4 flex-row items-center mt-4">
            <Checkbox
              className="w-full gap-4"
              checked={isSmartAddressChecked}
              disabled={true}
              onClick={() => {
                setIsSmartAddressChecked(!isSmartAddressChecked);
                onUpdateAdditionalField(componentType);
              }}
            ></Checkbox>
            <CaptionText>Smart Address Input</CaptionText>
          </div>
        );
      case CWFItemType.HazardsAndControls:
        return (
          <>
            <div className="flex items-center gap-2 mt-4">
              <ComponentLabel>Energy Wheel</ComponentLabel>
              <Toggle
                checked={isEnergyWheelEnabled}
                onClick={() => setIsEnergyWheelEnabled(!isEnergyWheelEnabled)}
              />
            </div>
            <div className="flex flex-col mt-4">
              <ComponentLabel>High Energy Hazard Label*</ComponentLabel>
              <InputRaw
                value={subTitle}
                onChange={setSubTitle}
                placeholder="Enter field Label"
              />
            </div>
          </>
        );
      case CWFItemType.Summary:
        return (
          <SummaryHistoricalIncidentSetting
            isHistoricalIncidentEnabled={isHistoricalIncidentEnabled}
            setIsHistoricalIncidentEnabled={setIsHistoricalIncidentEnabled}
            historicalIncidentLabel={historicalIncidentLabel}
            setHistoricalIncidentLabel={setHistoricalIncidentLabel}
          />
        );
      default:
        return <></>;
    }
  };

  const getSaveButtonDisabled = (component?: string): boolean => {
    if (!titleName.trim()) {
      return true;
    }

    switch (component) {
      case CWFItemType.Summary:
        return isHistoricalIncidentEnabled && !historicalIncidentLabel.trim();
      case CWFItemType.HazardsAndControls:
        return !subTitle.trim();
      default:
        return false;
    }
  };

  return (
    <Modal
      title={getTitle(item?.type)}
      isOpen={isEditModalOpen}
      closeModal={() => setIsEditModalOpen(false)}
      size="lg"
    >
      <div className={"flex flex-col "}>
        <ComponentLabel>Label*</ComponentLabel>
        <InputRaw
          value={titleName}
          onChange={setTitleName}
          placeholder="Enter field Label"
        />
        {getAdditionalField(item?.type)}
        <div
          className={`flex justify-end gap-2 pt-4 border-t ${
            isHazardsSetting ? "mt-4" : "mt-16"
          }`}
        >
          <ButtonRegular
            label="Cancel"
            onClick={() => setIsEditModalOpen(false)}
          />
          <ButtonPrimary
            label="Save"
            onClick={() => handleSave(item?.type)}
            disabled={getSaveButtonDisabled(item?.type)}
          />
        </div>
      </div>
    </Modal>
  );
};

export default EditTitlePopUp;
