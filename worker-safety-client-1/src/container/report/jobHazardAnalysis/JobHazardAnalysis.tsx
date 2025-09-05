import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "@/types/project/HazardAggregator";
import type {
  JobHazardAnalysisSectionInputs,
  TaskAnalysisInputs,
  SiteConditionAnalysisInputs,
} from "@/types/report/DailyReportInputs";
import SiteConditionsReportCard from "@/components/report/jobReport/siteConditionReportCard/SiteConditionReportCard";
import TaskReportCard from "@/components/report/jobReport/taskReportCard/TaskReportCard";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type SiteConditionOrTaskAnalysisInputs =
  | SiteConditionAnalysisInputs
  | TaskAnalysisInputs;

type JobWrapperProps = {
  type?: "task" | "siteCondition";
  title: string;
  list:
    | HazardAggregator[]
    | TaskHazardAggregator[]
    | SiteConditionOrTaskAnalysisInputs[];
  selections?: SiteConditionOrTaskAnalysisInputs[];
  isCompleted?: boolean;
};

const JobWrapper = ({
  type = "siteCondition",
  title,
  list,
  selections = [],
  isCompleted,
}: JobWrapperProps): JSX.Element => {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const hasElementsInList = Array.isArray(list) && list.length > 0;
  return (
    <section data-print-section>
      <h5 className="font-semibold mb-4">{title}</h5>
      {hasElementsInList ? (
        list.map(element => (
          <div className="mb-6 last:mb-0" key={element.id}>
            {type === "siteCondition" ? (
              <SiteConditionsReportCard
                siteCondition={element as HazardAggregator}
                selectedSiteCondition={(
                  selections as unknown as SiteConditionAnalysisInputs[]
                )?.find(({ id }) => id === element.id)}
                isCompleted={isCompleted}
              />
            ) : (
              <TaskReportCard
                task={element as TaskHazardAggregator}
                selectedTask={(
                  selections as unknown as TaskAnalysisInputs[]
                )?.find(({ id }) => id === element.id)}
                isCompleted={isCompleted}
              />
            )}
          </div>
        ))
      ) : (
        <Paragraph
          text={`There are currently no ${title.toLowerCase()} that have been selected
          between the set ${workPackage.attributes.primeContractor.label.toLowerCase()} start and end dates.`}
        />
      )}
    </section>
  );
};

export type JobHazardAnalysisProps = {
  tasks: TaskHazardAggregator[];
  siteConditions: HazardAggregator[];
  defaultValues?: JobHazardAnalysisSectionInputs;
  isCompleted?: boolean;
};

export default function JobHazardAnalysis({
  tasks,
  siteConditions,
  defaultValues,
  isCompleted,
}: JobHazardAnalysisProps): JSX.Element {
  const { task, siteCondition, activity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const siteConditionList = isCompleted
    ? (defaultValues?.siteConditions as SiteConditionAnalysisInputs[])
    : siteConditions;

  const taskList = isCompleted
    ? (defaultValues?.tasks as TaskAnalysisInputs[])
    : tasks;

  return (
    <div className="flex flex-col gap-6 p-1">
      <JobWrapper
        title={siteCondition.labelPlural}
        list={siteConditionList}
        selections={defaultValues?.siteConditions}
        isCompleted={isCompleted}
      />
      <JobWrapper
        type="task"
        title={`${activity.label} ${task.labelPlural.toLowerCase()}`}
        list={taskList}
        selections={defaultValues?.tasks}
        isCompleted={isCompleted}
      />
    </div>
  );
}
