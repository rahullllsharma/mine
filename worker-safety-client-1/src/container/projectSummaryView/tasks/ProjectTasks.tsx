import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import TaskCard from "@/components/taskCard/TaskCard";
import TaskTable from "@/container/table/TaskTable";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type ProjectTasksProps = {
  projectId: string;
  locationId: string;
  tasks?: TaskHazardAggregator[];
};

const TaskCardContainer = ({
  projectId,
  locationId,
  tasks,
}: ProjectTasksProps): JSX.Element => {
  return (
    <div className="grid lg:hidden gap-4 grid-cols-auto-fill-list-card">
      {tasks?.map(task => (
        <TaskCard
          key={task.id}
          projectId={projectId}
          locationId={locationId}
          task={task}
        />
      ))}
    </div>
  );
};

export default function ProjectTasks({
  projectId,
  locationId,
  tasks = [],
}: ProjectTasksProps): JSX.Element {
  const { workPackage, location, task } = useTenantStore(state =>
    state.getAllEntities()
  );

  if (tasks.length === 0) {
    return (
      <div className="mt-24">
        <EmptyContent
          title={`You currently have no ${task.labelPlural.toLowerCase()}`}
          description={`${
            task.labelPlural
          } will appear here once they have been added to ${workPackage.label.toLowerCase()} ${location.labelPlural.toLowerCase()}`}
        />
      </div>
    );
  }

  return (
    <>
      <div className="hidden lg:block">
        <TaskTable
          projectId={projectId}
          locationId={locationId}
          tasks={tasks}
        />
      </div>
      <TaskCardContainer
        projectId={projectId}
        locationId={locationId}
        tasks={tasks}
      />
    </>
  );
}
