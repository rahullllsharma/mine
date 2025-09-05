import type {
  ActivitiesAndTasksCardProps,
  Activity,
  SelectedActivity,
  SelectedTask,
  SelectionPayload,
  ActivitiesData,
  UnifiedActivity,
} from "../../templatesComponents/customisedForm.types";
import type { IconName } from "@urbint/silica";
import { ActionLabel, CaptionText } from "@urbint/silica";
import { useQuery, useMutation } from "@apollo/client";
import { useContext, useState, useEffect } from "react";
import { validate as validateUuid } from "uuid";
import ActivitiesAndTasks from "@/graphql/queries/activitiesAndTasks.gql";
import DeleteActivity from "@/graphql/mutations/activities/deleteActivity.gql";
import DeleteTask from "@/graphql/queries/deleteTask.gql";
import { convertDateToString } from "@/utils/date/helper";
import useCWFFormState from "@/hooks/useCWFFormState";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { Checkbox } from "../../forms/Basic/Checkbox/Checkbox";
import { RiskLevel } from "../../riskBadge/RiskLevel";
import CustomisedFromStateContext from "../../../context/CustomisedDataContext/CustomisedFormStateContext";
import CardLazyLoader from "../../shared/cardLazyLoader/CardLazyLoader";
import Dropdown from "../../shared/dropdown/Dropdown";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import ToastContext from "../../shared/toast/context/ToastContext";
import CWFAddActivityModal from "./CWFAddActivityModal";
import DeleteActivityConfirmationModal from "./DeleteActivityConfirmationModal";
import { TasksBlankField } from "./utils";
import { CWFTaskCard } from "./CWFTaskCard";

