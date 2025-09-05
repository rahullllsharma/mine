import type { Incident } from "@/types/project/Incident";
import type { HistoricalIncidentProps } from "../../templatesComponents/customisedForm.types";
import {
  ActionLabel,
  Badge,
  BodyText,
  Icon,
  SectionHeading,
} from "@urbint/silica";
import { useQuery } from "@apollo/client";
import { useContext, useState, useEffect, useRef, useMemo } from "react";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import GetHistoricIncidentsForTasks from "@/graphql/queries/getHistoricalIncidentsForTasks.gql";
import { convertDateToString } from "@/utils/date/helper";
import useRestMutation from "@/hooks/useRestMutation";
import axiosRest from "@/api/customFlowApi";

import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import { ExpandableText } from "../../shared/ExpandableText";
import { renderEmptyIncidents, formatSnakeCaseToTitleCase } from "./utils";

const HistoricalIncident = ({
  label,
  componentId,
  readOnly,
}: HistoricalIncidentProps) => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const [currentIncidentIndex, setCurrentIncidentIndex] = useState(0);
  const shouldSaveFormRef = useRef(false);
  const previousIncidentRef = useRef<Incident | null>(null);

  // Extract library task IDs from local activities
  const activitiesTasks = useMemo(
    () => state.form.component_data?.activities_tasks || [],
    [state.form.component_data?.activities_tasks]
  );
  const libraryTaskIds = useMemo(
    () =>
      activitiesTasks.length
        ? activitiesTasks.flatMap(activity =>
            activity.tasks
              .filter(task => task.selected === true)
              .map(task => task.libraryTask?.id || task.id)
          )
        : [],
    [activitiesTasks]
  );

  const { data: historicIncidentsForTasks } = useQuery(
    GetHistoricIncidentsForTasks,
    {
      fetchPolicy: "cache-and-network",
      variables: {
        libraryTaskIds: libraryTaskIds,
      },
      onCompleted: data => {
        if (componentId) {
          const incidents = data?.historicalIncidentsForTasks || [];
          shouldSaveFormRef.current = true;
          dispatch({
            type: CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT,
            payload: {
              componentId,
              incident: incidents.length > 0 ? incidents[0] : null,
            },
          });
        }
      },
    }
  );

  const incidents: Incident[] =
    historicIncidentsForTasks?.historicalIncidentsForTasks || [];

  // Get current incident
  const currentIncident = incidents ? incidents[currentIncidentIndex] : null;

  // API mutation to save form data
  const { mutate: updateForm } = useRestMutation({
    endpoint: `/forms/${state.form?.id}`,
    method: "put",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
  });

  // Function to save form data to API
  const saveFormData = () => {
    if (!state.form?.id) return;

    const apiData = {
      ...state.form,
    };

    updateForm(apiData);
  };

  // Shuffle function to randomly pick an incident
  const shuffleIncident = () => {
    if (incidents.length > 1) {
      let newIndex;
      do {
        newIndex = Math.floor(Math.random() * incidents.length);
      } while (newIndex === currentIncidentIndex && incidents.length > 1);

      setCurrentIncidentIndex(newIndex);

      // Update the state with the new incident
      shouldSaveFormRef.current = true;
      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT,
        payload: {
          componentId,
          incident: incidents[newIndex] || null,
        },
      });
    }
  };

  // Initialize historical incident in state when component loads and incidents are available
  useEffect(() => {
    if (componentId && historicIncidentsForTasks !== undefined) {
      shouldSaveFormRef.current = true;
      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT,
        payload: {
          componentId,
          incident: currentIncident,
        },
      });
    }
  }, [historicIncidentsForTasks, componentId, currentIncident]);

  // Save to API when form state changes (after incident is updated in state)
  useEffect(() => {
    if (
      shouldSaveFormRef.current &&
      state.form?.id &&
      historicIncidentsForTasks !== undefined
    ) {
      shouldSaveFormRef.current = false;
      previousIncidentRef.current = currentIncident;

      // Use Promise.resolve to ensure state has been updated before calling API
      Promise.resolve().then(() => {
        saveFormData();
      });
    }
  }, [state.form?.contents]);

  // If we have an empty array, still show the component but with no incident
  if (incidents.length === 0 || historicIncidentsForTasks === undefined) {
    return renderEmptyIncidents(label);
  }

  return (
    <div className="mt-6 p-4 bg-gray-100 rounded-md">
      <div className="flex justify-between items-start mb-3">
        <SectionHeading>{label}</SectionHeading>

        {!readOnly && (
          <ButtonSecondary
            label="Shuffle"
            iconStart="shuffle"
            onClick={shuffleIncident}
            disabled={incidents.length <= 1}
          />
        )}
      </div>

      <BodyText className="text-sm text-gray-600 mb-4">
        Safety records related to this job. Shuffle to view more records.
      </BodyText>

      {currentIncident && (
        <div className="bg-white p-4 rounded-md border border-gray-200">
          <ActionLabel className="font-bold text-lg mb-3">
            {currentIncident.incidentType}
          </ActionLabel>

          <div className="flex justify-between my-4">
            <div className="flex items-center gap-2">
              <Icon name="calendar" />
              <BodyText className="text-sm text-gray-600">
                {convertDateToString(currentIncident.incidentDate)}
              </BodyText>
            </div>
            {currentIncident?.severityCode && (
              <Badge
                label={formatSnakeCaseToTitleCase(
                  currentIncident?.severityCode
                )}
                className="px-2 py-1 bg-gray-200 text-gray-600 text-md rounded-full normal-case"
              />
            )}
          </div>
          <ExpandableText
            description={currentIncident?.description || ""}
            characterLimit={150}
            readMoreLabel="Read more"
            readLessLabel="Read less"
            iconStart="chevron_big_down"
          />
        </div>
      )}
    </div>
  );
};

export default HistoricalIncident;
