import type { IconName } from "@urbint/silica";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { Incident } from "@/types/project/Incident";
import { useQuery } from "@apollo/client";
import { useMemo } from "react";
import TaskContent from "@/components/layout/taskCard/content/TaskContent";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import { countTotalControls } from "@/container/Utils";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { getBorderColorByRiskLevel } from "@/utils/risk";
import { messages } from "@/locales/messages";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import getHistoricIncidents from "@/graphql/queries/getHistoricIncidents.gql";
import { IconSpinner } from "@/components/iconSpinner";

type ActivityTaskSectionProps = {
  task: TaskHazardAggregator;
  isOpen: boolean;
  onElementClick?: (element: TaskHazardAggregator) => void;
  onToggle: (task: TaskHazardAggregator) => void;
  onTaskClicked: (task: TaskHazardAggregator) => void;
  onHistoricOptionClick?: () => void;
};

function ActivityTaskSection({
  task,
  isOpen,
  onToggle,
  onTaskClicked,
  onHistoricOptionClick,
}: ActivityTaskSectionProps): JSX.Element {
  const { hasPermission } = useAuthStore();
  const { task: taskEntity } = useTenantStore(state => state.getAllEntities());
  const iconName: IconName = isOpen ? "chevron_big_down" : "chevron_big_right";
  const hasEditPermission = hasPermission("EDIT_TASKS");

  const onClick = () => onToggle(task);
  const onMenuClickHandler = () => onTaskClicked(task);

  const { libraryTask } = task;
  const libraryTaskId = libraryTask?.id;
  const { data, loading } = useQuery(getHistoricIncidents, {
    variables: { libraryTaskId },
  });

  const dropdownOptions = useMemo(() => {
    const options = [];

    if (hasEditPermission) {
      options.push([
        {
          label: `Edit ${taskEntity.label.toLowerCase()}`,
          onClick: () => onMenuClickHandler(),
        },
      ]);
    }

    const incidents: Incident[] | undefined = data?.historicalIncidents;

    options.push([
      {
        label: messages.historicIncidentLabel,
        onClick: () => onHistoricOptionClick?.(),
        disabled: loading,
        rightSlot: loading && <IconSpinner />,
      },
    ]);

    if (!loading && !incidents?.length) {
      options.pop();
    }

    return options;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, loading, hasEditPermission, taskEntity.label]);

  const taskHeader = (
    <TaskHeader
      icon={iconName}
      headerText={task.name}
      riskLevel={task.riskLevel}
      onClick={onClick}
      showSummaryCount={!isOpen}
      totalHazards={task.hazards.length}
      totalControls={countTotalControls(task.hazards)}
      menuIcon={hasEditPermission ? "edit" : undefined}
      onMenuClicked={onMenuClickHandler}
      hasDropdown
      dropdownOptions={dropdownOptions}
    />
  );

  return (
    <TaskCard
      className={getBorderColorByRiskLevel(task.riskLevel)}
      isOpen={isOpen}
      taskHeader={taskHeader}
    >
      <TaskContent hazards={task.hazards}></TaskContent>
    </TaskCard>
  );
}

export { ActivityTaskSection };
