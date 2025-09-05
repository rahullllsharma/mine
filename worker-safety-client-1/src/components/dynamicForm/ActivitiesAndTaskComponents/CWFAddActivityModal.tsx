import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import type { LibraryTask } from "@/types/task/LibraryTask";
import type {
  SelectionPayload,
  SelectedActivity,
  SelectedTask,
  CWFAddActivityModalProps,
  ActivityFilter,
  CWFActivityInputs,
} from "../../templatesComponents/customisedForm.types";
import { useState, useContext, useMemo, useEffect } from "react";
import { useQuery, useLazyQuery, useMutation } from "@apollo/client";
import { FormProvider, useForm, Controller } from "react-hook-form";
import cx from "classnames";
import { useRouter } from "next/router";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Modal from "@/components/shared/modal/Modal";
import Loader from "@/components/shared/loader/Loader";
import { groupByAliasesOrName } from "@/container/Utils";
import CWFActivitiesAndTasks from "@/graphql/queries/cwfActivitiesAndTasks.gql";
import ActivityTaskSelection from "@/components/activity/activityTaskSelection/ActivityTaskSelection";
import ActivityConfiguration from "@/components/activity/activityConfiguration/ActivityConfiguration";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import {
  getTaskListWithDuplicates,
  removeDuplicatedTaskIds,
  buildActivityName,
  extractBaseTaskId,
} from "@/components/activity/utils";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import HazardsControlsLibrary from "@/graphql/queries/hazardsControlsLibrary.gql";
import LocationHazardControlSettingsQuery from "@/graphql/queries/locationHazardControlSettings.gql";
import { LibraryFilterType } from "@/types/LibraryFilterType";
import WorkTypeLinkedLibraryTasks from "@/graphql/queries/workTypeLinkedLibraryTasks.gql";
import ActivityTypesLibrary from "@/graphql/queries/activityTypesLibrary.gql";
import { orderByName, orderByCategory } from "@/graphql/utils";
import {
  buildActivityData,
  getLocationHazardControlSettingChanges,
} from "@/utils/task";
import CreateActivity from "@/graphql/queries/createActivity.gql";
import UpdateLocationRecommendationSettings from "@/graphql/mutations/updateLocationHazardControlSettings.gql";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import RemoveTasksFromActivity from "@/graphql/queries/removeTasksFromActivity.gql";
import AddTasksToActivity from "@/graphql/queries/addTasksToActivity.gql";
import EditActivity from "@/graphql/mutations/activities/editActivity.gql";

const getModalTitle = (
  activityLabel: string,
  step: number,
  isEditing: boolean
) => {
  if (isEditing) {
    if (step === 0) return "Edit Tasks";
    if (step === 1) return `Configure ${activityLabel}`;
    return `Review ${activityLabel}`;
  }
  if (step === 0) return `Add Tasks`;
  if (step === 1) return `Configure ${activityLabel}`;
  return `Review ${activityLabel}`;
};

