import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { Control } from "@/types/project/Control";
import type {
  LocationHazardControlSettings,
  LocationHazardControlSettingsData,
  TaskData,
} from "@/types/task/TaskData";
import type { TaskFormControl } from "@/types/task/TaskFormControl";
import type { TaskFormHazard } from "@/types/task/TaskFormHazard";
import type { TaskInputs } from "@/types/task/TaskInputs";
import type { Hazard } from "@/types/project/Hazard";
import type { TaskSelectionSectionInputs } from "@/types/report/DailyReportInputs";
import type { ControlInput, ControlKeyInput } from "@/types/form/ControlInput";
import type { HazardInput, HazardKeyInput } from "@/types/form/HazardInput";
import type { SiteConditionInputs } from "@/types/siteCondition/SiteConditionInputs";
import type { SiteConditionData } from "@/types/siteCondition/SiteConditionData";
import type {
  ActivityInputs,
  ActivityTask,
} from "@/container/activity/addActivityModal/AddActivityModal";
import { map, keyBy, isEmpty, isNil } from "lodash-es";
import { TaskStatus } from "@/types/task/TaskStatus";

export const getFormHazards = (hazards: TaskFormHazard[]): HazardKeyInput => {
  return hazards.reduce((hazardAcc: HazardKeyInput, hazard: TaskFormHazard) => {
    const libraryHazardId = hazard.libraryHazard?.id;

    let hazardFormData: HazardInput = {
      libraryHazardId: libraryHazardId ?? hazard.id,
      isApplicable: hazard.isApplicable,
      controls: getHazardFormControls(hazard.controls as TaskFormControl[]),
    };

    if (libraryHazardId) {
      hazardFormData = { ...hazardFormData, id: hazard.id };
    }
    return {
      ...hazardAcc,
      [hazard.key]: hazardFormData,
    };
  }, {});
};

const getHazardFormControls = (
  controls: TaskFormControl[]
): ControlKeyInput => {
  return controls.reduce(
    (controlAcc: ControlKeyInput, control: TaskFormControl) => {
      const libraryControlId = control.libraryControl?.id;

      let controlFormData: ControlInput = {
        libraryControlId: libraryControlId ?? control.id,
        isApplicable: control.isApplicable,
      };

      if (libraryControlId) {
        controlFormData = { ...controlFormData, id: control.id };
      }
      return {
        ...controlAcc,
        [control.key]: controlFormData,
      };
    },
    {}
  );
};

const buildData = (hazards: HazardKeyInput = {}) => {
  return Object.values(hazards).map(hazard => ({
    ...hazard,
    controls: Object.values(hazard.controls ?? []),
  }));
};

// TODO: https://urbint.atlassian.net/browse/WSAPP-1268
// Remove this when the clean up is done.
type BuildTaskDataArgs = Omit<TaskInputs, "status" | "startDate" | "endDate"> &
  Partial<Pick<TaskInputs, "status" | "startDate" | "endDate">>;
type BuildTaskDataReturn = Omit<TaskData, "status" | "startDate" | "endDate"> &
  Partial<Pick<TaskData, "status" | "startDate" | "endDate">>;

export const buildTaskData = ({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  status,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  startDate,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  endDate,
  ...data
}: BuildTaskDataArgs): BuildTaskDataReturn => {
  const taskData: BuildTaskDataReturn = {
    ...data,
    hazards: buildData(data.hazards),
  };

  return taskData;
};

export const buildSiteConditionData = (
  data: SiteConditionInputs
): SiteConditionData => {
  return {
    ...data,
    hazards: buildData(data.hazards),
  };
};

const buildActivityTaskData = (tasks: ActivityTask[]) => {
  return Object.values(tasks).map(task => ({
    ...task,
    hazards: buildData(task.hazards),
  }));
};

export const buildActivityData = (activity: ActivityInputs) => {
  return {
    ...activity,
    ...(Object.keys(activity).includes("status") && {
      status: activity.status.id.toUpperCase(),
    }),
    tasks: buildActivityTaskData(activity.tasks),
  };
};

/**
 * Check if a given id exist in the list of controls
 *
 * While adding a new Task/Site Conditions, we use the `id` to compare;
 * While editing a Task/Site Condition, we already have an instance of control and then we use the `libraryControl.id` to compare
 *
 * Recommended controls are controls recommended by Urbint system and consequently createdBy is null by definition. Thus, return true
 * if `id` corresponds to Urbint's recommended control
 *
 * @param controls
 * @param id
 * @returns
 */
const hasRecommendedControl = (controls: Control[], id: string) =>
  controls.some(
    ({ libraryControl, createdBy, id: controlId }) =>
      !createdBy && (libraryControl?.id || controlId) === id
  );

/**
 * Get a list of controls that exclude the recommended controls for a given hazard
 *
 * @param controlsLibrary
 * @param controls
 * @returns
 */
export const excludeRecommendedControls = (
  controlsLibrary: Control[],
  controls: Control[]
): Control[] =>
  controlsLibrary.filter(({ id }) => !hasRecommendedControl(controls, id));

/**
 * Check if a given id exist in the list of hazards
 *
 * While adding a new Task/Site Conditions, we use the `id` to compare;
 * While editing a Task/Site Condition, we already have an instance of hazard and then we use the `libraryHazard.id` to compare
 *
 * Recommended hazards are controls recommended by Urbint system and consequently createdBy is null by definition. Thus, return true
 * if `id` corresponds to Urbint's recommended hazard
 *
 * @param hazards
 * @param id
 * @returns
 */
