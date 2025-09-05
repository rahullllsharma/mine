import type { FormElementsType } from "@/components/templatesComponents/customisedForm.types";
import React from "react";
import {
  ActionLabel,
  BodyText,
  Badge,
  Icon,
} from "@urbint/silica";
import { convertDateToString } from "@/utils/date/helper";
import { formatSnakeCaseToTitleCase } from "@/components/dynamicForm/HistoricalIncident/utils";

const SummaryHistoricalIncident = ({
  content,
}: {
  content: FormElementsType;
}): JSX.Element => {
  const historicalIncident = content.properties?.historical_incident;
  return (
    <div className="p-4 bg-gray-100 rounded-md">
      <div className="flex justify-between items-start mb-3">
        <BodyText>{historicalIncident?.label}</BodyText>
      </div>

      {historicalIncident?.incident ? (
        <>
          <BodyText className="text-sm text-gray-600 mb-4">
            A safety record related to this job.
          </BodyText>
          <div className="bg-white p-4 rounded-md border border-gray-200">
            <ActionLabel className="font-bold text-lg mb-3">
              {historicalIncident.incident?.incidentType}
            </ActionLabel>

            <div className="flex justify-between my-4">
              <div className="flex items-center gap-2">
                <Icon name="calendar" />
                <BodyText className="text-sm text-gray-600">
                  {convertDateToString(
                    historicalIncident.incident?.incidentDate
                  )}
                </BodyText>
              </div>
              <Badge
                label={formatSnakeCaseToTitleCase(
                  historicalIncident.incident?.severity
                )}
                className="px-2 py-1 bg-gray-200 text-gray-600 text-md rounded-full normal-case"
              />
            </div>

            <div className="text-sm text-gray-700 leading-relaxed min-h-[80px] max-h-[200px] overflow-y-auto">
              {historicalIncident.incident?.description}
            </div>
          </div>
        </>
      ) : (
        <div>
          <BodyText className="text-sm text-gray-600 mt-2">
            No content available for this job.
          </BodyText>
        </div>
      )}
    </div>
  );
};

export default SummaryHistoricalIncident;
