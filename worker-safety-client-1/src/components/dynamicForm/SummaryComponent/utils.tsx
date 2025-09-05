import type { SummaryHistoricalIncidentSettingProps } from "../../templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel, Subheading } from "@urbint/silica";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import { InputRaw } from "@/components/forms/Basic/Input";

const SummaryTextedBlankField = () => {
  return (
    <div className="flex flex-col items-center sm:flex-row gap-2 sm:gap-4 p-2 sm:p-4 bg-gray-100 h-24 sm:h-32 w-full mt-5">
      <BodyText className="text-neutrals-secondary">
        There are no sections available to be displayed on this page.
      </BodyText>
    </div>
  );
};

export const handlePreventInitialSpace = (
  e: React.KeyboardEvent<HTMLInputElement>,
  currentValue: string
): void => {
  if (e.key === " " && currentValue.length === 0) {
    e.preventDefault();
  }
};

export const handleHistoricalIncidentLabelChange = (
  value: string,
  setValue: ((value: string) => void) | undefined,
  maxLength = 50
): void => {
  if (
    value.length <= maxLength &&
    !(value.length === 1 && value === " ") &&
    setValue
  ) {
    setValue(value);
  }
};

export const SummaryHistoricalIncidentSetting = ({
  isHistoricalIncidentEnabled,
  setIsHistoricalIncidentEnabled,
  historicalIncidentLabel,
  setHistoricalIncidentLabel,
}: SummaryHistoricalIncidentSettingProps) => {
  return (
    <div className="mt-4">
      <Subheading>Job-Specific Safety Guide</Subheading>
      <BodyText className="pt-2">
        Adds a section to the end of the Summary that displays a single safety
        record related to the job. Users can shuffle to view additional records.
      </BodyText>
      <div className="flex flex-row mt-4">
        <Checkbox
          className="w-full gap-4"
          checked={isHistoricalIncidentEnabled}
          onClick={() => {
            const enableIncidnets = !isHistoricalIncidentEnabled;
            setIsHistoricalIncidentEnabled?.(enableIncidnets);
            if (
              enableIncidnets &&
              (!historicalIncidentLabel ||
                historicalIncidentLabel.trim() === "")
            ) {
              setHistoricalIncidentLabel?.("Job-Specific Safety Guide");
            }
          }}
        ></Checkbox>
        <BodyText className="pl-2">Enable this section</BodyText>
      </div>
      {isHistoricalIncidentEnabled && (
        <div className="flex flex-col mt-4">
          <ComponentLabel>Section Label*</ComponentLabel>
          <div className="relative">
            <InputRaw
              value={historicalIncidentLabel}
              onChange={value =>
                handleHistoricalIncidentLabelChange(
                  value,
                  setHistoricalIncidentLabel
                )
              }
              onKeyDown={e =>
                handlePreventInitialSpace(e, historicalIncidentLabel)
              }
              placeholder="Enter section label"
            />
            <BodyText className="absolute right-2 top-4 text-xs text-gray-500">
              {historicalIncidentLabel.length}/50
            </BodyText>
          </div>
        </div>
      )}
    </div>
  );
};

export { SummaryTextedBlankField };
