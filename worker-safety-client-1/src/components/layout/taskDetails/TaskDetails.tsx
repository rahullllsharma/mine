import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import TaskContentEdit from "@/components/layout/taskCard/content/TaskContentEdit";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import { excludeRecommendedHazards, isTaskComplete } from "@/utils/task";
import { getBorderColorByRiskLevel } from "@/utils/risk";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useHazardForm } from "../../detailsForm/hooks";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import { TaskDetailsHeader } from "./components/taskDetailsHeader/TaskDetailsHeader";
import { buildHazardOptions } from "./utils";

type TaskDetailsProps = {
  task: TaskHazardAggregator;
  hazardsLibrary: Hazard[];
  controlsLibrary: Control[];
  withTaskNameVisible?: boolean;
  controlFormPrefix?: `${string}.${number}`;
};

function TaskDetails({
  task,
  hazardsLibrary,
  controlsLibrary,
  controlFormPrefix,
  withTaskNameVisible = false,
}: TaskDetailsProps): JSX.Element {
  const useHazardFormOptions = buildHazardOptions(controlFormPrefix);

  const { hazard } = useTenantStore(state => state.getAllEntities());

  const {
    hazards,
    isAddButtonDisabled,
    addHazardHandler,
    removeHazardHandler,
    selectHazardHandler,
  } = useHazardForm(task.hazards, hazardsLibrary, useHazardFormOptions);

  const isTaskCompleted = isTaskComplete(task?.activity?.status);
  const canAddHazards = hazardsLibrary.length > 0 && !isTaskCompleted;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-2">
        {withTaskNameVisible && (
          <h5 className="font-semibold text-neutral-shade-58 text-lg">
            {task.name}
          </h5>
        )}
        {canAddHazards && (
          <ButtonSecondary
            label={`Add a ${hazard.label.toLowerCase()}`}
            iconStart="plus"
            size="sm"
            className="ml-auto"
            title={
              isAddButtonDisabled()
                ? `No more ${hazard.labelPlural.toLowerCase()} available`
                : ""
            }
            disabled={isAddButtonDisabled()}
            onClick={addHazardHandler}
          />
        )}
      </div>

      <section className="mt-2 bg-white">
        <TaskCard
          className={getBorderColorByRiskLevel(task.riskLevel)}
          taskHeader={<TaskDetailsHeader />}
        >
          <TaskContentEdit
            controlFormPrefix={controlFormPrefix}
            hazards={hazards}
            controlsLibrary={controlsLibrary}
            hazardsLibrary={excludeRecommendedHazards(
              hazardsLibrary,
              task.hazards
            )}
            onRemoveHazard={removeHazardHandler}
            onSelectHazard={selectHazardHandler}
            isDisabled={isTaskCompleted}
          />
        </TaskCard>
      </section>
    </div>
  );
}

export { TaskDetails };
export type { TaskDetailsProps };
