import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { FormEventHandler } from "react";

import cx from "classnames";
import { Controller, useFormContext } from "react-hook-form";

import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import { getBorderColorByRiskLevel } from "@/utils/risk";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type TaskCardListItem = TaskHazardAggregator & {
  isSelected: boolean;
};

export type TasksProps = {
  tasks: TaskCardListItem[];
  isCompleted?: boolean;
};

export const taskFormInputPrefix = "taskSelection";

export default function Tasks({
  tasks = [],
  isCompleted,
}: TasksProps): JSX.Element {
  const {
    workPackage,
    location,
    task: taskEntity,
    activity: activityEntity,
  } = useTenantStore(state => state.getAllEntities());

  const isTaskVisible = (isSelected: boolean): boolean => {
    return !isCompleted || isSelected;
  };

  const filteredTasks =
    tasks?.length > 0
      ? tasks.filter(task => isTaskVisible(task.isSelected))
      : [];

  const hasTasks = filteredTasks?.length > 0;

  const { watch, getValues, setValue } = useFormContext();

  const fieldsAsArray = Object.values(watch()?.[taskFormInputPrefix] || []);

  // This is only needed if no selection is done
  const areAllTasksSelected =
    hasTasks &&
    (fieldsAsArray.length === 0
      ? filteredTasks.every(({ isSelected }) => !!isSelected)
      : fieldsAsArray.every(value => !!value));

  const onToggleAllHandler: FormEventHandler<HTMLInputElement> = ({
    currentTarget: { checked },
  }) => {
    Object.keys(getValues()[taskFormInputPrefix]).forEach(task => {
      setValue(`${taskFormInputPrefix}.${task}`, checked, {
        shouldDirty: true,
      });
    });
  };

  const onToggleHandler = (id: string) => {
    const inputName = `${taskFormInputPrefix}.${id}`;
    const inputValue = getValues(inputName);
    setValue(inputName, !inputValue, { shouldDirty: true });
  };

  return (
    <>
      <h3 className="text-xl text-neutral-shade-100 font-semibold">
        {`${activityEntity.label} ${taskEntity.label.toLowerCase()} selection`}
      </h3>
      <p className="text-sm text-neutral-shade-100">
        {`Select the ${taskEntity.labelPlural.toLowerCase()} you were responsible for overseeing at this ${location.label.toLowerCase()}`}
        .
      </p>
      {hasTasks ? (
        <div className="mt-4">
          {!isCompleted && (
            <label className="flex items-center mb-4 gap-4" htmlFor="all">
              <Checkbox
                id="all"
                checked={areAllTasksSelected}
                onChange={onToggleAllHandler}
              />
              <span className="font-semibold text-neutral-shade-75 hover:cursor-pointer">
                {`All ${taskEntity.labelPlural.toLowerCase()}`}
              </span>
            </label>
          )}
          <ul className="mt-4">
            {filteredTasks.map(
              ({ id, riskLevel, name, isSelected, activity }) => (
                <li key={id} className="flex gap-4 items-center mb-2">
                  {/* if we start to have performance issues, we should consider only using uncontrolled inputs */}
                  {!isCompleted && (
                    <Controller
                      name={`${taskFormInputPrefix}.${id}`}
                      defaultValue={isSelected}
                      render={({ field }) => (
                        <Checkbox
                          {...field}
                          checked={field.value}
                          value={`${taskFormInputPrefix}.${id}`}
                          aria-label={name}
                          className="mr-1"
                        />
                      )}
                    />
                  )}
                  <TaskCard
                    className={cx(
                      "flex-1 mb-0",
                      getBorderColorByRiskLevel(riskLevel)
                    )}
                    taskHeader={
                      <TaskHeader
                        headerText={name}
                        subHeaderText={activity?.name}
                        riskLevel={riskLevel}
                        onClick={() => onToggleHandler(id)}
                      />
                    }
                  />
                </li>
              )
            )}
          </ul>
        </div>
      ) : (
        <p className="mt-8 ">
          {`There are currently no ${activityEntity.labelPlural.toLowerCase()} in progress between the set
           ${workPackage.attributes.primeContractor.label.toLowerCase()} start and end dates.`}
        </p>
      )}
    </>
  );
}