const hasRecommendedHazard = (hazards: Hazard[], id: string) =>
  hazards.some(
    hazard =>
      !hazard.createdBy && (hazard.libraryHazard?.id || hazard.id) === id
  );

/**
 * Get a list of hazards that exclude recommended hazards for a given task
 *
 * @param hazardsLibrary
 * @param hazards
 * @returns
 */
export const excludeRecommendedHazards = (
  hazardsLibrary: Hazard[],
  hazards: Hazard[]
): Hazard[] =>
  hazardsLibrary.filter(({ id }) => !hasRecommendedHazard(hazards, id));

/**
 * Maps a task list to a task list with the `isSelected` property that will be used
 * by the Tasks section (daily inspection report).
 *
 * When passes a selectedTasks, it will try to find which tasks is already selected and
 * mark it as selected.
 * By default, all tasks are disabled.
 *
 * @param {Array<HazardAggregator>} tasks
 * @param {TaskSelectionSectionInputs['selectedTasks']} selectedTasks
 * @returns Array<HazardAggregator & { isSelected: boolean }>
 */
export const transformTasksToListTasks = (
  tasks: TaskHazardAggregator[] = [],
  selectedTasks: TaskSelectionSectionInputs["selectedTasks"] = []
): Array<TaskHazardAggregator & { isSelected: boolean }> =>
  tasks.map(task => ({
    ...task,
    isSelected: selectedTasks.some(selectedTask => selectedTask.id === task.id),
  }));

export const isTaskComplete = (taskStatus?: TaskStatus): boolean =>
  taskStatus === TaskStatus.COMPLETE;

/**
 * Applies tenant/location specific settings to
 * recommended hazards and controls
 */
export const applyLocationHazardControlSettings = (
  task: TaskHazardAggregator,
  locationHazardControlSettings: LocationHazardControlSettings[]
) => {
  if (isEmpty(locationHazardControlSettings)) {
    return task;
  }

  const taskWithLocationSettings = { ...task };

  taskWithLocationSettings.hazards.map(hazard => {
    const settingForHazard = locationHazardControlSettings.find(
      hazardControlSetting =>
        hazardControlSetting.libraryHazardId === hazard.id &&
        isNil(hazardControlSetting.libraryControlId)
    );
    if (settingForHazard && settingForHazard.disabled) {
      hazard.isApplicable = false;
    }

    hazard.controls.map(control => {
      const settingForControl = locationHazardControlSettings.find(
        hazardControlSetting =>
          hazardControlSetting.libraryHazardId === hazard.id &&
          hazardControlSetting.libraryControlId === control.id
      );
      if (settingForControl && settingForControl.disabled) {
        control.isApplicable = false;
      }
    });
  });

  return taskWithLocationSettings;
};

/**
 * Analyzes an Activity input on submit and compares
 * changes to the Hazard/Control settings for the Activity's location.
 */
export const getLocationHazardControlSettingChanges = (
  activity: ActivityInputs,
  locationHazardControlSettings: LocationHazardControlSettings[]
): {
  newLocationHazardControlSettings: LocationHazardControlSettingsData[];
  existingHazardControlSettingsToRemove: string[];
} => {
  const newLocationHazardControlSettings: LocationHazardControlSettingsData[] =
      [],
    existingHazardControlSettingsToRemove: string[] = [];
  const { tasks, locationId } = activity;

  const locationHazardControlSettingsMap = keyBy(
    locationHazardControlSettings,
    setting => `${setting.libraryHazardId}${setting.libraryControlId ?? ""}`
  );

  tasks?.forEach(task => {
    map(task.hazards, hazard => {
      const settingsForJustHazard =
        locationHazardControlSettingsMap[hazard.libraryHazardId];

      // IF a hazard has been toggled off, record the hazard setting
      if (!hazard.isApplicable && !settingsForJustHazard) {
        return newLocationHazardControlSettings.push({
          locationId,
          libraryHazardId: hazard.libraryHazardId,
          libraryControlId: null,
        });
      }

      // IF a hazard has been re-enabled, remove existing preset setting
      if (
        hazard.isApplicable &&
        settingsForJustHazard &&
        settingsForJustHazard.disabled
      ) {
        existingHazardControlSettingsToRemove.push(settingsForJustHazard.id);
      }

      map(hazard.controls, control => {
        const matchingSettingForHazardAndControl =
          locationHazardControlSettingsMap[
            `${hazard.libraryHazardId}${control.libraryControlId}`
          ];
        // IF a controls has been toggled off, record the hazard/control setting
        if (!control.isApplicable && !matchingSettingForHazardAndControl) {
          newLocationHazardControlSettings.push({
            locationId,
            libraryHazardId: hazard.libraryHazardId,
            libraryControlId: control.libraryControlId,
          });
        }

        // IF any controls have been re-enabled, remove existing preset setting
        if (
          control.isApplicable &&
          matchingSettingForHazardAndControl &&
          matchingSettingForHazardAndControl.disabled
        ) {
          existingHazardControlSettingsToRemove.push(
            matchingSettingForHazardAndControl.id
          );
        }
      });
    });
  });

  return {
    newLocationHazardControlSettings,
    existingHazardControlSettingsToRemove,
  };
};