export default function CWFAddActivityModal({
  isOpen,
  closeModal,
  handleChangeInActivity,
  activityToEdit,
  refetch,
}: CWFAddActivityModalProps): JSX.Element {
  const { activity: activityEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const { task: taskEntity } = useTenantStore(state => state.getAllEntities());
  const { state } = useContext(CustomisedFromStateContext)!;
  const toastCtx = useContext(ToastContext);
  const router = useRouter();
  const { project, location } = router.query;

  // Check if work_package exists
  const hasWorkPackage = !!state.form?.metadata?.work_package || project;
  const locationId =
    state.form?.metadata?.location?.id || (location as string) || "";

  const isEditing = !!activityToEdit;

  // State for multi-step flow
  const [step, setStep] = useState(0);
  const [completeTasksList, setCompleteTasksList] = useState<LibraryTask[]>([]);
  const [activityFilters, setActivityFilters] = useState<ActivityFilter[]>([]);

  // Extract work type IDs from form state
  const workTypeIds = useMemo(() => {
    // First try to get work types from form state
    const formWorkTypes = state.form?.metadata?.work_types;
    if (formWorkTypes && formWorkTypes.length > 0) {
      return formWorkTypes.map(wt => wt.id);
    }

    try {
      const selectedWorkTypesValue = localStorage.getItem("selectedWorkTypes");
      if (selectedWorkTypesValue) {
        const selectedWorkTypes = JSON.parse(selectedWorkTypesValue);
        if (Array.isArray(selectedWorkTypes) && selectedWorkTypes.length > 0) {
          return selectedWorkTypes.map((workType: any) => workType.id);
        }
      }
    } catch (error) {
      console.warn("Error parsing selectedWorkTypes from localStorage:", error);
    }

    return [];
  }, [state.form?.metadata?.work_types]);

  // CWF Activities and Tasks query with dynamic work type IDs
  const { data: _cwfData, loading } = useQuery(CWFActivitiesAndTasks, {
    variables: {
      workTypeIds: workTypeIds,
      orderBy: [orderByCategory],
    },
    skip: workTypeIds.length === 0, // Skip if no work types are available
    onCompleted: data => {
      if (data?.tenantAndWorkTypeLinkedLibraryTasks) {
        const tasks = getTaskListWithDuplicates(
          data.tenantAndWorkTypeLinkedLibraryTasks
        );
        const tasksByCategory = groupByAliasesOrName<LibraryTask>(tasks);

        setCompleteTasksList(tasks);

        let existingSelectedTaskIds: Set<string>;

        if (isEditing && activityToEdit) {
          existingSelectedTaskIds = new Set(
            activityToEdit.tasks
              .filter(task => task.selected)
              .map(task => task.libraryTask?.id || task.id)
          );
        } else {
          existingSelectedTaskIds = new Set();
        }

        // Initialize filters with existing selections
        setActivityFilters(
          Object.keys(tasksByCategory).map(groupName => {
            const groupTasks = tasksByCategory[groupName];
            const selectedValues: Array<
              CheckboxOption & { isCritical?: boolean }
            > = [];

            groupTasks.forEach(task => {
              const normalizedTaskId = extractBaseTaskId(task.id);
              if (existingSelectedTaskIds.has(normalizedTaskId)) {
                selectedValues.push({
                  id: task.id,
                  name: task.name,
                  isChecked: true,
                  isCritical: task.isCritical,
                });
              }
            });

            return {
              groupName,
              values: selectedValues,
            };
          })
        );
      }
    },
  });

  // Queries for work package flow
  const { data: activityTypesLib = [] } = useQuery(ActivityTypesLibrary, {
    variables: {
      orderBy: [orderByName],
    },
    skip: !hasWorkPackage,
  });

  const [getHazardsControlsLibrary] = useLazyQuery(HazardsControlsLibrary, {
    variables: {
      type: LibraryFilterType.TASK,
      orderBy: [orderByName],
    },
  });

  const [
    getLocationHazardControlSettings,
    { data: { locationHazardControlSettings = [] } = {} },
  ] = useLazyQuery(LocationHazardControlSettingsQuery, {
    variables: {
      locationId,
    },
    fetchPolicy: "no-cache",
  });

  const [addActivity, { loading: isLoading }] = useMutation(CreateActivity, {
    onCompleted: data => {
      if (handleChangeInActivity && data?.createActivity) {
        const selectedTaskIds = activityFilters
          .flatMap(filter => filter.values)
          .map(task => task.id);

        const selectedTasksWithRiskData = completeTasksList.filter(task =>
          selectedTaskIds.includes(task.id)
        );

        const existingActivities =
          state.form?.component_data?.activities_tasks || [];

        let newTasksWithRiskData;
        if (hasWorkPackage) {
          // Allow all selected tasks for workpackage activities
          newTasksWithRiskData = selectedTasksWithRiskData;
        } else {
          // For non-workpackage activities, filter out existing tasks
          const existingTaskLibraryIds = new Set(
            existingActivities.flatMap(activity =>
              activity.tasks.map(task => task.libraryTask?.id || task.id)
            )
          );

          newTasksWithRiskData = selectedTasksWithRiskData.filter(task => {
            const baseTaskId = extractBaseTaskId(task.id);
            return !existingTaskLibraryIds.has(baseTaskId);
          });
        }

        if (newTasksWithRiskData.length > 0) {
          const newActivity: SelectedActivity = {
            id: data.createActivity.id,
            name: data.createActivity.name,
            isCritical: data.createActivity.isCritical,
            criticalDescription: data.createActivity.criticalDescription,
            status: data.createActivity.status,
            startDate: data.createActivity.startDate,
            endDate: data.createActivity.endDate,
            taskCount: newTasksWithRiskData.length,
            tasks: newTasksWithRiskData.map((task, index) => {
              const baseTaskId = extractBaseTaskId(task.id);

              return {
                id: `backend-task-${baseTaskId}-${Date.now()}-${index}`,
                name: task.name,
                fromWorkOrder: false,
                riskLevel:
                  (task.riskLevel as keyof typeof RiskLevel) ||
                  RiskLevel.UNKNOWN,
                recommended: true,
                selected: true,
                libraryTask: {
                  __typename: "LibraryTask",
                  id: baseTaskId,
                  name: task.name,
                  riskLevel:
                    (task.riskLevel as keyof typeof RiskLevel) ||
                    RiskLevel.UNKNOWN,
                },
              };
            }),
          };

          const updatedActivities = [...existingActivities, newActivity];
          handleChangeInActivity({ activities: updatedActivities });
        }

        toastCtx?.pushToast("success", `${activityEntity.label} added`);
        closeModal();
        if (hasWorkPackage && refetch) {
          refetch();
        }
      }
    },
    onError: (err: any) => {
      sessionExpiryHandlerForApolloClient(err);
      toastCtx?.pushToast(
        "error",
        `Error adding ${activityEntity.label.toLowerCase()}`
      );
    },
  });

  const [removeTasksFromActivityMutation, { loading: removeTasksLoading }] =
    useMutation(RemoveTasksFromActivity, {
      onError: error => {
        toastCtx?.pushToast("error", "Error removing tasks from activity");
        sessionExpiryHandlerForApolloClient(error);
      },
    });

  const [addTasksToActivityMutation, { loading: addTasksLoading }] =
    useMutation(AddTasksToActivity, {
      onError: error => {
        toastCtx?.pushToast("error", "Error adding tasks to activity");
        sessionExpiryHandlerForApolloClient(error);
      },
    });

  const [updateLocationRecommendationSettings] = useMutation(
    UpdateLocationRecommendationSettings
  );

  const [editActivityMutation, { loading: editActivityLoading }] = useMutation(
    EditActivity,
    {
      onError: error => {
        sessionExpiryHandlerForApolloClient(error);
      },
    }
  );

  const [
    getTaskLibrary,
    { data: { tenantAndWorkTypeLinkedLibraryTasks = [] } = {} },
  ] = useLazyQuery<{
    tenantAndWorkTypeLinkedLibraryTasks: Array<any>;
  }>(WorkTypeLinkedLibraryTasks, {
    fetchPolicy: "no-cache",
  });

  const methods = useForm<CWFActivityInputs>({
    mode: "onChange",
    defaultValues: {
      locationId,
      name: activityToEdit?.name || "",
      startDate:
        activityToEdit?.startDate ||
        (hasWorkPackage ? state.form?.metadata?.startDate || "" : ""), //need to update start date and end date for work package in the API
      endDate:
        activityToEdit?.endDate ||
        (hasWorkPackage ? state.form?.metadata?.endDate || "" : ""),
      status: activityToEdit?.status
        ? { id: activityToEdit.status, name: activityToEdit.status }
        : { id: "NOT_STARTED", name: "NOT_STARTED" },
      isCritical: activityToEdit?.isCritical || false,
      criticalDescription: activityToEdit?.criticalDescription || null,
    },
  });

  const {
    handleSubmit,
    setValue,
    trigger,
    reset,
    formState: { isValid },
  } = methods;

  useEffect(() => {
    if (isOpen) {
      reset({
        locationId,
        name: activityToEdit?.name || "",
        startDate:
          activityToEdit?.startDate ||
          (hasWorkPackage ? state.form?.metadata?.startDate || "" : ""),
        endDate:
          activityToEdit?.endDate ||
          (hasWorkPackage ? state.form?.metadata?.endDate || "" : ""),
        status: activityToEdit?.status
          ? { id: activityToEdit.status, name: activityToEdit.status }
          : { id: "NOT_STARTED", name: "NOT_STARTED" },
        isCritical: activityToEdit?.isCritical || false,
        criticalDescription: activityToEdit?.criticalDescription || null,
      });
    }
  }, [
    isOpen,
    activityToEdit,
    hasWorkPackage,
    state.form?.metadata?.startDate,
    state.form?.metadata?.endDate,
    reset,
  ]);

  const getCheckboxUpdatedValues = (
    filteredValues: CheckboxOption[],
    newValue: CheckboxOption | undefined
  ) => {
    if (!newValue) {
      return filteredValues;
    }

    const updatedFilters: CheckboxOption[] = [...filteredValues];
    if (newValue.isChecked) {
      updatedFilters.push(newValue);
    } else {
      const index = updatedFilters.findIndex(item => item.id === newValue.id);
      if (index !== -1) {
        updatedFilters.splice(index, 1);
      }
    }
    return updatedFilters;
  };

  const updateFilterHandler = (
    value: CheckboxOption | undefined,
    groupName: string
  ): void => {
    if (!value) return;

    setActivityFilters(prevState =>
      prevState.map(filter =>
        filter.groupName === groupName
          ? {
              groupName,
              values: [...getCheckboxUpdatedValues(filter.values, value)],
            }
          : filter
      )
    );
  };

  const areAnyFiltersSelected = activityFilters.some(
    filter => filter.values.length > 0
  );

  const getAllTasksToReview = (taskIds: string[]) => {
    getTaskLibrary({
      variables: {
        tasksLibraryId: taskIds,
        orderBy: [orderByName],
        hazardsOrderBy: [orderByName],
        controlsOrderBy: [orderByName],
        workTypeIds: workTypeIds,
      },
    });
  };

  const goToNextStep = () => setStep(step + 1);
  const goToPreviousStep = () => setStep(step - 1);

  const nextClickHandler = () => {
    if (step === 0) {
      const selectedItems = removeDuplicatedTaskIds(activityFilters);
      const selectedTaskIds = selectedItems
        .reduce(
          (acc, filter) => acc.concat(filter.values),
          [] as { id: string }[]
        )
        .map(task => task.id);

      if (workTypeIds.length > 0) {
        getAllTasksToReview(selectedTaskIds);
      }

      const selectedTaskCriticalActivity = selectedItems
        .reduce(
          (acc, filter) => acc.concat(filter.values),
          [] as { id: string; isCritical?: boolean }[]
        )
        .map(task => task.isCritical ?? false);
      const hasCriticalTask = selectedTaskCriticalActivity.includes(true);
      setValue("isCritical", hasCriticalTask);

      if (hasWorkPackage) {
        getHazardsControlsLibrary();
        getLocationHazardControlSettings();
        setValue("name", buildActivityName(selectedItems));
      } else {
        if (!isEditing) {
          const defaultName = buildActivityName(selectedItems);
          setValue("name", defaultName);
        }
      }
      trigger("name");
      goToNextStep();
    } else if (step === 1) {
      // For work package flow, go to next step
      if (hasWorkPackage) {
        handleSubmit(goToNextStep)();
      }
    }
  };

  const submitHandler = () => {
    if (!handleChangeInActivity) return;

    const selectedItems = removeDuplicatedTaskIds(activityFilters);

    const existingActivities =
      state.form?.component_data?.activities_tasks || [];

    if (isEditing && activityToEdit) {
      // Check if this is a workpackage activity (has an ID that matches API format)
      const isWorkpackageActivity =
        activityToEdit.id &&
        !activityToEdit.id.startsWith("adhoc-") &&
        !activityToEdit.id.startsWith("cwf-");

      if (isWorkpackageActivity && hasWorkPackage) {
        const selectedLibraryTaskIds = new Set(
          selectedItems
            .flatMap(item => item.values)
            .map(task => task.id.split("__")[0])
        );

        const tasksToRemove = activityToEdit.tasks
          .filter(task => {
            if (
              task.id.startsWith("backend-task-") ||
              task.id.startsWith("cwf-task-") ||
              task.id.startsWith("adhoc-")
            ) {
              return false;
            }
            const libraryTaskId = task.libraryTask?.id || task.id;
            return !selectedLibraryTaskIds.has(libraryTaskId);
          })
          .map(task => task.id);

        const currentLibraryTaskIds = new Set(
          activityToEdit.tasks.map(task => task.libraryTask?.id || task.id)
        );

        const tasksToAdd = Array.from(selectedLibraryTaskIds).filter(
          libraryTaskId => !currentLibraryTaskIds.has(libraryTaskId)
        );

        const taskOperations: Promise<any>[] = [];

        const newActivityName = methods.getValues("name");
        const hasNameChanged = newActivityName !== activityToEdit.name;

        if (hasNameChanged) {
          taskOperations.push(
            editActivityMutation({
              variables: {
                id: activityToEdit.id,
                name: newActivityName,
                startDate: activityToEdit.startDate,
                endDate: activityToEdit.endDate,
                status: activityToEdit.status,
                isCritical: activityToEdit.isCritical,
                criticalDescription: activityToEdit.criticalDescription,
              },
            })
          );
        }

        if (tasksToRemove.length > 0) {
          taskOperations.push(
            removeTasksFromActivityMutation({
              variables: {
                id: activityToEdit.id,
                taskIds: {
                  taskIdsToBeRemoved: tasksToRemove,
                },
              },
            }).catch(error => {
              throw error;
            })
          );
        }

        // Add new tasks that are selected
        if (tasksToAdd.length > 0) {
          const newTasksData = tasksToAdd.map(taskId => ({
            libraryTaskId: taskId,
            hazards: [],
          }));

          taskOperations.push(
            addTasksToActivityMutation({
              variables: {
                id: activityToEdit.id,
                newTasks: {
                  tasksToBeAdded: newTasksData,
                },
              },
            })
          );
        }

        // Execute all task operations
        Promise.all(taskOperations)
          .then(() => {
            toastCtx?.pushToast("success", `${activityEntity.label} updated`);
            closeModal();
            if (hasWorkPackage && refetch) {
              refetch();
            }
          })
          .catch(error => {
            toastCtx?.pushToast("error", "Error updating tasks" + error);
          });
      } else {
        // Non-workpackage activity editing
        const tasksByActivityGroup = new Map<
          string,
          {
            id: string;
            name: string;
            isCritical?: boolean;
            riskLevel?: string;
            libraryTaskId: string;
          }[]
        >();

        selectedItems.forEach(item => {
          item.values.forEach(task => {
            const taskData = completeTasksList.find(t => {
              const baseTaskId = extractBaseTaskId(t.id);
              return baseTaskId === task.id;
            });

            if (taskData) {
              const activityGroupName = item.groupName;
              if (!tasksByActivityGroup.has(activityGroupName)) {
                tasksByActivityGroup.set(activityGroupName, []);
              }
              tasksByActivityGroup.get(activityGroupName)!.push({
                id: task.id,
                name: taskData.name,
                isCritical: task.isCritical,
                riskLevel: taskData.riskLevel || "UNKNOWN",
                libraryTaskId: extractBaseTaskId(taskData.id),
              });
            }
          });
        });

        // Create a single updated activity
        const allTasks: {
          id: string;
          name: string;
          isCritical?: boolean;
          riskLevel?: string;
          libraryTaskId: string;
        }[] = [];
        tasksByActivityGroup.forEach(groupTasks =>
          allTasks.push(...groupTasks)
        );

        const formattedTasks: SelectedTask[] = allTasks.map((task, index) => ({
          id: `cwf-task-${task.libraryTaskId}-${Date.now()}-${index}`,
          name: task.name,
          fromWorkOrder: false,
          riskLevel:
            (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
          recommended: true,
          selected: true,
          libraryTask: {
            __typename: "LibraryTask",
            id: task.libraryTaskId,
            name: task.name,
            riskLevel:
              (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
          },
        }));

        const hasCriticalTask = allTasks.some(task => task.isCritical);

        const activityName = methods.getValues("name") || activityToEdit.name;

        const updatedActivity: SelectedActivity = {
          id: activityToEdit.id,
          name: activityName,
          isCritical: hasCriticalTask,
          criticalDescription: hasCriticalTask
            ? "Critical task selected"
            : null,
          status: activityToEdit.status,
          startDate: activityToEdit.startDate,
          endDate: activityToEdit.endDate,
          taskCount: formattedTasks.length,
          tasks: formattedTasks,
        };

        const updatedActivities = existingActivities.map(activity =>
          activity.id === activityToEdit.id ? updatedActivity : activity
        );

        const payload: SelectionPayload = {
          activities: updatedActivities,
        };

        handleChangeInActivity(payload);
        closeModal();
      }
    } else {
      if (hasWorkPackage) {
        // Work Package flow: create one activity per selected group
        const existingActivitiesByGroup = new Map<string, SelectedActivity>();
        existingActivities.forEach(activity => {
          const groupName =
            activity.name === "Selected Tasks" ? "General" : activity.name;
          existingActivitiesByGroup.set(groupName, activity);
        });

        const tasksByActivityGroup = new Map<
          string,
          {
            id: string;
            name: string;
            isCritical?: boolean;
            riskLevel?: string;
            libraryTaskId: string;
          }[]
        >();

        selectedItems.forEach(item => {
          item.values.forEach(task => {
            const taskData = completeTasksList.find(t => {
              const baseTaskId = extractBaseTaskId(t.id);
              return baseTaskId === task.id;
            });

            if (taskData) {
              const activityGroupName = item.groupName;
              if (!tasksByActivityGroup.has(activityGroupName)) {
                tasksByActivityGroup.set(activityGroupName, []);
              }
              tasksByActivityGroup.get(activityGroupName)!.push({
                id: task.id,
                name: taskData.name,
                isCritical: task.isCritical,
                riskLevel: taskData.riskLevel || "UNKNOWN",
                libraryTaskId: extractBaseTaskId(taskData.id),
              });
            }
          });
        });

        const updatedActivities: SelectedActivity[] = [];

        tasksByActivityGroup.forEach((tasks, activityGroupName) => {
          const formattedTasks: SelectedTask[] = tasks.map((task, index) => ({
            id: `cwf-task-${task.libraryTaskId}-${Date.now()}-${index}`,
            name: task.name,
            fromWorkOrder: false,
            riskLevel:
              (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
            recommended: true,
            selected: true,
            libraryTask: {
              __typename: "LibraryTask",
              id: task.libraryTaskId,
              name: task.name,
              riskLevel:
                (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
            },
          }));

          const hasCriticalTask = tasks.some(task => task.isCritical);
          const activityName =
            activityGroupName === "General"
              ? "Selected Tasks"
              : activityGroupName;
          const existingActivity =
            existingActivitiesByGroup.get(activityGroupName);

          if (existingActivity) {
            updatedActivities.push({
              ...existingActivity,
              tasks: [...existingActivity.tasks, ...formattedTasks],
              taskCount: existingActivity.tasks.length + formattedTasks.length,
              isCritical: existingActivity.isCritical || hasCriticalTask,
              criticalDescription:
                existingActivity.isCritical || hasCriticalTask
                  ? "Critical task selected"
                  : null,
            });
          } else {
            updatedActivities.push({
              id: `adhoc-${activityGroupName}-${Date.now()}`,
              name: activityName,
              isCritical: hasCriticalTask,
              criticalDescription: hasCriticalTask
                ? "Critical task selected"
                : null,
              status: "NOT_STARTED",
              startDate: new Date().toISOString().split("T")[0],
              endDate: new Date().toISOString().split("T")[0],
              taskCount: formattedTasks.length,
              tasks: formattedTasks,
            });
          }
        });

        existingActivities.forEach(activity => {
          const groupName =
            activity.name === "Selected Tasks" ? "General" : activity.name;
          if (!tasksByActivityGroup.has(groupName)) {
            updatedActivities.push(activity);
          }
        });

        const payload: SelectionPayload = { activities: updatedActivities };
        handleChangeInActivity(payload);
        closeModal();
      } else {
        // Non-workpackage flow: create a single activity with custom name
        const allTasks: {
          id: string;
          name: string;
          isCritical?: boolean;
          riskLevel?: string;
          libraryTaskId: string;
        }[] = [];

        selectedItems.forEach(item => {
          item.values.forEach(task => {
            const taskData = completeTasksList.find(t => {
              const baseTaskId = extractBaseTaskId(t.id);
              return baseTaskId === task.id;
            });

            if (taskData) {
              allTasks.push({
                id: task.id,
                name: taskData.name,
                isCritical: task.isCritical,
                riskLevel: taskData.riskLevel || "UNKNOWN",
                libraryTaskId: extractBaseTaskId(taskData.id),
              });
            }
          });
        });

        const formattedTasks: SelectedTask[] = allTasks.map((task, index) => ({
          id: `cwf-task-${task.libraryTaskId}-${Date.now()}-${index}`,
          name: task.name,
          fromWorkOrder: false,
          riskLevel:
            (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
          recommended: true,
          selected: true,
          libraryTask: {
            __typename: "LibraryTask",
            id: task.libraryTaskId,
            name: task.name,
            riskLevel:
              (task.riskLevel as keyof typeof RiskLevel) || RiskLevel.UNKNOWN,
          },
        }));

        const hasCriticalTask = allTasks.some(task => task.isCritical);
        const activityName = methods.getValues("name") || "Selected Tasks";

        const newActivity: SelectedActivity = {
          id: `adhoc-${Date.now()}`,
          name: activityName,
          isCritical: hasCriticalTask,
          criticalDescription: hasCriticalTask
            ? "Critical task selected"
            : null,
          status: "NOT_STARTED",
          startDate: new Date().toISOString().split("T")[0],
          endDate: new Date().toISOString().split("T")[0],
          taskCount: formattedTasks.length,
          tasks: formattedTasks,
        };

        const updatedActivities = [...existingActivities, newActivity];
        const payload: SelectionPayload = { activities: updatedActivities };
        handleChangeInActivity(payload);
        closeModal();
      }
    }
  };

  const submitAddActivity = async (activityInputsData: CWFActivityInputs) => {
    return addActivity({
      variables: {
        activityData: buildActivityData(activityInputsData),
      },
    });
  };

  const submitUpdateLocationRecommendationSettings = async (
    activityInputsData: CWFActivityInputs,
    locationHazardControlSettingsData: any[]
  ) => {
    const {
      newLocationHazardControlSettings,
      existingHazardControlSettingsToRemove,
    } = getLocationHazardControlSettingChanges(
      activityInputsData,
      locationHazardControlSettingsData
    );

    if (
      newLocationHazardControlSettings.length === 0 &&
      existingHazardControlSettingsToRemove.length === 0
    ) {
      return;
    }

    return updateLocationRecommendationSettings({
      variables: {
        locationHazardControlSettingsData: newLocationHazardControlSettings,
        locationHazardControlSettingIds: existingHazardControlSettingsToRemove,
      },
    });
  };

  const addActivityButton = () => {
    handleSubmit(activityData => {
      // Get selected task IDs
      const selectedTaskIds = activityFilters
        .flatMap(filter => filter.values)
        .map(task => task.id);

      // Normalize selected task IDs to match the lazy query results
      const normalizedSelectedTaskIds = selectedTaskIds.map(id =>
        extractBaseTaskId(id)
      );

      // Filter tenantAndWorkTypeLinkedLibraryTasks to only include selected tasks
      const newTasks = tenantAndWorkTypeLinkedLibraryTasks.filter(task =>
        normalizedSelectedTaskIds.includes(extractBaseTaskId(task.id))
      );

      const activityWithTasks: CWFActivityInputs = {
        ...activityData,
        tasks: newTasks.map(task => ({
          libraryTaskId: extractBaseTaskId(task.id),
        })),
      };

      // Only submit to backend - the form state will be updated in the mutation's onCompleted callback
      submitAddActivity(activityWithTasks);
      submitUpdateLocationRecommendationSettings(
        activityData,
        locationHazardControlSettings
      );
    })();
  };

  const cancelClickHandler = () => {
    closeModal();
  };

  const previousClickHandler = () => {
    goToPreviousStep();
  };

  const isTaskSelection = step === 0;
  const isActivityConfiguration = step === 1;

  const modalSize = step > 1 ? "lg" : "md";
  const isNextButtonDisabled = !areAnyFiltersSelected || (step > 1 && !isValid);

  return (
    <Modal
      title={
        getModalTitle(activityEntity.label, step, !!activityToEdit) ||
        `Review ${taskEntity.labelPlural}`
      }
      isOpen={isOpen}
      closeModal={closeModal}
      className="my-4"
      size={modalSize}
    >
      <div className="flex flex-col gap-6">
        <FormProvider {...methods}>
          {/* Task Selection Step */}
          <div
            className={cx({
              block: isTaskSelection,
              hidden: !isTaskSelection,
            })}
          >
            {loading ? (
              <div className="flex justify-center items-center py-8">
                <Loader />
              </div>
            ) : (
              <ActivityTaskSelection
                filteredTasks={activityFilters}
                activityTasks={completeTasksList}
                updateFilterHandler={updateFilterHandler}
                isEditing={isEditing}
              />
            )}
          </div>

          {/* Activity Configuration Step (only for work package flow) */}
          {hasWorkPackage && (
            <div
              className={cx({
                block: isActivityConfiguration,
                hidden: !isActivityConfiguration,
              })}
            >
              <ActivityConfiguration
                minStartDate={
                  state.form?.metadata?.startDate ||
                  new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
                    .toISOString()
                    .split("T")[0]
                }
                maxEndDate={
                  state.form?.metadata?.endDate ||
                  new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
                    .toISOString()
                    .split("T")[0]
                }
                activityTypeLibrary={activityTypesLib}
              />
            </div>
          )}

          {/* Simple Name Configuration Step (forAd-hoc package flow) */}
          {!hasWorkPackage && (
            <div
              className={cx({
                block: isActivityConfiguration,
                hidden: !isActivityConfiguration,
              })}
            >
              <div className="flex flex-col gap-4">
                <Controller
                  name="name"
                  rules={{ required: "Activity name is required" }}
                  defaultValue=""
                  render={({ field }) => (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Activity Name *
                      </label>
                      <input
                        {...field}
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter activity name"
                        onChange={e => {
                          const inputValue = e.target.value;
                          if (/^\s/.test(inputValue)) {
                            field.onChange(inputValue.trimStart());
                          } else {
                            field.onChange(inputValue);
                          }
                        }}
                      />
                    </div>
                  )}
                />
              </div>
            </div>
          )}
        </FormProvider>

        <footer className="flex">
          {step > 0 && (
            <ButtonSecondary
              iconStart="chevron_big_left"
              label="Previous"
              onClick={previousClickHandler}
            />
          )}
          <div className="flex flex-1 justify-end">
            <ButtonRegular
              className="mr-2"
              label="Cancel"
              onClick={cancelClickHandler}
            />

            {/* For work package flow */}
            {hasWorkPackage ? (
              <>
                {isTaskSelection && (
                  <ButtonPrimary
                    label="Next"
                    onClick={nextClickHandler}
                    disabled={isNextButtonDisabled}
                    loading={isLoading}
                  />
                )}

                {isActivityConfiguration && (
                  <ButtonPrimary
                    label={isEditing ? "Done" : "Add Tasks"}
                    onClick={isEditing ? submitHandler : addActivityButton}
                    disabled={isNextButtonDisabled}
                    loading={
                      isEditing
                        ? removeTasksLoading ||
                          addTasksLoading ||
                          editActivityLoading
                        : isLoading
                    }
                  />
                )}
              </>
            ) : (
              /* ForAd-hoc package flow */
              <>
                {isTaskSelection && (
                  <ButtonPrimary
                    label="Next"
                    onClick={nextClickHandler}
                    disabled={isNextButtonDisabled}
                    loading={isLoading}
                  />
                )}

                {isActivityConfiguration && (
                  <ButtonPrimary
                    label={isEditing ? "Done" : "Add Tasks"}
                    onClick={submitHandler}
                    disabled={!isValid}
                    loading={isLoading}
                  />
                )}
              </>
            )}
          </div>
        </footer>
      </div>
    </Modal>
  );
}