const ActivitiesAndTasksCard = ({
  handleChangeInActivity,
  readOnly,
  inSummary,
  errorMessage,
}: ActivitiesAndTasksCardProps & { errorMessage?: string }): JSX.Element => {
  const { state } = useContext(CustomisedFromStateContext)!;
  const toastCtx = useContext(ToastContext);
  const { activity: activityEntity, task: taskEntity } = useTenantStore(
    tenantState => tenantState.getAllEntities()
  );
  const locationId = state.form?.metadata?.location?.id || "";
  const reportingDate = convertDateToString(
    state.form.properties?.report_start_date || new Date()
  );
  const hasWorkPackage = !!state.form?.metadata?.work_package;

  const {
    data = { activities: [] },
    loading,
    refetch,
  } = useQuery<ActivitiesData>(ActivitiesAndTasks, {
    fetchPolicy: "cache-and-network",
    variables: {
      locationId: locationId,
      date: reportingDate,
      filterTenantSettings: true,
    },
    skip: readOnly || !hasWorkPackage,
  });

  // Mutations for workpackage activities and tasks
  const [deleteActivityMutation, { loading: deleteActivityLoading }] =
    useMutation(DeleteActivity, {
      update: (cache, { data: mutationData }) => {
        if (mutationData?.deleteActivity && activityToDelete) {
          if (handleChangeInActivity) {
            const existingActivities =
              state.form?.component_data?.activities_tasks || [];
            const updatedActivities = existingActivities.filter(
              activity => activity.id !== activityToDelete.id
            );

            const payload: SelectionPayload = {
              activities: updatedActivities,
            };

            handleChangeInActivity(payload);
            setCWFFormStateDirty(true);
          }
        }
      },
      onCompleted: mutationData => {
        if (
          mutationData?.deleteActivity &&
          activityToDelete &&
          handleChangeInActivity
        ) {
          const existingActivities =
            state.form?.component_data?.activities_tasks || [];
          const updatedActivities = existingActivities.filter(
            activity => activity.id !== activityToDelete.id
          );

          const payload: SelectionPayload = {
            activities: updatedActivities,
          };

          handleChangeInActivity(payload);
          setCWFFormStateDirty(true);
        }
        refetch();
        toastCtx?.pushToast("success", `${activityEntity.label} deleted`);
      },
      onError: error => {
        toastCtx?.pushToast(
          "error",
          `Error deleting ${activityEntity.label.toLowerCase()}`
        );
        sessionExpiryHandlerForApolloClient(error);
      },
    });

  const [deleteTaskMutation, { loading: deleteTaskLoading }] = useMutation(
    DeleteTask,
    {
      update: (cache, { data: mutationData }) => {
        if (mutationData?.deleteTask && taskToDelete) {
          if (handleChangeInActivity) {
            const { task, activity } = taskToDelete;
            const existingActivities =
              state.form?.component_data?.activities_tasks || [];
            const updatedActivities = existingActivities.map(
              existingActivity => {
                if (existingActivity.id === activity.id) {
                  return {
                    ...existingActivity,
                    tasks: existingActivity.tasks.filter(t => t.id !== task.id),
                  };
                }
                return existingActivity;
              }
            );

            const payload: SelectionPayload = {
              activities: updatedActivities,
            };

            handleChangeInActivity(payload);
            setCWFFormStateDirty(true);
          }
          setSelectedActivities([]);
          setSelectedTasks([]);
        }
      },
      onCompleted: mutationData => {
        if (
          mutationData?.deleteTask &&
          taskToDelete &&
          handleChangeInActivity
        ) {
          const { task, activity } = taskToDelete;
          const existingActivities =
            state.form?.component_data?.activities_tasks || [];
          const updatedActivities = existingActivities.map(existingActivity => {
            if (existingActivity.id === activity.id) {
              return {
                ...existingActivity,
                tasks: existingActivity.tasks.filter(t => t.id !== task.id),
              };
            }
            return existingActivity;
          });

          const payload: SelectionPayload = {
            activities: updatedActivities,
          };

          handleChangeInActivity(payload);
          setCWFFormStateDirty(true);
        }
        setSelectedActivities([]);
        setSelectedTasks([]);

        toastCtx?.pushToast("success", `${taskEntity.label} deleted`);
      },
      onError: error => {
        toastCtx?.pushToast(
          "error",
          `Error deleting ${taskEntity.label.toLowerCase()}`
        );
        sessionExpiryHandlerForApolloClient(error);
      },
    }
  );

  // State to track selected activities and tasks
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);
  const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
  const [dataInitialized, setDataInitialized] = useState<boolean>(false);
  const { setCWFFormStateDirty } = useCWFFormState();

  const [activityToEdit, setActivityToEdit] = useState<SelectedActivity | null>(
    null
  );
  const [activityToDelete, setActivityToDelete] =
    useState<SelectedActivity | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isTaskDeleteModalOpen, setIsTaskDeleteModalOpen] = useState(false);

  // Combine API activities with CWF activities for display
  const apiActivities = data?.activities || [];
  const cwfActivitiesFromState =
    state.form?.component_data?.activities_tasks || [];

  const combinedActivities = [
    ...apiActivities,
    ...cwfActivitiesFromState.filter(
      (cwfActivity: SelectedActivity) =>
        !apiActivities.some(
          (apiActivity: Activity) => apiActivity.id === cwfActivity.id
        )
    ),
  ];

  const activities = readOnly ? cwfActivitiesFromState : combinedActivities;

  useEffect(() => {
    if (!dataInitialized) return;
    const updatedPayload = prepareSelectionPayload(
      selectedActivities,
      selectedTasks
    );
    if (handleChangeInActivity) {
      handleChangeInActivity(updatedPayload);
    }
  }, [dataInitialized]);

  useEffect(() => {
    if (!loading && data.activities.length > 0) {
      const newSelectedTasks: string[] = [];
      const newSelectedActivities: string[] = [];

      // Process each activity from work package/location
      data.activities.forEach((activity: Activity) => {
        let allTasksSelected = true;

        // Find matching activity in cwf Activities by ID
        const matchingCwfActivity = cwfActivitiesFromState.find(
          (cwfAct: SelectedActivity) => cwfAct.id === activity.id
        );

        // Process each task in this activity
        activity.tasks.forEach((task: any) => {
          let shouldSelect = true; // Default selection for tasks not in cwfActivity

          // If we found a matching activity in cwf data
          if (matchingCwfActivity) {
            // Find matching task by libraryTask.id
            const matchingCwfTask = matchingCwfActivity.tasks.find(
              (cwfTask: SelectedTask) => cwfTask.id === task.libraryTask?.id
            );

            // If found a matching task, use its selection status
            if (matchingCwfTask) {
              shouldSelect = matchingCwfTask.selected;
            }
          }

          if (shouldSelect) {
            newSelectedTasks.push(task.id);
          } else {
            allTasksSelected = false;
          }
        });

        // If all tasks in this activity are selected, select the activity too
        if (allTasksSelected && activity.tasks.length > 0) {
          newSelectedActivities.push(activity.id);
        }
      });

      // Also select all tasks from newly added CWF activities
      cwfActivitiesFromState.forEach((cwfActivity: SelectedActivity) => {
        if (
          !apiActivities.some(apiActivity => apiActivity.id === cwfActivity.id)
        ) {
          newSelectedActivities.push(cwfActivity.id);
          cwfActivity.tasks.forEach(task => {
            if (task.selected) {
              newSelectedTasks.push(task.id);
            }
          });
        }
      });

      setSelectedTasks([...new Set(newSelectedTasks)]);
      setSelectedActivities([...new Set(newSelectedActivities)]);
      setDataInitialized(true);
    }
  }, [data, loading, cwfActivitiesFromState]);

  const updateSelectionsAndNotify = (
    updatedActivities: string[],
    updatedTasks: string[]
  ) => {
    setSelectedActivities(updatedActivities);
    setSelectedTasks(updatedTasks);

    if (!dataInitialized) return;

    const updatedPayload = prepareSelectionPayload(
      updatedActivities,
      updatedTasks
    );
    if (handleChangeInActivity) {
      handleChangeInActivity(updatedPayload);
    }
    setCWFFormStateDirty(true);
  };

  const prepareSelectionPayload = (
    currentSelectedActivities: string[],
    currentSelectedTasks: string[]
  ): SelectionPayload => {
    const apiActivitiesForPayload = data?.activities || [];
    const selectedActivitiesData: SelectedActivity[] = [];

    // Process API activities
    apiActivitiesForPayload.forEach((activity: Activity) => {
      const formattedTasks: SelectedTask[] = activity.tasks.map((task: any) => {
        const isSelected = currentSelectedTasks.includes(task.id);
        return {
          id: task.libraryTask?.id || "",
          // TO:DO task.libraryTask?.name should be used here
          name: task?.name || "",
          fromWorkOrder: true,
          riskLevel: task.libraryTask?.riskLevel || "UNKNOWN",
          recommended: true,
          selected: isSelected,
        };
      });

      selectedActivitiesData.push({
        id: activity.id,
        isCritical: activity.isCritical,
        criticalDescription: activity.criticalDescription,
        name: activity.name,
        status: activity.status,
        startDate: activity.startDate,
        endDate: activity.endDate,
        taskCount: activity.tasks.length,
        tasks: formattedTasks,
      });
    });

    const cwfActivitiesNotFromApi = cwfActivitiesFromState.filter(
      (cwfActivity: SelectedActivity) =>
        !apiActivitiesForPayload.some(
          (apiActivity: Activity) => apiActivity.id === cwfActivity.id
        )
    );

    const updatedCwfActivities = cwfActivitiesNotFromApi.map(cwfActivity => {
      const updatedTasks = cwfActivity.tasks.map(task => ({
        ...task,
        selected: currentSelectedTasks.includes(task.id),
      }));
      return { ...cwfActivity, tasks: updatedTasks };
    });

    selectedActivitiesData.push(...updatedCwfActivities);

    return {
      activities: selectedActivitiesData,
    };
  };

  const handleActivitySelect = (
    activityId: string,
    tasks: any[],
    isSelected: boolean
  ): void => {
    let updatedActivities = [...selectedActivities];
    if (isSelected) {
      updatedActivities = [...new Set([...updatedActivities, activityId])];
    } else {
      updatedActivities = updatedActivities.filter(id => id !== activityId);
    }

    let updatedTasks = [...selectedTasks];
    const taskIds = tasks.map(task => task.id);

    if (isSelected) {
      updatedTasks = [...new Set([...updatedTasks, ...taskIds])];
    } else {
      updatedTasks = updatedTasks.filter(id => !taskIds.includes(id));
    }
    updateSelectionsAndNotify(updatedActivities, updatedTasks);
  };

  const handleTaskSelect = (
    taskId: string,
    activityId: string,
    allTasksInActivity: any[],
    isSelected: boolean
  ): void => {
    let updatedTasks = [...selectedTasks];
    if (isSelected) {
      updatedTasks = [...new Set([...updatedTasks, taskId])];
    } else {
      updatedTasks = updatedTasks.filter(id => id !== taskId);
    }

    let updatedActivities = [...selectedActivities];
    const activityTaskIds = allTasksInActivity.map(task => task.id);
    const allActivityTasksSelected = activityTaskIds.every(id =>
      updatedTasks.includes(id)
    );

    if (allActivityTasksSelected) {
      if (!updatedActivities.includes(activityId)) {
        updatedActivities = [...new Set([...updatedActivities, activityId])];
      }
    } else {
      if (updatedActivities.includes(activityId)) {
        updatedActivities = updatedActivities.filter(id => id !== activityId);
      }
    }
    updateSelectionsAndNotify(updatedActivities, updatedTasks);
  };

  const handleEditActivity = (activity: SelectedActivity) => {
    setActivityToEdit(activity);
    setIsEditModalOpen(true);
  };

  const handleDeleteActivity = (activity: SelectedActivity) => {
    setActivityToDelete(activity);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (!activityToDelete || !handleChangeInActivity) return;

    const isWorkpackageActivity =
      activityToDelete.id &&
      !activityToDelete.id.startsWith("adhoc-") &&
      !activityToDelete.id.startsWith("cwf-") &&
      validateUuid(activityToDelete.id);

    if (isWorkpackageActivity) {
      deleteActivityMutation({
        variables: {
          id: activityToDelete.id,
        },
      });
    } else {
      // Handle CWF activity deletion (existing logic)
      const existingActivities =
        state.form?.component_data?.activities_tasks || [];
      const updatedActivities = existingActivities.filter(
        activity => activity.id !== activityToDelete.id
      );

      const payload: SelectionPayload = {
        activities: updatedActivities,
      };

      handleChangeInActivity(payload);
      setCWFFormStateDirty(true);
    }

    setIsDeleteModalOpen(false);
    setActivityToDelete(null);
  };

  const handleEditComplete = (payload: SelectionPayload) => {
    if (handleChangeInActivity) {
      handleChangeInActivity(payload);
    }
    setCWFFormStateDirty(true);
    setIsEditModalOpen(false);
    setActivityToEdit(null);
  };

  const handleTaskDeleteConfirm = () => {
    if (!taskToDelete) return;

    const { task, activity } = taskToDelete;

    // Check if it's a workpackage task by ID format or isApiTask property
    // API tasks have backend-task- prefix or are marked as isApiTask
    const isWorkpackageTask =
      task.isApiTask || (task.id && task.id.startsWith("backend-task-"));

    if (isWorkpackageTask) {
      deleteTaskMutation({
        variables: {
          deleteTaskId: task.id,
        },
      });
    } else {
      // Handle CWF task deletion (remove from local state)
      const existingActivities =
        state.form?.component_data?.activities_tasks || [];
      const updatedActivities = existingActivities.map(existingActivity => {
        if (existingActivity.id === activity.id) {
          return {
            ...existingActivity,
            tasks: existingActivity.tasks.filter(t => t.id !== task.id),
          };
        }
        return existingActivity;
      });

      const payload: SelectionPayload = {
        activities: updatedActivities,
      };

      if (handleChangeInActivity) {
        handleChangeInActivity(payload);
      }
      setCWFFormStateDirty(true);
    }

    setIsTaskDeleteModalOpen(false);
    setTaskToDelete(null);
  };

  const createUnifiedActivity = (
    activity: Activity | SelectedActivity
  ): UnifiedActivity => {
    const isApiActivity =
      "tasks" in activity &&
      activity.tasks.length > 0 &&
      "libraryTask" in activity.tasks[0];

    if (isApiActivity) {
      // API activity - convert to unified format
      const apiActivity = activity as Activity;
      return {
        id: apiActivity.id,
        name: apiActivity.name,
        isCritical: apiActivity.isCritical,
        criticalDescription: apiActivity.criticalDescription,
        status: apiActivity.status,
        startDate: apiActivity.startDate,
        endDate: apiActivity.endDate,
        taskCount: apiActivity.taskCount,
        tasks: apiActivity.tasks.map(task => ({
          id: task.id,
          // TO:DO task.libraryTask?.name should be used here
          name: task?.name || "",
          riskLevel: task.libraryTask?.riskLevel || task.riskLevel || "UNKNOWN",
          selected: task.selected || false,
          isApiTask: true,
          originalTask: task,
        })),
      };
    } else {
      const cwfActivity = activity as SelectedActivity;
      return {
        id: cwfActivity.id,
        name: cwfActivity.name,
        isCritical: cwfActivity.isCritical,
        criticalDescription: cwfActivity.criticalDescription,
        status: cwfActivity.status,
        startDate: cwfActivity.startDate,
        endDate: cwfActivity.endDate,
        taskCount: cwfActivity.taskCount,
        tasks: cwfActivity.tasks.map(task => ({
          id: task.id,
          name: task.name,
          riskLevel: task.riskLevel,
          selected: task.selected,
          isApiTask: task.id.startsWith("backend-task-") || !!task.libraryTask,
          originalTask: task,
        })),
      };
    }
  };

  const unifiedActivities: UnifiedActivity[] = activities.map(
    createUnifiedActivity
  );

  const convertToSelectedActivity = (
    unifiedActivity: UnifiedActivity
  ): SelectedActivity => {
    return {
      id: unifiedActivity.id,
      name: unifiedActivity.name,
      isCritical: unifiedActivity.isCritical,
      criticalDescription: unifiedActivity.criticalDescription,
      status: unifiedActivity.status,
      startDate: unifiedActivity.startDate,
      endDate: unifiedActivity.endDate,
      taskCount: unifiedActivity.taskCount,
      tasks: unifiedActivity.tasks.map(task => {
        const isSelected = task.isApiTask
          ? selectedTasks.includes(task.id) || task.selected
          : task.selected;

        return {
          id: task.id,
          name: task.name,
          fromWorkOrder: task.isApiTask,
          riskLevel: task.riskLevel as keyof typeof RiskLevel,
          recommended: true,
          selected: isSelected,
          libraryTask: task.isApiTask
            ? task.originalTask.libraryTask
            : undefined,
        };
      }),
    };
  };

  const getActivityMenuItems = (activity: UnifiedActivity) => {
    if (readOnly || inSummary) return [];

    hasWorkPackage;
    return [
      [
        {
          label: "Edit",
          icon: "edit" as IconName,
          onClick: () =>
            handleEditActivity(convertToSelectedActivity(activity)),
        },
        {
          label: "Delete",
          icon: "trash_empty" as IconName,
          onClick: () =>
            handleDeleteActivity(convertToSelectedActivity(activity)),
        },
      ],
    ];
  };

  return (
    <div className="mt-2.5">
      {!inSummary && hasWorkPackage && (
        <CaptionText className="text-sm">
          Select the tasks you were responsible for overseeing at this location.{" "}
        </CaptionText>
      )}
      {loading ? (
        <CardLazyLoader cards={2} rowsPerCard={2} rowClassName="ml-12" />
      ) : activities.length === 0 ? (
        <TasksBlankField errorMessage={errorMessage} />
      ) : (
        unifiedActivities.map(activity => (
          <div
            key={activity.id}
            className={`mb-4 mt-5 ${
              inSummary ? "" : "bg-gray-100 rounded p-3"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                {inSummary ? (
                  activity.tasks.filter(task => task.selected).length > 0 && (
                    <ActionLabel className="mt-2.5">
                      {activity.name}
                    </ActionLabel>
                  )
                ) : hasWorkPackage ? (
                  <Checkbox
                    className="w-full gap-4"
                    checked={
                      selectedActivities.includes(activity.id) ||
                      activity.tasks.every(task => task.selected) ||
                      false
                    }
                    onClick={() =>
                      handleActivitySelect(
                        activity.id,
                        activity.tasks,
                        !selectedActivities.includes(activity.id)
                      )
                    }
                    disabled={readOnly}
                  >
                    <ActionLabel className="mt-2.5">
                      {activity.name}
                    </ActionLabel>
                  </Checkbox>
                ) : (
                  <ActionLabel className="mt-2.5">{activity.name}</ActionLabel>
                )}
              </div>

              {!readOnly && !inSummary && (
                <div className="ml-2">
                  <Dropdown
                    className="z-90"
                    menuItems={getActivityMenuItems(activity)}
                  >
                    <ButtonIcon iconName="more_horizontal" />
                  </Dropdown>
                </div>
              )}
            </div>

            <div className={`${inSummary ? "" : "ml-6"}`}>
              {activity.tasks &&
                activity.tasks
                  .filter(task =>
                    inSummary
                      ? selectedTasks.includes(task.id) || task?.selected
                      : true
                  )
                  .map(task =>
                    inSummary ? (
                      <CWFTaskCard
                        className="mt-2.5 gap-4"
                        key={task.id}
                        title={task.name}
                        risk={
                          task.riskLevel
                            ? RiskLevel[
                                task.riskLevel as keyof typeof RiskLevel
                              ]
                            : RiskLevel.UNKNOWN
                        }
                        showRiskInformation={true}
                        showRiskText={true}
                        withLeftBorder={true}
                      />
                    ) : hasWorkPackage ? (
                      <div
                        key={task.id}
                        className="flex items-center justify-between mt-2.5"
                      >
                        <Checkbox
                          className="w-full gap-4"
                          checked={
                            selectedTasks.includes(task.id) ||
                            task?.selected ||
                            false
                          }
                          labelClassName="w-full"
                          onClick={() =>
                            handleTaskSelect(
                              task.id,
                              activity.id,
                              activity.tasks,
                              !selectedTasks.includes(task.id)
                            )
                          }
                          disabled={readOnly}
                        >
                          <CWFTaskCard
                            title={task.name}
                            risk={
                              task.riskLevel
                                ? RiskLevel[
                                    task.riskLevel as keyof typeof RiskLevel
                                  ]
                                : RiskLevel.UNKNOWN
                            }
                            showRiskInformation={true}
                            showRiskText={true}
                            withLeftBorder={true}
                          />
                        </Checkbox>
                      </div>
                    ) : (
                      <div
                        key={task.id}
                        className="flex items-center justify-between mt-2.5"
                      >
                        <CWFTaskCard
                          className="mt-2.5 gap-4 flex-1"
                          title={task.name}
                          risk={
                            task.riskLevel
                              ? RiskLevel[
                                  task.riskLevel as keyof typeof RiskLevel
                                ]
                              : RiskLevel.UNKNOWN
                          }
                          showRiskInformation={true}
                          showRiskText={true}
                          withLeftBorder={true}
                        />
                      </div>
                    )
                  )}
            </div>
          </div>
        ))
      )}

      {activityToEdit && (
        <CWFAddActivityModal
          isOpen={isEditModalOpen}
          closeModal={() => {
            setIsEditModalOpen(false);
            setActivityToEdit(null);
          }}
          handleChangeInActivity={handleEditComplete}
          activityToEdit={activityToEdit}
          refetch={refetch}
        />
      )}

      <DeleteActivityConfirmationModal
        isOpen={isDeleteModalOpen}
        closeModal={() => {
          setIsDeleteModalOpen(false);
          setActivityToDelete(null);
        }}
        onConfirm={handleDeleteConfirm}
        isLoading={deleteActivityLoading}
      />

      <DeleteActivityConfirmationModal
        isOpen={isTaskDeleteModalOpen}
        closeModal={() => {
          setIsTaskDeleteModalOpen(false);
          setTaskToDelete(null);
        }}
        onConfirm={handleTaskDeleteConfirm}
        isLoading={deleteTaskLoading}
      />
    </div>
  );
};

export { ActivitiesAndTasksCard };
