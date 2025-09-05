import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import type { LibraryTask } from "@/types/task/LibraryTask";
import type { ModalSize } from "@/components/shared/modal/Modal";
import type { HazardKeyInput } from "@/types/form/HazardInput";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { LocationHazardControlSettings } from "@/types/task/TaskData";
import type { WorkType } from "../../../types/task/WorkType";
import { useContext, useState } from "react";
import { useLazyQuery, useMutation, useQuery } from "@apollo/client";
import { FormProvider, useForm } from "react-hook-form";
import cx from "classnames";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import { groupByAliasesOrName } from "@/container/Utils";
import WorkTypeLinkedActivityTasks from "@/graphql/queries/workTypeLinkedActivityTasks.gql";
import { orderByCategory, orderByName } from "@/graphql/utils";
import ActivityConfiguration from "@/components/activity/activityConfiguration/ActivityConfiguration";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import {
  buildActivityName,
  getTaskListWithDuplicates,
  removeDuplicatedTaskIds,
} from "@/components/activity/utils";
import HazardsControlsLibrary from "@/graphql/queries/hazardsControlsLibrary.gql";
import LocationHazardControlSettingsQuery from "@/graphql/queries/locationHazardControlSettings.gql";
import { LibraryFilterType } from "@/types/LibraryFilterType";
import WorkTypeLinkedLibraryTasks from "@/graphql/queries/workTypeLinkedLibraryTasks.gql";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import {
  buildActivityData,
  getLocationHazardControlSettingChanges,
} from "@/utils/task";
import CreateActivity from "@/graphql/queries/createActivity.gql";
import UpdateLocationRecommendationSettings from "@/graphql/mutations/updateLocationHazardControlSettings.gql";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import ActivityTaskSelection from "@/components/activity/activityTaskSelection/ActivityTaskSelection";
import { useProjectSummaryEvents } from "@/container/projectSummaryView/context/ProjectSummaryContext";
import ActivityTypesLibrary from "@/graphql/queries/activityTypesLibrary.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

type AddActivityModalProps = {
  isOpen: boolean;
  closeModal: () => void;
  projectStartDate: string;
  projectEndDate: string;
  startDate: string;
  locationId: string;
  projectWorkTypes?: WorkType[];
};

export type ActivityFilter = {
  groupName: string;
  values: Array<CheckboxOption & { isCritical?: boolean }>;
};

export type ActivityTask = {
  libraryTaskId: string;
  hazards?: HazardKeyInput;
};

export type ActivityInputs = {
  locationId: string;
  name: string;
  startDate: string;
  endDate: string;
  status: { id: string; name: string };
  libraryActivityTypeId?: string;
  tasks: ActivityTask[];
  isCritical: boolean;
  criticalDescription: string | null;
};

const getModalTitle = (activityLabel: string) => [
  `Add an ${activityLabel}`,
  `Configure ${activityLabel}`,
];

