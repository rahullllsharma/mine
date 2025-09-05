import type {
  ActivePageObjType,
  ActivitiesAndTasksFormType,
  Hazards,
  SelectedActivity,
  Task,
  WorkTypes,
} from "../../templatesComponents/customisedForm.types";
import { FormProvider, useForm } from "react-hook-form";
import { useContext, useEffect, useMemo, useState } from "react";
import { useQuery } from "@apollo/client";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import WorkTypeLinkedLibraryTasks from "@/graphql/queries/workTypeLinkedLibraryTasks.gql";
import { validateField } from "../../templatesComponents/customisedForm.utils";
import ActivitiesAndTaskComponent from "./ActivitiesAndTaskComponent";

const CWFActivitiesAndTask = ({
  mode,
  item,
  inSummary,
}: {
  mode: string;
  section: any;
  activePageDetails: ActivePageObjType;
  item: ActivitiesAndTasksFormType;
  inSummary?: boolean;
}) => {
  const methods = useForm({
    defaultValues: { activities_tasks: [] },
  });
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  // Local state to track changes before saving
  const [localActivities, setLocalActivities] = useState<SelectedActivity[]>(
    state.form.component_data?.activities_tasks || []
  );

  const [validationError, setValidationError] = useState<{
    show: boolean;
    message: string;
  }>({
    show: false,
    message: "",
  });

  useEffect(() => {
    const globalActivities = state.form.component_data?.activities_tasks || [];
    setLocalActivities(globalActivities);
  }, [state.form.component_data?.activities_tasks]);

  // Extract library task IDs from local activities
  const activitiesTasks = localActivities;
  const libraryTaskIds = activitiesTasks.length
    ? activitiesTasks.flatMap(activity =>
        activity.tasks
          .filter(task => task.selected === true)
          .map(task => task.libraryTask?.id || task.id)
      )
    : [];

  const workTypeIds = useMemo(() => {
    // First try to get work types from form state
    const formWorkTypes = state.form.metadata?.work_types;
    if (formWorkTypes && formWorkTypes.length > 0) {
      return formWorkTypes.map((workType: WorkTypes) => workType.id);
    }

    try {
      const selectedWorkTypesValue = localStorage.getItem("selectedWorkTypes");
      if (selectedWorkTypesValue) {
        const selectedWorkTypes = JSON.parse(selectedWorkTypesValue);
        if (Array.isArray(selectedWorkTypes) && selectedWorkTypes.length > 0) {
          return selectedWorkTypes.map((workType: WorkTypes) => workType.id);
        }
      }
    } catch (error) {
      console.warn("Error parsing selectedWorkTypes from localStorage:", error);
    }

    return [];
  }, [state.form.metadata?.work_types]);

  const shouldFetchTasksWithWorkTypes =
    libraryTaskIds.length > 0 && workTypeIds.length > 0;

  // fetch hazards by library id from tasks saved in the form
  const { data: tasksHazardData, loading: loadingTasks } = useQuery(
    WorkTypeLinkedLibraryTasks,
    {
      fetchPolicy: "no-cache",
      variables: {
        tasksLibraryId: libraryTaskIds,
        workTypeIds: workTypeIds,
      },
      skip: !shouldFetchTasksWithWorkTypes, // Ensures query runs only when needed
    }
  );

  const handleChangeInActivity = (value: {
    activities: SelectedActivity[];
  }) => {
    // Update local state with activities array
    setLocalActivities(value.activities);

    setValidationError({ show: false, message: "" });

    // Immediately update the global form state so activities appear in the card right away
    dispatch({
      type: CF_REDUCER_CONSTANTS.ACTIVITIES_VALUE_CHANGE,
      payload: value.activities,
    });
  };

  // Listen for save event to dispatch changes and log data
  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        const validationResult = validateField(
          [item],
          state.form.component_data
        );

        if (!validationResult.isValid) {
          setValidationError({
            show: true,
            message:
              validationResult.errorMessage ||
              "Please select at least one activity",
          });
          return;
        }

        setValidationError({ show: false, message: "" });

        // Calculate current libraryTaskIds based on latest localActivities
        const currentTaskIds = localActivities.length
          ? localActivities.flatMap(activity =>
              activity.tasks
                .filter(task => task.selected === true)
                .map(task => task.libraryTask?.id || task.id)
            )
          : [];

        // Get existing tasks from state
        const existingTasks =
          state.form.component_data?.hazards_controls?.tasks || [];

        // Create a map of existing tasks by ID for quick lookup
        const existingTasksMap = new Map(
          existingTasks.map(task => [task.id, task])
        );

        // New tasks from the API response
        const newTasksFromAPI =
          tasksHazardData?.tenantAndWorkTypeLinkedLibraryTasks || [];
        const newTasksMap = new Map(
          newTasksFromAPI.map((task: Hazards) => [task.id, task])
        );

        // Final tasks array should only include currently selected tasks
        const updatedTasks = currentTaskIds
          .map(taskId => {
            if (existingTasksMap.has(taskId)) {
              return existingTasksMap.get(taskId);
            } else if (newTasksMap.has(taskId)) {
              return newTasksMap.get(taskId);
            }

            // This should not happen if the API works correctly
            console.warn(
              `Task with ID ${taskId} not found in API response or existing tasks`
            );
            return null;
          })
          .filter(Boolean); // Remove any null values

        // Update tasks in state
        dispatch({
          type: CF_REDUCER_CONSTANTS.SET_TASKS_HAZARD_DATA,
          payload: updatedTasks as Task[],
        });

        // Note: Activities are now updated immediately in handleChangeInActivity
        // so we don't need to update them again here
      }
    );

    return () => {
      token.remove();
    };
  }, [
    localActivities,
    dispatch,
    tasksHazardData,
    loadingTasks,
    state.form.component_data?.hazards_controls?.tasks,
    item,
    state.form.component_data,
  ]);

  return (
    <FormProvider {...methods}>
      <ActivitiesAndTaskComponent
        id={item.id}
        configs={{
          title: item.properties.title || "Activities And Tasks",
          buttonIcon: "image_alt",
        }}
        mode={mode}
        handleChangeInActivity={handleChangeInActivity}
        inSummary={inSummary}
        errorMessage={
          validationError.show ? validationError.message : undefined
        }
      />
    </FormProvider>
  );
};

export default CWFActivitiesAndTask;
