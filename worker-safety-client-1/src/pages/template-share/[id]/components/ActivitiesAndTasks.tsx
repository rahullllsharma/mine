import type {
  Activity,
  FormElement,
  SelectedActivity,
  Task,
} from "@/components/templatesComponents/customisedForm.types";
import { ActionLabel, BodyText } from "@urbint/silica";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { CWFTaskCard } from "@/components/dynamicForm/ActivitiesAndTaskComponents/CWFTaskCard";

const ActivitiesAndTasks = ({
  item,
  activitiesAndTasks,
}: {
  item: FormElement;
  activitiesAndTasks: SelectedActivity[];
}): JSX.Element => {
  return (
    <div className="flex flex-col bg-brand-gray-10 gap-4 p-4 rounded-lg">
      <div className="flex flex-col">
        <BodyText className="text-[20px] font-semibold">
          {item.properties.title ?? "Activities and Tasks"}
        </BodyText>
      </div>
      {activitiesAndTasks.length === 0 ? (
        <BodyText className="flex text-sm font-semibold">
          No information provided
        </BodyText>
      ) : (
        activitiesAndTasks.map((activity: Activity) => (
          <div key={activity.id} className="flex flex-col gap-4">
            <ActionLabel className="text-neutral-shade-75 text-base">
              {activity.name}
            </ActionLabel>
            <div className="gap-4 flex flex-col">
              {activity.tasks &&
                activity.tasks.map(
                  (task: Task) =>
                    task.selected && (
                      <CWFTaskCard
                        key={task.id}
                        title={task.libraryTask?.name || task.name}
                        risk={
                          task.libraryTask?.riskLevel || task.riskLevel
                            ? RiskLevel[
                                (task.libraryTask?.riskLevel ||
                                  task.riskLevel) as keyof typeof RiskLevel
                              ]
                            : RiskLevel.UNKNOWN
                        }
                        showRiskInformation={true}
                        showRiskText={true}
                        withLeftBorder={true}
                      />
                    )
                )}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default ActivitiesAndTasks;
