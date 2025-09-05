import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { TaskAnalysisInputs } from "@/types/report/DailyReportInputs";
import { Controller } from "react-hook-form";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import JobReportCard, {
  jobHazardAnalysisFormInputPrefix,
} from "../JobReportCard";
import { MarkAllControls } from "../markAllControls/MarkAllControls";

export type TaskReportCardProps = {
  task: TaskHazardAggregator;
  selectedTask?: TaskAnalysisInputs;
  isCompleted?: boolean;
};

export default function TaskReportCard({
  task,
  selectedTask,
  isCompleted,
}: TaskReportCardProps): JSX.Element {
  const { task: taskEntity } = useTenantStore(state => state.getAllEntities());
  const isMarkAllControlsVisible = !isCompleted;

  return (
    <>
      <JobReportCard
        job={task}
        selectedJob={selectedTask}
        switchLabel="Performed"
        formGroupKey="tasks"
        isCompleted={isCompleted}
      >
        {isMarkAllControlsVisible && (
          <MarkAllControls
            element={task}
            hazards={selectedTask?.hazards}
            formGroupKey="tasks"
          />
        )}
        <Controller
          name={`${jobHazardAnalysisFormInputPrefix}.tasks.${task.id}.notes`}
          defaultValue={selectedTask?.notes ?? ""}
          render={({ field }) => {
            return (
              <FieldTextArea
                {...field}
                initialValue={field.value}
                label={`${taskEntity.label} notes`}
                className={isCompleted ? "mb-2" : "mb-4"}
                readOnly={isCompleted}
              />
            );
          }}
        />
      </JobReportCard>
    </>
  );
}