export default function AddActivityModal({
  isOpen,
  closeModal,
  projectStartDate,
  projectEndDate,
  startDate,
  locationId,
  projectWorkTypes,
}: AddActivityModalProps): JSX.Element {
  const { activity: activityEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const toastCtx = useContext(ToastContext);
  const { task: taskEntity } = useTenantStore(state => state.getAllEntities());
  const events = useProjectSummaryEvents();

  useQuery(WorkTypeLinkedActivityTasks, {
    variables: {
      orderBy: [orderByCategory],
      workTypeIds: projectWorkTypes?.map(workType => workType.id),
    },
    onCompleted: data => {
      const tasks =
        data?.tenantAndWorkTypeLinkedLibraryTasks &&
        getTaskListWithDuplicates(data.tenantAndWorkTypeLinkedLibraryTasks);

      // Group tasks by aliases or names, which will deduplicate tasks within each group
      const tasksByCategory = groupByAliasesOrName<LibraryTask>(tasks);

      // Set the complete tasks list with deduplicated tasks
      setCompleteTasksList(tasks);
      setActivityFilters(
        Object.keys(tasksByCategory).map(groupName => ({
          groupName,
          values: [],
        }))
      );
    },
  });

  const { data: activityTypesLib = [] } = useQuery(ActivityTypesLibrary, {
    variables: {
      orderBy: [orderByName],
    },
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
    onCompleted: () => {
      events.refetchActivitiesBasedOnLocation();
      toastCtx?.pushToast("success", `${activityEntity.label} added`);
      closeModal();
    },
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast(
        "error",
        `Error adding ${activityEntity.label.toLowerCase()}`
      );
    },
  });

  const [updateLocationRecommendationSettings] = useMutation(
    UpdateLocationRecommendationSettings
  );

  const submitAddActivity = async (activityInputsData: ActivityInputs) => {
    return addActivity({
      variables: {
        activityData: buildActivityData(activityInputsData),
      },
    });
  };

  const submitUpdateLocationRecommendationSettings = async (
    activityInputsData: ActivityInputs,
    locationHazardControlSettingsData: LocationHazardControlSettings[]
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

  const [completeTasksList, setCompleteTasksList] = useState<LibraryTask[]>([]);
  const [step, setStep] = useState(0);
  const [activityFilters, setActivityFilters] = useState<ActivityFilter[]>([]);

  const isTaskSelection = step === 0;
  const isActivityConfiguration = step === 1;

  const methods = useForm<ActivityInputs>({
    mode: "onChange",
    defaultValues: {
      startDate,
      locationId,
      name: "",
      isCritical: false,
      criticalDescription: null,
    },
  });

  const {
    handleSubmit,
    setValue,
    trigger,
    formState: { isValid },
  } = methods;

  const getCheckboxUpdatedValues = (
    filteredValues: CheckboxOption[],
    newValue: CheckboxOption
  ) => {
    const updatedFilters: CheckboxOption[] = filteredValues;
    if (newValue.isChecked) {
      updatedFilters.push(newValue);
    } else {
      updatedFilters.splice(
        filteredValues.findIndex(item => item.id === newValue.id),
        1
      );
    }
    return updatedFilters;
  };

  const updateFilterHandler = (
    value: CheckboxOption,
    groupName: string
  ): void => {
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

  const [
    getTaskLibrary,
    { data: { tenantAndWorkTypeLinkedLibraryTasks = [] } = {} },
  ] = useLazyQuery<{
    tenantAndWorkTypeLinkedLibraryTasks: Array<TaskHazardAggregator>;
  }>(WorkTypeLinkedLibraryTasks, {
    fetchPolicy: "no-cache",
  });

  const getAllTasksToReview = (taskIds: string[]) => {
    getTaskLibrary({
      variables: {
        tasksLibraryId: taskIds,
        orderBy: [orderByName],
        hazardsOrderBy: [orderByName],
        controlsOrderBy: [orderByName],
        workTypeIds: projectWorkTypes?.map(workType => workType.id),
      },
    });
  };

  const goToNextStep = () => setStep(step + 1);
  const goToPreviousStep = () => setStep(step - 1);

  const nextClickHandler = () => {
    if (isTaskSelection) {
      const selectedItems = removeDuplicatedTaskIds(activityFilters);
      const selectedTaskIds = selectedItems
        .reduce(
          (acc, filter) => acc.concat(filter.values),
          [] as { id: string }[]
        )
        .map(task => task.id);
      getAllTasksToReview(selectedTaskIds);
      const selectedTaskCriticalActivity = selectedItems
        .reduce(
          (acc, filter) => acc.concat(filter.values),
          [] as { id: string; isCritical?: boolean }[]
        )
        .map(task => task.isCritical ?? false);
      const hasCriticalTask = selectedTaskCriticalActivity.includes(true);
      setValue("isCritical", hasCriticalTask);

      getHazardsControlsLibrary();
      getLocationHazardControlSettings();
      setValue("name", buildActivityName(selectedItems));
      trigger("name");
      goToNextStep();
    } else if (isActivityConfiguration) {
      handleSubmit(goToNextStep)();
    }
  };

  const cancelClickHandler = () => {
    closeModal();
  };

  const previousClickHandler = () => {
    goToPreviousStep();
  };

  const modalSize: ModalSize = step > 1 ? "lg" : "md";
  const isNextButtonDisabled = !areAnyFiltersSelected || (step > 1 && !isValid);

  const addactivitybutton = () => {
    handleSubmit(activity => {
      const activityWithTasks: ActivityInputs = {
        ...activity,
        tasks: tenantAndWorkTypeLinkedLibraryTasks.map(task => ({
          libraryTaskId: task.id,
        })),
      };
      submitAddActivity(activityWithTasks);
      submitUpdateLocationRecommendationSettings(
        activity,
        locationHazardControlSettings
      );
    })();
  };

  return (
    <Modal
      title={
        getModalTitle(activityEntity.label)[step] ||
        `Review ${taskEntity.labelPlural}`
      }
      isOpen={isOpen}
      closeModal={closeModal}
      className="my-4"
      size={modalSize}
    >
      <div className="flex flex-col gap-6">
        <FormProvider {...methods}>
          <div
            className={cx({
              block: isTaskSelection,
              hidden: !isTaskSelection,
            })}
          >
            <ActivityTaskSelection
              filteredTasks={activityFilters}
              activityTasks={completeTasksList}
              updateFilterHandler={updateFilterHandler}
            />
          </div>
          <div
            className={cx({
              block: isActivityConfiguration,
              hidden: !isActivityConfiguration,
            })}
          >
            <ActivityConfiguration
              minStartDate={projectStartDate}
              maxEndDate={projectEndDate}
              activityTypeLibrary={activityTypesLib}
            />
          </div>
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
                label="Add Activity"
                onClick={addactivitybutton}
                disabled={isNextButtonDisabled}
                loading={isLoading}
              />
            )}
          </div>
        </footer>
      </div>
    </Modal>
  );
}
